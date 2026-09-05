<!-- markdownlint-disable MD013 -->

# TDD、競態條件與效能測試：五種語言的極致品質實戰指南

高品質不是把單元測試跑到全綠，也不是追求單一覆蓋率數字。可靠的品質流程必須同時回答四個問題：

1. **邏輯正確性**：輸入、狀態轉換、邊界與錯誤處理是否符合規格？
2. **併發安全性**：不同排程下是否出現資料競態、死鎖、活鎖或遺失更新？
3. **效能穩定性**：延遲、吞吐量、記憶體與資源使用是否維持在預算內？
4. **系統完整性**：模組、程序、資料庫與外部服務組合後，使用者流程是否仍然成立？

本指南以測試驅動開發（Test-Driven Development，TDD）為骨架，涵蓋 Go、Rust、C/C++、Python 與 Node.js／JavaScript。重點不是堆砌工具，而是讓每個品質風險都有明確的測試方法、失敗證據與品質閘門。

> 本文聚焦「從規格到持續整合的品質工程」。若要查本機容器模擬與 GDB、Delve、PDB 的操作細節，請搭配[本機單元測試與除錯器完整驗證指南](local-unit-testing-debugging-guide.md)。

## 先建立正確觀念

### 測試工具各自能證明什麼？

| 方法 | 主要問題 | 通過代表什麼 | 通過仍不能證明什麼 |
| --- | --- | --- | --- |
| 範例／單元測試 | 已知案例是否符合規格？ | 這批案例得到預期結果 | 未列出的輸入與排程都正確 |
| 性質測試／模糊測試 | 大量生成輸入是否破壞不變量？ | 本次探索未找到反例 | 完整輸入空間沒有反例 |
| Race detector／sanitizer | 本次執行是否觀察到資料競態或記憶體錯誤？ | 已執行路徑未被工具報錯 | 未執行路徑安全，或沒有邏輯競態 |
| Benchmark | 指定環境中的樣本效能為何？ | 樣本符合當次門檻 | 正式環境必然同樣快 |
| 系統測試 | 完整流程是否符合驗收條件？ | 指定環境與流程可運作 | 所有故障模式都已涵蓋 |
| Coverage | 哪些程式碼曾被執行？ | 指定程式碼被測試碰到 | 斷言有效或行為正確 |
| Debugger／profiler | 失敗或瓶頸在哪裡？ | 找到可解釋的證據 | 問題已修正且不會復發 |

Go 官方特別說明 race detector 只能發現執行時實際觸發的競態，因此要搭配真實負載與足夠覆蓋率。[Go Data Race Detector][go-race] 同樣地，Rust 的型別系統能排除 safe Rust 中的資料競態，但不能證明業務邏輯正確；官方測試章節也明確指出型別檢查不能確認函式是否完成預期運算。[Rust 自動化測試][rust-tests]

### Data race 與 race condition 不相同

- **資料競態（data race）**：多個執行單元未同步存取同一記憶體位置，且至少一方寫入。這通常是 Go race detector 或 ThreadSanitizer 的目標。
- **競態條件（race condition）**：結果取決於事件先後順序。即使所有存取都有鎖，也可能因「檢查後再執行」、重複扣款或過期回應覆蓋新狀態而出錯。
- **死鎖（deadlock）**：執行單元互相等待，永遠無法前進。
- **活鎖（livelock）**：執行單元持續反應與重試，但沒有實質進展。

因此，「race detector 無報告」只是其中一道檢查，不能取代狀態模型、線性化檢查、逾時、壓力測試與系統不變量。

## 極致品質的 TDD 迴圈

```text
需求範例與不變量
        ↓
Red：寫一個會因缺少行為而失敗的測試
        ↓
確認失敗原因正確，避免假紅燈
        ↓
Green：只做足以通過測試的最小實作
        ↓
跑快速測試、靜態檢查與相關回歸測試
        ↓
Refactor：改善名稱、結構與重複，但不改行為
        ↓
依風險加入生成輸入、排程擾動、sanitizer、benchmark
        ↓
系統測試與 CI 品質閘門
```

### 第 0 步：先把規格轉成可驗證項目

每個需求至少寫出：

- 正常案例、邊界值、無效輸入與錯誤類型。
- 狀態轉換前置條件、後置條件與永遠成立的不變量。
- 共享狀態的擁有者、同步策略與允許的操作順序。
- 延遲、吞吐量、記憶體及資源上限，並標明測量環境。
- 對外可觀察結果，例如 HTTP 狀態、資料庫內容、事件與日誌欄位。

