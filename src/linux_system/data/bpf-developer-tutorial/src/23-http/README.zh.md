# 通過 eBPF socket filter 或 syscall trace 追蹤 HTTP 請求等七層協議 - eBPF 實踐教程

在當今的技術環境中，隨著微服務、雲原生應用和複雜的分佈式系統的崛起，系統的可觀測性已成為確保其健康、性能和安全的關鍵要素。特別是在微服務架構中，應用程序的組件可能分佈在多個容器和服務器上，這使得傳統的監控方法往往難以提供足夠的深度和廣度來全面瞭解系統的行為。這就是為什麼觀測七層協議，如 HTTP、gRPC、MQTT 等，變得尤為重要。

七層協議為我們提供了關於應用程序如何與其他服務和組件交互的詳細信息。在微服務環境中，瞭解這些交互是至關重要的，因為它們經常是性能瓶頸、故障和安全問題的根源。然而，監控這些協議並不簡單。傳統的網絡監控工具，如 tcpdump，雖然在捕獲網絡流量方面非常有效，但在處理七層協議的複雜性和動態性時，它們往往顯得力不從心。

這正是 eBPF 技術發揮作用的地方。eBPF 允許開發者和運維人員深入到系統的內核層，實時觀測和分析系統的行為，而無需對應用程序代碼進行任何修改或插入埋點。這為我們提供了一個獨特的機會，可以更簡單、更高效地處理應用層流量，特別是在微服務環境中。

在本教程中，我們將深入探討以下內容：

- 追蹤七層協議，如 HTTP，以及與其相關的挑戰。
- eBPF 的 socket filter 和 syscall 追蹤：這兩種技術如何幫助我們在不同的內核層次追蹤 HTTP 網絡請求數據，以及這兩種方法的優勢和侷限性。
- eBPF 實踐教程：如何開發一個 eBPF 程序，使用 eBPF socket filter 或 syscall 追蹤來捕獲和分析 HTTP 流量

隨著網絡流量的增加和應用程序的複雜性增加，對七層協議的深入瞭解變得越來越重要。通過本教程，您將獲得必要的知識和工具，以便更有效地監控和分析您的網絡流量，從而為您的應用程序和服務器提供最佳的性能。

本文是 eBPF 開發者教程的一部分，更詳細的內容可以在這裡找到：<https://eunomia.dev/tutorials/> 源代碼在 [GitHub 倉庫](https://github.com/eunomia-bpf/bpf-developer-tutorial) 中開源。

## 追蹤 HTTP, HTTP/2 等七層協議的挑戰

在現代的網絡環境中，七層協議不僅僅侷限於 HTTP。實際上，有許多七層協議，如 HTTP/2, gRPC, MQTT, WebSocket, AMQP 和 SMTP，它們都在不同的應用場景中發揮著關鍵作用。這些協議為我們提供了關於應用程序如何與其他服務和組件交互的詳細信息。但是，追蹤這些協議並不是一個簡單的任務，尤其是在複雜的分佈式系統中。

1. **多樣性和複雜性**：每種七層協議都有其特定的設計和工作原理。例如，gRPC 使用了 HTTP/2 作為其傳輸協議，並支持多種語言。而 MQTT 是為低帶寬和不可靠的網絡設計的輕量級發佈/訂閱消息傳輸協議。

2. **動態性**：許多七層協議都是動態的，這意味著它們的行為可能會根據網絡條件、應用需求或其他因素而變化。

3. **加密和安全性**：隨著安全意識的增強，許多七層協議都採用了加密技術，如 TLS/SSL。這為追蹤和分析帶來了額外的挑戰，因為需要解密流量才能進行深入的分析。

4. **高性能需求**：在高流量的生產環境中，捕獲和分析七層協議的流量可能會對系統性能產生影響。傳統的網絡監控工具可能無法處理大量的併發會話。

5. **數據的完整性和連續性**：與 tcpdump 這樣的工具只捕獲單獨的數據包不同，追蹤七層協議需要捕獲完整的會話，這可能涉及多個數據包。這要求工具能夠正確地重組和解析這些數據包，以提供連續的會話視圖。

6. **代碼侵入性**：為了深入瞭解七層協議的行為，開發人員可能需要修改應用程序代碼以添加監控功能。這不僅增加了開發和維護的複雜性，而且可能會影響應用程序的性能。

正如上文所述，eBPF 提供了一個強大的解決方案，允許我們在內核層面捕獲和分析七層協議的流量，而無需對應用程序進行任何修改。這種方法為我們提供了一個獨特的機會，可以更簡單、更高效地處理應用層流量，特別是在微服務和分佈式環境中。

在處理網絡流量和系統行為時，選擇在內核態而非用戶態進行處理有其獨特的優勢。首先，內核態處理可以直接訪問系統資源和硬件，從而提供更高的性能和效率。其次，由於內核是操作系統的核心部分，它可以提供對系統行為的全面視圖，而不受任何用戶空間應用程序的限制。

**無插樁追蹤（"zero-instrumentation observability"）**的優勢如下：

