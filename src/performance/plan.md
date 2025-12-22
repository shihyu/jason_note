# Plan: Create Performance.md (Traditional Chinese)

## Goal
Create a new document `Performance.md` in Traditional Chinese that introduces performance measurement knowledge, tools, and methodologies. This document will serve as a guide for developers to understand how to measure and analyze system and application performance.

## Project Structure
- Directory: `src/performance`
- Target File: `Performance.md`

## Content Outline for `Performance.md` (Traditional Chinese)
1.  **緒論 (Introduction)**: 為什麼效能量測至關重要。
2.  **關鍵指標 (Key Metrics)**:
    - 延遲 (Latency): P50, P95, P99 的定義與應用。
    - 吞吐量 (Throughput): RPS, TPS, 頻寬。
    - 資源利用率 (Resource Usage): CPU, Memory, Disk I/O, Network。
    - 飽和度與錯誤 (Saturation & Errors): USE 方法論。
3.  **量測方法論 (Measurement Methodologies)**:
    - 基準測試 (Benchmarking): 微觀 (Micro) vs 宏觀 (Macro)。
    - 效能分析 (Profiling): CPU 採樣、記憶體分配、鎖競爭 (Mutex contention)。
    - 追蹤 (Tracing): 系統調用 (Syscalls)、分佈式追蹤。
4.  **常用工具 (Tools - Linux Focus)**:
    - 系統級別: `top`, `htop`, `vmstat`, `iostat`, `strace`, `perf`。
    - 應用層級: `gprof`, `pprof` (提及 `data/cpp-pprof-demo` 與 `data/cpp-fgprof-demo`)。
    - 壓力測試: `wrk`, `ab`, `locust`。
5.  **常見陷阱 (Common Pitfalls)**:
    - 觀測者效應 (Observer Effect)。
    - 冷啟動與預熱 (Cold Start vs. Warmup)。
    - 協同省略 (Coordinated Omission)。

## Makefile Specification
- `make build`: Echo "Documentation project, no build required."
- `make run`: Echo "Open Performance.md to read."
- `make test`: Verify that `Performance.md` exists and is not empty.
- `make clean`: Clean up any temporary files (if any).
- `make help`: Show available commands.

## Sub-tasks
1.  [x] Create `Performance.md` with the outlined structure and content in Traditional Chinese.
2.  [x] Update/Create `Makefile` to support the defined targets.
3.  [x] Verify the file creation using `make test`.
