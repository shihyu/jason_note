# 更多的參考資料：論文、項目等等

可以在這裡找到更多關於 eBPF 的信息：

- 一個關於 eBPF 相關內容和信息的詳細列表：<https://github.com/zoidbergwill/awesome-ebpf>
- eBPF 相關項目、教程：<https://ebpf.io/>

這是我近年來讀過的與 eBPF 相關的論文列表，可能對於對 eBPF 相關研究感興趣的人有所幫助。

eBPF（擴展的伯克利數據包過濾器）是一種新興的技術，允許在 Linux 內核中安全地執行用戶提供的程序。近年來，它因加速網絡處理、增強可觀察性和實現可編程數據包處理而得到了廣泛的應用。此文檔列出了過去幾年關於 eBPF 的一些關鍵研究論文。這些論文涵蓋了 eBPF 的幾個方面，包括加速分佈式系統、存儲和網絡，正式驗證 eBPF 的 JIT 編譯器和驗證器，將 eBPF 用於入侵檢測，以及從 eBPF 程序自動生成硬件設計。

一些關鍵亮點：

- eBPF 允許在內核中執行自定義函數，以加速分佈式協議、存儲引擎和網絡應用，與傳統的用戶空間實現相比，可以提高吞吐量和降低延遲。
- eBPF 組件（如 JIT 和驗證器）的正式驗證確保了正確性，並揭示了實際實現中的錯誤。
- eBPF 的可編程性和效率使其適合在內核中完全構建入侵檢測和網絡監控應用。
- 從 eBPF 程序中自動生成硬件設計允許軟件開發人員快速生成網絡卡中的優化數據包處理管道。

這些論文展示了 eBPF 在加速系統、增強安全性和簡化網絡編程方面的多功能性。隨著 eBPF 的採用不斷增加，它是一個與性能、安全性、硬件集成和易用性相關的系統研究的重要領域。

如果您有任何建議或添加論文的意見，請隨時開放一個問題或PR。此列表創建於 2023.10，未來將添加新的論文。