1. **性能開銷小**：由於不需要修改或添加額外的代碼到應用程序中，所以對性能的影響最小化。
2. **透明性**：開發者和運維人員不需要知道應用程序的內部工作原理，也不需要訪問源代碼。
3. **靈活性**：可以輕鬆地在不同的環境和應用程序中部署和使用，無需進行任何特定的配置或修改。
4. **安全性**：由於不需要修改應用程序代碼，所以降低了引入潛在安全漏洞的風險。

利用 eBPF 在內核態進行無插樁追蹤，我們可以實時捕獲和分析系統的行為，而不需要對應用程序進行任何修改。這種方法不僅提供了對系統深入的洞察力，而且確保了最佳的性能和效率。這是為什麼 eBPF 成為現代可觀測性工具的首選技術，特別是在需要高性能和低延遲的生產環境中。

## eBPF 中的 socket filter 與 syscall 追蹤：深入解析與比較

### **eBPF Socket Filter**

**是什麼？**
eBPF socket filter 是經典的 Berkeley Packet Filter (BPF) 的擴展，允許在內核中直接進行更高級的數據包過濾。它在套接字層操作，使得可以精細地控制哪些數據包被用戶空間應用程序處理。

**主要特點：**

- **性能**：通過在內核中直接處理數據包，eBPF socket filters 減少了用戶和內核空間之間的上下文切換的開銷。
- **靈活性**：eBPF socket filters 可以附加到任何套接字，為各種協議和套接字類型提供了通用的數據包過濾機制。
- **可編程性**：開發者可以編寫自定義的 eBPF 程序來定義複雜的過濾邏輯，超越簡單的數據包匹配。

**用途：**

- **流量控制**：根據自定義條件限制或優先處理流量。
- **安全性**：在它們到達用戶空間應用程序之前丟棄惡意數據包。
- **監控**：捕獲特定數據包進行分析，而不影響其它流量。

### **eBPF Syscall Tracing**

**是什麼？**
使用 eBPF 進行的系統調用跟蹤允許監視和操作應用程序發出的系統調用。系統調用是用戶空間應用程序與內核交互的主要機制，因此跟蹤它們可以深入瞭解應用程序的行為。

**主要特點：**

- **粒度**：eBPF 允許跟蹤特定的系統調用，甚至是這些系統調用中的特定參數。
- **低開銷**：與其他跟蹤方法相比，eBPF 系統調用跟蹤旨在具有最小的性能影響。
- **安全性**：內核驗證 eBPF 程序，以確保它們不會損害系統穩定性。

**工作原理：**
eBPF 系統調用跟蹤通常涉及將 eBPF 程序附加到與系統調用相關的 tracepoints 或 kprobes。當跟蹤的系統調用被調用時，執行 eBPF 程序，允許收集數據或甚至修改系統調用參數。

### eBPF 的 socket filter 和 syscall 追蹤的對比

| 項目 | eBPF Socket Filter | eBPF Syscall Tracing |
|------|--------------------|----------------------|
| **操作層** | 套接字層，主要處理從套接字接收或發送的網絡數據包 | 系統調用層，監視和可能更改應用程序發出的系統調用的行為 |
| **主要用途** | 主要用於網絡數據包的過濾、監控和操作 | 用於性能分析、安全監控和系統調用交互的調試 |
| **粒度** | 專注於單個網絡數據包 | 可以監視與網絡無關的廣泛的系統活動 |
| **追蹤 HTTP 流量** | 可以用於過濾和捕獲通過套接字傳遞的 HTTP 數據包 | 可以跟蹤與網絡操作相關的系統調用 |

總之，eBPF 的 socket filter 和 syscall 追蹤都可以用於追蹤 HTTP 流量，但 socket filters 更直接且更適合此目的。然而，如果您對應用程序如何與系統交互的更廣泛的上下文感興趣（例如，哪些系統調用導致了 HTTP 流量），那麼系統調用跟蹤將是非常有價值的。在許多高級的可觀察性設置中，這兩種工具可能會同時使用，以提供系統和網絡行為的全面視圖。

## 使用 eBPF socket filter 來捕獲 HTTP 流量

eBPF 代碼由用戶態和內核態組成，這裡主要關注於內核態代碼。這是使用 eBPF socket filter 技術來在內核中捕獲HTTP流量的主要邏輯，完整代碼如下：

