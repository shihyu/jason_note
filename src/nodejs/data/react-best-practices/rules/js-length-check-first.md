---
title: 陣列比較時先檢查長度
impact: MEDIUM-HIGH
impactDescription: 長度不同時避免昂貴操作
tags: javascript, 陣列, 效能, 優化, 比較
---

## 陣列比較時先檢查長度

當使用昂貴操作（排序、深度相等、序列化）比較陣列時，先檢查長度。如果長度不同，陣列不可能相等。

在實際應用中，當比較在熱點路徑（事件處理器、渲染迴圈）執行時，此優化特別有價值。

**錯誤（總是執行昂貴的比較）：**

```typescript
function hasChanges(current: string[], original: string[]) {
  // 即使長度不同，也總是排序和連接
  return current.sort().join() !== original.sort().join()
}
```

即使 `current.length` 是 5 而 `original.length` 是 100，也會執行兩次 O(n log n) 排序。還有連接陣列和比較字串的額外開銷。

**正確（先進行 O(1) 長度檢查）：**

```typescript
function hasChanges(current: string[], original: string[]) {
  // 長度不同時提前返回
  if (current.length !== original.length) {
    return true
  }
  // 只在長度相同時排序/連接
  const currentSorted = current.toSorted()
  const originalSorted = original.toSorted()
  for (let i = 0; i < currentSorted.length; i++) {
    if (currentSorted[i] !== originalSorted[i]) {
      return true
    }
  }
  return false
}
```

這種新方法更有效率，因為：
- 長度不同時避免排序和連接陣列的開銷
- 避免為連接的字串消耗記憶體（對大型陣列特別重要）
- 避免修改原始陣列
- 發現差異時提前返回
