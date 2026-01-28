---
title: 將事件處理器儲存在 Refs 中
impact: LOW
impactDescription: 穩定的訂閱
tags: advanced, hooks, refs, 事件處理器, 優化
---

## 將事件處理器儲存在 Refs 中

當回調函數用於不應在回調變更時重新訂閱的 effect 中，請將其儲存在 refs 中。

**錯誤（每次渲染都會重新訂閱）：**

```tsx
function useWindowEvent(event: string, handler: () => void) {
  useEffect(() => {
    window.addEventListener(event, handler)
    return () => window.removeEventListener(event, handler)
  }, [event, handler])
}
```

**正確（穩定的訂閱）：**

```tsx
function useWindowEvent(event: string, handler: () => void) {
  const handlerRef = useRef(handler)
  useEffect(() => {
    handlerRef.current = handler
  }, [handler])

  useEffect(() => {
    const listener = () => handlerRef.current()
    window.addEventListener(event, listener)
    return () => window.removeEventListener(event, listener)
  }, [event])
}
```

**替代方案：如果使用最新版 React，可以使用 `useEffectEvent`：**

```tsx
import { useEffectEvent } from 'react'

function useWindowEvent(event: string, handler: () => void) {
  const onEvent = useEffectEvent(handler)

  useEffect(() => {
    window.addEventListener(event, onEvent)
    return () => window.removeEventListener(event, onEvent)
  }, [event])
}
```

`useEffectEvent` 為相同的模式提供更簡潔的 API：它建立一個穩定的函數引用，始終呼叫最新版本的處理器。
