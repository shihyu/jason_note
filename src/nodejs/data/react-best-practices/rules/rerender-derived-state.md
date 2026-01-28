---
title: 訂閱衍生狀態
impact: MEDIUM
impactDescription: 減少重新渲染頻率
tags: rerender, 衍生狀態, media-query, 優化
---

## 訂閱衍生狀態

訂閱衍生的布林狀態而非連續值，以減少重新渲染頻率。

**錯誤（每個像素變化都重新渲染）：**

```tsx
function Sidebar() {
  const width = useWindowWidth()  // 持續更新
  const isMobile = width < 768
  return <nav className={isMobile ? 'mobile' : 'desktop'}>
}
```

**正確（只在布林值變化時重新渲染）：**

```tsx
function Sidebar() {
  const isMobile = useMediaQuery('(max-width: 767px)')
  return <nav className={isMobile ? 'mobile' : 'desktop'}>
}
```
