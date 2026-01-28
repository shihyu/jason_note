---
title: 條件式模組載入
impact: HIGH
impactDescription: 只在需要時載入大型資料
tags: bundle, 條件式載入, 延遲載入
---

## 條件式模組載入

只在功能啟用時載入大型資料或模組。

**範例（延遲載入動畫影格）：**

```tsx
function AnimationPlayer({ enabled }: { enabled: boolean }) {
  const [frames, setFrames] = useState<Frame[] | null>(null)

  useEffect(() => {
    if (enabled && !frames && typeof window !== 'undefined') {
      import('./animation-frames.js')
        .then(mod => setFrames(mod.frames))
        .catch(() => setEnabled(false))
    }
  }, [enabled, frames])

  if (!frames) return <Skeleton />
  return <Canvas frames={frames} />
}
```

`typeof window !== 'undefined'` 檢查防止為 SSR 打包此模組，優化伺服器打包大小和建置速度。
