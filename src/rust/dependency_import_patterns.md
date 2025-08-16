# 套件管理：聲明 vs 使用 完全對照

## 🎯 核心概念對比

多數現代語言都採用 **二階段模式**：
1. **階段1**：在配置檔案中**聲明依賴**（我需要什麼）
2. **階段2**：在代碼中**導入使用**（我要用什麼）

---

## 📊 各語言對應規則詳細比較

### 🦀 Rust

#### 依賴聲明（Cargo.toml）
```toml
[dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1.0", features = ["full"] }
my_math = { package = "advanced-math", version = "2.0" }  # 別名
```

#### 導入使用（.rs 檔案）
```rust
use serde::{Serialize, Deserialize};           // ✅ 對應 serde
use tokio::sync::mpsc;                        // ✅ 對應 tokio  
use my_math::complex::Complex;                // ✅ 對應 my_math（別名）
use advanced_math::complex::Complex;          // ❌ 錯誤！要用別名 my_math
use some_other::lib;                         // ❌ 錯誤！沒在 Cargo.toml 聲明
```

**核心規則**：use 的第一段必須是 Cargo.toml 中的**依賴名稱**（或別名）

---

### 🐍 Python

#### 依賴聲明（requirements.txt 或 pyproject.toml）
```txt
# requirements.txt
requests==2.28.0
pandas>=1.5.0
numpy
scikit-learn==1.1.0
```

```toml
# pyproject.toml
[project.dependencies]
requests = ">=2.28.0"
pandas = ">=1.5.0"
```

#### 導入使用（.py 檔案）
```python
import requests                    # ✅ 對應 requests
from pandas import DataFrame       # ✅ 對應 pandas
import numpy as np                 # ✅ 對應 numpy
from sklearn import metrics       # ✅ 對應 scikit-learn（套件名 != import 名！）
import tensorflow                  # ❌ 錯誤！沒在依賴中聲明
```

**易混淆點**：
- 套件安裝名：`scikit-learn`
- 導入名：`sklearn`
- 這是 Python 的特殊情況！

---

### ☕ Java

#### 依賴聲明（pom.xml 或 build.gradle）
```xml
<!-- Maven pom.xml -->
<dependencies>
    <dependency>
        <groupId>com.fasterxml.jackson.core</groupId>
        <artifactId>jackson-core</artifactId>
        <version>2.14.0</version>
    </dependency>
    <dependency>
        <groupId>org.springframework</groupId>
        <artifactId>spring-context</artifactId>
        <version>5.3.0</version>
    </dependency>
</dependencies>
```

```gradle
// Gradle build.gradle
dependencies {
    implementation 'com.fasterxml.jackson.core:jackson-core:2.14.0'
    implementation 'org.springframework:spring-context:5.3.0'
}
```

#### 導入使用（.java 檔案）
```java
import com.fasterxml.jackson.core.JsonParser;           // ✅ 對應 jackson-core
import org.springframework.context.ApplicationContext;   // ✅ 對應 spring-context
import com.google.gson.Gson;                            // ❌ 錯誤！沒在依賴中聲明
```

**核心規則**：import 路徑必須來自已聲明的 JAR 檔案

---

### 🟨 JavaScript/Node.js

#### 依賴聲明（package.json）
```json
{
  "dependencies": {
    "express": "^4.18.0",
    "lodash": "^4.17.21",
    "react": "^18.2.0",
    "@types/node": "^18.0.0"
  },
  "devDependencies": {
    "typescript": "^4.8.0"
  }
}
```

#### 導入使用（.js/.ts 檔案）
```javascript
// CommonJS
const express = require('express');        // ✅ 對應 express
const _ = require('lodash');               // ✅ 對應 lodash
const fs = require('fs');                  // ✅ Node.js 內建，不需聲明

// ES Modules
import express from 'express';             // ✅ 對應 express
import React from 'react';                // ✅ 對應 react
import { readFile } from 'fs/promises';   // ✅ Node.js 內建
import axios from 'axios';                // ❌ 錯誤！沒在 package.json 聲明
```

**特殊情況**：
- scoped packages：`@types/node` → `import type { ... } from 'node'`
- 內建模組不需聲明：`fs`, `path`, `http` 等

---

### 🏗️ C#/.NET

#### 依賴聲明（.csproj 或 packages.config）
```xml
<!-- .csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <ItemGroup>
    <PackageReference Include="Newtonsoft.Json" Version="13.0.1" />
    <PackageReference Include="Microsoft.EntityFrameworkCore" Version="7.0.0" />
    <PackageReference Include="Serilog" Version="2.12.0" />
  </ItemGroup>
</Project>
```

