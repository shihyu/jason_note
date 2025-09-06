use chrono::{DateTime, Utc};
use clap::Parser;
use futures::stream::{self, StreamExt};
use reqwest::Client;
use serde::{Deserialize, Serialize};
use statrs::statistics::{Data, OrderStatistics};
use std::sync::Arc;
use std::time::{Duration, Instant};
use tokio::sync::Mutex;

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
struct AsyncOrderClient {
    client: Client,
    base_url: String,
    latencies: Arc<Mutex<Vec<f64>>>,
}

impl AsyncOrderClient {
    fn new(base_url: &str, num_connections: usize) -> Self {
        let client = Client::builder()
            .pool_max_idle_per_host(num_connections)
            .pool_idle_timeout(Duration::from_secs(30))
            .timeout(Duration::from_secs(30))
            .build()
            .expect("Failed to build HTTP client");

        Self {
            client,
            base_url: base_url.to_string(),
            latencies: Arc::new(Mutex::new(Vec::new())),
        }
    }

    async fn place_order(&self, _order_id: usize, demo_order: &Order) -> Result<OrderResult, Box<dyn std::error::Error>> {
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

        let start_time = Instant::now();
        
        let response = self
            .client
            .post(format!("{}/order", self.base_url))
            .json(&order_data)
            .send()
            .await?;

        let end_time = Instant::now();
        let round_trip_ms = end_time.duration_since(start_time).as_secs_f64() * 1000.0;

        if response.status().is_success() {
            let order_response: OrderResponse = response.json().await?;
            
            let mut latencies = self.latencies.lock().await;
            latencies.push(round_trip_ms);

            Ok(OrderResult {
                success: true,
                round_trip_ms,
                server_latency_ms: order_response.latency_ms,
                response: Some(order_response),
                error: None,
            })
        } else {
            Ok(OrderResult {
                success: false,
                round_trip_ms,
                server_latency_ms: 0.0,
                response: None,
                error: Some(format!("HTTP {}", response.status())),
            })
        }
    }

    async fn batch_orders(&self, num_orders: usize, concurrent: usize, demo_order: &Order) -> Vec<OrderResult> {
        let futures = (0..num_orders).map(|i| {
            let client = self.clone();
            let order = demo_order.clone();
            async move {
                match client.place_order(i, &order).await {
                    Ok(result) => result,
                    Err(e) => OrderResult {
                        success: false,
                        round_trip_ms: 0.0,
                        server_latency_ms: 0.0,
                        response: None,
                        error: Some(e.to_string()),
                    },
                }
            }
        });

        stream::iter(futures)
            .buffer_unordered(concurrent)
            .collect()
            .await
    }

    async fn print_stats(&self) {
        let latencies = self.latencies.lock().await;
        
        if latencies.is_empty() {
            println!("No successful orders to analyze");
            return;
        }

        let mut data = Data::new(latencies.clone());
        
        println!("\n=== Rust Client Performance Stats ===");
        println!("Total orders: {}", latencies.len());
        let min = latencies.iter().cloned().fold(f64::INFINITY, f64::min);
        let max = latencies.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
        let mean = latencies.iter().sum::<f64>() / latencies.len() as f64;
        let median = data.median();
        let variance = latencies.iter().map(|x| (x - mean).powi(2)).sum::<f64>() / latencies.len() as f64;
        let std_dev = variance.sqrt();
        
        println!("Min latency: {:.2} ms", min);
        println!("Max latency: {:.2} ms", max);
        println!("Avg latency: {:.2} ms", mean);
        println!("Median latency: {:.2} ms", median);
        println!("Std dev: {:.2} ms", std_dev);

        // Percentiles
        let percentiles = vec![50, 90, 95, 99];
        for p in percentiles {
            if latencies.len() >= 100 || (p <= 95 && latencies.len() >= 20) {
                let percentile = data.percentile(p);
                println!("P{}: {:.2} ms", p, percentile);
            }
        }
    }
}

#[derive(Debug)]
#[allow(dead_code)]
struct OrderResult {
    success: bool,
    round_trip_ms: f64,
    server_latency_ms: f64,
    response: Option<OrderResponse>,
    error: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
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

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    #[arg(long, default_value_t = 1000)]
    orders: usize,

    #[arg(long, default_value_t = 100)]
    connections: usize,

    #[arg(long, default_value_t = 100)]
    warmup: usize,
}

async fn run_test(num_orders: usize, num_connections: usize, warmup: usize) {
    let client = AsyncOrderClient::new("http://localhost:8080", num_connections);

    println!("Rust Async Client - Starting test with {} orders", num_orders);
    println!("Using {} concurrent connections", num_connections);
    
    // Create demo Taiwan stock order
    let demo_order = Order {
        buy_sell: BSAction::Buy,
        symbol: 2881,
        price: 66.0,
        quantity: 2000,
        market_type: MarketType::Common,
        price_type: PriceType::Limit,
        time_in_force: TimeInForce::ROD,
        order_type: OrderType::Stock,
        user_def: Some("From_Rust".to_string()),
    };
    
    println!("Testing with Taiwan Stock Order: Symbol={} Price=NT${} Qty={}", 
             demo_order.symbol, demo_order.price, demo_order.quantity);

    if warmup > 0 {
        println!("\nWarming up with {} orders...", warmup);
        client.batch_orders(warmup, num_connections, &demo_order).await;
        // Clear warmup latencies
        client.latencies.lock().await.clear();
    }

    println!("\nSending {} orders...", num_orders);
    let start_time = Instant::now();

    let results = client.batch_orders(num_orders, num_connections, &demo_order).await;

    let end_time = Instant::now();
    let total_time = end_time.duration_since(start_time).as_secs_f64();

    let successful = results.iter().filter(|r| r.success).count();
    let failed = num_orders - successful;

    println!("\nCompleted in {:.2} seconds", total_time);
    println!("Successful: {}, Failed: {}", successful, failed);
    println!("Throughput: {:.2} orders/sec", num_orders as f64 / total_time);

    client.print_stats().await;
}

#[tokio::main]
async fn main() {
    let args = Args::parse();
    
    run_test(args.orders, args.connections, args.warmup).await;
}