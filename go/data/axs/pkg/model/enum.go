package model

type ChangeLogStatus int8

const (
	ChangeLogStatusInit           ChangeLogStatus = 0
	ChangeLogStatusApplied        ChangeLogStatus = 1
	ChangeLogStatusCannotApplied  ChangeLogStatus = 2
	ChangeLogStatusCannotCanceled ChangeLogStatus = 3
)

func (val ChangeLogStatus) IsFinalStatus() bool {
	return val >= ChangeLogStatusApplied
}

type AckStatus int8

const (
	AckStatusPending AckStatus = 0
	AckStatusAcked   AckStatus = 1
	AckStatusFailed  AckStatus = 2
)

type CallbackLogStatus int8

const (
	CallbackLogStatusPending CallbackLogStatus = 0
	CallbackLogStatusSuccess CallbackLogStatus = 1
	CallbackLogStatusFailed  CallbackLogStatus = 2
)
