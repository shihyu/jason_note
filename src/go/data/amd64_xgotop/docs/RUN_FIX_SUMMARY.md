# xgotop 可運行修正整理（`git diff .`）

## 背景

在 `x86_64` 主機上執行：

```bash
make compile
sudo ./xgotop -b ./testserver -web
sudo ./xgotop -pid <PROCESS_ID> -web
```

原本會遇到兩類問題：

1. `make compile` 失敗（BPF target 架構固定為 `arm64`）
2. `xgotop` 啟動失敗（CO-RE relocation 讀取 kernel module BTF `cast_common` 出錯）

## 本次實際修改檔案

- `gen.go`
- `xgotop.h`
- `cmd/xgotop/main.go`
- `vmlinux.h`（重新生成，屬環境產物）

## 修正摘要（原因與方式）

### 1. `gen.go`：`bpf2go` target 寫死 `arm64`

問題原因：

- `//go:generate` 固定使用 `-target arm64`
- 在 `x86_64` 環境會生成/編譯錯誤的 BPF 目標

修正方式：

- 改為依 `go env GOARCH` 自動選擇：
  - `amd64 -> -target amd64`
  - `arm64 -> -target arm64`

效果：

- `make compile` 可在 `x86_64` 正常通過

---

### 2. `xgotop.h`：BPF 程式只支援 arm64，且寄存器讀取路徑固定

問題原因：

- 原本只允許 `bpf_target_arm64`
- 讀取 Go runtime `g` 指標時固定用 ARM64 寄存器 `regs[28]`
- 在 `x86_64` 下會導致 BPF 編譯/執行不相容

修正方式：

- 放寬支援架構為 `arm64` 與 `x86_64`
- 抽出共用巨集 `__GO_G_ADDR(x)`：
  - `arm64` 使用 `regs[28]`
  - `x86_64` 使用 `r14`
- `get_go_g_struct_arm()` 改用共用巨集讀取

效果：

- `x86_64` 可正確編譯並讀取 Go `g` 指標

---

### 3. `cmd/xgotop/main.go`：CO-RE relocation 掃到壞掉的 module BTF（`cast_common`）

問題原因：

- `xgotop` 載入 eBPF objects 時，`cilium/ebpf` 會自動掃 kernel module BTF
- 本機 `/sys/kernel/btf/cast_common` 有 BTF 資料異常（`string table is empty`）
- 導致 `loadEbpfObjects()` 失敗，`-web` 無法真正跑起來

修正方式：

- 顯式載入 vmlinux BTF：`btf.LoadKernelSpec()`
- 傳入 `ebpf.CollectionOptions`：
  - `KernelTypes: kernelTypes`
  - `KernelModuleTypes: map[string]*btf.Spec{}`
- 用空的 `KernelModuleTypes` 禁止自動掃描 module BTF（避開 `cast_common`）
- 若 `LoadKernelSpec()` 失敗，保留原本 fallback 行為

效果：

- `sudo ./xgotop -b ./testserver -web` 可成功啟動
- `sudo ./xgotop -pid <PROCESS_ID> -web` 可成功啟動
- Web API 可正常回應，且能收到事件（`RPS/PPS` 非 0）

## `vmlinux.h` 為什麼 diff 很大

原因：

- `make compile` 會執行 `bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h`
- `vmlinux.h` 是根據「當前主機 kernel」重新生成
- 因此和 repo 內既有版本相比，會出現大量差異

結論：

- `vmlinux.h` 的大 diff 主要是環境產物，不是本次手動邏輯修改的核心

## 驗證結果（修正後）

- `make compile`：成功
- `sudo ./xgotop -b ./testserver -web`：成功啟動、Web API 可用、可收到事件
- `sudo ./xgotop -pid <PROCESS_ID> -web`：成功啟動、限定 PID attach、可收到事件

