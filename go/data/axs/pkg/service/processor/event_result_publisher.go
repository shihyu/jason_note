package processor

import (
	"context"

	"strconv"
	"time"

	segmentioJson "github.com/segmentio/encoding/json"

	"github.com/vx416/axs/pkg/infra"
	"github.com/vx416/axs/pkg/logger"
	"github.com/vx416/axs/pkg/model"
	"github.com/vx416/axs/pkg/mq"
)

type ResultPublisher struct {
	Producer mq.Producer
}

func (rp *ResultPublisher) PublishResults(ctx context.Context, changedReadBalance map[int64]*model.ReadAccount, batchEvent *BatchEvents, eventResults []*model.EventApplyResult) {
	idemKeyEventMap := make(map[string]*DecodedEvent)
	for _, de := range batchEvent.NewEvents {
		idemKeyEventMap[de.Event.IdempotencyKey] = de
	}

	idemKeySet := make(map[string]struct{})
	for _, result := range eventResults {
		if _, exists := idemKeySet[result.IdempotencyKey]; exists {
			continue
		}
		idemKeySet[result.IdempotencyKey] = struct{}{}
		createdMsc := idemKeyEventMap[result.IdempotencyKey].Event.CreatedMsec
		delayCnt, err := idemKeyEventMap[result.IdempotencyKey].Msg.GetMessageDelayCount()
		if err != nil {
			logger.GetLogger(ctx).Error().Err(err).Str("idemKey", result.IdempotencyKey).Msg("failed to get message delay count")
		}
		changeResults := map[string]string{
			"eventID":       result.EventID,
			"status":        strconv.Itoa(int(result.Status)),
			"idemKey":       result.IdempotencyKey,
			"rejectReason":  result.RejectReason,
			"createdMsec":   strconv.FormatInt(createdMsc, 10),
			"publishedMsec": strconv.FormatInt(time.Now().UnixMilli(), 10),
			"delayCount":    strconv.FormatInt(delayCnt, 10),
		}
		data, err := segmentioJson.Marshal(changeResults)
		if err != nil {
			continue
		}

		rp.Producer.AsyncPublish(ctx, &mq.ProducedMessage{
			Topic:   model.BalanceChangeResultTopic,
			Message: data,
		})
	}
}

func (rp *ResultPublisher) PublishStressTestStats(ctx context.Context, stats *model.StressTestStats) {
	stats.PublishedMsec = time.Now().UnixMilli()
	data, err := segmentioJson.Marshal(stats)
	if err != nil {
		logger.GetLogger(ctx).Error().Err(err).Msg("failed to marshal stress test stats")
		return
	}

	rp.Producer.AsyncPublish(ctx, &mq.ProducedMessage{
		Topic:   infra.GetConfig().Server.StressStatsTopic,
		Message: data,
	})
}
