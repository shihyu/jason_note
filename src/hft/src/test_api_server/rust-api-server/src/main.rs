use axum::{
    extract::State,
    http::StatusCode,
    response::Json,
    routing::post,
    Router,
};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use std::time::Instant;
use tokio::sync::Mutex;
use tower_http::cors::CorsLayer;
use tracing::{info, Level};
use tracing_subscriber;

#[derive(Debug, Deserialize)]
#[serde(rename_all = "snake_case")]
enum BSAction {
    Buy,
    Sell,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "snake_case")]
enum MarketType {
    Common,
    Warrant,
    OddLot,
    Daytime,
    FixedPrice,
    PlaceFirst,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "snake_case")]
enum PriceType {
    Limit,
    Market,
    LimitUp,
    LimitDown,
    Range,
}

#[derive(Debug, Deserialize)]
enum TimeInForce {
    #[serde(rename = "rod")]
    ROD,
    #[serde(rename = "ioc")]
    IOC,
    #[serde(rename = "fok")]
    FOK,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "snake_case")]
enum OrderType {
    Stock,
    Futures,
    Option,
}

#[derive(Debug, Deserialize)]
struct OrderRequest {
    buy_sell: BSAction,
    symbol: i32,
    price: f64,
    quantity: i32,
    market_type: MarketType,
    price_type: PriceType,
    time_in_force: TimeInForce,
    order_type: OrderType,
    #[serde(default)]
    user_def: Option<String>,
    client_timestamp: DateTime<Utc>,
}

#[allow(dead_code)]
impl OrderRequest {
    fn market_type(&self) -> &MarketType {
        &self.market_type
    }
    
    fn price_type(&self) -> &PriceType {
        &self.price_type
    }
    
    fn time_in_force(&self) -> &TimeInForce {
        &self.time_in_force
    }
    
    fn user_def(&self) -> Option<&String> {
        self.user_def.as_ref()
    }
}

#[derive(Debug, Serialize)]
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

#[derive(Debug, Clone)]
struct AppState {
    order_count: Arc<Mutex<u64>>,
    start_time: Instant,
}

async fn place_order(
    State(state): State<AppState>,
    Json(order): Json<OrderRequest>,
) -> Result<Json<OrderResponse>, StatusCode> {
    let server_timestamp = Utc::now();
    let latency_ms = (server_timestamp - order.client_timestamp).num_microseconds()
        .map(|us| us as f64 / 1000.0)
        .unwrap_or(0.0);
    
    let mut count = state.order_count.lock().await;
    *count += 1;
    let current_count = *count;
    
    let buy_sell_str = match order.buy_sell {
        BSAction::Buy => "BUY",
        BSAction::Sell => "SELL",
    };
    
    info!(
        "Order #{}: {} {} shares of {} @ NT${} | Type: {:?} | Latency: {:.2}ms",
        current_count,
        buy_sell_str,
        order.quantity,
        order.symbol,
        order.price,
        order.order_type,
        latency_ms
    );
    
    let response = OrderResponse {
        symbol: order.symbol,
        buy_sell: buy_sell_str.to_string(),
        quantity: order.quantity,
        price: order.price,
        status: "ACCEPTED".to_string(),
        client_timestamp: order.client_timestamp,
        server_timestamp,
        latency_ms,
    };
    
    Ok(Json(response))
}

async fn get_stats(State(state): State<AppState>) -> Json<serde_json::Value> {
    let count = state.order_count.lock().await;
    let elapsed = state.start_time.elapsed().as_secs_f64();
    let tps = if elapsed > 0.0 {
        *count as f64 / elapsed
    } else {
        0.0
    };
    
    Json(serde_json::json!({
        "total_orders": *count,
        "elapsed_seconds": elapsed,
        "orders_per_second": tps
    }))
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_max_level(Level::INFO)
        .init();
    
    let state = AppState {
        order_count: Arc::new(Mutex::new(0)),
        start_time: Instant::now(),
    };
    
    let app = Router::new()
        .route("/order", post(place_order))
        .route("/stats", axum::routing::get(get_stats))
        .layer(CorsLayer::permissive())
        .with_state(state);
    
    let addr = "0.0.0.0:8080";
    info!("API Server listening on {}", addr);
    
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}