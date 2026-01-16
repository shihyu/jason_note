---
title: 批次處理 DOM CSS 變更
impact: MEDIUM
impactDescription: 減少重排/重繪
tags: javascript, dom, css, 效能, 重排
---

## 批次處理 DOM CSS 變更

避免逐一變更樣式屬性。透過 class 或 `cssText` 將多個 CSS 變更合併在一起，以最小化瀏覽器重排。

**錯誤（多次重排）：**

```typescript
function updateElementStyles(element: HTMLElement) {
  // 每一行都會觸發重排
  element.style.width = '100px'
  element.style.height = '200px'
  element.style.backgroundColor = 'blue'
  element.style.border = '1px solid black'
}
```

**正確（新增 class - 單次重排）：**

```typescript
// CSS 檔案
.highlighted-box {
  width: 100px;
  height: 200px;
  background-color: blue;
  border: 1px solid black;
}

// JavaScript
function updateElementStyles(element: HTMLElement) {
  element.classList.add('highlighted-box')
}
```

**正確（變更 cssText - 單次重排）：**

```typescript
function updateElementStyles(element: HTMLElement) {
  element.style.cssText = `
    width: 100px;
    height: 200px;
    background-color: blue;
    border: 1px solid black;
  `
}
```

**React 範例：**

```tsx
// 錯誤：逐一變更樣式
function Box({ isHighlighted }: { isHighlighted: boolean }) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (ref.current && isHighlighted) {
      ref.current.style.width = '100px'
      ref.current.style.height = '200px'
      ref.current.style.backgroundColor = 'blue'
    }
  }, [isHighlighted])

  return <div ref={ref}>Content</div>
}

// 正確：切換 class
function Box({ isHighlighted }: { isHighlighted: boolean }) {
  return (
    <div className={isHighlighted ? 'highlighted-box' : ''}>
      Content
    </div>
  )
}
```

盡可能優先使用 CSS class 而非行內樣式。Class 會被瀏覽器快取，並提供更好的關注點分離。
