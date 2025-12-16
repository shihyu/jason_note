package logger

import (
	"context"
	"runtime/debug"
)

// SafeGo runs the given function in a new goroutine and recovers from any panic, logging the error and stack trace.
func SafeGo(fn func()) {
	go func() {
		defer func() {
			if r := recover(); r != nil {
				stack := debug.Stack()
				GetLogger(context.Background()).Error().Msgf("panic recovered in goroutine: %v, stack:%s", r, string(stack))
			}
		}()
		fn()
	}()
}
