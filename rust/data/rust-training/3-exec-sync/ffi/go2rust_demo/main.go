package main

/*
#cgo LDFLAGS: -L./lib -lhello
#include <stdlib.h>
#include "./lib/libhello.h"
*/
import "C"

import (
	"fmt"
	"unsafe"
)

func main() {
	s := "Go say: Hello Rust"

	input := C.CString(s)
	defer C.free(unsafe.Pointer(input))
	o := C.HelloWorld(input)
	output := C.GoString(o)
	fmt.Printf("%s\n", output)
}
