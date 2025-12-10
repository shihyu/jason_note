package utils

import (
	err "errors"

	"github.com/pkg/errors"
)

func ErrIs(err, target error) bool {
	if errors.Is(err, target) {
		return true
	}
	if errors.Is(errors.Cause(err), target) {
		return true
	}
	return errors.Is(errors.Unwrap(err), target)
}

func JoinErrors(errs ...error) error {
	return err.Join(errs...)
}
