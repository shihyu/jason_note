# 本機單元測試與除錯器完整驗證指南

在沒有 Kubernetes 權限時，仍可在本機建立可靠的驗證流程。核心組合是：

> 單元測試負責以可重複的方式判定對錯；sanitizer、race detector 與
> fuzzing 主動找錯；GDB、Delve、PDB 負責觀察失敗當下的狀態並定位原因。

除錯器與單元測試確實相輔相成，但除錯器本身不是測試框架。它不會自動增加
測試案例、覆蓋率或驗收標準，也不應以一次手動除錯階段取代 CI 測試結果。

## 建議的本機驗證流程

```text
format / lint / type check
          ↓
unit test + boundary test
          ↓
property test / fuzz test
          ↓
sanitizer / race detector / leak check
          ↓
local integration test（真實 DB、queue、cache）
          ↓
以相同 container image 執行 system test
          ↓
失敗時才進入 GDB / Delve / PDB
          ↓
把失敗輸入固化成 regression test，再跑完整測試
```

「完整」不是每次都進入除錯器，而是讓多種工具檢查不同類型的錯誤，並將
結果儲存為可重複執行的測試。

## 工具責任分工

| 工具 | 能回答的問題 | 不能證明的事情 |
| --- | --- | --- |
| Unit test | 給定輸入是否得到預期結果？邊界與錯誤處理是否正確？ | 未執行路徑、真實網路、排程與 production 設定是否正確 |
| Coverage | 哪些程式碼被測試執行過？ | 執行過的程式碼是否真的驗證正確 |
| Fuzz/property test | 隨機或生成輸入是否能造成 panic、crash 或違反 invariant？ | 所有可能輸入都已驗證 |
| Sanitizer/race detector | 執行路徑中是否出現記憶體錯誤、UB 或 data race？ | 沒被執行的路徑沒有錯誤 |
| GDB/Delve/PDB | 程式為什麼在這個狀態失敗？呼叫堆疊、執行緒及變數為何？ | 未來修改仍正確，或所有案例都通過 |
| 本機整合／系統測試 | 多模組與外部服務是否可運作？ | Kubernetes 控制平面、CNI、CSI、RBAC 與正式環境是否一致 |

## Go：unit test + race + fuzz + Delve

先跑快速測試，再跑 race detector：

```bash
go test ./...
go test -race ./...
go test -coverprofile=tests/coverage.out ./...
```

對 fuzz target 執行限時 fuzzing：

```bash
go test ./path/to/pkg -fuzz='^FuzzParse$' -fuzztime=60s
```

只針對一個失敗測試進行除錯：

```bash
dlv test ./path/to/pkg -- -test.run '^TestParseInvalidInput$' -test.v
```

常用 Delve 指令：

```text
break package.Function
condition 1 variable == unexpectedValue
continue
goroutines
goroutine <id> stack
locals
args
print variable
```

Go 優先使用 Delve，而不是 GDB。Delve 理解 goroutine、interface、channel 與
Go runtime。若測試疑似 deadlock，先設定 timeout 以保留 goroutine dump，
再用 Delve 檢查可重現案例：

```bash
go test ./... -run '^TestConcurrentFlow$' -count=100 -timeout=30s
```

不要因為 Delve 改變排程後問題消失，就判定 race 已修復。最終仍應以 `go test -race` 和可重複壓力測試驗收。

## Rust：cargo test + Clippy + Miri/fuzz + GDB

```bash
cargo fmt --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-features
```

先編譯測試但不執行，Cargo 會列出測試 binary：

```bash
cargo test --no-run
```

使用 `rust-gdb` 啟動該測試 binary，並把測試名稱傳給 Rust test harness：

```bash
rust-gdb --args target/debug/deps/TEST_BINARY TestName --exact --nocapture
```

在可用的 nightly/toolchain 環境，可加入 Miri 檢查 unsafe 與未定義行為：

```bash
cargo +nightly miri test
```

也可對 parser、protocol、序列化或 unsafe 邊界加入 `cargo-fuzz`。Fuzzer 找到的
最小失敗輸入應加入單元測試／迴歸測試語料庫。

GDB 適合檢查原生程式崩潰、FFI、執行緒、堆疊框架與記憶體；Rust 所有權或
生命週期錯誤應優先由編譯器、Clippy 與 Miri 處理。

