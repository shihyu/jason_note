use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::Duration;
use crossbeam::queue::ArrayQueue;
use rand::Rng;
use libc::{cpu_set_t, CPU_SET, CPU_ZERO, pthread_setaffinity_np};
use std::mem;

#[repr(C, packed)]
#[derive(Clone, Copy)]
struct MarketData {
    timestamp: u64,
    bid: f64,
    ask: f64,
    volume: u64,
    symbol: [u8; 8],
}

#[repr(C, packed)]
#[derive(Clone, Copy)]
struct Order {
    id: u64,
    timestamp: u64,
    price: f64,
    quantity: u64,
    side: u8, // 'B' or 'S'
    symbol: [u8; 8],
}

struct HFTEngine {
    market_buffer: Arc<ArrayQueue<MarketData>>,
    order_buffer: Arc<ArrayQueue<Order>>,
    processed_orders: Arc<AtomicU64>,
    total_latency_ns: Arc<AtomicU64>,
    running: Arc<AtomicBool>,
    spread_threshold: f64,
}

impl HFTEngine {
    fn new() -> Self {
        HFTEngine {
            market_buffer: Arc::new(ArrayQueue::new(65536)),
            order_buffer: Arc::new(ArrayQueue::new(32768)),
            processed_orders: Arc::new(AtomicU64::new(0)),
            total_latency_ns: Arc::new(AtomicU64::new(0)),
            running: Arc::new(AtomicBool::new(true)),
            spread_threshold: 0.001,
        }
    }

    fn get_timestamp() -> u64 {
        use std::time::SystemTime;
        SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap()
            .as_nanos() as u64
    }

    fn set_cpu_affinity(cpu: usize) {
        unsafe {
            let mut cpuset: cpu_set_t = mem::zeroed();
            CPU_ZERO(&mut cpuset);
            CPU_SET(cpu, &mut cpuset);
            pthread_setaffinity_np(
                libc::pthread_self(),
                mem::size_of::<cpu_set_t>(),
                &cpuset,
            );
        }
    }

    fn process_market_data(&self, data: &MarketData) {
        let start_time = Self::get_timestamp();
        
        let spread = data.ask - data.bid;
        
        if spread > self.spread_threshold {
            let order_id = self.processed_orders.fetch_add(1, Ordering::Relaxed);
            
            let buy_order = Order {
                id: order_id,
                timestamp: Self::get_timestamp(),
                price: data.bid + 0.0001,
                quantity: 100,
                side: b'B',
                symbol: data.symbol,
            };
            
            let sell_order = Order {
                id: order_id + 1,
                timestamp: Self::get_timestamp(),
                price: data.ask - 0.0001,
                quantity: 100,
                side: b'S',
                symbol: data.symbol,
            };
            
            self.order_buffer.push(buy_order).ok();
            self.order_buffer.push(sell_order).ok();
            self.processed_orders.fetch_add(1, Ordering::Relaxed);
        }
        
        let end_time = Self::get_timestamp();
        self.total_latency_ns.fetch_add(end_time - start_time, Ordering::Relaxed);
    }

    fn market_data_generator(
        buffer: Arc<ArrayQueue<MarketData>>,
        running: Arc<AtomicBool>,
    ) {
        Self::set_cpu_affinity(2);
        
        let mut rng = rand::thread_rng();
        let symbol: [u8; 8] = *b"AAPL\0\0\0\0";
        
        while running.load(Ordering::Relaxed) {
            let mid_price = rng.gen_range(99.0..101.0);
            let data = MarketData {
                timestamp: Self::get_timestamp(),
                bid: mid_price - 0.001,
                ask: mid_price + 0.001,
                volume: rng.gen_range(100..10000),
                symbol,
            };
            
            buffer.push(data).ok();
            thread::sleep(Duration::from_micros(100));
        }
    }

    fn trading_loop(
        market_buffer: Arc<ArrayQueue<MarketData>>,
        order_buffer: Arc<ArrayQueue<Order>>,
        processed_orders: Arc<AtomicU64>,
        total_latency_ns: Arc<AtomicU64>,
        running: Arc<AtomicBool>,
    ) {
        Self::set_cpu_affinity(3);
        
        let engine = HFTEngine {
            market_buffer: market_buffer.clone(),
            order_buffer,
            processed_orders: processed_orders.clone(),
            total_latency_ns: total_latency_ns.clone(),
            running: running.clone(),
            spread_threshold: 0.001,
        };
        
        let mut messages_processed = 0u64;
        
        while running.load(Ordering::Relaxed) {
            if let Some(data) = market_buffer.pop() {
                engine.process_market_data(&data);
                messages_processed += 1;
                
                if messages_processed % 10000 == 0 {
                    let orders = processed_orders.load(Ordering::Relaxed);
                    if orders > 0 {
                        let avg_latency = total_latency_ns.load(Ordering::Relaxed) / orders;
                        println!(
                            "Processed: {} messages, {} orders, Avg latency: {} ns ({:.2} μs)",
                            messages_processed,
                            orders,
                            avg_latency,
                            avg_latency as f64 / 1000.0
                        );
                    }
                }
            }
        }
    }

    fn order_executor(
        order_buffer: Arc<ArrayQueue<Order>>,
        running: Arc<AtomicBool>,
    ) {
        Self::set_cpu_affinity(4);
        
        let mut executed_orders = 0u64;
        
        while running.load(Ordering::Relaxed) {
            if let Some(_order) = order_buffer.pop() {
                // Simulate order execution
                executed_orders += 1;
                
                if executed_orders % 1000 == 0 {
                    println!("Executed {} orders", executed_orders);
                }
            }
        }
    }

    fn run(&self, duration_seconds: u64) {
        println!("Starting Rust HFT Engine for {} seconds...", duration_seconds);
        
        let market_buffer = self.market_buffer.clone();
        let order_buffer = self.order_buffer.clone();
        let processed_orders = self.processed_orders.clone();
        let total_latency_ns = self.total_latency_ns.clone();
        let running = self.running.clone();
        
        let running_gen = running.clone();
        let market_thread = thread::spawn(move || {
            Self::market_data_generator(market_buffer, running_gen);
        });
        
        let market_buffer = self.market_buffer.clone();
        let running_trade = running.clone();
        let trading_thread = thread::spawn(move || {
            Self::trading_loop(
                market_buffer,
                order_buffer,
                processed_orders,
                total_latency_ns,
                running_trade,
            );
        });
        
        let order_buffer = self.order_buffer.clone();
        let running_exec = running.clone();
        let executor_thread = thread::spawn(move || {
            Self::order_executor(order_buffer, running_exec);
        });
        
        thread::sleep(Duration::from_secs(duration_seconds));
        
        self.running.store(false, Ordering::Relaxed);
        
        market_thread.join().unwrap();
        trading_thread.join().unwrap();
        executor_thread.join().unwrap();
        
        // Print final statistics
        println!("\n=== Final Statistics ===");
        let total_orders = self.processed_orders.load(Ordering::Relaxed);
        println!("Total orders processed: {}", total_orders);
        
        if total_orders > 0 {
            let avg_latency = self.total_latency_ns.load(Ordering::Relaxed) / total_orders;
            println!(
                "Average latency: {} ns ({:.2} μs)",
                avg_latency,
                avg_latency as f64 / 1000.0
            );
        }
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let duration = if args.len() > 1 {
        args[1].parse().unwrap_or(30)
    } else {
        30
    };
    
    println!("Rust High-Frequency Trading Simulator");
    println!("=====================================");
    
    let engine = HFTEngine::new();
    engine.run(duration);
}