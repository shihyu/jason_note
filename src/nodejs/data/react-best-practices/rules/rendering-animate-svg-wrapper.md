---
title: 動畫化 SVG 包裝元素而非 SVG 元素本身
impact: LOW
impactDescription: 啟用硬體加速
tags: rendering, svg, css, 動畫, 效能
---

## 動畫化 SVG 包裝元素而非 SVG 元素本身

許多瀏覽器對 SVG 元素的 CSS3 動畫沒有硬體加速。將 SVG 包裝在 `<div>` 中，並改為動畫化包裝元素。

**錯誤（直接動畫化 SVG - 無硬體加速）：**

```tsx
function LoadingSpinner() {
  return (
    <svg
      className="animate-spin"
      width="24"
      height="24"
      viewBox="0 0 24 24"
    >
      <circle cx="12" cy="12" r="10" stroke="currentColor" />
    </svg>
  )
}
```

**正確（動畫化包裝 div - 硬體加速）：**

```tsx
function LoadingSpinner() {
  return (
    <div className="animate-spin">
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
      >
        <circle cx="12" cy="12" r="10" stroke="currentColor" />
      </svg>
    </div>
  )
}
```

這適用於所有 CSS 變換和過渡（`transform`、`opacity`、`translate`、`scale`、`rotate`）。包裝 div 允許瀏覽器使用 GPU 加速以獲得更流暢的動畫。
