package model

const (
	BalanceChangeEventTopic  = "balance_change_events"
	BalanceChangeResultTopic = "balance_change_results"
)

type PartitionOffset struct {
	Topic        string          `db:"topic"`
	Partition    int32           `db:"partition"`
	CommitOffset int64           `db:"commit_offset"`
	UpdatedMsec  TimestampInMsec `db:"updated_msec"`
	UpdaterSvcID string          `db:"updater_svc_id"`
}

type PartitionLeaderLock struct {
	Topic            string          `db:"topic"`
	Partition        int32           `db:"partition"`
	CommitOffset     int64           `db:"commit_offset"`
	UpdatedMsec      TimestampInMsec `db:"updated_msec"`
	UpdaterSvcID     string          `db:"updater_svc_id"`
	LeaderSvcID      string          `db:"leader_svc_id"`
	LeaseExpiredMsec int64           `db:"lease_expired_msec"`
	FencingToken     int64           `db:"fencing_token"`
}
