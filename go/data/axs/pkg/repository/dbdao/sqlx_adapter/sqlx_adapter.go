package sqlx_adapter

import (
	"context"
	"database/sql"

	"github.com/jmoiron/sqlx"
	"github.com/vx416/axs/pkg/utils"
)

type SqlxDB interface {
	QueryContext(ctx context.Context, query string, args ...interface{}) (*sql.Rows, error)
	QueryRowxContext(ctx context.Context, query string, args ...interface{}) *sqlx.Row
	QueryxContext(ctx context.Context, query string, args ...interface{}) (*sqlx.Rows, error)
	NamedExecContext(ctx context.Context, query string, arg interface{}) (sql.Result, error)
	ExecContext(ctx context.Context, query string, args ...any) (sql.Result, error)
	SelectContext(ctx context.Context, dest interface{}, query string, args ...interface{}) error
	GetContext(ctx context.Context, dest interface{}, query string, args ...interface{}) error
	PrepareContext(ctx context.Context, query string) (*sql.Stmt, error)
	PrepareNamedContext(ctx context.Context, query string) (*sqlx.NamedStmt, error)
	NamedQueryContext(ctx context.Context, query string, arg any) (*sqlx.Rows, error)
}

type txKey struct{}

func NewSqlxAdapter(db *sqlx.DB) *SqlxAdapter {
	return &SqlxAdapter{
		DB:         db,
		DriverType: db.DriverName(),
	}
}

type SqlxAdapter struct {
	DB         *sqlx.DB
	DriverType string
}

func (d *SqlxAdapter) Close() error {
	return d.DB.Close()
}

func (d *SqlxAdapter) ExecuteInTransaction(ctx context.Context, fn func(txnCtx context.Context) error) error {
	tx, err := d.DB.BeginTxx(ctx, nil)
	if err != nil {
		return err
	}
	txnCtx := context.WithValue(ctx, txKey{}, tx)
	err = fn(txnCtx)
	if err != nil {
		rbErr := tx.Rollback()
		if rbErr != nil {
			return utils.JoinErrors(err, rbErr)
		}
		return err
	}
	return tx.Commit()
}

func (d *SqlxAdapter) GetDB(ctx context.Context) SqlxDB {
	if tx, ok := d.GetTxFromCtx(ctx); ok {
		return &LogDriver{DB: &ExtTx{Tx: tx}, DriverType: d.DriverType}
	}

	return &LogDriver{DB: d.DB, DriverType: d.DriverType}
}

func (d *SqlxAdapter) GetTxFromCtx(ctx context.Context) (*sqlx.Tx, bool) {
	tx, ok := ctx.Value(txKey{}).(*sqlx.Tx)
	return tx, ok
}

type ExtTx struct {
	*sqlx.Tx
}

func (ext *ExtTx) NamedQueryContext(ctx context.Context, query string, val any) (*sqlx.Rows, error) {
	sql, args, err := sqlx.BindNamed(sqlx.BindType(ext.DriverName()), query, val)
	if err != nil {
		return nil, err
	}
	return ext.Tx.QueryxContext(ctx, sql, args...)
}
