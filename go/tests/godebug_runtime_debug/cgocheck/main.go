package main

/*
static void sink(void *p) { (void)p; }
*/
import "C"

import "unsafe"

type node struct {
	next *int
}

func main() {
	v := 42
	n := node{next: &v}
	C.sink(unsafe.Pointer(&n))
	println("cgocheck passed")
}
