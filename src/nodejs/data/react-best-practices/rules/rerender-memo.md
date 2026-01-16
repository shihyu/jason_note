---
title: 提取為記憶化元件
impact: MEDIUM
impactDescription: 啟用提前返回
tags: rerender, memo, useMemo, 優化
---

## 提取為記憶化元件

將昂貴的工作提取到記憶化元件中，以便在運算前啟用提前返回。

**錯誤（即使在載入中也計算 avatar）：**

```tsx
function Profile({ user, loading }: Props) {
  const avatar = useMemo(() => {
    const id = computeAvatarId(user)
    return <Avatar id={id} />
  }, [user])

  if (loading) return <Skeleton />
  return <div>{avatar}</div>
}
```

**正確（載入中時跳過運算）：**

```tsx
const UserAvatar = memo(function UserAvatar({ user }: { user: User }) {
  const id = useMemo(() => computeAvatarId(user), [user])
  return <Avatar id={id} />
})

function Profile({ user, loading }: Props) {
  if (loading) return <Skeleton />
  return (
    <div>
      <UserAvatar user={user} />
    </div>
  )
}
```

**注意：** 如果您的專案啟用了 [React Compiler](https://react.dev/learn/react-compiler)，使用 `memo()` 和 `useMemo()` 進行手動記憶化是不必要的。編譯器會自動優化重新渲染。
