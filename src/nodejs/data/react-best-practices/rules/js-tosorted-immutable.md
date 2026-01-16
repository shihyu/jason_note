---
title: 使用 toSorted() 而非 sort() 以確保不可變性
impact: MEDIUM-HIGH
impactDescription: 防止 React 狀態中的變異 bug
tags: javascript, 陣列, 不可變性, react, 狀態, 變異
---

## 使用 toSorted() 而非 sort() 以確保不可變性

`.sort()` 會原地修改陣列，這可能導致 React 狀態和 props 的 bug。使用 `.toSorted()` 建立新的排序陣列而不修改原陣列。

**錯誤（修改原始陣列）：**

```typescript
function UserList({ users }: { users: User[] }) {
  // 修改了 users prop 陣列！
  const sorted = useMemo(
    () => users.sort((a, b) => a.name.localeCompare(b.name)),
    [users]
  )
  return <div>{sorted.map(renderUser)}</div>
}
```

**正確（建立新陣列）：**

```typescript
function UserList({ users }: { users: User[] }) {
  // 建立新的排序陣列，原陣列不變
  const sorted = useMemo(
    () => users.toSorted((a, b) => a.name.localeCompare(b.name)),
    [users]
  )
  return <div>{sorted.map(renderUser)}</div>
}
```

**為什麼這在 React 中很重要：**

1. Props/狀態變異破壞 React 的不可變性模型 - React 期望 props 和狀態被視為唯讀
2. 導致閉包過時的 bug - 在閉包（回調、effect）中修改陣列可能導致非預期行為

**瀏覽器支援（舊版瀏覽器的備援方案）：**

`.toSorted()` 在所有現代瀏覽器中可用（Chrome 110+、Safari 16+、Firefox 115+、Node.js 20+）。對於舊環境，使用展開運算子：

```typescript
// 舊版瀏覽器的備援方案
const sorted = [...items].sort((a, b) => a.value - b.value)
```

**其他不可變陣列方法：**

- `.toSorted()` - 不可變排序
- `.toReversed()` - 不可變反轉
- `.toSpliced()` - 不可變拼接
- `.with()` - 不可變元素替換
