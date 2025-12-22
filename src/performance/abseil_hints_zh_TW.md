# 效能建議 (Performance Hints)

[Jeff Dean](https://research.google/people/jeff/), [Sanjay Ghemawat](https://research.google/people/sanjayghemawat/)

原始版本：2023/07/27，最後更新：2025/12/16

展開所有細節 摺疊所有細節

多年來，我們（Jeff 與 Sanjay）對各種程式碼的效能調校（performance tuning）進行了相當深入的研究。從 Google 成立之初，提升軟體效能就一直非常重要，因為這能讓我們為更多使用者提供更多服務。我們撰寫這份文件的目的是為了歸納我們在進行這類工作時所使用的一些一般性原則與具體技術，並嘗試挑選具代表性的原始碼變更（變更列表，或稱 CL）作為各種方法與技術的範例。雖然下文中的大多數具體建議都涉及 C++ 類型與 CL，但這些一般性原則同樣適用於其他語言。本文重點在於單一二進制檔背景下的一般效能調校，不涵蓋分散式系統或機器學習（ML）硬體效能調校（這些本身就是龐大的領域）。我們希望這份文件對其他人有所幫助。

_文件中的許多範例都附帶程式碼片段以展示技術細節（點擊小三角形！）。請注意，其中部分片段提到了 Google 內部的程式碼庫抽象概念。如果我們認為這些範例具備足夠的獨立性，即使不熟悉這些抽象細節的人也能理解，我們仍會將其保留。_

## 考慮效能的重要性 (The importance of thinking about performance)

Knuth 經常被斷章取義地引用為「過早優化是萬惡之源」。[完整的引文](https://dl.acm.org/doi/pdf/10.1145/356635.356640)是：_「在約 97% 的時間裡，我們應該忘記微小的效率改善：過早優化是萬惡之源。然而，在剩下的關鍵 3% 中，我們不應錯過優化機會。」_ 這份文件討論的就是那關鍵的 3%。同樣來自 Knuth 的另一段更具說服力的話寫道：

> 從範例 2 到範例 2a 的速度提升僅約 12%，許多人會認為這微不足道。當今許多軟體工程師共有的傳統觀念是忽略微小的效率問題；但我認為這只是對他們所見到的「錙銖必較卻因小失大」程式設計師（那些無法除錯或維護其「優化」程式的人）所做行為的一種過度反應。在成熟的工程領域中，輕易獲得的 12% 改進從未被視為邊緣化；我相信同樣的觀點也應盛行於軟體工程中。當然，我不會在一併性的工作中費心進行此類優化，但當涉及到準備高品質程式時，我不希望限制自己使用那些否定此類效率工具的方法。

許多人會說「讓我們先以最簡單的方式編寫程式碼，等以後可以進行效能分析（profile）時再處理效能問題」。然而，這種方法往往是錯誤的：

  1. 如果您在開發大型系統時忽視所有效能考量，最終會得到一個「平坦的分析結果 (flat profile)」，其中沒有明顯的熱點，因為效能損耗無處不在。這將很難確定該從何處開始改進效能。
  2. 如果您正在開發一個將供他人使用的函式庫，那些遇到效能問題的人很可能無法輕易改進效能（他們必須理解他人/團隊編寫的程式碼細節，並就效能優化的重要性與之協商）。
  3. 當系統處於重度使用狀態時，更難對其進行重大變更。
  4. 也很難判斷是否存在可以輕易解決的效能問題，因此我們最終可能會採用昂貴的解決方案，例如過度複製或嚴重過度配置服務，以處理負載問題。

相反地，我們建議在編寫程式碼時，如果不會顯著影響程式碼的可讀性或複雜性，請嘗試選擇更快的替代方案。

## 估算 (Estimation)

如果您能對編寫的程式碼中效能的重要性建立直覺，就能做出更明智的決定（例如：為了效能，值得增加多少額外的複雜度）。以下是一些在編寫程式碼時估算效能的技巧：

  * **它是測試程式碼嗎？** 如果是，您主要需要擔心演算法和資料結構的漸近複雜度。（順帶一提：開發週期時間很重要，因此請避免編寫執行時間過長的測試。）
  * **它是特定於應用程式的程式碼嗎？** 如果是，請嘗試弄清楚效能對這段程式碼的重要性。這通常不難：只需區分這段程式碼是初始化/設定程式碼，還是最終會出現在熱點路徑（hot paths，例如：處理服務中的每個請求）上的程式碼即可。
  * **它是將供許多應用程式使用的函式庫程式碼嗎？** 在這種情況下，很難判斷它會變得多敏感。這時遵循本文中描述的一些簡單技術就顯得尤為重要。例如，如果您需要儲存一個通常包含少量元素的向量，請使用 `absl::InlinedVector` 而非 `std::vector`。這些技術並不難遵循，且不會為系統增加任何非局部 (non-local) 的複雜度。如果事實證明您編寫的程式碼確實消耗了大量資源，那麼它從一開始就具備更高的效能，且在查看分析結果時更容易找到下一個優化重點。

在依賴[概算 (back of the envelope calculations)](https://en.wikipedia.org/wiki/Back-of-the-envelope_calculation) 在具有潛在不同效能特性的選項之間進行選擇時，您可以進行稍微深入的分析。這類計算可以迅速提供不同方案效能的粗略估計，其結果可用於排除某些方案而無需實際實作它們。

以下是這類估算的運作方式：

  1. 估算需要多少種低階操作，例如磁碟搜尋次數、網路往返次數、傳輸的位元組數等。
  2. 將每種昂貴操作的次數乘以其粗略成本，並將結果相加。
  3. 上述過程給出了系統在資源使用方面的**成本**。如果您關心延遲（latency），且系統具有任何併發性，某些成本可能會重疊，您可能需要進行稍微複雜一點的分析來估計延遲。

下表是 [2007 年史丹佛大學演講](https://static.googleusercontent.com/media/research.google.com/en//people/jeff/stanford-295-talk.pdf)中表格的更新版本（2007 年演講的影片已不復存在，但有一個[相關的 2011 年史丹佛演講影片](https://www.youtube.com/watch?v=modXC5IWTJI)，涵蓋了部分相同內容），它列出了需要考慮的操作類型及其粗略成本，可能對您有所幫助：
```cpp 
    L1 快取參考 (L1 cache reference)                0.5 ns
    L2 快取參考 (L2 cache reference)                  3 ns
    分支預測錯誤 (Branch mispredict)                   5 ns
    Mutex 鎖定/解鎖 (無競爭情況)                      15 ns
    主記憶體參考 (Main memory reference)             50 ns
    使用 Snappy 壓縮 1K 位元組                    1,000 ns
    從 SSD 讀取 4KB                            20,000 ns
    同資料中心內的往返延遲                      50,000 ns
    從記憶體循序讀取 1MB                        64,000 ns
    透過 100 Gbps 網路讀取 1MB                100,000 ns
    從 SSD 讀取 1MB                         1,000,000 ns
    磁碟搜尋 (Disk seek)                    5,000,000 ns
    從磁碟循序讀取 1MB                     10,000,000 ns
    加州 -> 荷蘭 -> 加州 封包傳輸          150,000,000 ns
    
```

上表包含了某些基本低階操作的粗略成本。您可能還會發現追蹤與您的系統相關的高階操作估計成本很有用。例如，您可能想知道從 SQL 資料庫讀取一個點的粗略成本、與雲端服務互動的延遲，或渲染一個簡單 HTML 頁面的時間。如果您不知道不同操作的相關成本，就無法進行體面的概算！

### 範例：對十億個 4 位元組數字進行快速排序 (Quicksort) 的時間

作為粗略估計，一個良好的快速排序演算法會對大小為 N 的陣列進行 log(N) 次處理。在每次處理中，陣列內容將從記憶體串流到處理器快取中，分區程式碼會將每個元素與基準 (pivot) 元素進行一次比較。讓我們計算主要的成本：

  1. **記憶體頻寬：** 陣列佔用 4 GB（十億個數字乘以每個數字 4 位元組）。假設每個核心的記憶體頻寬約為 16GB/s。這意味著每次處理將耗時約 0.25 秒。N 約為 2^30，因此我們將進行約 30 次處理，記憶體傳輸的總成本約為 7.5 秒。
  2. **分支預測錯誤：** 我們總共會進行 N*log(N) 次比較，即約 300 億次比較。假設其中一半（即 150 億次）預測錯誤。乘以每次預測錯誤 5 ns，我們得到 75 秒的預測錯誤成本。在此分析中，我們假設正確預測的分支成本為零。
  3. **將上述數字相加：** 我們得到約 82.5 秒的估算值。

如有必要，我們可以細化分析以考慮處理器快取。根據上述分析，由於分支預測錯誤是主要成本，這種細化可能並非必需，但我們仍將其作為另一個範例包含在此。假設我們有一個 32MB 的 L3 快取，且從 L3 快取將資料傳輸到處理器的成本可以忽略不計。L3 快取可容納 2^23 個數字，因此最後 22 次處理可以在駐留在 L3 快取的資料上運行（倒數第 23 次處理將資料帶入 L3 快取，其餘處理操作該資料）。這將記憶體傳輸成本從 7.5 秒（30 次傳輸）降低到 2.5 秒（10 次以 16GB/s 傳輸 4GB）。

### 範例：生成包含 30 個圖片縮圖的網頁時間

讓我們比較兩種潛在設計，其中原始圖像儲存在磁碟上，每張圖像大小約為 1MB。

  1. **循序讀取 30 張圖像的內容並為每張圖像生成縮圖。** 每次讀取需要一次搜尋 + 一次傳輸，其中搜尋耗時 5ms，傳輸耗時 10ms，總計 30 張圖像乘以每張圖像 15ms，即 450ms。
  2. **並列讀取，假設圖像均勻分布在 K 個磁碟上。** 前述資源使用估計仍然成立，但延遲將大約降低 K 倍（忽略變異數，例如我們有時運氣不好，一個磁碟包含超過 1/K 的讀取圖像）。因此，如果在具有數百個磁碟的分散式檔案系統上運行，預期延遲將降至約 15ms。
  3. **考慮所有圖像都在單個 SSD 上的變體。** 這將循序讀取效能改為 20µs + 1ms/每張圖像，總體約為 30ms。

## 測量 (Measurement)

前一節提供了一些技巧，說明如何在不需過度擔心如何測量效能影響的情況下，在編寫程式碼時思考效能。然而，在您實際開始進行改進，或遇到涉及效能、簡潔性等多種因素的權衡之前，您會希望測量或估算潛在的效能效益。能夠有效地測量事物是您在進行效能相關工作時最重要的工具。

順帶一提，值得指出的是，對您不熟悉的程式碼進行分析也是了解程式碼庫一般結構及其運作方式的好方法。檢查程式動態呼叫圖中頻繁參與的常式的原始碼，可以讓您對執行程式碼時「發生了什麼」有一個高層次的認識，這進而能建立您在稍微不熟悉的程式碼中進行效能改進變更的信心。

### 效能分析工具與技巧

目前有許多有用的分析工具。首先可以考慮使用的是 [pprof](https://github.com/google/pprof/blob/main/doc/README.md)，因為它能提供良好的高層次效能資訊，且在本地和生產環境執行的程式碼中都易於使用。如果您想獲得更詳細的效能見解，也可以嘗試 [perf](https://perf.wiki.kernel.org/index.php/Main_Page)。

效能分析的一些技巧：

  * 使用適當的除錯資訊和優化旗標建置生產環境二進制檔。
  * 如果可以，寫一個[微基準測試](https://abseil.io/fast/75)來涵蓋您正在改進的程式碼。微基準測試可以縮短效能改進時的週轉時間，幫助驗證效能改進的影響，並有助於防止未來的效能退化。然而，微基準測試可能存在[陷阱](https://abseil.io/fast/39)，使其無法代表完整的系統效能。用於編寫微基準測試的有用的函式庫：[C++](https://github.com/google/benchmark/blob/main/README.md) [Go](https://pkg.go.dev/testing#hdr-Benchmarks) [Java](https://github.com/openjdk/jmh)。
  * 使用基準測試函式庫來[發出效能計數器讀數](https://abseil.io/fast/53)，以獲得更好的精確度並更深入地了解程式行為。

  * 鎖競爭 (Lock contention) 通常會人為地降低 CPU 使用率。某些 Mutex 實作提供了對分析鎖競爭的支援。
  * 對於機器學習效能工作，請使用 [ML 分析器](https://www.tensorflow.org/tensorboard/tensorboard_profiling_keras#debug_performance_bottlenecks)。

### 當分析結果平坦時該怎麼辦 (What to do when profiles are flat)

您經常會遇到 CPU 分析結果平坦（沒有明顯的大型效能耗損者）的情況。這通常發生在所有輕易獲得的優化 (low-hanging fruit) 都已被採摘之後。如果您發現自己處於這種情況，請考慮以下建議：

  * **不要低估許多微小優化的價值！** 在某個子系統中分別進行二十個 1% 的改進通常是非常可能的，而且集合起來意味著相當可觀的改進（這類工作通常依賴於擁有穩定且高品質的微基準測試）。這類變更的一些範例包含在「展示多種技術的變更」章節中。
  * **尋找呼叫堆疊頂部的迴圈**（CPU 分析的火焰圖視圖在此處可能很有幫助）。潛在地，迴圈或其呼叫的程式碼可以重構成更高效率的結構。某些最初透過對輸入節點和邊進行迴圈來增量建構複雜圖結構的程式碼，被改為透過傳遞整個輸入來一次性建構圖結構。這消除了初始程式碼中每條邊都會進行的一系列內部檢查。
  * **退後一步，尋找呼叫堆疊中較高層次的結構性變更**，而不是集中在微小優化上。演算法改進下列出的技術在執行此操作時可能會很有用。
  * **尋找過於通用的程式碼。** 將其替換為客製化或更低階的實作。例如，如果應用程式在簡單的前綴匹配就足夠的情況下重複使用正規表示式匹配，請考慮捨棄正規表示式的用法。
  * **嘗試減少配置數量：** [取得配置分析 (allocation profile)](https://gperftools.github.io/gperftools/heapprofile.html)，並針對配置數量最高的部分進行優化。這將產生兩個效果：(1) 直接減少在分配器（以及垃圾回收語言中的垃圾回收器）中花費的時間 (2) 通常會減少快取失誤，因為在長時間執行的程式中使用 tcmalloc 時，每個配置往往會分配到不同的快取行。
  * **收集其他類型的分析資料**，特別是基於硬體效能計數器的資料。這類分析可能會指出遇到高快取失誤率的函式。效能分析工具與技巧章節中描述的技術可能會有所幫助。

## API 考量 (API considerations)

下面建議的一些技術需要更改資料結構和函式簽名，這可能會對呼叫者造成干擾。嘗試組織程式碼，以便可以在不影響公共介面的情況下在封裝邊界內進行建議的效能改進。如果您的[模組是深層的](https://web.stanford.edu/~ouster/cgi-bin/book.php)（透過狹窄介面存取顯著功能），這將更容易實現。

廣泛使用的 API 面臨著增加功能的巨大壓力。添加新功能時要小心，因為這些功能會約束未來的實作，並為不需要新功能的使用者不必要地增加成本。例如，許多 C++ 標準函式庫容器承諾迭代器穩定性，這在典型的實作中顯著增加了配置數量，即使許多使用者並不需要指標穩定性。

下面列出了一些具體技術。請仔細考慮效能效益與這些變更引入的任何 API 可用性問題。

### 批量 API (Bulk APIs)

提供批量操作 (bulk ops) 以減少昂貴的 API 邊界跨越或利用演算法改進。

加入批量 `MemoryManager::LookupMany` 介面。

除了加入批量介面外，這也簡化了新批量變體的簽名：事實證明用戶端只需要知道是否找到了所有鍵，因此我們可以返回一個 bool 而不是 Status 物件。

memory_manager.h
```cpp 
    class MemoryManager {
     public:
      ...
      util::StatusOr<LiveTensor> Lookup(const TensorIdProto& id);
    
```
```cpp 
    class MemoryManager {
     public:
      ...
      util::StatusOr<LiveTensor> Lookup(const TensorIdProto& id);
    
      // 查詢識別出的 Tensor
      struct LookupKey {
        ClientHandle client;
        uint64 local_id;
      };
      bool LookupMany(absl::Span<const LookupKey> keys,
                      absl::Span<tensorflow::Tensor> tensors);
    
```

加入批量 `ObjectStore::DeleteRefs` API 以攤銷鎖定開銷。

object_store.h
```cpp 
    template <typename T>
    class ObjectStore {
     public:
      ...
      absl::Status DeleteRef(Ref);
    
```
```cpp 
    template <typename T>
    class ObjectStore {
     public:
      ...
      absl::Status DeleteRef(Ref);
    
      // 刪除多個引用。對於每個引用，如果沒有其他引用指向同一個
      // 物件，則該物件將被刪除。發生任何錯誤時返回非 OK。
      absl::Status DeleteRefs(absl::Span<const Ref> refs);
      ...
    template <typename T>
    absl::Status ObjectStore<T>::DeleteRefs(absl::Span<const Ref> refs) {
      util::Status result;
      absl::MutexLock l(&mu_);
      for (auto ref : refs) {
        result.Update(DeleteRefLocked(ref));
      }
      return result;
    }
    
```

memory_tracking.cc
```cpp 
    void HandleBatch(int, const plaque::Batch& input) override {
      for (const auto& t : input) {
        auto in = In(t);
        PLAQUE_OP_ASSIGN_OR_RETURN(const auto& handles, in.handles());
        for (const auto handle : handles.value->handles()) {
          PLAQUE_OP_RETURN_IF_ERROR(in_buffer_store_
                                        ? bstore_->DeleteRef(handle)
                                        : tstore_->DeleteRef(handle));
        }
      }
    }
    
```
```cpp 
    void HandleBatch(int, const plaque::Batch& input) override {
      for (const auto& t : input) {
        auto in = In(t);
        PLAQUE_OP_ASSIGN_OR_RETURN(const auto& handles, in.handles());
        if (in_buffer_store_) {
          PLAQUE_OP_RETURN_IF_ERROR(
              bstore_->DeleteRefs(handles.value->handles()));
        } else {
          PLAQUE_OP_RETURN_IF_ERROR(
              tstore_->DeleteRefs(handles.value->handles()));
        }
      }
    }
    
```

使用 [Floyd 的堆積構建法](https://en.wikipedia.org/wiki/Heapsort#Variations) 進行高效率初始化。

堆積的批量初始化可以在 O(N) 時間內完成，而每次添加一個元素並在每次添加後更新堆積屬性則需要 O(N lg(N)) 時間。

有時很難直接更改呼叫者以使用新的批量 API。在這種情況下，在內部使用批量 API 並快取結果以用於未來的非批量 API 呼叫可能會很有益：

快取區塊解碼結果以供未來呼叫使用。

每次查詢需要解碼整個包含 K 個項目的區塊。將解碼後的項目儲存在快取中，並在未來的查詢中諮詢快取。

lexicon.cc
```cpp 
    void GetTokenString(int pos, std::string* out) const {
      ...
      absl::FixedArray<LexiconEntry, 32> entries(pos + 1);
    
      // 解碼直到並包括 pos 的所有詞典項目。
      for (int i = 0; i <= pos; ++i) {
        p = util::coding::TwoValuesVarint::Decode32(p, &entries[i].remaining,
                                                    &entries[i].shared);
        entries[i].remaining_str = p;
        p += entries[i].remaining;  // 剩餘位元組跟隨每個項目。
      }
    
```
```cpp 
    mutable std::vector<absl::InlinedVector<std::string, 16>> cache_;
    ...
    void GetTokenString(int pos, std::string* out) const {
      ...
      DCHECK_LT(skentry, cache_.size());
      if (!cache_[skentry].empty()) {
        *out = cache_[skentry][pos];
        return;
      }
      ...
      // 初始化快取。
      ...
      const char* prev = p;
      for (int i = 0; i < block_sz; ++i) {
        uint32 shared, remaining;
        p = TwoValuesVarint::Decode32(p, &remaining, &shared);
        auto& cur = cache_[skentry].emplace_back();
        gtl::STLStringResizeUninitialized(&cur, remaining + shared);
    
        std::memcpy(cur.data(), prev, shared);
        std::memcpy(cur.data() + shared, p, remaining);
        prev = cur.data();
        p += remaining;
      }
      *out = cache_[skentry][pos];
    
```

### 視圖類型 (View types)

優先使用視圖類型（例如 `std::string_view`, `std::Span<T>`, `absl::FunctionRef<R(Args...)>`）作為函式引數（除非涉及所有權轉移）。這些類型能減少複製，並允許呼叫者選擇自己的容器類型（例如：一個呼叫者可能使用 `std::vector`，而另一個使用 `absl::InlinedVector`）。

### 預先分配/預先計算的引數 (Pre-allocated/pre-computed arguments)

對於頻繁呼叫的常式，有時允許較高層次的呼叫者傳入他們擁有的資料結構，或被呼叫常式需要但客戶端已經擁有的資訊是很有用的。這可以避免低階常式被迫配置自己的臨時資料結構或重新計算已經可用的資訊。

加入 `RPC_Stats::RecordRPC` 變體，允許用戶端傳入已經可用的 `WallTime` 值。

rpc-stats.h
```cpp 
    static void RecordRPC(const Name &name, const RPC_Stats_Measurement& m);
    
```
```cpp 
    static void RecordRPC(const Name &name, const RPC_Stats_Measurement& m,
                          WallTime now);
    
```

clientchannel.cc
```cpp 
    const WallTime now = WallTime_Now();
    ...
    RPC_Stats::RecordRPC(stats_name, m);
    
```
```cpp 
    const WallTime now = WallTime_Now();
    ...
    RPC_Stats::RecordRPC(stats_name, m, now);
    
```

### 執行緒相容 vs. 執行緒安全類型 (Thread-compatible vs. Thread-safe types)

類型可以是執行緒相容的（外部同步）或執行緒安全的（內部同步）。大多數通用類型應設計為執行緒相容。這樣不需要執行緒安全性的呼叫者就不必為此付費。

使類別成為執行緒相容，因為呼叫者已經同步。

hitless-transfer-phase.cc
```cpp 
    TransferPhase HitlessTransferPhase::get() const {
      static CallsiteMetrics cm("HitlessTransferPhase::get");
      MonitoredMutexLock l(&cm, &mutex_);
      return phase_;
    }
    
```
```cpp 
    TransferPhase HitlessTransferPhase::get() const { return phase_; }
    
```

hitless-transfer-phase.cc
```cpp 
    bool HitlessTransferPhase::AllowAllocate() const {
      static CallsiteMetrics cm("HitlessTransferPhase::AllowAllocate");
      MonitoredMutexLock l(&cm, &mutex_);
      return phase_ == TransferPhase::kNormal || phase_ == TransferPhase::kBrownout;
    }
    
```
```cpp 
    bool HitlessTransferPhase::AllowAllocate() const {
      return phase_ == TransferPhase::kNormal || phase_ == TransferPhase::kBrownout;
    }
    
```

然而，如果類型的典型用途需要同步，則優先將同步移到類型內部。這允許根據需要調整同步機制以提高效能（例如：透過分片減少競爭），而不會影響呼叫者。

## 演算法改進 (Algorithmic improvements)

效能改進最關鍵的機會來自演算法改進，例如將 O(N²) 演算法轉為 O(N lg(N)) 或 O(N)，避免潛在的指數行為等。這些機會在穩定的程式碼中很少見，但在編寫新程式碼時值得注意。以下是一些對既有程式碼進行此類改進的範例：

以反向後序 (reverse post-order) 添加節點至循環檢測結構。

我們之前是逐個將圖節點和邊添加到循環檢測資料結構中，這需要對每條邊進行昂貴的工作。我們現在以反向後序添加整個圖，這使得循環檢測變得微道。

graphcycles.h
```cpp 
    class GraphCycles : public util_graph::Graph {
     public:
      GraphCycles();
      ~GraphCycles() override;
    
      using Node = util_graph::Node;
    
```
```cpp 
    class GraphCycles : public util_graph::Graph {
     public:
      GraphCycles();
      ~GraphCycles() override;
    
      using Node = util_graph::Node;
    
      // InitFrom 從 src 添加所有節點和邊，成功則返回 true，
      // 如果遇到循環則返回 false。
      // 要求：尚未向 GraphCycles 添加任何節點和邊。
      bool InitFrom(const util_graph::Graph& src);
    
```

graphcycles.cc
```cpp 
    bool GraphCycles::InitFrom(const util_graph::Graph& src) {
      ...
      // 以拓撲順序分配排名，這樣我們在初始化期間就不需要任何重新排序。
      // 對於無環圖，DFS 以反向拓撲順序離開節點，因此我們在離開節點時分配遞減的排名。
      Rank last_rank = n;
      auto leave = [&](util_graph::Node node) {
        DCHECK(r->rank[node] == kMissingNodeRank);
        NodeInfo* nn = &r->nodes[node];
        nn->in = kNil;
        nn->out = kNil;
        r->rank[node] = --last_rank;
      };
      util_graph::DFSAll(src, std::nullopt, leave);
    
      // 添加所有邊（在過程中檢測循環）。
      bool have_cycle = false;
      util_graph::PerEdge(src, [&](util_graph::Edge e) {
        DCHECK_NE(r->rank[e.src], kMissingNodeRank);
        DCHECK_NE(r->rank[e.dst], kMissingNodeRank);
        if (r->rank[e.src] >= r->rank[e.dst]) {
          have_cycle = true;
        } else if (!HasEdge(e.src, e.dst)) {
          EdgeListAddNode(r, &r->nodes[e.src].out, e.dst);
          EdgeListAddNode(r, &r->nodes[e.dst].in, e.src);
        }
      });
      if (have_cycle) {
        return false;
      } else {
        DCHECK(CheckInvariants());
        return true;
      }
    }
    
```

graph_partitioner.cc
```cpp 
    absl::Status MergeGraph::Init() {
      const Graph& graph = *compiler_->graph();
      clusters_.resize(graph.NodeLimit());
      graph.PerNode([&](Node node) {
        graph_->AddNode(node);
        NodeList* n = new NodeList;
        n->push_back(node);
        clusters_[node] = n;
      });
      absl::Status s;
      PerEdge(graph, [&](Edge e) {
        if (!s.ok()) return;
        if (graph_->HasEdge(e.src, e.dst)) return;  // 已添加
        if (!graph_->InsertEdge(e.src, e.dst)) {
          s = absl::InvalidArgumentError("原始圖中存在循環");
        }
      });
      return s;
    }
    
```
      return s;
    }
    
```
```cpp 
    absl::Status MergeGraph::Init() {
      const Graph& graph = *compiler_->graph();
      if (!graph_->InitFrom(graph)) {
        return absl::InvalidArgumentError("原始圖中存在循環");
      }
      clusters_.resize(graph.NodeLimit());
      graph.PerNode([&](Node node) {
        NodeList* n = new NodeList;
        n->push_back(node);
        clusters_[node] = n;
      });
      return absl::OkStatus();
    }
    
```

以更好的演算法替換內建在 Mutex 實作中的死結檢測系統。

將死結檢測演算法替換為速度約快 50 倍且可輕鬆擴展至數百萬個 Mutex 的演算法（舊演算法依賴 2K 限制以避免效能懸崖）。新程式碼基於以下論文：A dynamic topological sort algorithm for directed acyclic graphs David J. Pearce, Paul H. J. Kelly Journal of Experimental Algorithmics (JEA) JEA Homepage archive Volume 11, 2006, Article No. 1.7

新演算法佔用 O(|V|+|E|) 空間（而不是舊演算法所需的 O(|V|^2) 位元）。鎖獲取順序圖非常稀疏，因此這節省了大量空間。該演算法也非常簡單：核心部分約為 100 行 C++。由於程式碼現在可以擴展到更大數量的 Mutex，我們能夠放寬人為的 2K 限制，這揭露了實際程式中許多潛在的死結。

基準測試結果：這些是在 DEBUG 模式下執行的，因為死結檢測主要在除錯模式下啟用。基準測試參數 (/2k 等) 是追蹤節點的數量。在舊演算法預設的 2k 限制下，新演算法每次 InsertEdge 僅需 0.5 微秒，而舊演算法則需 22 微秒。新演算法還能輕鬆擴展到更大的圖，而舊演算法則會迅速崩潰。
```cpp 
    DEBUG: Benchmark            Time(ns)    CPU(ns) Iterations
    ----------------------------------------------------------
    DEBUG: BM_StressTest/2k        23553      23566      29086
    DEBUG: BM_StressTest/4k        45879      45909      15287
    DEBUG: BM_StressTest/16k      776938     777472        817
    
```
```cpp 
    DEBUG: BM_StressTest/2k          392        393   10485760
    DEBUG: BM_StressTest/4k          392        393   10485760
    DEBUG: BM_StressTest/32k         407        407   10485760
    DEBUG: BM_StressTest/256k        456        456   10485760
    DEBUG: BM_StressTest/1M          534        534   10485760
    
```

使用雜湊表 (O(1) 查詢) 取代 `IntervalMap` (具有 O(lg N) 查詢)。

初始程式碼使用 `IntervalMap` 是因為它看起來是支援相鄰區塊合併的正確資料結構，但雜湊表就足夠了，因為相鄰區塊可以透過雜湊表查詢找到。這（加上 CL 中的其他變更）使 `tpu::BestFitAllocator` 的效能提高了約 4 倍。

best_fit_allocator.h
```cpp 
    using Block = gtl::IntervalMap<int64, BlockState>::Entry;
    ...
    // 對於覆蓋範圍 [0, allocatable_range_end_) 的每個配置，都有一個 (地址範圍, BlockState) 對的映射項目。
    // 相鄰的 kFree 和 kReserved 區塊會被合併。相鄰的 kAllocated 區塊則不會被合併。
    gtl::IntervalMap<int64, BlockState> block_list_;
    
    // 所有根據配置策略排序的空閒區塊集合。相鄰的空閒區塊會被合併。
    std::set<Block, BlockSelector> free_list_;
    
```
```cpp 
    // 用於 BlockTable 中偏移量的更快雜湊函式
    struct OffsetHash {
      ABSL_ATTRIBUTE_ALWAYS_INLINE size_t operator()(int64 value) const {
        uint64 m = value;
        m *= uint64_t{0x9ddfea08eb382d69};
        return static_cast<uint64_t>(m ^ (m >> 32));
      }
    };
    
    // 雜湊表從區塊起始位址映射到區塊資訊。
    // 我們在此資訊中包含前一個區塊的長度，以便我們可以找到前導區塊進行合併。
    struct HashTableEntry {
      BlockState state;
      int64 my_length;
      int64 prev_length;  // 如果沒有前一個區塊則為零。
    };
    using BlockTable = absl::flat_hash_map<int64, HashTableEntry, OffsetHash>;
    
```

使用雜湊表查詢 (O(N)) 取代排序列表交集 (O(N log N))。

舊程式碼偵測兩個節點是否共享共同來源時，會以排序順序取得每個節點的來源，然後執行排序交集。新程式碼將一個節點的來源放在雜湊表中，然後迭代另一個節點的來源並檢查雜湊表。
```cpp 
    名稱 (name)        舊時間 (old time/op)  新時間 (new time/op)  差異 (delta)
    BM_CompileLarge        28.5s ± 2%            22.4s ± 2%        -21.61%  (p=0.008 n=5+5)
    
```

實作良好的雜湊函式，使複雜度為 O(1) 而非 O(N)。

location.h
```cpp 
    // Location 物件的雜湊器。
    struct LocationHash {
      size_t operator()(const Location* key) const {
        return key != nullptr ? util_hash::Hash(key->address()) : 0;
      }
    };
    
```
```cpp 
    size_t HashLocation(const Location& loc);
    ...
    struct LocationHash {
      size_t operator()(const Location* key) const {
        return key != nullptr ? HashLocation(*key) : 0;
      }
    };
    
```

location.cc
```cpp 
    size_t HashLocation(const Location& loc) {
      util_hash::MurmurCat m;
    
      // 將一些較簡單的特徵編碼成單一數值。
      m.AppendAligned((loc.dynamic() ? 1 : 0)                    //
                      | (loc.append_shard_to_address() ? 2 : 0)  //
                      | (loc.is_any() ? 4 : 0)                   //
                      | (!loc.any_of().empty() ? 8 : 0)          //
                      | (loc.has_shardmap() ? 16 : 0)            //
                      | (loc.has_sharding() ? 32 : 0));
    
      if (loc.has_shardmap()) {
        m.AppendAligned(loc.shardmap().output() |
                        static_cast<uint64_t>(loc.shardmap().stmt()) << 20);
      }
      if (loc.has_sharding()) {
        uint64_t num = 0;
        switch (loc.sharding().type_case()) {
          case Sharding::kModShard:
            num = loc.sharding().mod_shard();
            break;
          case Sharding::kRangeSplit:
            num = loc.sharding().range_split();
            break;
          case Sharding::kNumShards:
            num = loc.sharding().num_shards();
            break;
          default:
            num = 0;
            break;
        }
        m.AppendAligned(static_cast<uint64_t>(loc.sharding().type_case()) |
                        (num << 3));
      }
    
      auto add_string = [&m](absl::string_view s) {
        if (!s.empty()) {
          m.Append(s.data(), s.size());
        }
      };
    
      add_string(loc.address());
      add_string(loc.lb_policy());
    
      // 我們不包含 any_of，因為計算一個對順序和重複不敏感的雜湊值很複雜。
      return m.GetHash();
    }
    
```

## 更好的記憶體表示 (Better memory representation)

仔細考慮重要資料結構的記憶體佔用和快取佔用通常可以產生巨大的節省。下面的資料結構側重於透過觸及更少的快取行來支援常見操作。在這裡花費心思可以 (a) 避免昂貴的快取失誤 (b) 減少記憶體匯流排流量，這不僅能加速當前程式，也能加速同一機器上運行的任何其他程式。它們依賴於一些您在設計自己的資料結構時可能會發現有用的常用技術。

### 精簡資料結構 (Compact data structures)

對於會被頻繁存取或佔用應用程式大部分記憶體使用的資料，使用精簡表示。精簡表示可以透過觸及更少的快取行和減少記憶體匯流排頻寬使用來顯著減少記憶體使用並提高效能。然而，要小心快取行競爭。

### 記憶體佈局 (Memory layout)

仔細考慮具有大量記憶體或快取足跡的類型的記憶體佈局。

  * 重新排序欄位以減少具有不同對齊要求的欄位之間的填補 (padding)（參見 [類別佈局討論](https://stackoverflow.com/questions/9989164/optimizing-memory-layout-of-class-instances-in-c)）。
  * 在儲存的資料符合較小類型時，使用較小的數值類型。
  * 除非您很小心，否則列舉值有時會佔用整個字 (word)。考慮使用較小的表示形式（例如：使用 `enum class OpType : uint8_t { ... }` 而不是 `enum class OpType { ... }`）。
  * 排序欄位，使經常一起存取的欄位彼此靠近——這將減少常見操作中觸及的快取行數量。
  * 將熱門 (hot) 的唯讀欄位與熱門的可變欄位分開，以免對可變欄位的寫入導致唯讀欄位從附近的快取中被驅逐。
  * 移動冷資料，使其不與熱資料相鄰，可以將冷資料放在結構體的末尾，或放在間接層 (indirection) 之後，或者放在單獨的陣列中。
  * 考慮透過使用位元 (bit) 和位元組級編碼將內容打包進更少的位元組中。這可能很複雜，因此僅當所討論的資料封裝在經過良好測試的模組內，且記憶體使用的總體減少顯著時才這樣做。此外，要注意副作用，例如頻繁使用的資料對齊不足，或者存取打包表示形式的程式碼更昂貴。使用基準測試驗證此類變更。

### 索引取代指標 (Indices instead of pointers)

在現代 64 位元機器上，指標佔用 64 位元。如果您有一個指標豐富的資料結構，您很容易因為大量的 `T*` 引用而耗盡記憶體。相反地，考慮使用指向陣列 `T[]` 或其他資料結構的整數索引。不僅引用會變小（如果索引數量少到可以用 32 位元或更少的位元表示），而且所有 `T[]` 元素的儲存將是連續的，這通常會導致更好的快取局部性。

### 批量儲存 (Batched storage)

避免為每個儲存元素配置單獨物件的資料結構（例如 C++ 中的 `std::map`、`std::unordered_map`）。相反地，考慮使用分塊 (chunked) 或平坦 (flat) 表示形式將多個元素儲存在記憶體中相近位置的類型（例如 C++ 中的 `std::vector`、`absl::flat_hash_{map,set}`）。這類類型往往具有更好的快取行為。此外，它們遇到的分配器開銷較少。

一種有用的技術是將元素分區為塊 (chunks)，其中每個塊可以容納固定數量的元素。這種技術可以在保持良好漸近行為的同時顯著減少資料結構的快取足跡。

對於某些資料結構，單個塊就足以容納所有元素（例如字串和向量）。其他類型（例如 `absl::flat_hash_map`）也使用這種技術。

### 內聯儲存 (Inlined storage)

某些容器類型針對儲存少量元素進行了優化。這些類型在最上層為少量元素提供空間，並在元素數量較少時完全避免配置。當這類類型的實例經常被建構（例如：作為頻繁執行程式碼中的堆疊變數），或者如果同時存在許多實例時，這會非常有幫助。如果一個容器通常包含少量元素，請考慮使用內聯儲存類型之一，例如 `InlinedVector`。

警告：如果 `sizeof(T)` 很大，內聯儲存容器可能不是最佳選擇，因為內聯的備份儲存會很大。

### 不必要的嵌套 Map (Unnecessarily nested maps)

有時，嵌套 Map 資料結構可以用具有複合鍵的單層 Map 替換。這可以顯著降低查詢和插入的成本。

透過將 `btree<a,btree<b,c>>` 轉換為 `btree<pair<a,b>,c>` 來減少配置並改善快取足跡。

graph_splitter.cc
```cpp 
    absl::btree_map<std::string, absl::btree_map<std::string, OpDef>> ops;
    
```
```cpp 
    // 此 btree 從 {package_name, op_name} 映射到其 const Opdef*。
    absl::btree_map<std::pair<absl::string_view, absl::string_view>,
                    const OpDef*>
        ops;
    
```

警告：如果第一個 Map 的鍵很大，堅持使用嵌套 Map 可能會更好：

切換到嵌套 Map 使微基準測試的效能提高了 76%。

我們之前有一個單層雜湊表，其鍵由（字串）路徑和一些其他數值子鍵組成。平均每個路徑出現在大約 1000 個鍵中。我們將雜湊表拆分為兩層，第一層以路徑為鍵，每個第二層雜湊表僅保留特定路徑的子鍵到資料的映射。這使儲存路徑的記憶體使用量減少了 1000 倍，並且還加速了對同一路徑的多個子鍵一起存取的情況。

### Arena (競技場)

Arena 可以幫助減少記憶體配置成本，但它們還有另一個好處，就是將獨立配置的項目打包在一起，通常位於更少的快取行中，並消除了大部分析構 (destruction) 成本。它們對於具有許多子物件的複雜資料結構可能最有效。考慮為 Arena 提供適當的初始大小，因為這有助於減少配置。

警告：很容易誤用 Arena，將太多短效物件放入長效 Arena 中，這可能會不必要地膨脹記憶體足跡。

### 陣列取代 Map (Arrays instead of maps)

如果 Map 的定義域可以用小整數表示或者是列舉，或者如果 Map 的元素非常少，那麼 Map 有時可以用陣列或某種形式的向量替換。

使用陣列取代 `flat_map`。

rtp_controller.h
```cpp 
    const gtl::flat_map<int, int> payload_type_to_clock_frequency_;
    
```
```cpp 
    // 一個由 payload_type 索引到該 payload 類型的時鐘頻率（或 0）的映射（實作為簡單陣列）
    struct PayloadTypeToClockRateMap {
      int map[128];
    };
    ...
    const PayloadTypeToClockRateMap payload_type_to_clock_frequency_;
    
```

### 位元向量取代 Set (Bit vectors instead of sets)

如果 Set 的定義域可以用小整數表示，則可以用位元向量（`InlinedBitVector` 通常是不錯的選擇）替換 Set. 使用位元布林運算（聯集用 OR，交集用 AND 等），這些表示形式上的 Set 操作也可以非常高效。

Spanner 放置系統。使用每個區域一位元的位元向量取代 `dense_hash_set<ZoneId>`。

zone_set.h
```cpp 
    class ZoneSet: public dense_hash_set<ZoneId> {
     public:
      ...
      bool Contains(ZoneId zone) const {
        return count(zone) > 0;
      }
    
```
```cpp 
    class ZoneSet {
      ...
      // 若且唯若 "zone" 包含在集合中時返回 true
      bool ContainsZone(ZoneId zone) const {
        return zone < b_.size() && b_.get_bit(zone);
      }
      ...
     private:
      int size_;          // 插入的區域數量
      util::bitmap::InlinedBitVector<256> b_;
    
```

基準測試結果：
```cpp 
    CPU: AMD Opteron (4 cores) dL1:64KB dL2:1024KB
    基準測試 (Benchmark)              基準 (Base) (ns)  新 (New) (ns) 改進 (Improvement)
    ------------------------------------------------------------------
    BM_Evaluate/1                            960       676    +29.6%
    BM_Evaluate/2                           1661      1138    +31.5%
    BM_Evaluate/3                           2305      1640    +28.9%
    BM_Evaluate/4                           3053      2135    +30.1%
    BM_Evaluate/5                           3780      2665    +29.5%
    BM_Evaluate/10                          7819      5739    +26.6%
    BM_Evaluate/20                         17922     12338    +31.2%
    BM_Evaluate/40                         36836     26430    +28.2%
    
```

使用位元矩陣來追蹤運算元之間的通達性 (reachability)屬性，而不是使用雜湊表。

hlo_computation.h
```cpp 
    using TransitiveOperandMap =
        std::unordered_map<const HloInstruction*,
                           std::unordered_set<const HloInstruction*>>;
    
```
```cpp 
    class HloComputation::ReachabilityMap {
      ...
      // 從 HloInstruction* 到數值的密集 ID 分配
      tensorflow::gtl::FlatMap<const HloInstruction*, int> ids_;
      // matrix_(a,b) 為 true 若且唯若 b 可從 a 到達時
      tensorflow::core::Bitmap matrix_;
    };
    
```

## 減少配置 (Reduce allocations)

記憶體配置會增加成本：

  1. 它增加了在分配器中花費的時間。
  2. 新配置的物件可能需要昂貴的初始化，有時在不再需要時還需要相應的昂貴析構。
  3. 每個配置往往位於新的快取行上，因此分散在許多獨立配置中的資料會比分散在較少配置中的資料具有更大的快取足跡。

垃圾回收執行環境有時透過在記憶體中連續放置連續的配置來避免問題 #3。

### 避免不必要的配置 (Avoid unnecessary allocations)

減少配置使基準測試吞吐量提高 21%。

memory_manager.cc
```cpp 
    LiveTensor::LiveTensor(tf::Tensor t, std::shared_ptr<const DeviceInfo> dinfo,
                           bool is_batched)
        : tensor(std::move(t)),
          device_info(dinfo ? std::move(dinfo) : std::make_shared<DeviceInfo>()),
          is_batched(is_batched) {
    
```
```cpp 
    static const std::shared_ptr<DeviceInfo>& empty_device_info() {
      static std::shared_ptr<DeviceInfo>* result =
          new std::shared_ptr<DeviceInfo>(new DeviceInfo);
      return *result;
    }
    
    LiveTensor::LiveTensor(tf::Tensor t, std::shared_ptr<const DeviceInfo> dinfo,
                           bool is_batched)
        : tensor(std::move(t)), is_batched(is_batched) {
      if (dinfo) {
        device_info = std::move(dinfo);
      } else {
        device_info = empty_device_info();
      }
    
```

盡可能使用靜態配置的零向量，而不是配置一個向量並用零填充。

embedding_executor_8bit.cc
```cpp 
    // 使用模板參數而非物件成員來提高效能的 EmbeddingLookUpT 實際實作。
    template <bool Mean, bool SymmetricInputRange>
    static tensorflow::Status EmbeddingLookUpT(...) {
        ...
      std::unique_ptr<tensorflow::quint8[]> zero_data(
          new tensorflow::quint8[max_embedding_width]);
      memset(zero_data.get(), 0, sizeof(tensorflow::quint8) * max_embedding_width);
    
```
```cpp 
    // 足以處理大多數嵌入寬度的大小
    static const int kTypicalMaxEmbedding = 256;
    static tensorflow::quint8 static_zero_data[kTypicalMaxEmbedding];  // 全為零
    ...
    // 使用模板參數而非物件成員來提高效能的 EmbeddingLookUpT 實際實作。
    template <bool Mean, bool SymmetricInputRange>
    static tensorflow::Status EmbeddingLookUpT(...) {
        ...
      std::unique_ptr<tensorflow::quint8[]> zero_data_backing(nullptr);
    
      // 取得指向至少具有 "max_embedding_width" 個 quint8 零值的記憶體區域的指標。
      tensorflow::quint8* zero_data;
      if (max_embedding_width <= ARRAYSIZE(static_zero_data)) {
        // static_zero_data 足夠大，因此我們不需要配置零資料
        zero_data = &static_zero_data[0];
      } else {
        // static_zero_data 不夠大：我們需要配置零資料
        zero_data_backing =
            absl::make_unique<tensorflow::quint8[]>(max_embedding_width);
        memset(zero_data_backing.get(), 0,
               sizeof(tensorflow::quint8) * max_embedding_width);
        zero_data = zero_data_backing.get();
      }
    
```

此外，當物件生命週期受作用域 (scope) 限制時，優先使用堆疊 (stack) 分配而非堆 (heap) 分配（儘管對於大型物件要注意堆疊框架的大小）。

### 調整容器大小或預留空間 (Resize or reserve containers)

當預先知道向量（或其他某些容器類型）的最大或預期最大大小時，請預先設定容器的備份儲存大小（例如：在 C++ 中使用 `resize` 或 `reserve`）。

預先調整向量大小並填充它，而不是進行 N 次 `push_back` 操作。

indexblockdecoder.cc
```cpp 
    for (int i = 0; i < ndocs-1; i++) {
      uint32 delta;
      ERRORCHECK(b->GetRice(rice_base, &delta));
      docs_.push_back(DocId(my_shard_ + (base + delta) * num_shards_));
      base = base + delta + 1;
    }
    docs_.push_back(last_docid_);
    
```
```cpp 
    docs_.resize(ndocs);
    DocId* docptr = &docs_[0];
    for (int i = 0; i < ndocs-1; i++) {
      uint32 delta;
      ERRORCHECK(b.GetRice(rice_base, &delta));
      *docptr = DocId(my_shard_ + (base + delta) * num_shards_);
      docptr++;
      base = base + delta + 1;
    }
    *docptr = last_docid_;
    
```

警告：不要使用 `resize` 或 `reserve` 每次增加一個元素，因為這可能導致二次方 (quadratic) 行為。此外，如果元素建構很昂貴，優先使用初始 `reserve` 呼叫後接多次 `push_back` 或 `emplace_back` 呼叫，而不是初始 `resize`，因為後者會使建構子呼叫次數翻倍。

### 盡可能避免複製 (Avoid copying when possible)

  * 盡可能優先選擇移動 (moving) 而非複製資料結構。
  * 如果生命週期不是問題，在暫時性資料結構中儲存指標或索引，而非物件的副本。例如，如果使用局部 Map 從傳入的 Proto 列表中選擇一組 Proto，我們可以使 Map 僅儲存指向傳入 Proto 的指標，而不是複製可能深層嵌套的資料。另一個常見範例是排序索引向量，而不是直接排序大型物件向量，因為後者會產生顯著的複製/移動成本。

避免在透過 gRPC 接收 Tensor 時產生額外的複製。

一個傳送大約 400KB Tensor 的基準測試速度提升了約 10-15%：
```cpp 
    基準測試 (Benchmark)    時間 (Time) (ns)    CPU (ns)  迭代次數 (Iterations)
    -----------------------------------------------------
    BM_RPC/30/98k_mean    148764691 1369998944       1000
    
```
```cpp 
    基準測試 (Benchmark)    時間 (Time) (ns)    CPU (ns)  迭代次數 (Iterations)
    -----------------------------------------------------
    BM_RPC/30/98k_mean    131595940 1216998084       1000
    
```

移動大型選項結構而不是複製它。

index.cc
```cpp 
    return search_iterators::DocPLIteratorFactory::Create(opts);
    
```
```cpp 
    return search_iterators::DocPLIteratorFactory::Create(std::move(opts));
    
```

使用 `std::sort` 取代 `std::stable_sort`，這避免了 `stable_sort` 實作內部的內部複製。

encoded-vector-hits.h
```cpp 
    std::stable_sort(hits_.begin(), hits_.end(),
                     gtl::OrderByField(&HitWithPayloadOffset::docid));
    
```
```cpp 
    struct HitWithPayloadOffset {
      search_iterators::LocalDocId64 docid;
      int first_payload_offset;  // 負載向量的偏移量。
      int num_payloads;
    
      bool operator<(const HitWithPayloadOffset& other) const {
        return (docid < other.docid) ||
               (docid == other.docid &&
                first_payload_offset < other.first_payload_offset);
      }
    };
        ...
        std::sort(hits_.begin(), hits_.end());
    
```

### 重用臨時物件 (Reuse temporary objects)

在迴圈內部宣告的容器或物件將在每次迴圈迭代時重新建立。這可能導致昂貴的建構、析構和調整大小。將宣告提升 (hoisting) 到迴圈之外可以實現重用，並能顯著提升效能。（編譯器通常由於語言語意或無法確保程式等效性而無法自行執行此類提升。）

將變數定義提升到迴圈迭代之外。

autofdo_profile_utils.h
```cpp 
    auto iterator = absl::WrapUnique(sstable->GetIterator());
    while (!iterator->done()) {
      T profile;
      if (!profile.ParseFromString(iterator->value_view())) {
        return absl::InternalError(
            "解析 mem_block 到指定的 profile 類型失敗。");
      }
      ...
      iterator->Next();
    }
    
```
```cpp 
    auto iterator = absl::WrapUnique(sstable->GetIterator());
    T profile;
    while (!iterator->done()) {
      if (!profile.ParseFromString(iterator->value_view())) {
        return absl::InternalError(
            "解析 mem_block 到指定的 profile 類型失敗。");
      }
      ...
      iterator->Next();
    }
    
```

在迴圈外定義 Protobuf 變數，以便其分配的儲存空間可以在迴圈迭代之間重用。

stats-router.cc
```cpp 
    for (auto& r : routers_to_update) {
      ...
      ResourceRecord record;
      {
        MutexLock agg_lock(r.agg->mutex());
        r.agg->AddResourceRecordUsages(measure_indices, &record);
      }
      ...
    }
    
```
```cpp 
    ResourceRecord record;
    for (auto& r : routers_to_update) {
      ...
      record.Clear();
      {
        MutexLock agg_lock(r.agg->mutex());
        r.agg->AddResourceRecordUsages(measure_indices, &record);
      }
      ...
    }
    
```

重複序列化到同一個 `std::string`。

program_rep.cc
```cpp 
    std::string DeterministicSerialization(const proto2::Message& m) {
      std::string result;
      proto2::io::StringOutputStream sink(&result);
      proto2::io::CodedOutputStream out(&sink);
      out.SetSerializationDeterministic(true);
      m.SerializePartialToCodedStream(&out);
      return result;
    }
    
```
```cpp 
    absl::string_view DeterministicSerializationTo(const proto2::Message& m,
                                                   std::string* scratch) {
      scratch->clear();
      proto2::io::StringOutputStream sink(scratch);
      proto2::io::CodedOutputStream out(&sink);
      out.SetSerializationDeterministic(true);
      m.SerializePartialToCodedStream(&out);
      return absl::string_view(*scratch);
    }
    
```

警告：Protobuf、字串、向量、容器等往往會增長到其中儲存過的最大值的大小。因此，定期（例如：每使用 N 次後）重新建構它們有助於減少記憶體需求和重新初始化成本。

## 避免不必要的工作 (Avoid unnecessary work)

改進效能最有效的類別之一或許就是避免您不必做的工作。這可以採取多種形式，包括為常見情況建立專用的程式碼路徑以避免更通用的昂貴計算、預先計算、將工作推遲到真正需要時、將工作提升到執行頻率較低的程式碼段中，以及其他類似的方法。以下是這種一般方法的許多範例，分為幾個具代表性的類別。

### 常見情況的快速路徑 (Fast paths for common cases)

通常，程式碼被編寫為涵蓋所有情況，但某些情況子集比其他情況更簡單且更常見。例如，`vector::push_back` 通常有足夠的空間放置新元素，但在沒有空間時包含調整底層儲存大小的程式碼。對程式碼結構的一些關注可以幫助使常見的簡單情況更快，而不會顯著損害非常見情況的效能。

使快速路徑涵蓋更多常見情況。

加入對末尾單個 ASCII 位元組的處理，而不是僅在此常式中處理四位元組的倍數。這避免了對全 ASCII 字串（例如：5 位元組）呼叫較慢的通用常式。

utf8statetable.cc
```cpp 
    // 根據狀態表掃描 UTF-8 stringpiece。
    // 始終掃描完整的 UTF-8 字元。
    // 設定掃描的位元組數。返回退出的原因。
    // 針對 7 位元 ASCII 0000..007f 全都有效的情況進行優化。
    int UTF8GenericScanFastAscii(const UTF8ScanObj* st, absl::string_view str,
                                 int* bytes_consumed) {
                                 ...
      int exit_reason;
      do {
        // 一次跳過 8 位元組 ASCII；沒有字節序問題。
        while ((src_limit - src >= 8) &&
               (((UNALIGNED_LOAD32(src + 0) | UNALIGNED_LOAD32(src + 4)) &
                 0x80808080) == 0)) {
          src += 8;
        }
        // 對其餘部分執行狀態表。
        int rest_consumed;
        exit_reason = UTF8GenericScan(
            st, absl::ClippedSubstr(str, src - initial_src), &rest_consumed);
        src += rest_consumed;
      } while (exit_reason == kExitDoAgain);
    
      *bytes_consumed = src - initial_src;
      return exit_reason;
    }
    
```
```cpp 
    // 根據狀態表掃描 UTF-8 stringpiece。
    // 始終掃描完整的 UTF-8 字元。
    // 設定掃詢的位元組數。返回退出的原因。
    // 針對 7 位元 ASCII 0000..007f 全都有效的情況進行優化。
    int UTF8GenericScanFastAscii(const UTF8ScanObj* st, absl::string_view str,
                                 int* bytes_consumed) {
                                 ...
      int exit_reason = kExitOK;
      do {
        // 一次跳過 8 位元組 ASCII；沒有字節序問題。
        while ((src_limit - src >= 8) &&
               (((UNALIGNED_LOAD32(src + 0) | UNALIGNED_LOAD32(src + 4)) &
                 0x80808080) == 0)) {
          src += 8;
        }
        while (src < src_limit && Is7BitAscii(*src)) { // 跳過 ASCII 位元組。
          src++;
        }
        if (src < src_limit) {
          // 對其餘部分執行狀態表。
          int rest_consumed;
          exit_reason = UTF8GenericScan(
              st, absl::ClippedSubstr(str, src - initial_src), &rest_consumed);
          src += rest_consumed;
        }
      } while (exit_reason == kExitDoAgain);
    
      *bytes_consumed = src - initial_src;
      return exit_reason;
    }
    
```

`InlinedVector` 的更簡單快速路徑。

inlined_vector.h
```cpp 
    auto Storage<T, N, A>::Resize(ValueAdapter values, size_type new_size) -> void {
      StorageView storage_view = MakeStorageView();
    
      IteratorValueAdapter<MoveIterator> move_values( 
          MoveIterator(storage_view.data));
    
      AllocationTransaction allocation_tx(GetAllocPtr());
      ConstructionTransaction construction_tx(GetAllocPtr());
    
      absl::Span<value_type> construct_loop;
      absl::Span<value_type> move_construct_loop;
      absl::Span<value_type> destroy_loop;
    
      if (new_size > storage_view.capacity) {
      ...
      } else if (new_size > storage_view.size) {
        construct_loop = {storage_view.data + storage_view.size,
                          new_size - storage_view.size};
      } else {
        destroy_loop = {storage_view.data + new_size, storage_view.size - new_size};
      }
    
```
```cpp 
    auto Storage<T, N, A>::Resize(ValueAdapter values, size_type new_size) -> void {
      StorageView storage_view = MakeStorageView();
      auto* const base = storage_view.data;
      const size_type size = storage_view.size;
      auto* alloc = GetAllocPtr();
      if (new_size <= size) {
        // 銷毀多餘的舊元素。
        inlined_vector_internal::DestroyElements(alloc, base + new_size,
                                                 size - new_size);
      } else if (new_size <= storage_view.capacity) {
        // 在原位建構新元素。
        inlined_vector_internal::ConstructElements(alloc, base + size, &values,
                                                   new_size - size);
      } else {
      ...
      }
    
```

初始化 1-D 到 4-D Tensor 常見情況的快速路徑。

tensor_shape.cc
```cpp 
    template <class Shape>
    TensorShapeBase<Shape>::TensorShapeBase(gtl::ArraySlice<int64> dim_sizes) {
      set_tag(REP16);
      set_data_type(DT_INVALID);
      set_ndims_byte(0);
      set_num_elements(1);
      for (int64 s : dim_sizes) {
        AddDim(internal::SubtleMustCopy(s));
      }
    }
    
```
```cpp 
    template <class Shape>
    void TensorShapeBase<Shape>::InitDims(gtl::ArraySlice<int64> dim_sizes) {
      DCHECK_EQ(tag(), REP16);
    
      // 允許小於 kint64max^0.25 的大小，以便下面的四路乘法不會溢出。
      static const uint64 kMaxSmall = 0xd744;
      static_assert(kMaxSmall * kMaxSmall * kMaxSmall * kMaxSmall <= kint64max,
                    "bad overflow check");
      bool large_size = false;
      for (auto s : dim_sizes) {
        if (s > kMaxSmall) {
          large_size = true;
          break;
        }
      }
    
      if (!large_size) {
        // 每個大小都符合 16 位元；對維度在 {1,2,3,4} 內的情況使用快速路徑。
        uint16* dst = as16()->dims_;
        switch (dim_sizes.size()) {
          case 1: {
            set_ndims_byte(1);
            const int64 size = dim_sizes[0];
            const bool neg = Set16(kIsPartial, dst, 0, size);
            set_num_elements(neg ? -1 : size);
            return;
          }
          case 2: {
            set_ndims_byte(2);
            const int64 size0 = dim_sizes[0];
            const int64 size1 = dim_sizes[1];
            bool neg = Set16(kIsPartial, dst, 0, size0);
            neg |= Set16(kIsPartial, dst, 1, size1);
            set_num_elements(neg ? -1 : (size0 * size1));
            return;
          }
          case 3: {
          ...
          }
          case 4: {
          ...
          }
        }
      }
    
      set_ndims_byte(0);
      set_num_elements(1);
      for (int64 s : dim_sizes) {
        AddDim(internal::SubtleMustCopy(s));
      }
    }
    
```

使 Varint 解析器快速路徑僅涵蓋 1 位元組情況，而不是涵蓋 1 位元組和 2 位元組情況。

減小（內聯）快速路徑的大小可以減少程式碼大小和 icache 壓力，從而提高效能。

parse_context.h
```cpp 
    template <typename T>
    PROTOBUF_NODISCARD const char* VarintParse(const char* p, T* out) {
      auto ptr = reinterpret_cast<const uint8_t*>(p);
      uint32_t res = ptr[0];
      if (!(res & 0x80)) {
        *out = res;
        return p + 1;
      }
      uint32_t byte = ptr[1];
      res += (byte - 1) << 7;
      if (!(byte & 0x80)) {
        *out = res;
        return p + 2;
      }
      return VarintParseSlow(p, res, out);
    }
    
```
```cpp 
    template <typename T>
    PROTOBUF_NODISCARD const char* VarintParse(const char* p, T* out) {
      auto ptr = reinterpret_cast<const uint8_t*>(p);
      uint32_t res = ptr[0];
      if (!(res & 0x80)) {
        *out = res;
        return p + 1;
      }
      return VarintParseSlow(p, res, out);
    }
    
```

parse_context.cc
```cpp 
    std::pair<const char*, uint32_t> VarintParseSlow32(const char* p,
                                                       uint32_t res) {
      for (std::uint32_t i = 2; i < 5; i++) {
      ...
    }
    ...
    std::pair<const char*, uint64_t> VarintParseSlow64(const char* p,
                                                       uint32_t res32) {
      uint64_t res = res32;
      for (std::uint32_t i = 2; i < 10; i++) {
      ...
    }
    
```
```cpp 
    std::pair<const char*, uint32_t> VarintParseSlow32(const char* p,
                                                       uint32_t res) {
      for (std::uint32_t i = 1; i < 5; i++) {
      ...
    }
    ...
    std::pair<const char*, uint64_t> VarintParseSlow64(const char* p,
                                                       uint32_t res32) {
      uint64_t res = res32;
      for (std::uint32_t i = 1; i < 10; i++) {
      ...
    }
    
```

如果沒有發生錯誤，則在 `RPC_Stats_Measurement` 加法中跳過顯著工作。

rpc-stats.h
```cpp 
    struct RPC_Stats_Measurement {
      ...
      double errors[RPC::NUM_ERRORS];
    
```
```cpp 
    struct RPC_Stats_Measurement {
      ...
      double get_errors(int index) const { return errors[index]; }
      void set_errors(int index, double value) {
        errors[index] = value;
        any_errors_set = true;
      }
     private:
      ...
      // 我們將此設為私有，以便我們能追蹤這些值中是否有任何一個
      // 被設定為非零值。
      double errors[RPC::NUM_ERRORS];
      bool any_errors_set;  // 若且唯若 errors[i] 值中任一個為非零時為 true。
    
```

rpc-stats.cc
```cpp 
    void RPC_Stats_Measurement::operator+=(const RPC_Stats_Measurement& x) {
      ...
      for (int i = 0; i < RPC::NUM_ERRORS; ++i) {
        errors[i] += x.errors[i];
      }
    }
    
```
```cpp 
    void RPC_Stats_Measurement::operator+=(const RPC_Stats_Measurement& x) {
      ...
      if (x.any_errors_set) {
        for (int i = 0; i < RPC::NUM_ERRORS; ++i) {
          errors[i] += x.errors[i];
        }
        any_errors_set = true;
      }
    }
    
```

對字串的第一個位元組執行陣列查詢，以便通常避免對整個字串進行指紋識別 (fingerprinting)。

soft-tokens-helper.cc
```cpp 
    bool SoftTokensHelper::IsSoftToken(const StringPiece& token) const {
      return soft_tokens_.find(Fingerprint(token.data(), token.size())) !=
          soft_tokens_.end();
    }
    
```

soft-tokens-helper.h
```cpp 
    class SoftTokensHelper {
     ...
     private:
      ...
      // 由於軟 Token (soft tokens) 大多與標點符號相關，為了效能目的，
      // 我們保留一個陣列 filter_。filter_[i] 為 true 若且唯若任何
      // 軟 Token 以位元組值 'i' 開頭。這在常見情況下避免了對術語進行指紋識別，
      // 因為我們只需基於第一個位元組進行陣列查詢，如果 filter_[b] 為 false，
      // 則我們可以立即返回 false。
      bool          filter_[256];
      ...
    };
    
    inline bool SoftTokensHelper::IsSoftToken(const StringPiece& token) const {
      if (token.size() >= 1) {
        char first_char = token.data()[0];
        if (!filter_[first_char]) {
          return false;
        }
      }
      return IsSoftTokenFallback(token);
    }
    
```

soft-tokens-helper.cc
```cpp 
    bool SoftTokensHelper::IsSoftTokenFallback(const StringPiece& token) const {
      return soft_tokens_.find(Fingerprint(token.data(), token.size())) !=
          soft_tokens_.end();
    }
    
```

### 預先計算昂貴資訊一次 (Precompute expensive information once)

預先計算 TensorFlow 圖執行節點屬性，使我們能夠快速排除某些異常情況。

executor.cc
```cpp 
    struct NodeItem {
      ...
      bool kernel_is_expensive = false;  // 若且唯若 kernel->IsExpensive() 時為 true
      bool kernel_is_async = false;      // 若且唯若 kernel->AsAsync() != nullptr 時為 true
      bool is_merge = false;             // 若且唯若 IsMerge(node) 時為 true
      ...
      if (IsEnter(node)) {
      ...
      } else if (IsExit(node)) {
      ...
      } else if (IsNextIteration(node)) {
      ...
      } else {
        // 大多數節點的正常路徑
        ...
      }
    
```
```cpp 
    struct NodeItem {
      ...
      bool kernel_is_expensive : 1;  // 若且唯若 kernel->IsExpensive() 時為 true
      bool kernel_is_async : 1;      // 若且唯若 kernel->AsAsync() != nullptr 時為 true
      bool is_merge : 1;             // 若且唯若 IsMerge(node) 時為 true
      bool is_enter : 1;             // 若且唯若 IsEnter(node) 時為 true
      bool is_exit : 1;              // 若且唯若 IsExit(node) 時為 true
      bool is_control_trigger : 1;   // 若且唯若 IsControlTrigger(node) 時為 true
      bool is_sink : 1;              // 若且唯若 IsSink(node) 時為 true
      // 若且唯若 IsEnter(node) || IsExit(node) || IsNextIteration(node) 時為 true
      bool is_enter_exit_or_next_iter : 1;
      ...
      if (!item->is_enter_exit_or_next_iter) {
        // 不需要特殊處理的節點類型的快速路徑
        DCHECK_EQ(input_frame, output_frame);
        ...
      } else if (item->is_enter) {
      ...
      } else if (item->is_exit) {
      ...
      } else {
        DCHECK(IsNextIteration(node));
        ...
      }
    
```

預先計算 256 個元素的陣列，並在 Trigram 初始化期間使用。

byte_trigram_classifier.cc
```cpp 
    void ByteTrigramClassifier::VerifyModel(void) const {
      ProbT class_sums[num_classes_];
      for (int cls = 0; cls < num_classes_; cls++) {
        class_sums[cls] = 0;
      }
      for (ByteNgramId id = 0; id < trigrams_.num_trigrams(); id++) {
        for (int cls = 0; cls < num_classes_; ++cls) {
          class_sums[cls] += Prob(trigram_probs_[id].log_probs[cls]);
        }
      }
      ...
    }                         
    
```
```cpp 
    void ByteTrigramClassifier::VerifyModel(void) const {
      CHECK_EQ(sizeof(ByteLogProbT), 1);
      ProbT fast_prob[256];
      for (int b = 0; b < 256; b++) {
        fast_prob[b] = Prob(static_cast<ByteLogProbT>(b));
      }
    
      ProbT class_sums[num_classes_];
      for (int cls = 0; cls < num_classes_; cls++) {
        class_sums[cls] = 0;
      }
      for (ByteNgramId id = 0; id < trigrams_.num_trigrams(); id++) {
        for (int cls = 0; cls < num_classes_; ++cls) {
          class_sums[cls] += fast_prob[trigram_probs_[id].log_probs[cls]];
        }
      }
      ...
    }                         
    
```

一般建議：在模組邊界檢查格式錯誤的輸入，而不是在內部重複檢查。

### 將昂貴計算移出迴圈 (Move expensive computations outside loops)

將邊界計算移出迴圈。

literal_linearizer.cc
```cpp 
    for (int64 i = 0; i < src_shape.dimensions(dimension_numbers.front());
         ++i) {
    
```
```cpp 
    int64 dim_front = src_shape.dimensions(dimension_numbers.front());
    const uint8* src_buffer_data = src_buffer.data();
    uint8* dst_buffer_data = dst_buffer.data();
    for (int64 i = 0; i < dim_front; ++i) {
    
```

### 推遲昂貴計算 (Defer expensive computation)

推遲 `GetSubSharding` 呼叫直到需要時，這將 43 秒的 CPU 時間減少到 2 秒。

sharding_propagation.cc
```cpp 
    HloSharding alternative_sub_sharding =
        user.sharding().GetSubSharding(user.shape(), {i});
    if (user.operand(i) == &instruction &&
        hlo_sharding_util::IsShardingMoreSpecific(alternative_sub_sharding,
                                                  sub_sharding)) {
      sub_sharding = alternative_sub_sharding;
    }
    
```
```cpp 
    if (user.operand(i) == &instruction) {
      // 僅在對此運算元感興趣時才評估 GetSubSharding，因為它相對昂貴。
      HloSharding alternative_sub_sharding =
          user.sharding().GetSubSharding(user.shape(), {i});
      if (hlo_sharding_util::IsShardingMoreSpecific(
              alternative_sub_sharding, sub_sharding)) {
        sub_sharding = alternative_sub_sharding;
      }
    }
    
```

不要主動更新統計資訊；按需計算。

不要在非常頻繁的配置/解除配置呼叫中更新統計資訊。相反地，當呼叫頻率低得多的 `Stats()` 方法被調用時，再按需計算統計資訊。

在 Google Web 伺服器中預先分配 10 個節點而非 200 個節點來處理查詢。

一個簡單的更改使 Web 伺服器的 CPU 使用率降低了 7.5%。

querytree.h
```cpp 
    static const int kInitParseTreeSize = 200;   // 查詢節點池的初始大小
    
```
```cpp 
    static const int kInitParseTreeSize = 10;   // 查詢節點池的初始大小
    
```

更改搜尋順序使吞吐量提高 19%。

一個舊的搜尋系統（約 2000 年）有兩個層級：一個包含全文索引，另一個層級僅包含標題和錨點術語的索引。我們以前常先搜尋較小的標題/錨點層級。與直覺相反，我們發現先搜尋較大的全文索引層級成本更低，因為如果我們到達全文層級的末尾，我們可以完全跳過搜尋標題/錨點層級（全文層級的子集）。這種情況經常發生，並使我們能夠減少處理查詢的平均磁碟搜尋次數。

有關背景資訊，請參見 [The Anatomy of a Large-Scale Hypertextual Web Search Engine](https://research.google/pubs/the-anatomy-of-a-large-scale-hypertextual-web-search-engine/) 中關於標題和錨點文本處理的討論。

### 特化程式碼 (Specialize code)

特定的效能敏感呼叫點可能不需要通用函式庫提供的完整通用性。在這種情況下，如果特化程式碼能提供效能提升，請考慮編寫特化程式碼而非呼叫通用程式碼。

`Histogram` 類別的自訂列印程式碼速度是 `sprintf` 的 4 倍。

這段程式碼對效能很敏感，因為當監控系統從各種伺服器收集統計資訊時會呼叫它。

histogram_export.cc
```cpp 
    void Histogram::PopulateBuckets(const string &prefix,
                                    expvar::MapProto *const var) const {
                                    ...
      for (int i = min_bucket; i <= max_bucket; ++i) {
        const double count = BucketCount(i);
        if (!export_empty_buckets && count == 0.0) continue;
        acc += count;
        // 離散直方圖導出儲存桶的標籤格式指定一個包含性上限，
        // 這與原始 Histogram 實作中的相同。此格式不適用於
        // 非離散直方圖，因此對它們使用半開區間，
        // 並使用 "_" 代替 "-" 作為分隔符號，以區分格式。
        string key =
            options_.export_cumulative_counts() ?
                StringPrintf("%.12g", boundaries_->BucketLimit(i)) :
            options_.discrete() ?
                StringPrintf("%.0f-%.0f",
                             ceil(boundaries_->BucketStart(i)),
                             ceil(boundaries_->BucketLimit(i)) - 1.0) :
                StringPrintf("%.12g_%.12g",
                             boundaries_->BucketStart(i),
                             boundaries_->BucketLimit(i));
        EscapeMapKey(&key);
        const double value = options_.export_cumulative_counts() ? acc : count;
        expvar::AddMapFloat(StrCat(prefix,
                                   options_.export_bucket_key_prefix(),
                                   key),
                            value * count_mult,
                            var);
      }
    
```
```cpp 
    // 根據格式格式化 "val"。如果 "need_escape" 為 true，則該格式可能產生
    // 帶有 '.' 的輸出，結果將被轉義。如果 "need_escape" 為 false，則呼叫者
    // 保證格式使得產生的數字不會有任何 '.' 字元，因此我們可以避免呼叫 EscapeKey。
    // 函式可以根據需要自由使用 "*scratch" 作為暫存空間，產生的 StringPiece
    // 可能指向 "*scratch"。
    static StringPiece FormatNumber(const char* format,
                                    bool need_escape,
                                    double val, string* scratch) {
      // 此常式專門用於僅處理有限數量的格式
      DCHECK(StringPiece(format) == "%.0f" || StringPiece(format) == "%.12g");
    
      scratch->clear();
      if (val == trunc(val) && val >= kint32min && val <= kint32max) {
        // 一個我們可以直接使用 StrAppend 的整數
        StrAppend(scratch, static_cast<int32>(val));
        return StringPiece(*scratch);
      } else if (isinf(val)) {
        // 無窮大，表示為 'inf'。
        return StringPiece("inf", 3);
      } else {
        // 根據 "format" 格式化，並可能轉義。
        StringAppendF(scratch, format, val);
        if (need_escape) {
          EscapeMapKey(scratch);
        } else {
          DCHECK(!StringPiece(*scratch).contains("."));
        }
        return StringPiece(*scratch);
      }
    }
    ...
    void Histogram::PopulateBuckets(const string &prefix,
                                    expvar::MapProto *const var) const {
                                    ...
      const string full_key_prefix = StrCat(prefix,
                                            options_.export_bucket_key_prefix());
      string key = full_key_prefix;  // 鍵將以 "full_key_prefix" 開頭。
      string start_scratch;
      string limit_scratch;
      const bool cumul_counts = options_.export_cumulative_counts();
      const bool discrete = options_.discrete();
      for (int i = min_bucket; i <= max_bucket; ++i) {
        const double count = BucketCount(i);
        if (!export_empty_buckets && count == 0.0) continue;
        acc += count;
        // 離散直方圖導出儲存桶的標籤格式指定一個包含性上限，
        // 這與原始 Histogram 實作中的相同。此格式不適用於
        // 非離散直方圖，因此對它們使用半開區間，
        // 並使用 "_" 代替 "-" 作為分隔符號，以區分格式。
        key.resize(full_key_prefix.size());  // 以 full_key_prefix 開頭。
        DCHECK_EQ(key, full_key_prefix);
    
        const double limit = boundaries_->BucketLimit(i);
        if (cumul_counts) {
          StrAppend(&key, FormatNumber("%.12g", true, limit, &limit_scratch));
        } else {
          const double start = boundaries_->BucketStart(i);
          if (discrete) {
            StrAppend(&key,
                      FormatNumber("%.0f", false, ceil(start), &start_scratch),
                      "-",
                      FormatNumber("%.0f", false, ceil(limit) - 1.0,
                                   &limit_scratch));
          } else {
            StrAppend(&key,
                      FormatNumber("%.12g", true, start, &start_scratch),
                      "_",
                      FormatNumber("%.12g", true, limit, &limit_scratch));
          }
        }
        const double value = cumul_counts ? acc : count;
    
        // 添加到 Map var
        expvar::AddMapFloat(key, value * count_mult, var);
      }
    }
    
```

加入對 `VLOG(1)`, `VLOG(2)`, … 的特化，以提高速度並縮小程式碼大小。

`VLOG` 是整個程式碼庫中頻繁使用的巨集。此更改避免了在幾乎每個呼叫點傳遞額外的整數常數（如果呼叫點的日誌級別是常數，就像在 `VLOG(1) << ...` 中幾乎總是如此），這節省了程式碼空間。

vlog_is_on.h
```cpp 
    class VLogSite final {
     public:
      ...
      bool IsEnabled(int level) {
        int stale_v = v_.load(std::memory_order_relaxed);
        if (ABSL_PREDICT_TRUE(level > stale_v)) {
          return false;
        }
    
        // 我們將快速路徑之外的所有內容（即 Vlogging 已初始化但未開啟）
        // 放在一個行外函式中以減少程式碼大小。
        return SlowIsEnabled(stale_v, level);
      }
      ...
     private:
      ...
      ABSL_ATTRIBUTE_NOINLINE
      bool SlowIsEnabled(int stale_v, int level);
      ...
    };
    
```
```cpp 
    class VLogSite final {
     public:
      ...
      bool IsEnabled(int level) {
        int stale_v = v_.load(std::memory_order_relaxed);
        if (ABSL_PREDICT_TRUE(level > stale_v)) {
          return false;
        }
    
        // 我們將快速路徑之外的所有內容（即 Vlogging 已初始化但未開啟）
        // 放在一個行外函式中以減少程式碼大小。
        // "level" 幾乎總是呼叫點常數，因此我們可以透過針對級別 1, 2, 和 3 
        // 進行特殊處理來節省一些程式碼空間。
    #if defined(__has_builtin) && __has_builtin(__builtin_constant_p)
        if (__builtin_constant_p(level)) {
          if (level == 0) return SlowIsEnabled0(stale_v);
          if (level == 1) return SlowIsEnabled1(stale_v);
          if (level == 2) return SlowIsEnabled2(stale_v);
          if (level == 3) return SlowIsEnabled3(stale_v);
          if (level == 4) return SlowIsEnabled4(stale_v);
          if (level == 5) return SlowIsEnabled5(stale_v);
        }
    #endif
        return SlowIsEnabled(stale_v, level);
        ...
     private:
      ...
      ABSL_ATTRIBUTE_NOINLINE
      bool SlowIsEnabled(int stale_v, int level);
      ABSL_ATTRIBUTE_NOINLINE bool SlowIsEnabled0(int stale_v);
      ABSL_ATTRIBUTE_NOINLINE bool SlowIsEnabled1(int stale_v);
      ABSL_ATTRIBUTE_NOINLINE bool SlowIsEnabled2(int stale_v);
      ABSL_ATTRIBUTE_NOINLINE bool SlowIsEnabled3(int stale_v);
      ABSL_ATTRIBUTE_NOINLINE bool SlowIsEnabled4(int stale_v);
      ABSL_ATTRIBUTE_NOINLINE bool SlowIsEnabled5(int stale_v);
      ...
    };
    
```

vlog_is_on.cc
```cpp 
    bool VLogSite::SlowIsEnabled0(int stale_v) { return SlowIsEnabled(stale_v, 0); }
    bool VLogSite::SlowIsEnabled1(int stale_v) { return SlowIsEnabled(stale_v, 1); }
    bool VLogSite::SlowIsEnabled2(int stale_v) { return SlowIsEnabled(stale_v, 2); }
    bool VLogSite::SlowIsEnabled3(int stale_v) { return SlowIsEnabled(stale_v, 3); }
    bool VLogSite::SlowIsEnabled4(int stale_v) { return SlowIsEnabled(stale_v, 4); }
    bool VLogSite::SlowIsEnabled5(int stale_v) { return SlowIsEnabled(stale_v, 5); }
    
```

盡可能使用簡單的前綴匹配取代 `RE2` 呼叫。

read_matcher.cc
```cpp 
    enum MatchItemType {
      MATCH_TYPE_INVALID,
      MATCH_TYPE_RANGE,
      MATCH_TYPE_EXACT,
      MATCH_TYPE_REGEXP,
    };
    
```
```cpp 
    enum MatchItemType {
      MATCH_TYPE_INVALID,
      MATCH_TYPE_RANGE,
      MATCH_TYPE_EXACT,
      MATCH_TYPE_REGEXP,
      MATCH_TYPE_PREFIX,   // 正規表示式 ".*" 的特殊類型
    };
    
```

read_matcher.cc
```cpp 
    p->type = MATCH_TYPE_REGEXP;
    
```
```cpp 
    term.NonMetaPrefix().CopyToString(&p->prefix);
    if (term.RegexpSuffix() == ".*") {
      // 匹配任何內容的正規表示式的特殊情況，因此我們可以繞過 RE2::FullMatch
      p->type = MATCH_TYPE_PREFIX;
    } else {
      p->type = MATCH_TYPE_REGEXP;
    
```

使用 `StrCat` 而非 `StringPrintf` 來格式化 IP 地址。

ipaddress.cc
```cpp 
    string IPAddress::ToString() const {
      char buf[INET6_ADDRSTRLEN];
    
      switch (address_family_) {
        case AF_INET:
          CHECK(inet_ntop(AF_INET, &addr_.addr4, buf, INET6_ADDRSTRLEN) != NULL);
          return buf;
        case AF_INET6:
          CHECK(inet_ntop(AF_INET6, &addr_.addr6, buf, INET6_ADDRSTRLEN) != NULL);
          return buf;
        case AF_UNSPEC:
          LOG(DFATAL) << "在空的 IPAddress 上呼叫 ToString()";
          return "";
        default:
          LOG(FATAL) << "未知位址族群 " << address_family_;
      }
    }
    ...
    string IPAddressToURIString(const IPAddress& ip) {
      switch (ip.address_family()) {
        case AF_INET6:
          return StringPrintf("[%s]", ip.ToString().c_str());
        default:
          return ip.ToString();
      }
    }
    ...
    string SocketAddress::ToString() const {
      return IPAddressToURIString(host_) + StringPrintf(":%u", port_);
    }
    
```
```cpp 
    string IPAddress::ToString() const {
      char buf[INET6_ADDRSTRLEN];
    
      switch (address_family_) {
        case AF_INET: {
          uint32 addr = gntohl(addr_.addr4.s_addr);
          int a1 = static_cast<int>((addr >> 24) & 0xff);
          int a2 = static_cast<int>((addr >> 16) & 0xff);
          int a3 = static_cast<int>((addr >> 8) & 0xff);
          int a4 = static_cast<int>(addr & 0xff);
          return StrCat(a1, ".", a2, ".", a3, ".", a4);
        }
        case AF_INET6:
          CHECK(inet_ntop(AF_INET6, &addr_.addr6, buf, INET6_ADDRSTRLEN) != NULL);
          return buf;
        case AF_UNSPEC:
          LOG(DFATAL) << "在空的 IPAddress 上呼叫 ToString()";
          return "";
        default:
          LOG(FATAL) << "未知位址族群 " << address_family_;
      }
    }
    ...
    string IPAddressToURIString(const IPAddress& ip) {
      switch (ip.address_family()) {
        case AF_INET6:
          return StrCat("[", ip.ToString(), "]");
        default:
          return ip.ToString();
      }
    }
    ...
    string SocketAddress::ToString() const {
      return StrCat(IPAddressToURIString(host_), ":", port_);
    }
    
```

### 使用快取避免重複工作 (Use caching to avoid repeated work)

基於預先計算的大型序列化 Proto 指紋進行快取。

dp_ops.cc
```cpp 
    InputOutputMappingProto mapping_proto;
    PLAQUE_OP_REQUIRES(
        mapping_proto.ParseFromStringPiece(GetAttrMappingProto(state)),
        absl::InternalError("解析 InputOutputMappingProto 失敗"));
    ParseMapping(mapping_proto);
    
```
```cpp 
    uint64 mapping_proto_fp = GetAttrMappingProtoFp(state);
    {
      absl::MutexLock l(&fp_to_iometa_mu);
      if (fp_to_iometa == nullptr) {
        fp_to_iometa =
            new absl::flat_hash_map<uint64, std::unique_ptr<ProgramIOMetadata>>;
      }
      auto it = fp_to_iometa->find(mapping_proto_fp);
      if (it != fp_to_iometa->end()) {
        io_metadata_ = it->second.get();
      } else {
        auto serial_proto = GetAttrMappingProto(state);
        DCHECK_EQ(mapping_proto_fp, Fingerprint(serial_proto));
        InputOutputMappingProto mapping_proto;
        PLAQUE_OP_REQUIRES(
            mapping_proto.ParseFromStringPiece(GetAttrMappingProto(state)),
            absl::InternalError("解析 InputOutputMappingProto 失敗"));
        auto io_meta = ParseMapping(mapping_proto);
        io_metadata_ = io_meta.get();
        (*fp_to_iometa)[mapping_proto_fp] = std::move(io_meta);
      }
    }
    
```

### 讓編譯器的工作更容易 (Make the compiler’s job easier)

編譯器在透過抽象層進行優化時可能會遇到困難，因為它必須對程式碼的整體行為做出保守假設，或者可能無法做出正確的速度與大小權衡。應用程式程式設計師通常對系統行為有更多了解，可以透過將程式碼重寫為在更低層次運行來幫助編譯器。但是，僅在效能分析顯示問題時才這樣做，因為編譯器通常能自行處理。查看效能關鍵常式的產生的組合語言程式碼可以幫助您了解編譯器是否「做對了」。`pprof` 提供了非常有用的[源代碼與反彙編交織顯示](https://github.com/google/pprof/blob/main/doc/README.md#annotated-source-code)，並標註了效能資料。

一些可能有用的技術：

  1. 避免在熱點函式中呼叫函式（允許編譯器避免框架設定成本）。
  2. 將慢速路徑程式碼移動到單獨的尾部呼叫 (tail-called) 函式中。
  3. 在重度使用之前將少量資料複製到局部變數中。這可以讓編譯器假設沒有與其他資料的別名 (aliasing)，從而可能改進自動向量化和暫存器分配。
  4. 手動展開極熱的迴圈。

透過將 `absl::Span` 替換為指向底層陣列的原始指標來加速 `ShapeUtil::ForEachState`。

shape_util.h
```cpp 
    struct ForEachState {
      ForEachState(const Shape& s, absl::Span<const int64_t> b,
                   absl::Span<const int64_t> c, absl::Span<const int64_t> i);
      ~ForEachState();
    
      const Shape& shape;
      const absl::Span<const int64_t> base;
      const absl::Span<const int64_t> count;
      const absl::Span<const int64_t> incr;
    
```
```cpp 
    struct ForEachState {
      ForEachState(const Shape& s, absl::Span<const int64_t> b,
                   absl::Span<const int64_t> c, absl::Span<const int64_t> i);
      inline ~ForEachState() = default;
    
      const Shape& shape;
      // 指向傳入 Span 的陣列指標
      const int64_t* const base;
      const int64_t* const count;
      const int64_t* const incr;
    
```

手動展開[循環冗餘檢查](https://en.wikipedia.org/wiki/Cyclic_redundancy_check) (CRC) 計算迴圈。

crc.cc
```cpp 
    void CRC32::Extend(uint64 *lo, uint64 *hi, const void *bytes, size_t length)
                          const {
                          ...
      // 一次處理 4 位元組
      while ((p + 4) <= e) {
        uint32 c = l ^ WORD(p);
        p += 4;
        l = this->table3_[c & 0xff] ^
            this->table2_[(c >> 8) & 0xff] ^
            this->table1_[(c >> 16) & 0xff] ^
            this->table0_[c >> 24];
      }
    
      // 處理最後幾個位元組
      while (p != e) {
        int c = (l & 0xff) ^ *p++;
        l = this->table0_[c] ^ (l >> 8);
      }
      *lo = l;
    }
    
```
```cpp 
    void CRC32::Extend(uint64 *lo, uint64 *hi, const void *bytes, size_t length)
                          const {
                          ...
    #define STEP {                                  
        uint32 c = l ^ WORD(p);
        p += 4;
        l = this->table3_[c & 0xff] ^
            this->table2_[(c >> 8) & 0xff] ^
            this->table1_[(c >> 16) & 0xff] ^
            this->table0_[c >> 24];
    }
    
      // 一次處理 16 位元組
      while ((e-p) >= 16) {
        STEP;
        STEP;
        STEP;
        STEP;
      }
    
      // 一次處理 4 位元組
      while ((p + 4) <= e) {
        STEP;
      }
    #undef STEP
    
      // 處理最後幾個位元組
      while (p != e) {
        int c = (l & 0xff) ^ *p++;
        l = this->table0_[c] ^ (l >> 8);
      }
      *lo = l;
    }
    
```

在解析 Spanner Key 時一次處理四個字元。

  1. 手動展開迴圈以一次處理四個字元，而不是使用 `memchr`
  2. 手動展開用於尋找名稱分隔部分的迴圈
  3. 向後搜尋帶有 '#' 分隔符號的名稱分隔部分（而不是向前搜尋），因為名稱的第一部分可能是最長的。

key.cc
```cpp 
    void Key::InitSeps(const char* start) {
      const char* base = &rep_[0];
      const char* limit = base + rep_.size();
      const char* s = start;
    
      DCHECK_GE(s, base);
      DCHECK_LT(s, limit);
    
      for (int i = 0; i < 3; i++) {
        s = (const char*)memchr(s, '#', limit - s);
        DCHECK(s != NULL);
        seps_[i] = s - base;
        s++;
      }
    }
    
```
```cpp 
    inline const char* ScanBackwardsForSep(const char* base, const char* p) {
      while (p >= base + 4) {
        if (p[0] == '#') return p;
        if (p[-1] == '#') return p-1;
        if (p[-2] == '#') return p-2;
        if (p[-3] == '#') return p-3;
        p -= 4;
      }
      while (p >= base && *p != '#') p--;
      return p;
    }
    
    void Key::InitSeps(const char* start) {
      const char* base = &rep_[0];
      const char* limit = base + rep_.size();
      const char* s = start;
    
      DCHECK_GE(s, base);
      DCHECK_LT(s, limit);
    
      // 我們從字串末尾開始向後搜尋，而不是向正向搜尋，
      // 因為目錄名稱可能很長，且肯定不包含任何 '#' 字元。
      const char* p = ScanBackwardsForSep(s, limit - 1);
      DCHECK(*p == '#');
      seps_[2] = p - base;
      p--;
    
      p = ScanBackwardsForSep(s, p);
      DCHECK(*p == '#');
      seps_[1] = p - base;
      p--;
    
      p = ScanBackwardsForSep(s, p);
      DCHECK(*p == '#');
      seps_[0] = p - base;
    }
    
```

透過將 `ABSL_LOG(FATAL)` 轉換為 `ABSL_DCHECK(false)` 來避免框架設定成本。

arena_cleanup.h
```cpp 
    inline ABSL_ATTRIBUTE_ALWAYS_INLINE size_t Size(Tag tag) {
      if (!EnableSpecializedTags()) return sizeof(DynamicNode);
    
      switch (tag) {
        case Tag::kDynamic:
          return sizeof(DynamicNode);
        case Tag::kString:
          return sizeof(TaggedNode);
        case Tag::kCord:
          return sizeof(TaggedNode);
        default:
          ABSL_LOG(FATAL) << "損壞的清理標籤: " << static_cast<int>(tag);
          return sizeof(DynamicNode);
      }
    }
    
```
```cpp 
    inline ABSL_ATTRIBUTE_ALWAYS_INLINE size_t Size(Tag tag) {
      if (!EnableSpecializedTags()) return sizeof(DynamicNode);
    
      switch (tag) {
        case Tag::kDynamic:
          return sizeof(DynamicNode);
        case Tag::kString:
          return sizeof(TaggedNode);
        case Tag::kCord:
          return sizeof(TaggedNode);
        default:
          ABSL_DCHECK(false) << "損壞的清理標籤: " << static_cast<int>(tag);
          return sizeof(DynamicNode);
      }
    }
    
```

### 減少統計收集成本 (Reduce stats collection costs)

在統計資訊及系統其他行為資訊的效用與維護該資訊的成本之間取得平衡。額外的資訊通常能幫助人們理解和改善高層次行為，但維護成本也可能很高。 

無用的統計資訊可以完全捨棄。

停止在 `SelectServer` 中維護關於警報和閉包 (closure) 數量的昂貴統計資訊。

這是將設定警報時間從 771 ns 減少到 271 ns 的更改之一。

selectserver.h
```cpp 
    class SelectServer {
     public:
     ...
     protected:
      ...
      scoped_ptr<MinuteTenMinuteHourStat> num_alarms_stat_;
      ...
      scoped_ptr<MinuteTenMinuteHourStat> num_closures_stat_;
      ...
    };
    
```
```cpp 
    // Selectserver 類別
    class SelectServer {
     ...
     protected:
     ...
    };
    
```

/selectserver.cc
```cpp 
    void SelectServer::AddAlarmInternal(Alarmer* alarmer,
                                        int offset_in_ms,
                                        int id,
                                        bool is_periodic) {
                                        ...
      alarms_->insert(alarm);
      num_alarms_stat_->IncBy(1);
      ...
    }
    
```
```cpp 
    void SelectServer::AddAlarmInternal(Alarmer* alarmer,
                                        int offset_in_ms,
                                        int id,
                                        bool is_periodic) {
                                        ...
      alarms_->Add(alarm);
      ...
    }
    
```

/selectserver.cc
```cpp 
    void SelectServer::RemoveAlarm(Alarmer* alarmer, int id) {
          ...
          alarms_->erase(alarm);
          num_alarms_stat_->IncBy(-1);
          ...
    }
    
```
```cpp 
    void SelectServer::RemoveAlarm(Alarmer* alarmer, int id) {
          ...
          alarms_->Remove(alarm);
          ...
    }
    
```

通常，可以對系統處理的元素子集（例如 RPC 請求、輸入記錄、使用者）維護統計資訊或其他屬性。許多子系統使用這種方法（tcmalloc 配置追蹤、/requestz status 頁面、Dapper 採樣）。

進行採樣時，考慮在適當時降低採樣率。

僅對 doc info 請求的樣本維護統計資訊。

採樣使我們能夠在大多數請求中避免觸及 39 個直方圖和 `MinuteTenMinuteHour` 統計資訊。

generic-leaf-stats.cc
```cpp 
    ... 為每個請求更新各種統計資訊而觸及 39 個直方圖的程式碼 ...
    
```
```cpp 
    // 定期添加到直方圖中
    if (TryLockToUpdateHistogramsDocInfo(docinfo_stats, bucket)) {
      // 僅在我們應該對此請求進行採樣以維護統計資訊時，
      // 返回 true 並獲取 bucket->lock
      ... 觸及 39 個直方圖以更新各種統計資訊的程式碼 ...
      bucket->lock.Unlock();
    }
    
```

降低採樣率並做出更快的採樣決定。

此更改將採樣率從 1/10 降低到 1/32。此外，我們現在僅對採樣事件保留執行時間統計資訊，並透過使用 2 的冪次方取模 (modulus) 來加速採樣決定。這段程式碼在 Google Meet 視訊會議系統的每個封包上都會被呼叫，並且在 COVID 爆發初期，隨著使用者迅速遷移到進行更多線上會議，需要進行效能工作以跟上容量需求。

packet_executor.cc
```cpp 
    class ScopedPerformanceMeasurement {
     public:
      explicit ScopedPerformanceMeasurement(PacketExecutor* packet_executor)
          : packet_executor_(packet_executor),
            tracer_(packet_executor->packet_executor_trace_threshold_,
                    kClosureTraceName) {
        // ThreadCPUUsage 是一個昂貴的呼叫。在撰寫本文時，
        // 它耗時超過 400ns，大約比 absl::Now 慢 30 倍，
        // 因此我們僅對 10% 的閉包 (closure) 進行採樣以降低成本。
        if (packet_executor->closures_executed_ % 10 == 0) {
          thread_cpu_usage_start_ = base::ThreadCPUUsage();
        }
    
        // 在可能執行上述昂貴呼叫後對開始時間進行採樣，
        // 以免污染牆鐘時間 (wall time) 測量。
        run_start_time_ = absl::Now();
      }
    
      ~ScopedPerformanceMeasurement() {
    
```
```cpp 
    ScopedPerformanceMeasurement::ScopedPerformanceMeasurement(
        PacketExecutor* packet_executor)
        : packet_executor_(packet_executor),
          tracer_(packet_executor->packet_executor_trace_threshold_,
                  kClosureTraceName) {
      // ThreadCPUUsage 是一個昂貴的呼叫。在撰寫本文時，
      // 它耗時超過 400ns，大約比 absl::Now 慢 30 倍，
      // 因此我們僅對 32 個閉包中取 1 個進行採樣以降低成本。
      if (packet_executor->closures_executed_ % 32 == 0) {
        thread_cpu_usage_start_ = base::ThreadCPUUsage();
      }
    
      // 在可能執行上述昂貴呼叫後對開始時間進行採樣，
      // 以免污染牆鐘時間 (wall time) 測量。
      run_start_time_ = absl::Now();
    }
    
```

packet_executor.cc
```cpp 
    ~ScopedPerformanceMeasurement() {
      auto run_end_time = absl::Now();
      auto run_duration = run_end_time - run_start_time_;
    
      if (thread_cpu_usage_start_.has_value()) {
      ...
      }
    
      closure_execution_time->Record(absl::ToInt64Microseconds(run_duration));
    
```
```cpp 
    ScopedPerformanceMeasurement::~ScopedPerformanceMeasurement() {
      auto run_end_time = absl::Now();
      auto run_duration = run_end_time - run_start_time_;
    
      if (thread_cpu_usage_start_.has_value()) {
        ...
        closure_execution_time->Record(absl::ToInt64Microseconds(run_duration));
      }
    
```

基準測試結果：
```cpp 
    Run on (40 X 2793 MHz CPUs); 2020-03-24T20:08:19.991412535-07:00
    CPU: Intel Ivybridge with HyperThreading (20 cores) dL1:32KB dL2:256KB dL3:25MB
    基準測試 (Benchmark)                           基準 (Base) (ns)    新 (New) (ns) 改進 (Improvement)
    ----------------------------------------------------------------------------
    BM_PacketOverhead_mean                               224          85    +62.0%
    
```

### 避免在熱點程式碼路徑上進行日誌記錄 (Avoid logging on hot code paths)

日誌記錄語句可能代價高昂，即使該語句的日誌層級actually並未記錄任何內容。例如，`ABSL_VLOG` 的實作至少需要一次載入和一次比較，這在熱點程式碼路徑中可能是一個問題。此外，日誌記錄程式碼的存在可能會阻礙編譯器優化。考慮從熱點程式碼路徑中完全刪除日誌記錄。

從記憶體分配器核心移除日誌記錄。

這是一個較大更改的一小部分。

gpu_bfc_allocator.cc
```cpp 
    void GPUBFCAllocator::SplitChunk(...) {
      ...
      VLOG(6) << "添加到區塊地圖: " << new_chunk->ptr;
      ...
    }
    ...
    void GPUBFCAllocator::DeallocateRawInternal(void* ptr) {
      ...
      VLOG(6) << "位於 " << c->ptr << " 的區塊不再使用";
      ...
    }
    
```
```cpp 
    void GPUBFCAllocator::SplitChunk(...) {
    ...
    }
    ...
    void GPUBFCAllocator::DeallocateRawInternal(void* ptr) {
    ...
    }
    
```

在嵌套迴圈外預先計算是否啟用了日誌記錄。

image_similarity.cc
```cpp 
    for (int j = 0; j < output_subimage_size_y; j++) {
      int j1 = j - rad + output_to_integral_subimage_y;
      int j2 = j1 + 2 * rad + 1;
      // 為此行的輸出建立一個指標，考慮到與完整圖像的偏移量。
      double *image_diff_ptr = &(*image_diff)(j + min_j, min_i);
    
      for (int i = 0; i < output_subimage_size_x; i++) {
        ...
        if (VLOG_IS_ON(3)) {
        ...
        }
        ...
      }
    }
    
```
```cpp 
    const bool vlog_3 = DEBUG_MODE ? VLOG_IS_ON(3) : false;
    
    for (int j = 0; j < output_subimage_size_y; j++) {
      int j1 = j - rad + output_to_integral_subimage_y;
      int j2 = j1 + 2 * rad + 1;
      // 為此行的輸出建立一個指標，考慮到與完整圖像的偏移量。
      double *image_diff_ptr = &(*image_diff)(j + min_j, min_i);
    
      for (int i = 0; i < output_subimage_size_x; i++) {
        ...
        if (vlog_3) {
        ...
        }
      }
    }
    
```
```cpp 
    Run on (40 X 2801 MHz CPUs); 2016-05-16T15:55:32.250633072-07:00
    CPU: Intel Ivybridge with HyperThreading (20 cores) dL1:32KB dL2:256KB dL3:25MB
    基準測試 (Benchmark)              基準 (Base) (ns)  新 (New) (ns) 改進 (Improvement)
    ------------------------------------------------------------------
    BM_NCCPerformance/16                   29104     26372     +9.4%
    BM_NCCPerformance/64                  473235    425281    +10.1%
    BM_NCCPerformance/512               30246238  27622009     +8.7%
    BM_NCCPerformance/1k              125651445  113361991     +9.8%
    BM_NCCLimitedBoundsPerformance/16       8314      7498     +9.8%
    BM_NCCLimitedBoundsPerformance/64     143508    132202     +7.9%
    BM_NCCLimitedBoundsPerformance/512   9335684   8477567     +9.2%
    BM_NCCLimitedBoundsPerformance/1k   37223897  34201739     +8.1%
    
```

預先計算是否啟用了日誌記錄，並在輔助常式中使用該結果。

periodic_call.cc
```cpp 
      VLOG(1) << Logid()
              << "MaybeScheduleAlarmAtNextTick. Time until next real time: "
              << time_until_next_real_time;
              ...
      uint64 next_virtual_time_ms =
          next_virtual_time_ms_ - num_ticks * kResolutionMs;
      CHECK_GE(next_virtual_time_ms, 0);
      ScheduleAlarm(now, delay, next_virtual_time_ms);
    }
    
    void ScheduleNextAlarm(uint64 current_virtual_time_ms)
        ABSL_EXCLUSIVE_LOCKS_REQUIRED(mutex_) {
      if (calls_.empty()) {
        VLOG(1) << Logid() << "無剩餘呼叫，進入空閒模式";
        next_real_time_ = absl::InfiniteFuture();
        return;
      }
      uint64 next_virtual_time_ms = FindNextVirtualTime(current_virtual_time_ms);
      auto delay =
          absl::Milliseconds(next_virtual_time_ms - current_virtual_time_ms);
      ScheduleAlarm(GetClock().TimeNow(), delay, next_virtual_time_ms);
    }
    
    // 由此函式排定的警報取代所有先前排定的警報。
    // 這透過 `scheduling_sequence_number_` 來確保。
    void ScheduleAlarm(absl::Time now, absl::Duration delay,
                       uint64 virtual_time_ms)
        ABSL_EXCLUSIVE_LOCKS_REQUIRED(mutex_) {
      next_real_time_ = now + delay;
      next_virtual_time_ms_ = virtual_time_ms;
      ++ref_count_;  // 警報持有一個引用。
      ++scheduling_sequence_number_;
      VLOG(1) << Logid() << "ScheduleAlarm. Time : "
              << absl::FormatTime("%M:%S.%E3f", now, absl::UTCTimeZone())
              << ", delay: " << delay << ", virtual time: " << virtual_time_ms
              << ", refs: " << ref_count_
              << ", seq: " << scheduling_sequence_number_
              << ", executor: " << executor_;
    
      executor_->AddAfter(
          delay, new Alarm(this, virtual_time_ms, scheduling_sequence_number_));
    }
    
```
```cpp 
      const bool vlog_1 = VLOG_IS_ON(1);
    
      if (vlog_1) {
        VLOG(1) << Logid()
                << "MaybeScheduleAlarmAtNextTick. Time until next real time: "
                << time_until_next_real_time;
      }
      ...
      uint64 next_virtual_time_ms =
          next_virtual_time_ms_ - num_ticks * kResolutionMs;
      CHECK_GE(next_virtual_time_ms, 0);
      ScheduleAlarm(now, delay, next_virtual_time_ms, vlog_1);
    }
    
    void ScheduleNextAlarm(uint64 current_virtual_time_ms, bool vlog_1)
        ABSL_EXCLUSIVE_LOCKS_REQUIRED(mutex_) {
      if (calls_.empty()) {
        if (vlog_1) {
          VLOG(1) << Logid() << "無剩餘呼叫，進入空閒模式";
        }
        next_real_time_ = absl::InfiniteFuture();
        return;
      }
      uint64 next_virtual_time_ms = FindNextVirtualTime(current_virtual_time_ms);
      auto delay =
          absl::Milliseconds(next_virtual_time_ms - current_virtual_time_ms);
      ScheduleAlarm(GetClock().TimeNow(), delay, next_virtual_time_ms, vlog_1);
    }
    
    // 由此函式排定的警報取代所有先前排定的警報。
    // 這透過 `scheduling_sequence_number_` 來確保。
    void ScheduleAlarm(absl::Time now, absl::Duration delay,
                       uint64 virtual_time_ms,
                       bool vlog_1)
        ABSL_EXCLUSIVE_LOCKS_REQUIRED(mutex_) {
      next_real_time_ = now + delay;
      next_virtual_time_ms_ = virtual_time_ms;
      ++ref_count_;  // 警報持有一個引用。
      ++scheduling_sequence_number_;
      if (vlog_1) {
        VLOG(1) << Logid() << "ScheduleAlarm. Time : "
                << absl::FormatTime("%M:%S.%E3f", now, absl::UTCTimeZone())
                << ", delay: " << delay << ", virtual time: " << virtual_time_ms
                << ", refs: " << ref_count_
                << ", seq: " << scheduling_sequence_number_
                << ", executor: " << executor_;
      }
    
      executor_->AddAfter(
          delay, new Alarm(this, virtual_time_ms, scheduling_sequence_number_));
    }
    
```
## 程式碼大小考量 (Code size considerations)

效能不僅僅包含執行速度。有時，考慮軟體選擇對產生的程式碼大小的影響也是值得的。較大的程式碼大小意謂著更長的編譯和連結時間、膨脹的執行檔、更多的記憶體使用、更多的指令快取 (icache) 壓力，以及其他有時對分支預測器等微架構結構產生的負面影響。在編寫將在許多地方使用的低階函式庫程式碼，或編寫您預期將為許多不同類型實例化的模板程式碼時，思考這些問題尤為重要。

用於減少程式碼大小的技術因程式語言而異。以下是一些我們發現對 C++ 程式碼有用的技術（C++ 程式碼常受過度使用模板和內聯之苦）。

### 修剪常用的內聯程式碼 (Trim commonly inlined code)

廣泛呼叫的函式結合內聯會對程式碼大小產生劇烈影響。

加速 `TF_CHECK_OK`。

避免建立 Ok 物件，並透過在行外 (out-of-line) 執行致命錯誤訊息的複雜格式化，而不是在每個呼叫點執行，來節省程式碼空間。

status.h
```cpp 
    #define TF_CHECK_OK(val) CHECK_EQ(::tensorflow::Status::OK(), (val))
    #define TF_QCHECK_OK(val) QCHECK_EQ(::tensorflow::Status::OK(), (val))
    
```
```cpp 
    extern tensorflow::string* TfCheckOpHelperOutOfLine(
        const ::tensorflow::Status& v, const char* msg);
    inline tensorflow::string* TfCheckOpHelper(::tensorflow::Status v,
                                               const char* msg) {
      if (v.ok()) return nullptr;
      return TfCheckOpHelperOutOfLine(v, msg);
    }
    #define TF_CHECK_OK(val)                                           \
      while (tensorflow::string* _result = TfCheckOpHelper(val, #val)) \
      LOG(FATAL) << *(_result)
    #define TF_QCHECK_OK(val)                                          \
      while (tensorflow::string* _result = TfCheckOpHelper(val, #val)) \
      LOG(QFATAL) << *(_result)
    
```

status.cc
```cpp 
    string* TfCheckOpHelperOutOfLine(const ::tensorflow::Status& v,
                                     const char* msg) {
      string r("非 OK 狀態: ");
      r += msg;
      r += " 狀態: ";
      r += v.ToString();
      // 洩漏字串，但這僅用於致命錯誤訊息
      return new string(r);
    }
    
```

將每個 `RETURN_IF_ERROR` 呼叫點縮小 79 位元組的程式碼。

  1. 加入僅供 `RETURN_IF_ERROR` 使用的特殊適配器類別。
  2. 不在 `RETURN_IF_ERROR` 的快速路徑上建構/析構 `StatusBuilder`。
  3. 不內聯某些現在快速路徑上不再需要的 `StatusBuilder` 方法。
  4. 避免不必要的 `~Status` 呼叫。

將 `CHECK_GE` 的效能提升 4.5 倍，並將程式碼大小從 125 位元組縮小到 77 位元組。

logging.h
```cpp 
    struct CheckOpString {
      CheckOpString(string* str) : str_(str) { } 
      ~CheckOpString() { delete str_; }
      operator bool() const { return str_ == NULL; }
      string* str_;
    };
    ... 
    #define DEFINE_CHECK_OP_IMPL(name, op) \
      template <class t1, class t2> \
      inline string* Check##name##Impl(const t1& v1, const t2& v2, \
                                       const char* names) { \
        if (v1 op v2) return NULL; \
        else return MakeCheckOpString(v1, v2, names); \
      } \
      string* Check##name##Impl(int v1, int v2, const char* names);
    DEFINE_CHECK_OP_IMPL(EQ, ==)
    DEFINE_CHECK_OP_IMPL(NE, !=)
    DEFINE_CHECK_OP_IMPL(LE, <=)
    DEFINE_CHECK_OP_IMPL(LT, < )
    DEFINE_CHECK_OP_IMPL(GE, >=)
    DEFINE_CHECK_OP_IMPL(GT, > )
    #undef DEFINE_CHECK_OP_IMPL
    
```
```cpp 
    struct CheckOpString {
      CheckOpString(string* str) : str_(str) { } 
      // 無析構函式：如果 str_ 非空，我們即將呼叫 LOG(FATAL)，
      // 因此清理 str_ 沒有意義。
      operator bool() const { return str_ == NULL; }
      string* str_;
    };
    ... 
    extern string* MakeCheckOpStringIntInt(int v1, int v2, const char* names);
    
    template<int, int>
    string* MakeCheckOpString(const int& v1, const int& v2, const char* names) {
      return MakeCheckOpStringIntInt(v1, v2, names);
    }
    ...
    #define DEFINE_CHECK_OP_IMPL(name, op) \
      template <class t1, class t2> \
      inline string* Check##name##Impl(const t1& v1, const t2& v2, \
                                       const char* names) { \
        if (v1 op v2) return NULL; \
        else return MakeCheckOpString(v1, v2, names); \
      } \
      inline string* Check##name##Impl(int v1, int v2, const char* names) { \
        if (v1 op v2) return NULL; \
        else return MakeCheckOpString(v1, v2, names); \
      }
    DEFINE_CHECK_OP_IMPL(EQ, ==)
    DEFINE_CHECK_OP_IMPL(NE, !=)
    DEFINE_CHECK_OP_IMPL(LE, <=)
    DEFINE_CHECK_OP_IMPL(LT, < )
    DEFINE_CHECK_OP_IMPL(GE, >=)
    DEFINE_CHECK_OP_IMPL(GT, > )
    #undef DEFINE_CHECK_OP_IMPL
    
```

logging.cc
```cpp 
    string* MakeCheckOpStringIntInt(int v1, int v2, const char* names) {
      strstream ss;
      ss << names << " (" << v1 << " vs. " << v2 << ")";
      return new string(ss.str(), ss.pcount());
    }
    
```

### 謹慎內聯 (Inline with care)

內聯通常可以提高效能，但有時它會增加程式碼大小而沒有相應的效能回報（在某些情況下，由於指令快取壓力增加，甚至會導致效能損失）。

減少 TensorFlow 中的內聯。

此更改停止內聯許多非效能敏感函式（例如：錯誤路徑和運算子註冊程式碼）。此外，某些效能敏感函式的慢速路徑被移動到非內聯函式中。

這些更改使典型執行檔中 tensorflow 符號的大小減少了 12.2%（從 8814545 位元組降至 7740233 位元組）

Protocol Buffer 函式庫更改。避免在編碼長度 ≥ 128 位元組的訊息時佔用昂貴的內聯程式碼空間，改為呼叫共享的行外常式。

不僅使重要的大型執行檔更小，而且更快。

一個大型執行檔中某個高度內聯常式每行產生的程式碼位元組數。第一個數字代表為特定源代碼行產生的總位元組數，包括該程式碼被內聯的所有位置。

Before:
```cpp 
    .           0   1825 template <typename MessageType>
    .           0   1826 inline uint8* WireFormatLite::InternalWriteMessage(
    .           0   1827     int field_number, const MessageType& value, uint8* target,
    .           0   1828     io::EpsCopyOutputStream* stream) {
    >>>    389246   1829   target = WriteTagToArray(field_number, WIRETYPE_LENGTH_DELIMITED, target);
    >>>   5454640   1830   target = io::CodedOutputStream::WriteVarint32ToArray(
    >>>    337837   1831       static_cast<uint32>(value.GetCachedSize()), target);
    >>>   1285539   1832   return value._InternalSerialize(target, stream);
    .           0   1833 }
    
```

此更改後的程式碼大小輸出如下：
```cpp 
    .           0   1825 template <typename MessageType>
    .           0   1826 inline uint8* WireFormatLite::InternalWriteMessage(
    .           0   1827     int field_number, const MessageType& value, uint8* target,
    .           0   1828     io::EpsCopyOutputStream* stream) {
    >>>    450612   1829   target = WriteTagToArray(field_number, WIRETYPE_LENGTH_DELIMITED, target);
    >>       9609   1830   target = io::CodedOutputStream::WriteVarint32ToArrayOutOfLine(
    >>>    434668   1831       static_cast<uint32>(value.GetCachedSize()), target);
    >>>   1597394   1832   return value._InternalSerialize(target, stream);
    .           0   1833 }
    
```

```
coded_stream.h
```cpp 
    class PROTOBUF_EXPORT CodedOutputStream {
      ...
      // 類似 WriteVarint32() 但直接寫入目標陣列，且較少見的情況路徑位於行外而非內聯。
      static uint8* WriteVarint32ToArrayOutOfLine(uint32 value, uint8* target);
      ...
    };
    ...
    inline uint8* CodedOutputStream::WriteVarint32ToArrayOutOfLine(uint32 value,
                                                                   uint8* target) {
      target[0] = static_cast<uint8>(value);
      if (value < 0x80) {
        return target + 1;
      } else {
        return WriteVarint32ToArrayOutOfLineHelper(value, target);
      }
    }
    
```

coded_stream.cc
```cpp 
    uint8* CodedOutputStream::WriteVarint32ToArrayOutOfLineHelper(uint32 value,
                                                                  uint8* target) {
      DCHECK_GE(value, 0x80);
      target[0] |= static_cast<uint8>(0x80);
      value >>= 7;
      target[1] = static_cast<uint8>(value);
      if (value < 0x80) {
        return target + 2;
      }
      target += 2;
      do {
        // 在我們剛寫入的位元組中開啟持續位元。
        target[-1] |= static_cast<uint8>(0x80);
        value >>= 7;
        *target = static_cast<uint8>(value);
        ++target;
      } while (value >= 0x80);
      return target;
    }
    
```

減少 `absl::flat_hash_set` 和 `absl::flat_hash_map` 的程式碼大小。

  1. 將不依賴於特定雜湊表類型的程式碼提取到公共 (非內聯) 函式中。
  2. 明智地放置 `ABSL_ATTRIBUTE_NOINLINE` 指令。
  3. 將一些慢速路徑移出行外。

將一些大型執行檔的大小減少了約 0.5%。

不使用 Protobuf Arena 時，不內聯字串配置和解除配置。

public/arenastring.h
```cpp 
      if (IsDefault(default_value)) {
        std::string* new_string = new std::string();
        tagged_ptr_.Set(new_string);
        return new_string;
      } else {
        return UnsafeMutablePointer();
      }
    }
    
```
```cpp 
      if (IsDefault(default_value)) {
        return SetAndReturnNewString();
      } else {
        return UnsafeMutablePointer();
      }
    }
    
```

internal/arenastring.cc
```cpp 
    std::string* ArenaStringPtr::SetAndReturnNewString() {
      std::string* new_string = new std::string();
      tagged_ptr_.Set(new_string);
      return new_string;
    }
    
```

避免內聯某些常式。建立接受 `const char*` 而非 `const std::string&` 的常式變體，以避免在每個呼叫點產生的 `std::string` 建構程式碼。

op.h
```cpp 
    class OpDefBuilderWrapper {
     public:
      explicit OpDefBuilderWrapper(const char name[]) : builder_(name) {}
      OpDefBuilderWrapper& Attr(std::string spec) {
        builder_.Attr(std::move(spec));
        return *this;
      }
      OpDefBuilderWrapper& Input(std::string spec) {
        builder_.Input(std::move(spec));
        return *this;
      }
      OpDefBuilderWrapper& Output(std::string spec) {
        builder_.Output(std::move(spec));
        return *this;
      }
    
```
```cpp 
    class OpDefBuilderWrapper {
     public:
      explicit OpDefBuilderWrapper(const char name[]) : builder_(name) {}
      OpDefBuilderWrapper& Attr(std::string spec) {
        builder_.Attr(std::move(spec));
        return *this;
      }
      OpDefBuilderWrapper& Attr(const char* spec) TF_ATTRIBUTE_NOINLINE {
        return Attr(std::string(spec));
      }
      OpDefBuilderWrapper& Input(std::string spec) {
        builder_.Input(std::move(spec));
        return *this;
      }
      OpDefBuilderWrapper& Input(const char* spec) TF_ATTRIBUTE_NOINLINE {
        return Input(std::string(spec));
      }
      OpDefBuilderWrapper& Output(std::string spec) {
        builder_.Output(std::move(spec));
        return *this;
      }
      OpDefBuilderWrapper& Output(const char* spec) TF_ATTRIBUTE_NOINLINE {
        return Output(std::string(spec));
      }
    
```

### 減少模板實例化 (Reduce template instantiations)

模板程式碼在實例化時，會針對模板引數的每種可能組合進行重複。

使用正規引數取代模板引數。

將一個以 `bool` 為模板引數的大型常式改為將該 `bool` 作為額外引數。（該 `bool` 僅被使用一次來選擇兩個字串常數之一，因此執行時檢查完全沒問題。）這將該大型常式的實例化數量從 287 個減少到 143 個。

sharding_util_ops.cc
```cpp 
    template <bool Split>
    Status GetAndValidateAttributes(OpKernelConstruction* ctx,
                                    std::vector<int32>& num_partitions,
                                    int& num_slices, std::vector<int32>& paddings,
                                    bool& has_paddings) {
      absl::string_view num_partitions_attr_name =
          Split ? kNumSplitsAttrName : kNumConcatsAttrName;
          ...
      return OkStatus();
    }
    
```
```cpp 
    Status GetAndValidateAttributes(bool split, OpKernelConstruction* ctx,
                                    std::vector<int32>& num_partitions,
                                    int& num_slices, std::vector<int32>& paddings,
                                    bool& has_paddings) {
      absl::string_view num_partitions_attr_name =
          split ? kNumSplitsAttrName : kNumConcatsAttrName;
          ...
      return OkStatus();
    }
    
```

將龐大的程式碼從模板化建構子移動到非模板化的共享基類建構子。

同時將模板實例化數量從 `<T, Device, Rank>` 的每個組合一個減少到每個 `<T>` 一個和每個 `<Rank>` 一個。

sharding_util_ops.cc
```cpp 
    template <typename Device, typename T>
    class XlaSplitNDBaseOp : public OpKernel {
     public:
      explicit XlaSplitNDBaseOp(OpKernelConstruction* ctx) : OpKernel(ctx) {
        OP_REQUIRES_OK(
            ctx, GetAndValidateAttributes(/*split=*/true, ctx, num_splits_,
                                          num_slices_, paddings_, has_paddings_));
      }
    
```
```cpp 
    // 共享基類以節省程式碼空間
    class XlaSplitNDShared : public OpKernel {
     public:
      explicit XlaSplitNDShared(OpKernelConstruction* ctx) TF_ATTRIBUTE_NOINLINE
          : OpKernel(ctx),
            num_slices_(1),
            has_paddings_(false) {
        GetAndValidateAttributes(/*split=*/true, ctx, num_splits_, num_slices_,
                                 paddings_, has_paddings_);
      }
    
```

減少 `absl::flat_hash_set` 和 `absl::flat_hash_map` 產生的程式碼大小。

  * 將不依賴於特定雜湊表類型的程式碼提取到公共 (非內聯) 函式中。
  * 明智地放置 `ABSL_ATTRIBUTE_NOINLINE` 指令。
  * 將一些慢速路徑移出行外。

### 減少容器操作 (Reduce container operations)

考慮 Map 和其他容器操作的影響，因為每次呼叫此類操作都可能產生大量的程式碼。

將初始化 Emoji 字元雜湊表的許多連續 Map 插入呼叫轉換為單個批量插入操作 (從 188KB 文本減少到連結到許多執行檔的函式庫中的 360 位元組)。 😊

textfallback_init.h
```cpp 
    inline void AddEmojiFallbacks(TextFallbackMap *map) {
      (*map)[0xFE000] = &kFE000;
      (*map)[0xFE001] = &kFE001;
      (*map)[0xFE002] = &kFE002;
      (*map)[0xFE003] = &kFE003;
      (*map)[0xFE004] = &kFE004;
      (*map)[0xFE005] = &kFE005;
      ...
      (*map)[0xFEE7D] = &kFEE7D;
      (*map)[0xFEEA0] = &kFEEA0;
      (*map)[0xFE331] = &kFE331;
    };
    
```
```cpp 
    inline void AddEmojiFallbacks(TextFallbackMap *map) {
    #define PAIR(x) {0x##x, &k##x}
      // clang-format off
      map->insert({
        PAIR(FE000),
        PAIR(FE001),
        PAIR(FE002),
        PAIR(FE003),
        PAIR(FE004),
        PAIR(FE005),
        ...
        PAIR(FEE7D),
        PAIR(FEEA0),
        PAIR(FE331)});
      // clang-format on
    #undef PAIR
    };
    
```

停止內聯 `InlinedVector` 操作的重度使用者。

將從 `.h` 檔案中內聯的極長常式移動到 `.cc`（內聯此內容沒有實際的效能好處）。

reduction_ops_common.h
```cpp 
    Status Simplify(const Tensor& data, const Tensor& axis,
                    const bool keep_dims) {
      ... 八十行常式主體 ...
    }
    
```
```cpp 
    Status Simplify(const Tensor& data, const Tensor& axis, const bool keep_dims);
    
```

## 並列化與同步 (Parallelization and synchronization)

### 利用並列性 (Exploit parallelism)

現代機器具有許多核心，且通常未被充分利用。因此，透過並列化，昂貴的工作可能會更快完成。最常見的方法是並列處理不同的項目，並在完成後合併結果。通常，項目首先被分區成批次，以避免為並列執行每個項目付出代價。

四路並列化使編碼 Token 的速率提高了約 3.6 倍。

blocked-token-coder.cc
```cpp 
    MutexLock l(&encoder_threads_lock);
    if (encoder_threads == NULL) {
      encoder_threads = new ThreadPool(NumCPUs());
      encoder_threads->SetStackSize(262144);
      encoder_threads->StartWorkers();
    }
    encoder_threads->Add
        (NewCallback(this,
                     &BlockedTokenEncoder::EncodeRegionInThread,
                     region_tokens, N, region,
                     stats,
                     controller_->GetClosureWithCost
                     (NewCallback(&DummyCallback), N)));
    
```

並列化使解碼效能提高了 5 倍。

coding.cc
```cpp 
    for (int c = 0; c < clusters->size(); c++) {
      RET_CHECK_OK(DecodeBulkForCluster(...);
    }
    
```
```cpp 
    struct SubTask {
      absl::Status result;
      absl::Notification done;
    };
    
    std::vector<SubTask> tasks(clusters->size());
    for (int c = 0; c < clusters->size(); c++) {
      options_.executor->Schedule([&, c] {
        tasks[c].result = DecodeBulkForCluster(...);
        tasks[c].done.Notify();
      });
    }
    for (int c = 0; c < clusters->size(); c++) {
      tasks[c].done.WaitForNotification();
    }
    for (int c = 0; c < clusters->size(); c++) {
      RETURN_IF_ERROR(tasks[c].result);
    }
    
```

應仔細測量對系統效能的影響——如果沒有可用的備用 CPU，或者如果記憶體頻寬已飽和，並列化可能沒有幫助，甚至可能有害。

### 攤銷鎖獲取成本 (Amortize lock acquisition)

避免細粒度鎖定，以減少熱點路徑中 Mutex 操作的成本。警告：僅當變更不會增加鎖競爭時才應這樣做。

一次獲取鎖以釋放整個查詢節點樹，而不是為樹中的每個節點重新獲取鎖。

mustang-query.cc
```cpp 
    // 查詢節點池
    ThreadSafeFreeList<MustangQuery> pool_(256);
    ...
    void MustangQuery::Release(MustangQuery* node) {
      if (node == NULL)
        return;
      for (int i=0; i < node->children_->size(); ++i)
        Release((*node->children_)[i]);
      node->children_->clear();
      pool_.Delete(node);
    }
    
```
```cpp 
    // 查詢節點池
    Mutex pool_lock_;
    FreeList<MustangQuery> pool_(256);
    ...
    void MustangQuery::Release(MustangQuery* node) {
      if (node == NULL)
        return;
      MutexLock l(&pool_lock_);
      ReleaseLocked(node);
    }
    
    void MustangQuery::ReleaseLocked(MustangQuery* node) {
    #ifndef NDEBUG
      pool_lock_.AssertHeld();
    #endif
      if (node == NULL)
        return;
      for (int i=0; i < node->children_->size(); ++i)
        ReleaseLocked((*node->children_)[i]);
      node->children_->clear();
      pool_.Delete(node);
    }
    
```

### 保持關鍵區間簡短 (Keep critical sections short)

避免在關鍵區間 (critical sections) 內執行昂貴的工作。特別是要注意看起來無害、但可能正在執行 RPC 或存取檔案的程式碼。

減少關鍵區間內觸及的快取行數量。

仔細的資料結構調整顯著減少了存取的快取行數量，並使 ML 訓練執行的效能提高了 3.3%。

  1. 預先計算一些每個節點類型的屬性，作為 `NodeItem` 資料結構內的位元，這意謂著我們可以避免在關鍵區間內觸及傳出邊的 `Node*` 物件。
  2. 更改 `ExecutorState::ActivateNodes` 以針對每個傳出邊使用目標節點的 `NodeItem`，而不是觸及 `*item->node` 物件中的欄位。通常這意謂著我們總共觸及 1 或 2 個快取行來存取所需的邊資料，而不是 `~2 + O(傳出邊數量)`（對於執行它們的多核心大型圖，TLB 壓力也會更小）。

避免在持有 Mutex 時執行 RPC。

trainer.cc
```cpp 
    {
      // 通知參數伺服器我們正在開始。
      MutexLock l(&lock_);
      model_ = model;
      MaybeRecordProgress(last_global_step_);
    }
    
```
```cpp 
    bool should_start_record_progress = false;
    int64 step_for_progress = -1;
    {
      // 通知參數伺服器我們正在開始。
      MutexLock l(&lock_);
      model_ = model;
      should_start_record_progress = ShouldStartRecordProgress();
      step_for_progress = last_global_step_;
    }
    if (should_start_record_progress) {
      StartRecordProgress(step_for_progress);
    }
    
```

此外，要警惕在 Mutex 解鎖前執行的昂貴析構函式（這通常發生在由 `~MutexUnlock` 觸發 Mutex 解鎖時）。在 `MutexLock` 之前宣告具有昂貴析構函式的物件可能會有幫助（假設它是執行緒安全的）。

### 透過分片減少競爭 (Reduce contention by sharding)

有時，受 Mutex 保護但表現出高度競爭的資料結構可以安全地拆分為多個分片 (shards)，每個分片都有自己的 Mutex。（注意：這要求不同分片之間沒有跨分片的不變性。）

將快取分成 16 個分片，這在多執行緒負載下使吞吐量提高了約 2 倍。

cache.cc
```cpp 
    class ShardedLRUCache : public Cache {
     private:
      LRUCache shard_[kNumShards];
      port::Mutex id_mutex_;
      uint64_t last_id_;
    
      static inline uint32_t HashSlice(const Slice& s) {
        return Hash(s.data(), s.size(), 0);
      }

      static uint32_t Shard(uint32_t hash) {
        return hash >> (32 - kNumShardBits);
      }
      ...
      virtual Handle* Lookup(const Slice& key) {
        const uint32_t hash = HashSlice(key);
        return shard_[Shard(hash)].Lookup(key, hash);
      }
    
```

將用於追蹤呼叫的 Spanner 資料結構分片。

transaction_manager.cc
```cpp 
    absl::MutexLock l(&active_calls_in_mu_);
    ActiveCallMap::const_iterator iter = active_calls_in_.find(m->tid());
    if (iter != active_calls_in_.end()) {
      iter->second.ExtractElements(&m->tmp_calls_);
    }
    
```
```cpp 
    ActiveCalls::LockedShard shard(active_calls_in_, m->tid());
    const ActiveCallMap& active_calls_map = shard.active_calls_map();
    ActiveCallMap::const_iterator iter = active_calls_map.find(m->tid());
    if (iter != active_calls_map.end()) {
      iter->second.ExtractElements(&m->tmp_calls_);
    }
    
```

如果所討論的資料結構是 Map，請考慮使用併發雜湊表 (concurrent hash map) 實作。

小心用於分片選擇的資訊。例如，如果您使用雜湊值的某些位元進行分片選擇，然後稍後又再次使用這些相同的位元，後者的使用可能會因為雜湊值分布偏移而表現不佳。

修正用於分片選擇的資訊以防止雜湊表問題。

netmon_map_impl.h
```cpp 
    ConnectionBucket* GetBucket(Index index) {
      // 重新雜湊以確保我們不是基於原始雜湊對儲存桶進行分區。
      // 如果 num_buckets_ 是 2 的冪次方，那會降低儲存桶的熵。
      size_t original_hash = absl::Hash<Index>()(index);
      int hash = absl::Hash<size_t>()(original_hash) % num_buckets_;
      return &buckets_[hash];
    }
    
```
```cpp 
    ConnectionBucket* GetBucket(Index index) {
      absl::Hash<std::pair<Index, size_t>> hasher{};
      // 將雜湊值與 42 結合，以防止使用與底層雜湊表相同的位元進行分片選擇。
      return &buckets_[hasher({index, 42}) % num_buckets_];
    }
    
```

將用於追蹤呼叫的 Spanner 資料結構分片。

此 CL 將 `ActiveCallMap` 分為 64 個分片。每個分片都由單獨的 Mutex 保護。給定的事務將精確映射到一個分片。加入了一個新的介面 `LockedShard(tid)`，用於以執行緒安全的方式存取事務的 `ActiveCallMap`。範例用法：

transaction_manager.cc
```cpp 
    {
      absl::MutexLock l(&active_calls_in_mu_);
      delayed_locks_timer_ring_.Add(delayed_locks_flush_time_ms, tid);
    }
    
```
```cpp 
    {
      ActiveCalls::LockedShard shard(active_calls_in_, tid);
      shard.delayed_locks_timer_ring().Add(delayed_locks_flush_time_ms, tid);
    }
    
```

結果顯示，在使用 8192 個 Fiber 執行基準測試時，總體牆鐘時間 (wall-clock time) 減少了 69%。
```cpp 
    基準測試 (Benchmark)           時間 (Time) (ns)    CPU (ns)  迭代次數 (Iterations)
    ------------------------------------------------------------------
    BM_ActiveCalls/8k        11854633492     98766564676            10
    BM_ActiveCalls/16k       26356203552    217325836709            10
    
```
```cpp 
    基準測試 (Benchmark)           時間 (Time) (ns)    CPU (ns)  迭代次數 (Iterations)
    ------------------------------------------------------------------
    BM_ActiveCalls/8k         3696794642     39670670110            10
    BM_ActiveCalls/16k        7366284437     79435705713            10
    
```

### SIMD 指令 (SIMD Instructions)

探索是否使用現代 CPU 上可用的 [SIMD](https://en.wikipedia.org/wiki/Single_instruction,_multiple_data) 指令一次處理多個項目可以帶來加速（例如：參見下面批量操作章節中的 `absl::flat_hash_map` 討論）。

### 減少偽共享 (Reduce false sharing)

如果不同的執行緒存取不同的可變資料，請考慮將不同的資料項放置在不同的快取行上，例如在 C++ 中使用 `alignas` 指令。然而，這些指令很容易被誤用，並可能顯著增加物件大小，因此請確保效能測量證明了它們的使用是合理的。

將常用的突變欄位與其他欄位隔離在不同的快取行中。

histogram.h
```cpp 
    HistogramOptions options_;
    ...
    internal::HistogramBoundaries *boundaries_;
    ...
    std::vector<double> buckets_;
    
    double min_;             // 最小值。
    double max_;             // 最大值。
    double count_;           // 發生次數總計。
    double sum_;             // 值之和。
    double sum_of_squares_;  // 值的平方和。
    ...
    RegisterVariableExporter *exporter_;
    
```
```cpp 
      HistogramOptions options_;
      ...
      internal::HistogramBoundaries *boundaries_;
      ...
      RegisterVariableExporter *exporter_;
      ...
      // 將下列欄位放置在專用快取行中，因為它們經常被突變，
      // 這樣我們可以避免潛在的偽共享。
      ...
    #ifndef SWIG
      alignas(ABSL_CACHELINE_SIZE)
    #endif
      std::vector<double> buckets_;
    
      double min_;             // 最小值。
      double max_;             // 最大值。
      double count_;           // 發生次數總計。
      double sum_;             // 值之和。
      double sum_of_squares_;  // 值的平方和。
    
```

### 減少上下文切換的頻率 (Reduce frequency of context switches)

內聯處理小型工作項，而不是在裝置執行緒池中處理。

cast_op.cc
```cpp 
    template <typename Device, typename Tout, typename Tin>
    void CastMaybeInline(const Device& d, typename TTypes<Tout>::Flat o,
                         typename TTypes<Tin>::ConstFlat i) {
      if (o.size() * (sizeof(Tin) + sizeof(Tout)) < 16384) {
        // CPU 上的小型轉型：內聯執行
        o = i.template cast<Tout>();
      } else {
        o.device(d) = i.template cast<Tout>();
      }
    }
    
```

### 使用緩衝通道進行流水線處理 (Use buffered channels for pipelining)

通道可以是無緩衝的，這意謂著寫入者會阻塞，直到讀取者準備好獲取項目。當通道用於同步時，無緩衝通道可能很有用，但當通道用於增加並列性時則不然。

### 考慮無鎖方法 (Consider lock-free approaches)

有時，無鎖資料結構可以比更傳統的受 Mutex 保護的資料結構帶來差異。然而，直接進行原子變數操作可能很[危險](https://abseil.io/docs/cpp/atomic_danger)。優先選擇更高層次的抽象。

使用無鎖 Map 管理 RPC 通道快取。

RPC Stub 快取中的項目每秒被讀取數千次，且很少修改。切換到適當的無鎖 Map 可將搜尋延遲減少 3%-5%。

使用固定的詞典 + 無鎖雜湊表來加速確定 `IsValidTokenId`。

dynamic_token_class_manager.h
```cpp 
    mutable Mutex mutex_;
    
    // 此雜湊表的密度由動態詞典在嘗試分配新 TokenId 之前重用
    // 之前分配的 TokenId 來保證。
    dense_hash_map<TokenId, common::LocalTokenClassId> tid_to_cid_
        GUARDED_BY(mutex_);
    
```
```cpp 
    // 此雜湊表的讀取存取應使用 'epoch_gc_'::(EnterFast / LeaveFast) 執行。
    // 寫入者應定期透過簡單地呼叫 LockFreeHashMap::CreateGC 來 GC 刪除的項目。
    typedef util::gtl::LockFreeHashMap<TokenId, common::LocalTokenClassId>
        TokenIdTokenClassIdMap;
    TokenIdTokenClassIdMap tid_to_cid_;
    
```

## Protocol Buffer 建議 (Protocol Buffer advice)

Protobuf 是資料的便捷表示形式，特別是如果要透過網路傳送或持久化儲存資料。然而，它們可能具有顯著的效能成本。例如，一段填充 1000 個點並加總 Y 座標的程式碼，從 Protobuf 轉換為 C++ 的 `std::vector` 結構體後，速度提高了 **20 倍**！

兩個版本的基準測試程式碼結果。
```cpp 
    名稱 (name)        舊時間 (old time/op)  新時間 (new time/op)  差異 (delta)
    BenchmarkIteration      17.4µs ± 5%           0.8µs ± 1%        -95.30%  (p=0.000 n=11+12)
    
```

Protobuf 版本：
```cpp 
    message PointProto {
      int32 x = 1;
      int32 y = 2;
    }
    message PointListProto {
      repeated PointProto points = 1;
    }
    
```
```cpp 
    void SumProto(const PointListProto& vec) {
      int sum = 0;
      for (const PointProto& p : vec.points()) {
        sum += p.y();
      }
      ABSL_VLOG(1) << sum;
    }
    
    void BenchmarkIteration() {
      PointListProto points;
      points.mutable_points()->Reserve(1000);
      for (int i = 0; i < 1000; i++) {
        PointProto* p = points.add_points();
        p->set_x(i);
        p->set_y(i * 2);
      }
      SumProto(points);
    }
    
```

非 Protobuf 版本：
```cpp 
    struct PointStruct {
      int x;
      int y;
    };
    
    void SumVector(const std::vector<PointStruct>& vec) {
      int sum = 0;
      for (const PointStruct& p : vec) {
        sum += p.y;
      }
      ABSL_VLOG(1) << sum;
    }
    
    void BenchmarkIteration() {
      std::vector<PointStruct> points;
      points.reserve(1000);
      for (int i = 0; i < 1000; i++) {
        points.push_back({i, i * 2});
      }
      SumVector(points);
    }
    
```

此外，Protobuf 版本向二進制檔案添加了幾 KB 的程式碼和資料，這看起來可能不多，但在具有許多 Protobuf 類型的系統中會迅速累積。這種增加的大小透過產生 i-cache 和 d-cache 壓力來引發效能問題。

以下是一些與 Protobuf 效能相關的技巧：

不要不必要地使用 Protobuf。

鑑於上述 20 倍的效能差異，如果某些資料永遠不會被序列化或解析，您可能不應將其放入 Protocol Buffer 中。Protocol Buffer 的目的是使資料結構的序列化 and 反序列化變得容易，但它們可能具有顯著的程式碼大小、記憶體和 CPU 開銷。如果您想要的只是 `DebugString` 和可複製性等其他優點，請不要使用它們。

避免不必要的訊息層級。

訊息層級對於以更易讀的方式組織資訊很有用。然而，額外的訊息層級會產生成本，如記憶體配置、函式呼叫、快取失誤、較大的序列化訊息等。

例如，與其使用：
```cpp 
    message Foo {
      optional Bar bar = 1;
    }
    message Bar {
      optional Baz baz = 1;
    }
    message Baz {
      optional int32 count = 1;
    }
    
```

優先選擇：
```cpp 
    message Foo {
      optional int32 count = 1;
    }
    
```

Protocol Buffer 訊息對應於 C++ 產生的程式碼中的訊息類別，並在網路上發出標籤和負載長度。為了承載一個整數，舊形式需要更多的配置（和解除配置），並產生更大量的程式碼。因此，所有 Protocol Buffer 操作（解析、序列化、大小計算等）都會變得更昂貴，因為必須遍歷訊息樹。新形式沒有這種開銷，效率更高。

對頻繁出現的欄位使用小的欄位編號。

Protobuf 對欄位編號和網路格式 (wire format) 的組合使用變長整數表示（參見 [Protobuf 編碼文件](https://protobuf.dev/programming-guides/encoding/)）。對於 1 到 15 之間的欄位編號，此表示為 1 位元組，對於 16 到 2047 之間的欄位編號，此表示為 2 位元組。（通常應避免使用 2048 或更大的欄位編號。）

考慮為效能敏感的 Protobuf 的未來擴展預留一些小的欄位編號。

在 `int32`, `sint32`, `fixed32`, 和 `uint32`（以及同樣的 64 位元變體）之間仔細選擇。

通常使用 `int32` 或 `int64`，但對於雜湊碼等大型數值使用 `fixed32` 或 `fixed64`，對於經常為負的數值使用 `sint32` 或 `sint64`。

Varint 佔用較少的位元組來編碼小的整數，可以節省空間，代價是解碼更昂貴。但是，對於負數或大型數值，它可能會佔用更多空間。在這種情況下，使用 `fixed32` 或 `fixed64`（而非 `uint32` 或 `uint64`）可以透過更便宜的編碼和解碼來減小大小。對於小的負整數，使用 `sint32` 或 `sint64` 而非 `int32` 或 `int64`。

對於 proto2，透過標註 `[packed=true]` 來打包重複的數值欄位。

在 proto2 中，重複的值預設序列化為一序列（標籤, 值）對。這效率低下，因為必須為每個元素解碼標籤。

打包的重複 Primitive 在序列化時先發出負載長度，後跟不帶標籤的值。使用固定寬度的值時，我們可以透過在開始解析時就獲知最終大小來避免重新配置；即沒有重新配置成本。我們仍然不知道負載中有多少個 Varint，可能仍需支付重新配置成本。

在 proto3 中，重複欄位預設是打包的。

打包對於 `fixed32`, `fixed64`, `float`, `double` 等固定寬度的值效果最好，因為整個編碼長度 dapat 透過將元素數量乘以固定值大小來預先確定，而無需計算每個單獨元素的長度。

對二進制資料和大型數值使用 `bytes` 而非 `string`。

`string` 類型持有 UTF8 編碼的文本，有時可能需要驗證。`bytes` 類型可以持有任意位元組序列（非文本資料），通常比 `string` 更合適也更有效率。

考慮 `string_type = VIEW` 以避免複製。

在解析期間複製大的字串或位元組欄位很昂貴。這種成本通常可以透過將欄位標記為 `string_type = VIEW` 來避免。
```cpp 
    message Image {
      ...
      bytes jpeg_encoding = 4 [features.(pb.cpp).string_type=VIEW];
    }
    
```

如果沒有 `VIEW` 標註，當解析 Protocol Buffer 時，潛在的大型欄位內容會從序列化的 Protocol Buffer 複製到記憶體中的字串物件。根據字串或位元組欄位的數量以及這些欄位的大小，複製的開銷可能會很顯著。

常式（如 `ParseFromStringWithAliasing`）不會複製大型二進制物件，而是使用 `absl::string_view` 來引用原始備份字串。請注意，原始備份字串（序列化的 Protocol Buffer）的生命週期必須長於包含該別名的 Protocol Buffer 實例。

考慮對大型欄位使用 `Cord` 以降低複製成本。

標註大型 `bytes` 和 `string` 欄位為 `[ctype=CORD]` 可能會降低複製成本。此標註將欄位的表示形式從 `std::string` 更改為 `absl::Cord`。`absl::Cord` 使用引用計數和基於樹的存儲來降低複製和追加成本。如果 Protocol Buffer 被序列化為 Cord，則解析帶有 `[ctype=CORD]` 的字串或位元組欄位可以避免複製欄位內容。
```cpp 
    message Document {
      ...
      bytes html = 4 [ctype = CORD];
    }
    
```

Cord 欄位的效能取決於長度分布和存取模式。使用基準測試來驗證此類更改。

在 C++ 程式碼中使用 Protobuf Arena。

考慮使用 Arena 來節省配置和解除配置成本，特別是對於包含重複、字串或訊息欄位的 Protobuf。

訊息和字串欄位是在堆上配置的（即使頂層 Protocol Buffer 物件是在堆疊上配置的）。如果一個 Protocol Buffer 訊息有很多子訊息欄位和字串欄位，配置和解除配置成本可能會很顯著。Arena 會攤銷配置成本，並使解除配置幾乎免費。它還透過從連續記憶體塊進行配置來改善記憶體局部性。

保持 .proto 檔案較小。

不要在單個 .proto 檔案中放入太多訊息。一旦您依賴 .proto 檔案中的任何內容，整個檔案都會被連結器拉入，即使大部分內容未被使用。這會增加建置時間和二進制檔案大小。您可以使用擴展 (Extensions) 和 `Any` 來避免對具有許多訊息類型的大型 .proto 檔案建立硬依賴。

考慮將 Protocol Buffer 以序列化形式存儲，即使是在記憶體中。

記憶體中的 Protobuf 物件具有較大的記憶體足跡（通常是網路格式大小的 5 倍），並可能分布在許多快取行中。因此，如果您的應用程式將長時間保留許多 Protobuf 物件，請考慮以序列化形式存儲它們。

避免使用 Protobuf Map 欄位。

Protobuf Map 欄位存在效能問題，通常超過了它們提供的微小語法便利。優先使用從 Protobuf 內容初始化的非 Protobuf Map：

msg.proto
```cpp 
    map<string, bytes> env_variables = 5;
    
```
```cpp 
    message Var {
      string key = 1;
      bytes value = 2;
    }
    repeated Var env_variables = 5;
    
```

使用具有欄位子集的 Protobuf 訊息定義。

如果您只想存取大型訊息類型的少數幾個欄位，請考慮定義您自己的、模仿原始類型的 Protocol Buffer 訊息類型，但僅定義您關心的欄位。這是一個範例：
```cpp 
    message FullMessage {
      optional int32 field1 = 1;
      optional BigMessage field2 = 2;
      optional int32 field3 = 3;
      repeater AnotherBigMessage field4 = 4;
      ...
      optional int32 field100 = 100;
    }
    
```
```cpp 
    message SubsetMessage {
      optional int32 field3 = 3;
      optional int32 field88 = 88;
    }
    
```

透過將序列化的 `FullMessage` 解析為 `SubsetMessage`，一百個欄位中僅有兩個被解析，其他欄位被視為未知欄位。在適當時，考慮使用丟棄未知欄位的 API 來進一步提高效能。

盡可能重用 Protobuf 物件。

在迴圈外宣告 Protobuf 物件，以便其分配的儲存空間可以在迴圈迭代之間重用。

## C++ 專屬建議 (C++-Specific advice)

### absl::flat_hash_map (與 set)

[Absl 雜湊表](https://abseil.io/docs/cpp/guides/container) 通常優於 C++ 標準函式庫容器，如 `std::map` 和 `std::unordered_map`。

加速 `LanguageFromCode`（使用 `absl::flat_hash_map` 代替 `__gnu_cxx::hash_map`）。

languages.cc
```cpp 
    class CodeToLanguage
        ...
        : public __gnu_cxx::hash_map<absl::string_view, i18n::languages::Language,
                                     CodeHash, CodeCompare> {
    
```
```cpp 
    class CodeToLanguage
        ...
        : public absl::flat_hash_map<absl::string_view, i18n::languages::Language,
                                     CodeHash, CodeCompare> {
    
```

基準測試結果：
```cpp 
    名稱 (name)        舊時間 (old time/op)  新時間 (new time/op)  差異 (delta)
    BM_CodeToLanguage      19.4ns ± 1%           10.2ns ± 3%        -47.47%  (p=0.000 n=8+10) 
    
```

加速統計發佈/取消發佈（這是一個較舊的更改，因此使用了 `dense_hash_map` 而不是當時尚不存在的 `absl::flat_hash_map`）。

publish.cc
```cpp 
    typedef hash_map<uint64, Publication*> PublicationMap;
    static PublicationMap* publications = NULL;
    
```
```cpp 
    typedef dense_hash_map<uint64, Publication*> PublicationMap;;
    static PublicationMap* publications GUARDED_BY(mu) = NULL;
    
```

使用 `dense_hash_map` 取代 `hash_map` 來追蹤 `SelectServer` 警報（今天會使用 `absl::flat_hash_map`）。

alarmer.h
```cpp 
    typedef hash_map<int, Alarm*> AlarmList;
    
```
```cpp 
    typedef dense_hash_map<int, Alarm*> AlarmList;
    
```

### absl::btree_map/absl::btree_set

`absl::btree_map` 和 `absl::btree_set` 每個樹節點存儲多個項目。與 `std::map` 等有序 C++ 標準函式庫容器相比，這具有許多優勢。首先，指向子樹節點的指標開銷通常顯著減少。其次，由於給定 B-tree 節點的項目或鍵/值在記憶體中是連續存儲的，因此快取效率通常顯著更好。

使用 `btree_set` 取代 `std::set` 來表示一個非常頻繁使用的工作隊列。

register_allocator.h
```cpp 
    using container_type = std::set<WorklistItem>;
    
```
```cpp 
    using container_type = absl::btree_set<WorklistItem>;
    
```

### util::bitmap::InlinedBitVector

`util::bitmap::InlinedBitvector` 可以內聯存儲短的位元向量，因此通常比 `std::vector<bool>` 或其他位圖類型更好的選擇。

使用 `InlinedBitVector` 取代 `std::vector<bool>`，然後使用 `FindNextBitSet` 來尋找下一個感興趣的項目。

block_encoder.cc
```cpp 
    vector<bool> live_reads(nreads);
    ...
    for (int offset = 0; offset < b_.block_width(); offset++) {
      ...
      for (int r = 0; r < nreads; r++) {
        if (live_reads[r]) {
    
```
```cpp 
    util::bitmap::InlinedBitVector<4096> live_reads(nreads);
    ...
    for (int offset = 0; offset < b_.block_width(); offset++) {
      ...
      for (size_t r = 0; live_reads.FindNextSetBit(&r); r++) {
        DCHECK(live_reads[r]);
    
```

### absl::InlinedVector

`absl::InlinedVector` 內聯存儲少量元素（可透過第二個模板引數配置）。這使得多達此數量的元素的小型向量通常具有更好的快取效率，並且在元素數量較少時完全避免配置備份儲存陣列。

在各處使用 `InlinedVector` 取代 `std::vector`。

bundle.h
```cpp 
    class Bundle {
     public:
     ...
     private:
      // (插槽化指令, 非插槽化立即運算元) 序列。
      std::vector<InstructionRecord> instructions_;
      ...
    };
    
```
```cpp 
    class Bundle {
     public:
     ...
     private:
      // (插槽化指令, 非插槽化立即運算元) 序列。
      absl::InlinedVector<InstructionRecord, 2> instructions_;
      ...
    };
    
```

### gtl::vector32

透過使用僅支援符合 32 位元大小的自訂向量類型來節省空間。

簡單的類型更改在 Spanner 中節省了 ~8TiB 記憶體。

table_ply.h
```cpp 
    class TablePly {
        ...
        // 返回為此表存儲在此檔案中的數據列集合。
        const std::vector<FamilyId>& modified_data_columns() const {
          return modified_data_columns_;
        }
        ...
       private:
        ...
        std::vector<FamilyId> modified_data_columns_;  // 表中的數據列。
    
```
```cpp 
    #include "util/gtl/vector32.h"
        ...
        // 返回為此表存儲在此檔案中的數據列集合。
        absl::Span<const FamilyId> modified_data_columns() const {
          return modified_data_columns_;
        }
        ...
    
        ...
        // 表中的數據列。
        gtl::vector32<FamilyId> modified_data_columns_;
    
```

### gtl::small_map

`gtl::small_map` 使用內聯陣列存儲多達一定數量的唯一鍵值對元素，但在空間耗盡時會自動升級為由使用者指定的 Map 類型支援。

在 `tflite_model` 中使用 `gtl::small_map`。

tflite_model.cc
```cpp 
    using ChoiceIdToContextMap = gtl::flat_hash_map<int, TFLiteContext*>;
    
```
```cpp 
    using ChoiceIdToContextMap =
        gtl::small_map<gtl::flat_hash_map<int, TFLiteContext*>>;
    
```

### gtl::small_ordered_set

`gtl::small_ordered_set` 是對關聯容器（如 `std::set` 或 `absl::btree_multiset`）的優化。它使用固定陣列存儲一定數量的元素，然後在空間耗盡時恢復使用 Set 或 Multiset。對於通常較小的 Set，這可能比直接使用 Set 快得多，因為 Set 是針對大數據集優化的。此更改縮小了快取足跡並減少了關鍵區間長度。

使用 `gtl::small_ordered_set` 持有監聽者集合。

broadcast_stream.h
```cpp 
    class BroadcastStream : public ParsedRtpTransport {
     ...
     private:
      ...
      std::set<ParsedRtpTransport*> listeners_ ABSL_GUARDED_BY(listeners_mutex_);
    };
    
```
```cpp 
    class BroadcastStream : public ParsedRtpTransport {
     ...
     private:
      ...
      using ListenersSet =
          gtl::small_ordered_set<std::set<ParsedRtpTransport*>, 10>;
      ListenersSet listeners_ ABSL_GUARDED_BY(listeners_mutex_);
    
```

### gtl::intrusive_list

`gtl::intrusive_list<T>` 是一個雙向鏈結串列，其中鏈結指標嵌入在 T 類型的元素中。與 `std::list<T*>` 相比，它每個元素節省了一個快取行和間接層。

使用 `intrusive_list` 追蹤每個索引行更新的在途請求。

row-update-sender-inflight-set.h
```cpp 
    std::set<int64> inflight_requests_ GUARDED_BY(mu_);
    
```
```cpp 
    class SeqNum : public gtl::intrusive_link<SeqNum> {
      ...
      int64 val_ = -1;
      ...
    };
    ...
    gtl::intrusive_list<SeqNum> inflight_requests_ GUARDED_BY(mu_);
    
```

### 限制 absl::Status 和 absl::StatusOr 的使用 (Limit absl::Status and absl::StatusOr usage)

儘管 `absl::Status` 和 `absl::StatusOr` 類型相當高效，但即使在成功路徑上它們也具有非零開銷，因此對於不需要返回任何有意義錯誤細節（或者甚至永遠不會失敗！）的熱點常式，應避免使用它們：

為 `RoundUpToAlignment()` 函式避免 `StatusOr<int64>` 返回類型。

best_fit_allocator.cc
```cpp 
    absl::StatusOr<int64> BestFitAllocator::RoundUpToAlignment(int64 bytes) const {
      TPU_RET_CHECK_GE(bytes, 0);
    
      const int64 max_aligned = MathUtil::RoundDownTo<int64>(
          std::numeric_limits<int64>::max(), alignment_in_bytes_);
      if (bytes > max_aligned) {
        return util::ResourceExhaustedErrorBuilder(ABSL_LOC) 
               << "嘗試分配 "
               << strings::HumanReadableNumBytes::ToString(bytes)
               << ", 對齊到 "
               << strings::HumanReadableNumBytes::ToString(alignment_in_bytes_)
               << " 後無法表示為 int64。";
      }
    
      return MathUtil::RoundUpTo<int64>(bytes, alignment_in_bytes_);
    }
    
```

best_fit_allocator.h
```cpp 
    // 將位元組向上舍入到最接近的 alignment_ 的倍數。
    // 要求：bytes >= 0。
    // 要求：結果不溢出 int64。
    // 要求：alignment_in_bytes_ 是 2 的冪次方（在建構子中檢查）。
    int64 RoundUpToAlignment(int64 bytes) const {
      DCHECK_GE(bytes, 0);
      DCHECK_LE(bytes, max_aligned_bytes_);
      int64 result =
          ((bytes + (alignment_in_bytes_ - 1)) & ~(alignment_in_bytes_ - 1));
      DCHECK_EQ(result, MathUtil::RoundUpTo<int64>(bytes, alignment_in_bytes_));
      return result;
    }
    
```

加入 `ShapeUtil::ForEachIndexNoStatus` 以避免為 Tensor 的每個元素建立 Status 返回物件。

shape_util.h
```cpp 
    using ForEachVisitorFunction = 
        absl::FunctionRef<StatusOr<bool>(absl::Span<const int64_t>)>;
        ...
    static void ForEachIndex(const Shape& shape, absl::Span<const int64_t> base,
                             absl::Span<const int64_t> count, 
                             absl::Span<const int64_t> incr,
                             const ForEachVisitorFunction& visitor_function);
    
    
```
```cpp 
    using ForEachVisitorFunctionNoStatus = 
        absl::FunctionRef<bool(absl::Span<const int64_t>)>;
        ...
    static void ForEachIndexNoStatus(
        const Shape& shape, absl::Span<const int64_t> base,
        absl::Span<const int64_t> count, absl::Span<const int64_t> incr,
        const ForEachVisitorFunctionNoStatus& visitor_function);
    
```

literal.cc
```cpp 
    ShapeUtil::ForEachIndex(
        result_shape, [&](absl::Span<const int64_t> output_index) {
          for (int64_t i = 0, end = dimensions.size(); i < end; ++i) {
            scratch_source_index[i] = output_index[dimensions[i]];
          }
          int64_t dest_index = IndexUtil::MultidimensionalIndexToLinearIndex(
              result_shape, output_index);
          int64_t source_index = IndexUtil::MultidimensionalIndexToLinearIndex(
              shape(), scratch_source_index);
          memcpy(dest_data + primitive_size * dest_index,
                 source_data + primitive_size * source_index, primitive_size);
          return true;
        });
    
```
```cpp 
    ShapeUtil::ForEachIndexNoStatus(
        result_shape, [&](absl::Span<const int64_t> output_index) {
          // 計算 dest_index
          int64_t dest_index = IndexUtil::MultidimensionalIndexToLinearIndex(
              result_shape, result_minor_to_major, output_index);
    
          // 計算 source_index
          int64_t source_index;
          for (int64_t i = 0, end = dimensions.size(); i < end; ++i) {
            scratch_source_array[i] = output_index[dimensions[i]];
          }
          if (src_shape_dims == 1) {
            // 此情況的快速路徑
            source_index = scratch_source_array[0];
            DCHECK_EQ(source_index, 
                      IndexUtil::MultidimensionalIndexToLinearIndex(
                          src_shape, src_minor_to_major, scratch_source_span));
          } else {
            source_index = IndexUtil::MultidimensionalIndexToLinearIndex(
                src_shape, src_minor_to_major, scratch_source_span);
          }
          // 將一個元素從源中的 source_index 移動到目標中的 dest_index
          memcpy(dest_data + PRIMITIVE_SIZE * dest_index,
                 source_data + PRIMITIVE_SIZE * source_index, PRIMITIVE_SIZE);
          return true;
        });
    
```

在 `TF_CHECK_OK` 中，避免為了測試 `ok()` 而建立 Ok 物件。

status.h
```cpp 
    #define TF_CHECK_OK(val) CHECK_EQ(::tensorflow::Status::OK(), (val))
    #define TF_QCHECK_OK(val) QCHECK_EQ(::tensorflow::Status::OK(), (val))
    
```
```cpp 
    extern tensorflow::string* TfCheckOpHelperOutOfLine(
        const ::tensorflow::Status& v, const char* msg);
    inline tensorflow::string* TfCheckOpHelper(::tensorflow::Status v, 
                                               const char* msg) {
      if (v.ok()) return nullptr;
      return TfCheckOpHelperOutOfLine(v, msg);
    }
    #define TF_CHECK_OK(val)                                           \
      while (tensorflow::string* _result = TfCheckOpHelper(val, #val)) \
      LOG(FATAL) << *(_result)
    #define TF_QCHECK_OK(val)                                          \
      while (tensorflow::string* _result = TfCheckOpHelper(val, #val)) \
      LOG(QFATAL) << *(_result)
    
```

從遠程程序呼叫 (RPC) 的熱點路徑中移除 `StatusOr`。

從熱點路徑移除 `StatusOr` 消除了一個由早期更改引起的 RPC 基準測試中 14% 的 CPU 退化。

privacy_context.h
```cpp 
    absl::StatusOr<privacy::context::PrivacyContext> GetRawPrivacyContext(
        const CensusHandle& h);
    
```

privacy_context_statusfree.h
```cpp 
    enum class Result { 
      kSuccess,
      kNoRootScopedData,
      kNoPrivacyContext,
      kNoDDTContext,
      kDeclassified,
      kNoPrequestContext
    };
    ...
    Result GetRawPrivacyContext(const CensusHandle& h,
                                PrivacyContext* privacy_context);
    
```

## 批量操作 (Bulk operations)

如果可能，一次處理多個項目，而不是僅處理一個。

`absl::flat_hash_map` 使用單個 SIMD 指令從一組鍵中比較每個鍵的一個雜湊位元組。

參見 [Swiss Table 設計筆記](https://abseil.io/about/design/swisstables) 及 Matt Kulukundis 相關的 [CppCon 2017](https://www.youtube.com/watch?v=ncHmEUmJZf4) 和 [CppCon 2019](https://www.youtube.com/watch?v=JZE3_0qvrMg) 演講。

raw_hash_set.h
```cpp 
    // 返回一個位元遮罩，表示與雜湊匹配的插槽位置。
    BitMask<uint32_t> Match(h2_t hash) const {
      auto ctrl = _mm_loadu_si128(reinterpret_cast<const __m128i*>(pos));
      auto match = _mm_set1_epi8(hash);
      return BitMask<uint32_t>(_mm_movemask_epi8(_mm_cmpeq_epi8(match, ctrl)));
    }
    
```

執行單個操作來處理多個位元組並進行修正，而不是檢查每個位元組該做什麼。

ordered-code.cc
```cpp 
    int len = 0;
    while (val > 0) {
      len++;
      buf[9 - len] = (val & 0xff);
      val >>= 8;
    }
    buf[9 - len - 1] = (unsigned char)len;
    len++;
    FastStringAppend(dest, reinterpret_cast<const char*>(buf + 9 - len), len);
    
```
```cpp 
    BigEndian::Store(val, buf + 1);  // buf[0] 可能需要用於長度
    const unsigned int length = OrderedNumLength(val);
    char* start = buf + 9 - length - 1;
    *start = length;
    AppendUpto9(dest, start, length + 1);
    
```

透過更有效地分塊處理多個交錯的輸入緩衝區，提高 Reed-Solomon 處理速度。
```cpp 
    Run on (12 X 3501 MHz CPUs); 2016-09-27T16:04:55.065995192-04:00
    CPU: Intel Haswell with HyperThreading (6 cores) dL1:32KB dL2:256KB dL3:15MB
    基準測試 (Benchmark)              基準 (Base) (ns)  新 (New) (ns) 改進 (Improvement)
    ------------------------------------------------------------------
    BM_OneOutput/3/2                      466867    351818    +24.6%
    BM_OneOutput/4/2                      563130    474756    +15.7%
    BM_OneOutput/5/3                      815393    688820    +15.5%
    BM_OneOutput/6/3                      897246    780539    +13.0%
    BM_OneOutput/8/4                     1270489   1137149    +10.5%
    BM_AllOutputs/3/2                     848772    642942    +24.3%
    BM_AllOutputs/4/2                    1067647    638139    +40.2%
    BM_AllOutputs/5/3                    1739135   1151369    +33.8%
    BM_AllOutputs/6/3                    2045817   1456744    +28.8%
    BM_AllOutputs/8/4                    3012958   2484937    +17.5%
    BM_AllOutputsSetUpOnce/3/2            717310    493371    +31.2%
    BM_AllOutputsSetUpOnce/4/2            833866    600060    +28.0%
    BM_AllOutputsSetUpOnce/5/3           1537870   1137357    +26.0%
    BM_AllOutputsSetUpOnce/6/3           1802353   1398600    +22.4%
    BM_AllOutputsSetUpOnce/8/4           3166930   2455973    +22.4%
    
```

一次解碼四個整數（約 2004 年）。

引入了 [GroupVarInt 格式](https://static.googleusercontent.com/media/research.google.com/en//people/jeff/WSDM09-keynote.pdf)，它一次在 5-17 位元組中編碼/解碼一組 4 個變長整數，而不是一次一個。解碼新格式中的一組 4 個整數僅需解碼 4 個單獨 Varint 編碼整數所需時間的約 1/3。

groupvarint.cc
```cpp 
    const char* DecodeGroupVar(const char* p, int N, uint32* dest) {
      assert(groupvar_initialized);
      assert(N % 4 == 0);
      while (N) {
        uint8 tag = *p;
        p++;
    
        uint8* lenptr = &groupvar_table[tag].length[0];
    
    #define GET_NEXT                                        \
        do {                                                \
          uint8 len = *lenptr;
          *dest = UNALIGNED_LOAD32(p) & groupvar_mask[len]; \
          dest++;                                           \
          p += len;                                         \
          lenptr++;                                         \
        } while (0)
        GET_NEXT;
        GET_NEXT;
        GET_NEXT;
        GET_NEXT;
    #undef GET_NEXT
    
        N -= 4;
      }
      return p;
    }
    
```

一次編碼一組 4 個 k 位元數字。

添加了 `KBitStreamEncoder` 和 `KBitStreamDecoder` 類別，用於將一組 4 個 k 位元數字編碼/解碼到位元流中。由於 K 在編譯時已知，編碼和解碼可以非常高效。例如，由於一次編碼四個數字，程式碼可以假設流始終是位元組對齊的（對於偶數 k）或半位元組對齊的（對於奇數 k）。

## 展示多種技術的 CL (CLs that demonstrate multiple techniques)

有時，單個 CL 包含許多使用上述多種技術的效能改進變更。查看這些 CL 中的變更類型有時是進入在將系統某部分識別為瓶頸後加速其效能的通用變更思維模式的好方法。

將 GPU 記憶體分配器速度提升約 40%。

`GPUBFCAllocator` 的配置/解除配置速度提升 36-48%：

  1. 透過控制代碼編號而非 `Chunk` 指標來識別區塊。`Chunk` 資料結構現在配置在 `vector<Chunk>` 中，控制代碼是該向量的索引，用於引用特定區塊。這使得 `Chunk` 中的 `next` 和 `prev` 指標可以是 `ChunkHandle` (4 位元組)，而不是 `Chunk*` (8 位元組)。

  2. 當 `Chunk` 物件不再使用時，我們維護一個 `Chunk` 物件的空閒列表，其頭部由 `ChunkHandle free_chunks_list_` 指定，且 `Chunk->next` 指向下一個空閒列表項。結合 (1)，這使我們能夠避免在分配器中對 `Chunk` 物件進行堆配置/解除配置，除非（極少數情況下）`vector<Chunk>` 增長。它還使所有 `Chunk` 物件的記憶體連續。

  3. 我們不再讓 `bins_` 資料結構成為 `std::set` 並使用 `lower_bound` 來根據 `byte_size` 定位合適的儲存桶，而是擁有一個儲存桶陣列，由 `log₂(byte_size/256)` 函式索引。這允許透過幾次位元操作定位儲存桶，而不是透過二進制搜尋樹查詢。它還允許我們在連續陣列中為所有 `Bin` 資料結構配置儲存，而不是在許多不同的快取行中。這減少了多執行緒執行配置時必須在核心之間移動的快取行數量。

  4. 為 `GPUBFCAllocator::AllocateRaw` 添加了快速路徑，該路徑首先嘗試在不涉及 `retry_helper_` 的情況下配置記憶體。如果初始嘗試失敗（返回 `nullptr`），則我們透過 `retry_helper_`，但通常我們可以避免多層程序呼叫以及帶有多個引數的 `std::function` 的配置/解除配置。

  5. 註釋掉了大部分 `VLOG` 呼叫。這些可以在需要除錯時透過取消註釋並重新編譯來選擇性地重新啟用。

加入了多執行緒基準測試，以測試競爭下的配置。

在我的配備 Titan X 顯卡的桌上型電腦上，將 `ptb_word_lm` 的速度從每秒 8036 個單詞提升到 8272 個單詞 (+2.9%)。
```cpp 
    Run on (40 X 2801 MHz CPUs); 2016/02/16-15:12:49
    CPU: Intel Ivybridge with HyperThreading (20 cores) dL1:32KB dL2:256KB dL3:25MB
    基準測試 (Benchmark)              基準 (Base) (ns)  新 (New) (ns) 改進 (Improvement)
    ------------------------------------------------------------------
    BM_Allocation                            347       184    +47.0%
    BM_AllocationThreaded/1                  351       181    +48.4%
    BM_AllocationThreaded/4                 2470      1975    +20.0%
    BM_AllocationThreaded/16               11846      9507    +19.7%
    BM_AllocationDelayed/1                   392       199    +49.2%
    BM_AllocationDelayed/10                  285       169    +40.7%
    BM_AllocationDelayed/100                 245       149    +39.2%
    BM_AllocationDelayed/1000                238       151    +36.6%
    
```

透過一系列雜項更改將 Pathways 吞吐量提高約 20%。

  * 將一系列特殊的快速描述符解析函式統一到單個 `ParsedDescriptor` 類別中，並在更多地方使用此類別以避免昂貴的完整解析呼叫。

  * 將幾個 Protocol Buffer 欄位從 `string` 更改為 `bytes`（避免不必要的 UTF-8 檢查及相關的錯誤處理程式碼）。

  * `DescriptorProto.inlined_contents` 現在是 `string` 而非 `Cord`（預期僅用於小型 Tensor）。這需要加入一系列 `tensor_util.cc` 中的複製輔助函式（現在需要同時支援 `string` 和 `Cord`）。

  * 在一些地方使用 `flat_hash_map` 取代 `std::unordered_map`。

  * 加入 `MemoryManager::LookupMany` 供 Stack 運算使用，而不是為每個批次元素呼叫 `Lookup`。此更改減少了鎖定等設定開銷。

  * 移除了 `TransferDispatchOp` 中一些不必要的字串建立。

  * 在同一程序中將 1000 個 1KB Tensor 的批次從一個組件傳輸到另一個組件的效能結果：
```cpp 
    之前 (Before): 227.01 steps/sec
    之後 (After):  272.52 steps/sec (+20% 吞吐量)
    
```

透過一系列更改將 XLA 編譯器效能提升約 15%。

一些加速 XLA 編譯的更改：

  1. 在 `SortComputationsByContent` 中，如果比較函式中 `a == b` 則返回 `false`，以避免序列化和指紋識別長計算字串。

  2. 將 `CHECK` 轉為 `DCHECK` 以避免在 `HloComputation::ComputeInstructionPostOrder` 中觸及額外的快取行。

  3. 避免在 `CoreSequencer::IsVectorSyncHoldSatisfied()` 中對前端指令進行昂貴的複製。

  4. 重新設計雙引數 `HloComputation::ToString` 和 `HloComputation::ToCord` 常式，使其大部分工作透過追加到 `std::string` 而不是追加到 `Cord` 來完成。

  5. 將 `PerformanceCounterSet::Increment` 更改為僅執行單次雜湊表查詢而非兩次。

  6. 精簡 `Scoreboard::Update` 程式碼。

整體而言，某個重要模型的 XLA 編譯時間縮短了 14%。

加速 Google Meet 應用程式碼中的低階日誌記錄。

加速 `ScopedLogId`，它位於每個封包的關鍵路徑上。

  * 移除了 `LOG_EVERY_N(ERROR, ...)` 訊息，這些訊息似乎僅用於查看不變量是否被違反。
  * 內聯了 `PushLogId` 和 `PopLogid()` 常式（因為沒有了 `LOG_EVERY_N_SECONDS(ERROR, ...)` 語句，它們現在足夠小以進行內聯）。
  * 切換到使用大小為 4 的固定陣列和一個 `int size` 變數，而不是使用 `InlinedVector<...>` 來維護執行緒局部狀態。由於我們的大小從未超過 4，因此 `InlinedVector` 的功能超出了需求。

```cpp 
    基準 (Base): 基準線加上 scoped_logid_test.cc 中加入基準測試的程式碼
    新 (New): 此變更列表 (CL)
    
    CPU: Intel Ivybridge with HyperThreading (20 cores) dL1:32KB dL2:256KB dL3:25MB
    基準測試 (Benchmark)                           基準 (Base) (ns)    新 (New) (ns) 改進 (Improvement)
    ----------------------------------------------------------------------------
    BM_ScopedLogId/threads:1                               8           4    +52.6%
    BM_ScopedLogId/threads:2                               8           4    +51.9%
    BM_ScopedLogId/threads:4                               8           4    +52.9%
    BM_ScopedLogId/threads:8                               8           4    +52.1%
    BM_ScopedLogId/threads:16                             11           6    +44.0%
    
```

透過改進 Shape 處理，將 XLA 編譯時間縮短約 31%。

改進 XLA 編譯器效能的幾項更改：

  1. 透過以下幾種方式改進了 `ShapeUtil::ForEachIndex...` 迭代的效能：

     * 在 `ShapeUtil::ForEachState` 中，僅儲存由 Span 表示的陣列指標，而非完整的 Span 物件。

     * 預先形成一個指向 `ShapeUtil::ForEachState::indexes` 向量的 `ShapeUtil::ForEachState::indexes_span`，而不是在每次迴圈迭代時從向量建構此 Span。

     * 儲存指向 `ShapeUtil::ForEachState::indexes` 向量備份儲存的 `ShapeUtil::ForEachState::indexes_ptr` 指標，在 `ShapeUtil::ForEachState::IncrementDim()` 中允許簡單的陣列操作，而非更昂貴的 `vector::operator[]` 操作。

     * 儲存一個在建構子中透過呼叫 `shape.layout().minor_to_major().data()` 初始化的 `minor_to_major` 陣列指標，而不是在每次迭代中為每個維度呼叫 `LayoutUtil::Minor(...)`。

     * 內聯了 `ShapeUtil::ForEachState` 建構子和 `ShapeUtil::ForEachState::IncrementDim()` 常式。

  2. 改進了不需要在傳入函式中返回 Status 功能的呼叫點的 `ShapeUtil::ForEachIndex` 迭代效能。透過引入 `ShapeUtil::ForEachIndexNoStatus` 變體實作，該變體接受 `ForEachVisitorFunctionNoStatus`（返回純 `bool`）。這比接受 `ForEachVisitorFunction`（返回 `StatusOr<bool>`，這在我們迭代的每個元素上都需要昂貴的 `StatusOr<bool>` 析構函式呼叫）的 `ShapeUtil::ForEachIndex` 常式更快。

     * 在 `LiteralBase::Broadcast` 和 `GenerateReduceOutputElement` 中使用了此 `ShapeUtil::ForEachIndexNoStatus` 變體。

  3. 透過幾種方式改進了 `LiteralBase::Broadcast` 的效能：

     * 在 `literal.cc` 中引入了針對不同 Primitive 位元組大小進行特化的模板化 `BroadcastHelper` 常式（沒有這個，`primitive_size` 是一個執行時變數，因此編譯器無法很好地優化每個元素髮生的 `memcpy`，並且會呼叫假設位元組計數相當大的通用 `memcpy` 路徑，即使在我們的情況下它是微小的 2 的冪次方（通常為 1, 2, 4 或 8））。

     * 透過在 `LiteralBase::Broadcast` 常式開始時單次呼叫 `shape()`，避免了每次 Broadcast 呼叫中除一次外的所有約 `~(5 + 維度數量 + 結果元素數量)` 次虛擬呼叫。散布在各處的看起來無害的 `shape()` 呼叫最終歸結為 `root_piece().subshape()`，其中 `subshape()` 是一個虛擬函式。

     * 在 `BroadcastHelper` 常式中，針對來源維度為 1 的情況進行了特殊處理，並避免了對此情況呼叫 `IndexUtil::MultiDimensionalIndexToLinearIndex`。

     * 在 `BroadcastHelper` 中，使用指向 `scratch_source_index` 向量備份儲存的 `scratch_source_array` 指標變數，並直接使用它以避免在每元素程式碼內部執行 `vector::operator[]` 操作。還在 `BroadcastHelper` 的每元素迴圈之外預先計算了一個指向 `scratch_source_index` 向量的 `scratch_source_span`，以避免在每個元素上從向量建構 Span。

     * 引入了新的三引數變體 `IndexUtil::MultiDimensionalIndexToLinearIndex`，其中呼叫者傳入與 shape 引數相關聯的 `minor_to_major` Span。在 `BroadcastHelper` 中使用它來為來源和目標 Shape 每 Broadcast 計算一次，而不是每複製一個元素計算一次。

  4. 在 `ShardingPropagation::GetShardingFromUser` 中，對於 `HloOpcode::kTuple` 情況，僅當我們發現該運算元值得關注時才呼叫 `user.sharding().GetSubSharding(...)`。避免主動呼叫它使一個冗長編譯中的此常式 CPU 時間從 43.7s 減少到 2.0s。

  5. 為 `ShapeUtil::ForEachIndex` 和 `Literal::Broadcast` 以及新的 `ShapeUtil::ForEachIndexNoStatus` 加入了基準測試。
```cpp 
    基準 (Base) 是加入了 BM_ForEachIndex 和 BM_BroadcastVectorToMatrix 基準測試（以及加入基準測試依賴項的 BUILD 檔案更改），但沒有其他更改。
    
    新 (New) 是此 CL。
    
    Run on (72 X 1357.56 MHz CPU s) CPU 快取：L1 Data 32 KiB (x36)
    L1 Instruction 32 KiB (x36) L2 Unified 1024 KiB (x36) L3 Unified 25344 KiB (x2)
    
    Benchmark                                      Base (ns)    New (ns) Improvement
    ----------------------------------------------------------------------------
    BM_MakeShape                                       18.40       18.90     -2.7%
    BM_MakeValidatedShape                              35.80       35.60     +0.6%
    BM_ForEachIndex/0                                  57.80       55.80     +3.5%
    BM_ForEachIndex/1                                  90.90       85.50     +5.9%
    BM_ForEachIndex/2                               1973606     1642197     +16.8%
    
```

新加入的 `ForEachIndexNoStatus` 比 `ForEachIndex` 變體明顯快得多（它僅存在於此新 CL 中，但 `BM_ForEachIndexNoStatus/NUM` 執行的基準測試工作與上述 `BM_ForEachIndex/NUM` 結果相當）。
```cpp 
    Benchmark                                      Base (ns)    New (ns) Improvement
    ----------------------------------------------------------------------------
    BM_ForEachIndexNoStatus/0                             0        46.90    ----
    BM_ForEachIndexNoStatus/1                             0        65.60    ----
    BM_ForEachIndexNoStatus/2                             0     1001277     ----
    
```

Broadcast 效能提高了約 58%。
```cpp 
    Benchmark                                      Base (ns)    New (ns) Improvement
    ----------------------------------------------------------------------------
    BM_BroadcastVectorToMatrix/16/16                   5556        2374     +57.3%
    BM_BroadcastVectorToMatrix/16/1024               319510      131075     +59.0%
    BM_BroadcastVectorToMatrix/1024/1024           20216949     8408188     +58.4%
    
```

對一個大型語言模型進行提前編譯 (AOT) 的巨觀結果（程式不僅僅執行 XLA 編譯，但花費了不到一半的時間在 XLA 相關程式碼中）：

整體基準程式：573 秒 使用此 CL 的整體程式：465 秒 (+19% 改進)

執行此程式中編譯兩個最大的 XLA 程式所花費的時間：

基準線：141s + 143s = 284s 使用此 CL：99s + 95s = 194s (+31% 改進)

在 Plaque（一個分散式執行框架）中將大型程式的編譯時間縮短約 22%。

微調以加速編譯約 22%：

  1. 加速偵測兩個節點是否共享共同來源。以前，我們會按排序順序取得每個節點的來源，然後執行排序交集。我們現在將一個節點的來源放入雜湊表中，然後迭代另一個節點的來源並檢查雜湊表。
  2. 重用步驟 1 中的同一個暫存雜湊表。
  3. 生成編譯後的 Proto 時，保持單個由 `pair<package, opname>` 作為鍵的 B-tree，而不是 B-tree 的 B-tree。
  4. 在上述 B-tree 中儲存指向 `opdef` 的指標，而不是將 `opdef` 複製到 B-tree 中。

對大型程式（約 4.5 萬個運算）的速度測量：
```cpp 
    名稱 (name)        舊時間 (old time/op)  新時間 (new time/op)  差異 (delta)
    BM_CompileLarge        28.5s ± 2%            22.4s ± 2%        -21.61%  (p=0.008 n=5+5)
    
```

MapReduce 改進（單詞計數基準測試加速約 2 倍）。

MapReduce 加速：

  1. 更改了 `SafeCombinerMapOutput` 類別的 Combiner 資料結構。我們不再使用 `hash_multimap<SafeCombinerKey, StringPiece>`（它為表中插入的每個唯一鍵值對都有一個雜湊表項），而是使用 `hash_map<SafeCombinerKey, ValuePtr*>`（其中 `ValuePtr` 是值和重複計數的鏈結串列）。這在三方面有幫助：

     * 它顯著減少了記憶體使用，因為我們對每個值僅使用 `sizeof(ValuePtr) + value_len` 位元組，而不是為每個值使用 `sizeof(SafeCombinerKey) + sizeof(StringPiece) + value_len + 新雜湊表項開銷`。這意謂著我們刷新 Reducer 緩衝區的頻率更低。

     * 它明顯更快，因為當我們為表中已存在的鍵插入新值時，我們避免了額外的雜湊表項（相反地，我們只需將值掛接到該鍵的值鏈結串列中）。

     * 由於我們為鏈結串列中的每個值關聯了一個重複計數，我們可以將此序列：
```cpp Output(key, "1");
           Output(key, "1");
           Output(key, "1");
           Output(key, "1");
           Output(key, "1");
           
```

表示為「key」鏈結串列中的單個條目，重複計數為 5。內部我們向使用者層級的 Combining 函式產出 5 次「1」。(類似的技巧或許也可以應用於 Reduce 端)。

  2. (次要) 為預設的 `MapReductionBase::KeyFingerprintSharding` 函式添加了 `nshards == 1` 的測試，如果我們僅使用 1 個 Reduce 分片，則完全避免對鍵進行指紋識別（因為在這種情況下我們可以不檢查鍵直接返回 0）。

  3. 在為每個添加到 Combiner 的鍵值對呼叫的程式碼路徑中，將一些 `VLOG(3)` 語句改為 `DVLOG(3)`。

將一個單詞計數基準測試的時間從 12.56s 縮短到 6.55s。

重構 `SelectServer` 中的警報處理程式碼，以顯著提高其效能（添加 + 移除警報從 771 ns 降至 271 ns）。

重構了 `SelectServer` 中的警報處理程式碼，以顯著提高其效能。

更改：

  1. 切換為對 `AlarmQueue` 使用 `AdjustablePriorityQueue<Alarm>` 而非 `set<Alarm*>`。這顯著加速了警報處理，將添加和移除警報的時間從 771 奈秒縮短到 281 奈秒。此更改避免了每次警報設定時的配置/解除配置（針對 STL set 物件中的紅黑樹節點），並且還提供了更好的快取局部性（因為 `AdjustablePriorityQueue` 是在向量中實作的堆，而非紅黑樹），在每次通過 selectserver 迴圈操作 `AlarmQueue` 時觸及的快取行更少。

  2. 將 `Alarmer` 中的 `AlarmList` 從 `hash_map` 轉換為 `dense_hash_map`，以避免在警報添加/刪除時發生另一次配置/解除配置（這也改善了添加/移除警報時的快取局部性）。

  3. 移除了 `num_alarms_stat_` 和 `num_closures_stat_` `MinuteTenMinuteHourStat` 物件以及相應的導出變數。雖然監控這些看起來不錯，但在實踐中它們為關鍵網路程式碼添加了顯著開銷。如果我將這些變數保留為 `Atomic32` 變數而非 `MinuteTenMinuteHourStat`，它們仍會將添加和移除警報的成本從 281 奈秒增加到 340 奈秒。

基準測試結果
```cpp 
    Benchmark                      Time(ns)  CPU(ns) Iterations
    -----------------------------------------------------------
    BM_AddAlarm/1                       902      771     777777
    
```

使用此更改
```cpp 
    Benchmark                      Time(ns)  CPU(ns) Iterations
    -----------------------------------------------------------
    BM_AddAlarm/1                       324      281    2239999
    
```

索引服務速度提升 3.3 倍！

我們在 2001 年計劃將索引服務從磁碟切換到記憶體時發現了許多效能問題。此更改修復了許多這些問題，並使我們從每秒 150 次記憶體查詢提升到超過 500 次（針對雙 Pentium III 處理器機器上的 2 GB 記憶體索引）。

  * 索引區塊解碼速度的多項改進（微基準測試從 8.9 MB/s 提升到 13.1 MB/s）。
  * 我們現在在解碼期間對區塊進行校驗和。這使我們能夠在執行所有 `getsymbol` 操作時不進行任何邊界檢查。
  * 我們擁有粗糙的巨集，在整個迴圈中將 `BitDecoder` 的各個欄位保存在局部變數中，然後在迴圈結束時將它們存回。
  * 我們使用內聯組合語言來調用 Intel 晶片上的 `bsf` 指令以實現 `getUnary` (尋找字中第一個 1 位元的索引)。
  * 將值解碼到向量中時，我們在迴圈外調整向量大小，並僅沿著向量移動指標，而不是執行帶邊界檢查的存取來儲存每個值。
  * 在 DocId 解碼期間，我們將 DocId 保留在局部 DocId 空間中，以避免乘以 `num_shards_`。僅當我們與需實際的 DocId 值時，我們才乘以 `num_shards_` 並加上 `my_shard_`。
  * `IndexBlockDecoder` 現在導出了一個 `AdvanceToDocid` 介面，該介面返回第一個 DocId ≥ "d" 的索引。這允許根據局部 DocId 執行掃描，而不是在客戶端為區塊中的每個索引呼叫 `GetDocid(index)` 時強制轉換每個局部 DocId 為全域 DocId。
  * 文件的位置資料解碼現在改為按需執行，而不是在客戶端要求區塊內任何文件的位置資料時為整個區塊主動執行。
  * 如果正在解碼的索引區塊結束於頁面邊界 4 位元組以內，我們將其複製到局部緩衝區。這使我們始終可以透過 4 位元組載入來載入位元解碼緩衝區，而無需擔心如果跑出 mmap 頁面末尾會發生段錯誤 (seg fault)。
  * 我們僅初始化各種評分資料結構的前 `nterms_` 個元素，而不是初始化所有 `MAX_TERMS` 個元素（在某些情況下，我們為評分的每個文件不必要地 memsetting 了 20K 到 100K 的資料）。
  * 當計算出的值為 0 時，避免 `round_to_int` 及隨後對中間評分值的計算（隨後的計算只是在我們 memset 的 0 上寫入 '0'，而這是最常見的情況）。
  * 將評分資料結構上的邊界檢查改為除錯模式斷言 (assertion)。

## 延伸閱讀 (Further reading)

排名不分先後，作者發現有助於了解效能的書籍和文章列表：

  * Agner Fog 的 [Optimizing software in C++](https://www.agner.org/optimize/optimizing_cpp.pdf)。描述了許多用於改進效能的有用的低階技術。
  * Richard L. Sites 的 [Understanding Software Dynamics](https://www.oreilly.com/library/view/understanding-software-dynamics/9780137589692/)。涵蓋了用於診斷和修復效能問題的專家方法和先進工具。
  * [Performance tips of the week](https://abseil.io/fast/) - 有用技巧的合集。
  * [Performance Matters](https://travisdowns.github.io/) - 關於效能的文章合集。
  * [Daniel Lemire 的網誌](https://lemire.me/blog/) - 有趣演算法的高效能實作。
  * [Building Software Systems at Google and Lessons Learned](https://www.youtube.com/watch?v=modXC5IWTJI) - 一個影片，描述了 Google 十年來遇到的系統效能問題。
  * Jon Bentley 的 [Programming Pearls](https://books.google.com/books/about/Programming_Pearls.html?id=kse_7qbWbjsC) 和 [More Programming Pearls: Confessions of a Coder](https://books.google.com/books/about/More_Programming_Pearls.html?id=a2AZAQAAIAAJ)。關於從演算法開始並以簡單高效的實作結束的文章。
  * Henry S. Warren 的 [Hacker’s Delight](https://en.wikipedia.org/wiki/Hacker%27s_Delight)。用於解決一些常見問題的位元級和算術演算法。
  * John L. Hennessy 和 David A. Patterson 的 [Computer Architecture: A Quantitative Approach](https://books.google.com/books/about/Computer_Architecture.html?id=cM8mDwAAQBAJ) - 涵蓋了計算機架構的許多方面，包括效能導向的軟體開發人員應該了解的內容，如快取、分支預測器、TLB 等。

## 建議引用 (Suggested citation)

如果您想引用此文件，我們建議：
```cpp 
    Jeffrey Dean & Sanjay Ghemawat, Performance Hints, 2025, https://abseil.io/fast/hints.html
    
```

或以 BibTeX 引用：
```cpp 
    @misc{DeanGhemawatPerformance2025,
      author = {Dean, Jeffrey and Ghemawat, Sanjay},
      title = {Performance Hints},
      year = {2025},
      howpublished = {\url{https://abseil.io/fast/hints.html}},
    }
    
```

## 致謝 (Acknowledgments)

許多同事為此文件提供了有用的回饋，包括：

  * Adrian Ulrich
  * Alexander Kuzmin
  * Alexei Bendebury
  * Alexey Alexandrov
  * Amer Diwan
  * Austin Sims
  * Benoit Boissinot
  * Brooks Moses
  * Chris Kennelly
  * Chris Ruemmler
  * Danila Kutenin
  * Darryl Gove
  * David Majnemer
  * Dmitry Vyukov
  * Emanuel Taropa
  * Felix Broberg
  * Francis Birck Moreira
  * Gideon Glass
  * Henrik Stewenius
  * Jeremy Dorfman
  * John Dethridge
  * Kurt Kluever
  * Kyle Konrad
  * Lucas Pereira
  * Marc Eaddy
  * Michael Marty
  * Michael Whittaker
  * Mircea Trofin
  * Misha Brukman
  * Nicolas Hillegeer
  * Ranjit Mathew
  * Rasmus Larsen
  * Soheil Hassas Yeganeh
  * Srdjan Petrovic
  * Steinar H. Gunderson
  * Stergios Stergiou
  * Steven Timotius
  * Sylvain Vignaud
  * Thomas Etter
  * Thomas Köppe
  * Tim Chestnutt
  * Todd Lipcon
  * Vance Lankhaar
  * Victor Costan
  * Yao Zuo
  * Zhou Fang
