---
title: 使用明確的條件渲染
impact: LOW
impactDescription: 防止渲染 0 或 NaN
tags: rendering, 條件, jsx, 假值
---

## 使用明確的條件渲染

當條件可能是 `0`、`NaN` 或其他會被渲染的假值時，使用明確的三元運算子（`? :`）而非 `&&` 進行條件渲染。

**錯誤（當 count 為 0 時渲染 "0"）：**

```tsx
function Badge({ count }: { count: number }) {
  return (
    <div>
      {count && <span className="badge">{count}</span>}
    </div>
  )
}

// 當 count = 0 時，渲染：<div>0</div>
// 當 count = 5 時，渲染：<div><span class="badge">5</span></div>
```

**正確（當 count 為 0 時不渲染任何內容）：**

```tsx
function Badge({ count }: { count: number }) {
  return (
    <div>
      {count > 0 ? <span className="badge">{count}</span> : null}
    </div>
  )
}

// 當 count = 0 時，渲染：<div></div>
// 當 count = 5 時，渲染：<div><span class="badge">5</span></div>
```
