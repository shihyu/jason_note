---
title: 使用 Activity 元件進行顯示/隱藏
impact: MEDIUM
impactDescription: 保留狀態/DOM
tags: rendering, activity, 可見性, 狀態保留
---

## 使用 Activity 元件進行顯示/隱藏

使用 React 的 `<Activity>` 來保留頻繁切換可見性的昂貴元件的狀態/DOM。

**使用方式：**

```tsx
import { Activity } from 'react'

function Dropdown({ isOpen }: Props) {
  return (
    <Activity mode={isOpen ? 'visible' : 'hidden'}>
      <ExpensiveMenu />
    </Activity>
  )
}
```

避免昂貴的重新渲染和狀態丟失。
