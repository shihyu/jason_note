---
title: 策略性 Suspense 邊界
impact: HIGH
impactDescription: 更快的首次繪製
tags: async, suspense, 串流, 版面偏移
---

## 策略性 Suspense 邊界

不要在非同步元件中 await 資料後才返回 JSX，而是使用 Suspense 邊界在資料載入時更快地顯示包裝器 UI。

**錯誤（包裝器被資料擷取阻塞）：**

```tsx
async function Page() {
  const data = await fetchData() // 阻塞整個頁面

  return (
    <div>
      <div>Sidebar</div>
      <div>Header</div>
      <div>
        <DataDisplay data={data} />
      </div>
      <div>Footer</div>
    </div>
  )
}
```

即使只有中間部分需要資料，整個版面都在等待。

**正確（包裝器立即顯示，資料串流進來）：**

```tsx
function Page() {
  return (
    <div>
      <div>Sidebar</div>
      <div>Header</div>
      <div>
        <Suspense fallback={<Skeleton />}>
          <DataDisplay />
        </Suspense>
      </div>
      <div>Footer</div>
    </div>
  )
}

async function DataDisplay() {
  const data = await fetchData() // 只阻塞這個元件
  return <div>{data.content}</div>
}
```

Sidebar、Header 和 Footer 立即渲染。只有 DataDisplay 等待資料。

**替代方案（跨元件共享 promise）：**

```tsx
function Page() {
  // 立即啟動擷取，但不 await
  const dataPromise = fetchData()

  return (
    <div>
      <div>Sidebar</div>
      <div>Header</div>
      <Suspense fallback={<Skeleton />}>
        <DataDisplay dataPromise={dataPromise} />
        <DataSummary dataPromise={dataPromise} />
      </Suspense>
      <div>Footer</div>
    </div>
  )
}

function DataDisplay({ dataPromise }: { dataPromise: Promise<Data> }) {
  const data = use(dataPromise) // 解包 promise
  return <div>{data.content}</div>
}

function DataSummary({ dataPromise }: { dataPromise: Promise<Data> }) {
  const data = use(dataPromise) // 重用相同的 promise
  return <div>{data.summary}</div>
}
```

兩個元件共享相同的 promise，所以只發生一次擷取。版面立即渲染，兩個元件一起等待。

**不該使用此模式的情況：**

- 版面決策所需的關鍵資料（影響定位）
- 首屏上方的 SEO 關鍵內容
- 小型、快速的查詢，suspense 開銷不值得
- 當你想避免版面偏移時（載入 → 內容跳動）

**權衡：** 更快的首次繪製 vs 潛在的版面偏移。根據你的 UX 優先順序選擇。
