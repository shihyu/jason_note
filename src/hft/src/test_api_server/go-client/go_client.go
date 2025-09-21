// Optimized Go client - simplified for better performance
package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"math"
	"net"
	"net/http"
	"runtime"
	"runtime/debug"
	"sort"
	"sync"
	"sync/atomic"
	"time"
)

// OrderRequest structure
type OrderRequest struct {
	BuySell         string  `json:"buy_sell"`
	Symbol          int     `json:"symbol"`
	Price           float64 `json:"price"`
	Quantity        int     `json:"quantity"`
	MarketType      string  `json:"market_type"`
	PriceType       string  `json:"price_type"`
	TimeInForce     string  `json:"time_in_force"`
	OrderType       string  `json:"order_type"`
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

// HFTClient structure
type HFTClient struct {
	client       *http.Client
	serverURL    string
	successCount atomic.Int64
	errorCount   atomic.Int64
	latencies    []float64
	latenciesMu  sync.Mutex
	semaphore    chan struct{}
}

// NewHFTClient creates an optimized client
func NewHFTClient(serverURL string, maxConnections int) *HFTClient {
	// Create transport with optimized settings
	transport := &http.Transport{
		MaxIdleConns:        maxConnections * 2,
		MaxConnsPerHost:     maxConnections,
		MaxIdleConnsPerHost: maxConnections,
		IdleConnTimeout:     90 * time.Second,
		DisableCompression:  true,
		ForceAttemptHTTP2:   false,
		DialContext: (&net.Dialer{
			Timeout:   5 * time.Second,
			KeepAlive: 30 * time.Second,
			DualStack: false,
		}).DialContext,
		DisableKeepAlives: false,
		TLSHandshakeTimeout: 5 * time.Second,
		ExpectContinueTimeout: 1 * time.Second,
		ResponseHeaderTimeout: 5 * time.Second,
		WriteBufferSize: 65536,
		ReadBufferSize:  65536,
	}

	client := &HFTClient{
		client: &http.Client{
			Transport: transport,
			Timeout:   10 * time.Second,
		},
		serverURL: serverURL,
		latencies: make([]float64, 0, 50000),
		semaphore: make(chan struct{}, maxConnections),
	}

	return client
}

// submitOrder submits a single order
func (c *HFTClient) submitOrder(orderID int, wg *sync.WaitGroup) {
	defer wg.Done()

	// Acquire semaphore
	c.semaphore <- struct{}{}
	defer func() { <-c.semaphore }()

	order := &OrderRequest{
		BuySell:         "buy",
		Symbol:          2881,
		Price:           66.0,
		Quantity:        2000,
		MarketType:      "common",
		PriceType:       "limit",
		TimeInForce:     "rod",
		OrderType:       "stock",
		ClientTimestamp: time.Now().UTC().Format(time.RFC3339Nano),
	}

	// Encode JSON
	jsonData, err := json.Marshal(order)
	if err != nil {
		c.errorCount.Add(1)
		return
	}

	startTime := time.Now()

	// Create and send request
	resp, err := c.client.Post(
		c.serverURL+"/order",
		"application/json",
		bytes.NewBuffer(jsonData),
	)

	if err != nil {
		c.errorCount.Add(1)
		return
	}
	defer resp.Body.Close()

	endTime := time.Now()
	roundTripTime := endTime.Sub(startTime).Seconds() * 1000

	if resp.StatusCode == http.StatusOK {
		c.successCount.Add(1)
		c.recordLatency(roundTripTime)
	} else {
		c.errorCount.Add(1)
	}
}

// recordLatency records a latency measurement
func (c *HFTClient) recordLatency(latency float64) {
	c.latenciesMu.Lock()
	c.latencies = append(c.latencies, latency)
	c.latenciesMu.Unlock()
}

// runTest executes the performance test
func (c *HFTClient) runTest(totalOrders, maxConcurrent, warmupOrders int) {
	fmt.Printf("Starting optimized test with %d total orders, %d concurrent connections, %d warmup orders\n",
		totalOrders, maxConcurrent, warmupOrders)

	// Warmup phase
	if warmupOrders > 0 {
		fmt.Printf("Warming up with %d orders...\n", warmupOrders)
		var warmupWg sync.WaitGroup
		warmupWg.Add(warmupOrders)

		for i := 0; i < warmupOrders; i++ {
			go c.submitOrder(i, &warmupWg)
		}
		warmupWg.Wait()

		// Reset stats after warmup
		c.successCount.Store(0)
		c.errorCount.Store(0)
		c.latenciesMu.Lock()
		c.latencies = c.latencies[:0]
		c.latenciesMu.Unlock()
	}

	// Main test phase
	fmt.Println("Starting main test...")
	var wg sync.WaitGroup
	wg.Add(totalOrders)

	startTime := time.Now()

	// Submit all orders using goroutines
	for i := 0; i < totalOrders; i++ {
		go c.submitOrder(warmupOrders+i, &wg)
	}

	// Wait for all orders to complete
	wg.Wait()

	endTime := time.Now()
	totalTime := endTime.Sub(startTime).Seconds()

	c.printStats(totalTime, totalOrders)
}

// printStats prints performance statistics
func (c *HFTClient) printStats(totalTime float64, totalOrders int) {
	success := c.successCount.Load()
	errors := c.errorCount.Load()

	fmt.Printf("\n=== Go Client Optimized ===\n")
	fmt.Printf("Features: Native goroutines, Connection pooling\n")
	fmt.Printf("Total orders: %d\n", totalOrders)
	fmt.Printf("Successful: %d\n", success)
	fmt.Printf("Errors: %d\n", errors)
	fmt.Printf("Total time: %.3f seconds\n", totalTime)
	fmt.Printf("Orders per second: %.2f\n", float64(success)/totalTime)

	c.latenciesMu.Lock()
	defer c.latenciesMu.Unlock()

	if len(c.latencies) > 0 {
		sort.Float64s(c.latencies)

		// Calculate statistics
		var sum float64
		for _, l := range c.latencies {
			sum += l
		}
		avg := sum / float64(len(c.latencies))

		// Calculate standard deviation
		var variance float64
		for _, l := range c.latencies {
			diff := l - avg
			variance += diff * diff
		}
		stdDev := math.Sqrt(variance / float64(len(c.latencies)))

		p50 := percentile(c.latencies, 50)
		p90 := percentile(c.latencies, 90)
		p95 := percentile(c.latencies, 95)
		p99 := percentile(c.latencies, 99)
		p999 := percentile(c.latencies, 99.9)

		fmt.Printf("\n=== Latency Statistics (ms) ===\n")
		fmt.Printf("Average: %.3f\n", avg)
		fmt.Printf("Std Dev: %.3f\n", stdDev)
		fmt.Printf("Min: %.3f\n", c.latencies[0])
		fmt.Printf("Max: %.3f\n", c.latencies[len(c.latencies)-1])
		fmt.Printf("P50: %.3f\n", p50)
		fmt.Printf("P90: %.3f\n", p90)
		fmt.Printf("P95: %.3f\n", p95)
		fmt.Printf("P99: %.3f\n", p99)
		fmt.Printf("P99.9: %.3f\n", p999)

		fmt.Printf("\nThroughput: %.2f orders/sec\n", float64(success)/totalTime)
		fmt.Printf("Success Rate: %.2f%%\n", float64(success)/float64(totalOrders)*100)
	}
}

// percentile calculates the percentile value from sorted slice
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

	// Handle positional arguments for compatibility
	if len(flag.Args()) == 3 {
		fmt.Sscanf(flag.Arg(0), "%d", orders)
		fmt.Sscanf(flag.Arg(1), "%d", connections)
		fmt.Sscanf(flag.Arg(2), "%d", warmup)
	}

	fmt.Printf("Go Optimized Client\n")
	fmt.Printf("CPU cores: %d, GOMAXPROCS: %d\n", runtime.NumCPU(), runtime.GOMAXPROCS(0))

	// Optimize GC for lower latency
	debug.SetGCPercent(100)
	debug.SetMemoryLimit(2 << 30) // 2GB memory limit

	client := NewHFTClient(*serverURL, *connections)
	client.runTest(*orders, *connections, *warmup)
}