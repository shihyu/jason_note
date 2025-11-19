# 1. 多種語言協同構造的 OS

已有工作：

1. TypeKernel：三位六字班同學在2019年OS+編譯專題訓練課上的聯合實驗。用Haskell語言構造了一個用於編寫OS的DSL，將其編譯為C語言子集（C----），並實現了一個基於UEFI的Demo。

參考資料：

1. [Typekernel](http://os.cs.tsinghua.edu.cn/oscourse/OsTrain2019/g6)，[給後來者的話](https://github.com/typekernel/typekernel-doc/blob/master/TO_FOLLOWERS.md)

# 2. 為 rcore 實現更多 Linux 系統調用

主要目標：

* 在 rcore 上擴展 Linux 系統調用支持，以支持更多應用。可以考慮實現或者完善：信號機制、TTY、用戶和群組權限管理、procfs和devfs。

已有工作：

1. 在 OS2019 大實驗中，王潤基和陳嘉傑合作在 rCore 中實現了 Linux ABI，支持運行原生的 Linux 程序（基於 musl libc，不支持 glibc）。目前 rCore 中已經實現了60多個 Linux Syscall（+20多個空實現），支持運行：Busybox, GCC, Nginx, Redis, Rustc 等實際應用。
2. [Biscuit](https://github.com/mit-pdos/biscuit) 是 MIT 用 Golang 編寫的類 Unix OS，[相關論文](https://pdos.csail.mit.edu/papers/biscuit.pdf)發表在 OSDI2018 上。他們實現了58 個 Syscall（不完全兼容Linux），支持運行 Nginx 和 Redis（經過修改，基於他們自己的 libc）。性能測試與 Linux 對比，只慢了 5%-10%。我們嘗試在 rCore 上重複這一工作，但最終由於真機調試過於困難而作罷。 

參考資料：

1. [rCore 對標 Biscuit OS 進行真實應用/網卡的性能測試](http://os.cs.tsinghua.edu.cn/oscourse/OS2019spring/projects/g04)
2. [rCore 畢業論文](http://os.cs.tsinghua.edu.cn/oscourse/OsTrain2019?action=AttachFile&do=view&target=Rust語言操作系統的設計與實現_王潤基畢業論文.pdf)
3. [在 rCore 中實現 epoll](http://os.cs.tsinghua.edu.cn/oscourse/OsTrain2019/g4)
4. [在 rCore 中實現 SystemV 信號量和共享內存](http://os.cs.tsinghua.edu.cn/oscourse/OsTrain2019/g3)
5. [在 rCore 中實現 Framebuffer 運行 mgba](http://os.cs.tsinghua.edu.cn/oscourse/OS2019spring/projects/g02)

# 3. 用 RUST 重寫 zircon（zCore）

主要目標：

* 基於 rCore 現有基礎，用 Rust 重新實現 Zircon 微內核。
* 根據文檔描述，實現相應的內核對象和系統調用，目標是能運行到 shell。
* 在新項目中嘗試新技術、積累經驗，用來重構和改進 rCore。

已有工作：

1. 潘慶霖在 OSTrain2019 大實驗中對 Fuchsia 進行了完整的調研和分析。
2. 隨後王潤基在寒假期間嘗試搭起了 zCore 項目框架，目前已實現了 8 個 syscall 和諸多內核對象，還剩 50 多個。
3. zCore 嘗試的新技術包括：抽象出 HAL 以實現純用戶態開發和測試，應用 async 實現內核任務管理……

參考資料：

1. [Fuchsia 調研項目 wiki](http://os.cs.tsinghua.edu.cn/oscourse/OsTrain2019/g1)，[分析文檔](https://github.com/PanQL/zircon-notes)
2. [zCore 項目倉庫](https://github.com/rcore-os/zCore)
3. [Fuchsia 源碼及官方文檔](https://github.com/PanQL/fuchsia/tree/master/docs)
4. [Fuchsia 中文社區](https://fuchsia-china.com)

PS：

* 此項目是某位助教哥哥的畢設課題，和另一位助教哥哥本學期的個人娛樂項目：）））

# 4. 用 RUST 實現 KVM 功能

主要目標：

* 實現一個簡單的 VMM（虛擬機監控程序）
* 對外提供 Linux KVM 或 [Zircon Hypervisor 接口](https://github.com/PanQL/fuchsia/tree/master/docs/reference/syscalls#hypervisor-guests)
* 嘗試利用 x86 VT-x、RISCV H 擴展或 ARM 相關指令集
* 能夠同時運行多個 rCore

參考資料：

1. [JailHouse：Linux-based Hypervisor](https://github.com/siemens/jailhouse)
2. [RVirt：MIT 用 Rust 寫的 RISCV Hypervisor](https://github.com/siemens/jailhouse)
3. [Linux KVM](https://www.linux-kvm.org/page/Main_Page), [Apple Hypervisor Framework](https://developer.apple.com/documentation/hypervisor)

# 5. RISCV 用戶態中斷

主要目標：

* 利用 RISCV 用戶態中斷機制，改進 OS 以提升 IPC 及 IO 性能。

參考資料：

1. [RISCV 特權級手冊](https://riscv.org/specifications/privileged-isa)

# 6. 重構 rcore 內核組件形成 OS-Kit

主要目標：

* 將 rCore 拆分成獨立可複用的 crates，可組合成多種特定 OS

已有工作：

* 將龐大的 OS 拆分成一個個獨立的模塊，一直是 rCore 開發的指導思想和終極目標。不過現實中工程總是十分 dirty 的，需要不斷地在優雅設計和實際產出中作出妥協。

參考資料：

* [JudgeDuckOS64](https://github.com/wangrunji0408/JudgeDuck-OS-64)：利用 rCore 現有模塊重新實現的[應用程序穩態測試系統（評測鴨）](http://os.cs.tsinghua.edu.cn/oscourse/OS2018spring/projects/g04)

# 7. 為 rcore 適配樹莓派4（ARM64）

主要目標：

* 讓 rCore 支持樹莓派4物理硬件
* 完善與改進已有的樹莓派3驅動(SD卡、音頻、GPU)，或添加新驅動支持(USB、網卡、藍牙)

參考資料：

1. [rCore 的 ARM64 和樹莓派3移植](http://os.cs.tsinghua.edu.cn/oscourse/OsTrain2018/g2)
2. [在 rCore 中支持樹莓派3聲卡](http://os.cs.tsinghua.edu.cn/oscourse/OS2019spring/projects/g08)
3. [在 rCore 中支持樹莓派3 SD卡](http://os.cs.tsinghua.edu.cn/oscourse/OS2019spring/projects/g11)
4. [在 rCore 中移植 VideoCore IV 驅動](http://os.cs.tsinghua.edu.cn/oscourse/OsTrain2019/g2)

# 8. 為 rcore 適配基於 rv64 的物理硬件（如 K210、FPGA+Rocket Chip等）

# 9. 形式化驗證的OS

# 10. 基於 rcore 的網絡路由器

主要目標：

* 完善多網卡支持，實現系統路由表和內置的網絡功能，或者給用戶態提供一個類似PCAP的接口，然後編寫一個軟路由
* （可選）在計網聯合實驗的成果上繼續
* （可選）優化 10G 網卡驅動（ixgbe）的穩定性和性能，並且在 PC 機上運行

參考資料：

1. [FPGA 上運行 RISC-V rCore 構建路由器](http://os.cs.tsinghua.edu.cn/oscourse/OS2019spring/projects/g05)
2. [計網聯合實驗](https://github.com/z4yx/Router-Lab/tree/master/Joint)

# 11. 改進rust語言的async on no-std

# 12. 內核態的rust std實現

# 13. 基於Labeled RISCV的OS kernel支持

參考資料：

1. [為 rCore 適配 PARD / Labeled RISCV](http://os.cs.tsinghua.edu.cn/oscourse/OsTrain2018/g3)

# 14. 在 rcore 中支持 container

# 1. 自由選擇 OS 相關的論文、改進結果

參考資料

# 1. 為 rcore 添加 USB 驅動支持

主要目標：

* 在 rcore 中實現 USB 協議棧
* 支持簡單的 USB 設備，如 USB 鍵盤/鼠標、U 盤讀寫
* 能夠在至少一種真實硬件上演示(樹莓派、PC)

參考資料：

1. [https://github.com/cfgbd/rustos/tree/master/usb](https://github.com/cfgbd/rustos/tree/master/usb)
1. [在 rCore 中移植 USB 驅動的嘗試](http://os.cs.tsinghua.edu.cn/oscourse/OsTrain2018/g2)