範例：轉帳功能不能只測試「A 轉 100 給 B」。還應定義總金額守恆、餘額不得為負、相同冪等鍵不得重複扣款，以及兩筆併發轉帳的允許結果集合。

### 第 1 步：Red 必須真的因缺少行為而失敗

1. 一次只加入一項可觀察行為。
2. 執行測試並保存完整失敗輸出。
3. 確認失敗是預期的 assertion，而非拼字錯誤、fixture 壞掉或環境缺失。
4. 如果測試在實作前就通過，先修正測試或規格，不要直接寫程式。

### 第 2 步：Green 只加入最小行為

- 不在同一步順便重構其他模組。
- 不用 mock 掩蓋真正需要驗證的合作行為。
- 每修正一個反例，就把最小失敗輸入保留為永久迴歸案例。
- 隨機測試必須輸出 seed，失敗時可用同一 seed 重播。

### 第 3 步：Refactor 必須保持測試全綠

重構前後都執行同一組測試。若變更同步原語、資料布局、序列化或查詢策略，必須額外重跑競態與效能套件，因為「行為相同」不代表排程與成本相同。

## 四大品質面向的詳細作法

### 1. 邏輯正確性測試

#### 建議組合

1. **範例測試**：以 Given–When–Then 或 Arrange–Act–Assert 表達需求。
2. **表格／參數化測試**：同一規則涵蓋正常值、零值、上下界與無效值。
3. **性質測試**：生成大量輸入驗證不變量，例如序列化後再反序列化仍等價。
4. **狀態模型測試**：把系統表示為命令與狀態機，逐步比對實作與參考模型。
5. **變異測試（mutation testing）**：刻意改變運算子或分支，檢查測試是否能抓到錯誤。

#### 邏輯正確性的通過條件

- 每個公開行為至少有正常、邊界與失敗案例。
- 測試名稱描述行為，不描述內部函式實作。
- 斷言檢查最終可觀察結果及必要的不變量。
- Coverage 用來尋找盲區，不把 100% coverage 當成品質完成。
- 重要 mutation 存活時，補強規格或斷言後才能合併。

#### 常見反模式

- 只斷言「沒有拋出例外」。
- 逐行 mock 內部呼叫，使重構必須大量改測試。
- 測試複製正式演算法，讓測試與實作犯相同錯誤。
- 快照過大，reviewer 無法辨認真正行為變化。

### 2. 競態條件與併發測試

#### 分成五層防線

1. **設計層**：縮小共享可變狀態；明確定義 mutex、channel、actor、transaction 或 immutable message 的邊界。
2. **決定性協調**：在測試中用 barrier、latch、channel 或 hook 控制關鍵交錯，不用固定 `sleep` 猜時序。
3. **排程探索**：以 Loom 等模型工具系統化探索交錯；其他語言則反覆改變執行緒數、CPU 數與工作順序。
4. **動態偵測**：Go `-race`、C/C++ ThreadSanitizer，以及 nightly Rust sanitizer 檢查實際執行路徑。
5. **壓力與系統不變量**：長時間執行真實工作負載，持續檢查守恆、唯一性、順序與冪等性。

#### 併發測試的基本模板

```text
建立乾淨且可重現的初始狀態
建立 N 個工作者，但先阻擋在同一個 barrier
同時釋放工作者執行互相衝突的操作
設定明確 timeout，避免 CI 永久卡住
等待所有工作者結束並收集錯誤
檢查最終狀態、不變量、重複事件與資源洩漏
以多個 worker 數量、CPU 數與 seed 重複執行
```

#### 必查案例

- read–modify–write、check–then–act、lazy initialization。
- cache 更新與失效、重試與冪等鍵、訊息至少一次投遞。
- 關閉中的 queue/channel、取消與 timeout、資源釋放。
- 鎖順序反轉、巢狀鎖、漏掉通知、錯失喚醒。
- 共享 iterator、集合、buffer、連線或 native extension。

#### 競態測試的通過條件

- 動態偵測器零報告，且不能用大範圍 suppressions 讓它「變綠」。
- 所有併發測試都有 timeout，失敗會輸出 seed、工作者數與狀態摘要。
- 壓力執行期間不變量始終成立；結束後沒有遺留執行緒、goroutine、task 或 handle。
- 同一失敗至少能用受控排程、保存的 seed 或縮小案例重現。

> 中斷點會改變執行時序，可能讓競態消失。Debugger 適合調查已重現的狀態，不是競態測試的通過依據。

