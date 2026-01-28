---
title: 使用延遲狀態初始化
impact: MEDIUM
impactDescription: 每次渲染都浪費運算
tags: react, hooks, useState, 效能, 初始化
---

## 使用延遲狀態初始化

對於昂貴的初始值，傳遞函數給 `useState`。如果不使用函數形式，初始化器會在每次渲染時執行，即使該值只使用一次。

**錯誤（每次渲染都執行）：**

```tsx
function FilteredList({ items }: { items: Item[] }) {
  // buildSearchIndex() 在每次渲染時都執行，即使初始化後
  const [searchIndex, setSearchIndex] = useState(buildSearchIndex(items))
  const [query, setQuery] = useState('')

  // 當 query 變更時，buildSearchIndex 會不必要地再次執行
  return <SearchResults index={searchIndex} query={query} />
}

function UserProfile() {
  // JSON.parse 每次渲染都執行
  const [settings, setSettings] = useState(
    JSON.parse(localStorage.getItem('settings') || '{}')
  )

  return <SettingsForm settings={settings} onChange={setSettings} />
}
```

**正確（只執行一次）：**

```tsx
function FilteredList({ items }: { items: Item[] }) {
  // buildSearchIndex() 只在初始渲染時執行
  const [searchIndex, setSearchIndex] = useState(() => buildSearchIndex(items))
  const [query, setQuery] = useState('')

  return <SearchResults index={searchIndex} query={query} />
}

function UserProfile() {
  // JSON.parse 只在初始渲染時執行
  const [settings, setSettings] = useState(() => {
    const stored = localStorage.getItem('settings')
    return stored ? JSON.parse(stored) : {}
  })

  return <SettingsForm settings={settings} onChange={setSettings} />
}
```

當從 localStorage/sessionStorage 計算初始值、建立資料結構（索引、map）、從 DOM 讀取，或執行繁重轉換時，使用延遲初始化。

對於簡單的原始值（`useState(0)`）、直接引用（`useState(props.value)`）或便宜的字面值（`useState({})`），函數形式是不必要的。
