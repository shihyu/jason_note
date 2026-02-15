package middleware

import "fmt"

type HandlerFunc func(ctx map[string]string) error

type Chain struct {
	handlers []HandlerFunc
}

func NewChain() *Chain {
	return &Chain{}
}

func (c *Chain) Use(fn HandlerFunc) {
	c.handlers = append(c.handlers, fn)
	fmt.Printf("  載入 middleware: %v\n", getFuncName(fn))
}

func (c *Chain) Execute(ctx map[string]string) error {
	for _, fn := range c.handlers {
		if err := fn(ctx); err != nil {
			return err
		}
	}
	return nil
}

func getFuncName(_ HandlerFunc) string {
	return "handler"
}

func Logger(ctx map[string]string) error {
	fmt.Println("    [middleware] logger")
	return nil
}

func Auth(ctx map[string]string) error {
	fmt.Println("    [middleware] auth check")
	return nil
}

func RateLimit(ctx map[string]string) error {
	fmt.Println("    [middleware] rate limit")
	return nil
}
