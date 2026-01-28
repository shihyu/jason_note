---
title: 延遲載入非關鍵第三方函式庫
impact: MEDIUM
impactDescription: 在 hydration 後載入
tags: bundle, 第三方, 分析, 延遲
---

## 延遲載入非關鍵第三方函式庫

分析、日誌和錯誤追蹤不會阻塞使用者互動。在 hydration 後載入它們。

**錯誤（阻塞初始打包）：**

```tsx
import { Analytics } from '@vercel/analytics/react'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
```

**正確（在 hydration 後載入）：**

```tsx
import dynamic from 'next/dynamic'

const Analytics = dynamic(
  () => import('@vercel/analytics/react').then(m => m.Analytics),
  { ssr: false }
)

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
```