### 3. 效能測試

效能測試必須先定義「預算」，再量測。只有「比上次快」而沒有環境、樣本與誤差資訊，不足以做品質判斷。

#### 指標分層

| 層級 | 常用指標 | 適合工具 |
| --- | --- | --- |
| 微基準 | 每次操作時間、配置次數、bytes/op | 語言 benchmark framework |
| 元件負載 | throughput、p50/p95/p99、錯誤率 | k6、Locust、wrk、autocannon |
| 系統容量 | 最大穩定吞吐、queue depth、飽和點 | 負載產生器與監控平台 |
| Profiling | CPU、allocation、lock contention、I/O | pprof、perf、flame graph、語言 profiler |

#### 可信量測流程

1. 固定硬體、OS、runtime、compiler、flags、依賴版本與電源模式。
2. 隔離背景負載；容器環境記錄 CPU／memory limit。
3. 先暖機，再執行多次樣本；隨機交錯 baseline 與 candidate，降低環境漂移偏差。
4. 防止 dead-code elimination，並把 setup、I/O 或 fixture 成本排除在目標區段之外。
5. 同時保存原始樣本、平均／中位數、變異程度與環境資訊。
6. 用「統計顯著」加「實務門檻」判定。例如 p95 增加超過 5% 且差異可信才阻擋。
7. benchmark 發現退化後，再以 profiler 找原因；不要用 profiler 取代 benchmark。

Google Benchmark 支援暖機、重複執行、平均／中位數／標準差、隨機交錯及 JSON 輸出；其比較工具也提醒效能資料有雜訊，統計差異仍須結合實際幅度判讀。[Google Benchmark 使用指南][google-benchmark] [比較工具說明][google-benchmark-tools]

#### 效能測試的通過條件

- 正確性測試先通過，benchmark 才有意義。
- 基準線與候選版本在同一受控環境量測。
- 吞吐量、尾端延遲、記憶體與錯誤率皆符合事先定義的預算。
- CI 上的微小抖動不立即判定回歸；重大退化也不能被平均值掩蓋。

### 4. 系統／整合測試

#### 建議層次

- **契約測試**：驗證 API schema、事件欄位與相容性。
- **元件整合測試**：連接真實資料庫、cache、queue 或檔案系統。
- **程序級測試**：從 CLI／HTTP 入口啟動正式 binary，觀察輸出與退出碼。
- **端對端測試**：以使用者流程驗證跨服務結果。
- **故障注入**：加入延遲、斷線、重複訊息、服務重啟與部分失敗。

#### 系統測試的通過條件

- 測試自己建立並清理隔離資料，不依賴執行順序。
- 外部依賴版本固定，ready check 成功後才開始測試。
- 每個等待都有期限，不以任意長度 `sleep` 代替條件等待。
- 失敗保存 server log、request ID、seed 與必要 artifacts。
- 重要流程同時驗證成功結果與副作用，例如資料、事件、audit log 及重試次數。

## 五種語言的工具與命令

命令是可組合的起點。請依專案版本鎖定工具，並在 CI 使用與本機相同的入口腳本。

### Go

| 目的 | 內建／常用工具 | 建議命令 |
| --- | --- | --- |
| 邏輯與 coverage | `testing` | `go test ./... -coverprofile=tests/coverage.out` |
| 重複與排程變化 | `testing` | `go test ./... -count=100 -shuffle=on -timeout=2m` |
| 資料競態 | race detector | `go test -race ./... -count=10 -timeout=10m` |
| 模糊測試 | native fuzzing | `go test ./path/to/pkg -fuzz='^FuzzTarget$' -fuzztime=60s` |
| 微基準 | `testing.B` | `go test ./... -run='^$' -bench=. -benchmem -count=10` |
| Profile | `pprof` | `go test ./pkg -run='^$' -bench=BenchmarkX -cpuprofile=tests/cpu.out` |
| 系統測試 | `go test` + 正式 binary | `go test ./tests/system/... -count=1 -timeout=10m` |

Go fuzzing 會把找到的失敗輸入寫入 corpus，之後一般 `go test` 也會將其當作迴歸案例。[Go Fuzzing][go-fuzz] `-race` 的 CPU 與記憶體成本很高，適合獨立 CI job；官方列出的典型成本是 2–20 倍時間與 5–10 倍記憶體。[Go Data Race Detector][go-race]

推薦順序：

