# 操作日誌

格式：`## [日期] action | 標題`

---

## 使用範例

```markdown
## [2026-04-07] ingest | Rust 所有權教學
- 來源：sources/2026-04-07-rust-所有權.md
- 更新頁面：languages/rust, concepts/記憶體管理
- 新增：concepts/所有權地圖

## [2026-04-06] query | 比較 Rust 和 Go 的併發
- 回答：併發模型比較
- 歸檔：concepts/併發模型

## [2026-04-05] lint | 健康檢查
- 發現 2 個孤立頁面
- 標記 1 個過時主張
```

---

## 快速查詢最近 5 條

```bash
grep "^## \[" wiki/log.md | tail -5
```
