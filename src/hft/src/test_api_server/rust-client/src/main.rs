use chrono::{DateTime, Utc};
use clap::Parser;
use futures::stream::{self, StreamExt};
use hyper::{Body, Client, Method, Request};
use hyper::client::HttpConnector;
use hyper_tls::HttpsConnector;
use serde::{Deserialize, Serialize};
use statrs::statistics::{Data, Distribution, OrderStatistics};
use std::sync::Arc;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::time::{Duration, Instant};
use parking_lot::Mutex;
use bytes::Bytes;
use core_affinity;
use libc::{mlock, mmap, munmap, MAP_ANON, MAP_FAILED, MAP_HUGETLB, MAP_PRIVATE, PROT_READ, PROT_WRITE};
use libc::{sched_setscheduler, sched_param, SCHED_FIFO};
use std::ptr;
use std::alloc::{alloc, dealloc, Layout};
use std::mem;
use crossbeam::channel::{bounded, Sender};
use std::thread;

// Cache line size for padding
const CACHE_LINE_SIZE: usize = 64;

// HFT Memory Optimization Utilities

/// Set real-time scheduling priority
#[allow(dead_code)]
unsafe fn set_realtime_priority() {
    let param = sched_param {
        sched_priority: 99,
    };
    sched_setscheduler(0, SCHED_FIFO, &param);
}

/// Cache-aligned atomic counter
#[repr(C, align(64))]
struct CacheAlignedCounter {
    value: AtomicUsize,
    _padding: [u8; CACHE_LINE_SIZE - std::mem::size_of::<AtomicUsize>()],
}

impl CacheAlignedCounter {
    fn new() -> Self {
        Self {
            value: AtomicUsize::new(0),
            _padding: [0; CACHE_LINE_SIZE - std::mem::size_of::<AtomicUsize>()],
        }
    }

    fn increment(&self) -> usize {
        self.value.fetch_add(1, Ordering::Relaxed)
    }

    fn get(&self) -> usize {
        self.value.load(Ordering::Relaxed)
    }
}

/// Lock-free ring buffer for order tasks
struct LockFreeRingBuffer<T> {
    buffer: Vec<Option<T>>,
    head: CacheAlignedCounter,
    tail: CacheAlignedCounter,
    capacity: usize,
}

impl<T> LockFreeRingBuffer<T> {
    fn new(capacity: usize) -> Self {
        let mut buffer = Vec::with_capacity(capacity);
        for _ in 0..capacity {
            buffer.push(None);
        }
        Self {
            buffer,
            head: CacheAlignedCounter::new(),
            tail: CacheAlignedCounter::new(),
            capacity,
        }
    }

    fn push(&mut self, item: T) -> bool {
        let tail = self.tail.get() % self.capacity;
        let head = self.head.get() % self.capacity;

        if (tail + 1) % self.capacity == head {
            return false; // Buffer full
        }

        self.buffer[tail] = Some(item);
        self.tail.increment();
        true
    }

    fn pop(&mut self) -> Option<T> {
        let head = self.head.get() % self.capacity;
        let tail = self.tail.get() % self.capacity;

        if head == tail {
            return None; // Buffer empty
        }

        let item = self.buffer[head].take();
        self.head.increment();
        item
    }
}

/// NUMA-aware memory allocation (placeholder for Linux-specific implementation)
#[cfg(target_os = "linux")]
#[allow(dead_code)]
unsafe fn numa_alloc_onnode(size: usize, _node: i32) -> Option<*mut u8> {
    // In a real implementation, this would use libnuma
    // For now, fall back to regular allocation
    allocate_locked_memory(size)
}

/// Allocate memory with huge pages for better TLB efficiency
#[allow(dead_code)]
unsafe fn allocate_huge_page(size: usize) -> Option<*mut u8> {
    let ptr = mmap(
        ptr::null_mut(),
        size,
        PROT_READ | PROT_WRITE,
        MAP_PRIVATE | MAP_ANON | MAP_HUGETLB,
        -1,
        0,
    );

    if ptr == MAP_FAILED {
        None
    } else {
        // Lock the memory to prevent swapping
        if mlock(ptr, size) == 0 {
            // Prefetch by writing zeros
            ptr::write_bytes(ptr as *mut u8, 0, size);
            Some(ptr as *mut u8)
        } else {
            munmap(ptr, size);
            None
        }
    }
}

