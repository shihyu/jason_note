package consumer

import (
	"github.com/pkg/errors"
	"github.com/vx416/axs/pkg/utils"
)

var (
	ErrNeedRetry = errors.New("need retry")
)

func IsNeedRetryError(err error) bool {
	return utils.ErrIs(err, ErrNeedRetry)
}

var (
	ErrDeadLetterQueue = errors.New("send to dead letter queue")
)

func IsDeadLetterQueueError(err error) bool {
	return utils.ErrIs(err, ErrDeadLetterQueue)
}

func NewNeedRetryError(err error) error {
	return errors.WithMessage(ErrNeedRetry, err.Error())
}
