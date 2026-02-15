package main

import (
	"math/rand"
	"testing"

	"github.com/demo/go-callgraph-demo/service"
)

func BenchmarkFullWorkflow(b *testing.B) {
	for i := 0; i < b.N; i++ {
		userSvc := service.NewUserService()
		orderSvc := service.NewOrderService()

		users := []string{"Alice", "Bob", "Charlie"}
		for _, name := range users {
			user := userSvc.CreateUser(name)
			count := rand.Intn(3) + 1
			for j := 0; j < count; j++ {
				orderSvc.PlaceOrder(user.ID, "product", rand.Float64()*1000)
			}
		}
		orderSvc.GenerateReport()
	}
}
