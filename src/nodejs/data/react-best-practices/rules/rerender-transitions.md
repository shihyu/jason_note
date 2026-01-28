---
title: 對非緊急更新使用 Transitions
impact: MEDIUM
impactDescription: 維持 UI 響應性
tags: rerender, transitions, startTransition, 效能
---

## 對非緊急更新使用 Transitions

將頻繁的非緊急狀態更新標記為 transitions，以維持 UI 響應性。

**錯誤（每次滾動都阻塞 UI）：**

```tsx
function ScrollTracker() {
  const [scrollY, setScrollY] = useState(0)
  useEffect(() => {
    const handler = () => setScrollY(window.scrollY)
    window.addEventListener('scroll', handler, { passive: true })
    return () => window.removeEventListener('scroll', handler)
  }, [])
}
```

**正確（非阻塞更新）：**

```tsx
import { startTransition } from 'react'

function ScrollTracker() {
  const [scrollY, setScrollY] = useState(0)
  useEffect(() => {
    const handler = () => {
      startTransition(() => setScrollY(window.scrollY))
    }
    window.addEventListener('scroll', handler, { passive: true })
    return () => window.removeEventListener('scroll', handler)
  }, [])
}
```
