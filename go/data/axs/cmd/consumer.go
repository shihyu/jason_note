package cmd

import (
	"os"

	"github.com/spf13/cobra"
	app "github.com/vx416/axs/pkg/app"
)

// GrpcServerCmd is the command to start the gRPC server
var ConsumerServerCmd = &cobra.Command{
	Run: runConsumerServer,
	Use: "consumer",
}

func runConsumerServer(cmd *cobra.Command, args []string) {
	app := app.NewConsumerAPP(os.Getenv("AXS_CONFIG_NAME"))
	app.Run()
}