```bash
go test ./... -shuffle=on
go test -race ./... -count=10 -timeout=10m
go test ./... -run='^$' -bench=. -benchmem -count=10
go test ./tests/system/... -count=1 -timeout=10m
```

### Rust

| 目的 | 內建／常用工具 | 建議命令 |
| --- | --- | --- |
| 邏輯與整合 | Cargo／libtest | `cargo test --all-features` |
| 靜態品質 | rustfmt／Clippy | `cargo fmt --check && cargo clippy --all-targets --all-features -- -D warnings` |
| 排程探索 | Loom | `RUSTFLAGS='--cfg loom' cargo test --test concurrency --release` |
| unsafe／UB | Miri | `cargo +nightly miri test` |
| 資料競態 | nightly ThreadSanitizer | `RUSTFLAGS='-Zsanitizer=thread' cargo +nightly test -Zbuild-std --target x86_64-unknown-linux-gnu` |
| 模糊測試 | cargo-fuzz | `cargo +nightly fuzz run fuzz_target -- -max_total_time=60` |
| 微基準 | Criterion | `cargo bench` |
| 系統測試 | `tests/` + `Command` | `cargo test --test system -- --test-threads=1` |

Rust 的內建測試預設平行執行；共享檔案或全域資源可能讓測試互相干擾，可用 `--test-threads=1` 診斷，但長期應隔離資源。[Rust 測試執行方式][rust-test-control] Safe Rust 防止資料競態，不會防止 deadlock、原子操作順序錯誤或業務競態。Loom 可探索多種併發排列；sanitizer 仍屬 nightly、不穩定功能，且有平台與同步原語限制。[Loom][loom] [Rust sanitizer][rust-sanitizer]

### C/C++

| 目的 | 內建／常用工具 | 建議命令 |
| --- | --- | --- |
| 邏輯 | GoogleTest／Catch2 + CTest | `ctest --test-dir build-test --output-on-failure` |
| 記憶體／UB | ASan + UBSan | `-O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer` |
| 資料競態 | ThreadSanitizer | `-O1 -g -fsanitize=thread` |
| 模糊測試 | libFuzzer | `-O1 -g -fsanitize=fuzzer,address` |
| 微基準 | Google Benchmark | `./build-bench/bench --benchmark_repetitions=20 --benchmark_format=json` |
| 系統追蹤 | `perf` | `perf stat -r 10 ./build-release/app` |
| 系統測試 | CTest／Bats／自訂 harness | `ctest --test-dir build-system --output-on-failure` |

ASan 與 TSan 不可放在同一個 binary，應建立獨立 build 與 CI job。Clang 文件也指出 TSan 通常需要所有程式碼都插樁，未插樁的預編譯函式庫可能造成漏報或誤報。[Clang 編譯器手冊][clang-manual] [ThreadSanitizer][clang-tsan]

```bash
cmake -S . -B build-asan \
  -DCMAKE_C_FLAGS='-O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer' \
  -DCMAKE_CXX_FLAGS='-O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer'
cmake --build build-asan
ctest --test-dir build-asan --output-on-failure

cmake -S . -B build-tsan \
  -DCMAKE_C_FLAGS='-O1 -g -fsanitize=thread' \
  -DCMAKE_CXX_FLAGS='-O1 -g -fsanitize=thread'
cmake --build build-tsan
ctest --test-dir build-tsan --output-on-failure
```

### Python

| 目的 | 內建／常用工具 | 建議命令 |
| --- | --- | --- |
| 邏輯與參數化 | pytest | `python -m pytest tests/unit -q` |
| 性質測試 | Hypothesis | `python -m pytest tests/unit -q` |
| coverage | coverage.py／pytest-cov | `python -m pytest --cov=src --cov-report=term-missing` |
| 競態壓力 | barrier + 重複測試 | `python -m pytest tests/concurrency -q -x` |
| free-threaded 驗證 | CPython free-threaded build | `python -VV && python -m pytest tests/concurrency -q` |
| 微基準 | pyperf | `python -m pyperf timeit --rigorous --setup='from pkg import f' 'f()'` |
| 負載測試 | Locust | `locust -f tests/performance/locustfile.py --headless` |
| 系統測試 | pytest + subprocess／HTTP client | `python -m pytest tests/system -q` |

原稿「Python 因 GIL 不會發生 data race」並不正確。一般 CPython 會在 bytecode 之間切換執行緒，阻塞 I/O 也會釋放 GIL，純 Python 邏輯仍需正確同步；CPython 3.13 起更提供可選的 free-threaded build。[Python 執行緒與 GIL][python-gil] [Python free-threading][python-free-threading]

