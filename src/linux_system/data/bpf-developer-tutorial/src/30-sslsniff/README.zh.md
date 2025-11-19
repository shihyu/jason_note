# eBPF 實踐教程：使用 uprobe 捕獲多種庫的 SSL/TLS 明文數據

隨著TLS在現代網絡環境中的廣泛應用，跟蹤微服務RPC消息已經變得愈加棘手。傳統的流量嗅探技術常常受限於只能獲取到加密後的數據，導致無法真正觀察到通信的原始內容。這種限制為系統的調試和分析帶來了不小的障礙。

但現在，我們有了新的解決方案。使用 eBPF 技術，通過其能力在用戶空間進行探測，提供了一種方法重新獲得明文數據，使得我們可以直觀地查看加密前的通信內容。然而，每個應用可能使用不同的庫，每個庫都有多個版本，這種多樣性給跟蹤帶來了複雜性。

在本教程中，我們將帶您瞭解一種跨多種用戶態 SSL/TLS 庫的 eBPF 追蹤技術，它不僅可以同時跟蹤 GnuTLS 和 OpenSSL 等用戶態庫，而且相比以往，大大降低了對新版本庫的維護工作。完整的源代碼可以在這裡查看：<https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/30-sslsniff>

## 背景知識

在深入本教程的主題之前，我們需要理解一些核心概念，這些概念將為我們後面的討論提供基礎。

### SSL 和 TLS

SSL (Secure Sockets Layer): 由 Netscape 在 1990 年代早期開發，為網絡上的兩臺機器之間提供數據加密傳輸。然而，由於某些已知的安全問題，SSL的使用已被其後繼者TLS所替代。

TLS (Transport Layer Security): 是 SSL 的繼任者，旨在提供更強大和更安全的數據加密方式。TLS 工作通過一個握手過程，在這個過程中，客戶端和服務器之間會選擇一個加密算法和相應的密鑰。一旦握手完成，數據傳輸開始，所有數據都使用選擇的算法和密鑰加密。

### TLS 的工作原理

Transport Layer Security (TLS) 是一個密碼學協議，旨在為計算機網絡上的通信提供安全性。它主要目標是通過密碼學，例如證書的使用，為兩個或更多通信的計算機應用程序提供安全性，包括隱私（機密性）、完整性和真實性。TLS 由兩個子層組成：TLS 記錄協議和TLS 握手協議。

#### 握手過程

當客戶端與啟用了TLS的服務器連接並請求建立安全連接時，握手過程開始。握手允許客戶端和服務器通過不對稱密碼來建立連接的安全性參數，完整流程如下：

1. **初始握手**：客戶端連接到啟用了TLS的服務器，請求安全連接，並提供它支持的密碼套件列表（加密算法和哈希函數）。
2. **選擇密碼套件**：從提供的列表中，服務器選擇它也支持的密碼套件和哈希函數，並通知客戶端已做出的決定。
3. **提供數字證書**：通常，服務器接下來會提供形式為數字證書的身份驗證。此證書包含服務器名稱、信任的證書授權機構（為證書的真實性提供擔保）以及服務器的公共加密密鑰。
4. **驗證證書**：客戶端在繼續之前確認證書的有效性。
5. **生成會話密鑰**：為了生成用於安全連接的會話密鑰，客戶端有以下兩種方法：
    - 使用服務器的公鑰加密一個隨機數（PreMasterSecret）並將結果發送到服務器（只有服務器才能使用其私鑰解密）；雙方然後使用該隨機數生成一個獨特的會話密鑰，用於會話期間的數據加密和解密。
    - 使用 Diffie-Hellman 密鑰交換（或其變體橢圓曲線DH）來安全地生成一個隨機且獨特的會話密鑰，用於加密和解密，該密鑰具有前向保密的額外屬性：即使在未來公開了服務器的私鑰，也不能用它來解密當前的會話，即使第三方攔截並記錄了會話。

一旦上述步驟成功完成，握手過程便結束，加密的連接開始。此連接使用會話密鑰進行加密和解密，直到連接關閉。如果上述任何步驟失敗，則TLS握手失敗，連接將不會建立。

#### OSI模型中的TLS

TLS 和 SSL 不完全適合 OSI 模型或 TCP/IP 模型的任何單一層次。TLS 在“某些可靠的傳輸協議（例如，TCP）之上運行”，這意味著它位於傳輸層之上。它為更高的層提供加密，這通常是表示層的功能。但是，使用TLS 的應用程序通常視其為傳輸層，即使使用TLS的應用程序必須積極控制啟動 TLS 握手和交換的認證證書的處理。

