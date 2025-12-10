package cmd

import (
	"context"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/spf13/cobra"
	app "github.com/vx416/axs/pkg/app"
)

// GrpcServerCmd is the command to start the gRPC server
var GrpcServerCmd = &cobra.Command{
	Run: runGrpcServer,
	Use: "grpc",
}

func runGrpcServer(cmd *cobra.Command, args []string) {

	app := app.NewGrpcApiAPP(os.Getenv("AXS_CONFIG_NAME"))

	ctx := context.Background()
	// l := absol.DefaultLogger
	err := app.Start(ctx)
	if err != nil {
		// l.Errorf("start app failed, err:%+v", err)
		os.Exit(1)
	}

	sigterm := make(chan os.Signal, 1)
	signal.Notify(sigterm, syscall.SIGINT, syscall.SIGTERM)
	<-sigterm
	// l.Info("shutdown process start")
	stopCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if err := app.Stop(stopCtx); err != nil {
		// l.Errorf("shutdown process failed, err:%+v", err)
	}
}
