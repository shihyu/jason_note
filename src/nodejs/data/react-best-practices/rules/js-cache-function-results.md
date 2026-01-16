---
title: 快取重複的函數呼叫結果
impact: MEDIUM
impactDescription: 避免冗餘運算
tags: javascript, 快取, 記憶化, 效能
---

## 快取重複的函數呼叫結果

當同一個函數在渲染過程中使用相同的輸入被重複呼叫時，使用模組層級的 Map 來快取函數結果。

**錯誤（冗餘運算）：**

```typescript
function ProjectList({ projects }: { projects: Project[] }) {
  return (
    <div>
      {projects.map(project => {
        // slugify() 對相同的專案名稱被呼叫 100 次以上
        const slug = slugify(project.name)

        return <ProjectCard key={project.id} slug={slug} />
      })}
    </div>
  )
}
```

**正確（快取結果）：**

```typescript
// 模組層級快取
const slugifyCache = new Map<string, string>()

function cachedSlugify(text: string): string {
  if (slugifyCache.has(text)) {
    return slugifyCache.get(text)!
  }
  const result = slugify(text)
  slugifyCache.set(text, result)
  return result
}

function ProjectList({ projects }: { projects: Project[] }) {
  return (
    <div>
      {projects.map(project => {
        // 每個唯一的專案名稱只計算一次
        const slug = cachedSlugify(project.name)

        return <ProjectCard key={project.id} slug={slug} />
      })}
    </div>
  )
}
```

**單一值函數的簡化模式：**

```typescript
let isLoggedInCache: boolean | null = null

function isLoggedIn(): boolean {
  if (isLoggedInCache !== null) {
    return isLoggedInCache
  }

  isLoggedInCache = document.cookie.includes('auth=')
  return isLoggedInCache
}

// 當認證狀態改變時清除快取
function onAuthChange() {
  isLoggedInCache = null
}
```

使用 Map（而非 hook），這樣它可以在任何地方運作：工具函數、事件處理器，不只是 React 元件。

參考資料：[How we made the Vercel Dashboard twice as fast](https://vercel.com/blog/how-we-made-the-vercel-dashboard-twice-as-fast)
