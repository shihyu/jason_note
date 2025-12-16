package sqlx_adapter

import (
	"context"
	"database/sql"
	"time"

	"github.com/jmoiron/sqlx"
	"github.com/vx416/axs/pkg/logger"
)

type LogDriver struct {
	DB         SqlxDB
	DriverType string
}

func (driver *LogDriver) QueryRowxContext(ctx context.Context, query string, args ...any) *sqlx.Row {
	start := time.Now()
	defer func() {
		cost := time.Since(start)
		logger.PrintSQL(ctx, nil, nil, cost, query, args...)
	}()
	return driver.DB.QueryRowxContext(ctx, query, args...)
}

func (driver *LogDriver) QueryxContext(ctx context.Context, query string, args ...any) (*sqlx.Rows, error) {
	start := time.Now()
	rows, err := driver.DB.QueryxContext(ctx, query, args...)
	cost := time.Since(start)
	logger.PrintSQL(ctx, nil, err, cost, query, args...)
	return rows, err
}

func (driver *LogDriver) NamedExecContext(ctx context.Context, query string, val any) (sql.Result, error) {
	start := time.Now()
	sql, args, err := sqlx.BindNamed(sqlx.BindType(driver.DriverType), query, val)
	if err != nil {
		return nil, err
	}
	result, err := driver.DB.ExecContext(ctx, sql, args...)
	cost := time.Since(start)
	var rowsAffected *int64
	if err == nil {
		if ra, err := result.RowsAffected(); err == nil {
			ra64 := int64(ra)
			rowsAffected = &ra64
		}
	}
	logger.PrintSQL(ctx, rowsAffected, err, cost, sql, args...)
	return result, err
}

func (driver *LogDriver) ExecContext(ctx context.Context, query string, args ...any) (sql.Result, error) {
	start := time.Now()
	result, err := driver.DB.ExecContext(ctx, query, args...)
	cost := time.Since(start)
	var rowsAffected *int64
	if err == nil {
		if ra, err := result.RowsAffected(); err == nil {
			ra64 := int64(ra)
			rowsAffected = &ra64
		}
	}
	logger.PrintSQL(ctx, rowsAffected, err, cost, query, args...)
	return result, err
}

func (driver *LogDriver) SelectContext(ctx context.Context, dest any, query string, args ...any) error {
	start := time.Now()
	err := driver.DB.SelectContext(ctx, dest, query, args...)
	cost := time.Since(start)
	logger.PrintSQL(ctx, nil, err, cost, query, args...)
	return err
}
func (driver *LogDriver) GetContext(ctx context.Context, dest any, query string, args ...any) error {
	start := time.Now()
	err := driver.DB.GetContext(ctx, dest, query, args...)
	cost := time.Since(start)
	logger.PrintSQL(ctx, nil, err, cost, query, args...)
	return err
}

func (driver *LogDriver) PrepareContext(ctx context.Context, query string) (*sql.Stmt, error) {
	start := time.Now()
	stmt, err := driver.DB.PrepareContext(ctx, query)
	cost := time.Since(start)
	logger.PrintSQL(ctx, nil, err, cost, query)
	return stmt, err
}

func (driver *LogDriver) PrepareNamedContext(ctx context.Context, query string) (*sqlx.NamedStmt, error) {
	start := time.Now()
	nstmt, err := driver.DB.PrepareNamedContext(ctx, query)
	cost := time.Since(start)
	logger.PrintSQL(ctx, nil, err, cost, query)
	return nstmt, err
}

func (driver *LogDriver) QueryContext(ctx context.Context, query string, args ...any) (*sql.Rows, error) {
	start := time.Now()
	rows, err := driver.DB.QueryContext(ctx, query, args...)
	cost := time.Since(start)
	logger.PrintSQL(ctx, nil, err, cost, query, args...)
	return rows, err
}

func (driver *LogDriver) NamedQueryContext(ctx context.Context, query string, arg any) (*sqlx.Rows, error) {
	start := time.Now()
	sql, args, err := sqlx.BindNamed(sqlx.BindType(driver.DriverType), query, arg)
	if err != nil {
		return nil, err
	}
	rows, err := driver.DB.QueryxContext(ctx, sql, args...)
	cost := time.Since(start)
	logger.PrintSQL(ctx, nil, err, cost, sql, args...)
	return rows, err
}
