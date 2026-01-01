# 專案計畫：eBPF Lifecycle Monitor

## 任務目標
將原有的 `cpp-monitor` 專案標準化為 `ebpf-lifecycle-monitor`，使用 eBPF 技術監控 Linux 系統中的 Process 生命週期（Exec, Exit）與 OOM Kill 事件。

## 專案結構組織
- **專案名稱**: `ebpf-lifecycle-monitor`
- **目錄結構**:
  ```text
  ebpf-lifecycle-monitor/
  ├── bpf/                # eBPF 核心程式碼 (*.bpf.c, vmlinux.h)
  ├── src/                # C++ User Space 程式碼 (main.cpp, mongoose.c)
  ├── tests/              # 測試程式碼與輸出 (oom_trigger.c, logs)
  ├── dist/               # 建置產物 (monitor, oom_trigger)
  ├── web/                # 前端介面 (如有)
  ├── Makefile            # 建置腳本
  ├── package.json        # Node.js 依賴 (若用於前端或工具)
  └── plan.md             # 本計畫文件
  ```

## 預期產出
1.  **可執行檔**:
    - `dist/monitor`: 主程式，負責載入 eBPF 程式並透過 WebSocket/Log 輸出事件。
    - `dist/oom_trigger`: 用於測試 OOM 監控功能的工具。
2.  **eBPF 物件**:
    - `bpf/monitor.bpf.o`: 編譯後的 eBPF bytecode。
    - `src/monitor.skel.h`: 從 BPF 物件生成的 skeleton header。
3.  **文件**:
    - `README.md` (可選，簡易說明)
4.  **測試**:
    - 能夠觸發並捕捉 Process Exec/Exit 事件。
    - 能夠觸發並捕捉 OOM Kill 事件。

## Makefile 規範

### 必備目標
- `make` (無參數)：顯示可用目標和使用範例。
- `make build`：編譯整個專案 (BPF + C++ Backend)。
- `make run`：執行監控程式 (自動處理 sudo 與 port 清理)。
- `make test`：目前對應 `test-oom`，後續可擴充整合測試。
- `make clean`：清理 `dist/`、`bpf/*.o` 及生成的 header 檔。

### 特殊處理
- Server 預設 Port: 8080 (用於 WebSocket 或網頁介面)
- run 目標會自動執行 `lsof -ti:8080 | xargs -r kill -9` 清理佔用的 port。
- 需要 root 權限執行 (`sudo`)。

## 驗收標準
1.  **編譯無誤**: `make build` 成功產生 `dist/monitor`。
2.  **執行正常**: `make run` 能啟動程式，無崩潰。
3.  **功能驗證**:
    - 啟動 monitor 後，執行任意指令（如 `ls`），monitor 能顯示 `EVENT_PROCESS_EXEC` 和 `EVENT_PROCESS_EXIT`。
    - 執行 `make test-oom`，monitor 能顯示 `EVENT_OOM_KILL`。
4.  **清理乾淨**: `make clean` 能移除所有生成檔案。

## 子任務拆解
1.  **專案初始化與結構確認**: 確認更名後的結構正確，並建立 `plan.md`。(已完成)
2.  **Makefile 標準化**: 更新 Makefile 以符合 `plan.md` 的規範 (如統一 `build`, `run`, `test` 目標名稱)。
3.  **程式碼重構 (Refactor)**:
    - 清理與簡化 `src/main.cpp` (使用現代 C++ 風格)。
    - 優化 `bpf/monitor.bpf.c`。
    - 移除無用檔案 (如舊的 log 或 js 驗證檔)。
    - 修正路徑依賴。
4.  **功能驗證**:
    - 測試 Exec/Exit 事件監控。
    - 測試 OOM 事件監控。
5.  **文件與流程圖**: 繪製並解釋系統運作流程圖。
