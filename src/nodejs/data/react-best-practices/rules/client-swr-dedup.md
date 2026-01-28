---
title: 使用 SWR 自動去重
impact: MEDIUM-HIGH
impactDescription: 自動請求去重
tags: client, swr, 去重, 資料獲取
---

## 使用 SWR 自動去重

SWR 可在元件實例之間實現請求去重、快取和重新驗證。

**錯誤（無去重，每個實例都會發送請求）：**

```tsx
function UserList() {
  const [users, setUsers] = useState([])
  useEffect(() => {
    fetch('/api/users')
      .then(r => r.json())
      .then(setUsers)
  }, [])
}
```

**正確（多個實例共用一個請求）：**

```tsx
import useSWR from 'swr'

function UserList() {
  const { data: users } = useSWR('/api/users', fetcher)
}
```

**對於不可變資料：**

```tsx
import { useImmutableSWR } from '@/lib/swr'

function StaticContent() {
  const { data } = useImmutableSWR('/api/config', fetcher)
}
```

**對於資料變更操作：**

```tsx
import { useSWRMutation } from 'swr/mutation'

function UpdateButton() {
  const { trigger } = useSWRMutation('/api/user', updateUser)
  return <button onClick={() => trigger()}>更新</button>
}
```

參考資料：[https://swr.vercel.app](https://swr.vercel.app)
