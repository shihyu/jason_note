---
title: 將狀態讀取延遲到使用點
impact: MEDIUM
impactDescription: 避免不必要的訂閱
tags: rerender, searchParams, localStorage, 優化
---

## 將狀態讀取延遲到使用點

如果您只在回調中讀取動態狀態（searchParams、localStorage），就不要訂閱它。

**錯誤（訂閱所有 searchParams 變更）：**

```tsx
function ShareButton({ chatId }: { chatId: string }) {
  const searchParams = useSearchParams()

  const handleShare = () => {
    const ref = searchParams.get('ref')
    shareChat(chatId, { ref })
  }

  return <button onClick={handleShare}>分享</button>
}
```

**正確（按需讀取，無訂閱）：**

```tsx
function ShareButton({ chatId }: { chatId: string }) {
  const handleShare = () => {
    const params = new URLSearchParams(window.location.search)
    const ref = params.get('ref')
    shareChat(chatId, { ref })
  }

  return <button onClick={handleShare}>分享</button>
}
```