```c
SEC("socket")
int socket_handler(struct __sk_buff *skb)
{
    struct so_event *e;
    __u8 verlen;
    __u16 proto;
    __u32 nhoff = ETH_HLEN;
    __u32 ip_proto = 0;
    __u32 tcp_hdr_len = 0;
    __u16 tlen;
    __u32 payload_offset = 0;
    __u32 payload_length = 0;
    __u8 hdr_len;

    bpf_skb_load_bytes(skb, 12, &proto, 2);
    proto = __bpf_ntohs(proto);
    if (proto != ETH_P_IP)
        return 0;

    if (ip_is_fragment(skb, nhoff))
        return 0;

    // ip4 header lengths are variable
    // access ihl as a u8 (linux/include/linux/skbuff.h)
    bpf_skb_load_bytes(skb, ETH_HLEN, &hdr_len, sizeof(hdr_len));
    hdr_len &= 0x0f;
    hdr_len *= 4;

    /* verify hlen meets minimum size requirements */
    if (hdr_len < sizeof(struct iphdr))
    {
        return 0;
    }

    bpf_skb_load_bytes(skb, nhoff + offsetof(struct iphdr, protocol), &ip_proto, 1);

    if (ip_proto != IPPROTO_TCP)
    {
        return 0;
    }

    tcp_hdr_len = nhoff + hdr_len;
    bpf_skb_load_bytes(skb, nhoff + 0, &verlen, 1);
    bpf_skb_load_bytes(skb, nhoff + offsetof(struct iphdr, tot_len), &tlen, sizeof(tlen));

    __u8 doff;
    bpf_skb_load_bytes(skb, tcp_hdr_len + offsetof(struct __tcphdr, ack_seq) + 4, &doff, sizeof(doff)); // read the first byte past __tcphdr->ack_seq, we can't do offsetof bit fields
    doff &= 0xf0; // clean-up res1
    doff >>= 4; // move the upper 4 bits to low
    doff *= 4; // convert to bytes length

    payload_offset = ETH_HLEN + hdr_len + doff;
    payload_length = __bpf_ntohs(tlen) - hdr_len - doff;

    char line_buffer[7];
    if (payload_length < 7 || payload_offset < 0)
    {
        return 0;
    }
    bpf_skb_load_bytes(skb, payload_offset, line_buffer, 7);
    bpf_printk("%d len %d buffer: %s", payload_offset, payload_length, line_buffer);
    if (bpf_strncmp(line_buffer, 3, "GET") != 0 &&
        bpf_strncmp(line_buffer, 4, "POST") != 0 &&
        bpf_strncmp(line_buffer, 3, "PUT") != 0 &&
        bpf_strncmp(line_buffer, 6, "DELETE") != 0 &&
        bpf_strncmp(line_buffer, 4, "HTTP") != 0)
    {
        return 0;
    }

    /* reserve sample from BPF ringbuf */
    e = bpf_ringbuf_reserve(&rb, sizeof(*e), 0);
    if (!e)
        return 0;

    e->ip_proto = ip_proto;
    bpf_skb_load_bytes(skb, nhoff + hdr_len, &(e->ports), 4);
    e->pkt_type = skb->pkt_type;
    e->ifindex = skb->ifindex;

    e->payload_length = payload_length;
    bpf_skb_load_bytes(skb, payload_offset, e->payload, MAX_BUF_SIZE);

    bpf_skb_load_bytes(skb, nhoff + offsetof(struct iphdr, saddr), &(e->src_addr), 4);
    bpf_skb_load_bytes(skb, nhoff + offsetof(struct iphdr, daddr), &(e->dst_addr), 4);
    bpf_ringbuf_submit(e, 0);

    return skb->len;
}
```

當分析這段eBPF程序時，我們將按照每個代碼塊的內容來詳細解釋，並提供相關的背景知識：

```c
SEC("socket")
int socket_handler(struct __sk_buff *skb)
{
    // ...
}
```

這是eBPF程序的入口點，它定義了一個名為 `socket_handler` 的函數，它會被內核用於處理傳入的網絡數據包。這個函數位於一個名為 `socket` 的 eBPF 節（section）中，表明這個程序用於套接字處理。

```c
struct so_event *e;
__u8 verlen;
__u16 proto;
__u32 nhoff = ETH_HLEN;
__u32 ip_proto = 0;
__u32 tcp_hdr_len = 0;
__u16 tlen;
__u32 payload_offset = 0;
__u32 payload_length = 0;
__u8 hdr_len;
```

在這個代碼塊中，我們定義了一些變量來存儲在處理數據包時需要的信息。這些變量包括了`struct so_event *e`用於存儲事件信息，`verlen`、`proto`、`nhoff`、`ip_proto`、`tcp_hdr_len`、`tlen`、`payload_offset`、`payload_length`、`hdr_len`等用於存儲數據包信息的變量。

- `struct so_event *e;`：這是一個指向`so_event`結構體的指針，用於存儲捕獲到的事件信息。該結構體的具體定義在程序的其他部分。
- `__u8 verlen;`、`__u16 proto;`、`__u32 nhoff = ETH_HLEN;`：這些變量用於存儲各種信息，例如協議類型、數據包偏移量等。`nhoff`初始化為以太網幀頭部的長度，通常為14字節，因為以太網幀頭部包括目標MAC地址、源MAC地址和幀類型字段。
- `__u32 ip_proto = 0;`：這個變量用於存儲IP協議的類型，初始化為0。
- `__u32 tcp_hdr_len = 0;`：這個變量用於存儲TCP頭部的長度，初始化為0。
- `__u16 tlen;`：這個變量用於存儲IP數據包的總長度。
- `__u32 payload_offset = 0;`、`__u32 payload_length = 0;`：這兩個變量用於存儲HTTP請求的載荷（payload）的偏移量和長度。
- `__u8 hdr_len;`：這個變量用於存儲IP頭部的長度。

