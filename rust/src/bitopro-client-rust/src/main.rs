// src/main.rs
use reqwest::{Client as HttpClient, StatusCode};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::error::Error;
use std::time::Duration;
use tokio_tungstenite::{
    connect_async, 
    tungstenite::protocol::Message
};
use futures::{SinkExt, StreamExt};
use url::Url;
use std::time::{SystemTime, UNIX_EPOCH};

// 訂單簿中的單個訂單條目
#[derive(Debug, Clone, Deserialize)]
struct OrderBookEntry {
    pub price: String,
    pub amount: String,
    pub count: i32,
    pub total: String,
}

// 完整的訂單簿結構
#[derive(Debug, Clone, Deserialize)]
struct OrderBook {
    pub bids: Vec<OrderBookEntry>,
    pub asks: Vec<OrderBookEntry>,
}

// BitoPro API 客戶端
struct BitoproRestfulClient {
    http_client: HttpClient,
}

impl BitoproRestfulClient {
    // 創建新客戶端
    fn new() -> Self {
        Self {
            http_client: HttpClient::new(),
        }
    }

    // 獲取指定交易對的訂單簿
    async fn get_order_book(&self, pair: &str, limit: Option<u32>, scale: Option<u32>) -> Result<OrderBook, Box<dyn Error>> {
        let api_base_url = "https://api.bitopro.com/v3";
        let endpoint = format!("/order-book/{}", pair);
        let url = format!("{}{}", api_base_url, endpoint);
        
        // 建立查詢參數
        let mut query_params = vec![];
        query_params.push(("limit", limit.unwrap_or(5).to_string()));
        
        if let Some(scale_value) = scale {
            query_params.push(("scale", scale_value.to_string()));
        }
        
        println!("請求 URL: {}", url);
        println!("參數: {:?}", query_params);
        
        // 發送請求
        let response = self.http_client.get(&url)
            .query(&query_params)
            .send()
            .await?;
        
        let status = response.status();
        println!("回應狀態碼: {}", status);
        
        match status {
            StatusCode::OK => {
                let order_book = response.json::<OrderBook>().await?;
                Ok(order_book)
            },
            _ => {
                let error_text = response.text().await?;
                println!("錯誤回應: {}", error_text);
                Err(format!("API 錯誤: {}", error_text).into())
            }
        }
    }
}

// 獲取當前時間戳（毫秒）
fn get_current_timestamp() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or(Duration::from_secs(0))
        .as_millis() as u64
}

// 生成認證 Headers
fn build_headers(api_key: &str, api_secret: &str, params: &impl Serialize) -> HashMap<String, String> {
    use hmac::{Hmac, Mac};
    use sha2::Sha384;
    use base64::{engine::general_purpose, Engine as _};
    
    // 將參數序列化為 JSON 字符串
    let json_string = serde_json::to_string(params).unwrap_or_default();
    
    // Base64 URL 安全編碼
    let payload = general_purpose::URL_SAFE.encode(json_string.as_bytes());
    
    // 創建 HMAC 簽名
    let mut mac = Hmac::<Sha384>::new_from_slice(api_secret.as_bytes())
        .expect("HMAC can take key of any size");
    mac.update(payload.as_bytes());
    let signature = hex::encode(mac.finalize().into_bytes());
    
    let mut headers = HashMap::new();
    headers.insert("X-BITOPRO-APIKEY".to_string(), api_key.to_string());
    headers.insert("X-BITOPRO-PAYLOAD".to_string(), payload);
    headers.insert("X-BITOPRO-SIGNATURE".to_string(), signature);
    
    headers
}

// WebSocket 客戶端 trait
trait WebSocketClient {
    fn new(symbols: Vec<String>, callback: fn(&str)) -> Self;
    fn init_websocket(&mut self);
    fn start(&mut self);
}

// 訂單簿 WebSocket 客戶端
struct BitoproOrderBookWs {
    connect_endpoint: String,
    ws_handle: Option<tokio::task::JoinHandle<()>>,
    callback: fn(&str),
}

