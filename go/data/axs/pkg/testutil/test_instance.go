package testutil

import (
	"context"
	"encoding/json"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"testing"

	"github.com/jackc/pgx/v5"
	"github.com/jmoiron/sqlx"
	"github.com/pkg/errors"
	"github.com/redis/go-redis/v9"
	"github.com/vx416/axs/pkg/infra"
	"github.com/vx416/axs/pkg/logger"
	"github.com/vx416/axs/pkg/mq"
	"github.com/vx416/axs/setup/tools"
	"go.uber.org/fx"
)

func NewTestInstance(t *testing.T) (*TestInstance, error) {
	builder, err := NewContainerBuilder("")
	if err != nil {
		return nil, err
	}
	ti := &TestInstance{
		T:                t,
		ContainerBuilder: builder,
		Ctx:              context.Background(),
	}

	config, err := infra.InitConfig("config.test", infra.GetAbsPath("config"))
	if err != nil {
		return nil, err
	}
	logger.InitLogger()
	ti.Config = config
	buildPGOptions := PostgresContainerOptions{
		Name:         "axs-test-postgres",
		Host:         config.DB.DBHost,
		Port:         strconv.Itoa(config.DB.DBPort),
		Username:     config.DB.DBUser,
		Password:     config.DB.DBPassword,
		DatabaseName: config.DB.DBName,
	}
	_, err = BuildPostgresContainer(ti.ContainerBuilder, buildPGOptions)
	if err != nil {
		return nil, err
	}

	buildRedisOptions := RedisContainerOptions{
		Name:     "axs-test-redis",
		Host:     config.Redis.Addr,
		Port:     strconv.Itoa(config.Redis.Port),
		Password: config.Redis.Password,
	}
	_, err = BuildRedisContainer(ti.ContainerBuilder, buildRedisOptions)
	if err != nil {
		return nil, err
	}

	db, pgxConn, err := infra.NewSqlx(ti.Config.DB)
	if err != nil {
		return nil, errors.WithMessage(err, "failed to connect to test db")
	}
	ti.PgxConn = pgxConn
	ti.SqlxDB = db
	err = ti.RunDBMigrations()
	if err != nil {
		return nil, err
	}

	redisClient, err := infra.NewRedisClient(ti.Config.Redis)
	if err != nil {
		return nil, err
	}
	ti.Redis = redisClient

	ti.MockProducer = mq.NewMockProducer(ti.T)
	ti.ImMemConsumerReader = mq.NewInMemoryConsumer(100)
	return ti, nil
}

type TestInstance struct {
	T                   *testing.T
	Config              infra.Config
	SqlxDB              *sqlx.DB
	PgxConn             *pgx.Conn
	ImMemConsumerReader *mq.InMemoryConsumer
	Redis               redis.UniversalClient
	MockProducer        *mq.MockProducer
	ContainerBuilder    *ContainerBuilder
	Ctx                 context.Context
}

func (ti *TestInstance) GetTestInfraProvider() (fx.Option, error) {
	return fx.Options(
		fx.Provide(func() *sqlx.DB {
			return ti.SqlxDB
		}),
		fx.Provide(func() redis.UniversalClient {
			return ti.Redis
		}),
		fx.Provide(func() mq.Producer {
			return ti.MockProducer
		}),
		fx.Provide(func() mq.ConsumerReader {
			return ti.ImMemConsumerReader
		}),
		fx.Provide(func() *pgx.Conn {
			return ti.PgxConn
		}),
	), nil
}

func (ti *TestInstance) TeardownInfra() error {
	return nil
}

func (ti *TestInstance) RunDBMigrations() error {
	err := tools.DBMigrationUpWithDriver(ti.SqlxDB.DB, infra.GetAbsPath("/setup/migration"))
	if err != nil {
		return err
	}
	return nil
}

func (ti *TestInstance) ClearRedisData() error {
	ctx := context.Background()
	return ti.Redis.FlushDB(ctx).Err()
}

func (ti *TestInstance) ResetAndRunSeedData() error {
	testDataDir := infra.GetAbsPath("pkg/testutil/testdata")
	err := filepath.Walk(testDataDir, func(file string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if info.IsDir() {
			return nil
		}
		if filepath.Ext(file) == ".sql" {
			data, err := os.ReadFile(file)
			if err != nil {
				return err
			}

			if string(data) != "" {
				dataStr := string(data)
				for stmt := range strings.SplitSeq(dataStr, ";\n") {
					stmt = strings.TrimSpace(stmt)
					if stmt == "" {
						continue
					}

					stmt = escapeString(stmt)
					stmt = strings.ReplaceAll(stmt, `\`, ``)
					_, err = ti.SqlxDB.ExecContext(ti.Ctx, stmt)
					if err != nil {
						return errors.WithMessage(err, stmt)
					}
				}
			}
		}
		return nil
	})

	return err
}

func (ti *TestInstance) ResetDB() error {
	deletes := []string{
		"DELETE FROM partition_leader_locks;",
		"DELETE FROM balance_change_logs;",
		"DELETE FROM accounts;",
		"DELETE FROM account_balances;",
	}
	for _, del := range deletes {
		_, err := ti.SqlxDB.ExecContext(ti.Ctx, del)
		if err != nil {
			return err
		}
	}
	return nil
}

func (ti *TestInstance) PGCopyFromLargeJson() error {
	err := pgCopyFromJSON(ti.PgxConn, "accounts", infra.GetAbsPath("pkg/testutil/testdata/accounts_large.json"))
	if err != nil {
		return err
	}
	err = pgCopyFromJSON(ti.PgxConn, "account_balances", infra.GetAbsPath("pkg/testutil/testdata/account_balances_large.json"))
	if err != nil {
		return err
	}
	err = pgCopyFromJSON(ti.PgxConn, "balance_change_logs", infra.GetAbsPath("pkg/testutil/testdata/balance_change_logs_large.json"))
	if err != nil {
		return err
	}
	return nil
}

func escapeString(value string) string {
	var sb strings.Builder
	for i := 0; i < len(value); i++ {
		c := value[i]
		switch c {
		case '\\', 0, '\n', '\r', '\'', '"':
			sb.WriteByte('\\')
			sb.WriteByte(c)
		case '\032':
			sb.WriteByte('\\')
			sb.WriteByte('Z')
		default:
			sb.WriteByte(c)
		}
	}
	return sb.String()
}

func pgCopyFromJSON(pgConn *pgx.Conn, tableName string, filePath string) error {
	jsonBytes, err := os.ReadFile(filePath)
	if err != nil {
		return err
	}
	jsonData := []map[string]any{}
	err = json.Unmarshal(jsonBytes, &jsonData)
	if err != nil {
		return err
	}
	columns := []string{}
	if len(jsonData) > 0 {
		for k := range jsonData[0] {
			columns = append(columns, k)
		}
	}
	values := [][]any{}
	for _, row := range jsonData {
		valRow := []any{}
		for _, col := range columns {
			valRow = append(valRow, row[col])
		}
		values = append(values, valRow)
	}
	_, err = pgConn.CopyFrom(
		context.Background(),
		pgx.Identifier{tableName},
		columns,
		pgx.CopyFromRows(values),
	)
	return err
}
