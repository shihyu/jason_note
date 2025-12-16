package utils

import (
	"context"
	"errors"
	"runtime/debug"
	"sync"
	"sync/atomic"
	"time"

	"github.com/vx416/axs/pkg/logger"
	"go.uber.org/fx"
)

var (
	globalWorkerPool WorkerPool
	once             sync.Once
)

func WorkerPoolProvider(workerCount uint32, queueSize int, gracefulWaitTime time.Duration) func(lc fx.Lifecycle) (WorkerPool, error) {
	return func(lc fx.Lifecycle) (WorkerPool, error) {
		wp, err := InitAndRunGlobalWorkerPool(workerCount, queueSize)
		if err != nil {
			return nil, err
		}
		lc.Append(fx.Hook{
			OnStop: func(ctx context.Context) error {
				logger.GetLogger(ctx).Info().Msg("shutting down worker pool")
				err := wp.GracefulShutdown(gracefulWaitTime)
				if err != nil {
					logger.GetLogger(ctx).Error().Err(err).Msg("worker pool shutdown failed")
				} else {
					logger.GetLogger(ctx).Info().Msg("worker pool shutdown success")
				}
				return err
			},
		})
		return wp, nil
	}
}

func InitAndRunGlobalWorkerPool(workerCount uint32, queueSize int) (WorkerPool, error) {
	var err error
	once.Do(func() {
		globalWorkerPool = &workerPool{
			queue:       NewChQueue(queueSize),
			workerCount: workerCount,
		}
		err = globalWorkerPool.Run()
		if err != nil {
			return
		}
	})
	return globalWorkerPool, err
}

func GetGlobalWorkerPool() WorkerPool {
	return globalWorkerPool
}

type WorkerJob interface {
	Execute(ctx context.Context) error
}

// Worker interface
type WorkerPool interface {
	// GracefulShutdown shutdown worker pool gracefully
	//  note: this method will wait for all jobs done
	GracefulShutdown(to time.Duration) error
	// Run start worker pool
	Run() error
	// PushJob push job to queue
	PushJob(ctx context.Context, job WorkerJob) error
	WaitAllDone(waitTime time.Duration)
}

type JobMessage struct {
	ctx       context.Context
	job       WorkerJob
	StartTime time.Time
}

type workerPool struct {
	queue       Queue
	workerCount uint32
	wg          sync.WaitGroup
	closed      atomic.Int32
}

func (wp *workerPool) Run() error {
	for i := uint32(0); i < wp.workerCount; i++ {
		wp.wg.Add(1)
		go func(workerID uint32) {
			logger.GetLogger(context.Background()).Debug().Msgf("Worker %d started", workerID)
			defer wp.wg.Done()
			defer func() {
				if r := recover(); r != nil {

					logger.GetLogger(context.Background()).Error().Msgf("worker %d panicked: %v stack:%s", workerID, r, string(debug.Stack()))
				}
			}()
			for {
				jobMsg, ok := wp.queue.Pop()
				if !ok {
					logger.GetLogger(context.Background()).Info().Msgf("Worker %d stopped", workerID)
					return
				}
				err := jobMsg.job.Execute(jobMsg.ctx)
				if err != nil {
					logger.GetLogger(jobMsg.ctx).Error().Err(err).Msg("")
				}
			}
		}(i)
	}
	return nil
}

func (wp *workerPool) PushJob(ctx context.Context, job WorkerJob) error {
	if wp.closed.Load() == 1 {
		return errors.New("worker pool is closed")
	}
	return wp.queue.PushJob(JobMessage{
		ctx:       context.WithoutCancel(ctx),
		job:       job,
		StartTime: time.Now(),
	})
}

func (wp *workerPool) WaitAllDone(waitTime time.Duration) {
	for wp.queue.Len() > 0 {

	}
	time.Sleep(waitTime)
}

func (wp *workerPool) GracefulShutdown(to time.Duration) error {
	if !wp.closed.CompareAndSwap(0, 1) {
		return nil
	}
	wp.queue.Close()
	c := make(chan struct{})
	go func() {
		defer close(c)
		wp.wg.Wait()
	}()
	select {
	case <-c:
		return nil
	case <-time.After(to):
		return nil
	}
}

type Queue interface {
	PushJob(JobMessage) error
	Pop() (JobMessage, bool)
	Len() int
	Close()
}

// NewChQueue in memory channel queue, not support partition
func NewChQueue(size int) Queue {
	return chQueue(make(chan JobMessage, size))
}

type chQueue chan JobMessage

func (q chQueue) Len() int {
	return len(q)
}

func (q chQueue) PushJob(job JobMessage) error {
	q <- job
	return nil
}

func (q chQueue) Pop() (JobMessage, bool) {
	job, ok := <-q
	return job, ok
}

func (q chQueue) Close() {
	close(q)
}

type FuncJob func(ctx context.Context) error

func (job FuncJob) Execute(ctx context.Context) error {
	return job(ctx)
}