Python 缺少可與 Go `-race` 等同的一鍵偵測器。實務上應：

1. 用 `threading.Barrier` 控制衝突點，不把 `sys.setswitchinterval()` 當正確性證明。
2. 以 Hypothesis 產生命令序列，驗證狀態機不變量。
3. 對支援的專案，同時在一般與 free-threaded CPython 執行併發套件。
4. C extension 另以 ASan／TSan 編譯測試。
5. 用 timeout、faulthandler 與 thread dump 保存死鎖證據。

pytest 的參數值會直接傳入、不自動複製；若測試修改共享 list 或 dict，後續案例可能受污染。[pytest 參數化][pytest-parametrize]

### Node.js／JavaScript

| 目的 | 內建／常用工具 | 建議命令 |
| --- | --- | --- |
| 邏輯 | `node:test` + `node:assert` | `node --test tests/unit` |
| coverage | Node test runner | `node --test --experimental-test-coverage tests/unit` |
| 順序／隔離診斷 | Node test runner | `node --test --test-concurrency=1 tests` |
| 非同步競態 | barrier、fake timer、重複與 worker 測試 | `node --test tests/concurrency` |
| 微基準 | Tinybench／Benchmark.js | `node tests/performance/bench.mjs` |
| CPU／heap profile | Node profiler | `node --cpu-prof app.mjs`／`node --heap-prof app.mjs` |
| 精細計時 | `node:perf_hooks` | 在 benchmark 中使用 `performance.mark()`／`measure()` |
| 系統／負載 | Playwright、k6、autocannon | `node --test tests/system` |

Node test runner 預設以獨立 child process 執行測試檔案；`--test-concurrency` 控制檔案層級平行度，但單一測試檔內的測試仍在同一 application thread 執行。[Node.js test runner][node-test] 要測真正的平行共享記憶體，需涵蓋 `worker_threads`、`SharedArrayBuffer` 與 `Atomics` 使用情境。[Node.js worker threads][node-workers]

Node.js 沒有與 Go `-race` 等價的通用 JavaScript race detector。測試重點分成：

- Promise、callback、timer、取消與事件順序造成的邏輯競態。
- 多個 request 同時修改資料庫或 cache 的系統競態。
- worker threads 共享記憶體的同步與 termination。
- native addon 以 C/C++ sanitizer 另建測試 job。

`node:perf_hooks` 適合在程序內做高解析度量測，但正式效能回歸仍需獨立 benchmark harness、暖機、多次樣本與環境控制。[Node.js Performance APIs][node-perf]

## CI 品質閘門：快速回饋與深度驗證分離

### 每個 pull request

1. 格式、lint、型別與編譯檢查。
2. 快速單元、參數化與契約測試。
3. 受影響模組的系統 smoke test。
4. 低成本 concurrency regression test。
5. 若改到共享狀態、unsafe、native code 或同步邏輯，強制執行 race／sanitizer job。

### 每晚或專用硬體

1. 全套 race detector、ASan／UBSan／TSan 與 Miri。
2. 較長時間 fuzzing、property 與排程探索。
3. 多組 worker／CPU／seed 的壓力測試。
4. 固定機器上的 benchmark baseline comparison。
5. 完整系統測試、故障注入與資源洩漏檢查。

### 發布前

- 所有 release build 與正式設定重新跑關鍵系統流程。
- 在目標硬體做容量測試，確認 p95／p99、吞吐與錯誤率預算。
- 檢查 sanitizer、fuzzer、benchmark 與系統測試 artifacts。
- 所有 quarantine／skip／suppression 都有負責人、原因與到期日。

## Flaky test 的處理準則

不穩定測試是缺陷訊號，不應只靠 retry 變綠。

1. 保存失敗 seed、執行順序、時間、CPU 數、runtime 版本與完整 log。
2. 先判斷是產品競態、測試共享狀態、外部服務、時鐘、隨機數，還是資源不足。
3. 以 barrier、fake clock、隔離資料與固定 seed 縮小問題。
4. 修正後用原 seed 或交錯方式重播，再增加迴歸測試。
5. 必須 quarantine 時，不得靜默忽略；建立追蹤項目並設定解除期限。

## AI 輔助測試的品質邊界

AI 適合產生邊界值候選、表格測試骨架、fuzz property 與失敗摘要，但人仍需負責：

