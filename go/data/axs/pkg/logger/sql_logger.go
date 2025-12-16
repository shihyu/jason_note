package logger

import (
	"context"
	"database/sql/driver"
	"fmt"
	"reflect"
	"regexp"
	"strconv"
	"strings"
	"time"
	"unicode"

	"gorm.io/gorm/utils"
)

const (
	tmFmtWithMS = "2006-01-02 15:04:05.999"
	tmFmtZero   = "0000-00-00 00:00:00"
	nullStr     = "NULL"
)

func isPrintable(s []byte) bool {
	for _, r := range s {
		if !unicode.IsPrint(rune(r)) {
			return false
		}
	}
	return true
}

var convertibleTypes = []reflect.Type{reflect.TypeOf(time.Time{}), reflect.TypeOf(false), reflect.TypeOf([]byte{})}

func ExplainSQL(sql string, avars ...interface{}) string {
	var convertParams func(interface{}, int)
	var vars = make([]string, len(avars))
	escaper := `"`

	convertParams = func(v interface{}, idx int) {
		switch v := v.(type) {
		case bool:
			vars[idx] = strconv.FormatBool(v)
		case time.Time:
			if v.IsZero() {
				vars[idx] = escaper + tmFmtZero + escaper
			} else {
				vars[idx] = escaper + v.Format(tmFmtWithMS) + escaper
			}
		case *time.Time:
			if v != nil {
				if v.IsZero() {
					vars[idx] = escaper + tmFmtZero + escaper
				} else {
					vars[idx] = escaper + v.Format(tmFmtWithMS) + escaper
				}
			} else {
				vars[idx] = nullStr
			}
		case driver.Valuer:
			reflectValue := reflect.ValueOf(v)
			if v != nil && reflectValue.IsValid() && ((reflectValue.Kind() == reflect.Ptr && !reflectValue.IsNil()) || reflectValue.Kind() != reflect.Ptr) {
				r, _ := v.Value()
				convertParams(r, idx)
			} else {
				vars[idx] = nullStr
			}
		case []byte:
			if isPrintable(v) {
				vars[idx] = escaper + strings.Replace(string(v), escaper, "\\"+escaper, -1) + escaper
			} else {
				vars[idx] = escaper + "<binary>" + escaper
			}
		case int, int8, int16, int32, int64, uint, uint8, uint16, uint32, uint64:
			vars[idx] = utils.ToString(v)
		case float64, float32:
			vars[idx] = fmt.Sprintf("%.10f", v)
		case string:
			vars[idx] = escaper + strings.Replace(v, escaper, "\\"+escaper, -1) + escaper
		default:
			rv := reflect.ValueOf(v)
			if v == nil || !rv.IsValid() || rv.Kind() == reflect.Ptr && rv.IsNil() {
				vars[idx] = nullStr
			} else if valuer, ok := v.(driver.Valuer); ok {
				v, _ = valuer.Value()
				convertParams(v, idx)
			} else if rv.Kind() == reflect.Ptr && !rv.IsZero() {
				convertParams(reflect.Indirect(rv).Interface(), idx)
			} else if rv.Kind() == reflect.Int || rv.Kind() == reflect.Int8 || rv.Kind() == reflect.Int16 || rv.Kind() == reflect.Int32 || rv.Kind() == reflect.Int64 {
				vars[idx] = fmt.Sprintf("%d", rv.Int())
			} else if rv.Kind() == reflect.Uint || rv.Kind() == reflect.Uint8 || rv.Kind() == reflect.Uint16 || rv.Kind() == reflect.Uint32 || rv.Kind() == reflect.Uint64 {
				vars[idx] = fmt.Sprintf("%d", rv.Uint())
			} else {
				for _, t := range convertibleTypes {
					if rv.Type().ConvertibleTo(t) {
						convertParams(rv.Convert(t).Interface(), idx)
						return
					}
				}
				vars[idx] = escaper + strings.Replace(fmt.Sprint(v), escaper, "\\"+escaper, -1) + escaper
			}
		}
	}

	for idx, v := range avars {
		convertParams(v, idx)
	}

	if IsPg {
		sql = pgRex.ReplaceAllString(sql, "$$$1$$")
		for idx, v := range vars {
			sql = strings.Replace(sql, "$"+strconv.Itoa(idx+1)+"$", v, 1)
		}
	} else {
		var idx int
		var newSQL strings.Builder
		for _, v := range []byte(sql) {
			if v == '?' {
				if len(vars) > idx {
					newSQL.WriteString(vars[idx])
					idx++
					continue
				}
			}
			newSQL.WriteByte(v)
		}
		sql = newSQL.String()
	}

	return sql
}

var pgRex = regexp.MustCompile(`\$(\d+)`)

type (
	Level    uint8
	LevelKey struct{}
)

func SetLevel(ctx context.Context, level Level) context.Context {
	return context.WithValue(ctx, LevelKey{}, level)
}

func SetDefaultLevel(level Level) {
	LogLevel = level
}

// SetIsPg sets the IsPg variable based on the provided dbType string.
func SetIsPg(dbType string) {
	switch strings.ToLower(dbType) {
	case "postgres", "postgresql", "pgx", "pg":
		IsPg = true
	default:
		IsPg = false
	}
}

func getLevel(ctx context.Context) Level {
	level, ok := ctx.Value(LevelKey{}).(Level)
	if !ok {
		return LogLevel
	}
	return level
}

const (
	Debug Level = iota + 1
	Info
	Off
)

var (
	IsPg          bool
	LogLevel      = Debug
	SlowThreshold = 1 * time.Second
)

// PrintSQL logs the SQL execution details including the query, arguments, execution time, affected rows, and any errors.
func PrintSQL(ctx context.Context, rowsAffected *int64, err error, cost time.Duration, query string, args ...interface{}) {
	level := getLevel(ctx)
	if level == Off {
		return
	}

	l := GetLogger(ctx)

	sql := ExplainSQL(query, args...)
	*l = l.With().Int("db_cost_msec", int(cost.Milliseconds())).Logger()
	if rowsAffected != nil {
		*l = l.With().Int("row_affected", int(*rowsAffected)).Logger()
	}
	if err != nil {
		l.Error().Err(err).Msg(sql)
		return
	}
	if SlowThreshold > 0 && cost > SlowThreshold {
		*l = l.With().Dur("slow_threshold", SlowThreshold).Logger()
		l.Warn().Str("slow", "true").Msg(sql)
		return
	}
	switch level {
	case Debug:
		l.Debug().Msg(sql)
	case Info:
		l.Info().Msg(sql)
	case Off:
		// do nothing
	}
}
