package svcerr

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

var (
	StopConsumingError = errors.New("stop consuming messages")
)

func IsStopConsumingError(err error) bool {
	return utils.ErrIs(err, StopConsumingError)
}

var (
	ErrLeaderChange = errors.New("leader change")
)

func IsLeaderChangeError(err error) bool {
	return utils.ErrIs(err, ErrLeaderChange)
}

var (
	ErrBalanceInsufficient = errors.New("balance insufficient")
)

var (
	ErrIdempotentViolation = errors.New("idempotent violation")
)