> 如果您對 eBPF 有些進一步的興趣的話，也可以查看我們在 [eunomia-bpf](https://github.com/eunomia-bpf) 的開源項目和 [bpf-developer-tutorial](https://github.com/eunomia-bpf/bpf-developer-tutorial) 的 eBPF 教程。我也在尋找 2024/2025 年系統和網絡領域的 PhD 相關機會，這是我的 [Github](https://github.com/yunwei37) 和 [郵箱](mailto:yunwei356@gmail.com)。

## XRP: In-Kernel Storage Functions with eBPF

隨著微秒級 NVMe 存儲設備的出現，Linux 內核存儲堆棧開銷變得顯著，幾乎使訪問時間翻倍。我們介紹了 XRP，一個框架，允許應用程序從 eBPF 在 NVMe 驅動程序中的鉤子執行用戶定義的存儲功能，如索引查找或聚合，安全地繞過大部分內核的存儲堆棧。為了保持文件系統的語義，XRP 將少量的內核狀態傳播到其 NVMe 驅動程序鉤子，在那裡調用用戶註冊的 eBPF 函數。我們展示瞭如何利用 XRP 顯著提高兩個鍵值存儲，BPF-KV，一個簡單的 B+ 樹鍵值存儲，和 WiredTiger，一個流行的日誌結構合併樹存儲引擎的吞吐量和延遲。

OSDI '22 最佳論文: <https://www.usenix.org/conference/osdi22/presentation/zhong>

## Specification and verification in the field: Applying formal methods to BPF just-in-time compilers in the Linux kernel

本文描述了我們將形式方法應用於 Linux 內核中的一個關鍵組件，即 Berkeley 數據包過濾器 (BPF) 虛擬機的即時編譯器 ("JIT") 的經驗。我們使用 Jitterbug 驗證這些 JIT，這是第一個提供 JIT 正確性的精確規範的框架，能夠排除實際錯誤，並提供一個自動化的證明策略，該策略可以擴展到實際實現。使用 Jitterbug，我們設計、實施並驗證了一個新的針對 32 位 RISC-V 的 BPF JIT，在五個其他部署的 JIT 中找到並修復了 16 個之前未知的錯誤，並開發了新的 JIT 優化；所有這些更改都已上傳到 Linux 內核。結果表明，在一個大型的、未經驗證的系統中，通過仔細設計規範和證明策略，可以構建一個經過驗證的組件。

OSDI 20: <https://www.usenix.org/conference/osdi20/presentation/nelson>

## λ-IO: A Unified IO Stack for Computational Storage

新興的計算存儲設備為存儲內計算提供了一個機會。它減少了主機與設備之間的數據移動開銷，從而加速了數據密集型應用程序。在這篇文章中，我們介紹 λ-IO，一個統一的 IO 堆棧，跨主機和設備管理計算和存儲資源。我們提出了一套設計 - 接口、運行時和調度 - 來解決三個關鍵問題。我們在全堆棧軟件和硬件環境中實施了 λ-IO，並使用合成和實際應用程序對其

進行評估，與 Linux IO 相比，顯示出高達 5.12 倍的性能提升。

FAST23: <https://www.usenix.org/conference/fast23/presentation/yang-zhe>

## Extension Framework for File Systems in User space

用戶文件系統相對於其內核實現提供了許多優勢，例如開發的簡易性和更好的系統可靠性。然而，它們會導致重大的性能損失。我們觀察到現有的用戶文件系統框架非常通用；它們由一個位於內核中的最小干預層組成，該層簡單地將所有低級請求轉發到用戶空間。雖然這種設計提供了靈活性，但由於頻繁的內核-用戶上下文切換，它也嚴重降低了性能。

這項工作介紹了 ExtFUSE，一個用於開發可擴展用戶文件系統的框架，該框架還允許應用程序在內核中註冊"薄"的專用請求處理程序，以滿足其特定的操作需求，同時在用戶空間中保留複雜的功能。我們使用兩個 FUSE 文件系統對 ExtFUSE 進行評估，結果表明 ExtFUSE 可以通過平均不到幾百行的改動來提高用戶文件系統的性能。ExtFUSE 可在 GitHub 上找到。

ATC 19: <https://www.usenix.org/conference/atc19/presentation/bijlani>

## Electrode: Accelerating Distributed Protocols with eBPF

在標準的Linux內核網絡棧下實現分佈式協議可以享受到負載感知的CPU縮放、高兼容性以及強大的安全性和隔離性。但由於過多的用戶-內核切換和內核網絡棧遍歷，其性能較低。我們介紹了Electrode，這是一套為分佈式協議設計的基於eBPF的性能優化。這些優化在網絡棧之前在內核中執行，但實現了與用戶空間中實現的相似功能（例如，消息廣播，收集ack的仲裁），從而避免了用戶-內核切換和內核網絡棧遍歷所帶來的開銷。我們展示，當應用於經典的Multi-Paxos狀態機複製協議時，Electrode可以提高其吞吐量高達128.4%，並將延遲降低高達41.7%。

NSDI 23: [鏈接](https://www.usenix.org/conference/nsdi23/presentation/zhou)

## BMC: Accelerating Memcached using Safe In-kernel Caching and Pre-stack Processing

內存鍵值存儲是幫助擴展大型互聯網服務的關鍵組件，通過提供對流行數據的低延遲訪問。Memcached是最受歡迎的鍵值存儲之一，由於Linux網絡棧固有的性能限制，當使用高速網絡接口時，其性能不高。雖然可以使用DPDK基礎方案繞過Linux網絡棧，但這種方法需要對軟件棧進行完全重新設計，而且在客戶端負載較低時也會導致高CPU利用率。

為了克服這些限制，我們提出了BMC，這是一個為Memcached設計的內核緩存，可以在執行標準網絡棧之前服務於請求。對BMC緩存的請求被視為NIC中斷的一部分，這允許性能隨著為NIC隊列服務的核心數量而擴展。為確保安全，BMC使用eBPF實現。儘管eBPF具有安全約束，但我們展示了實現複雜緩存服務是可能的。因為BMC在商用硬件上運行，並且不需要修改Linux內核或Memcached應用程序，所以它可以在現有系統上廣泛部署。BMC優化了Facebook樣式的小型請求的處理時間。在這個目標工作負載上，我們的評估顯示，與原始的Memcached應用程序相比，BMC的吞吐量提高了高達18倍，與使用SO_REUSEPORT套接字標誌的優化版Memcached相比，提高了高達6倍。此外，我們的結果還顯示，對於非目標工作負載，BMC的開銷可以忽略不計，並且不會降低吞吐量。

NSDI 21: [鏈接](https://www.usenix.org/conference/nsdi21/presentation/ghigoff)

## hXDP: Efficient Software Packet Processing on FPGA NICs

FPGA加速器在NIC上使得從CPU卸載昂貴的數據包處理任務成為可能。但是，FPGA有限的資源可能需要在多個應用程序之間共享，而編程它們則很困難。

我們提出了一種在FPGA上運行Linux的eXpress Data Path程序的解決方案，這些程序使用eBPF編寫，僅使用可用硬件資源的一部分，同時匹配高端CPU的性能。eBPF的迭代執行模型不適合FPGA加速器。儘管如此，我們展示了，當針對一個特定的FPGA執行器時，一個eBPF程序的許多指令可以被壓縮、並行化或完全刪除，從而顯著提高性能。我們利用這一點設計了hXDP，它包括(i)一個優化編譯器，該編譯器並行化並將eBPF字節碼轉換為我們定義的擴展eBPF指令集架構；(ii)一個在FPGA上執行這些指令的軟處理器；以及(iii)一個基於FPGA的基礎設施，提供XDP的maps和Linux內核中定義的helper函數。

我們在FPGA NIC上實現了hXDP，並評估了其運行真實世界的未經修改的eBPF程序的性能。我們的實現以156.25MHz的速度時鐘，使用約15%的FPGA資源，並可以運行動態加載的程序。儘管有這些適度的要求，但它達到了高端CPU核心的數據包處理吞吐量，並提供了10倍低的數據包轉發延遲。

OSDI 20: [鏈接](https://www.usenix.org/conference/osdi20/presentation/brunella)

## Network-Centric Distributed Tracing with DeepFlow: Troubleshooting Your Microservices in Zero Code

微服務正變得越來越複雜，給傳統的性能監控解決方案帶來了新的挑戰。一方面，微服務的快速演變給現有的分佈式跟蹤框架的使用和維護帶來了巨大的負擔。另一方面，複雜的基礎設施增加了網絡性能問題的概率，並在網絡側創造了更多的盲點。在這篇論文中，我們介紹了 DeepFlow，一個用於微服務故障排除的以網絡為中心的分佈式跟蹤框架。DeepFlow 通過一個以網絡為中心的跟蹤平面和隱式的上下文傳播提供開箱即用的跟蹤。此外，它消除了網絡基礎設施中的盲點，以低成本方式捕獲網絡指標，並增強了不同組件和層之間的關聯性。我們從分析和實證上證明，DeepFlow 能夠準確地定位微服務性能異常，而開銷幾乎可以忽略不計。DeepFlow 已經為超過26家公司發現了71多個關鍵性能異常，並已被數百名開發人員所使用。我們的生產評估顯示，DeepFlow 能夠為用戶節省數小時的儀表化工作，並將故障排除時間從數小時縮短到幾分鐘。

SIGCOMM 23: <https://dl.acm.org/doi/10.1145/3603269.3604823>

## Fast In-kernel Traffic Sketching in eBPF

擴展的伯克利數據包過濾器（eBPF）是一個基礎設施，允許在不重新編譯的情況下動態加載並直接在 Linux 內核中運行微程序。

在這項工作中，我們研究如何在 eBPF 中開發高性能的網絡測量。我們以繪圖為案例研究，因為它們具有支持廣泛任務的能力，同時提供低內存佔用和準確性保證。我們實現了 NitroSketch，一個用於用戶空間網絡的最先進的繪圖，並表明用戶空間網絡的最佳實踐不能直接應用於 eBPF，因為它的性能特點不同。通過應用我們學到的經驗教訓，我們將其性能提高了40%，與初級實現相比。

SIGCOMM 23: <https://dl.acm.org/doi/abs/10.1145/3594255.3594256>

## SPRIGHT: extracting the server from serverless computing! high-performance eBPF-based event-driven, shared-memory processing

無服務器計算在雲環境中承諾提供高效、低成本的計算能力。然而，現有的解決方案，如Knative這樣的開源平臺，包含了繁重的組件，破壞了無服務器計算的目標。此外，這種無服務器平臺缺乏數據平面優化，無法實現高效的、高性能的功能鏈，這也是流行的微服務開發範式的設施。它們為構建功能鏈使用的不必要的複雜和重複的功能嚴重降低了性能。"冷啟動"延遲是另一個威懾因素。

我們描述了 SPRIGHT，一個輕量級、高性能、響應式的無服務器框架。SPRIGHT 利用共享內存處理顯著提高了數據平面的可伸縮性，通過避免不必要的協議處理和序列化-反序列化開銷。SPRIGHT 大量利用擴展的伯克利數據包過濾器 (eBPF) 進行事件驅動處理。我們創造性地使用 eBPF 的套接字消息機制支持共享內存處理，其開銷嚴格與負載成正比。與常駐、基於輪詢的DPDK相比，SPRIGHT 在真實工作負載下實現了相同的數據平面性能，但 CPU 使用率降低了10倍。此外，eBPF 為 SPRIGHT 帶來了好處，替換了繁重的無服務器組件，使我們能夠以微不足道的代價保持函數處於"暖"狀態。

我們的初步實驗結果顯示，與 Knative 相比，SPRIGHT 在吞吐量和延遲方面實現了一個數量級的提高，同時大大減少了 CPU 使用，並消除了 "冷啟動"的需要。

<https://dl.acm.org/doi/10.1145/3544216.3544259>

## Kgent: Kernel Extensions Large Language Model Agent

修改和擴展操作系統的能力是提高系統安全性、可靠性和性能的重要功能。擴展的伯克利數據包過濾器（eBPF）生態系統已經成為擴展Linux內核的標準機制，並且最近已被移植到Windows。eBPF程序將新邏輯注入內核，使系統在現有邏輯之前或之後執行這些邏輯。雖然eBPF生態系統提供了一種靈活的內核擴展機制，但目前開發人員編寫eBPF程序仍然困難。eBPF開發人員必須深入瞭解操作系統的內部結構，以確定在何處放置邏輯，並應對eBPF驗證器對其eBPF程序的控制流和數據訪問施加的編程限制。本文介紹了KEN，一種通過允許使用自然語言編寫內核擴展來緩解編寫eBPF程序難度的替代框架。KEN利用大語言模型（LLMs）的最新進展，根據用戶的英文提示生成eBPF程序。為了確保LLM的輸出在語義上等同於用戶的提示，KEN結合了LLM增強的程序理解、符號執行和一系列反饋循環。KEN的關鍵創新在於這些技術的結合。特別是，該系統以一種新穎的結構使用符號執行，使其能夠結合程序綜合和程序理解的結果，並建立在LLMs在每個任務中單獨展示的成功基礎上。為了評估KEN，我們開發了一個新的自然語言提示eBPF程序的語料庫。我們顯示，KEN在80%的情況下生成了正確的eBPF程序，這比LLM增強的程序綜合基線提高了2.67倍。

eBPF'24: <https://dl.acm.org/doi/10.1145/3672197.3673434> 和arxiv <https://arxiv.org/abs/2312.05531>

## Programmable System Call Security with eBPF

利用 eBPF 進行可編程的系統調用安全

系統調用過濾是一種廣泛用於保護共享的 OS 內核免受不受信任的用戶應用程序威脅的安全機制。但是，現有的系統調用過濾技術要麼由於用戶空間代理帶來的上下文切換開銷過於昂貴，要麼缺乏足夠的可編程性來表達高級策略。Seccomp 是 Linux 的系統調用過濾模塊，廣泛用於現代的容器技術、移動應用和系統管理服務。儘管採用了經典的 BPF 語言（cBPF），但 Seccomp 中的安全策略主要限於靜態的允許列表，主要是因為 cBPF 不支持有狀態的策略。因此，許多關鍵的安全功能無法準確地表達，和/或需要修改內核。

在這篇論文中，我們介紹了一個可編程的系統調用過濾機制，它通過利用擴展的 BPF 語言（eBPF）使得更高級的安全策略得以表達。更具體地說，我們創建了一個新的 Seccomp eBPF 程序類型，暴露、修改或創建新的 eBPF 助手函數來安全地管理過濾狀態、訪問內核和用戶狀態，以及利用同步原語。重要的是，我們的系統與現有的內核特權和能力機制集成，使非特權用戶能夠安全地安裝高級過濾器。我們的評估表明，我們基於 eBPF 的過濾可以增強現有策略（例如，通過時間專化，減少早期執行階段的攻擊面積高達55.4％）、緩解實際漏洞並加速過濾器。

<https://arxiv.org/abs/2302.10366>

## Cross Container Attacks: The Bewildered eBPF on Clouds

在雲上困惑的 eBPF 之間的容器攻擊

擴展的伯克利數據包過濾器（eBPF）為用戶空間程序提供了強大而靈活的內核接口，通過在內核空間直接運行字節碼來擴展內核功能。它已被雲服務廣泛使用，以增強容器安全性、網絡管理和系統可觀察性。然而，我們發現在 Linux 主機上廣泛討論的攻擊性 eBPF 可以為容器帶來新的攻擊面。通過 eBPF 的追蹤特性，攻擊者可以破壞容器的隔離並攻擊主機，例如，竊取敏感數據、進行 DoS 攻擊，甚至逃逸容器。在這篇論文中，我們研究基於 eBPF 的跨容器攻擊，並揭示其在實際服務中的安全影響。利用 eBPF 攻擊，我們成功地妨害了五個在線的 Jupyter/交互式 Shell 服務和 Google Cloud Platform 的 Cloud Shell。此外，我們發現三家領先的雲供應商提供的 Kubernetes 服務在攻擊者通過 eBPF 逃逸容器後可以被利用來發起跨節點攻擊。具體來說，在阿里巴巴的 Kubernetes 服務中，攻擊者可以通過濫用他們過度特權的雲指標或管理 Pods 來妨害整個集群。不幸的是，容器上的 eBPF 攻擊鮮為人知，並且現有的入侵檢測系統幾乎無法發現它們。此外，現有的 eBPF 權限模型無法限制 eBPF 並確保在共享內核的容器環境中安全使用。為此，我們提出了一個新的 eBPF 權限模型，以對抗容器中的 eBPF 攻擊。

<https://www.usenix.org/conference/usenixsecurity23/presentation/he>

## Comparing Security in eBPF and WebAssembly

比較 eBPF 和 WebAssembly 中的安全性

本文研究了 eBPF 和 WebAssembly（Wasm）的安全性，這兩種技術近年來得到了廣泛的採用，儘管它們是為非常不同的用途和環境而設計的。當 eBPF 主要用於 Linux 等操作系統內核時，Wasm 是一個為基於堆棧的虛擬機設計的二進制指令格式，其用途超出了 web。鑑於 eBPF 的增長和不斷擴大的雄心，Wasm 可能提供有啟發性的見解，因為它圍繞在如 web 瀏覽器和雲等複雜和敵對環境中安全執行任意不受信任的程序進行設計。我們分析了兩種技術的安全目標、社區發展、內存模型和執行模型，並進行了比較安全性評估，探討了內存安全性、控制流完整性、API 訪問和旁路通道。我們的結果表明，eBPF 有一個首先關注性能、其次關注安全的歷史，而 Wasm 更強調安全，儘管要支付一些運行時開銷。考慮 eBPF 的基於語言的限制和一個用於 API 訪問的安全模型是未來工作的有益方向。

<https://dl.acm.org/doi/abs/10.1145/3609021.3609306>

更多內容可以在第一個 eBPF 研討會中找到：<https://conferences.sigcomm.org/sigcomm/2023/workshop-ebpf.html>

## A flow-based IDS using Machine Learning in eBPF

基於eBPF中的機器學習的流式入侵檢測系統

eBPF 是一種新技術，允許動態加載代碼片段到 Linux 內核中。它可以大大加速網絡，因為它使內核能夠處理某些數據包而無需用戶空間程序的參與。到目前為止，eBPF 主要用於簡單的數據包過濾應用，如防火牆或拒絕服務保護。我們證明在 eBPF 中完全基於機器學習開發流式網絡入侵檢測系統是可行的。我們的解決方案使用決策樹，併為每個數據包決定它是否惡意，考慮到網絡流的整個先前上下文。與作為用戶空間程序實現的同一解決方案相比，我們實現了超過 20% 的性能提升。

<https://arxiv.org/abs/2102.09980>

## Femto-containers: lightweight virtualization and fault isolation for small software functions on low-power IoT microcontrollers

針對低功耗 IoT 微控制器上的小型軟件功能的輕量級虛擬化和故障隔離： Femto-容器

低功耗的 IoT 微控制器上運行的操作系統運行時通常提供基礎的 API、基本的連接性和（有時）一個（安全的）固件更新機制。相比之下，在硬件約束較少的場合，網絡化軟件已進入無服務器、微服務和敏捷的時代。考慮到彌合這一差距，我們在論文中設計了 Femto-容器，這是一種新的中間件運行時，可以嵌入到各種低功耗 IoT 設備中。Femto-容器使得可以在低功耗 IoT 設備上通過網絡安全地部署、執行和隔離小型虛擬軟件功能。我們實施了 Femto-容器，並在 RIOT 中提供了集成，這是一個受歡迎的開源 IoT 操作系統。然後，我們評估了我們的實現性能，它已被正式驗證用於故障隔離，確保 RIOT 受到加載並在 Femto-容器中執行的邏輯的保護。我們在各種受歡迎的微控制器架構（Arm Cortex-M、ESP32 和 RISC-V）上的實驗表明，Femto-容器在內存佔用開銷、能源消耗和安全性方面提供了有吸引力的權衡。

<https://dl.acm.org/doi/abs/10.1145/3528535.3565242>
