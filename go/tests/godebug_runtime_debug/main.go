package main

import (
	"fmt"
	"os"
	"runtime"
	"runtime/debug"
	"time"
	"unsafe"
)

var sink uint64

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, "usage: go run tests/godebug_runtime_debug/main.go <mode>")
		os.Exit(2)
	}

	switch os.Args[1] {
	case "gc":
		runGC()
	case "addr":
		runAddr()
	case "clobber":
		runClobber()
	case "stack":
		runStack()
	case "memprofilerate":
		runMemProfileRate()
	case "invalidptr":
		runInvalidPtr()
	case "asyncpreempt":
		runAsyncPreempt()
	case "sched":
		runSched()
	case "traceback":
		runTraceback()
	case "rss":
		runRSS()
	default:
		fmt.Fprintf(os.Stderr, "unknown mode: %s\n", os.Args[1])
		os.Exit(2)
	}
}

func runGC() {
	blocks := make([][]byte, 0, 48)
	for i := 0; i < 48; i++ {
		b := make([]byte, 1<<20)
		b[0] = byte(i)
		blocks = append(blocks, b)
	}
	blocks = nil
	runtime.GC()
	debug.FreeOSMemory()

	var ms runtime.MemStats
	runtime.ReadMemStats(&ms)
	fmt.Printf("heap_alloc=%d heap_released=%d num_gc=%d\n", ms.HeapAlloc, ms.HeapReleased, ms.NumGC)
}

func runAddr() {
	keep := make([][]byte, 0, 4)
	for i := 0; i < 4; i++ {
		b := make([]byte, 8192)
		b[0] = byte(i)
		keep = append(keep, b)
	}
	for i, b := range keep {
		fmt.Printf("phase1_addr%d=%#x\n", i, uintptr(unsafe.Pointer(&b[0])))
	}
	keep = nil
	runtime.GC()

	keep = make([][]byte, 0, 4)
	for i := 0; i < 4; i++ {
		b := make([]byte, 8192)
		b[0] = byte(i)
		keep = append(keep, b)
	}
	for i, b := range keep {
		fmt.Printf("phase2_addr%d=%#x\n", i, uintptr(unsafe.Pointer(&b[0])))
	}
	runtime.KeepAlive(keep)
}

func runClobber() {
	buf := make([]byte, 8192)
	for i := range buf {
		buf[i] = 0x41
	}
	ptr := uintptr(unsafe.Pointer(&buf[0]))
	buf = nil
	runtime.GC()
	junk := make([][]byte, 0, 64)
	for i := 0; i < 64; i++ {
		b := make([]byte, 8192)
		b[0] = byte(i)
		junk = append(junk, b)
	}
	runtime.GC()

	stale := unsafe.Slice((*byte)(unsafe.Pointer(ptr)), 16)
	fmt.Printf("stale=% x\n", stale)
	runtime.KeepAlive(junk)
}

func runStack() {
	ready := make(chan struct{})
	release := make(chan struct{})

	go func() {
		sink += grow(0, 8192)
		close(ready)
		<-release
	}()

	<-ready
	reportStack("after_grow")
	runtime.GC()
	debug.FreeOSMemory()
	reportStack("after_gc_while_parked")
	close(release)
	time.Sleep(50 * time.Millisecond)
	runtime.GC()
	debug.FreeOSMemory()
	reportStack("after_worker_exit")
}

func grow(depth, max int) uint64 {
	var pad [256]byte
	pad[0] = byte(depth)
	if depth == max {
		return uint64(pad[0])
	}
	return uint64(pad[0]) + grow(depth+1, max)
}

func reportStack(label string) {
	var ms runtime.MemStats
	runtime.ReadMemStats(&ms)
	fmt.Printf("%s stack_inuse=%d stack_sys=%d num_gc=%d\n", label, ms.StackInuse, ms.StackSys, ms.NumGC)
}

func runMemProfileRate() {
	fmt.Printf("MemProfileRate=%d\n", runtime.MemProfileRate)
}

func runInvalidPtr() {
	type holder struct {
		p *int
	}

	h := &holder{}
	*(*uintptr)(unsafe.Pointer(&h.p)) = 1
	fmt.Println("forcing GC")
	runtime.GC()
	runtime.KeepAlive(h)
	fmt.Println("survived")
}

func runAsyncPreempt() {
	runtime.GOMAXPROCS(1)

	start := time.Now()
	done := make(chan struct{})

	go func() {
		time.Sleep(10 * time.Millisecond)
		fmt.Printf("secondary=%dms\n", time.Since(start).Milliseconds())
		close(done)
	}()

	sink += busyLoop(500_000_000)
	fmt.Printf("loop=%dms\n", time.Since(start).Milliseconds())
	<-done
}

func busyLoop(n uint64) uint64 {
	var acc uint64
	for i := uint64(0); i < n; i++ {
		acc += i
	}
	return acc
}

func runSched() {
	runtime.GOMAXPROCS(4)
	for i := 0; i < 8; i++ {
		go func() {
			sink += busyLoop(250_000_000)
		}()
	}
	time.Sleep(1500 * time.Millisecond)
	fmt.Println("sched-demo-done")
}

func runTraceback() {
	go levelOne()
	time.Sleep(200 * time.Millisecond)
	fmt.Println("unreachable")
}

func levelOne() {
	go levelTwo()
	time.Sleep(150 * time.Millisecond)
}

func levelTwo() {
	go func() {
		panic("traceback demo")
	}()
	time.Sleep(150 * time.Millisecond)
}

func runRSS() {
	reportRSS("before_alloc")

	blocks := make([][]byte, 0, 256)
	for i := 0; i < 256; i++ {
		b := make([]byte, 1<<20)
		for j := 0; j < len(b); j += 4096 {
			b[j] = byte(i)
		}
		blocks = append(blocks, b)
	}
	reportRSS("after_alloc")

	blocks = nil
	runtime.GC()
	debug.FreeOSMemory()
	reportRSS("after_free")
}

func reportRSS(label string) {
	data, err := os.ReadFile("/proc/self/status")
	if err != nil {
		fmt.Printf("%s read_error=%v\n", label, err)
		return
	}
	vmrss := ""
	for _, line := range bytesLines(data) {
		if len(line) >= 6 && string(line[:6]) == "VmRSS:" {
			vmrss = string(line)
			break
		}
	}

	var ms runtime.MemStats
	runtime.ReadMemStats(&ms)
	fmt.Printf("%s %s heap_released=%d heap_idle=%d\n", label, vmrss, ms.HeapReleased, ms.HeapIdle)
}

func bytesLines(b []byte) [][]byte {
	lines := make([][]byte, 0, 64)
	start := 0
	for i, c := range b {
		if c == '\n' {
			lines = append(lines, b[start:i])
			start = i + 1
		}
	}
	if start < len(b) {
		lines = append(lines, b[start:])
	}
	return lines
}
