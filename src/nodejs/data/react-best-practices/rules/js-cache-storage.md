---
title: 快取 Storage API 呼叫
impact: LOW-MEDIUM
impactDescription: 減少昂貴的 I/O 操作
tags: javascript, localStorage, storage, 快取, 效能
---

## 快取 Storage API 呼叫

`localStorage`、`sessionStorage` 和 `document.cookie` 是同步且昂貴的操作。將讀取結果快取在記憶體中。

**錯誤（每次呼叫都讀取 storage）：**

```typescript
function getTheme() {
  return localStorage.getItem('theme') ?? 'light'
}
// 呼叫 10 次 = 10 次 storage 讀取
```

**正確（Map 快取）：**

```typescript
const storageCache = new Map<string, string | null>()

function getLocalStorage(key: string) {
  if (!storageCache.has(key)) {
    storageCache.set(key, localStorage.getItem(key))
  }
  return storageCache.get(key)
}

function setLocalStorage(key: string, value: string) {
  localStorage.setItem(key, value)
  storageCache.set(key, value)  // 保持快取同步
}
```

使用 Map（而非 hook），這樣它可以在任何地方運作：工具函數、事件處理器，不只是 React 元件。

**Cookie 快取：**

```typescript
let cookieCache: Record<string, string> | null = null

function getCookie(name: string) {
  if (!cookieCache) {
    cookieCache = Object.fromEntries(
      document.cookie.split('; ').map(c => c.split('='))
    )
  }
  return cookieCache[name]
}
```

**重要（外部變更時使快取失效）：**

如果 storage 可能被外部變更（其他分頁、伺服器設定的 cookies），需要使快取失效：

```typescript
window.addEventListener('storage', (e) => {
  if (e.key) storageCache.delete(e.key)
})

document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') {
    storageCache.clear()
  }
})
```