## C/C++：unit test + sanitizer + GDB

一般 debug build：

```bash
cmake -S . -B build-debug \
  -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_C_FLAGS='-g -O0' \
  -DCMAKE_CXX_FLAGS='-g -O0'
cmake --build build-debug
ctest --test-dir build-debug --output-on-failure
```

記憶體與未定義行為檢查：

```bash
SANITIZER_FLAGS='-O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer'
cmake -S . -B build-asan \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DCMAKE_C_FLAGS="$SANITIZER_FLAGS" \
  -DCMAKE_CXX_FLAGS="$SANITIZER_FLAGS" \
  -DCMAKE_EXE_LINKER_FLAGS='-fsanitize=address,undefined'
cmake --build build-asan
ctest --test-dir build-asan --output-on-failure
```

Data race 需建立另一個 TSan build；不要與 ASan 混在同一 binary：

```bash
cmake -S . -B build-tsan \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DCMAKE_C_FLAGS='-O1 -g -fsanitize=thread' \
  -DCMAKE_CXX_FLAGS='-O1 -g -fsanitize=thread' \
  -DCMAKE_EXE_LINKER_FLAGS='-fsanitize=thread'
cmake --build build-tsan
ctest --test-dir build-tsan --output-on-failure
```

對指定 GoogleTest 案例進入 GDB：

```bash
gdb --args ./build-debug/tests/my_tests \
  --gtest_filter='ParserTest.RejectsInvalidFrame'
```

若 sanitizer 已指出程式崩潰行數，GDB 可用來檢查呼叫堆疊、指標、執行緒和
條件斷點；修正後仍需重新執行 sanitizer 測試套件。

## Python：pytest + property test + PDB

```bash
python -m pytest tests/unit -q
python -m pytest tests/system -q
python -m pytest --cov=src --cov-report=term-missing
```

第一個失敗案例直接進入 post-mortem PDB：

```bash
python -m pytest -x --pdb tests/unit/test_parser.py
```

只重跑一個案例：

```bash
python -m pytest -vv \
  tests/unit/test_parser.py::test_rejects_invalid_frame
```

Python 的 parser、資料轉換與狀態機可用 Hypothesis 產生大量輸入。將造成失敗的
最小化案例保留為迴歸測試。若問題來自 C extension，先在 Python 層重現，
再將 GDB 附加至 Python 行程，或直接以 GDB 啟動 Python。

## 沒有 Kubernetes 權限時，本機可以驗證什麼？

不要只在主機上執行程式。應使用與部署相同的容器映像、進入點、環境變數名稱、
非 root 使用者和唯讀檔案系統。

### 1. 使用真實依賴，不只使用 mock

單元測試可模擬 port/interface；整合測試則啟動真實版本的 PostgreSQL、Redis、
Kafka 或其他相依服務：

```bash
docker compose up -d --wait
./test.sh
docker compose down -v
```

測試資料必須隔離，不可連線至正式環境端點。

### 2. 驗證正式容器映像

```bash
docker build -t app:test .
docker run --rm --read-only --user 10001:10001 \
  --env-file tests/fixtures/test.env \
  app:test
```

測試映像是否包含正確的執行檔、CA 憑證、時區資料、動態函式庫、資料庫遷移與
健康檢查命令。

### 3. 模擬資源限制與 Linux 行為

```bash
docker run --rm \
  --cpus=0.5 \
  --memory=256m \
  --pids-limit=128 \
  app:test
```

另外測試 SIGTERM、優雅關閉、連線中斷、DNS 失敗、磁碟已滿、時鐘逾時與
相依服務重新啟動。這些故障注入通常比手動逐行除錯更能擴大覆蓋範圍。

### 4. 在本機容器中進行遠端除錯

Go 可在除錯映像中啟動無頭模式的 Delve：

```bash
dlv --headless --listen=127.0.0.1:40000 \
  --api-version=2 --accept-multiclient \
  exec /app/server
```

容器通常還需要 `SYS_PTRACE` 與較寬鬆的 seccomp 設定。只能在本機除錯容器中
使用：

```bash
docker run --rm -p 127.0.0.1:40000:40000 \
  --cap-add=SYS_PTRACE \
  --security-opt seccomp=unconfined \
  app:debug
```

