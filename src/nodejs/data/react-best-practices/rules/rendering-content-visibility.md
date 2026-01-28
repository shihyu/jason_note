---
title: 對長列表使用 CSS content-visibility
impact: HIGH
impactDescription: 更快的初始渲染
tags: rendering, css, content-visibility, 長列表
---

## 對長列表使用 CSS content-visibility

套用 `content-visibility: auto` 來延遲螢幕外元素的渲染。

**CSS：**

```css
.message-item {
  content-visibility: auto;
  contain-intrinsic-size: 0 80px;
}
```

**範例：**

```tsx
function MessageList({ messages }: { messages: Message[] }) {
  return (
    <div className="overflow-y-auto h-screen">
      {messages.map(msg => (
        <div key={msg.id} className="message-item">
          <Avatar user={msg.author} />
          <div>{msg.content}</div>
        </div>
      ))}
    </div>
  )
}
```

對於 1000 則訊息，瀏覽器會跳過約 990 個螢幕外項目的佈局/繪製（初始渲染速度提升 10 倍）。
