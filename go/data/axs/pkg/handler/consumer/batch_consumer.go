package consumer

import (
	"context"
	"fmt"
	"strings"
	"sync"
	"time"

	"github.com/vx416/axs/pkg/logger"
	"github.com/vx416/axs/pkg/mq"
	"github.com/vx416/axs/pkg/service/svcerr"
	"github.com/vx416/axs/pkg/utils"
)

type EventProcesser interface {
	ProcessEvents(ctx context.Context, msgs []mq.ConsumedMessage) error
	// Dead Letter Queue (DLQ)
	ProcessEventsErr(ctx context.Context, msgs []mq.ConsumedMessage, err error)
}

func NewBatchEventConsumer(mqReader mq.ConsumerReader, handler EventProcesser, batchSize int, batchingDelay, maxReadTimeout time.Duration) *BatchEventConsumer {
	cctx, cancelFunc := context.WithCancel(context.Background())
	return &BatchEventConsumer{
		batchSize:      batchSize,
		batchingDelay:  batchingDelay,
		maxReadTimeout: maxReadTimeout,
		mqReader:       mqReader,
		handler:        handler,
		ctx:            cctx,
		closeFunc:      cancelFunc,
		processTimeout: 3 * time.Second,
	}
}

type BatchEventConsumer struct {
	batchSize      int
	batchingDelay  time.Duration
	maxReadTimeout time.Duration
	mqReader       mq.ConsumerReader
	handler        EventProcesser
	ctx            context.Context
	closeFunc      context.CancelFunc
	wg             sync.WaitGroup
	processTimeout time.Duration
}

func (c *BatchEventConsumer) StartConsuming() {
	c.wg.Add(1)
	defer c.wg.Done()
	readTimeout := c.maxReadTimeout
	batchMsg := make([]mq.ConsumedMessage, 0, c.batchSize)
	for {
		newCtx, newCtxCancel := context.WithTimeout(context.Background(), c.processTimeout)
		select {
		case <-c.ctx.Done():
			if len(batchMsg) > 0 {
				err := c.handler.ProcessEvents(newCtx, batchMsg)
				if err != nil {
					c.handleErr(newCtx, err, batchMsg)
				}
			}
			newCtxCancel()
			return
		default:
		}
		msg, err := c.mqReader.ReadMessage(newCtx, readTimeout)
		newCtx = c.setLogger(newCtx, msg)
		if err != nil {
			if mq.IsTimeoutError(err) {
				if len(batchMsg) > 0 {
					err := c.handler.ProcessEvents(newCtx, batchMsg)
					if err != nil {
						c.handleErr(newCtx, err, batchMsg)
					}
					logger.GetLogger(newCtx).Debug().Msgf("batch processed due to timeout, batch size: %d", len(batchMsg))
					batchMsg = batchMsg[:0]
				}
				readTimeout = c.maxReadTimeout
				newCtxCancel()
				continue
			}
			logger.GetLogger(newCtx).Error().Err(err).Msg("failed to read message from mq")
			newCtxCancel()
			continue
		}
		logger.GetLogger(newCtx).Debug().
			Str("topic", msg.GetTopic()).
			Int32("partition", msg.GetPartition()).
			Int64("offset", msg.GetOffset()).Msg("receive message")

		readTimeout = c.batchingDelay
		batchMsg = append(batchMsg, msg)
		if len(batchMsg) >= c.batchSize {
			err := c.handler.ProcessEvents(newCtx, batchMsg)
			if err != nil {
				c.handleErr(newCtx, err, batchMsg)
			}
			batchMsg = batchMsg[:0]
			readTimeout = c.maxReadTimeout
			logger.GetLogger(newCtx).Debug().Msgf("batch processed due to reach batch size, batch size: %d", len(batchMsg))
		}
		newCtxCancel()
	}
}

func (c *BatchEventConsumer) GracefulShutdown(timeout time.Duration) error {
	c.closeFunc()
	var findErr error
	closeChan := make(chan struct{})
	go func() {
		c.wg.Wait()
		close(closeChan)
	}()

	timeoutChan := time.After(timeout)
	select {
	case <-closeChan:
		// graceful shutdown completed
	case <-timeoutChan:
		findErr = utils.JoinErrors(findErr, fmt.Errorf("graceful shutdown timeout after %s", timeout.String()))
	}

	err := c.mqReader.CommitAndClose(timeout)
	if err != nil {
		if !strings.Contains(err.Error(), "No offset stored") {
			findErr = utils.JoinErrors(findErr, err)
		}
	}
	return findErr
}

func (c *BatchEventConsumer) handleErr(ctx context.Context, err error, batchMsgs []mq.ConsumedMessage) {
	if svcerr.IsStopConsumingError(err) {
		logger.GetLogger(ctx).Warn().Err(err).Msg("stop consuming messages as instructed")
		err = c.GracefulShutdown(5 * time.Second)
		if err != nil {
			logger.GetLogger(ctx).Error().Err(err).Msg("error during graceful shutdown")
		}
		return
	}

	if svcerr.IsNeedRetryError(err) {
		retryErr := utils.Retry(func() (bool, error) {
			return true, c.handler.ProcessEvents(ctx, batchMsgs)
		})
		if retryErr != nil {
			c.handler.ProcessEventsErr(ctx, batchMsgs, retryErr)
		}
		return
	}
	c.handler.ProcessEventsErr(ctx, batchMsgs, err)
}

func (c *BatchEventConsumer) setLogger(ctx context.Context, msg mq.ConsumedMessage) context.Context {
	if msg == nil {
		return ctx
	}
	loggerWithFields := logger.GetLogger(ctx).With().
		Str("topic", msg.GetTopic()).
		Int32("partition", msg.GetPartition()).
		Int64("offset", msg.GetOffset()).
		Logger()
	loggerWithFields.Debug().Msg("receive msg")

	return loggerWithFields.WithContext(ctx)
}