```c
bpf_skb_load_bytes(skb, 12, &proto, 2);
proto = __bpf_ntohs(proto);
if (proto != ETH_P_IP)
    return 0;
```

在這裡，代碼從數據包中加載了以太網幀的類型字段，這個字段告訴我們數據包使用的網絡層協議。然後，使用`__bpf_ntohs`函數將網絡字節序的類型字段轉換為主機字節序。接下來，代碼檢查類型字段是否等於IPv4的以太網幀類型（0x0800）。如果不等於，說明這個數據包不是IPv4數據包，直接返回0，放棄處理。

這裡需要了解以下幾個概念：

- 以太網幀（Ethernet Frame）：是數據鏈路層（第二層）的協議，用於在局域網中傳輸數據幀。以太網幀通常包括目標MAC地址、源MAC地址和幀類型字段。
- 網絡字節序（Network Byte Order）：網絡協議通常使用大端字節序（Big-Endian）來表示數據。因此，需要將從網絡中接收到的數據轉換為主機字節序，以便在主機上正確解釋數據。
- IPv4幀類型（ETH_P_IP）：表示以太網幀中包含的協議類型字段，0x0800表示IPv4。

```c
if (ip_is_fragment(skb, nhoff))
    return 0;
```

這一部分的代碼檢查是否處理IP分片。IP分片是將較大的IP數據包分割成多個小片段以進行傳輸的機制。在這裡，如果數據包是IP分片，則直接返回0，表示不處理分片，只處理完整的數據包。

```c
static inline int ip_is_fragment(struct __sk_buff *skb, __u32 nhoff)
{
    __u16 frag_off;

    bpf_skb_load_bytes(skb, nhoff + offsetof(struct iphdr, frag_off), &frag_off, 2);
    frag_off = __bpf_ntohs(frag_off);
    return frag_off & (IP_MF | IP_OFFSET);
}
```

上述代碼是一個輔助函數，用於檢查傳入的IPv4數據包是否為IP分片。IP分片是一種機制，當IP數據包的大小超過了網絡的最大傳輸單元（MTU），路由器會將其分割成多個較小的片段，以便在網絡上進行傳輸。這個函數的目的是檢查數據包的分片標誌（Fragmentation Flag）以及片偏移（Fragment Offset）字段，以確定是否為分片。

下面是代碼的逐行解釋：

1. `__u16 frag_off;`：定義一個16位無符號整數變量`frag_off`，用於存儲片偏移字段的值。
2. `bpf_skb_load_bytes(skb, nhoff + offsetof(struct iphdr, frag_off), &frag_off, 2);`：這行代碼使用`bpf_skb_load_bytes`函數從數據包中加載IPv4頭部的片偏移字段（`frag_off`），並加載2個字節。`nhoff`是IPv4頭部在數據包中的偏移量，`offsetof(struct iphdr, frag_off)`用於計算片偏移字段在IPv4頭部中的偏移量。
3. `frag_off = __bpf_ntohs(frag_off);`：將加載的片偏移字段從網絡字節序（Big-Endian）轉換為主機字節序。網絡協議通常使用大端字節序表示數據，而主機可能使用大端或小端字節序。這裡將片偏移字段轉換為主機字節序，以便進一步處理。
4. `return frag_off & (IP_MF | IP_OFFSET);`：這行代碼通過使用位運算檢查片偏移字段的值，以確定是否為IP分片。具體來說，它使用位與運算符`&`將片偏移字段與兩個標誌位進行位與運算：
   - `IP_MF`：表示"更多分片"標誌（More Fragments）。如果這個標誌位被設置為1，表示數據包是分片的一部分，還有更多分片。
   - `IP_OFFSET`：表示片偏移字段。如果片偏移字段不為0，表示數據包是分片的一部分，且具有片偏移值。
   如果這兩個標誌位中的任何一個被設置為1，那麼結果就不為零，說明數據包是IP分片。如果都為零，說明數據包不是分片。

需要注意的是，IP頭部的片偏移字段以8字節為單位，所以實際的片偏移值需要左移3位來得到字節偏移。此外，IP頭部的"更多分片"標誌（IP_MF）表示數據包是否有更多的分片，通常與片偏移字段一起使用來指示整個數據包的分片情況。這個函數只關心這兩個標誌位，如果其中一個標誌被設置，就認為是IP分片。

```c
bpf_skb_load_bytes(skb, ETH_HLEN, &hdr_len, sizeof(hdr_len));
hdr_len &= 0x0f;
hdr_len *= 4;
```

這一部分的代碼從數據包中加載IP頭部的長度字段。IP頭部長度字段包含了IP頭部的長度信息，以4字節為單位，需要將其轉換為字節數。這裡通過按位與和乘以4來進行轉換。

