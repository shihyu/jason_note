# React 最佳實踐

為 AI 代理和 LLM 建立和維護 React 最佳實踐的結構化儲存庫。

## 結構

- `rules/` - 個別規則檔案（每個規則一個檔案）
  - `_sections.md` - 章節中繼資料（標題、影響程度、描述）
  - `_template.md` - 建立新規則的範本
  - `area-description.md` - 個別規則檔案
- `src/` - 建置腳本和工具
- `metadata.json` - 文件中繼資料（版本、組織、摘要）
- __`AGENTS.md`__ - 編譯輸出（自動生成）
- __`test-cases.json`__ - LLM 評估測試案例（自動生成）

## 開始使用

1. 安裝依賴：
   ```bash
   pnpm install
   ```

2. 從規則建置 AGENTS.md：
   ```bash
   pnpm build
   ```

3. 驗證規則檔案：
   ```bash
   pnpm validate
   ```

4. 提取測試案例：
   ```bash
   pnpm extract-tests
   ```

## 建立新規則

1. 複製 `rules/_template.md` 到 `rules/area-description.md`
2. 選擇適當的區域前綴：
   - `async-` 用於消除瀑布流（第 1 章節）
   - `bundle-` 用於打包大小優化（第 2 章節）
   - `server-` 用於伺服器端效能（第 3 章節）
   - `client-` 用於客戶端資料擷取（第 4 章節）
   - `rerender-` 用於重新渲染優化（第 5 章節）
   - `rendering-` 用於渲染效能（第 6 章節）
   - `js-` 用於 JavaScript 效能（第 7 章節）
   - `advanced-` 用於進階模式（第 8 章節）
3. 填寫前置資料和內容
4. 確保有清楚的範例和說明
5. 執行 `pnpm build` 以重新生成 AGENTS.md 和 test-cases.json

## 規則檔案結構

每個規則檔案應遵循以下結構：

```markdown
---
title: 規則標題
impact: MEDIUM
impactDescription: 選填的影響描述
tags: 標籤1, 標籤2, 標籤3
---

## 規則標題

規則的簡要說明及其重要性。

**錯誤（問題描述）：**

```typescript
// 錯誤程式碼範例
```

**正確（正確做法描述）：**

```typescript
// 正確程式碼範例
```

範例後的選填說明文字。

參考資料：[連結](https://example.com)

## 檔案命名慣例

- 以 `_` 開頭的檔案是特殊檔案（不納入建置）
- 規則檔案：`area-description.md`（例如：`async-parallel.md`）
- 章節從檔名前綴自動推斷
- 規則在每個章節內按標題字母順序排列
- ID（例如 1.1, 1.2）在建置時自動生成

## 影響等級

- `CRITICAL` - 最高優先級，重大效能提升
- `HIGH` - 顯著效能改善
- `MEDIUM-HIGH` - 中高度提升
- `MEDIUM` - 中度效能改善
- `LOW-MEDIUM` - 低中度提升
- `LOW` - 漸進式改善

## 腳本

- `pnpm build` - 將規則編譯成 AGENTS.md
- `pnpm validate` - 驗證所有規則檔案
- `pnpm extract-tests` - 提取 LLM 評估測試案例
- `pnpm dev` - 建置並驗證

## 貢獻

新增或修改規則時：

1. 為您的章節使用正確的檔名前綴
2. 遵循 `_template.md` 結構
3. 包含清楚的錯誤/正確範例與說明
4. 新增適當的標籤
5. 執行 `pnpm build` 以重新生成 AGENTS.md 和 test-cases.json
6. 規則會自動按標題排序 - 無需手動管理編號！

## 致謝

最初由 [@shuding](https://x.com/shuding) 在 [Vercel](https://vercel.com) 建立。
