package main

import (
	"debug/dwarf"
	"debug/elf"
	"debug/macho"
	"debug/pe"
	"fmt"
	"os"
	"strings"
)

// openDWARF returns DWARF data from ELF, Mach-O, or PE
func openDWARF(path string) (*dwarf.Data, error) {
	if f, err := elf.Open(path); err == nil {
		return f.DWARF()
	}
	if f, err := macho.Open(path); err == nil {
		return f.DWARF()
	}
	if f, err := pe.Open(path); err == nil {
		return f.DWARF()
	}
	return nil, fmt.Errorf("unsupported binary: %s", path)
}

func typeSize(d *dwarf.Data, typ dwarf.Type) int64 {
	switch t := typ.(type) {
	case *dwarf.IntType, *dwarf.UintType, *dwarf.FloatType,
		*dwarf.BoolType, *dwarf.AddrType, *dwarf.PtrType:
		return int64(t.Common().ByteSize)
	case *dwarf.StructType:
		return t.ByteSize
	case *dwarf.ArrayType:
		return t.ByteSize
	default:
		return 0 // fallback
	}
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("usage: go run main.go <binary>")
		return
	}
	d, err := openDWARF(os.Args[1])
	if err != nil {
		panic(err)
	}

	r := d.Reader()
	for {
		ent, err := r.Next()
		if err != nil || ent == nil {
			break
		}
		if ent.Tag != dwarf.TagStructType {
			continue
		}
		topName, _ := ent.Val(dwarf.AttrName).(string)
		// if map[string]bool{
		// 	"runtime.g":     true,
		// 	"abi.Type":     true,
		// 	"runtime._type": true,
		// }[topName] == false {
		// 	continue
		// }
		if !strings.Contains(topName, "runtime.g") &&
			!strings.Contains(topName, "abi.Type") &&
			!strings.Contains(topName, "runtime._type") &&
			!strings.Contains(topName, "MapType") {
			continue
		}

		var fields []struct {
			name string
			off  int64
			size int64
		}

		for {
			child, err := r.Next()
			if err != nil || child == nil {
				break
			}
			if child.Tag == 0 { // end of children
				break
			}
			if child.Tag == dwarf.TagMember {
				n, _ := child.Val(dwarf.AttrName).(string)
				off, _ := child.Val(dwarf.AttrDataMemberLoc).(int64)
				typOff, _ := child.Val(dwarf.AttrType).(dwarf.Offset)
				if typ, err := d.Type(typOff); err == nil {
					size := typeSize(d, typ)
					fields = append(fields, struct {
						name string
						off  int64
						size int64
					}{n, off, size})
				}
			}
		}

		// goid, parentGoid, startpc => runtime.g; Size_, Str => abi.Type;
		for _, name := range []string{"goid", "parentGoid", "startpc", "Size_", "Str", "Kind_", "Key", "Elem"} {
			for i, f := range fields {
				if f.name == name {
					var leftPad, rightPad int64
					if i > 0 {
						prev := fields[i-1]
						prevEnd := prev.off + prev.size
						if f.off > prevEnd {
							leftPad = f.off - prevEnd
						}
					}
					if i+1 < len(fields) {
						next := fields[i+1]
						end := f.off + f.size
						if next.off > end {
							rightPad = next.off - end
						}
					}
					fmt.Printf("%s.%s offset=%d size=%d leftPad=%d rightPad=%d\n",
						topName, name, f.off, f.size, leftPad, rightPad)
				}
			}
		}
	}
}