需要了解：

- IP頭部（IP Header）：IP頭部包含了關於數據包的基本信息，如源IP地址、目標IP地址、協議類型和頭部校驗和等。頭部長度字段（IHL，Header Length）表示IP頭部的長度，以4字節為單位，通常為20字節（5個4字節的字）。

```c
if (hdr_len < sizeof(struct iphdr))
{
    return 0;
}
```

這段代碼檢查IP頭部的長度是否滿足最小長度要求，通常IP頭部的最小長度是20字節。如果IP頭部的長度小於20字節，說明數據包不完整或損壞，直接返回0，放棄處理。

需要了解：

- `struct iphdr`：這是Linux內核中定義的結構體，表示IPv4頭部的格式。它包括了版本、頭部長度、服務類型、總長度、

標識符、標誌位、片偏移、生存時間、協議、頭部校驗和、源IP地址和目標IP地址等字段。

```c
bpf_skb_load_bytes(skb, nhoff + offsetof(struct iphdr, protocol), &ip_proto, 1);
if (ip_proto != IPPROTO_TCP)
{
    return 0;
}
```

在這裡，代碼從數據包中加載IP頭部中的協議字段，以確定數據包使用的傳輸層協議。然後，它檢查協議字段是否為TCP協議（IPPROTO_TCP）。如果不是TCP協議，說明不是HTTP請求或響應，直接返回0。

需要了解：

- 傳輸層協議：IP頭部中的協議字段指示了數據包所使用的傳輸層協議，例如TCP、UDP或ICMP。

```c
tcp_hdr_len = nhoff + hdr_len;
```

這行代碼計算了TCP頭部的偏移量。它將以太網幀頭部的長度（`nhoff`）與IP頭部的長度（`hdr_len`）相加，得到TCP頭部的起始位置。

```c
bpf_skb_load_bytes(skb, nhoff + 0, &verlen, 1);
```

這行代碼從數據包中加載TCP頭部的第一個字節，該字節包含了TCP頭部長度信息。這個長度字段以4字節為單位，需要進行後續的轉換。

```c
bpf_skb_load_bytes(skb, nhoff + offsetof(struct iphdr, tot_len), &tlen, sizeof(tlen));
```

這行代碼從數據包中加載IP頭部的總長度字段。IP頭部總長度字段表示整個IP數據包的長度，包括IP頭部和數據部分。

```c
__u8 doff;
bpf_skb_load_bytes(skb, tcp_hdr_len + offsetof(struct __tcphdr, ack_seq) + 4, &doff, sizeof(doff));
doff &= 0xf0;
doff >>= 4;
doff *= 4;
```

這段代碼用於計算TCP頭部的長度。它加載TCP頭部中的數據偏移字段（Data Offset，也稱為頭部長度字段），該字段表示TCP頭部的長度以4字節為單位。代碼將偏移字段的高四位清零，然後將其右移4位，最後乘以4，得到TCP頭部的實際長度。

需要了解：

- TCP頭部（TCP Header）：TCP頭部包含了TCP協議相關的信息，如源端口、目標端口、序列號、確認號、標誌位（如SYN、ACK、FIN等）、窗口大小和校驗和等。

```c
payload_offset = ETH_HLEN + hdr_len + doff;
payload_length = __bpf_ntohs(tlen) - hdr_len - doff;
```

這兩行代碼計算HTTP請求的載荷（payload）的偏移量和長度。它們將以太網幀頭部長度、IP頭部長度和TCP頭部長度相加，得到HTTP請求的數據部分的偏移量，然後通過減去總長度、IP頭部長度和TCP頭部長度，計算出HTTP請求數據的長度。

需要了解：

- HTTP請求載荷（Payload）：HTTP請求中包含的實際數據部分，通常是HTTP請求頭和請求體。

```c
char line_buffer[7];
if (payload_length < 7 || payload_offset < 0)
{
    return 0;
}
bpf_skb_load_bytes(skb, payload_offset, line_buffer, 7);
bpf_printk("%d len %d buffer: %s", payload_offset, payload_length, line_buffer);
```

這部分代碼用於加載HTTP請求行的前7個字節，存儲在名為`line_buffer`的字符數組中。然後，它檢查HTTP請求數據的長度是否小於7字節或偏移量是否為負數，如果滿足這些條件，說明HTTP請求不完整，直接返回0。最後，它使用`bpf_printk`函數將HTTP請求行的內容打印到內核日誌中，以供調試和分析。

```c
if (bpf_strncmp(line_buffer, 3, "GET") != 0 &&
    bpf_strncmp(line_buffer, 4, "POST") != 0 &&
    bpf_strncmp(line_buffer, 3, "PUT") != 0 &&
    bpf_strncmp(line_buffer, 6, "DELETE") != 0 &&
    bpf_strncmp(line_buffer, 4, "HTTP") != 0)
{
    return 0;
}
```

> 注意：bpf_strncmp 這個內核 helper 在 5.17 版本中才被引入，如果你的內核版本低於 5.17，可以手動匹配字符串來實現相同的功能。

