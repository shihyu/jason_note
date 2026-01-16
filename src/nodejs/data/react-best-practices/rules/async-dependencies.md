---
title: 基於依賴的並行化
impact: CRITICAL
impactDescription: 2-10 倍改善
tags: async, 並行化, 依賴, better-all
---

## 基於依賴的並行化

對於有部分依賴的操作，使用 `better-all` 來最大化並行性。它會自動在最早可能的時刻啟動每個任務。

**錯誤（profile 不必要地等待 config）：**

```typescript
const [user, config] = await Promise.all([
  fetchUser(),
  fetchConfig()
])
const profile = await fetchProfile(user.id)
```

**正確（config 和 profile 並行執行）：**

```typescript
import { all } from 'better-all'

const { user, config, profile } = await all({
  async user() { return fetchUser() },
  async config() { return fetchConfig() },
  async profile() {
    return fetchProfile((await this.$.user).id)
  }
})
```

參考資料：[https://github.com/shuding/better-all](https://github.com/shuding/better-all)
