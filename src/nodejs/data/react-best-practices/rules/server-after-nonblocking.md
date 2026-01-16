---
title: 使用 after() 進行非阻塞操作
impact: MEDIUM
impactDescription: 更快的回應時間
tags: server, async, 日誌, 分析, 副作用
---

## 使用 after() 進行非阻塞操作

使用 Next.js 的 `after()` 來排程在回應發送後執行的工作。這可以防止日誌記錄、分析和其他副作用阻塞回應。

**錯誤（阻塞回應）：**

```tsx
import { logUserAction } from '@/app/utils'

export async function POST(request: Request) {
  // 執行變更
  await updateDatabase(request)

  // 日誌記錄阻塞回應
  const userAgent = request.headers.get('user-agent') || 'unknown'
  await logUserAction({ userAgent })

  return new Response(JSON.stringify({ status: 'success' }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  })
}
```

**正確（非阻塞）：**

```tsx
import { after } from 'next/server'
import { headers, cookies } from 'next/headers'
import { logUserAction } from '@/app/utils'

export async function POST(request: Request) {
  // 執行變更
  await updateDatabase(request)

  // 在回應發送後記錄日誌
  after(async () => {
    const userAgent = (await headers()).get('user-agent') || 'unknown'
    const sessionCookie = (await cookies()).get('session-id')?.value || 'anonymous'

    logUserAction({ sessionCookie, userAgent })
  })

  return new Response(JSON.stringify({ status: 'success' }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  })
}
```

回應會立即發送，而日誌記錄在背景進行。

**常見使用場景：**

- 分析追蹤
- 稽核日誌
- 發送通知
- 快取失效
- 清理任務

**重要注意事項：**

- `after()` 即使回應失敗或重新導向也會執行
- 適用於 Server Actions、Route Handlers 和 Server Components

參考資料：[https://nextjs.org/docs/app/api-reference/functions/after](https://nextjs.org/docs/app/api-reference/functions/after)
