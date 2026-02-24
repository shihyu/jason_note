//go:build !linux
// +build !linux

package main

func getMonotonicNs() uint64 {
	panic("unimplemented")
}