除錯器連接埠只能綁定 `127.0.0.1`，不可暴露至公開網路。C/C++ 可用相同方式
在除錯映像內執行 `gdbserver`。

## 如何將除錯器驗證結果「固化」？

一次除錯階段不能由 CI 重播。每次找到問題後，至少固化一種證據：

- 將失敗輸入加入 regression test。
- 將 race/deadlock 的並行條件加入重複或壓力測試。
- 將 protocol packet、fixture 或 fuzz corpus 放在 `tests/`。
- 將 crash 的 stack trace、版本、compiler flags 與重現命令寫入測試紀錄。
- 將需要觀察的 invariant 改寫成 assertion，而不是永久依賴 breakpoint。

推薦循環：

```text
自動測試失敗
  → 用 debugger 找 root cause
  → 先新增或保留可重現測試
  → 修正實作
  → 單一測試通過
  → 完整 unit/system/sanitizer suite 通過
```

## AI 時代的用法

AI 適合協助：

- 依規格生成 unit test 草稿與邊界輸入。
- 根據失敗輸出提出 breakpoint 與 watch expression。
- 分析 stack trace、core dump 摘要與 sanitizer report。
- 把 debugger 找到的條件轉成 regression test。

AI 不應自行宣稱測試預期結果正確。產生的 assertion 可能只是重述現有的錯誤
實作。研究已開始讓 LLM 執行單元測試、讀取執行回饋，甚至操作具狀態的除錯器；
這能提升定位能力，但不能取代規格、實際執行和人工審查。

## 本機驗收清單

- [ ] 每個公開函式或類別有 unit test 與邊界條件。
- [ ] 有使用者視角的 system test，不只測內部函式。
- [ ] Coverage 已檢查，但沒有把 coverage 百分比當作正確性證明。
- [ ] Parser、協定或非信任輸入有 fuzz/property test。
- [ ] Go 執行 `go test -race`；C/C++ 分別執行 ASan/UBSan 與 TSan。
- [ ] Rust unsafe/FFI 邊界使用 Miri、sanitizer 或 fuzzing 中至少一項。
- [ ] 失敗案例可由單一命令重現並進入 debugger。
- [ ] Debugger 找到的問題已固化為 regression test。
- [ ] 使用與部署相同的 container image 跑 system test。
- [ ] 已驗證 non-root、read-only filesystem、resource limit 與 SIGTERM。
- [ ] 測試沒有連到 production DB、queue 或 API。
- [ ] 所有驗收最終由自動化測試通過判定，不靠手動 debugger 結論。

## 仍然無法由本機完全驗證的部分

即使上述全部通過，本機仍不能完全證明以下項目：

- Kubernetes RBAC、admission policy、CNI/CSI 與 service mesh 行為。
- 叢集 DNS、跨 node 網路、autoscaling 與 eviction。
- Production cloud IAM、load balancer、儲存與真實流量模式。
- 不同 kernel、CPU 架構或 production runtime 的差異。

因此文件應將結論表達為「本機驗證已達到高度可信」，而不是「已完整證明
Kubernetes 上必然正確」。

## 參考資料

- [Delve：`dlv test`](https://github.com/go-delve/delve/blob/master/Documentation/usage/dlv_test.md)
- [Go Data Race Detector](https://go.dev/doc/articles/race_detector)
- [Go Fuzzing](https://go.dev/doc/security/fuzz/)
- [Go Diagnostics](https://go.dev/doc/diagnostics)
- [Cargo `test`](https://doc.rust-lang.org/cargo/commands/cargo-test.html)
- [GDB 官方文件](https://sourceware.org/gdb/current/onlinedocs/gdb.html/)
- [Clang AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html)
- [Clang UndefinedBehaviorSanitizer](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html)
- [Clang ThreadSanitizer](https://clang.llvm.org/docs/ThreadSanitizer.html)
- [Python `pdb`](https://docs.python.org/3/library/pdb.html)
- [pytest debugging](https://docs.pytest.org/en/stable/how-to/failures.html)
- [GitHub Copilot：產生 unit tests](https://docs.github.com/en/copilot/tutorials/copilot-cookbook/testing-code/generate-unit-tests)
- [Learning to Generate Unit Tests for Automated Debugging](https://arxiv.org/abs/2502.01619)
- [InspectCoder：LLM 與互動式 debugger 協作](https://arxiv.org/abs/2510.18327)
