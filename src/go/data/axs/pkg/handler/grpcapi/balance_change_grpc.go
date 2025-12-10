package grpcapi

import (
	"context"
	"fmt"
	"strconv"
	"sync/atomic"
	"time"

	"github.com/vx416/axs/pb/apipb"
	"github.com/vx416/axs/pb/eventpb"
	"github.com/vx416/axs/pkg/infra"
	"github.com/vx416/axs/pkg/logger"
	"github.com/vx416/axs/pkg/model"
	"github.com/vx416/axs/pkg/mq"
	"github.com/vx416/axs/pkg/utils"
	"google.golang.org/protobuf/proto"
)

var (
	reqCount          = int32(0)
	avgCostTimeMillis = int32(0)
)

func (api GrpcApi) BatchSubmitBalanceChanges(ctx context.Context, in *apipb.BatchSubmitBalanceChangesRequest) (*apipb.BatchSubmitBalanceChangesResponse, error) {
	start := time.Now()
	reqStartMsec := 0
	if len(in.Requests) > 0 {
		reqStartMsec = int(in.Requests[0].CreatedMsec)
	}
	defer func(end time.Time) {
		atomic.AddInt32(&reqCount, 1)
		// logger.GetLogger(ctx).Info().Msgf("BatchSubmitBalanceChanges processed %d requests in %d ms", len(in.Requests), time.Since(start).Milliseconds())
		if avgCostTimeMillis == 0 {
			atomic.AddInt32(&avgCostTimeMillis, int32(time.Since(start).Milliseconds()))
		} else {
			atomic.StoreInt32(&avgCostTimeMillis, (int32(time.Since(start).Milliseconds())+atomic.LoadInt32(&avgCostTimeMillis))/2)
		}
		if atomic.LoadInt32(&reqCount)%1000 == 0 {
			logger.GetLogger(ctx).Info().Msgf("Average processing time per BatchSubmitBalanceChanges call: %d ms", avgCostTimeMillis)
		}
		if end.UnixMilli()-int64(reqStartMsec) > 100 {
			logger.GetLogger(ctx).Warn().Msgf("BatchSubmitBalanceChanges request processing time %d ms exceeds 100 ms, request start msec: %d, end msec: %d", end.UnixMilli()-int64(reqStartMsec), reqStartMsec, end.UnixMilli())
		}
	}(time.Now())
	// logger.GetLogger(ctx).Info().Msg("Received BatchSubmitBalanceChanges gRPC request")
	accountIDs := make([]int64, 0, len(in.Requests))
	for _, change := range in.Requests {
		accountIDs = append(accountIDs, change.AccountId)
	}
	accountShardIDMap, err := api.dbRepo.GetAccountShardID(ctx, accountIDs)
	if err != nil {
		return nil, err
	}

	submittedMsec := time.Now().UnixMilli()
	responses := make([]*apipb.SubmitBalanceChangeResponse, len(in.Requests))
	for i, req := range in.Requests {
		shardID, ok := accountShardIDMap[req.AccountId]
		if !ok {
			logger.GetLogger(ctx).Error().Msgf("account shard ID not found for account ID %d", req.AccountId)
			responses[i] = &apipb.SubmitBalanceChangeResponse{
				EventId:        req.EventId,
				IdempotencyKey: req.IdempotencyKey,
				Status:         apipb.BalanceChangeEventStatus_Cancelled,
				ErrorMessage:   fmt.Sprintf("account shard ID not found for account ID %d", req.AccountId),
			}
			continue
		}
		err := api.processReq(ctx, req, shardID)
		if err != nil {
			responses[i] = &apipb.SubmitBalanceChangeResponse{
				EventId:        req.EventId,
				IdempotencyKey: req.IdempotencyKey,
				Status:         apipb.BalanceChangeEventStatus_Cancelled,
				ErrorMessage:   err.Error(),
			}
			continue
		}
		responses[i] = &apipb.SubmitBalanceChangeResponse{
			EventId:        req.EventId,
			IdempotencyKey: req.IdempotencyKey,
			Status:         apipb.BalanceChangeEventStatus_Init,
			SubmittedMsec:  submittedMsec,
		}
	}
	// logger.GetLogger(ctx).Info().Msg("Received BatchSubmitBalanceChanges gRPC request done")
	return &apipb.BatchSubmitBalanceChangesResponse{
		Responses: responses,
	}, nil
}

