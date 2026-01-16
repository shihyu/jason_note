---
title: 基於使用者意圖預載
impact: MEDIUM
impactDescription: 減少感知延遲
tags: bundle, 預載, 使用者意圖, hover
---

## 基於使用者意圖預載

在需要之前預載大型打包以減少感知延遲。

**範例（在 hover/focus 時預載）：**

```tsx
function EditorButton({ onClick }: { onClick: () => void }) {
  const preload = () => {
    if (typeof window !== 'undefined') {
      void import('./monaco-editor')
    }
  }

  return (
    <button
      onMouseEnter={preload}
      onFocus={preload}
      onClick={onClick}
    >
      Open Editor
    </button>
  )
}
```

**範例（當功能旗標啟用時預載）：**

```tsx
function FlagsProvider({ children, flags }: Props) {
  useEffect(() => {
    if (flags.editorEnabled && typeof window !== 'undefined') {
      void import('./monaco-editor').then(mod => mod.init())
    }
  }, [flags.editorEnabled])

  return <FlagsContext.Provider value={flags}>
    {children}
  </FlagsContext.Provider>
}
```

`typeof window !== 'undefined'` 檢查防止為 SSR 打包預載的模組，優化伺服器打包大小和建置速度。
