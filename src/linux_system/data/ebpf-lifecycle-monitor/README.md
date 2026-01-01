# eBPF Lifecycle Monitor

這是一個基於 eBPF 的 Linux 系統監控工具，專注於 Process 生命週期 (Exec, Exit) 與 OOM Kill 事件。
它包含一個高效能的 C++ 後端，並內建 WebSocket 伺服器，可即時廣播事件給前端客戶端。

## 功能特點

- **Process Execution**: 監控所有新執行的程式 (execve)。
- **Process Exit**: 監控程式結束與其 Exit Code。
- **OOM Kill**: 監控 Out-Of-Memory Killer 的觸發事件。
- **WebSocket API**: 透過 `ws://localhost:8080/ws` 即時推送 JSON 格式的事件數據。
- **現代化架構**: 使用 CO-RE (Compile Once – Run Everywhere) 技術與 Libbpf。

## 技術原理 (Under the Hood)

為什麼當您在終端機輸入 `ls` 時，Monitor 能立刻捕捉到？

本專案利用 Linux 核心的 **Tracepoints** 機制，這是一種事件驅動的監控方式，而非傳統的輪詢 (Polling)。

1.  **觸發 (Trigger)**: 當您執行 `ls` 時，Shell 會呼叫 `execve` 系統呼叫。
2.  **攔截 (Intercept)**: Linux 核心在載入新程式時，會經過 `sched_process_exec` 這個追蹤點 (Tracepoint)。
3.  **執行 (Execute)**: 掛載在該點的 eBPF 程式 (`handle_exec`) 立即被觸發，讀取當下的 Process 資訊 (PID, Comm)。
4.  **傳送 (Emit)**: 資料透過 Ring Buffer 高速傳送到 User Space，並轉換為 JSON 輸出。

這種方式讓監控具有 **極低的延遲** 與 **極小的效能開銷**，且能捕捉系統中所有的程式執行事件（包含背景服務或容器內的程式）。

## 系統架構

```mermaid
graph TD
    subgraph Kernel Space
        A[Tracepoint: sched_process_exec] -->|Trigger| B(BPF Program: handle_exec)
        C[Tracepoint: sched_process_exit] -->|Trigger| D(BPF Program: handle_exit)
        E[Tracepoint: oom_mark_victim] -->|Trigger| F(BPF Program: handle_oom)
        
        B --> G{Ring Buffer}
        D --> G
        F --> G
    end

    subgraph User Space (C++ Backend)
        H[BPFManager] -->|Poll| G
        H -->|Event Callback| I[Main Loop]
        I -->|JSON Serialize| J[WebServer]
        J -->|WebSocket Broadcast| K((Clients))
    end
```

## 快速開始

### 需求
- Linux Kernel 5.8+ (支援 BTF)
- `clang`, `llvm`, `libbpf-dev`, `bpftool`
- `g++`, `make`

### 編譯與執行

1. **編譯專案**
   ```bash
   make build
   ```

2. **執行 Monitor** (需要 root 權限)
   ```bash
   make run
   ```
   程式將啟動於 `http://localhost:8080`。

3. **測試功能**
   開啟另一個終端機執行任意指令（如 `ls`），Monitor 終端應會顯示 JSON 格式的事件。

   ```json
   {"timestamp": 123456789, "pid": 1234, "ppid": 1000, "comm": "ls", "type": "EXEC", "exit_code": 0, "target_pid": 0}
   ```

## 目錄結構

- `bpf/`: eBPF 核心程式碼 (*.bpf.c)
- `src/`: C++ 使用者空間程式碼
- `dist/`: 編譯產出
- `tests/`: 測試工具

## 開發者指南

- **新增監控事件**:
  1. 在 `bpf/monitor.bpf.c` 新增 Tracepoint 或 Kprobe。
  2. 在 `src/monitor.h` 定義新的事件類型與結構。
  3. 在 `src/main.cpp` 的 `BPFManager` callback 中處理新事件。

## License
GPL
