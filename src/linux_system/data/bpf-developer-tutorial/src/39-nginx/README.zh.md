# 使用 eBPF 跟蹤 Nginx 請求

## 引言

Nginx 是世界上最流行的 Web 服務器和反向代理之一，以其高性能、穩定性和低資源消耗而聞名。它廣泛用於提供靜態內容、負載均衡以及作為動態應用的反向代理。為了保持其性能優勢，監控和優化 Nginx 的運行尤為重要，尤其是在處理大量請求時。利用 eBPF（擴展的伯克利包過濾器），可以深入瞭解 Nginx 的性能表現，識別瓶頸並進行優化，而無需修改源代碼或重啟服務。

eBPF 是一項革命性技術，允許開發人員在 Linux 內核中運行自定義程序。最初設計用於網絡數據包過濾，但 eBPF 現已發展為一個多功能工具，廣泛應用於跟蹤、監控和分析系統行為。通過利用 eBPF，您可以跟蹤 Nginx 的關鍵函數，測量延遲，識別瓶頸，進而優化系統性能。

## 背景：Nginx 和 eBPF

### Nginx

Nginx 採用事件驅動架構，使其在資源佔用極少的情況下能夠高效處理成千上萬的併發連接。這種高效性依賴於其請求處理、響應生成和事件處理等多個性能關鍵函數。瞭解這些函數在不同負載下的表現對於優化 Nginx 的使用至關重要。

### eBPF

eBPF 程序在 Linux 內核的安全沙盒環境中運行。這些程序可以附加到各種鉤子上，如系統調用、跟蹤點，甚至可以通過 uprobes（用戶級探針）附加到用戶空間的函數。這使得 eBPF 成為一個強大的系統可觀測性工具，可以收集詳細的性能數據並實時執行策略。

eBPF 的一個常見用例是跟蹤函數執行時間，以測量延遲。這對於瞭解 Nginx 中特定函數的執行時間特別有用，有助於診斷性能問題、優化資源使用，並提高 Nginx 部署的整體效率。

### Uprobes

