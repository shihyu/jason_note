---
title: 去除重複的全域事件監聽器
impact: LOW
impactDescription: N 個元件共用單一監聽器
tags: client, swr, 事件監聽器, 訂閱
---

## 去除重複的全域事件監聽器

使用 `useSWRSubscription()` 在元件實例之間共享全域事件監聽器。

**錯誤（N 個實例 = N 個監聽器）：**

```tsx
function useKeyboardShortcut(key: string, callback: () => void) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.metaKey && e.key === key) {
        callback()
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [key, callback])
}
```

當多次使用 `useKeyboardShortcut` hook 時，每個實例都會註冊一個新的監聽器。

**正確（N 個實例 = 1 個監聽器）：**

```tsx
import useSWRSubscription from 'swr/subscription'

// 模組層級的 Map，用於追蹤每個按鍵的回調
const keyCallbacks = new Map<string, Set<() => void>>()

function useKeyboardShortcut(key: string, callback: () => void) {
  // 在 Map 中註冊此回調
  useEffect(() => {
    if (!keyCallbacks.has(key)) {
      keyCallbacks.set(key, new Set())
    }
    keyCallbacks.get(key)!.add(callback)

    return () => {
      const set = keyCallbacks.get(key)
      if (set) {
        set.delete(callback)
        if (set.size === 0) {
          keyCallbacks.delete(key)
        }
      }
    }
  }, [key, callback])

  useSWRSubscription('global-keydown', () => {
    const handler = (e: KeyboardEvent) => {
      if (e.metaKey && keyCallbacks.has(e.key)) {
        keyCallbacks.get(e.key)!.forEach(cb => cb())
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  })
}

function Profile() {
  // 多個快捷鍵將共用同一個監聽器
  useKeyboardShortcut('p', () => { /* ... */ })
  useKeyboardShortcut('k', () => { /* ... */ })
  // ...
}
```
