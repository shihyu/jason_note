package utils

import (
	"time"

	"github.com/cenkalti/backoff/v4"
)

var (
	defaultRetryOptions = backoff.ExponentialBackOff{
		InitialInterval:     50 * time.Millisecond,
		RandomizationFactor: 0.5,
		Multiplier:          1.5,
		MaxInterval:         500 * time.Millisecond,
		MaxElapsedTime:      2 * time.Second,
		Clock:               backoff.SystemClock,
		Stop:                backoff.Stop,
	}
)

func Retry(fn func() (keepRetry bool, err error)) error {
	ok, err := fn()
	if err == nil {
		return nil
	}
	if !ok {
		return err
	}

	var retryErr error

	backoff.Retry(func() error {
		ok, err := fn()
		retryErr = err
		if !ok {
			return nil
		}
		return err
	}, &defaultRetryOptions)
	return retryErr
}
