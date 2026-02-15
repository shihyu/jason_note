package service

import (
	"fmt"
	"strings"

	"github.com/demo/go-callgraph-demo/model"
	"github.com/demo/go-callgraph-demo/util"
)

type OrderService struct {
	orders []*model.Order
}

func NewOrderService() *OrderService {
	return &OrderService{}
}

func (s *OrderService) PlaceOrder(userID, product string, amount float64) *model.Order {
	order := &model.Order{
		ID:      util.GenerateID("order"),
		UserID:  userID,
		Product: product,
		Amount:  amount,
		Status:  "pending",
	}
	s.processPayment(order)
	s.orders = append(s.orders, order)
	return order
}

func (s *OrderService) processPayment(order *model.Order) {
	// 模擬付款流程
	if order.Amount > 0 {
		order.Status = "paid"
		s.notifyUser(order)
	}
}

func (s *OrderService) notifyUser(order *model.Order) {
	fmt.Printf("    [通知] 訂單 %s 已付款\n", order.ID)
}

func (s *OrderService) GenerateReport() string {
	var sb strings.Builder
	total := 0.0
	for _, o := range s.orders {
		sb.WriteString(fmt.Sprintf("  %s | %s | %s | $%.2f\n", o.ID, o.UserID, o.Product, o.Amount))
		total += o.Amount
	}
	sb.WriteString(fmt.Sprintf("  總計: %d 筆訂單, $%.2f\n", len(s.orders), total))
	return sb.String()
}
