// HFT-optimized Go client
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
	"syscall"
	"time"

	"golang.org/x/sys/unix"
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

// Task represents a work unit
type Task struct {
	OrderID int
	Order   *OrderRequest
	Result  chan float64
}

// HFTClient structure
type HFTClient struct {
	client       *http.Client
	serverURL    string
	successCount atomic.Int64
	errorCount   atomic.Int64
	latencies    []float64
	latenciesMu  sync.Mutex
	workerPool   chan chan *Task
	taskQueue    chan *Task
}

// NewHFTClient creates an optimized client
func NewHFTClient(serverURL string, maxConnections int, numWorkers int) *HFTClient {
	// Set CPU affinity
	setCPUAffinity(0)

	// Optimize GC for low latency
	debug.SetGCPercent(100)

	// Lock memory
	unix.Mlockall(unix.MCL_CURRENT | unix.MCL_FUTURE)

	// Create transport with HFT optimizations
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
	}

	client := &HFTClient{
		client: &http.Client{
			Transport: transport,
			Timeout:   30 * time.Second,
		},
		serverURL:  serverURL,
		latencies:  make([]float64, 0, 50000),
		workerPool: make(chan chan *Task, numWorkers),
		taskQueue:  make(chan *Task, 10000),
	}

	// Start worker goroutines
	for i := 0; i < numWorkers; i++ {
		worker := NewWorker(i, client)
		worker.Start()
	}

	// Start dispatcher
	go client.dispatch()

	return client
}

// Worker represents a worker goroutine
type Worker struct {
	ID       int
	client   *HFTClient
	taskChan chan *Task
	quit     chan bool
}

// NewWorker creates a new worker
func NewWorker(id int, client *HFTClient) *Worker {
	return &Worker{
		ID:       id,
		client:   client,
		taskChan: make(chan *Task),
		quit:     make(chan bool),
	}
}

// Start begins processing tasks
func (w *Worker) Start() {
	go func() {
		// Set CPU affinity for this worker
		setCPUAffinity(w.ID % runtime.NumCPU())

		// Lock OS thread to prevent goroutine migration
		runtime.LockOSThread()
		defer runtime.UnlockOSThread()

		for {
			// Register worker as available
			w.client.workerPool <- w.taskChan

			select {
			case task := <-w.taskChan:
				w.processOrder(task)
			case <-w.quit:
				return
			}
		}
	}()
}