### eBPF 和 uprobe

eBPF (Extended Berkeley Packet Filter): 是一種內核技術，允許用戶在內核空間中運行預定義的程序，不需要修改內核源代碼或重新加載模塊。它創建了一個橋樑，使得用戶空間和內核空間可以交互，從而為系統監控、性能分析和網絡流量分析等任務提供了無前例的能力。

uprobes 是eBPF的一個重要特性，允許我們在用戶空間應用程序中動態地插入探測點，特別適用於跟蹤SSL/TLS庫中的函數調用。Uprobe 在內核態 eBPF 運行時，也可能產生比較大的性能開銷，這時候也可以考慮使用用戶態 eBPF 運行時，例如  [bpftime](https://github.com/eunomia-bpf/bpftime)。bpftime 是一個基於 LLVM JIT/AOT 的用戶態 eBPF 運行時，它可以在用戶態運行 eBPF 程序，和內核態的 eBPF 兼容，避免了內核態和用戶態之間的上下文切換，從而提高了 eBPF 程序的執行效率。對於 uprobe 而言，bpftime 的性能開銷比 kernel 小一個數量級。

### 用戶態庫

SSL/TLS協議的實現主要依賴於用戶態庫。以下是一些常見的庫：

- OpenSSL: 一個開源的、功能齊全的加密庫，廣泛應用於許多開源和商業項目中。
- BoringSSL: 是Google維護的OpenSSL的一個分支，重點是簡化和優化，適用於Google的需求。
- GnuTLS: 是GNU項目的一部分，提供了SSL，TLS和DTLS協議的實現。與OpenSSL和BoringSSL相比，GnuTLS在API設計、模塊結構和許可證上有所不同。

## OpenSSL API 分析

OpenSSL 是一個廣泛應用的開源庫，提供了 SSL 和 TLS 協議的完整實現，並廣泛用於各種應用程序中以確保數據傳輸的安全性。其中，SSL_read() 和 SSL_write() 是兩個核心的 API 函數，用於從 TLS/SSL 連接中讀取和寫入數據。本章節，我們將深入這兩個函數，幫助你理解其工作機制。

### 1. SSL_read 函數

當我們想從一個已建立的 SSL 連接中讀取數據時，可以使用 `SSL_read` 或 `SSL_read_ex` 函數。函數原型如下：

```c
int SSL_read_ex(SSL *ssl, void *buf, size_t num, size_t *readbytes);
int SSL_read(SSL *ssl, void *buf, int num);
```

`SSL_read` 和 `SSL_read_ex` 試圖從指定的 `ssl` 中讀取最多 `num` 字節的數據到緩衝區 `buf` 中。成功時，`SSL_read_ex` 會在 `*readbytes` 中存儲實際讀取到的字節數。

### 2. SSL_write 函數

當我們想往一個已建立的 SSL 連接中寫入數據時，可以使用 `SSL_write` 或 `SSL_write_ex` 函數。

函數原型：

```c
int SSL_write_ex(SSL *s, const void *buf, size_t num, size_t *written);
int SSL_write(SSL *ssl, const void *buf, int num);
```

`SSL_write` 和 `SSL_write_ex` 會從緩衝區 `buf` 中將最多 `num` 字節的數據寫入到指定的 `ssl` 連接中。成功時，`SSL_write_ex` 會在 `*written` 中存儲實際寫入的字節數。

## eBPF 內核態代碼編寫

在我們的例子中，我們使用 eBPF 來 hook ssl_read 和 ssl_write 函數，從而在數據讀取或寫入 SSL 連接時執行自定義操作。

### 數據結構

首先，我們定義了一個數據結構 probe_SSL_data_t 用於在內核態和用戶態之間傳輸數據：

```c
#define MAX_BUF_SIZE 8192
#define TASK_COMM_LEN 16

struct probe_SSL_data_t {
    __u64 timestamp_ns;  // 時間戳（納秒）
    __u64 delta_ns;      // 函數執行時間
    __u32 pid;           // 進程 ID
    __u32 tid;           // 線程 ID
    __u32 uid;           // 用戶 ID
    __u32 len;           // 讀/寫數據的長度
    int buf_filled;      // 緩衝區是否填充完整
    int rw;              // 讀或寫（0為讀，1為寫）
    char comm[TASK_COMM_LEN]; // 進程名
    __u8 buf[MAX_BUF_SIZE];  // 數據緩衝區
    int is_handshake;    // 是否是握手數據
};
```

### Hook 函數

我們的目標是 hook 到 `SSL_read` 和 `SSL_write` 函數。我們定義了一個函數 `SSL_exit` 來處理這兩個函數的返回值。該函數會根據當前進程和線程的 ID，確定是否需要追蹤並收集數據。

```c
static int SSL_exit(struct pt_regs *ctx, int rw) {
    int ret = 0;
    u32 zero = 0;
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 pid = pid_tgid >> 32;
    u32 tid = (u32)pid_tgid;
    u32 uid = bpf_get_current_uid_gid();
    u64 ts = bpf_ktime_get_ns();

    if (!trace_allowed(uid, pid)) {
        return 0;
    }

    /* store arg info for later lookup */
    u64 *bufp = bpf_map_lookup_elem(&bufs, &tid);
    if (bufp == 0)
        return 0;

    u64 *tsp = bpf_map_lookup_elem(&start_ns, &tid);
    if (!tsp)
        return 0;
    u64 delta_ns = ts - *tsp;

    int len = PT_REGS_RC(ctx);
    if (len <= 0)  // no data
        return 0;

    struct probe_SSL_data_t *data = bpf_map_lookup_elem(&ssl_data, &zero);
    if (!data)
        return 0;

    data->timestamp_ns = ts;
    data->delta_ns = delta_ns;
    data->pid = pid;
    data->tid = tid;
    data->uid = uid;
    data->len = (u32)len;
    data->buf_filled = 0;
    data->rw = rw;
    data->is_handshake = false;
    u32 buf_copy_size = min((size_t)MAX_BUF_SIZE, (size_t)len);

    bpf_get_current_comm(&data->comm, sizeof(data->comm));

    if (bufp != 0)
        ret = bpf_probe_read_user(&data->buf, buf_copy_size, (char *)*bufp);

    bpf_map_delete_elem(&bufs, &tid);
    bpf_map_delete_elem(&start_ns, &tid);

    if (!ret)
        data->buf_filled = 1;
    else
        buf_copy_size = 0;

    bpf_perf_event_output(ctx, &perf_SSL_events, BPF_F_CURRENT_CPU, data,
                            EVENT_SIZE(buf_copy_size));
    return 0;
}
```

這裡的 `rw` 參數標識是讀還是寫。0 代表讀，1 代表寫。

#### 數據收集流程

1. 獲取當前進程和線程的 ID，以及當前用戶的 ID。
2. 通過 `trace_allowed` 判斷是否允許追蹤該進程。
3. 獲取起始時間，以計算函數的執行時間。
4. 嘗試從 `bufs` 和 `start_ns` maps 中查找相關的數據。
5. 如果成功讀取了數據，則創建或查找 `probe_SSL_data_t` 結構來填充數據。
6. 將數據從用戶空間複製到緩衝區，並確保不超過預定的大小。
7. 最後，將數據發送到用戶空間。

注意：我們使用了兩個用戶返回探針 `uretprobe` 來分別 hook `SSL_read` 和 `SSL_write` 的返回：

```c
SEC("uretprobe/SSL_read")
int BPF_URETPROBE(probe_SSL_read_exit) {
    return (SSL_exit(ctx, 0));  // 0 表示讀操作
}

SEC("uretprobe/SSL_write")
int BPF_URETPROBE(probe_SSL_write_exit) {
    return (SSL_exit(ctx, 1));  // 1 表示寫操作
}
```

### Hook到握手過程

在 SSL/TLS 中，握手（handshake）是一個特殊的過程，用於在客戶端和服務器之間建立安全的連接。為了分析此過程，我們 hook 到了 `do_handshake` 函數，以跟蹤握手的開始和結束。

#### 進入握手

我們使用 `uprobe` 為 `do_handshake` 設置一個 probe：

```c

SEC("uprobe/do_handshake")
int BPF_UPROBE(probe_SSL_do_handshake_enter, void *ssl) {
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 pid = pid_tgid >> 32;
    u32 tid = (u32)pid_tgid;
    u64 ts = bpf_ktime_get_ns();
    u32 uid = bpf_get_current_uid_gid();

    if (!trace_allowed(uid, pid)) {
        return 0;
    }

    /* store arg info for later lookup */
    bpf_map_update_elem(&start_ns, &tid, &ts, BPF_ANY);
    return 0;
}
```

這段代碼的主要功能如下：

1. 獲取當前的 `pid`, `tid`, `ts` 和 `uid`。
2. 使用 `trace_allowed` 檢查進程是否被允許追蹤。
3. 將當前時間戳存儲在 `start_ns` 映射中，用於稍後計算握手過程的持續時間。

#### 退出握手

同樣，我們為 `do_handshake` 的返回設置了一個 `uretprobe`：

```c

SEC("uretprobe/do_handshake")
int BPF_URETPROBE(probe_SSL_do_handshake_exit) {
    u32 zero = 0;
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 pid = pid_tgid >> 32;
    u32 tid = (u32)pid_tgid;
    u32 uid = bpf_get_current_uid_gid();
    u64 ts = bpf_ktime_get_ns();
    int ret = 0;

    /* use kernel terminology here for tgid/pid: */
    u32 tgid = pid_tgid >> 32;

    /* store arg info for later lookup */
    if (!trace_allowed(tgid, pid)) {
        return 0;
    }

    u64 *tsp = bpf_map_lookup_elem(&start_ns, &tid);
    if (tsp == 0)
        return 0;

    ret = PT_REGS_RC(ctx);
    if (ret <= 0)  // handshake failed
        return 0;

    struct probe_SSL_data_t *data = bpf_map_lookup_elem(&ssl_data, &zero);
    if (!data)
        return 0;

    data->timestamp_ns = ts;
    data->delta_ns = ts - *tsp;
    data->pid = pid;
    data->tid = tid;
    data->uid = uid;
    data->len = ret;
    data->buf_filled = 0;
    data->rw = 2;
    data->is_handshake = true;
    bpf_get_current_comm(&data->comm, sizeof(data->comm));
    bpf_map_delete_elem(&start_ns, &tid);

    bpf_perf_event_output(ctx, &perf_SSL_events, BPF_F_CURRENT_CPU, data,
                            EVENT_SIZE(0));
    return 0;
}
```

此函數的邏輯如下：

1. 獲取當前的 `pid`, `tid`, `ts` 和 `uid`。
2. 使用 `trace_allowed` 再次檢查是否允許追蹤。
3. 查找 `start_ns` 映射中的時間戳，用於計算握手的持續時間。
4. 使用 `PT_REGS_RC(ctx)` 獲取 `do_handshake` 的返回值，判斷握手是否成功。
5. 查找或初始化與當前線程關聯的 `probe_SSL_data_t` 數據結構。
6. 更新數據結構的字段，包括時間戳、持續時間、進程信息等。
7. 通過 `bpf_perf_event_output` 將數據發送到用戶態。

我們的 eBPF 代碼不僅跟蹤了 `ssl_read` 和 `ssl_write` 的數據傳輸，還特別關注了 SSL/TLS 的握手過程。這些信息對於深入瞭解和優化安全連接的性能至關重要。

通過這些 hook 函數，我們可以獲得關於握手成功與否、握手所需的時間以及相關的進程信息的數據。這為我們提供了關於系統 SSL/TLS 行為的深入見解，可以幫助我們在需要時進行更深入的分析和優化。

## 用戶態輔助代碼分析與解讀

在 eBPF 的生態系統中，用戶態和內核態代碼經常協同工作。內核態代碼負責數據的採集，而用戶態代碼則負責設置、管理和處理這些數據。在本節中，我們將解讀上述用戶態代碼如何配合 eBPF 追蹤 SSL/TLS 交互。

### 1. 支持的庫掛載

上述代碼片段中，根據環境變量 `env` 的設定，程序可以選擇針對三種常見的加密庫（OpenSSL、GnuTLS 和 NSS）進行掛載。這意味著我們可以在同一個工具中對多種庫的調用進行追蹤。

為了實現這一功能，首先利用 `find_library_path` 函數確定庫的路徑。然後，根據庫的類型，調用對應的 `attach_` 函數來將 eBPF 程序掛載到庫函數上。

```c
    if (env.openssl) {
        char *openssl_path = find_library_path("libssl.so");
        printf("OpenSSL path: %s\n", openssl_path);
        attach_openssl(obj, openssl_path);
    }
    if (env.gnutls) {
        char *gnutls_path = find_library_path("libgnutls.so");
        printf("GnuTLS path: %s\n", gnutls_path);
        attach_gnutls(obj, gnutls_path);
    }
    if (env.nss) {
        char *nss_path = find_library_path("libnspr4.so");
        printf("NSS path: %s\n", nss_path);
        attach_nss(obj, nss_path);
    }
```

這裡主要包含 OpenSSL、GnuTLS 和 NSS 三個庫的掛載邏輯。NSS 是為組織設計的一套安全庫，支持創建安全的客戶端和服務器應用程序。它們最初是由 Netscape 開發的，現在由 Mozilla 維護。其他兩個庫前面已經介紹過了，這裡不再贅述。

### 2. 詳細掛載邏輯

具體的 attach 函數如下：

```c
#define __ATTACH_UPROBE(skel, binary_path, sym_name, prog_name, is_retprobe)   \
    do {                                                                       \
      LIBBPF_OPTS(bpf_uprobe_opts, uprobe_opts, .func_name = #sym_name,        \
                  .retprobe = is_retprobe);                                    \
      skel->links.prog_name = bpf_program__attach_uprobe_opts(                 \
          skel->progs.prog_name, env.pid, binary_path, 0, &uprobe_opts);       \
    } while (false)

int attach_openssl(struct sslsniff_bpf *skel, const char *lib) {
    ATTACH_UPROBE_CHECKED(skel, lib, SSL_write, probe_SSL_rw_enter);
    ATTACH_URETPROBE_CHECKED(skel, lib, SSL_write, probe_SSL_write_exit);
    ATTACH_UPROBE_CHECKED(skel, lib, SSL_read, probe_SSL_rw_enter);
    ATTACH_URETPROBE_CHECKED(skel, lib, SSL_read, probe_SSL_read_exit);

    if (env.latency && env.handshake) {
        ATTACH_UPROBE_CHECKED(skel, lib, SSL_do_handshake,
                            probe_SSL_do_handshake_enter);
        ATTACH_URETPROBE_CHECKED(skel, lib, SSL_do_handshake,
                                probe_SSL_do_handshake_exit);
    }

    return 0;
}

int attach_gnutls(struct sslsniff_bpf *skel, const char *lib) {
    ATTACH_UPROBE_CHECKED(skel, lib, gnutls_record_send, probe_SSL_rw_enter);
    ATTACH_URETPROBE_CHECKED(skel, lib, gnutls_record_send, probe_SSL_write_exit);
    ATTACH_UPROBE_CHECKED(skel, lib, gnutls_record_recv, probe_SSL_rw_enter);
    ATTACH_URETPROBE_CHECKED(skel, lib, gnutls_record_recv, probe_SSL_read_exit);

    return 0;
}

int attach_nss(struct sslsniff_bpf *skel, const char *lib) {
    ATTACH_UPROBE_CHECKED(skel, lib, PR_Write, probe_SSL_rw_enter);
    ATTACH_URETPROBE_CHECKED(skel, lib, PR_Write, probe_SSL_write_exit);
    ATTACH_UPROBE_CHECKED(skel, lib, PR_Send, probe_SSL_rw_enter);
    ATTACH_URETPROBE_CHECKED(skel, lib, PR_Send, probe_SSL_write_exit);
    ATTACH_UPROBE_CHECKED(skel, lib, PR_Read, probe_SSL_rw_enter);
    ATTACH_URETPROBE_CHECKED(skel, lib, PR_Read, probe_SSL_read_exit);
    ATTACH_UPROBE_CHECKED(skel, lib, PR_Recv, probe_SSL_rw_enter);
    ATTACH_URETPROBE_CHECKED(skel, lib, PR_Recv, probe_SSL_read_exit);

    return 0;
}
```

我們進一步觀察 `attach_` 函數，可以看到它們都使用了 `ATTACH_UPROBE_CHECKED` 和 `ATTACH_URETPROBE_CHECKED` 宏來實現具體的掛載邏輯。這兩個宏分別用於設置 uprobe（函數入口）和 uretprobe（函數返回）。

考慮到不同的庫有不同的 API 函數名稱（例如，OpenSSL 使用 `SSL_write`，而 GnuTLS 使用 `gnutls_record_send`），所以我們需要為每個庫寫一個獨立的 `attach_` 函數。

例如，在 `attach_openssl` 函數中，我們為 `SSL_write` 和 `SSL_read` 設置了 probe。如果用戶還希望追蹤握手的延遲 (`env.latency`) 和握手過程 (`env.handshake`)，那麼我們還會為 `SSL_do_handshake` 設置 probe。

在eBPF生態系統中，perf_buffer是一個用於從內核態傳輸數據到用戶態的高效機制。這對於內核態eBPF程序來說是十分有用的，因為它們不能直接與用戶態進行交互。使用perf_buffer，我們可以在內核態eBPF程序中收集數據，然後在用戶態異步地讀取這些數據。我們使用 `perf_buffer__poll` 函數來讀取內核態上報的數據，如下所示：

```c
    while (!exiting) {
        err = perf_buffer__poll(pb, PERF_POLL_TIMEOUT_MS);
        if (err < 0 && err != -EINTR) {
            warn("error polling perf buffer: %s\n", strerror(-err));
            goto cleanup;
        }
        err = 0;
    }
```

最後，在 print_event 函數中，我們將數據打印到標準輸出：

```c
// Function to print the event from the perf buffer
void print_event(struct probe_SSL_data_t *event, const char *evt) {
    ...
    if (buf_size != 0) {
        if (env.hexdump) {
            // 2 characters for each byte + null terminator
            char hex_data[MAX_BUF_SIZE * 2 + 1] = {0};
            buf_to_hex((uint8_t *)buf, buf_size, hex_data);

            printf("\n%s\n", s_mark);
            for (size_t i = 0; i < strlen(hex_data); i += 32) {
                printf("%.32s\n", hex_data + i);
            }
            printf("%s\n\n", e_mark);
        } else {
            printf("\n%s\n%s\n%s\n\n", s_mark, buf, e_mark);
        }
    }
}
```

完整的源代碼可以在這裡查看：<https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/30-sslsniff>

## 編譯與運行

關於如何安裝依賴，請參考：<https://eunomia.dev/tutorials/11-bootstrap/>

要開始使用 `sslsniff`，首先要進行編譯：

```sh
make
```

完成後，請按照以下步驟操作：

### **啟動 sslsniff**

在一個終端中，執行以下命令來啟動 `sslsniff`：

```sh
sudo ./sslsniff
```

### **執行 CURL 命令**

在另一個終端中，執行：

```console
curl https://example.com
```

正常情況下，你會看到類似以下的輸出：

```html
    <!doctype html>
    <html>
    <head>
        <title>Example Domain</title>
        ...
    <body>
    <div>
        ...
    </div>
    </body>
    </html>
```

### **sslsniff 輸出**

當執行 `curl` 命令後，`sslsniff` 會顯示以下內容：

```txt
    READ/RECV    0.132786160        curl             47458   1256
    ----- DATA -----
    <!doctype html>
    ...
    <div>
        <h1>Example Domain</h1>
        ...
    </div>
    </body>
    </html>

    ----- END DATA -----
```

**注意**：顯示的 HTML 內容可能會因 `example.com` 頁面的不同而有所不同。

### 顯示延遲和握手過程

要查看延遲和握手過程，請執行以下命令：

```console
$ sudo ./sslsniff -l --handshake
OpenSSL path: /lib/x86_64-linux-gnu/libssl.so.3
GnuTLS path: /lib/x86_64-linux-gnu/libgnutls.so.30
NSS path: /lib/x86_64-linux-gnu/libnspr4.so
FUNC         TIME(s)            COMM             PID     LEN     LAT(ms)
HANDSHAKE    0.000000000        curl             6460    1      1.384  WRITE/SEND   0.000115400        curl             6460    24     0.014
```

### 16進制輸出

要以16進制格式顯示數據，請執行以下命令：

```console
$ sudo ./sslsniff --hexdump
WRITE/SEND   0.000000000        curl             16104   24
----- DATA -----
505249202a20485454502f322e300d0a
0d0a534d0d0a0d0a
----- END DATA -----

...
```

## 總結

eBPF 是一個非常強大的技術，它可以幫助我們深入瞭解系統的工作原理。本教程是一個簡單的示例，展示瞭如何使用 eBPF 來監控 SSL/TLS 通信。如果您對 eBPF 技術感興趣，並希望進一步瞭解和實踐，可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 和教程網站 <https://eunomia.dev/zh/tutorials/>

參考資料：

- <https://github.com/iovisor/bcc/pull/4706>
- <https://github.com/openssl/openssl>
- <https://www.openssl.org/docs/man1.1.1/man3/SSL_read.html>
- <https://github.com/iovisor/bcc/blob/master/tools/sslsniff_example.txt>
- <https://en.wikipedia.org/wiki/Transport_Layer_Security>
