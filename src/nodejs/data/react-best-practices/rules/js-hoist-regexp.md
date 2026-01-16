---
title: 提升 RegExp 建立位置
impact: LOW-MEDIUM
impactDescription: 避免重複建立
tags: javascript, regexp, 優化, 記憶化
---

## 提升 RegExp 建立位置

不要在 render 內部建立 RegExp。將其提升到模組作用域或使用 `useMemo()` 進行記憶化。

**錯誤（每次渲染都建立新的 RegExp）：**

```tsx
function Highlighter({ text, query }: Props) {
  const regex = new RegExp(`(${query})`, 'gi')
  const parts = text.split(regex)
  return <>{parts.map((part, i) => ...)}</>
}
```

**正確（記憶化或提升）：**

```tsx
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function Highlighter({ text, query }: Props) {
  const regex = useMemo(
    () => new RegExp(`(${escapeRegex(query)})`, 'gi'),
    [query]
  )
  const parts = text.split(regex)
  return <>{parts.map((part, i) => ...)}</>
}
```

**警告（全域正規表達式具有可變狀態）：**

全域正規表達式（`/g`）具有可變的 `lastIndex` 狀態：

```typescript
const regex = /foo/g
regex.test('foo')  // true, lastIndex = 3
regex.test('foo')  // false, lastIndex = 0
```
