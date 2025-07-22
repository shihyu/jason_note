# ChCore

>  This is the repository of ChCore labs in SE3357, 2023 Spring.

## 課程/Lab相關情況說明

- 評分規則：課程平時分佔15%，六個Lab佔45%，期末考試佔40%
- 課上無點名，但是夏老師、海波老師、糜澤羽老師講得都非常好，不來絕對是你的損失(doge)
- Chcore Lab非常硬核，主要內容是編寫採用微內核架構的Chcore OS相關代碼，會讓你深入操作系統內核，編碼實現從啟動內核，到虛擬/物理地址管理、進程線程創建、異常處理、多核多進程調度、IPC機制、文件系統、Shell終端、設備驅動等多個模塊。**相信如果Lab從頭到尾都是你自己做的話，你對操作系統內核的設計思路以及工作機制的認識將會有極大的提升！**
- Chcore Lab是一個很好的Lab，希望學弟學妹珍惜這次學習的機會，**儘量自己寫，拒絕做Copycat**，以後就沒有這樣好的機會了哇！



## 文檔目錄說明

- [/ans](./ans)：各個Lab實現的說明文檔，包含思考題的回答以及實踐題的實現思路
- [/doc](./doc)：各個Lab的作業要求文檔
- [/hw](./hw)：老師佈置的兩次作業（虛擬化部分沒有Lab，本學期用作業的形式代替）
- [/notes](./notes)：本學期我記的筆記，前半部分比較詳盡，後半部分比較偷懶（霧），希望能幫到學弟學妹



## 運行

> 以下為課程助教給出的README.md文檔原內容

### Build

- `make` or `make build`: Build ChCore
- `make clean`: Clean ChCore

### Emulate

- `make qemu`: Start a QEMU instance to run ChCore

### Debug with GBD

- `make qemu-gdb`: Start a QEMU instance with GDB server
- `make gdb`: Start a GDB (gdb-multiarch) client

### Grade

- `make grade`: Show your grade of labs in the current branch

### Other

- Press `Ctrl+a x` to quit QEMU
- Press `Ctrl+d` to quit GDB
