---
title: 對大型元件使用動態匯入
impact: CRITICAL
impactDescription: 直接影響 TTI 和 LCP
tags: bundle, 動態匯入, 程式碼分割, next-dynamic
---

## 對大型元件使用動態匯入

使用 `next/dynamic` 延遲載入初始渲染不需要的大型元件。

**錯誤（Monaco 與主要 chunk 一起打包約 300KB）：**

```tsx
import { MonacoEditor } from './monaco-editor'

function CodePanel({ code }: { code: string }) {
  return <MonacoEditor value={code} />
}
```

**正確（Monaco 按需載入）：**

```tsx
import dynamic from 'next/dynamic'

const MonacoEditor = dynamic(
  () => import('./monaco-editor').then(m => m.MonacoEditor),
  { ssr: false }
)

function CodePanel({ code }: { code: string }) {
  return <MonacoEditor value={code} />
}
```
