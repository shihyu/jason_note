package mq

import (
	"github.com/pkg/errors"
	"github.com/vx416/axs/pkg/utils"
)

// subscriber errors
var (
	ErrSubscriberClosed        error = errors.New("subscriber close")
	ErrCancelMessageAckOrNack  error = errors.New("cancel ack or nack")
	ErrSubscriberCloseTimeout  error = errors.New("subscriber close timeout")
	ErrSubscriberTimeout       error = errors.New("subscriber timeout")
	ErrSubscriberExceedMaxPoll error = errors.New("subscriber exceed max poll")
)

func IsTimeoutError(err error) bool {
	return utils.ErrIs(err, ErrSubscriberTimeout)
}