這段代碼使用`bpf_strncmp`函數比較`line_buffer`中的數據與HTTP請求方法（GET、POST、PUT、DELETE、HTTP）是否匹配。如果不匹配，說明不是HTTP請求，直接返回0，放棄處理。

```c
e = bpf_ringbuf_reserve(&rb, sizeof(*e), 0);
if (!e)
    return 0;
```

這部分代碼嘗試從BPF環形緩衝區中保留一塊內存以存儲事件信息。如果無法保留內存塊，返回0。BPF環形緩衝區用於在eBPF程序和用戶空間之間傳遞事件數據。

需要了解：

- BPF環形緩衝區：BPF環形緩衝區是一種在eBPF程序和用戶空間之間傳遞數據的機制。它可以用來存儲事件信息，以便用戶空間應用程序進行進一步處理或分析。

```c
e->ip_proto = ip_proto;
bpf_skb_load_bytes(skb, nhoff + hdr_len, &(e->ports), 4);
e->pkt_type = skb->pkt_type;
e->ifindex = skb->ifindex;

e->payload_length = payload_length;
bpf_skb_load_bytes(skb, payload_offset, e->payload, MAX_BUF_SIZE);

bpf_skb_load_bytes(skb, nhoff + offsetof(struct iphdr, saddr), &(e->src_addr), 4);
bpf_skb_load_bytes(skb, nhoff + offsetof(struct iphdr, daddr), &(e->dst_addr), 4);
bpf_ringbuf_submit(e, 0);

return skb->len;
```

最後，這段代碼將捕獲到的事件信息存儲在`e`結構體中，並將

其提交到BPF環形緩衝區。它包括了捕獲的IP協議、源端口和目標端口、數據包類型、接口索引、載荷長度、源IP地址和目標IP地址等信息。最後，它返回數據包的長度，表示成功處理了數據包。

這段代碼主要用於將捕獲的事件信息存儲起來，以便後續的處理和分析。 BPF環形緩衝區用於將這些信息傳遞到用戶空間，供用戶空間應用程序進一步處理或記錄。

總結：這段eBPF程序的主要任務是捕獲HTTP請求，它通過解析數據包的以太網幀、IP頭部和TCP頭部來確定數據包是否包含HTTP請求，並將有關請求的信息存儲在`so_event`結構體中，然後提交到BPF環形緩衝區。這是一種高效的方法，可以在內核層面捕獲HTTP流量，適用於網絡監控和安全分析等應用。

### 潛在缺陷

上述代碼也存在一些潛在的缺陷，其中一個主要缺陷是它無法處理跨多個數據包的URL。

- 跨包URL：代碼中通過解析單個數據包來檢查HTTP請求中的URL，如果HTTP請求的URL跨足夠多的數據包，那麼只會檢查第一個數據包中的URL部分。這會導致丟失或部分記錄那些跨多個數據包的長URL。

解決這個問題的方法通常需要對多個數據包進行重新組裝，以還原完整的HTTP請求。這可能需要在eBPF程序中實現數據包的緩存和組裝邏輯，並在檢測到HTTP請求結束之前等待並收集所有相關數據包。這需要更復雜的邏輯和額外的內存來處理跨多個數據包的情況。

### 用戶態代碼

用戶態代碼的主要目的是創建一個原始套接字（raw socket），然後將先前在內核中定義的eBPF程序附加到該套接字上，從而允許eBPF程序捕獲和處理從該套接字接收到的網絡數據包,例如：

```c
    /* Create raw socket for localhost interface */
    sock = open_raw_sock(interface);
    if (sock < 0) {
        err = -2;
        fprintf(stderr, "Failed to open raw socket\n");
        goto cleanup;
    }

    /* Attach BPF program to raw socket */
    prog_fd = bpf_program__fd(skel->progs.socket_handler);
    if (setsockopt(sock, SOL_SOCKET, SO_ATTACH_BPF, &prog_fd, sizeof(prog_fd))) {
        err = -3;
        fprintf(stderr, "Failed to attach to raw socket\n");
        goto cleanup;
    }
```

1. `sock = open_raw_sock(interface);`：這行代碼調用了一個自定義的函數`open_raw_sock`，該函數用於創建一個原始套接字。原始套接字允許用戶態應用程序直接處理網絡數據包，而不經過協議棧的處理。函數`open_raw_sock`可能需要一個參數 `interface`，用於指定網絡接口，以便確定從哪個接口接收數據包。如果創建套接字失敗，它將返回一個負數，否則返回套接字的文件描述符`sock`。
2. 如果`sock`的值小於0，表示打開原始套接字失敗，那麼將`err`設置為-2，並在標準錯誤流上輸出一條錯誤信息。
3. `prog_fd = bpf_program__fd(skel->progs.socket_handler);`：這行代碼獲取之前在eBPF程序定義中的套接字過濾器程序（`socket_handler`）的文件描述符，以便後續將它附加到套接字上。`skel`是一個eBPF程序對象的指針，可以通過它來訪問程序集合。
4. `setsockopt(sock, SOL_SOCKET, SO_ATTACH_BPF, &prog_fd, sizeof(prog_fd))`：這行代碼使用`setsockopt`系統調用將eBPF程序附加到原始套接字。它設置了`SO_ATTACH_BPF`選項，將eBPF程序的文件描述符傳遞給該選項，以便內核知道要將哪個eBPF程序應用於這個套接字。如果附加成功，套接字將開始捕獲和處理從中接收到的網絡數據包。
5. 如果`setsockopt`失敗，它將`err`設置為-3，並在標準錯誤流上輸出一條錯誤信息。

