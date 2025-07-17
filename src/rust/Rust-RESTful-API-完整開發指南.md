# 完整 Rust RESTful API 開發指南

## 📋 目錄
- [專案概述](#專案概述)
- [環境準備](#環境準備)
- [專案結構](#專案結構)
- [核心代碼](#核心代碼)
- [功能特色](#功能特色)
- [API 文檔](#api-文檔)
- [測試指南](#測試指南)
- [部署指南](#部署指南)
- [擴展建議](#擴展建議)
- [常見問題](#常見問題)

## 專案概述

這是一個使用 Rust 語言和 Axum 框架開發的完整 RESTful API 專案。專案展示了如何使用現代 Rust 技術棧構建高性能、類型安全的 web 服務。

### 技術棧
- **語言**: Rust 1.70+
- **框架**: Axum 0.7
- **異步運行時**: Tokio
- **序列化**: Serde
- **日誌**: Tracing
- **測試**: 內建測試框架

### 主要功能
- 用戶管理（CRUD 操作）
- 輸入驗證和錯誤處理
- 結構化日誌記錄
- 健康檢查端點
- 完整的測試覆蓋

## 環境準備

### 系統要求
- Rust 1.70 或更高版本
- Cargo 包管理器
- curl 或 HTTPie（用於測試）

### 安裝 Rust
```bash
# 安裝 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 更新到最新版本
rustup update

# 驗證安裝
rustc --version
cargo --version
```

### 創建專案
```bash
# 創建新專案
cargo new rust-restful-api
cd rust-restful-api
```

## 專案結構

```
rust-restful-api/
├── Cargo.toml              # 依賴配置
├── src/
│   └── main.rs            # 主程式
├── tests/                 # 測試檔案
│   └── integration_tests.rs
├── scripts/               # 腳本檔案
│   └── test_api.sh
├── docker/                # Docker 配置
│   └── Dockerfile
└── README.md              # 專案說明
```

## 核心代碼

### 1. Cargo.toml 配置

```toml
[package]
name = "rust-restful-api"
version = "0.1.0"
edition = "2021"
description = "A complete RESTful API example in Rust using Axum"

[dependencies]
axum = "0.7"
tokio = { version = "1.0", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
uuid = { version = "1.0", features = ["v4", "serde"] }
tracing = "0.1"
tracing-subscriber = "0.3"
anyhow = "1.0"
chrono = { version = "0.4", features = ["serde"] }
tower = "0.4"

[dev-dependencies]
tower-test = "0.4"
```

### 2. 主程式 (src/main.rs)

```rust
use axum::{
    extract::{Json, Path, State},
    http::StatusCode,
    response::Json as ResponseJson,
    routing::{delete, get, post, put},
    Router,
};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use tokio::net::TcpListener;
use tracing::{info, warn, Level};
use uuid::Uuid;

// 數據模型
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct User {
    pub id: Uuid,
    pub name: String,
    pub email: String,
    pub age: u32,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Deserialize)]
pub struct CreateUserRequest {
    pub name: String,
    pub email: String,
    pub age: u32,
}

#[derive(Debug, Deserialize)]
pub struct UpdateUserRequest {
    pub name: Option<String>,
    pub email: Option<String>,
    pub age: Option<u32>,
}

// 響應模型
#[derive(Debug, Serialize)]
pub struct UserResponse {
    pub id: Uuid,
    pub name: String,
    pub email: String,
    pub age: u32,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Serialize)]
pub struct UsersListResponse {
    pub users: Vec<UserResponse>,
    pub total: usize,
}

#[derive(Debug, Serialize)]
pub struct ErrorResponse {
    pub error: String,
    pub code: u16,
    pub timestamp: DateTime<Utc>,
}

#[derive(Debug, Serialize)]
pub struct HealthResponse {
    pub status: String,
    pub timestamp: DateTime<Utc>,
    pub version: String,
}

// 應用狀態
pub type AppState = Arc<Mutex<HashMap<Uuid, User>>>;

// 輔助函數
impl User {
    fn new(name: String, email: String, age: u32) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            name,
            email,
            age,
            created_at: now,
            updated_at: now,
        }
    }
    
    fn update(&mut self, request: UpdateUserRequest) {
        if let Some(name) = request.name {
            self.name = name;
        }
        if let Some(email) = request.email {
            self.email = email;
        }
        if let Some(age) = request.age {
            self.age = age;
        }
        self.updated_at = Utc::now();
    }
}

impl From<User> for UserResponse {
    fn from(user: User) -> Self {
        Self {
            id: user.id,
            name: user.name,
            email: user.email,
            age: user.age,
            created_at: user.created_at,
            updated_at: user.updated_at,
        }
    }
}

// 錯誤處理
fn create_error_response(error: &str, code: u16) -> ErrorResponse {
    ErrorResponse {
        error: error.to_string(),
        code,
        timestamp: Utc::now(),
    }
}

// 輸入驗證
fn validate_create_user_request(request: &CreateUserRequest) -> Result<(), String> {
    if request.name.trim().is_empty() {
        return Err("Name cannot be empty".to_string());
    }
    if request.email.trim().is_empty() {
        return Err("Email cannot be empty".to_string());
    }
    if !request.email.contains('@') {
        return Err("Invalid email format".to_string());
    }
    if request.age > 150 {
        return Err("Age must be reasonable".to_string());
    }
    Ok(())
}

// API 處理器
pub async fn health_check() -> ResponseJson<HealthResponse> {
    ResponseJson(HealthResponse {
        status: "healthy".to_string(),
        timestamp: Utc::now(),
        version: env!("CARGO_PKG_VERSION").to_string(),
    })
}

pub async fn get_all_users(
    State(state): State<AppState>
) -> Result<ResponseJson<UsersListResponse>, (StatusCode, ResponseJson<ErrorResponse>)> {
    let users = state.lock().unwrap();
    let user_list: Vec<UserResponse> = users.values()
        .cloned()
        .map(UserResponse::from)
        .collect();
    
    let total = user_list.len();
    
    Ok(ResponseJson(UsersListResponse {
        users: user_list,
        total,
    }))
}

pub async fn get_user(
    State(state): State<AppState>,
    Path(id): Path<Uuid>,
) -> Result<ResponseJson<UserResponse>, (StatusCode, ResponseJson<ErrorResponse>)> {
    let users = state.lock().unwrap();
    
    match users.get(&id) {
        Some(user) => {
            info!("Retrieved user: {}", id);
            Ok(ResponseJson(UserResponse::from(user.clone())))
        }
        None => {
            warn!("User not found: {}", id);
            Err((
                StatusCode::NOT_FOUND,
                ResponseJson(create_error_response("User not found", 404)),
            ))
        }
    }
}

pub async fn create_user(
    State(state): State<AppState>,
    Json(payload): Json<CreateUserRequest>,
) -> Result<(StatusCode, ResponseJson<UserResponse>), (StatusCode, ResponseJson<ErrorResponse>)> {
    // 驗證輸入
    if let Err(error) = validate_create_user_request(&payload) {
        warn!("Invalid user creation request: {}", error);
        return Err((
            StatusCode::BAD_REQUEST,
            ResponseJson(create_error_response(&error, 400)),
        ));
    }

    // 檢查郵箱是否已存在
    {
        let users = state.lock().unwrap();
        if users.values().any(|u| u.email == payload.email) {
            return Err((
                StatusCode::CONFLICT,
                ResponseJson(create_error_response("Email already exists", 409)),
            ));
        }
    }

    let user = User::new(payload.name, payload.email, payload.age);
    let user_id = user.id;

    let mut users = state.lock().unwrap();
    users.insert(user_id, user.clone());

    info!("Created user: {} ({})", user.name, user_id);
    Ok((StatusCode::CREATED, ResponseJson(UserResponse::from(user))))
}

pub async fn update_user(
    State(state): State<AppState>,
    Path(id): Path<Uuid>,
    Json(payload): Json<UpdateUserRequest>,
) -> Result<ResponseJson<UserResponse>, (StatusCode, ResponseJson<ErrorResponse>)> {
    // 檢查郵箱衝突（如果更新郵箱）
    if let Some(ref new_email) = payload.email {
        let users = state.lock().unwrap();
        if users.values().any(|u| u.id != id && u.email == *new_email) {
            return Err((
                StatusCode::CONFLICT,
                ResponseJson(create_error_response("Email already exists", 409)),
            ));
        }
    }
    
    let mut users = state.lock().unwrap();
    match users.get_mut(&id) {
        Some(user) => {
            user.update(payload);
            info!("Updated user: {}", id);
            Ok(ResponseJson(UserResponse::from(user.clone())))
        }
        None => {
            warn!("Attempted to update non-existent user: {}", id);
            Err((
                StatusCode::NOT_FOUND,
                ResponseJson(create_error_response("User not found", 404)),
            ))
        }
    }
}

pub async fn delete_user(
    State(state): State<AppState>,
    Path(id): Path<Uuid>,
) -> Result<StatusCode, (StatusCode, ResponseJson<ErrorResponse>)> {
    let mut users = state.lock().unwrap();
    
    match users.remove(&id) {
        Some(user) => {
            info!("Deleted user: {} ({})", user.name, id);
            Ok(StatusCode::NO_CONTENT)
        }
        None => {
            warn!("Attempted to delete non-existent user: {}", id);
            Err((
                StatusCode::NOT_FOUND,
                ResponseJson(create_error_response("User not found", 404)),
            ))
        }
    }
}

// 路由構建
pub fn create_router() -> Router {
    let state = Arc::new(Mutex::new(HashMap::new()));

    Router::new()
        .route("/health", get(health_check))
        .route("/api/users", get(get_all_users))
        .route("/api/users", post(create_user))
        .route("/api/users/:id", get(get_user))
        .route("/api/users/:id", put(update_user))
        .route("/api/users/:id", delete(delete_user))
        .with_state(state)
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // 初始化日誌
    tracing_subscriber::fmt()
        .with_max_level(Level::INFO)
        .init();

    // 創建應用
    let app = create_router();

    // 啟動服務器
    let port = std::env::var("PORT").unwrap_or_else(|_| "3000".to_string());
    let addr = format!("0.0.0.0:{}", port);
    
    info!("🚀 Starting server on {}", addr);
    info!("📚 Health check: http://localhost:{}/health", port);
    
    let listener = TcpListener::bind(&addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}

// 測試模組
#[cfg(test)]
mod tests {
    use super::*;
    use axum::http::{Method, Request};
    use axum::body::Body;
    use tower::ServiceExt;

    #[tokio::test]
    async fn test_health_check() {
        let app = create_router();
        
        let response = app
            .oneshot(
                Request::builder()
                    .method(Method::GET)
                    .uri("/health")
                    .body(Body::empty())
                    .unwrap(),
            )
            .await
            .unwrap();

        assert_eq!(response.status(), StatusCode::OK);
    }

    #[tokio::test]
    async fn test_create_user() {
        let app = create_router();
        
        let user_data = serde_json::json!({
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30
        });

        let response = app
            .oneshot(
                Request::builder()
                    .method(Method::POST)
                    .uri("/api/users")
                    .header("content-type", "application/json")
                    .body(Body::from(user_data.to_string()))
                    .unwrap(),
            )
            .await
            .unwrap();

        assert_eq!(response.status(), StatusCode::CREATED);
    }

    #[tokio::test]
    async fn test_create_user_invalid_email() {
        let app = create_router();
        
        let user_data = serde_json::json!({
            "name": "John Doe",
            "email": "invalid-email",
            "age": 30
        });

        let response = app
            .oneshot(
                Request::builder()
                    .method(Method::POST)
                    .uri("/api/users")
                    .header("content-type", "application/json")
                    .body(Body::from(user_data.to_string()))
                    .unwrap(),
            )
            .await
            .unwrap();

        assert_eq!(response.status(), StatusCode::BAD_REQUEST);
    }

    #[tokio::test]
    async fn test_get_nonexistent_user() {
        let app = create_router();
        
        let response = app
            .oneshot(
                Request::builder()
                    .method(Method::GET)
                    .uri("/api/users/00000000-0000-0000-0000-000000000000")
                    .body(Body::empty())
                    .unwrap(),
            )
            .await
            .unwrap();

        assert_eq!(response.status(), StatusCode::NOT_FOUND);
    }

    #[tokio::test]
    async fn test_email_uniqueness() {
        let app = create_router();
        
        // 創建第一個用戶
        let user1_data = serde_json::json!({
            "name": "User One",
            "email": "duplicate@example.com",
            "age": 30
        });
        
        let response1 = app
            .clone()
            .oneshot(
                Request::builder()
                    .method(Method::POST)
                    .uri("/api/users")
                    .header("content-type", "application/json")
                    .body(Body::from(user1_data.to_string()))
                    .unwrap(),
            )
            .await
            .unwrap();
        
        assert_eq!(response1.status(), StatusCode::CREATED);
        
        // 嘗試創建具有相同電子郵件的第二個用戶
        let user2_data = serde_json::json!({
            "name": "User Two",
            "email": "duplicate@example.com",
            "age": 25
        });
        
        let response2 = app
            .oneshot(
                Request::builder()
                    .method(Method::POST)
                    .uri("/api/users")
                    .header("content-type", "application/json")
                    .body(Body::from(user2_data.to_string()))
                    .unwrap(),
            )
            .await
            .unwrap();
        
        assert_eq!(response2.status(), StatusCode::CONFLICT);
    }
}
```

## 功能特色

### 1. 🔒 類型安全
- **強類型系統**: 使用 Rust 的類型系統確保編譯時安全
- **序列化保證**: Serde 自動處理 JSON 序列化/反序列化
- **UUID 支持**: 唯一標識符保證資料完整性

### 2. ⚡ 高性能
- **異步處理**: 基於 Tokio 的異步運行時
- **零成本抽象**: Axum 框架提供高效的請求處理
- **內存安全**: 無垃圾回收，低延遲響應

### 3. 🛡️ 錯誤處理
- **統一錯誤格式**: 所有錯誤響應都包含錯誤碼和時間戳
- **輸入驗證**: 全面的請求數據驗證
- **適當的 HTTP 狀態碼**: 符合 REST 標準的響應碼

### 4. 📊 日誌記錄
- **結構化日誌**: 使用 tracing 記錄詳細的操作信息
- **可配置級別**: 支持不同的日誌級別
- **性能追蹤**: 異步友好的日誌記錄

### 5. 🧪 測試覆蓋
- **單元測試**: 涵蓋所有主要功能
- **集成測試**: 測試完整的 API 流程
- **邊界情況**: 包含錯誤情況的測試

## API 文檔

### 基本信息
- **Base URL**: `http://localhost:3000`
- **Content-Type**: `application/json`
- **認證**: 無（示例項目）

### 端點列表

#### 1. 健康檢查
```
GET /health
```

**響應示例**:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-17T10:30:00.000Z",
  "version": "0.1.0"
}
```

#### 2. 獲取所有用戶
```
GET /api/users
```

**響應示例**:
```json
{
  "users": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "張三",
      "email": "zhangsan@example.com",
      "age": 25,
      "created_at": "2025-07-17T10:30:00.000Z",
      "updated_at": "2025-07-17T10:30:00.000Z"
    }
  ],
  "total": 1
}
```

#### 3. 創建用戶
```
POST /api/users
```

**請求體**:
```json
{
  "name": "張三",
  "email": "zhangsan@example.com",
  "age": 25
}
```

**響應示例** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "張三",
  "email": "zhangsan@example.com",
  "age": 25,
  "created_at": "2025-07-17T10:30:00.000Z",
  "updated_at": "2025-07-17T10:30:00.000Z"
}
```

#### 4. 獲取單個用戶
```
GET /api/users/{id}
```

**路徑參數**:
- `id`: 用戶 UUID

**響應示例**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "張三",
  "email": "zhangsan@example.com",
  "age": 25,
  "created_at": "2025-07-17T10:30:00.000Z",
  "updated_at": "2025-07-17T10:30:00.000Z"
}
```

#### 5. 更新用戶
```
PUT /api/users/{id}
```

**請求體** (所有字段都是可選的):
```json
{
  "name": "李四",
  "email": "lisi@example.com",
  "age": 30
}
```

**響應示例**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "李四",
  "email": "lisi@example.com",
  "age": 30,
  "created_at": "2025-07-17T10:30:00.000Z",
  "updated_at": "2025-07-17T11:00:00.000Z"
}
```

#### 6. 刪除用戶
```
DELETE /api/users/{id}
```

**響應**: 204 No Content

### 錯誤響應格式

所有錯誤響應都遵循以下格式：

```json
{
  "error": "錯誤訊息",
  "code": 404,
  "timestamp": "2025-07-17T10:30:00.000Z"
}
```

### HTTP 狀態碼

| 狀態碼 | 說明 |
|--------|------|
| 200 | OK - 成功獲取資源 |
| 201 | Created - 成功創建資源 |
| 204 | No Content - 成功刪除資源 |
| 400 | Bad Request - 請求格式錯誤 |
| 404 | Not Found - 資源不存在 |
| 409 | Conflict - 資源衝突（如重複郵箱） |
| 500 | Internal Server Error - 服務器內部錯誤 |

## 測試指南

### 運行項目

```bash
# 編譯並運行
cargo run

# 在背景運行
cargo run &

# 指定端口
PORT=8080 cargo run
```

### 單元測試

```bash
# 運行所有測試
cargo test

# 運行特定測試
cargo test test_health_check

# 顯示測試輸出
cargo test -- --nocapture

# 運行測試並顯示覆蓋率
cargo test --verbose
```

### 手動測試

#### 使用 curl

```bash
# 1. 健康檢查
curl http://localhost:3000/health

# 2. 創建用戶
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "張三",
    "email": "zhangsan@example.com",
    "age": 25
  }'

# 3. 獲取所有用戶
curl http://localhost:3000/api/users

# 4. 獲取單個用戶 (替換 UUID)
curl http://localhost:3000/api/users/550e8400-e29b-41d4-a716-446655440000

# 5. 更新用戶
curl -X PUT http://localhost:3000/api/users/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "李四",
    "age": 30
  }'

# 6. 刪除用戶
curl -X DELETE http://localhost:3000/api/users/550e8400-e29b-41d4-a716-446655440000
```

#### 使用 HTTPie

```bash
# 安裝 HTTPie
pip install httpie

# 創建用戶
http POST localhost:3000/api/users name="王五" email="wangwu@example.com" age:=28

# 獲取用戶
http GET localhost:3000/api/users

# 更新用戶
http PUT localhost:3000/api/users/USER_ID name="趙六"

# 刪除用戶
http DELETE localhost:3000/api/users/USER_ID
```

### 自動化測試腳本

創建 `scripts/test_api.sh`:

```bash
#!/bin/bash

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BASE_URL="http://localhost:3000"
PASSED=0
FAILED=0

# 測試函數
test_endpoint() {
    local test_name="$1"
    local expected_code="$2"
    local actual_code="$3"
    
    echo -e "\n🧪 測試: $test_name"
    echo "期望狀態碼: $expected_code"
    echo "實際狀態碼: $actual_code"
    
    if [ "$actual_code" = "$expected_code" ]; then
        echo -e "${GREEN}✅ 通過${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ 失敗${NC}"
        ((FAILED++))
    fi
}

echo -e "${YELLOW}🚀 開始測試 Rust RESTful API${NC}"

# 檢查服務器
if ! curl -s "$BASE_URL/health" > /dev/null; then
    echo -e "${RED}❌ 服務器未運行${NC}"
    exit 1
fi

# 1. 健康檢查
echo -e "\n1️⃣ 健康檢查"
response=$(curl -s -w "%{http_code}" -o /tmp/health_response "$BASE_URL/health")
status_code="${response: -3}"
test_endpoint "健康檢查" "200" "$status_code"

# 2. 創建用戶
echo -e "\n2️⃣ 創建用戶"
response=$(curl -s -w "%{http_code}" -o /tmp/create_response \
    -X POST "$BASE_URL/api/users" \
    -H "Content-Type: application/json" \
    -d '{"name":"張三","email":"zhangsan@example.com","age":25}')
status_code="${response: -3}"
test_endpoint "創建用戶" "201" "$status_code"

# 提取用戶 ID
USER_ID=$(cat /tmp/create_response | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
echo -e "${YELLOW}用戶 ID: $USER_ID${NC}"

# 3. 獲取所有用戶
echo -e "\n3️⃣ 獲取所有用戶"
response=$(curl -s -w "%{http_code}" -o /tmp/users_response "$BASE_URL/api/users")
status_code="${response: -3}"
test_endpoint "獲取所有用戶" "200" "$status_code"

# 4. 獲取單個用戶
if [ -n "$USER_ID" ]; then
    echo -e "\n4️⃣ 獲取單個用戶"
    response=$(curl -s -w "%{http_code}" -o /tmp/user_response "$BASE_URL/api/users/$USER_ID")
    status_code="${response: -3}"
    test_endpoint "獲取單個用戶" "200" "$status_code"
    
    # 5. 更新用戶
    echo -e "\n5️⃣ 更新用戶"
    response=$(curl -s -w "%{http_code}" -o /tmp/update_response \
        -X PUT "$BASE_URL/api/users/$USER_ID" \
        -H "Content-Type: application/json" \
        -d '{"name":"李四","age":30}')
    status_code="${response: -3}"
    test_endpoint "更新用戶" "200" "$status_code"
    
    # 6. 刪除用戶
    echo -e "\n6️⃣ 刪除用戶"
    response=$(curl -s -w "%{http_code}" -o /tmp/delete_response \
        -X DELETE "$BASE_URL/api/users/$USER_ID")
    status_code="${response: -3}"
    test_endpoint "刪除用戶" "204" "$status_code"