impl WebSocketClient for BitoproOrderBookWs {
    fn new(symbols: Vec<String>, callback: fn(&str)) -> Self {
        let mut endpoint = "wss://stream.bitopro.com:443/ws/v1/pub/order-books/".to_string();
        
        // 為每個交易對添加默認限制 = 5
        for symbol in symbols {
            endpoint.push_str(&format!("{}:5,", symbol.to_lowercase()));
        }
        
        // 移除尾部的逗號
        if endpoint.ends_with(',') {
            endpoint.pop();
        }
        
        BitoproOrderBookWs {
            connect_endpoint: endpoint,
            ws_handle: None,
            callback,
        }
    }

    fn init_websocket(&mut self) {
        // 這裡不需要做特別的初始化
    }

    fn start(&mut self) {
        let endpoint = self.connect_endpoint.clone();
        let callback = self.callback;
        
        let handle = tokio::spawn(async move {
            println!("連接 WebSocket: {}", endpoint);
            
            // 嘗試連接 WebSocket
            let url = Url::parse(&endpoint).expect("無效的 WebSocket URL");
            
            match connect_async(url).await {
                Ok((ws_stream, _)) => {
                    println!("WebSocket 連接成功！");
                    
                    let (mut write, mut read) = ws_stream.split();
                    
                    // 處理接收到的消息
                    while let Some(message) = read.next().await {
                        match message {
                            Ok(msg) => {
                                match msg {
                                    Message::Text(text) => {
                                        // 調用回調函數處理接收到的消息
                                        callback(&text);
                                    }
                                    Message::Close(_) => {
                                        println!("WebSocket 連接已關閉");
                                        break;
                                    }
                                    _ => {}
                                }
                            }
                            Err(e) => {
                                println!("WebSocket 錯誤: {:?}", e);
                                break;
                            }
                        }
                    }
                    
                    // 關閉連接
                    let _ = write.send(Message::Close(None)).await;
                    println!("WebSocket 連接已關閉");
                }
                Err(e) => {
                    println!("WebSocket 連接失敗: {:?}", e);
                }
            }
        });
        
        self.ws_handle = Some(handle);
    }
}

// 歷史訂單 WebSocket 客戶端
struct BitoproHistoryOrders {
    connect_endpoint: String,
    ws_handle: Option<tokio::task::JoinHandle<()>>,
    account: String,
    api_key: String,
    api_secret: String,
    callback: fn(&str),
}

impl BitoproHistoryOrders {
    fn new(account: &str, api_key: &str, api_secret: &str, callback: fn(&str)) -> Self {
        let endpoint = "wss://stream.bitopro.com:443/ws/v1/pub/auth/orders/histories".to_string();
        
        BitoproHistoryOrders {
            connect_endpoint: endpoint,
            ws_handle: None,
            account: account.to_string(),
            api_key: api_key.to_string(),
            api_secret: api_secret.to_string(),
            callback,
        }
    }

    fn init_websocket(&mut self) {
        // 這裡不需要做特別的初始化
    }

    fn start(&mut self) {
        let endpoint = self.connect_endpoint.clone();
        let account = self.account.clone();
        let api_key = self.api_key.clone();
        let api_secret = self.api_secret.clone();
        let callback = self.callback;
        
        let handle = tokio::spawn(async move {
            println!("連接 WebSocket (歷史訂單): {}", endpoint);
            
            // 建立認證參數
            let params = serde_json::json!({
                "identity": account,
                "nonce": get_current_timestamp()
            });
            
            // 獲取認證 headers
            let auth_headers = build_headers(&api_key, &api_secret, &params);
            
            // 嘗試連接 WebSocket，並添加認證 headers
            let url = Url::parse(&endpoint).expect("無效的 WebSocket URL");
            
            let mut custom_headers = vec![];
            for (key, value) in auth_headers {
                custom_headers.push((key, value));
            }
            
            // 創建 WebSocket 請求
            let request = http::Request::builder()
                .uri(url.as_str())
                .header("User-Agent", "Rust WebSocket Client");
                
            // 添加認證 headers
            let request_with_headers = custom_headers.iter().fold(request, |req, (key, value)| {
                req.header(key, value)
            }).body(()).unwrap();
            
            // 連接 WebSocket
            match tokio_tungstenite::connect_async(request_with_headers).await {
                Ok((ws_stream, _)) => {
                    println!("WebSocket 連接成功！(歷史訂單)");
                    
                    let (mut write, mut read) = ws_stream.split();
                    
                    // 處理接收到的消息
                    while let Some(message) = read.next().await {
                        match message {
                            Ok(msg) => {
                                match msg {
                                    Message::Text(text) => {
                                        // 調用回調函數處理接收到的消息
                                        callback(&text);
                                    }
                                    Message::Close(_) => {
                                        println!("WebSocket 連接已關閉 (歷史訂單)");
                                        break;
                                    }
                                    _ => {}
                                }
                            }
                            Err(e) => {
                                println!("WebSocket 錯誤 (歷史訂單): {:?}", e);
                                break;
                            }
                        }
                    }
                    
                    // 關閉連接
                    let _ = write.send(Message::Close(None)).await;
                    println!("WebSocket 連接已關閉 (歷史訂單)");
                }
                Err(e) => {
                    println!("WebSocket 連接失敗 (歷史訂單): {:?}", e);
                }
            }
        });
        
        self.ws_handle = Some(handle);
    }
}

