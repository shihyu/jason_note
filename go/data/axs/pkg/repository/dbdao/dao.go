package dbdao

import (
	"fmt"

	"github.com/jackc/pgx/v5"
	"github.com/jmoiron/sqlx"
	"github.com/vx416/axs/pkg/domain"
	"github.com/vx416/axs/pkg/repository/dbdao/pg"
	"github.com/vx416/axs/pkg/repository/dbdao/sqlx_adapter"
	"go.uber.org/fx"
)

type Params struct {
	fx.In
	DB      *sqlx.DB
	PGxConn *pgx.Conn
}

// NewDBDRepository creates a new DBRepository based on the database driver.
func NewDBDRepository(param Params) (domain.DBRepository, error) {
	sqlxAdapter := sqlx_adapter.NewSqlxAdapter(param.DB)
	switch param.DB.DriverName() {
	case "postgres", "pgx", "pg":
		return pg.NewPGDao(sqlxAdapter, param.PGxConn)
	}
	return nil, fmt.Errorf("unsupported database driver: %s", param.DB.DriverName())
}
