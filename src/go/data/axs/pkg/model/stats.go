package model

type StressTestStats struct {
	EventCreatedMsec         int64 `json:"event_created_msec"`
	TotalEventsProcessed     int   `json:"total_events_processed"`
	TotalMessages            int   `json:"total_messages"`
	DecodeCostMicroSec       int   `json:"decode_cost"`
	ApplyCostMicroSec        int   `json:"apply_cost"`
	AsyncCostMicroSec        int   `json:"async_cost"`
	TotalProcessCostMicroSec int   `json:"process_cost"`
	StartProcessMsec         int64 `json:"start_process_msec"`
	PublishedMsec            int64 `json:"published_msec"`
	DelayCount               int   `json:"delay_count"`
}
