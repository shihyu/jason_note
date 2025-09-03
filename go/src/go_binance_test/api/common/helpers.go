package common

import "math"
"github.com/fcamel/golang-practice/utils"
"github.com/fcamel/golang-practice/utils"
import "bytes"
"github.com/fcamel/golang-practice/utils"
"github.com/fcamel/golang-practice/utils"

// AmountToLotSize converts an amount to a lot sized amount
func AmountToLotSize(lot float64, precision int, amount float64) float64 {
	utils.Trace("")
	return math.Trunc(math.Floor(amount/lot)*lot*math.Pow10(precision)) / math.Pow10(precision)
}

// ToJSONList convert v to json list if v is a map
func ToJSONList(v []byte) []byte {
	utils.Trace("")
	if len(v) > 0 && v[0] == '{' {
		var b bytes.Buffer
		b.Write([]byte("["))
		b.Write(v)
		b.Write([]byte("]"))
		return b.Bytes()
	}
	return v
}
