package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"net/http"
	"sort"
	"sync"
	"sync/atomic"
	"time"
)

type OrderRequest struct {
	BuySell         string  `json:"buy_sell"`
	Symbol          int     `json:"symbol"`
	Price           float64 `json:"price"`
	Quantity        int     `json:"quantity"`
	MarketType      string  `json:"market_type"`
	PriceType       string  `json:"price_type"`
	TimeInForce     string  `json:"time_in_force"`
	OrderType       string  `json:"order_type"`
	UserDef         string  `json:"user_def,omitempty"`
	ClientTimestamp string  `json:"client_timestamp"`
}

type OrderResponse struct {
	Symbol          int     `json:"symbol"`
	BuySell         string  `json:"buy_sell"`
	Quantity        int     `json:"quantity"`
	Price           float64 `json:"price"`
	Status          string  `json:"status"`
	ClientTimestamp string  `json:"client_timestamp"`
	ServerTimestamp string  `json:"server_timestamp"`
	LatencyMs       float64 `json:"latency_ms"`
}

type StatsResponse struct {
	TotalOrders      int     `json:"total_orders"`
	ElapsedSeconds   float64 `json:"elapsed_seconds"`
	OrdersPerSecond  float64 `json:"orders_per_second"`
}

type Client struct {
	client      *http.Client
	serverURL   string
	successCount int64
	errorCount   int64
	latencies    []float64
	mu           sync.Mutex
}

func NewClient(serverURL string, maxConnections int) *Client {
	transport := &http.Transport{
		MaxIdleConns:        maxConnections,
		MaxConnsPerHost:     maxConnections,
		MaxIdleConnsPerHost: maxConnections,
		IdleConnTimeout:     90 * time.Second,
		DisableCompression:  true,
	}

	return &Client{
		client: &http.Client{
			Transport: transport,
			Timeout:   30 * time.Second,
		},
		serverURL: serverURL,
		latencies: make([]float64, 0),
	}
}

func (c *Client) sendOrder(orderID int) (float64, error) {
	order := OrderRequest{
		BuySell:         "buy",
		Symbol:          2881, // 統一使用相同股票代碼
		Price:           66.0,
		Quantity:        2000,
		MarketType:      "common",
		PriceType:       "limit",
		TimeInForce:     "rod",
		OrderType:       "stock",
		UserDef:         fmt.Sprintf("ORDER_%06d", orderID),
		ClientTimestamp: time.Now().UTC().Format(time.RFC3339Nano),
	}

	jsonData, err := json.Marshal(order)
	if err != nil {
		return 0, err
	}

	startTime := time.Now()
	resp, err := c.client.Post(c.serverURL+"/order", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return 0, err
	}
	defer resp.Body.Close()

	endTime := time.Now()
	roundTripTime := endTime.Sub(startTime).Seconds() * 1000 // Convert to milliseconds

	if resp.StatusCode != http.StatusOK {
		return 0, fmt.Errorf("server returned status %d", resp.StatusCode)
	}

	var orderResp OrderResponse
	if err := json.NewDecoder(resp.Body).Decode(&orderResp); err != nil {
		return 0, err
	}

	return roundTripTime, nil
}

func (c *Client) runTest(totalOrders, maxConcurrent, warmupOrders int) {
	fmt.Printf("Starting test with %d total orders, %d concurrent connections, %d warmup orders\n",
		totalOrders, maxConcurrent, warmupOrders)

	// Warmup phase
	fmt.Printf("Warming up with %d orders...\n", warmupOrders)
	var warmupWg sync.WaitGroup
	warmupSem := make(chan struct{}, maxConcurrent)

	for i := 0; i < warmupOrders; i++ {
		warmupWg.Add(1)
		warmupSem <- struct{}{}
		go func(orderID int) {
			defer warmupWg.Done()
			defer func() { <-warmupSem }()
			c.sendOrder(orderID)
		}(i)
	}
	warmupWg.Wait()

	// Reset stats
	atomic.StoreInt64(&c.successCount, 0)
	atomic.StoreInt64(&c.errorCount, 0)
	c.mu.Lock()
	c.latencies = c.latencies[:0]
	c.mu.Unlock()

	// Main test phase
	fmt.Println("Starting main test...")
	var wg sync.WaitGroup
	sem := make(chan struct{}, maxConcurrent)
	startTime := time.Now()

	for i := 0; i < totalOrders; i++ {
		wg.Add(1)
		sem <- struct{}{} // Acquire semaphore

		go func(orderID int) {
			defer wg.Done()
			defer func() { <-sem }() // Release semaphore

			latency, err := c.sendOrder(warmupOrders + orderID)
			if err != nil {
				atomic.AddInt64(&c.errorCount, 1)
				fmt.Printf("Error sending order %d: %v\n", orderID, err)
			} else {
				atomic.AddInt64(&c.successCount, 1)
				c.mu.Lock()
				c.latencies = append(c.latencies, latency)
				c.mu.Unlock()
			}
		}(i)
	}

	wg.Wait()
	endTime := time.Now()
	totalTime := endTime.Sub(startTime).Seconds()

	c.printStats(totalTime, totalOrders)
}

