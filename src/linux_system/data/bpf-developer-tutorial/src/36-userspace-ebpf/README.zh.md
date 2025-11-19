# 用戶空間 eBPF 運行時：深度解析與應用實踐

鄭昱笙

本文旨在對用戶空間的 eBPF 運行時和對應的一些應用場景進行剖析和總結。儘管大多數人對基於內核的 eBPF 已有所瞭解，用戶空間 eBPF 的進展和應用實踐同樣引人注目。本文還將探討用戶空間 eBPF 運行時與 Wasm 運行時的技術比較，後者在雲原生和邊緣計算領域已獲得廣泛的關注。我們也新開源了一個用戶態 eBPF 運行時 [bpftime](https://github.com/eunomia-bpf/bpftime)。通過 LLVM `JIT/AOT` 後端支持，我們的基準測試表明 bpftime 是最快的用戶空間 eBPF 運行時之一，同時還可以讓內核中間的 eBPF Uprobe 無縫在用戶空間運行，獲得近十倍的性能提升。

## eBPF：內核的動態擴展運行時與字節碼

### eBPF 究竟是何方神聖？

eBPF，全稱 "extended Berkeley Packet Filter"，是一項允許在不更改內核源代碼或重啟系統的情況下動態干預和修改內核行為的革命性技術。雖然 eBPF 起初是作為網絡數據包過濾工具而設計，但如今已廣泛應用於從性能分析到安全策略等多個方面，逐漸成為系統管理員的得力助手。

eBPF 的前身，Berkeley Packet Filter (BPF) —— 20 世紀 90 年代初的產物，主要用於網絡數據包的高效過濾。儘管 BPF 已被廣大用戶所認可，eBPF 的出現則為其帶來了更為廣泛的指令集，並能直接與內核數據結構互動。自 2014 年 Linux 內核引入 eBPF 以後，它的影響力迅速擴張。Linux 的核心開發團隊不斷地完善 eBPF，使其從一個基礎的網絡數據包過濾器逐漸演變為一個功能強大的字節碼引擎。

### eBPF 對現代計算和網絡的深遠影響

隨著現代計算環境日益複雜，實時數據的採集和深入分析顯得尤為重要。在這一背景下，eBPF 憑藉其卓越的動態性，為開發者和管理員提供了實時干預系統行為的強大工具。eBPF 以其卓越的靈活性在現代網絡解決方案中佔據核心地位。它為流量控制、負載均衡及安全策略在內核級別提供了細緻的控制手段，確保了系統的性能優化和安全穩定。同時，eBPF 在系統可觀察性上也做出了顯著貢獻，為各種系統調用和硬件事件提供了詳細的可編程追蹤方案，促進了問題的迅速定位和解決。

## 用戶空間 eBPF 運行時：eBPF 的新生代

### 什麼是用戶空間 eBPF 運行時？

雖然 eBPF 最初是為內核設計的，但它在用戶空間的巨大潛力，以及內核對於 `GPL LICENSE` 的限制，也催生了用戶空間 eBPF 運行時的產生。這些運行時允許開發者在內核之外利用 eBPF 的能力，提供了一個在內核之外的運行平臺，擴展其實用性和適用性，同時不受限於 GPL LICENSE。雖然 eBPF 的一個突出特點是其在內核空間內執行代碼的能力，提供快速的可觀察性和數據聚合，但在某些情境下，擁有一個用戶空間的替代方案變得非常有價值。這些用戶空間運行時擴展了 eBPF 多功能性的範圍，超越了內核集成，並常常作為特定用例的實驗場地、調試工具或框架。

### 特定運行時簡介

#### **ubpf**

[uBPF](https://github.com/iovisor/ubpf) 是將 eBPF 引入用戶空間的早期嘗試之一。主要作為一個概念證明，它作為 eBPF 解釋器的用戶空間解釋與 x86_64 和 arm64 JIT 的結合。儘管其起源是一個早期原型，uBPF 吸引了注意並被用作高性能網絡項目（如 DPDK 和 Oko）的基礎。它的非 GPL 許可證（Apache）使其適用於各種項目，包括非開源項目。然而，最近，uBPF 正在迎頭趕上內核發展，特別是微軟為其 eBPF Windows 實現做出的貢獻。但是，開發 ubpf 和 rbpf 程序可能需要一個特定的工具鏈，這對於一些用戶可能是一個障礙。ubpf 只有一個有限的哈希 maps 實現，對大多數場景而言可能不夠。另外，ubpf 本身只是一個虛擬機/解釋器，在實際的使用中，依然需要編寫膠水代碼，和其他用戶空間程序進行編譯、鏈接後才能使用。

#### **rbpf**

[rbpf](https://github.com/qmonnet/rbpf) 和 uBPF 非常相似，但重點是使用了 Rust 進行開發，這是一種因其內存安全保證而著稱的語言。創建 rbpf 是由於想要探索 eBPF 和 Rust 的交集。雖然沒有廣泛採納，但 rbpf 的知名用戶包括 Solana 團隊，他們使用它為帶有 eBPF 驅動的智能合約的區塊鏈工具。rbpf 的一個優勢在於其許可證 (MIT)，允許在各種項目中廣泛重用。rbpf 也缺乏 eBPF Maps 支持，並且僅為 x86_64 提供 JIT 支持。同樣，rbpf 也需要編譯和手動嵌入對應的應用程序中才可以使用。

#### **bpftime**

基於 LLVM JIT/AOT 構建的 [bpftime](https://github.com/eunomia-bpf/bpftime) 是專為用戶空間操作設計的一個高性能 eBPF 運行時。它以其快速的 Uprobe 能力和 Syscall 鉤子脫穎而出，尤其是 Uprobe 性能比內核提高了十倍。此外，bpftime 提供編程 syscall 鉤子、共享內存映射和與熟悉的工具鏈（如 libbpf 和 clang）的兼容性。其設計解決了一些內核 eBPF 的限制，並在某些方面超越了像 Wasm 運行時這樣的插件系統。這是使用 Userspace bpftime 的 eBPF 進行 Hook 的一些性能數據，將用戶空間和內核空間進行對比：

| Probe/Tracepoint Types | Kernel (ns)  | Userspace (ns) | Insn Count |
|------------------------|-------------:|---------------:|---------------:|
| Uprobe                 | 3224.172760  | 314.569110     | 4    |
| Uretprobe              | 3996.799580  | 381.270270     | 2    |
| Syscall Tracepoint     | 151.82801    | 232.57691      | 4    |
| Embedding runtime      | Not available |  110.008430   | 4    |

bpftime 可以類似 Kernel 中的 Uprobe 那樣，自動將 eBPF 運行時注入到用戶空間進程中，無需修改用戶空間進程的代碼，也無需進行重啟進程即可使用。對於 ubpf 和 rbpf 而言，它們依然需要手動編寫膠水代碼和其他用戶空間程序進行集成，相對來說限制了它們的使用場景。在某些場景下，bpftime 可能能作為 kernel eBPF 的一種替代方案，它也不依賴於具體內核版本或 Linux 平臺，可以在其他平臺上運行。

## 為什麼用戶空間版本的 eBPF 會吸引如此多的關注？

eBPF，原本因其在內核空間的強大性能而被廣泛認知，但近年來，其在用戶空間的實現也引起了業界的濃厚興趣。以下是技術社區對於 eBPF 遷移到用戶空間的熱切關注的核心原因：

### 性能提升

在內核空間，eBPF 的 Uprobe 組件時常面臨因上下文切換帶來的性能瓶頸。這在延遲敏感的應用中可能導致不良影響，從而對實時監控和數據處理帶來挑戰。但用戶空間版本的 eBPF 能夠繞過與上下文切換有關的性能損失，實現更高的性能優化。例如，`bpftime` 運行時在用戶空間的表現，相較於其內核版本，展現出了顯著的性能增益。

### 靈活性與集成度

用戶空間的 eBPF 運行時帶來了更大的靈活性。與其他解決方案如 Wasm 運行時相比，它們無需手動集成即可提供自動插樁的特性。這意味著開發者可以輕鬆地將其集成進正在運行的進程中，避免了因重新啟動或重新編譯帶來的操作中斷。

### 安全性加固

在內核空間，eBPF 的執行通常需要 root 訪問權限，這可能無意中增加了系統的攻擊面，使其容易受到例如容器逃逸或潛在的內核利用等安全威脅。相反，用戶空間的實現在這種高風險環境之外運作。它們在用戶空間中運行，大大降低了對高權限的依賴，從而減少了潛在的安全風險。

### 調試與許可的便利性

用戶空間 eBPF 的一個顯著優點是，它為開發者提供了更加直觀的調試環境。相對於內核空間中有限的調試手段，用戶空間解釋器提供的斷點調試功能更為方便。此外，用戶空間 eBPF 的許可證更加靈活，通常採用 Apache 或 MIT 這樣的開源許可，這意味著它們可以輕鬆地與各種項目（包括商業項目）相結合，避免了與內核代碼相關的 GPL 限制。

## 使用案例：現有的 eBPF 用戶空間應用

用戶空間 eBPF 正在項目中使用，每個項目都利用 eBPF 的獨特功能來增強它們的功能:

1. [**Oko:**](https://github.com/Orange-OpenSource/Oko)

   Oko 是 Open vSwitch-DPDK 的擴展，提供了與 BPF 程序的運行時擴展。它允許使用 BPF 程序在用戶空間處理數據包，提供靈活的數據包處理，並促進 Open vSwitch 與其他系統的集成。

1. [**DPDK eBPF 支持:**](https://doc.dpdk.org/guides/prog_guide/bpf_lib.html)

   DPDK (數據平面開發套件) eBPF 支持通過允許在用戶空間使用 eBPF 程序來促進快速的數據包處理，這些程序可以加載並運行以分析網絡數據包。這增強了網絡應用的靈活性和可編程性，無需修改內核。

1. [**Solana:**](https://solana.com/)

   Solana 利用 eBPF 實現一個 JIT (即時)編譯器，這對於在其區塊鏈網絡上執行智能合約是至關重要的。使用 eBPF 確保了安全性、性能和架構中立性，從而允許在 Solana 區塊鏈上的驗證器節點上高效地執行智能合約。

1. [**eBPF for Windows (進行中的工作):**](https://github.com/microsoft/ebpf-for-windows)

   該項目旨在將 Linux 生態系統中熟悉的 eBPF 工具鏈和 API 帶到 Windows，允許在 Windows 之上使用現有的 eBPF 工具鏈。這展示了將 eBPF 的功能擴展到 Linux 之外的有前景的嘗試，儘管它仍然是一個進行中的工作。

使用 eBPF 的這些應用的好處包括：

- **靈活性:** eBPF 提供了一個靈活的框架，用於在內核或用戶空間中運行程序，使開發人員能夠擴展現有系統的功能，而無需修改其核心代碼。
- **性能:** 通過允許 JIT 編譯和高效的數據包處理，eBPF 可以顯著提高網絡應用和區塊鏈智能合約執行的性能。
- **安全性和安全性:** eBPF 框架為驗證程序執行前的安全屬性提供了機制，從而確保了其集成的系統的完整性和安全性。
- **跨平臺能力:** eBPF 指令集的架構中立性使得跨平臺兼容性成為可能，如 Solana 項目和進行中的 eBPF for Windows 所示。

這些屬性使 eBPF 成為增強各種應用的強大工具，從網絡處理到區塊鏈智能合約執行，再到更多。還有一些論文討論了在用戶空間中使用 eBPF 的用途：

1. [**RapidPatch: 用於實時嵌入式設備的固件熱修復**](https://www.usenix.org/conference/usenixsecurity22/presentation/he-yi):

   本文介紹了一個名為 RapidPatch 的新的熱修復框架，該框架旨在通過在異構嵌入式設備上安裝通用修復程序來促進修復的傳播，而不會中斷它們上運行的其他任務。此外，RapidPatch 提出了兩種類型的 eBPF 補丁，用於不同類型的漏洞，並開發了一個 eBPF 補丁驗證器以確保補丁安全。

2. [**Femto-Containers: 低功耗 IoT 微控制器上的小型軟件功能的輕量級虛擬化和故障隔離**](https://arxiv.org/abs/2210.03432):

   本文介紹了 Femto-Containers，這是一個新穎的框架，允許在低功耗 IoT 設備上安全地部署、執行和隔離小型虛擬軟件功能。該框架在 RIOT 中實現並提供，RIOT 是一個受歡迎的開源 IoT 操作系統，強調在低功耗 IoT 設備上安全地部署、執行和隔離小型虛擬軟件功能。該論文討論了在一個常見的低功耗 IoT 操作系統 (RIOT) 中集成的 Femto-Container 主機引擎的實現，增強了其在標準的 IPv6/6LoWPAN 網絡上按需啟動、更新或終止 Femto-Containers 的能力。

這些論文深入探討了固件補丁和輕量級虛擬化方面的相關進展，展示了針對實時嵌入式系統和低功耗 IoT 微控制器領域的關鍵挑戰的創新。

## 用戶空間 eBPF 運行時 vs Wasm 運行時

在不斷發展的雲原生和邊緣計算領域中，eBPF (擴展的伯克利數據包過濾器) 和 Wasm (WebAssembly) 都已成為強大的工具。但它們都有自己的設計原則和權衡取捨。

## eBPF 在用戶空間運行時 vs Wasm 運行時：雲原生計算的新紀元

在飛速進展的雲原生與邊緣計算生態中，eBPF (擴展的伯克利數據包過濾器) 和 Wasm (WebAssembly) 被廣泛認為是兩大技術巨頭。這兩者雖然都非常強大，但各有其獨特的設計哲學與優缺點。

### eBPF 與 Wasm 之間的技術差異

**eBPF**:

- **核心理念**：eBPF 是為了滿足高性能要求而設計的，特別是針對實時內核交互和高吞吐量的網絡任務。
- **安全性**：儘管eBPF的主要焦點是性能，但其驗證器機制確保了執行的程序在不引發內核恐慌或無限循環的前提下的安全性。

**Wasm**:

- **核心理念**：Wasm 誕生於網絡環境，其設計重點在於可移植性和執行安全性，旨在實現接近本地機器代碼的執行速度。
- **安全性**：Wasm 的安全策略主要基於軟件故障隔離 (SFI)。沙盒執行確保了代碼的安全性，但這可能會帶來某些運行時的額外開銷。

這兩種技術都依賴於底層的庫來執行復雜任務，如 Wasm 所依賴的 `Wasi-nn` 來進行神經網絡處理。與這些外部API 交互時，特別是在 Wasm 的環境下，需要進行更多的驗證和運行時檢查，這可能導致額外的性能損耗。而eBPF則提供了一個更為性能中心化的策略，其驗證器確保了代碼在主機上的安全執行，而不需要運行時的額外開銷。

在語言支持上，由於 eBPF 的專業特性，其語言選擇較為有限，通常是 C 和 Rust。而Wasm則支持更多的編程語言，包括但不限於 C、C++、Rust、Go、Python、Java和C#。這使得Wasm在跨平臺部署上有更大的靈活性，但也可能因為不恰當的語言選擇引入更多的性能開銷。

為了給大家提供一個直觀的對比，我們在 [https://github.com/eunomia-bpf/bpf-benchmark](https://github.com/eunomia-bpf/bpf-benchmark)中展示了eBPF和Wasm運行時的性能比較。

從更宏觀的角度看，eBPF運行時和Wasm實際上可以被視為是相互補充的。儘管 eBPF 擁有出色的驗證器機制來確保運行時安全性，但由於其編程語言的侷限性和相對較高的開發難度，它並不總是適合作為業務邏輯的首選運行時。反之，eBPF 更適用於像網絡流量轉發、可觀測性和 livepatch 這樣的高專業性任務。相對而言，Wasm 運行時可以作為 Serverless 的運行時平臺、插件系統和輕量級虛擬化等場景的首選。這兩者都有自己的優勢，但它們的選擇取決於特定的用例和優先級。

## bpftime 快速入門

使用`bpftime`，您可以使用熟悉的工具（如clang和libbpf）構建eBPF應用程序，並在用戶空間中執行它們。例如，`malloc` eBPF程序使用uprobe跟蹤malloc調用，並使用哈希映射對其進行統計。

您可以參考[documents/build-and-test.md](https://eunomia.dev/bpftime/documents/build-and-test)上的構建項目的方法，或者使用來自[GitHub packages](https://github.com/eunomia-bpf/bpftime/pkgs/container/bpftime)的容器映像。

要開始，請構建並運行一個基於libbpf的eBPF程序，使用以下命令行：

```console
make -C example/malloc # 構建示例的eBPF程序
bpftime load ./example/malloc/malloc
```

在另一個shell中，運行帶有eBPF的目標程序：

```console
$ bpftime start ./example/malloc/victim
Hello malloc!
malloc called from pid 250215
continue malloc...
malloc called from pid 250215
```

您還可以動態地將eBPF程序附加到正在運行的進程上：

```console
$ ./example/malloc/victim & echo $! # 進程ID為101771
[1] 101771
101771
continue malloc...
continue malloc...
```

然後附加到該進程：

```console
$ sudo bpftime attach 101771 # 您可能需要以root身份運行make install
Inject: "/root/.bpftime/libbpftime-agent.so"
成功注入。ID: 1
```

您可以看到原始程序的輸出：

```console
$ bpftime load ./example/malloc/malloc
...
12:44:35 
        pid=247299      malloc calls: 10
        pid=247322      malloc calls: 10
```

或者，您也可以直接在內核eBPF中運行我們的示例eBPF程序，以查看類似的輸出：

```console
$ sudo example/malloc/malloc
15:38:05
        pid=30415       malloc calls: 1079
        pid=30393       malloc calls: 203
        pid=29882       malloc calls: 1076
        pid=34809       malloc calls: 8
```

有關更多詳細信息，請參閱[documents/usage.md](https://eunomia.dev/bpftime/documents/usage)。

## 總結與前景

用戶空間的eBPF運行時正在打破邊界，將eBPF的能力從內核擴展到了更廣闊的領域。這種擴展帶來了顯著的性能、靈活性和安全性提升。例如，`bpftime`運行時顯示了其在某些低級性能場景下，甚至超越了像 Wasm 這樣的其他技術。也有越來越多的應用將用戶空間的 eBPF 用於快速補丁、輕量級虛擬化、網絡過濾等場景。

Wasm 的主要焦點在於可移植性、輕量級虛擬化、安全性、多語言等等，而 eBPF 則針對那些對性能有嚴格要求的基礎設施任務提供了更多的性能優勢和動態插樁特性。選擇哪種技術取決於特定的需求和優先級。隨著它們的進一步發展，用戶空間的eBPF運行時正在成為雲原生技術堆棧中的重要部分，為業界帶來前所未有的安全、效率和創新的組合。

> 我們誠邀您深入探索用戶空間eBPF的世界，您可以從我們的項目 [https://github.com/eunomia-bpf/bpftime](https://github.com/eunomia-bpf/bpftime) 開始。您的貢獻、反饋或僅僅是對此工具的使用和 star，都可以為我們的社區帶來巨大價值。
>
> 若您在研究中採用了我們的`bpftime`項目，請[引用我們的倉庫](https://github.com/eunomia-bpf/bpftime/blob/master/CITATION.cff)。我們期待您的寶貴意見和反饋，您可以通過 GitHub 倉庫的 issue、郵箱 [yunwei356@gmail.com](mailto:yunwei356@gmail.com) 或微信 yunwei2567 與我們聯繫。

## 參考資料

1. bpftime: <https://github.com/eunomia-bpf/bpftime>
2. ubpf: <https://github.com/iovisor/ubpf>
3. rbpf: <https://github.com/qmonnet/rbpf>
4. Oko: <https://github.com/Orange-OpenSource/Oko>
5. RapidPatch: Firmware Hotpatching for Real-Time Embedded Devices: <https://www.usenix.org/conference/usenixsecurity22/presentation/he-yi>
6. DPDK eBPF Support: <https://doc.dpdk.org/guides/prog_guide/bpf_lib.html>
7. Solana: <https://solana.com/>
8. eBPF for Windows (Work-In-Progress): <https://github.com/microsoft/ebpf-for-windows>
9. Femto-Containers: Lightweight Virtualization and Fault Isolation For Small Software Functions on Low-Power IoT Microcontrollers: <https://arxiv.org/abs/2210.03432>
