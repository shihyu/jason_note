package common

import (
	"bytes"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"log"
	"math"
	"time"
)

// AmountToLotSize converts an amount to a lot sized amount
func AmountToLotSize(lot float64, precision int, amount float64) float64 {
	return math.Trunc(math.Floor(amount/lot)*lot*math.Pow10(precision)) / math.Pow10(precision)
}

// ToJSONList convert v to json list if v is a map
func ToJSONList(v []byte) []byte {
	if len(v) > 0 && v[0] == '{' {
		var b bytes.Buffer
		b.Write([]byte("["))
		b.Write(v)
		b.Write([]byte("]"))
		return b.Bytes()
	}
	return v
}

func IsoTime() string {
	utcTime := time.Now().UTC()
	iso := utcTime.String()
	isoBytes := []byte(iso)
	iso = string(isoBytes[:10]) + "T" + string(isoBytes[11:23]) + "Z"
	return iso
}

/*
 struct convert json string
*/
func Struct2JsonString(raw interface{}) (jsonString string, err error) {
	data, err := json.Marshal(raw)
	if err != nil {
		log.Println("convert json failed!", err)
		return "", err
	}
	return string(data), nil
}

func Hmac256(timestamp string, method string, path string, body *bytes.Buffer, secret string) (string, error) {
	var raw string
	if body != nil {
		raw = fmt.Sprintf("%s%s%s%s", timestamp, method, path, body)
	} else {
		raw = fmt.Sprintf("%s%s%s", timestamp, method, path)
	}

	mac := hmac.New(sha256.New, []byte(secret))
	_, err := mac.Write([]byte(raw))
	if err != nil {
		return "", err
	}
	return base64.StdEncoding.EncodeToString(mac.Sum(nil)), nil
}
