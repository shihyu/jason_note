package Impl

import (
	. "github.com/tbtc-bot/go-okex/common"
)

type ReqData struct {
	Op   string              `json:"op"`
	Args []map[string]string `json:"args"`
}

func (r ReqData) GetType() int {
	return MSG_NORMAL
}

func (r ReqData) ToString() string {
	data, err := Struct2JsonString(r)
	if err != nil {
		return ""
	}
	return data
}

func (r ReqData) Len() int {
	return len(r.Args)
}
