//go:build linux
// +build linux

package main

import (
	"log"

	"golang.org/x/sys/unix"
)

// getMonotonicNs returns monotonic time in nanoseconds, matching bpf_ktime_get_ns()
func getMonotonicNs() uint64 {
	var ts unix.Timespec
	if err := unix.ClockGettime(unix.CLOCK_MONOTONIC, &ts); err != nil {
		log.Fatalf("getting monotonic clock: %v", err)
	}
	return uint64(ts.Sec*1e9 + ts.Nsec)
}
