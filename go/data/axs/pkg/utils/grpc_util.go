package utils

import (
	"context"
	"fmt"
	"time"

	"github.com/vx416/axs/pkg/logger"
	"google.golang.org/grpc"
	"google.golang.org/grpc/connectivity"
	"google.golang.org/grpc/credentials/insecure"
)

// NewGrpcClient creates a new gRPC client for the specified endpoint.
func NewGrpcClient[T any](endpoint string, newGrpcClient func(cc grpc.ClientConnInterface) T, opts ...grpc.DialOption) (T, error) {
	if endpoint == "" {
		var zero T
		return zero, fmt.Errorf("grpc endpoint is empty")
	}
	opts = append(opts,
		grpc.WithTransportCredentials(insecure.NewCredentials()), // 替代 WithTransportCredentials(creds)
		grpc.WithDefaultCallOptions(),
	)

	conn, err := grpc.NewClient(endpoint, opts...)
	if err != nil {
		var zero T
		return zero, err
	}
	conn.Connect()
	client := newGrpcClient(conn)
	retry := 0
	for {
		if conn.GetState() == connectivity.Ready {
			break
		}
		logger.GetLogger(context.Background()).Info().Msgf("waiting for grpc connection to be ready, current state: %s", conn.GetState().String())
		time.Sleep(200 * time.Millisecond)
		retry++
		if retry >= 10 {
			var zero T
			return zero, fmt.Errorf("failed to connect to grpc server: %s", endpoint)
		}
	}
	return client, nil
}