// 改進的 WebSocket 消息處理函數
fn websocket_handler(message: &str) {
    println!("\n收到 WebSocket 消息:");
    
    // 首先打印原始消息以便調試
    println!("原始消息: {}", message);
    // 打印型態
    // println!("消息類型: {}", message.chars().next().unwrap_or('N'));
    
    // 嘗試解析 JSON
    match serde_json::from_str::<serde_json::Value>(message) {
        Ok(json_value) => {
            // 檢查消息類型
            if let Some(event) = json_value.get("event").and_then(|e| e.as_str()) {
                match event {
                    "ORDER_BOOK" => {
                        println!("訂單簿更新:");
                        
                        // 獲取交易對
                        let pair = json_value.get("pair")
                            .and_then(|p| p.as_str())
                            .unwrap_or("未知交易對");
                        
                        println!("交易對: {}", pair);
                        
                        // 獲取時間戳
                        if let Some(timestamp) = json_value.get("timestamp").and_then(|t| t.as_u64()) {
                            println!("時間戳: {}", timestamp);
                        }
                        
                        // 解析並顯示買單
                        if let Some(data) = json_value.get("data") {
                            if let Some(bids) = data.get("bids").and_then(|b| b.as_array()) {
                                println!("\n買單 (前5筆):");
                                println!("{:<15} {:<15} {:<10}", "價格", "數量", "訂單數量");
                                println!("{}", "-".repeat(40));
                                
                                for (i, bid) in bids.iter().enumerate().take(5) {
                                    if let Some(bid_array) = bid.as_array() {
                                        if bid_array.len() >= 3 {
                                            let price = bid_array[0].as_str().unwrap_or("N/A");
                                            let amount = bid_array[1].as_str().unwrap_or("N/A");
                                            let count = bid_array[2].as_str().unwrap_or("N/A");
                                            
                                            println!("{:<15} {:<15} {:<10}", price, amount, count);
                                        }
                                    }
                                }
                            }
                            
                            // 解析並顯示賣單
                            if let Some(asks) = data.get("asks").and_then(|a| a.as_array()) {
                                println!("\n賣單 (前5筆):");
                                println!("{:<15} {:<15} {:<10}", "價格", "數量", "訂單數量");
                                println!("{}", "-".repeat(40));
                                
                                for (i, ask) in asks.iter().enumerate().take(5) {
                                    if let Some(ask_array) = ask.as_array() {
                                        if ask_array.len() >= 3 {
                                            let price = ask_array[0].as_str().unwrap_or("N/A");
                                            let amount = ask_array[1].as_str().unwrap_or("N/A");
                                            let count = ask_array[2].as_str().unwrap_or("N/A");
                                            
                                            println!("{:<15} {:<15} {:<10}", price, amount, count);
                                        }
                                    }
                                }
                            }
                            
                            // 計算市場價差
                            if let (Some(bids), Some(asks)) = (
                                data.get("bids").and_then(|b| b.as_array()),
                                data.get("asks").and_then(|a| a.as_array())
                            ) {
                                if !bids.is_empty() && !asks.is_empty() {
                                    if let (Some(bid_array), Some(ask_array)) = (bids[0].as_array(), asks[0].as_array()) {
                                        if bid_array.len() > 0 && ask_array.len() > 0 {
                                            if let (Some(bid_price), Some(ask_price)) = (
                                                bid_array[0].as_str().and_then(|s| s.parse::<f64>().ok()),
                                                ask_array[0].as_str().and_then(|s| s.parse::<f64>().ok())
                                            ) {
                                                let spread = ask_price - bid_price;
                                                let spread_percentage = (spread / bid_price) * 100.0;
                                                
                                                println!("\n市場摘要:");
                                                println!("最高買價: {}", bid_price);
                                                println!("最低賣價: {}", ask_price);
                                                println!("價差: {} ({:.4}%)", spread, spread_percentage);
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "RECENT_HISTORY_ORDERS" => {
                        println!("收到歷史訂單更新:");
                        // 這裡可以添加更多解析歷史訂單的邏輯
                        println!("{}", json_value);
                    },
                    _ => {
                        println!("收到未知類型的事件: {}", event);
                        println!("{}", json_value);
                    }
                }
            } else {
                println!("無法識別的JSON消息格式:");
                println!("{}", json_value);
            }
        },
        Err(e) => {
            println!("解析JSON失敗: {}", e);
            println!("原始消息: {}", message);
        }
    }
    
    println!("\n-----------------------------------");
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    println!("BitoPro 交易所測試");
    println!("====================");
    
    // === REST API 測試 ===
    
    // 初始化 REST 客戶端
    let client = BitoproRestfulClient::new();
    
    // 獲取訂單簿數據
    let pair = "BTC_USDT";
    let limit = Some(10);  // 獲取10筆訂單
    
    println!("\n[REST API] 正在獲取 {} 的訂單簿資料 (limit: {:?})...", pair, limit);
    
    // 發送請求並獲取訂單簿
    let order_book = client.get_order_book(pair, limit, None).await?;
    
    // 顯示買單
    println!("\nBids (買單):");
    println!("{:<15} {:<15} {:<10} {:<15}", "價格", "數量", "訂單數", "總額");
    println!("{}", "-".repeat(60));
    
    for bid in order_book.bids.iter().take(5) {
        println!("{:<15} {:<15} {:<10} {:<15}", 
                 bid.price, bid.amount, bid.count, bid.total);
    }
    
    // 顯示賣單
    println!("\nAsks (賣單):");
    println!("{:<15} {:<15} {:<10} {:<15}", "價格", "數量", "訂單數", "總額");
    println!("{}", "-".repeat(60));
    
    for ask in order_book.asks.iter().take(5) {
        println!("{:<15} {:<15} {:<10} {:<15}", 
                 ask.price, ask.amount, ask.count, ask.total);
    }
    
    // === WebSocket 測試 ===
    
    println!("\n[WebSocket] 開始訂閱 WebSocket...");
    
    // 創建訂單簿 WebSocket 客戶端
    let mut order_book_ws = BitoproOrderBookWs::new(
        vec![pair.to_string()], 
        websocket_handler
    );
    
    // 初始化並啟動 WebSocket 連接
    order_book_ws.init_websocket();
    order_book_ws.start();
    
    // 如果你有 BitoPro 帳號，可以取消下面註釋來訂閱歷史訂單
    /*
    // BitoPro 帳號配置
    let account = "你的帳號";
    let api_key = "你的API密鑰";
    let api_secret = "你的API密鑰";
    
    // 創建歷史訂單 WebSocket 客戶端
    let mut history_orders_ws = BitoproHistoryOrders::new(
        account, 
        api_key, 
        api_secret, 
        websocket_handler
    );
    
    // 初始化並啟動 WebSocket 連接
    history_orders_ws.init_websocket();
    history_orders_ws.start();
    */
    
    // 保持程序運行一段時間以接收 WebSocket 消息
    println!("\n等待接收 WebSocket 消息 (60秒後自動退出)...");
    tokio::time::sleep(Duration::from_secs(60)).await;
    
    println!("\n程序執行完畢");
    
    Ok(())
}
