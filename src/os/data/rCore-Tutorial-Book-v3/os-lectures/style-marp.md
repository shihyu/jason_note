##### 向勇使用的風格
```
---
marp: true
theme: default
paginate: true
_paginate: false
header: ''
footer: '向勇：異步編程、Rust語言和異步操作系統'
---
```

#### 分頁

```

---

```

#### 頁碼

```
---
<!-- _paginate: true -->

# Slide 2

## Subtitle

Lorem ipsum dolor sit amet, consectetur adipiscing elit.

---
```

#### 幻燈片頁眉

有了下面這一行後，後面的第一頁都會頁眉了。

```
<!-- header: '1. 異步編程 - 1.1 基本概念和原理'-->
```

#### Annotations in markdown

[Annotations in markdown](https://stackoverflow.com/questions/29853106/annotations-in-markdown)

下面幻燈片中的2和3行是不顯示的。

```
---
# Slide 3

* Item 1
<!--
* item 2
* Item 3 -->
```

#### 插圖

`![width:900px](figs/異步IO模型.png)`