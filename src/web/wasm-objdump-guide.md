# wasm-objdump 完整使用指南

## 1. 目錄結構差異

### pkg 目錄（主要檢查對象）✅
- **生成方式：** `wasm-pack build` 產生
- **路徑範例：** `pkg/your_project_bg.wasm`
- **特點：**
  - 已經過 wasm-bindgen 處理，包含 JS 綁定
  - 經過優化壓縮，體積較小
  - **這是實際部署到生產環境的檔案**
  - 檔名格式：`{project_name}_bg.wasm`
  - 包含 TypeScript 定義檔 (`.d.ts`) 和 JS 膠水代碼

### target 目錄（除錯用）
- **生成方式：** `cargo build --target wasm32-unknown-unknown`
- **路徑範例：** `target/wasm32-unknown-unknown/{debug|release}/your_project.wasm`
- **特點：**
  - 純 Rust 編譯器輸出，未經 wasm-bindgen 處理
  - debug 版本包含更多除錯資訊
  - release 版本有基本優化但缺少 JS 綁定
  - 適合底層分析和效能除錯

---

## 2. 常用 wasm-objdump 指令

### 基礎資訊檢查
```bash
# 檢查基本資訊（sections, imports, exports）
wasm-objdump -h pkg/your_project_bg.wasm

# 詳細模組資訊
wasm-objdump -x pkg/your_project_bg.wasm

# 查看所有 export 的函數
wasm-objdump -j Export pkg/your_project_bg.wasm
```

### 程式碼分析
```bash
# 反組譯全部程式碼
wasm-objdump -d pkg/your_project_bg.wasm

# 反組譯特定函數
wasm-objdump -d pkg/your_project_bg.wasm --func-name=your_function

# 顯示原始碼對應關係（需要除錯符號）
wasm-objdump -S pkg/your_project_bg.wasm
```

### 大小分析
```bash
# 查看各 section 大小
wasm-objdump -h pkg/your_project_bg.wasm | grep -E "(Section|size)"

# 結合其他工具分析大小
wasm-strip --version  # 檢查是否有 wasm-strip
ls -lh pkg/*.wasm     # 直接查看檔案大小
```

### 字符串和隱藏資訊分析 🔍
```bash
# 查看所有可讀字符串（非常有用！）
strings -af pkg/your_project_bg.wasm

# 過濾特定模式的字符串
strings -af pkg/your_project_bg.wasm | grep -E "(panic|error|debug)"

# 查看函數名稱（特別是被混淆的）
strings -af pkg/your_project_bg.wasm | grep -E "^\w+::" 

# 查看可能的路徑資訊
strings -af pkg/your_project_bg.wasm | grep "src/"
```

---

## 3. 建議工作流程

### 開發階段
```bash
# 1. 建立包含除錯資訊的開發版本
wasm-pack build --dev

# 2. 檢查開發版本基本資訊
wasm-objdump -h pkg/your_project_bg.wasm

# 3. 查看 exports（確認 API 正確暴露）
wasm-objdump -j Export pkg/your_project_bg.wasm

# 4. 用 strings 檢查隱藏的除錯資訊 ⭐
strings -af pkg/your_project_bg.wasm | head -20
```

### 發佈前檢查
```bash
# 1. 建立優化的發佈版本
wasm-pack build --release

# 2. 檢查最終版本大小和結構
wasm-objdump -x pkg/your_project_bg.wasm

# 3. 確認關鍵函數存在
wasm-objdump -d pkg/your_project_bg.wasm | grep -A 5 "your_key_function"

# 4. 檢查是否意外包含除錯字符串 ⚠️
strings -af pkg/your_project_bg.wasm | grep -E "(debug|panic|assert|src/)"
```

### 效能除錯
```bash
# 1. 建立除錯版本進行比較
cargo build --target wasm32-unknown-unknown --release

# 2. 比較兩個版本的差異
wasm-objdump -x target/wasm32-unknown-unknown/release/your_project.wasm
wasm-objdump -x pkg/your_project_bg.wasm

# 3. 分析特定效能瓶頸
wasm-objdump -d -j Code pkg/your_project_bg.wasm | less
```

---

## 4. strings 深度分析技巧 🔍

### 為什麼 strings -af 很重要？
- **wasm-objdump 的限制：** 主要分析結構化資料，可能遺漏嵌入的字符串
- **strings 的優勢：** 能找到所有可讀文本，包括：
  - 隱藏的函數名稱
  - 除錯資訊
  - 錯誤訊息
  - 原始碼路徑
  - 編譯器資訊