### 編譯運行

完整的源代碼可以在 <https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/23-http> 中找到。關於如何安裝依賴，請參考：<https://eunomia.dev/tutorials/11-bootstrap/> 編譯運行上述代碼：

```console
$ git submodule update --init --recursive
$ make
  BPF      .output/sockfilter.bpf.o
  GEN-SKEL .output/sockfilter.skel.h
  CC       .output/sockfilter.o
  BINARY   sockfilter
$ sudo ./sockfilter 
...
```

在另外一個窗口中，使用 python 啟動一個簡單的 web server：

```console
python3 -m http.server
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
127.0.0.1 - - [18/Sep/2023 01:05:52] "GET / HTTP/1.1" 200 -
```

可以使用 curl 發起請求：

```c
$ curl http://0.0.0.0:8000/
<!DOCTYPE HTML>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Directory listing for /</title>
....
```

在 eBPF 程序中，可以看到打印出了 HTTP 請求的內容：

```console
127.0.0.1:34552(src) -> 127.0.0.1:8000(dst)
payload: GET / HTTP/1.1
Host: 0.0.0.0:8000
User-Agent: curl/7.88.1
...
127.0.0.1:8000(src) -> 127.0.0.1:34552(dst)
payload: HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.11.4
...
```

分別包含了請求和響應的內容。

## 使用 eBPF syscall tracepoint 來捕獲 HTTP 流量

eBPF 提供了一種強大的機制，允許我們在內核級別追蹤系統調用。在這個示例中，我們將使用 eBPF 追蹤 accept 和 read 系統調用，以捕獲 HTTP 流量。由於篇幅有限，這裡我們僅僅對代碼框架做簡要的介紹。

```c
struct
{
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 4096);
    __type(key, u64);
    __type(value, struct accept_args_t);
} active_accept_args_map SEC(".maps");

// 定義在 accept 系統調用入口的追蹤點
SEC("tracepoint/syscalls/sys_enter_accept")
int sys_enter_accept(struct trace_event_raw_sys_enter *ctx)
{
    u64 id = bpf_get_current_pid_tgid();
    // ... 獲取和存儲 accept 調用的參數
    bpf_map_update_elem(&active_accept_args_map, &id, &accept_args, BPF_ANY);
    return 0;
}

// 定義在 accept 系統調用退出的追蹤點
SEC("tracepoint/syscalls/sys_exit_accept")
int sys_exit_accept(struct trace_event_raw_sys_exit *ctx)
{
    // ... 處理 accept 調用的結果
    struct accept_args_t *args =
        bpf_map_lookup_elem(&active_accept_args_map, &id);
    // ... 獲取和存儲 accept 調用獲得的 socket 文件描述符
    __u64 pid_fd = ((__u64)pid << 32) | (u32)ret_fd;
    bpf_map_update_elem(&conn_info_map, &pid_fd, &conn_info, BPF_ANY);
    // ...
}

struct
{
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 4096);
    __type(key, u64);
    __type(value, struct data_args_t);
} active_read_args_map SEC(".maps");

// 定義在 read 系統調用入口的追蹤點
SEC("tracepoint/syscalls/sys_enter_read")
int sys_enter_read(struct trace_event_raw_sys_enter *ctx)
{
    // ... 獲取和存儲 read 調用的參數
    bpf_map_update_elem(&active_read_args_map, &id, &read_args, BPF_ANY);
    return 0;
}

// 輔助函數，檢查是否為 HTTP 連接
static inline bool is_http_connection(const char *line_buffer, u64 bytes_count)
{
    // ... 檢查數據是否為 HTTP 請求或響應
}

// 輔助函數，處理讀取的數據
static inline void process_data(struct trace_event_raw_sys_exit *ctx,
                                u64 id, const struct data_args_t *args, u64 bytes_count)
{
    // ... 處理讀取的數據，檢查是否為 HTTP 流量，併發送事件
    if (is_http_connection(line_buffer, bytes_count))
    {
        // ...
        bpf_probe_read_kernel(&event.msg, read_size, args->buf);
        // ...
        bpf_perf_event_output(ctx, &events, BPF_F_CURRENT_CPU,
                              &event, sizeof(struct socket_data_event_t));
    }
}

// 定義在 read 系統調用退出的追蹤點
SEC("tracepoint/syscalls/sys_exit_read")
int sys_exit_read(struct trace_event_raw_sys_exit *ctx)
{
    // ... 處理 read 調用的結果
    struct data_args_t *read_args = bpf_map_lookup_elem(&active_read_args_map, &id);
    if (read_args != NULL)
    {
        process_data(ctx, id, read_args, bytes_count);
    }
    // ...
    return 0;
}

char _license[] SEC("license") = "GPL";
```

