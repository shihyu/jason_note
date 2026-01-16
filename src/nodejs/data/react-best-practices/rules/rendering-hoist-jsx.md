---
title: 提升靜態 JSX 元素
impact: LOW
impactDescription: 避免重複建立
tags: rendering, jsx, 靜態, 優化
---

## 提升靜態 JSX 元素

將靜態 JSX 提取到元件外部，避免重複建立。

**錯誤（每次渲染都重新建立元素）：**

```tsx
function LoadingSkeleton() {
  return <div className="animate-pulse h-20 bg-gray-200" />
}

function Container() {
  return (
    <div>
      {loading && <LoadingSkeleton />}
    </div>
  )
}
```

**正確（重複使用相同元素）：**

```tsx
const loadingSkeleton = (
  <div className="animate-pulse h-20 bg-gray-200" />
)

function Container() {
  return (
    <div>
      {loading && loadingSkeleton}
    </div>
  )
}
```

這對於大型且靜態的 SVG 節點特別有幫助，因為每次渲染時重新建立它們可能很昂貴。

**注意：** 如果您的專案啟用了 [React Compiler](https://react.dev/learn/react-compiler)，編譯器會自動提升靜態 JSX 元素並優化元件重新渲染，使手動提升變得不必要。
