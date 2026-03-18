package tracer

import (
	"fmt"
	"strings"
	"sync"
	"time"
)

var (
	mu    sync.Mutex
	depth int
)

// Trace prints function entry/exit with indentation and elapsed time.
// Usage: defer tracer.Trace("funcName")()
func Trace(name string) func() {
	mu.Lock()
	indent := strings.Repeat("  ", depth)
	fmt.Printf("%s--> %s\n", indent, name)
	depth++
	mu.Unlock()

	start := time.Now()

	return func() {
		elapsed := time.Since(start)

		mu.Lock()
		depth--
		indent := strings.Repeat("  ", depth)
		fmt.Printf("%s<-- %s (%v)\n", indent, name, elapsed)
		mu.Unlock()
	}
}
