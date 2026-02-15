// 帶函數追蹤的版本 — 顯示真實執行的函數呼叫路徑
package main

import (
	"fmt"
	"math/rand"
	"time"

	"github.com/demo/go-callgraph-demo/tracer"
)

// ===== Model =====

type User struct {
	ID   string
	Name string
}

type Order struct {
	ID      string
	UserID  string
	Product string
	Amount  float64
	Status  string
}

// ===== Util =====

func generateID(prefix string) string {
	defer tracer.Enter()()
	return fmt.Sprintf("%s-%04d", prefix, rand.Intn(10000))
}

// ===== Middleware =====

type HandlerFunc func(ctx map[string]string) error

type MiddlewareChain struct {
	handlers []HandlerFunc
}

func NewMiddlewareChain() *MiddlewareChain {
	defer tracer.Enter()()
	return &MiddlewareChain{}
}

func (c *MiddlewareChain) Use(fn HandlerFunc) {
	defer tracer.Enter()()
	c.handlers = append(c.handlers, fn)
}

func (c *MiddlewareChain) Execute(ctx map[string]string) error {
	defer tracer.Enter()()
	for _, fn := range c.handlers {
		if err := fn(ctx); err != nil {
			return err
		}
	}
	return nil
}

func LoggerMiddleware(ctx map[string]string) error {
	defer tracer.Enter()()
	return nil
}

func AuthMiddleware(ctx map[string]string) error {
	defer tracer.Enter()()
	return nil
}

func RateLimitMiddleware(ctx map[string]string) error {
	defer tracer.Enter()()
	return nil
}

// ===== App =====

type App struct {
	Name string
	mw   *MiddlewareChain
}

func NewApp(name string) *App {
	defer tracer.Enter()()
	return &App{
		Name: name,
		mw:   NewMiddlewareChain(),
	}
}

func (a *App) Init() {
	defer tracer.Enter()()
	a.mw.Use(LoggerMiddleware)
	a.mw.Use(AuthMiddleware)
	a.mw.Use(RateLimitMiddleware)
	a.setupRoutes()
}

func (a *App) setupRoutes() {
	defer tracer.Enter()()
}

func (a *App) HandleRequest(ctx map[string]string) error {
	defer tracer.Enter()()
	return a.mw.Execute(ctx)
}

func (a *App) Shutdown() {
	defer tracer.Enter()()
	a.cleanup()
}

func (a *App) cleanup() {
	defer tracer.Enter()()
}

// ===== UserService =====

type UserService struct {
	users map[string]*User
}

func NewUserService() *UserService {
	defer tracer.Enter()()
	return &UserService{users: make(map[string]*User)}
}

func (s *UserService) CreateUser(name string) *User {
	defer tracer.Enter()()
	id := generateID("user")
	user := &User{ID: id, Name: name}
	s.users[id] = user
	s.validate(user)
	return user
}

func (s *UserService) validate(user *User) {
	defer tracer.Enter()()
	if user.Name == "" {
		panic("user name cannot be empty")
	}
}

// ===== OrderService =====

type OrderService struct {
	orders []*Order
}

func NewOrderService() *OrderService {
	defer tracer.Enter()()
	return &OrderService{}
}

func (s *OrderService) PlaceOrder(userID, product string, amount float64) *Order {
	defer tracer.Enter()()
	order := &Order{
		ID:      generateID("order"),
		UserID:  userID,
		Product: product,
		Amount:  amount,
		Status:  "pending",
	}
	s.processPayment(order)
	s.orders = append(s.orders, order)
	return order
}

func (s *OrderService) processPayment(order *Order) {
	defer tracer.Enter()()
	if order.Amount > 0 {
		order.Status = "paid"
		s.notifyUser(order)
	}
}

func (s *OrderService) notifyUser(order *Order) {
	defer tracer.Enter()()
}

func (s *OrderService) GenerateReport() string {
	defer tracer.Enter()()
	total := 0.0
	for _, o := range s.orders {
		total += o.Amount
	}
	return fmt.Sprintf("共 %d 筆訂單, 總金額 $%.2f", len(s.orders), total)
}

// ===== main =====

func randomProduct() string {
	defer tracer.Enter()()
	products := []string{"手機", "筆電", "耳機", "鍵盤", "螢幕"}
	return products[rand.Intn(len(products))]
}

func main() {
	rand.New(rand.NewSource(time.Now().UnixNano()))

	app := NewApp("DemoApp")
	app.Init()

	// 模擬一個 request
	app.HandleRequest(map[string]string{"path": "/users"})

	userSvc := NewUserService()
	orderSvc := NewOrderService()

	// 只處理一個使用者，讓 trace 清晰
	user := userSvc.CreateUser("Alice")
	order := orderSvc.PlaceOrder(user.ID, randomProduct(), 599.99)
	_ = order

	report := orderSvc.GenerateReport()
	_ = report

	app.Shutdown()

	// 印出完整呼叫路徑
	tracer.PrintTrace()

	// 寫入檔案
	tracer.WriteTraceToFile("function-trace.md")
	fmt.Println("\n已寫入 function-trace.md")
}
