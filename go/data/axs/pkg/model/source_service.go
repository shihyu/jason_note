package model

type SourceService struct {
	ID          int64
	Name        string
	Secret      string
	CallbackURL string
	CreatedTime int64
	CreatorID   int64
	UpdatedTime int64
	UpdaterID   int64
}

type CallbackLog struct {
	ID             int64
	ChangeLogID    int64
	SourceSvcID    int64
	RelatedOrderID int64
	EventID        string
	EventTypeID    int64
	IdempotencyKey string
	Payload        []byte
	AttemptCount   int32
	LastError      string
	FailedTime     int64
	InsertTime     int64
}
