---
title: 使用 useLatest 取得穩定的回調 Refs
impact: LOW
impactDescription: 防止 effect 重複執行
tags: advanced, hooks, useLatest, refs, 優化
---

## 使用 useLatest 取得穩定的回調 Refs

在回調中存取最新值，而無需將它們加入依賴陣列。防止 effect 重複執行，同時避免閉包過時問題。

**實作方式：**

```typescript
function useLatest<T>(value: T) {
  const ref = useRef(value)
  useEffect(() => {
    ref.current = value
  }, [value])
  return ref
}
```

**錯誤（每次回調變更時 effect 都會重新執行）：**

```tsx
function SearchInput({ onSearch }: { onSearch: (q: string) => void }) {
  const [query, setQuery] = useState('')

  useEffect(() => {
    const timeout = setTimeout(() => onSearch(query), 300)
    return () => clearTimeout(timeout)
  }, [query, onSearch])
}
```

**正確（穩定的 effect，使用最新的回調）：**

```tsx
function SearchInput({ onSearch }: { onSearch: (q: string) => void }) {
  const [query, setQuery] = useState('')
  const onSearchRef = useLatest(onSearch)

  useEffect(() => {
    const timeout = setTimeout(() => onSearchRef.current(query), 300)
    return () => clearTimeout(timeout)
  }, [query])
}
```
