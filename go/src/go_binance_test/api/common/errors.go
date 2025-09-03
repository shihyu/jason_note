package common

import (
	"fmt"
	"github.com/fcamel/golang-practice/utils"
)

// APIError define API error when response status is 4xx or 5xx
type APIError struct {
	Code    int64  `json:"code"`
	Message string `json:"msg"`
}

// Error return error code and message
func (e APIError) Error() string {
	utils.Trace("")
	return fmt.Sprintf("<APIError> code=%d, msg=%s", e.Code, e.Message)
}

// IsAPIError check if e is an API error
func IsAPIError(e error) bool {
	utils.Trace("")
	_, ok := e.(*APIError)
	return ok
}
