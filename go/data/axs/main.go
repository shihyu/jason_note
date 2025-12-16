package main

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
	"github.com/vx416/axs/pkg/app"
)

var (
	// rootCmd is the root command for the application
	rootCmd = &cobra.Command{Use: "grpc or consumer server"}
)

// main is the entry point of the application
func main() {
	rootCmd.AddCommand(GrpcServerCmd, ConsumerServerCmd)
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

// GrpcServerCmd is the command to start the gRPC server
var ConsumerServerCmd = &cobra.Command{
	Run: func(cmd *cobra.Command, args []string) {
		app := app.NewConsumerAPP(os.Getenv("AXS_CONFIG_NAME"))
		app.Run()
	},
	Use: "consumer",
}

// GrpcServerCmd is the command to start the gRPC server
var GrpcServerCmd = &cobra.Command{
	Run: func(cmd *cobra.Command, args []string) {
		app := app.NewGrpcApiAPP(os.Getenv("AXS_CONFIG_NAME"))
		app.Run()
	},
	Use: "grpc",
}
