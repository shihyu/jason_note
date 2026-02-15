package server

import (
	"fmt"

	"github.com/demo/go-callgraph-demo/server/middleware"
)

type App struct {
	Name   string
	mw     *middleware.Chain
}

func NewApp(name string) *App {
	return &App{
		Name: name,
		mw:   middleware.NewChain(),
	}
}

func (a *App) Init() {
	fmt.Printf("[%s] 初始化中...\n", a.Name)
	a.mw.Use(middleware.Logger)
	a.mw.Use(middleware.Auth)
	a.mw.Use(middleware.RateLimit)
	a.setupRoutes()
	fmt.Printf("[%s] 初始化完成\n", a.Name)
}

func (a *App) setupRoutes() {
	fmt.Println("  設定路由: /users, /orders, /reports")
}

func (a *App) Shutdown() {
	fmt.Printf("[%s] 關閉中...\n", a.Name)
	a.cleanup()
	fmt.Printf("[%s] 已關閉\n", a.Name)
}

func (a *App) cleanup() {
	fmt.Println("  清理資源...")
}