// processOrder handles a single order
func (w *Worker) processOrder(task *Task) {
	// Update timestamp
	task.Order.ClientTimestamp = time.Now().UTC().Format(time.RFC3339Nano)

	// Encode JSON
	jsonData, err := json.Marshal(task.Order)
	if err != nil {
		w.client.errorCount.Add(1)
		task.Result <- -1
		return
	}

	startTime := time.Now()

	// Create request
	req, err := http.NewRequest("POST", w.client.serverURL+"/order", bytes.NewBuffer(jsonData))
	if err != nil {
		w.client.errorCount.Add(1)
		task.Result <- -1
		return
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Connection", "keep-alive")

	resp, err := w.client.client.Do(req)
	if err != nil {
		w.client.errorCount.Add(1)
		task.Result <- -1
		return
	}
	defer resp.Body.Close()

	endTime := time.Now()
	roundTripTime := endTime.Sub(startTime).Seconds() * 1000

	if resp.StatusCode == http.StatusOK {
		w.client.successCount.Add(1)
		w.client.recordLatency(roundTripTime)
		task.Result <- roundTripTime
	} else {
		w.client.errorCount.Add(1)
		task.Result <- -1
	}
}

// dispatch distributes tasks to workers
func (c *HFTClient) dispatch() {
	for task := range c.taskQueue {
		// Get next available worker
		worker := <-c.workerPool
		// Send task to worker
		worker <- task
	}
}

// submitOrder submits an order using the worker pool
func (c *HFTClient) submitOrder(orderID int) <-chan float64 {
	task := &Task{
		OrderID: orderID,
		Order: &OrderRequest{
			BuySell:     "buy",
			Symbol:      2881,
			Price:       66.0,
			Quantity:    2000,
			MarketType:  "common",
			PriceType:   "limit",
			TimeInForce: "rod",
			OrderType:   "stock",
		},
		Result: make(chan float64, 1),
	}

	// Submit to queue
	c.taskQueue <- task

	return task.Result
}

// recordLatency records a latency measurement
func (c *HFTClient) recordLatency(latency float64) {
	c.latenciesMu.Lock()
	c.latencies = append(c.latencies, latency)
	c.latenciesMu.Unlock()
}

// runTest executes the performance test
func (c *HFTClient) runTest(totalOrders, maxConcurrent, warmupOrders int) {
	fmt.Printf("Starting HFT-optimized test with %d total orders, %d concurrent connections, %d warmup orders\n",
		totalOrders, maxConcurrent, warmupOrders)

	// Force GC before test
	runtime.GC()
	runtime.Gosched()

	// Warmup phase
	if warmupOrders > 0 {
		fmt.Printf("Warming up with %d orders...\n", warmupOrders)
		results := make([]<-chan float64, warmupOrders)

		for i := 0; i < warmupOrders; i++ {
			results[i] = c.submitOrder(i)
		}

		// Wait for warmup to complete
		for _, result := range results {
			<-result
		}

		// Reset stats
		c.successCount.Store(0)
		c.errorCount.Store(0)
		c.latenciesMu.Lock()
		c.latencies = c.latencies[:0]
		c.latenciesMu.Unlock()
	}

	// Main test phase
	fmt.Println("Starting main test...")
	startTime := time.Now()

	// Submit all orders
	results := make([]<-chan float64, totalOrders)
	for i := 0; i < totalOrders; i++ {
		results[i] = c.submitOrder(warmupOrders + i)
	}

	// Wait for all orders to complete
	for _, result := range results {
		<-result
	}

	endTime := time.Now()
	totalTime := endTime.Sub(startTime).Seconds()

	c.printStats(totalTime, totalOrders)
}

// printStats prints performance statistics
func (c *HFTClient) printStats(totalTime float64, totalOrders int) {
	success := c.successCount.Load()
	errors := c.errorCount.Load()

	fmt.Printf("\n=== Go Client HFT Optimized ===\n")
	fmt.Printf("Features: CPU affinity, Memory locking, Worker pool\n")
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

// setCPUAffinity sets the CPU affinity for the current thread
func setCPUAffinity(cpuID int) {
	var cpuSet unix.CPUSet
	cpuSet.Zero()
	cpuSet.Set(cpuID)

	// Get current thread ID
	tid := syscall.Gettid()

	// Set CPU affinity
	err := unix.SchedSetaffinity(tid, &cpuSet)
	if err != nil {
		// Silently ignore errors (may not have permission)
		return
	}
}

// setRealtimePriority attempts to set real-time scheduling priority
func main() {
	var (
		orders      = flag.Int("orders", 1000, "Total number of orders")
		connections = flag.Int("connections", 100, "Number of concurrent connections")
		warmup      = flag.Int("warmup", 100, "Number of warmup orders")
		serverURL   = flag.String("server", "http://127.0.0.1:8080", "Server URL")
		workers     = flag.Int("workers", 0, "Number of worker goroutines (0 = auto)")
	)
	flag.Parse()

	// Handle positional arguments for compatibility
	if len(flag.Args()) == 3 {
		fmt.Sscanf(flag.Arg(0), "%d", orders)
		fmt.Sscanf(flag.Arg(1), "%d", connections)
		fmt.Sscanf(flag.Arg(2), "%d", warmup)
	}

	// Auto-detect worker count
	numWorkers := *workers
	if numWorkers == 0 {
		numWorkers = runtime.NumCPU() * 2
		if numWorkers > *connections {
			numWorkers = *connections
		}
	}

	fmt.Printf("Go HFT Optimized Client\n")
	fmt.Printf("CPU cores: %d, Worker threads: %d\n", runtime.NumCPU(), numWorkers)

	// Set GOMAXPROCS to use all CPUs
	runtime.GOMAXPROCS(runtime.NumCPU())


	// Optimize GC
	debug.SetGCPercent(50) // More aggressive GC for lower latency

	client := NewHFTClient(*serverURL, *connections, numWorkers)
	client.runTest(*orders, *connections, *warmup)
}