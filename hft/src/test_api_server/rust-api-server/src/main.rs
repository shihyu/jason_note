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
struct OrderRequest {
    order_id: String,
    symbol: String,
    quantity: i32,
    price: f64,
    side: String,
    client_timestamp: DateTime<Utc>,
}

#[derive(Debug, Serialize)]
struct OrderResponse {
    order_id: String,
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
    let latency_ms = (server_timestamp - order.client_timestamp).num_milliseconds() as f64;
    
    let mut count = state.order_count.lock().await;
    *count += 1;
    let current_count = *count;
    
    info!(
        "Order #{}: {} {} {} @ {} | Latency: {:.2}ms",
        current_count,
        order.side,
        order.quantity,
        order.symbol,
        order.price,
        latency_ms
    );
    
    let response = OrderResponse {
        order_id: order.order_id,
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