func (api GrpcApi) requestToEvent(req *apipb.SubmitBalanceChangeRequest, shardID int32) *eventpb.BalanceChangeEvent {
	if req == nil {
		return nil
	}

	changes := make([]*eventpb.BalanceChange, 0, len(req.Changes))
	for _, change := range req.Changes {
		changes = append(changes, &eventpb.BalanceChange{
			ChangeId:               change.ChangeId,
			CurrencyCode:           change.CurrencyCode,
			CurrencySymbol:         change.CurrencySymbol,
			AvailableDelta:         change.AvailableDelta,
			FrozenDelta:            change.FrozenDelta,
			FallbackCurrencyCode:   change.FallbackCurrencyCode,
			FallbackCurrencySymbol: change.FallbackCurrencySymbol,
			FallbackAvailableDelta: change.FallbackAvailableDelta,
			FallbackFrozenDelta:    change.FallbackFrozenDelta,
		})
	}

	return &eventpb.BalanceChangeEvent{
		EventId:        req.EventId,
		EventType:      req.EventType,
		EventTypeId:    req.EventTypeId,
		AccountId:      req.AccountId,
		UserId:         req.UserId,
		AccountShardId: shardID,
		SourceService:  req.SourceService,
		SourceSvcId:    req.SourceSvcId,
		RelatedOrderId: req.RelatedOrderId,
		IdempotencyKey: req.IdempotencyKey,
		CreatedMsec:    req.CreatedMsec,
		Changes:        changes,
	}
}

func (api GrpcApi) requestToBalanceChangeLog(req *apipb.SubmitBalanceChangeRequest, shardID int32) ([]*model.BalanceChangeLog, error) {
	if req == nil {
		return nil, nil
	}
	if len(req.Changes) == 0 {
		return nil, fmt.Errorf("no balance changes in request")
	}

	logs := make([]*model.BalanceChangeLog, 0, len(req.Changes))
	for _, change := range req.Changes {
		log, err := model.NewInitBalanceChangeLog(
			req.EventId,
			req.EventTypeId,
			req.IdempotencyKey,
			change.ChangeId,
			req.AccountId,
			shardID,
			req.UserId,
			change.CurrencyCode,
			change.CurrencySymbol,
			change.AvailableDelta,
			change.FrozenDelta,
			change.FallbackCurrencyCode,
			change.FallbackCurrencySymbol,
			change.FallbackAvailableDelta,
			change.FallbackFrozenDelta,
			req.SourceSvcId,
			req.RelatedOrderId,
			model.TimestampInMsec(req.CreatedMsec),
		)
		if err != nil {
			return nil, err
		}
		logs = append(logs, log)
	}

	return logs, nil
}

func (api GrpcApi) processReq(ctx context.Context, req *apipb.SubmitBalanceChangeRequest, shardID int32) error {
	event := api.requestToEvent(req, shardID)
	eventPayload, err := proto.Marshal(event)
	if err != nil {
		return fmt.Errorf("failed to marshal event: %w", err)
	}
	maxPartition := infra.GetConfig().Kafka.BalanceChangeTopicPartitions
	if maxPartition <= 0 {
		return fmt.Errorf("invalid balance change topic partitions: %d", maxPartition)
	}
	partition := int32(shardID % int32(maxPartition))
	mqMsg := &mq.ProducedMessage{
		Topic:   model.BalanceChangeEventTopic,
		Message: eventPayload,
		Header: map[string][]byte{
			"eventID":         []byte(req.EventId),
			"upstreamService": []byte(req.SourceService),
			"producedMsec":    []byte(strconv.FormatInt(time.Now().UnixMilli(), 10)),
			"createdMsec":     []byte(strconv.FormatInt(req.CreatedMsec, 10)),
		},
		Partition: utils.Ptr(partition),
	}

	logs, err := api.requestToBalanceChangeLog(req, shardID)
	if err != nil {
		return err
	}
	if len(logs) == 0 {
		return fmt.Errorf("no balance change logs to process")
	}
	_, err = api.dbRepo.InsertBalanceChangeLogs(context.Background(), logs)
	if err != nil {
		return err
	}

	idempotencyKey := req.IdempotencyKey
	err = api.workerPool.PushJob(ctx, utils.FuncJob(func(ctx context.Context) error {
		ctx, cancel := context.WithTimeout(ctx, 3*time.Second)
		defer cancel()
		start := time.Now()
		res := api.producer.Publish(ctx, mqMsg)
		if len(res) != 1 {
			return fmt.Errorf("unexpected produced message result length: %d", len(res))
		}
		mqMsg := res[0]
		if mqMsg.Error != nil {
			return fmt.Errorf("failed to publish balance change event message: %w", mqMsg.Error)
		}
		if time.Since(start) > 50*time.Millisecond {
			logger.GetLogger(ctx).Info().Msgf("Published balance change event message for idempotency key %s to partition %d at offset %d in %d ms", idempotencyKey, mqMsg.Partition, mqMsg.Offset, time.Since(start).Milliseconds())
		}
		updateData := map[string]any{
			"kafka_partition": mqMsg.Partition,
			"kafka_offset":    mqMsg.Offset,
		}
		err = api.dbRepo.UpdateChangeLog(ctx, idempotencyKey, updateData)
		if err != nil {
			return fmt.Errorf("failed to update change log for idempotency key %s: %w", idempotencyKey, err)
		}
		return nil
	}))
	return err
}