func (c *Client) printStats(totalTime float64, totalOrders int) {
	success := atomic.LoadInt64(&c.successCount)
	errors := atomic.LoadInt64(&c.errorCount)

	fmt.Printf("\n=== Test Results ===\n")
	fmt.Printf("Total orders: %d\n", totalOrders)
	fmt.Printf("Successful: %d\n", success)
	fmt.Printf("Errors: %d\n", errors)
	fmt.Printf("Total time: %.3f seconds\n", totalTime)
	fmt.Printf("Orders per second: %.2f\n", float64(success)/totalTime)

	c.mu.Lock()
	defer c.mu.Unlock()

	if len(c.latencies) > 0 {
		sort.Float64s(c.latencies)

		// Calculate statistics
		var sum float64
		for _, l := range c.latencies {
			sum += l
		}
		avg := sum / float64(len(c.latencies))

		p50 := percentile(c.latencies, 50)
		p90 := percentile(c.latencies, 90)
		p95 := percentile(c.latencies, 95)
		p99 := percentile(c.latencies, 99)

		fmt.Printf("\n=== Latency Statistics (ms) ===\n")
		fmt.Printf("Average: %.3f\n", avg)
		fmt.Printf("Min: %.3f\n", c.latencies[0])
		fmt.Printf("Max: %.3f\n", c.latencies[len(c.latencies)-1])
		fmt.Printf("P50: %.3f\n", p50)
		fmt.Printf("P90: %.3f\n", p90)
		fmt.Printf("P95: %.3f\n", p95)
		fmt.Printf("P99: %.3f\n", p99)

		// Print in format for compare_performance.py
		fmt.Printf("\nPerformance Summary:\n")
		fmt.Printf("Throughput: %.2f orders/sec\n", float64(success)/totalTime)
		fmt.Printf("Latency P50: %.3f ms\n", p50)
		fmt.Printf("Latency P90: %.3f ms\n", p90)
		fmt.Printf("Latency P95: %.3f ms\n", p95)
		fmt.Printf("Latency P99: %.3f ms\n", p99)
		fmt.Printf("Success Rate: %.2f%%\n", float64(success)/float64(totalOrders)*100)
	}
}

func percentile(sorted []float64, p float64) float64 {
	if len(sorted) == 0 {
		return 0
	}

	rank := p / 100 * float64(len(sorted)-1)
	lowerIndex := int(rank)
	upperIndex := lowerIndex + 1

	if upperIndex >= len(sorted) {
		return sorted[len(sorted)-1]
	}

	lowerValue := sorted[lowerIndex]
	upperValue := sorted[upperIndex]
	weight := rank - float64(lowerIndex)

	return lowerValue + weight*(upperValue-lowerValue)
}

func main() {
	var (
		orders      = flag.Int("orders", 1000, "Total number of orders")
		connections = flag.Int("connections", 100, "Number of concurrent connections")
		warmup      = flag.Int("warmup", 100, "Number of warmup orders")
		serverURL   = flag.String("server", "http://127.0.0.1:8080", "Server URL")
	)
	flag.Parse()

	if len(flag.Args()) == 3 {
		// Support positional arguments for compatibility
		fmt.Sscanf(flag.Arg(0), "%d", orders)
		fmt.Sscanf(flag.Arg(1), "%d", connections)
		fmt.Sscanf(flag.Arg(2), "%d", warmup)
	}

	client := NewClient(*serverURL, *connections)
	client.runTest(*orders, *connections, *warmup)
}