- 判定規格與不變量是否完整。
- 確認測試在錯誤實作上真的會失敗。
- 避免 AI 同時生成實作與同構測試，造成共同盲點。
- 審查 timeout、同步、資源清理與 benchmark 方法是否可信。
- 驗證引用的工具旗標與版本，不直接相信不存在的命令。

最有效的提示不是「幫我補測試」，而是提供規格、不變量、禁止事項與現有失敗證據，再要求 AI 列出尚未涵蓋的反例。

## 可直接採用的完成定義

### 邏輯正確性

- [ ] 新行為遵循 Red → Green → Refactor，保留第一次預期失敗輸出。
- [ ] 正常、邊界、錯誤、參數化與核心不變量都有測試。
- [ ] 重要 parser、protocol 或狀態機有 property／fuzz 測試。
- [ ] Coverage 沒有關鍵盲區，且關鍵斷言可殺死相關 mutation。

### 競態條件

- [ ] 測試使用同步點控制交錯，不靠任意 `sleep`。
- [ ] 所有等待都有 timeout，失敗能重播 seed 或排程。
- [ ] 適用的 race detector／TSan／Loom／free-threaded job 已執行。
- [ ] 驗證資料守恆、唯一性、冪等性、順序與資源完全釋放。

### 效能

- [ ] 延遲、吞吐、記憶體與錯誤率預算在實作前定義。
- [ ] baseline 與 candidate 使用相同環境，含暖機與多次樣本。
- [ ] 判定同時考量統計可信度與實務影響幅度。
- [ ] benchmark 與 profiler 分工清楚，原始結果可追溯。

### 系統品質

- [ ] 從正式 CLI／API 入口測試主要使用者流程。
- [ ] 真實依賴版本固定，資料隔離且 teardown 完整。
- [ ] timeout、重試、斷線、重複投遞與部分失敗已有案例。
- [ ] CI 與本機共用同一測試入口，失敗 artifacts 足以調查。

## 最終原則

極致品質不是所有工具每次都跑，而是依風險分層：TDD 讓規格先於實作；邏輯測試與生成式測試找反例；排程探索和動態偵測器揭露併發缺陷；benchmark 以可靠樣本守住效能預算；系統測試確認真實邊界。任何工具的「沒有報錯」都不能單獨證明正確，真正可維持的品質來自可重現證據、清楚不變量與持續執行的品質閘門。

## 參考資料

- [Go Data Race Detector][go-race]
- [Go Fuzzing][go-fuzz]
- [Rust：Writing Automated Tests][rust-tests]
- [Rust：Controlling How Tests Are Run][rust-test-control]
- [Rust sanitizer（Unstable Book）][rust-sanitizer]
- [Loom：Rust concurrency permutation testing][loom]
- [Clang ThreadSanitizer][clang-tsan]
- [Clang Compiler User's Manual：Sanitizers][clang-manual]
- [Google Benchmark User Guide][google-benchmark]
- [Google Benchmark comparison tools][google-benchmark-tools]
- [Python：Thread states and the GIL][python-gil]
- [Python：Free-threading support][python-free-threading]
- [pytest parametrization][pytest-parametrize]
- [Node.js Test Runner][node-test]
- [Node.js Worker Threads][node-workers]
- [Node.js Performance Measurement APIs][node-perf]

[go-race]: https://go.dev/doc/articles/race_detector
[go-fuzz]: https://go.dev/doc/security/fuzz/
[rust-tests]: https://doc.rust-lang.org/stable/book/ch11-00-testing.html
[rust-test-control]: https://doc.rust-lang.org/book/ch11-02-running-tests.html
[rust-sanitizer]: https://doc.rust-lang.org/beta/unstable-book/compiler-flags/sanitizer.html
[loom]: https://github.com/tokio-rs/loom
[clang-tsan]: https://clang.llvm.org/docs/ThreadSanitizer.html
[clang-manual]: https://clang.llvm.org/docs/UsersManual.html#controlling-code-generation
[google-benchmark]: https://github.com/google/benchmark/blob/main/docs/user_guide.md
[google-benchmark-tools]: https://github.com/google/benchmark/blob/main/docs/tools.md
[python-gil]: https://docs.python.org/3/c-api/threads.html
[python-free-threading]: https://docs.python.org/3/howto/free-threading-python.html
[pytest-parametrize]: https://docs.pytest.org/en/stable/how-to/parametrize.html
[node-test]: https://nodejs.org/api/test.html
[node-workers]: https://nodejs.org/api/worker_threads.html
[node-perf]: https://nodejs.org/api/perf_hooks.html
