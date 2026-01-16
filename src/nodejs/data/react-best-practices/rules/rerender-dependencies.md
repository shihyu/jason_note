---
title: 縮小 Effect 依賴範圍
impact: LOW
impactDescription: 最小化 effect 重新執行
tags: rerender, useEffect, 依賴, 優化
---

## 縮小 Effect 依賴範圍

指定原始型別依賴而非物件，以最小化 effect 重新執行。

**錯誤（任何 user 欄位變更都會重新執行）：**

```tsx
useEffect(() => {
  console.log(user.id)
}, [user])
```

**正確（只在 id 變更時重新執行）：**

```tsx
useEffect(() => {
  console.log(user.id)
}, [user.id])
```

**對於衍生狀態，在 effect 外部計算：**

```tsx
// 錯誤：width=767, 766, 765... 每次都執行
useEffect(() => {
  if (width < 768) {
    enableMobileMode()
  }
}, [width])

// 正確：只在布林值轉換時執行
const isMobile = width < 768
useEffect(() => {
  if (isMobile) {
    enableMobileMode()
  }
}, [isMobile])
```
