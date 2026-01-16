---
title: 使用函數式 setState 更新
impact: MEDIUM
impactDescription: 防止閉包過時和不必要的回調重建
tags: react, hooks, useState, useCallback, 回調, 閉包
---

## 使用函數式 setState 更新

當根據當前狀態值更新狀態時，使用 setState 的函數式更新形式，而非直接引用狀態變數。這可以防止閉包過時、消除不必要的依賴，並建立穩定的回調引用。

**錯誤（需要狀態作為依賴）：**

```tsx
function TodoList() {
  const [items, setItems] = useState(initialItems)

  // 回調必須依賴 items，每次 items 變更時都會重建
  const addItems = useCallback((newItems: Item[]) => {
    setItems([...items, ...newItems])
  }, [items])  // ❌ items 依賴導致重建

  // 如果忘記依賴，有閉包過時的風險
  const removeItem = useCallback((id: string) => {
    setItems(items.filter(item => item.id !== id))
  }, [])  // ❌ 缺少 items 依賴 - 將使用過時的 items！

  return <ItemsEditor items={items} onAdd={addItems} onRemove={removeItem} />
}
```

第一個回調每次 `items` 變更時都會重建，這可能導致子元件不必要地重新渲染。第二個回調有閉包過時的 bug——它會始終引用初始的 `items` 值。

**正確（穩定的回調，無閉包過時）：**

```tsx
function TodoList() {
  const [items, setItems] = useState(initialItems)

  // 穩定的回調，永不重建
  const addItems = useCallback((newItems: Item[]) => {
    setItems(curr => [...curr, ...newItems])
  }, [])  // ✅ 不需要依賴

  // 總是使用最新狀態，無閉包過時風險
  const removeItem = useCallback((id: string) => {
    setItems(curr => curr.filter(item => item.id !== id))
  }, [])  // ✅ 安全且穩定

  return <ItemsEditor items={items} onAdd={addItems} onRemove={removeItem} />
}
```

**優點：**

1. **穩定的回調引用** - 狀態變更時回調不需要重建
2. **無閉包過時** - 始終操作最新的狀態值
3. **更少的依賴** - 簡化依賴陣列並減少記憶體洩漏
4. **防止 bug** - 消除最常見的 React 閉包 bug 來源

**何時使用函數式更新：**

- 任何依賴當前狀態值的 setState
- 在需要狀態的 useCallback/useMemo 內部
- 引用狀態的事件處理器
- 更新狀態的非同步操作

**何時直接更新即可：**

- 設定狀態為靜態值：`setCount(0)`
- 僅從 props/參數設定狀態：`setName(newName)`
- 狀態不依賴先前的值

**注意：** 如果您的專案啟用了 [React Compiler](https://react.dev/learn/react-compiler)，編譯器可以自動優化某些情況，但仍建議使用函數式更新以確保正確性並防止閉包過時的 bug。