Uprobes 是一種用於跟蹤用戶空間應用程序函數的探針，它通過附加到特定用戶空間函數的入口和出口點，可以捕獲精確的時間信息。然而，需要注意的是，在內核模式 eBPF 運行時使用 uprobes 可能會帶來一定的性能開銷。為此，您可以考慮使用基於 LLVM JIT/AOT 的用戶模式 eBPF 運行時 [bpftime](https://github.com/eunomia-bpf/bpftime)。這種運行時可以在用戶空間中運行 eBPF 程序，與內核模式 eBPF 兼容，並有可能降低開銷。

## Nginx 的性能關鍵函數

以下是 Nginx 中一些性能關鍵的函數，可以通過 eBPF 進行監控：

- **ngx_http_process_request**：負責處理傳入的 HTTP 請求。監控此函數有助於跟蹤請求處理的開始。
- **ngx_http_upstream_send_request**：當 Nginx 作為反向代理時，負責向上遊服務器發送請求。
- **ngx_http_finalize_request**：完成 HTTP 請求的處理，包括髮送響應。跟蹤此函數可以衡量整個請求處理的時間。
- **ngx_event_process_posted**：處理事件循環中的隊列事件。
- **ngx_handle_read_event**：負責處理來自套接字的讀取事件，對監控網絡 I/O 性能至關重要。
- **ngx_writev_chain**：負責將響應發送回客戶端，通常與寫事件循環結合使用。

## 使用 bpftrace 跟蹤 Nginx 函數

為了監控這些函數，我們可以使用 `bpftrace`，一種 eBPF 的高級跟蹤語言。以下是一個用於跟蹤幾個關鍵 Nginx 函數執行時間的腳本：

```bt
#!/usr/sbin/bpftrace

// 監控 HTTP 請求處理的開始
uprobe:/usr/sbin/nginx:ngx_http_process_request
{
    printf("HTTP 請求處理開始 (tid: %d)\n", tid);
    @start[tid] = nsecs;
}

// 監控 HTTP 請求的完成
uretprobe:/usr/sbin/nginx:ngx_http_finalize_request
/@start[tid]/
{
    $elapsed = nsecs - @start[tid];
    printf("HTTP 請求處理時間: %d ns (tid: %d)\n", $elapsed, tid);
    delete(@start[tid]);
}

// 監控向上遊服務器發送請求的開始
uprobe:/usr/sbin/nginx:ngx_http_upstream_send_request
{
    printf("開始向上遊服務器發送請求 (tid: %d)\n", tid);
    @upstream_start[tid] = nsecs;
}

// 監控上游請求發送完成
uretprobe:/usr/sbin/nginx:ngx_http_upstream_send_request
/@upstream_start[tid]/
{
    $elapsed = nsecs - @upstream_start[tid];
    printf("上游請求發送完成時間: %d ns (tid: %d)\n", $elapsed, tid);
    delete(@upstream_start[tid]);
}

// 監控事件處理的開始
uprobe:/usr/sbin/nginx:ngx_event_process_posted
{
    printf("事件處理開始 (tid: %d)\n", tid);
    @event_start[tid] = nsecs;
}

// 監控事件處理的完成
uretprobe:/usr/sbin/nginx:ngx_event_process_posted
/@event_start[tid]/
{
    $elapsed = nsecs - @event_start[tid];
    printf("事件處理時間: %d ns (tid: %d)\n", $elapsed, tid);
    delete(@event_start[tid]);
}
```

### 運行腳本

要運行上述腳本，先啟動 Nginx，然後使用 `curl` 等工具生成 HTTP 請求：

```bt
# bpftrace /home/yunwei37/bpf-developer-tutorial/src/39-nginx/trace.bt
Attaching 4 probes...
事件處理開始 (tid: 1071)
事件處理時間: 166396 ns (tid: 1071)
事件處理開始 (tid: 1071)
事件處理時間: 87998 ns (tid: 1071)
HTTP 請求處理開始 (tid: 1071)
HTTP 請求處理時間: 1083969 ns (tid: 1071)
事件處理開始 (tid: 1071)
事件處理時間: 92597 ns (tid: 1071)
```

該腳本監控了幾個 Nginx 函數的開始和結束時間，並打印了每個函數的執行時間。這些數據可以用來分析和優化 Nginx 服務器的性能。

## 測試 Nginx 的函數延遲

為了更詳細地分析函數延遲，您可以使用 `funclatency` 工具，該工具可以測量 Nginx 函數的延遲分佈。以下是如何測試 `ngx_http_process_request` 函數的延遲：

```console
# sudo ./funclatency /usr/sbin/nginx:ngx_http_process_request
tracing /usr/sbin/nginx:ngx_http_process_request...
tracing func ngx_http_process_request in /usr/sbin/nginx...
Tracing /usr/sbin/nginx:ngx_http_process_request.  Hit Ctrl-C to exit
^C
     nsec                : count    distribution
         0 -> 1          : 0        |                                        |
   524288 -> 1048575    : 16546    |****************************************|
   1048576 -> 2097151    : 2296     |*****                                   |
   2097152 -> 4194303    : 1264     |***                                     |
   4194304 -> 8388607    : 293      |                                        |
   8388608 -> 16777215   : 37       |                                        |
Exiting trace of /usr/sbin/nginx:ngx_http_process_request
```

### 結果總結

上述結果顯示了 `ngx_http_process_request` 函數的延遲分佈。大多數請求在 524,288 至 1,048,575 納秒內處理完成，少部分請求處理時間更長。這些信息對於識別性能瓶頸和優化 Nginx 請求處理至關重要。

通過使用 `funclatency`，您可以：

- **識別性能瓶頸**：瞭解哪些函數執行時間最長，並將優化工作重點放在這些函數上。
- **監控系統性能**：定期監控函數延遲，確保在高負載下 Nginx 服務器的最佳性能。
- **優化 Nginx 配置**：利用延遲測量得出的洞察調整 Nginx 設置或修改應用程序，以提高整體性能。

您可以在 [bpf-developer-tutorial 倉庫](https://github.com/eunomia-bpf/bpf-developer-tutorial/blob/main/src/33-funclatency) 中找到 `funclatency` 工具。

## 結論

通過 eBPF 跟蹤 Nginx 請求可以為您的 Web 服務器提供寶貴的性能洞察，使您能夠監控、分析和優化其操作。使用 `bpftrace` 和 `funclatency`

 等工具，您可以測量函數執行時間、識別瓶頸，並根據數據做出決策來改進 Nginx 部署。

如果您有興趣瞭解更多關於 eBPF 的知識，包括更多高級示例和教程，請訪問我們的 [https://github.com/eunomia-bpf/bpf-developer-tutorial](https://github.com/eunomia-bpf/bpf-developer-tutorial) 或查看我們的網站 [https://eunomia.dev/tutorials/](https://eunomia.dev/tutorials/)。