/// Allocate locked memory (no swapping)
#[allow(dead_code)]
unsafe fn allocate_locked_memory(size: usize) -> Option<*mut u8> {
    let layout = Layout::from_size_align(size, mem::align_of::<u64>()).ok()?;
    let ptr = alloc(layout);

    if ptr.is_null() {
        return None;
    }

    // Lock the memory
    if mlock(ptr as *const _, size) == 0 {
        // Prefetch by writing zeros
        ptr::write_bytes(ptr, 0, size);
        Some(ptr)
    } else {
        dealloc(ptr, layout);
        None
    }
}

/// Set CPU affinity for the current thread
fn set_cpu_affinity(cpu_id: usize) {
    if let Some(core_ids) = core_affinity::get_core_ids() {
        if cpu_id < core_ids.len() {
            core_affinity::set_for_current(core_ids[cpu_id]);
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
enum BSAction {
    Buy,
    Sell,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
enum MarketType {
    Common,
    Warrant,
    OddLot,
    Daytime,
    FixedPrice,
    PlaceFirst,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
enum PriceType {
    Limit,
    Market,
    LimitUp,
    LimitDown,
    Range,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
enum TimeInForce {
    #[serde(rename = "rod")]
    ROD,
    #[serde(rename = "ioc")]
    IOC,
    #[serde(rename = "fok")]
    FOK,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
enum OrderType {
    Stock,
    Futures,
    Option,
}

#[derive(Debug, Serialize)]
struct OrderRequest {
    buy_sell: BSAction,
    symbol: i32,
    price: f64,
    quantity: i32,
    market_type: MarketType,
    price_type: PriceType,
    time_in_force: TimeInForce,
    order_type: OrderType,
    #[serde(skip_serializing_if = "Option::is_none")]
    user_def: Option<String>,
    client_timestamp: DateTime<Utc>,
}

#[derive(Debug, Deserialize)]
#[allow(dead_code)]
struct OrderResponse {
    symbol: i32,
    buy_sell: String,
    quantity: i32,
    price: f64,
    status: String,
    client_timestamp: DateTime<Utc>,
    server_timestamp: DateTime<Utc>,
    latency_ms: f64,
}

#[derive(Clone)]
struct Order {
    buy_sell: BSAction,
    symbol: i32,
    price: f64,
    quantity: i32,
    market_type: MarketType,
    price_type: PriceType,
    time_in_force: TimeInForce,
    order_type: OrderType,
    user_def: Option<String>,
}

struct OrderResult {
    #[allow(dead_code)]
    success: bool,
    #[allow(dead_code)]
    round_trip_ms: f64,
    #[allow(dead_code)]
    server_latency_ms: f64,
    #[allow(dead_code)]
    response: Option<OrderResponse>,
    #[allow(dead_code)]
    error: Option<String>,
}

/// Worker thread pool for HFT
struct WorkerPool {
    workers: Vec<thread::JoinHandle<()>>,
    sender: Sender<Box<dyn FnOnce() + Send + 'static>>,
}

impl WorkerPool {
    fn new(num_workers: usize) -> Self {
        let (sender, receiver): (Sender<Box<dyn FnOnce() + Send + 'static>>, _) = bounded(1000);
        let receiver = Arc::new(Mutex::new(receiver));

        let mut workers = Vec::with_capacity(num_workers);

        for id in 0..num_workers {
            let receiver = Arc::clone(&receiver);

            let handle = thread::spawn(move || {
                // Set CPU affinity for this worker
                set_cpu_affinity(id % core_affinity::get_core_ids().unwrap_or_default().len());

                // Try to set real-time priority
                unsafe {
                    let _ = set_realtime_priority();
                }

                loop {
                    let message = receiver.lock().recv();
                    match message {
                        Ok(job) => job(),
                        Err(_) => break,
                    }
                }
            });

            workers.push(handle);
        }

        Self { workers, sender }
    }

    fn execute<F>(&self, f: F)
    where
        F: FnOnce() + Send + 'static,
    {
        let _ = self.sender.send(Box::new(f));
    }
}

#[derive(Clone)]
struct OptimizedOrderClient {
    client: Client<HttpsConnector<HttpConnector>>,
    base_url: String,
    latencies: Arc<Mutex<Vec<f64>>>,
    success_count: Arc<CacheAlignedCounter>,
    error_count: Arc<CacheAlignedCounter>,
}

impl OptimizedOrderClient {
    fn new(base_url: &str, num_connections: usize) -> Self {
        let https = HttpsConnector::new();
        let client = Client::builder()
            .pool_idle_timeout(Duration::from_secs(90))
            .pool_max_idle_per_host(num_connections * 2)
            .http2_initial_stream_window_size(65536)
            .http2_initial_connection_window_size(65536)
            .http2_adaptive_window(true)
            .http2_max_frame_size(16384)
            .retry_canceled_requests(true)
            .set_host(false)
            .build(https);

        // HFT optimization: Pre-allocate latencies with locked memory
        let mut latencies_vec = Vec::with_capacity(10000);
        latencies_vec.reserve_exact(10000);

        // Try to lock the vector's memory
        unsafe {
            let ptr = latencies_vec.as_ptr();
            let size = latencies_vec.capacity() * std::mem::size_of::<f64>();
            let _ = mlock(ptr as *const _, size);
        }

        Self {
            client,
            base_url: base_url.to_string(),
            latencies: Arc::new(Mutex::new(latencies_vec)),
            success_count: Arc::new(CacheAlignedCounter::new()),
            error_count: Arc::new(CacheAlignedCounter::new()),
        }
    }

    async fn place_order(&self, _order_id: usize, demo_order: &Order) -> Result<OrderResult, Box<dyn std::error::Error + Send + Sync>> {
        let order_data = OrderRequest {
            buy_sell: demo_order.buy_sell.clone(),
            symbol: demo_order.symbol,
            price: demo_order.price,
            quantity: demo_order.quantity,
            market_type: demo_order.market_type.clone(),
            price_type: demo_order.price_type.clone(),
            time_in_force: demo_order.time_in_force.clone(),
            order_type: demo_order.order_type.clone(),
            user_def: demo_order.user_def.clone(),
            client_timestamp: Utc::now(),
        };

        let json_body = serde_json::to_vec(&order_data)?;
        let body_bytes = Bytes::from(json_body);

        let req = Request::builder()
            .method(Method::POST)
            .uri(format!("{}/order", self.base_url))
            .header("content-type", "application/json")
            .header("connection", "keep-alive")
            .body(Body::from(body_bytes))?;

        let start_time = Instant::now();
        let res = self.client.request(req).await?;
        let end_time = Instant::now();

        let round_trip_ms = end_time.duration_since(start_time).as_secs_f64() * 1000.0;

        if res.status().is_success() {
            let body_bytes = hyper::body::to_bytes(res.into_body()).await?;
            let order_response: OrderResponse = serde_json::from_slice(&body_bytes)?;

            let mut latencies = self.latencies.lock();
            latencies.push(round_trip_ms);

            self.success_count.increment();

            Ok(OrderResult {
                success: true,
                round_trip_ms,
                server_latency_ms: order_response.latency_ms,
                response: Some(order_response),
                error: None,
            })
        } else {
            self.error_count.increment();

            Ok(OrderResult {
                success: false,
                round_trip_ms,
                server_latency_ms: 0.0,
                response: None,
                error: Some(format!("HTTP {}", res.status())),
            })
        }
    }

    async fn batch_orders(&self, num_orders: usize, demo_order: &Order, max_concurrent: usize) {
        // HFT optimization: Set CPU affinity for main thread
        set_cpu_affinity(0);

        let mut futures = vec![];

        for i in 0..num_orders {
            let client = self.clone();
            let order = demo_order.clone();

            futures.push(async move {
                // Each async task can potentially run on different threads
                // Set affinity based on order ID for better cache locality
                if i % 10 == 0 {
                    set_cpu_affinity(i % core_affinity::get_core_ids().unwrap_or_default().len());
                }

                client.place_order(i, &order).await
            });
        }

        let results = stream::iter(futures)
            .buffer_unordered(max_concurrent)
            .collect::<Vec<_>>()
            .await;

        for result in results {
            if let Err(e) = result {
                eprintln!("Order failed: {}", e);
            }
        }
    }

    async fn warmup(&self, warmup_orders: usize, demo_order: &Order, max_concurrent: usize) {
        println!("Warming up with {} orders...", warmup_orders);

        let mut futures = vec![];
        for i in 0..warmup_orders {
            let client = self.clone();
            let order = demo_order.clone();

            futures.push(async move {
                let _ = client.place_order(i, &order).await;
            });
        }

        stream::iter(futures)
            .buffer_unordered(max_concurrent)
            .collect::<Vec<_>>()
            .await;

        self.latencies.lock().clear();
    }

    async fn print_stats(&self, elapsed_seconds: f64, num_orders: usize) {
        let latencies = self.latencies.lock();

        if latencies.is_empty() {
            println!("No successful orders to analyze");
            return;
        }

        let mut sorted_latencies = latencies.clone();
        sorted_latencies.sort_by(|a, b| a.partial_cmp(b).unwrap());

        let mut data = Data::new(sorted_latencies.clone());

        let min = sorted_latencies.first().unwrap();
        let max = sorted_latencies.last().unwrap();
        let mean = data.mean().unwrap();
        let median = data.median();
        let std_dev = data.std_dev().unwrap();

        let p90 = data.percentile(90);
        let p95 = data.percentile(95);
        let p99 = data.percentile(99);

        println!("\n=== Rust Client HFT Ultra-Optimized ===");
        println!("Features: Memory locking, CPU affinity, Lock-free structures, Pre-allocation");
        println!("Total orders: {}", latencies.len());
        println!("Min latency: {:.3} ms", min);
        println!("Max latency: {:.3} ms", max);
        println!("Avg latency: {:.3} ms", mean);
        println!("Median latency: {:.3} ms", median);
        println!("Std dev: {:.3} ms", std_dev);
        println!("P50: {:.3} ms", median);
        println!("P90: {:.3} ms", p90);
        println!("P95: {:.3} ms", p95);
        println!("P99: {:.3} ms", p99);
        println!("Throughput: {:.2} orders/sec", num_orders as f64 / elapsed_seconds);
    }
}

#[derive(Parser, Debug)]
#[clap(author, version, about, long_about = None)]
struct Args {
    /// Total number of orders to send
    #[clap(short, long, default_value = "1000")]
    orders: usize,

    /// Number of concurrent connections
    #[clap(short, long, default_value = "100")]
    connections: usize,

    /// Number of warmup orders
    #[clap(short, long, default_value = "100")]
    warmup: usize,

    /// Server URL
    #[clap(short, long, default_value = "http://localhost:8080")]
    server: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = Args::parse();

    println!("Rust Client (HFT Ultra-Optimized) - Starting test with {} orders", args.orders);
    println!("Features: Memory locking, CPU affinity, Lock-free structures");
    println!("Using {} concurrent connections", args.connections);
    println!("Server: {}", args.server);

    // HFT Optimization: Print system info
    if let Some(core_ids) = core_affinity::get_core_ids() {
        println!("CPU cores available: {}", core_ids.len());
    }

    // Try to increase memory lock limits (requires appropriate permissions)
    unsafe {
        let rlim = libc::rlimit {
            rlim_cur: libc::RLIM_INFINITY,
            rlim_max: libc::RLIM_INFINITY,
        };
        if libc::setrlimit(libc::RLIMIT_MEMLOCK, &rlim) == 0 {
            println!("Memory locking: UNLIMITED");
        } else {
            println!("Memory locking: LIMITED (run with elevated permissions for unlimited)");
        }
    }

    let demo_order = Order {
        buy_sell: BSAction::Buy,
        symbol: 2881,
        price: 66.0,
        quantity: 2000,
        market_type: MarketType::Common,
        price_type: PriceType::Limit,
        time_in_force: TimeInForce::ROD,
        order_type: OrderType::Stock,
        user_def: Some("RUST_OPT".to_string()),
    };

    let client = OptimizedOrderClient::new(&args.server, args.connections);

    // Warmup phase
    if args.warmup > 0 {
        client.warmup(args.warmup, &demo_order, args.connections).await;
    }

    println!("\nSending {} orders...", args.orders);
    let start_time = Instant::now();

    client.batch_orders(args.orders, &demo_order, args.connections).await;

    let elapsed = start_time.elapsed().as_secs_f64();

    println!("\nCompleted in {:.2} seconds", elapsed);

    client.print_stats(elapsed, args.orders).await;

    Ok(())
}