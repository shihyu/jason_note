---
title: 優化 SVG 精度
impact: LOW
impactDescription: 減少檔案大小
tags: rendering, svg, 優化, svgo
---

## 優化 SVG 精度

降低 SVG 座標精度以減少檔案大小。最佳精度取決於 viewBox 大小，但通常應考慮降低精度。

**錯誤（過度精確）：**

```svg
<path d="M 10.293847 20.847362 L 30.938472 40.192837" />
```

**正確（1 位小數）：**

```svg
<path d="M 10.3 20.8 L 30.9 40.2" />
```

**使用 SVGO 自動化：**

```bash
npx svgo --precision=1 --multipass icon.svg
```