#### 導入使用（.cs 檔案）
```csharp
using Newtonsoft.Json;                           // ✅ 對應 Newtonsoft.Json
using Microsoft.EntityFrameworkCore;             // ✅ 對應 Microsoft.EntityFrameworkCore
using Serilog;                                   // ✅ 對應 Serilog
using System.Collections.Generic;                // ✅ .NET 內建，不需聲明
using Some.Unknown.Library;                      // ❌ 錯誤！沒在 .csproj 聲明
```

---

### 🔷 Go

#### 依賴聲明（go.mod）
```go
module myproject

go 1.19

require (
    github.com/gin-gonic/gin v1.9.0
    github.com/go-redis/redis/v8 v8.11.5
    golang.org/x/crypto v0.7.0
)
```

#### 導入使用（.go 檔案）
```go
import (
    "fmt"                                    // ✅ Go 標準庫，不需聲明
    "net/http"                              // ✅ Go 標準庫
    "github.com/gin-gonic/gin"              // ✅ 對應 go.mod 中的 gin
    "github.com/go-redis/redis/v8"          // ✅ 對應 go.mod 中的 redis
    "golang.org/x/crypto/bcrypt"            // ✅ 對應 go.mod 中的 crypto
    "github.com/unknown/package"            // ❌ 錯誤！沒在 go.mod 聲明
)
```

**特色**：Go 的 import 路徑就是完整的模組路徑

---

## 🎭 容易搞混的情況對比

### 1. 套件名 vs 導入名不一致

| 語言 | 依賴聲明名 | 實際導入名 | 原因 |
|------|------------|------------|------|
| **Python** | `scikit-learn` | `sklearn` | 歷史原因，套件名有連字號但模組名沒有 |
| **Python** | `pillow` | `PIL` | PIL 是舊名稱，但導入時仍用舊名 |
| **Rust** | `my-crate` | `my_crate` | Rust 自動轉換連字號為底線 |
| **JavaScript** | `@types/node` | 直接用 `node` 類型 | scoped package 特殊處理 |

### 2. 別名處理

```rust
// Rust - Cargo.toml
[dependencies]
math = { package = "advanced-math", version = "1.0" }

// 使用
use math::complex::Complex;  // ✅ 用別名
// use advanced_math::complex::Complex;  // ❌ 不能用原名
```

```python
# Python
import numpy as np          # ✅ 導入時別名
import pandas as pd         # ✅ 導入時別名
# 但依賴聲明時用原名：numpy, pandas
```

```javascript
// JavaScript
import { readFile as read } from 'fs/promises';  // ✅ 導入時別名
// 但 package.json 不需要聲明 fs
```

### 3. 內建庫處理

| 語言 | 內建庫是否需要聲明 | 範例 |
|------|-------------------|------|
| **Rust** | ❌ 不需要 | `std`, `core`, `alloc` |
| **Python** | ❌ 不需要 | `os`, `sys`, `json` |
| **Java** | ❌ 不需要 | `java.util.*`, `java.io.*` |
| **JavaScript** | ❌ 不需要 | `fs`, `path`, `http`（Node.js） |
| **Go** | ❌ 不需要 | `fmt`, `net/http`, `encoding/json` |
| **C#** | ❌ 不需要 | `System.*` 命名空間 |

---

## 🚨 常見錯誤模式

### 錯誤1：忘記聲明依賴
```rust
// ❌ Cargo.toml 忘記加 serde
use serde::Serialize;  // 編譯錯誤
```

### 錯誤2：用錯名稱
```python
# requirements.txt 中是 scikit-learn
import scikit-learn  # ❌ 錯誤！
import sklearn       # ✅ 正確！
```

### 錯誤3：路徑不對
```java
// ❌ 依賴是 jackson-core，但路徑錯誤
import com.fasterxml.jackson.wrong.path.Something;
```

### 錯誤4：版本衝突
```toml
# Cargo.toml
[dependencies]
tokio = "1.0"
some-lib = "1.0"  # 內部依賴 tokio 0.9

# 可能導致編譯錯誤或運行時問題
```

---

## 🛠️ 除錯技巧

### 1. 查看可用模組
```bash
# Rust
cargo doc --open

# Python
pip show scikit-learn
python -c "import sklearn; help(sklearn)"

# Node.js
npm list
node -e "console.log(require('express'))"
```

### 2. IDE 自動完成
- 現代 IDE 會讀取依賴檔案
- 提供可用模組的自動完成
- 標示錯誤的導入

### 3. 檢查依賴樹
```bash
# Rust
cargo tree

# Python
pip list

# Node.js
npm ls

# Java
mvn dependency:tree
```

---

## 🎯 記憶口訣

1. **先聲明，後使用**：依賴檔案聲明 → 代碼中導入
2. **名稱要對應**：導入的第一段 = 依賴聲明的名稱
3. **內建不用聲明**：標準庫/內建模組直接用
4. **有疑問看文檔**：不確定就查官方文檔
5. **IDE 是好朋友**：善用自動完成和錯誤提示

