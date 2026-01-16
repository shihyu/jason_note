---
title: 防止 Hydration 不匹配且不產生閃爍
impact: MEDIUM
impactDescription: 避免視覺閃爍和 hydration 錯誤
tags: rendering, ssr, hydration, localStorage, 閃爍
---

## 防止 Hydration 不匹配且不產生閃爍

當渲染依賴客戶端儲存（localStorage、cookies）的內容時，透過注入同步腳本在 React hydrate 之前更新 DOM，可同時避免 SSR 中斷和 hydration 後的閃爍。

**錯誤（破壞 SSR）：**

```tsx
function ThemeWrapper({ children }: { children: ReactNode }) {
  // localStorage 在伺服器端不可用 - 會拋出錯誤
  const theme = localStorage.getItem('theme') || 'light'

  return (
    <div className={theme}>
      {children}
    </div>
  )
}
```

伺服器端渲染會失敗，因為 `localStorage` 未定義。

**錯誤（視覺閃爍）：**

```tsx
function ThemeWrapper({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState('light')

  useEffect(() => {
    // 在 hydration 後執行 - 導致可見的閃爍
    const stored = localStorage.getItem('theme')
    if (stored) {
      setTheme(stored)
    }
  }, [])

  return (
    <div className={theme}>
      {children}
    </div>
  )
}
```

元件首先使用預設值（`light`）渲染，然後在 hydration 後更新，導致錯誤內容的可見閃爍。

**正確（無閃爍，無 hydration 不匹配）：**

```tsx
function ThemeWrapper({ children }: { children: ReactNode }) {
  return (
    <>
      <div id="theme-wrapper">
        {children}
      </div>
      <script
        dangerouslySetInnerHTML={{
          __html: `
            (function() {
              try {
                var theme = localStorage.getItem('theme') || 'light';
                var el = document.getElementById('theme-wrapper');
                if (el) el.className = theme;
              } catch (e) {}
            })();
          `,
        }}
      />
    </>
  )
}
```

行內腳本在顯示元素之前同步執行，確保 DOM 已經有正確的值。無閃爍，無 hydration 不匹配。

此模式對於主題切換、使用者偏好設定、認證狀態，以及任何應立即渲染而不閃爍預設值的僅客戶端資料特別有用。
