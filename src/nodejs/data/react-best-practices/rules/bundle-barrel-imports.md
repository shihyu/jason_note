---
title: 避免桶狀檔案匯入
impact: CRITICAL
impactDescription: 200-800ms 匯入成本，慢速建置
tags: bundle, 匯入, tree-shaking, 桶狀檔案, 效能
---

## 避免桶狀檔案匯入

直接從原始檔案匯入，而不是從桶狀檔案匯入，以避免載入數千個未使用的模組。**桶狀檔案**是重新匯出多個模組的入口點（例如：執行 `export * from './module'` 的 `index.js`）。

流行的圖示和元件函式庫在其入口檔案中可能有**多達 10,000 個重新匯出**。對於許多 React 套件，**僅僅匯入它們就需要 200-800ms**，影響開發速度和生產冷啟動。

**為什麼 tree-shaking 沒有幫助：** 當函式庫被標記為外部（不打包）時，打包器無法優化它。如果你為了啟用 tree-shaking 而打包它，建置會因分析整個模組圖而大幅變慢。

**錯誤（匯入整個函式庫）：**

```tsx
import { Check, X, Menu } from 'lucide-react'
// 載入 1,583 個模組，開發時額外花費約 2.8 秒
// 執行時成本：每次冷啟動 200-800ms

import { Button, TextField } from '@mui/material'
// 載入 2,225 個模組，開發時額外花費約 4.2 秒
```

**正確（只匯入你需要的）：**

```tsx
import Check from 'lucide-react/dist/esm/icons/check'
import X from 'lucide-react/dist/esm/icons/x'
import Menu from 'lucide-react/dist/esm/icons/menu'
// 只載入 3 個模組（約 2KB vs 約 1MB）

import Button from '@mui/material/Button'
import TextField from '@mui/material/TextField'
// 只載入你使用的
```

**替代方案（Next.js 13.5+）：**

```js
// next.config.js - 使用 optimizePackageImports
module.exports = {
  experimental: {
    optimizePackageImports: ['lucide-react', '@mui/material']
  }
}

// 然後你可以保持人體工學的桶狀匯入：
import { Check, X, Menu } from 'lucide-react'
// 在建置時自動轉換為直接匯入
```

直接匯入提供 15-70% 更快的開發啟動、28% 更快的建置、40% 更快的冷啟動，以及顯著更快的 HMR。

常見受影響的函式庫：`lucide-react`、`@mui/material`、`@mui/icons-material`、`@tabler/icons-react`、`react-icons`、`@headlessui/react`、`@radix-ui/react-*`、`lodash`、`ramda`、`date-fns`、`rxjs`、`react-use`。

參考資料：[How we optimized package imports in Next.js](https://vercel.com/blog/how-we-optimized-package-imports-in-next-js)