記住：**依賴管理的本質是告訴系統「我需要什麼」和「我要用什麼」！**

---

## 🗂️ Rust 模組路徑系統詳解

### 什麼是 `use super::`？

`use super::` 是 Rust 中用來導入**上層模組**或**同層模組**的語法！這跟檔案系統的路徑概念很像。

#### 相對路徑關鍵字：
- `super::` = 上一層目錄（父模組）
- `self::` = 當前目錄（當前模組）  
- `crate::` = 根目錄（crate 根模組）

### 📁 模組結構範例

```
src/
├── lib.rs                    # crate 根模組
└── webbluetooth/            # webbluetooth 模組
    ├── mod.rs               # 模組定義檔案
    ├── webbluetooth_manager.rs
    └── webbluetooth_hardware.rs
```

### 🗂️ 檔案系統類比

就像檔案系統一樣：

```bash
# 檔案系統路徑
../parent_dir/file.txt     # 對應 super::parent_module::something
./current_dir/file.txt     # 對應 self::current_module::something  
/root/absolute/path.txt    # 對應 crate::absolute::path::something
```

```rust
// Rust 模組系統
use super::parent_module::something;    // 相當於 ../
use self::current_module::something;    // 相當於 ./
use crate::absolute::path::something;   // 相當於 /
```

### 🎯 各種路徑語法對比

```rust
// 假設你在 src/webbluetooth/mod.rs

// 1. 相對路徑 - 同層模組
use self::webbluetooth_hardware::WebBluetoothHardwareConnector;

// 2. 相對路徑 - 上層模組
use super::some_function_in_lib_rs;

// 3. 絕對路徑 - 從 crate 根開始
use crate::webbluetooth::webbluetooth_hardware::WebBluetoothHardwareConnector;

// 4. 外部 crate
use buttplug::server::ButtplugServer;
```

### 📋 實際範例

#### 專案結構：
```
my_project/
├── src/
│   ├── lib.rs              # crate 根
│   ├── utils.rs            
│   └── network/
│       ├── mod.rs          # network 模組
│       ├── http.rs
│       └── websocket.rs
```

#### 在 `network/mod.rs` 中：
```rust
// 導入同層的 http.rs
use self::http::HttpClient;
// 或簡寫為
use http::HttpClient;

// 導入同層的 websocket.rs  
use self::websocket::WebSocketClient;

// 導入上層的 utils.rs
use super::utils::helper_function;

// 導入根層的東西
use crate::some_root_function;

// 導入外部 crate
use serde::Serialize;
```

#### 在 `network/http.rs` 中：
```rust
// 導入同層的 websocket.rs（透過父模組）
use super::websocket::WebSocketClient;

// 導入上上層的 utils.rs
use super::super::utils::helper_function;
// 或使用絕對路徑（推薦）
use crate::utils::helper_function;
```

### 🎨 最佳實踐

#### ✅ 推薦寫法：
```rust
// 優先使用絕對路徑，清楚明確
use crate::webbluetooth::webbluetooth_hardware::WebBluetoothHardwareConnector;

// 外部 crate 直接寫
use buttplug::server::ButtplugServer;

// 正確的 mod.rs 範例
mod webbluetooth_hardware;
mod webbluetooth_manager;

pub use webbluetooth_hardware::{WebBluetoothHardwareConnector, WebBluetoothHardware};
pub use webbluetooth_manager::{WebBluetoothCommunicationManagerBuilder, WebBluetoothCommunicationManager};
```

#### ⚠️ 避免的寫法：
```rust
// 太多層的相對路徑，容易搞混
use super::super::super::something;

// 建議改用絕對路徑
use crate::path::to::something;
```

### 🔧 常見問題診斷

如果 `use super::webbluetooth_hardware::WebBluetoothHardwareConnector;` 出現問題，可能的原因：

1. **路徑錯誤**：應該用 `self::` 而不是 `super::`
2. **模組沒有正確宣告**：需要在 `mod.rs` 中加 `mod webbluetooth_hardware;`
3. **檔案結構不如預期**：檢查實際的目錄結構

### 🗺️ 模組路徑速查表

| 位置 | 目標 | 語法 | 說明 |
|------|------|------|------|
| `src/mod.rs` | 同層檔案 | `use self::target;` | 當前模組下的子模組 |
| `src/mod.rs` | 父層檔案 | `use super::target;` | 上一層模組 |
| 任何位置 | crate 根 | `use crate::target;` | 從根模組開始的絕對路徑 |
| 任何位置 | 外部 crate | `use external::target;` | 外部依賴（需在 Cargo.toml 聲明） |

**記住**：當不確定時，優先使用 `crate::` 開頭的絕對路徑，更清楚且不容易出錯！