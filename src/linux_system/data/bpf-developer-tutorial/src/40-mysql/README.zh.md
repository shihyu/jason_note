# 使用 eBPF 跟蹤 MySQL 查詢

MySQL 是全球最廣泛使用的關係型數據庫管理系統之一。無論您是在運行小型應用程序還是大型企業系統，瞭解 MySQL 數據庫的性能特徵都至關重要。特別是瞭解 SQL 查詢的執行時間以及哪些查詢佔用了最多的時間，有助於診斷性能問題，並優化數據庫以提高效率。

在這種情況下，eBPF（擴展的伯克利包過濾器）可以派上用場。eBPF 是一項強大的技術，它允許您編寫程序並在 Linux 內核中運行，幫助您跟蹤、監控和分析系統行為的各個方面，包括 MySQL 這類應用程序的性能。在本文中，我們將探討如何使用 eBPF 跟蹤 MySQL 查詢，測量其執行時間，並深入瞭解數據庫的性能表現。

## 背景：MySQL 和 eBPF

### MySQL

MySQL 是一種關係型數據庫管理系統（RDBMS），使用結構化查詢語言（SQL）來管理和查詢數據。它廣泛應用於各種場景，從 Web 應用程序到數據倉庫。MySQL 的性能對應用程序的整體性能至關重要，尤其是在處理大數據集或複雜查詢時。

### eBPF

eBPF 是一項允許在 Linux 內核中執行自定義程序的技術，而無需修改內核源代碼或加載內核模塊。eBPF 最初是為網絡數據包過濾而設計的，但現在已經發展為一個多用途的工具，可用於性能監控、安全和調試。eBPF 程序可以附加到各種內核和用戶空間事件上，使得我們能夠跟蹤函數、系統調用等的執行。

使用 eBPF，我們可以跟蹤 MySQL 的某些函數，例如負責處理 SQL 查詢的 `dispatch_command` 函數。通過跟蹤該函數，我們可以捕獲查詢執行的開始和結束時間，測量延遲，並記錄執行的查詢。

##  MySQL 查詢

要使用 eBPF 跟蹤 MySQL 查詢，我們可以編寫一個使用 `bpftrace` 的腳本，`bpftrace` 是一種 eBPF 的高級跟蹤語言。以下是一個跟蹤 MySQL 中 `dispatch_command` 函數的腳本，用於記錄執行的查詢並測量其執行時間：

```bt
#!/usr/bin/env bpftrace

// 跟蹤 MySQL 中的 dispatch_command 函數
uprobe:/usr/sbin/mysqld:dispatch_command
{
    // 將命令執行的開始時間存儲在 map 中
    @start_times[tid] = nsecs;
    
    // 打印進程 ID 和命令字符串
    printf("MySQL command executed by PID %d: ", pid);
    
    // dispatch_command 的第三個參數是 SQL 查詢字符串
    printf("%s\n", str(arg3));
}

uretprobe:/usr/sbin/mysqld:dispatch_command
{
    // 從 map 中獲取開始時間
    $start = @start_times[tid];
    
    // 計算延遲，以毫秒為單位
    $delta = (nsecs - $start) / 1000000;
    
    // 打印延遲
    printf("Latency: %u ms\n", $delta);
    
    // 從 map 中刪除條目以避免內存洩漏
    delete(@start_times[tid]);
}
```

### 腳本解釋

1. **跟蹤 `dispatch_command` 函數**：
   - 該腳本在 MySQL 中的 `dispatch_command` 函數上附加了一個 `uprobe`。該函數在 MySQL 需要執行 SQL 查詢時調用。`Uprobe` 在內核模式 eBPF 運行時中可能會導致較大的性能開銷。在這種情況下，您可以考慮使用用戶模式 eBPF 運行時，例如 [bpftime](https://github.com/eunomia-bpf/bpftime)。
   - `uprobe` 捕獲函數執行的開始時間並記錄正在執行的 SQL 查詢。

2. **計算和記錄延遲**：
   - 一個相應的 `uretprobe` 附加到 `dispatch_command` 函數。`uretprobe` 在函數返回時觸發，允許我們計算查詢的總執行時間（延遲）。
   - 延遲以毫秒為單位計算並打印到控制檯。

3. **使用 Map 管理狀態**：
   - 腳本使用一個 BPF map 來存儲每個查詢的開始時間，並以線程 ID (`tid`) 作為鍵。這使我們能夠匹配每次查詢執行的開始和結束時間。
   - 在計算延遲後，從 map 中刪除條目以避免內存洩漏。

## 運行腳本

要運行此腳本，只需將其保存為文件（例如 `trace_mysql.bt`），然後使用 `bpftrace` 執行它：

```bash
sudo bpftrace trace_mysql.bt
```

### 輸出示例

腳本運行後，它將打印 MySQL 執行的每個 SQL 查詢的信息，包括進程 ID、查詢內容以及延遲時間：

```console
MySQL command executed by PID 1234: SELECT * FROM users WHERE id = 1;
Latency: 15 ms
MySQL command executed by PID 1234: UPDATE users SET name = 'Alice' WHERE id = 2;
Latency: 23 ms
MySQL command executed by PID 1234: INSERT INTO orders (user_id, product_id) VALUES (1, 10);
Latency: 42 ms
```

這個輸出顯示了正在執行的 SQL 命令以及每個命令的執行時間，為您提供了關於 MySQL 查詢性能的寶貴見解。

## 跟蹤 MySQL 查詢可以帶來什麼收穫？

通過使用 eBPF 跟蹤 MySQL 查詢，您可以獲得以下幾點收穫：

- **識別慢查詢**：您可以快速識別哪些 SQL 查詢執行時間最長。這對於性能調優以及優化數據庫模式或索引策略至關重要。
- **監控數據庫性能**：定期監控查詢的延遲，確保您的 MySQL 數據庫在不同工作負載下保持最佳性能。
- **調試和故障排除**：在面對性能問題時，這種跟蹤方法可以幫助您準確定位導致延遲的查詢，從而更容易調試和解決問題。
- **容量規劃**：通過了解各種查詢的延遲，您可以更好地進行容量規劃，確保您的 MySQL 數據庫能夠處理更高的負載或更復雜的查詢。

## 結論

eBPF 提供了一種強大的方法來監控和跟蹤 MySQL 查詢的性能，而無需對系統進行侵入式更改。通過使用 `bpftrace` 這樣的工具，您可以實時瞭解數據庫的性能表現，識別潛在的瓶頸，並優化系統以獲得更好的性能。

如果您有興趣瞭解更多關於 eBPF 的知識，以及如何將其用於監控和優化系統的其他部分，請訪問我們的 [https://github.com/eunomia-bpf/bpf-developer-tutorial](https://github.com/eunomia-bpf/bpf-developer-tutorial) 或瀏覽我們的網站 [https://eunomia.dev/tutorials/](https://eunomia.dev/tutorials/) 獲取更多示例和完整的教程。
