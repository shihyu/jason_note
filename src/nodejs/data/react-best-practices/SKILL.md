---
name: vercel-react-best-practices
description: 來自 Vercel 工程團隊的 React 和 Next.js 效能優化指南。當撰寫、審查或重構 React/Next.js 程式碼時應使用此技能，以確保採用最佳效能模式。適用於涉及 React 元件、Next.js 頁面、資料擷取、打包優化或效能改進的任務。
license: MIT
metadata:
  author: vercel
  version: "1.0.0"
---

# Vercel React 最佳實踐

由 Vercel 維護的 React 和 Next.js 應用程式完整效能優化指南。包含 8 大類別共 45 條規則，依影響程度排序，用於指導自動重構和程式碼生成。

## 適用時機

在以下情況參考這些指南：
- 撰寫新的 React 元件或 Next.js 頁面
- 實作資料擷取（客戶端或伺服器端）
- 審查程式碼的效能問題
- 重構現有的 React/Next.js 程式碼
- 優化打包大小或載入時間

## 規則類別優先順序

| 優先級 | 類別 | 影響程度 | 前綴 |
|--------|------|----------|------|
| 1 | 消除瀑布流 | 關鍵 | `async-` |
| 2 | 打包大小優化 | 關鍵 | `bundle-` |
| 3 | 伺服器端效能 | 高 | `server-` |
| 4 | 客戶端資料擷取 | 中高 | `client-` |
| 5 | 重新渲染優化 | 中 | `rerender-` |
| 6 | 渲染效能 | 中 | `rendering-` |
| 7 | JavaScript 效能 | 低中 | `js-` |
| 8 | 進階模式 | 低 | `advanced-` |

## 快速參考

### 1. 消除瀑布流（關鍵）

- `async-defer-await` - 將 await 移至實際使用的分支中
- `async-parallel` - 對獨立操作使用 Promise.all()
- `async-dependencies` - 對部分依賴使用 better-all
- `async-api-routes` - 在 API 路由中提早啟動 Promise，延後 await
- `async-suspense-boundaries` - 使用 Suspense 串流內容

### 2. 打包大小優化（關鍵）

- `bundle-barrel-imports` - 直接匯入，避免桶狀檔案
- `bundle-dynamic-imports` - 對大型元件使用 next/dynamic
- `bundle-defer-third-party` - 在 hydration 後載入分析/日誌工具
- `bundle-conditional` - 僅在功能啟用時載入模組
- `bundle-preload` - 在 hover/focus 時預載以提升感知速度

### 3. 伺服器端效能（高）

- `server-cache-react` - 使用 React.cache() 進行單次請求去重
- `server-cache-lru` - 使用 LRU 快取進行跨請求快取
- `server-serialization` - 最小化傳遞給客戶端元件的資料
- `server-parallel-fetching` - 重構元件以並行化擷取
- `server-after-nonblocking` - 使用 after() 進行非阻塞操作

### 4. 客戶端資料擷取（中高）

- `client-swr-dedup` - 使用 SWR 進行自動請求去重
- `client-event-listeners` - 去重全域事件監聽器

### 5. 重新渲染優化（中）

- `rerender-defer-reads` - 不要訂閱僅在回呼中使用的狀態
- `rerender-memo` - 將昂貴的工作提取到記憶化元件中
- `rerender-dependencies` - 在 effect 中使用原始型別依賴
- `rerender-derived-state` - 訂閱衍生的布林值，而非原始值
- `rerender-functional-setstate` - 使用函數式 setState 以獲得穩定的回呼
- `rerender-lazy-state-init` - 對昂貴的值傳遞函數給 useState
- `rerender-transitions` - 對非緊急更新使用 startTransition

### 6. 渲染效能（中）

- `rendering-animate-svg-wrapper` - 動畫化 div 包裝器，而非 SVG 元素
- `rendering-content-visibility` - 對長列表使用 content-visibility
- `rendering-hoist-jsx` - 將靜態 JSX 提取到元件外部
- `rendering-svg-precision` - 降低 SVG 座標精度
- `rendering-hydration-no-flicker` - 對僅客戶端資料使用內聯腳本
- `rendering-activity` - 使用 Activity 元件進行顯示/隱藏
- `rendering-conditional-render` - 條件渲染使用三元運算子，而非 &&

### 7. JavaScript 效能（低中）

- `js-batch-dom-css` - 透過類別或 cssText 批次處理 CSS 變更
- `js-index-maps` - 為重複查詢建立 Map
- `js-cache-property-access` - 在迴圈中快取物件屬性
- `js-cache-function-results` - 在模組層級 Map 中快取函數結果
- `js-cache-storage` - 快取 localStorage/sessionStorage 讀取
- `js-combine-iterations` - 將多個 filter/map 合併為一個迴圈
- `js-length-check-first` - 在昂貴比較前先檢查陣列長度
- `js-early-exit` - 從函數提早返回
- `js-hoist-regexp` - 將 RegExp 建立提升到迴圈外部
- `js-min-max-loop` - 使用迴圈取得最小/最大值，而非排序
- `js-set-map-lookups` - 使用 Set/Map 進行 O(1) 查詢
- `js-tosorted-immutable` - 使用 toSorted() 保持不可變性

### 8. 進階模式（低）

- `advanced-event-handler-refs` - 將事件處理器儲存在 refs 中
- `advanced-use-latest` - 使用 useLatest 取得穩定的回呼 refs

## 使用方式

閱讀個別規則檔案以獲得詳細說明和程式碼範例：

```
rules/async-parallel.md
rules/bundle-barrel-imports.md
rules/_sections.md
```

每個規則檔案包含：
- 簡要說明其重要性
- 錯誤程式碼範例與說明
- 正確程式碼範例與說明
- 額外背景資訊與參考資料

## 完整編譯文件

完整指南（包含所有展開的規則）：`AGENTS.md`