這段代碼簡要展示瞭如何使用eBPF追蹤Linux內核中的系統調用來捕獲HTTP流量。以下是對代碼的hook位置和流程的詳細解釋，以及需要hook哪些系統調用來實現完整的請求追蹤：

### **Hook 位置和流程**

- 該代碼使用了eBPF的Tracepoint功能，具體來說，它定義了一系列的eBPF程序，並將它們綁定到了特定的系統調用的Tracepoint上，以捕獲這些系統調用的入口和退出事件。

- 首先，它定義了兩個eBPF哈希映射（`active_accept_args_map`和`active_read_args_map`）來存儲系統調用參數。這些映射用於跟蹤`accept`和`read`系統調用。

- 接著，它定義了多個Tracepoint追蹤程序，其中包括：
  - `sys_enter_accept`：定義在`accept`系統調用的入口處，用於捕獲`accept`系統調用的參數，並將它們存儲在哈希映射中。
  - `sys_exit_accept`：定義在`accept`系統調用的退出處，用於處理`accept`系統調用的結果，包括獲取和存儲新的套接字文件描述符以及建立連接的相關信息。
  - `sys_enter_read`：定義在`read`系統調用的入口處，用於捕獲`read`系統調用的參數，並將它們存儲在哈希映射中。
  - `sys_exit_read`：定義在`read`系統調用的退出處，用於處理`read`系統調用的結果，包括檢查讀取的數據是否為HTTP流量，如果是，則發送事件。

- 在`sys_exit_accept`和`sys_exit_read`中，還涉及一些數據處理和事件發送的邏輯，例如檢查數據是否為HTTP連接，組裝事件數據，並使用`bpf_perf_event_output`將事件發送到用戶空間供進一步處理。

### **需要 Hook 的完整系統調用**

要實現完整的HTTP請求追蹤，通常需要hook的系統調用包括：

- `socket`：用於捕獲套接字創建，以追蹤新的連接。
- `bind`：用於獲取綁定的端口信息。
- `listen`：用於開始監聽連接請求。
- `accept`：用於接受連接請求，獲取新的套接字文件描述符。
- `read`：用於捕獲接收到的數據，以檢查其中是否包含 HTTP 請求。
- `write`：用於捕獲發送的數據，以檢查其中是否包含 HTTP 響應。

上述代碼已經涵蓋了`accept`和`read`系統調用的追蹤。要完整實現HTTP請求的追蹤，還需要hook其他系統調用，並實現相應的邏輯來處理這些系統調用的參數和結果。

完整的源代碼可以在 <https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/23-http> 中找到。

## 總結

在當今複雜的技術環境中，系統的可觀測性變得至關重要，特別是在微服務和雲原生應用程序的背景下。本文探討了如何利用eBPF技術來追蹤七層協議，以及在這個過程中可能面臨的挑戰和解決方案。以下是對本文內容的總結：

1. **背景介紹**：
   - 現代應用程序通常由多個微服務和分佈式組件組成，因此觀測整個系統的行為至關重要。
   - 七層協議（如HTTP、gRPC、MQTT等）提供了深入瞭解應用程序交互的詳細信息，但監控這些協議通常具有挑戰性。

2. **eBPF技術的作用**：
   - eBPF允許開發者在不修改或插入應用程序代碼的情況下，深入內核層來實時觀測和分析系統行為。
   - eBPF技術為監控七層協議提供了一個強大的工具，特別適用於微服務環境。

3. **追蹤七層協議**：
   - 本文介紹瞭如何追蹤HTTP等七層協議的挑戰，包括協議的複雜性和動態性。
   - 傳統的網絡監控工具難以應對七層協議的複雜性。

4. **eBPF的應用**：
   - eBPF提供兩種主要方法來追蹤七層協議：socket filter和syscall trace。
   - 這兩種方法可以幫助捕獲HTTP等協議的網絡請求數據，並分析它們。

5. **eBPF實踐教程**：
   - 本文提供了一個實際的eBPF教程，演示如何使用eBPF socket filter或syscall trace來捕獲和分析HTTP流量。
   - 教程內容包括開發eBPF程序、使用eBPF工具鏈和實施HTTP請求的追蹤。

通過這篇文章，讀者可以獲得深入瞭解如何使用eBPF技術來追蹤七層協議，尤其是HTTP流量的知識。這將有助於更好地監控和分析網絡流量，從而提高應用程序性能和安全性。如果您希望學習更多關於 eBPF 的知識和實踐，可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/zh/tutorials/> 以獲取更多示例和完整的教程。

> 原文地址：<https://eunomia.dev/zh/tutorials/23-http/> 轉載請註明出處。
