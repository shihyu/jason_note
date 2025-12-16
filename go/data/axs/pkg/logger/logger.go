package logger

import (
	"context"
	"os"

	"github.com/rs/zerolog"
)

// InitLogger initializes and returns a zerolog logger
func InitLogger() *zerolog.Logger {
	consoleWriter := zerolog.ConsoleWriter{Out: os.Stdout, TimeFormat: "15:04:05"}

	logger := zerolog.New(consoleWriter).
		With().
		Timestamp().
		Logger()
	zerolog.SetGlobalLevel(zerolog.DebugLevel)
	zerolog.DefaultContextLogger = &logger
	return &logger
}

// GetLogger retrieves the logger from the context
func GetLogger(ctx context.Context) *zerolog.Logger {
	return zerolog.Ctx(ctx)
}

// SetGlobalLogger sets the global logger
func SetGlobalLogger(log *zerolog.Logger) {
	zerolog.DefaultContextLogger = log
}
