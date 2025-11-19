---
marp: true
theme: default
paginate: true
_paginate: false
header: ''
footer: ''
backgroundColor: white
---

<!-- theme: gaia -->
<!-- _class: lead -->

# 第八講 多處理器調度

## 第一節 對稱多處理與多核架構


<br>
<br>

向勇 陳渝 李國良 

2022年秋季

---

**提綱**

### 1. 多處理機器
2. Cache一致性(Cache Coherence)

---

#### 單核處理器
![w:800](figs/single-core.png) 


---
#### 超線程(Hyperthread, Simultaneous multithreading)處理器
![w:500](figs/hyperthread.png) 


---
#### 多核(multi-core)處理器
![w:1150](figs/multi-core.png) 

---
#### 眾核(many-core)處理器
![w:1150](figs/many-core.png) 

---

**提綱**

1. 多處理機器
### 2. Cache一致性(Cache Coherence)

---

#### 對稱多處理器(SMP)與非一致內存訪問系統(NUMA)
![w:1000](figs/smp-numa.png) 

---
#### Cache 一致性 (Cache Coherence)
![w:800](figs/cache-coherence.png) 


---

#### Cache 一致性問題
![w:900](figs/cache-coherence-problem.png)