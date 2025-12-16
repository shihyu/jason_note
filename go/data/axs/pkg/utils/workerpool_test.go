package utils_test

import (
	"context"
	"sync/atomic"
	"testing"
	"time"

	"github.com/stretchr/testify/require"
	"github.com/vx416/axs/pkg/utils"
)

func TestWorkerPool(t *testing.T) {
	wp, err := utils.InitAndRunGlobalWorkerPool(5, 100)
	require.NoError(t, err, "failed to init worker pool")

	val := atomic.Int32{}
	for range 20 {
		err = wp.PushJob(t.Context(), utils.FuncJob(func(ctx context.Context) error {
			val.Add(1)
			return nil
		}))
		require.NoError(t, err, "failed to push job to worker pool")
	}
	err = wp.GracefulShutdown(3 * time.Second)
	require.Equal(t, 20, int(val.Load()))
	require.NoError(t, err, "failed to shutdown worker pool")
}