### 實用的 strings 指令組合

```bash
# 基本字符串掃描
strings -af pkg/your_project_bg.wasm

# 找出可能的安全問題（洩露路徑）
strings -af pkg/your_project_bg.wasm | grep -E "/(home|Users|src|target)/"

# 檢查編譯器和版本資訊
strings -af pkg/your_project_bg.wasm | grep -E "(rustc|clang|llvm)"

# 查看錯誤和恐慌訊息
strings -af pkg/your_project_bg.wasm | grep -i -E "(panic|error|fail|abort)"

# 尋找函數名稱模式
strings -af pkg/your_project_bg.wasm | grep -E "^[a-zA-Z_][a-zA-Z0-9_]*::"

# 查看可能的測試代碼殘留
strings -af pkg/your_project_bg.wasm | grep -E "(test|mock|fixture)"

# 分析字符串長度分佈
strings -af pkg/your_project_bg.wasm | awk '{print length}' | sort -n | uniq -c
```

### strings + wasm-objdump 組合分析

```bash
# 1. 先用 strings 快速掃描
strings -af pkg/your_project_bg.wasm | head -50

# 2. 找到可疑函數名稱後，用 wasm-objdump 詳細分析
wasm-objdump -d pkg/your_project_bg.wasm --func-name=suspicious_function

# 3. 交叉驗證 export 清單
wasm-objdump -j Export pkg/your_project_bg.wasm
strings -af pkg/your_project_bg.wasm | grep -E "^(export|__wbindgen)"
```

---

## 5. 進階技巧與注意事項

### 檔案大小優化檢查
```bash
# 檢查是否包含不必要的 debug info
wasm-objdump -j "name" pkg/your_project_bg.wasm

# 查看 custom sections（可能包含額外資料）
wasm-objdump -j "producers" pkg/your_project_bg.wasm
```

### 相依性分析
```bash
# 檢查 import 的外部函數
wasm-objdump -j Import pkg/your_project_bg.wasm

# 查看記憶體配置
wasm-objdump -j Memory pkg/your_project_bg.wasm
```

### 錯誤排除
- **找不到函數：** 檢查是否使用了 `#[wasm_bindgen]` 標註
- **檔案太大：** 比較 debug 和 release 版本差異
- **執行錯誤：** 檢查 import/export 是否匹配

---

## 6. 差異對照表

| 特性 | pkg 目錄 | target 目錄 |
|------|----------|-------------|
| **用途** | 生產部署版本 ✅ | Rust 原始編譯版本 |
| **JS 綁定** | ✅ 含 wasm-bindgen 處理 | ❌ 純 WASM |
| **優化程度** | ✅ 高度優化 | 依建置模式而定 |
| **檔案命名** | `*_bg.wasm` | `*.wasm` |
| **除錯資訊** | 依 `--dev`/`--release` | 依 debug/release |
| **建議用途** | **主要檢查對象** | 深度除錯分析 |

---

## 7. 整合其他工具

### 與 wasm-pack 整合
```bash
# 同時生成多個目標
wasm-pack build --target web
wasm-pack build --target nodejs
wasm-pack build --target bundler

# 檢查不同目標的差異
wasm-objdump -x pkg/your_project_bg.wasm
```

### 與效能分析工具結合
```bash
# 結合 twiggy 分析大小
twiggy top pkg/your_project_bg.wasm

# 結合 wasm-opt 進一步優化
wasm-opt -O3 pkg/your_project_bg.wasm -o optimized.wasm
wasm-objdump -x optimized.wasm
```

---

## 8. 最佳實務總結

**檢查優先順序：**
1. **一律先檢查 `pkg/` 目錄** - 這是實際部署的版本
2. **搭配 `strings -af` 快速掃描** - 找出隱藏資訊 ⭐
3. 有問題時才深入 `target/` 目錄進行底層分析
4. 開發時使用 `--dev` 保留除錯資訊
5. 發佈前使用 `--release` 確認最終大小

**常用檢查清單：**
- ✅ 檔案大小合理
- ✅ 必要函數都有 export  
- ✅ import 依賴清楚明確
- ✅ 沒有意外的 debug section
- ✅ **沒有洩露敏感路徑或資訊** (用 strings 檢查)
- ✅ **release 版本沒有測試/除錯字符串殘留**