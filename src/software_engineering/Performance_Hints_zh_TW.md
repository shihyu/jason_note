# 效能提示
Jeff Dean, Sanjay Ghemawat

多年來,我們(Jeff 和 Sanjay)在各種程式碼片段的效能調校方面進行了大量深入研究,從 Google 最早期開始,改善軟體效能就一直很重要,因為這讓我們能為更多使用者做更多事。我們撰寫本文件是為了識別一些我們在進行此類工作時使用的通用原則和具體技術,並試圖挑選說明性的原始碼變更(變更列表,或 CL)來提供各種方法和技術的範例。以下大部分具體建議參考 C++ 類型和 CL,但通用原則適用於其他語言。本文件著重於單一執行檔範圍內的通用效能調校,不涵蓋分散式系統或機器學習(ML)硬體效能調校(這些本身就是龐大的領域)。我們希望其他人會覺得這有用。

_本文件中的許多範例都包含展示這些技術的程式碼片段(點擊小三角形！)。_ _請注意,其中一些程式碼片段提到了各種 Google 內部程式碼庫抽象概念。如果我們覺得這些範例足夠獨立,能讓不熟悉這些抽象概念細節的人理解,我們仍會包含這些範例。_

## 思考效能的重要性

Knuth 經常被斷章取義地引用為說_過早最佳化是萬惡之源_。[完整的引文](https://dl.acm.org/doi/pdf/10.1145/356635.356640)是這樣的：_「我們應該忘記小的效率提升,大約 97% 的時間都是如此:過早最佳化是萬惡之源。然而我們不應該放棄那關鍵的 3% 的機會。」_ 本文件就是關於那關鍵的 3%,而更有說服力的引文,同樣來自 Knuth,是這樣說的:

> 從範例 2 到範例 2a 的速度提升只有約 12%,許多人會認為這微不足道。許多現今軟體工程師分享的傳統智慧呼籲忽略小規模的效率提升；但我相信這只是對他們看到的被那些因小失大的程式設計師濫用的過度反應,這些人無法除錯或維護他們「最佳化」的程式。在已建立的工程學科中,輕易獲得的 12% 改善從不被認為是微不足道的；我相信同樣的觀點應該在軟體工程中盛行。當然,我不會為一次性的工作煩惱進行這樣的最佳化,但當涉及到準備高品質程式時,我不想限制自己使用那些拒絕我獲得這種效率的工具。

許多人會說「讓我們以盡可能簡單的方式寫下程式碼,稍後當我們可以進行效能分析時再處理效能問題」。然而,這種方法通常是錯誤的:

1.  如果你在開發大型系統時忽視所有效能問題,你最終會得到一個平坦的效能分析結果,其中沒有明顯的熱點,因為效能到處都在流失。將很難弄清楚如何開始進行效能改善。
2.  如果你正在開發一個將被其他人使用的函式庫,遇到效能問題的人很可能是那些無法輕易進行效能改善的人(他們必須理解其他人/團隊編寫的程式碼細節,並必須與他們協商效能最佳化的重要性)。
3.  當系統正在大量使用時,對系統進行重大變更更加困難。
4.  也很難判斷是否存在可以輕易解決的效能問題,因此我們最終可能會採用潛在昂貴的解決方案,如過度複製或嚴重過度配置服務以處理負載問題。

相反地,我們建議在編寫程式碼時,如果不會顯著影響程式碼的可讀性/複雜性,請嘗試選擇更快的替代方案。

## 估算

如果你能對你正在編寫的程式碼中效能可能有多重要形成直覺,你就可以做出更明智的決定(例如,為了效能值得增加多少額外的複雜性)。在編寫程式碼時估算效能的一些技巧:

-   這是測試程式碼嗎？如果是,你主要需要擔心演算法和資料結構的漸近複雜度。(順帶一提:開發週期時間很重要,所以避免編寫需要很長時間運行的測試。)
-   這是特定於應用程式的程式碼嗎？如果是,嘗試弄清楚效能對這段程式碼有多重要。這通常不是很困難:只要弄清楚程式碼是初始化/設定程式碼還是最終會在熱路徑上的程式碼(例如,處理服務中的每個請求)通常就足夠了
-   這是將被許多應用程式使用的函式庫程式碼嗎？在這種情況下,很難判斷它可能變得多敏感。這就是遵循本文件中描述的一些簡單技術變得特別重要的地方。例如,如果你需要儲存一個通常具有少量元素的向量,使用 absl::InlinedVector 而不是 std::vector。這些技術不是很難遵循,也不會給系統增加任何非局部的複雜性。如果結果證明你正在編寫的程式碼確實最終使用了大量資源,它從一開始就會有更高的效能。而且在查看效能分析結果時,找到下一個需要關注的事物會更容易。

在選擇可能具有不同效能特性的選項時,你可以通過依賴[粗略估算](https://en.wikipedia.org/wiki/Back-of-the-envelope_calculation)來進行稍微深入的分析。這樣的計算可以快速給出不同替代方案效能的非常粗略的估計,結果可以用來在不必實作的情況下淘汰一些替代方案。

以下是這樣的估算可能如何工作:

1.  估計需要多少種各類低層級操作,例如,磁碟尋道次數、網路往返次數、傳輸的位元組數等。
2.  將每種昂貴操作乘以其粗略成本,並將結果加總。
3.  前面的步驟給出了系統在資源使用方面的_成本_。如果你對延遲感興趣,而且如果系統有任何並發性,一些成本可能會重疊,你可能需要進行稍微更複雜的分析來估算延遲。

下表是來自 [2007 年史丹佛大學演講](https://static.googleusercontent.com/media/research.google.com/en//people/jeff/stanford-295-talk.pdf)的表格的更新版本(2007 年演講的影片已不存在,但有一個[2011 年史丹佛演講的影片,涵蓋了一些相同的內容](https://www.youtube.com/watch?v=modXC5IWTJI)),可能很有用,因為它列出了要考慮的操作類型及其粗略成本:

```
L1 cache reference                             0.5 ns
L2 cache reference                             3 ns
Branch mispredict                              5 ns
Mutex lock/unlock (uncontended)               15 ns
Main memory reference                         50 ns
Compress 1K bytes with Snappy              1,000 ns
Read 4KB from SSD                         20,000 ns
Round trip within same datacenter         50,000 ns
Read 1MB sequentially from memory         64,000 ns
Read 1MB over 100 Gbps network           100,000 ns
Read 1MB from SSD                      1,000,000 ns
Disk seek                              5,000,000 ns
Read 1MB sequentially from disk       10,000,000 ns
Send packet CA->Netherlands->CA      150,000,000 ns
```

前面的表格包含了一些基本低層級操作的粗略成本。你可能會發現追蹤與你的系統相關的更高層級操作的估算成本也很有用。例如,你可能想知道從 SQL 資料庫進行點讀取的粗略成本、與雲端服務互動的延遲,或渲染簡單 HTML 頁面的時間。如果你不知道不同操作的相關成本,你就無法進行像樣的粗略估算！

### 範例：快速排序十億個 4 位元組數字所需時間

作為粗略近似,一個好的快速排序演算法對大小為 N 的陣列進行 log(N) 次遍歷。在每次遍歷中,陣列內容將從記憶體串流到處理器快取中,分區程式碼將每個元素與樞軸元素比較一次。讓我們加總主要成本:

1.  記憶體頻寬:陣列佔用 4 GB(每個數字 4 位元組乘以十億個數字)。讓我們假設每個核心約 16GB/s 的記憶體頻寬。這意味著每次遍歷將花費約 0.25 秒。N 約為 2^30,所以我們將進行約 30 次遍歷,因此記憶體傳輸的總成本將約為 7.5 秒。
2.  分支預測失敗:我們將進行總共 N\*log(N) 次比較,即約 300 億次比較。讓我們假設其中一半(即 150 億次)預測失敗。乘以每次預測失敗 5 ns,我們得到預測失敗成本為 75 秒。我們假設在這個分析中,正確預測的分支是免費的。
3.  將前面的數字加總,我們得到約 82.5 秒的估計。

如有必要,我們可以優化我們的分析以考慮處理器快取。這種優化可能不需要,因為根據上面的分析,分支預測失敗是主要成本,但我們無論如何在這裡包含它作為另一個範例。讓我們假設我們有一個 32MB 的 L3 快取,並且從 L3 快取傳輸資料到處理器的成本可以忽略不計。L3 快取可以容納 2^23 個數字,因此最後 22 次遍歷可以對駐留在 L3 快取中的資料進行操作(倒數第 23 次遍歷將資料帶入 L3 快取,其餘遍歷對該資料進行操作。)這將記憶體傳輸成本降低到 2.5 秒(10 次 4GB 記憶體傳輸,16GB/s),而不是 7.5 秒(30 次記憶體傳輸)。

### 範例：生成包含 30 個縮圖的網頁所需時間

讓我們比較兩種潛在設計,其中原始圖片儲存在磁碟上,每張圖片約為 1MB 大小。

1.  串列讀取 30 張圖片的內容並為每張生成縮圖。每次讀取需要一次尋道 + 一次傳輸,尋道加起來是 5ms,傳輸是 10ms,加起來是 30 張圖片乘以每張圖片 15ms,即 450ms。
2.  並行讀取,假設圖片均勻分布在 K 個磁碟上。之前的資源使用估計仍然成立,但延遲將大約降低 K 倍,忽略變異(例如,我們有時會不走運,一個磁碟會有超過 1/K 的我們正在讀取的圖片)。因此,如果我們在具有數百個磁碟的分散式檔案系統上運行,預期延遲將降至約 15ms。
3.  讓我們考慮一個變體,其中所有圖片都在單個 SSD 上。這將順序讀取效能改變為每張圖片 20µs + 1ms,總計約 30 ms。

## 測量

前面的部分給出了一些關於在編寫程式碼時如何思考效能的技巧,而不必過多擔心如何測量你的選擇的效能影響。然而,在你實際開始進行改善之前,或遇到涉及各種事物(如效能、簡單性等)的權衡時,你會想要測量或估算潛在的效能優勢。能夠有效地測量事物是你在進行效能相關工作時想要擁有的第一工具。

順帶一提,值得指出的是,對你不熟悉的程式碼進行效能分析也可以是了解程式碼庫結構及其運作方式的好方法。檢查程式的動態呼叫圖中高度參與的例程的原始碼可以讓你對運行程式碼時「發生了什麼」有一個高層次的感覺,這可以建立你在稍微不熟悉的程式碼中進行效能改善變更的信心。

### 效能分析工具和技巧

有許多有用的效能分析工具可用。首先使用的有用工具是 [pprof](https://github.com/google/pprof/blob/main/doc/README.md),因為它提供了良好的高層級效能資訊,並且易於在本地和生產環境中運行的程式碼中使用。如果你想要更詳細的效能洞察,也可以嘗試 [perf](https://perf.wiki.kernel.org/index.php/Main_Page)。

效能分析的一些技巧:

-   使用適當的除錯資訊和最佳化旗標建置生產二進位檔案。
-   如果可以,編寫一個涵蓋你正在改善的程式碼的[微基準測試](https://abseil.io/fast/75)。微基準測試可以改善進行效能改善時的周轉時間,幫助驗證效能改善的影響,並可以幫助防止未來的效能回歸。然而,微基準測試可能有[陷阱](https://abseil.io/fast/39),使它們無法代表完整系統效能。用於編寫微基準測試的有用函式庫:[C++](https://github.com/google/benchmark/blob/main/README.md) [Go](https://pkg.go.dev/testing#hdr-Benchmarks) [Java](https://github.com/openjdk/jmh)。
-   使用基準測試函式庫[發出效能計數器讀數](https://abseil.io/fast/53),以獲得更好的精度,並更深入地了解程式行為。

-   鎖競爭通常會人為地降低 CPU 使用率。某些互斥鎖實作提供對鎖競爭效能分析的支援。
-   使用 [ML 效能分析器](https://www.tensorflow.org/tensorboard/tensorboard_profiling_keras#debug_performance_bottlenecks)進行機器學習效能工作。

### 當效能分析結果平坦時該怎麼辦

你經常會遇到 CPU 效能分析結果平坦的情況(沒有明顯的緩慢大貢獻者)。這通常會發生在所有低垂的果實都被採摘後。如果你發現自己處於這種情況,以下是一些要考慮的技巧:

-   不要低估許多小最佳化的價值！在某個子系統中進行二十個獨立的 1% 改善通常是完全可能的,並且總體上意味著相當大的改善(這種風格的工作通常依賴於擁有穩定和高品質的微基準測試)。這些類型的變更的一些範例在[展示多種技術的變更](https://abseil.io/fast/hints.html#cls-that-demonstrate-multiple-techniques)部分中。
-   在呼叫堆疊頂部附近找到迴圈(CPU 效能分析的火焰圖視圖在這裡可能有幫助)。潛在地,迴圈或它呼叫的程式碼可以重構得更有效率。一些最初通過循環輸入的節點和邊來增量建構複雜圖結構的程式碼被改為通過傳遞整個輸入一次性建構圖結構。這消除了在初始程式碼中每條邊都在發生的一堆內部檢查。
-   退一步,在呼叫堆疊的更高層級尋找結構性變更,而不是專注於微最佳化。[演算法改善](https://abseil.io/fast/hints.html#algorithmic-improvements)下列出的技術在這樣做時可能很有用。
-   尋找過於通用的程式碼。用客製化或低層級實作替換它。例如,如果應用程式重複使用正規表示式匹配,而簡單的前綴匹配就足夠了,考慮放棄使用正規表示式。
-   嘗試減少配置次數:[獲取配置效能分析](https://gperftools.github.io/gperftools/heapprofile.html),並挑選配置次數的最高貢獻者。這將有兩個效果:(1)它將直接減少在配置器中花費的時間(對於 GC 語言,在垃圾收集器中花費的時間)(2)快取未命中通常會減少,因為在使用 tcmalloc 的長時間運行的程式中,每次配置往往會到不同的快取行。
-   收集其他類型的效能分析,特別是基於硬體效能計數器的效能分析。這樣的效能分析可能會指出遇到高快取未命中率的函數。[效能分析工具和技巧](https://abseil.io/fast/hints.html#profiling-tools-and-tips)部分描述的技術可能有幫助。

## API 考量

以下建議的一些技術需要變更資料結構和函數簽章,這可能會干擾呼叫者。嘗試組織程式碼,以便可以在封裝邊界內進行建議的效能改善,而不影響公共介面。如果你的[模組是深層的](https://web.stanford.edu/~ouster/cgi-bin/book.php)(通過窄介面存取重要功能),這將更容易。

廣泛使用的 API 面臨著增加功能的巨大壓力。在增加新功能時要小心,因為這些將限制未來的實作,並為不需要新功能的使用者不必要地增加成本。例如,許多 C++ 標準函式庫容器承諾迭代器穩定性,在典型實作中這會顯著增加配置次數,即使許多使用者不需要指標穩定性。

下面列出了一些具體技術。仔細考慮效能優勢與這些變更引入的任何 API 可用性問題。

### 批次 API

提供批次操作以減少昂貴的 API 邊界穿越或利用演算法改善。

添加批次 MemoryManager::LookupMany 介面。

除了添加批次介面外,這還簡化了新批次變體的簽章:結果證明客戶端只需要知道是否找到了所有鍵,所以我們可以返回 bool 而不是 Status 物件。

memory\_manager.h

```c++
class MemoryManager {
 public:
  ...
  util::StatusOr<LiveTensor> Lookup(const TensorIdProto& id);
```

```c++
class MemoryManager {
 public:
  ...
  util::StatusOr<LiveTensor> Lookup(const TensorIdProto& id);

  // Lookup the identified tensors
  struct LookupKey {
    ClientHandle client;
    uint64 local_id;
  };
  bool LookupMany(absl::Span<const LookupKey> keys,
                  absl::Span<tensorflow::Tensor> tensors);
```

添加批次 ObjectStore::DeleteRefs API 以攤銷鎖定開銷。

object\_store.h

```c++
template <typename T>
class ObjectStore {
 public:
  ...
  absl::Status DeleteRef(Ref);
```

```c++
template <typename T>
class ObjectStore {
 public:
  ...
  absl::Status DeleteRef(Ref);

  // Delete many references.  For each ref, if no other Refs point to the same
  // object, the object will be deleted.  Returns non-OK on any error.
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

memory\_tracking.cc

```c++
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

```c++
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

使用 [Floyd 的堆建構](https://en.wikipedia.org/wiki/Heapsort#Variations)進行高效初始化。

堆的批次初始化可以在 O(N) 時間內完成,而一次添加一個元素並在每次添加後更新堆屬性需要 O(N lg(N)) 時間。

有時很難直接改變呼叫者使用新的批次 API。在這種情況下,在內部使用批次 API 並快取結果以供未來的非批次 API 呼叫使用可能是有益的:

快取區塊解碼結果以供未來呼叫使用。

每次查找都需要解碼整個 K 個條目的區塊。將解碼的條目儲存在快取中,並在未來的查找中查詢快取。

lexicon.cc

```c++
void GetTokenString(int pos, std::string* out) const {
  ...
  absl::FixedArray<LexiconEntry, 32> entries(pos + 1);

  // Decode all lexicon entries up to and including pos.
  for (int i = 0; i <= pos; ++i) {
    p = util::coding::TwoValuesVarint::Decode32(p, &entries[i].remaining,
                                                &entries[i].shared);
    entries[i].remaining_str = p;
    p += entries[i].remaining;  // remaining bytes trail each entry.
  }
```

```c++
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
  // Init cache.
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

### 視圖類型

對於函數參數,優先使用視圖類型(例如,`std::string_view`、`std::Span<T>`、`absl::FunctionRef<R(Args...)>`)(除非正在傳輸資料的所有權)。這些類型減少了複製,並允許呼叫者選擇他們自己的容器類型(例如,一個呼叫者可能使用 `std::vector`,而另一個使用 `absl::InlinedVector`)。

### 預配置/預計算的參數

對於經常呼叫的例程,有時允許更高層級的呼叫者傳入他們擁有的資料結構或客戶端已經擁有的被呼叫例程需要的資訊是有用的。這可以避免低層級例程被迫配置自己的臨時資料結構或重新計算已經可用的資訊。

添加 RPC\_Stats::RecordRPC 變體,允許客戶端傳入已經可用的 WallTime 值。

rpc-stats.h

```c++
static void RecordRPC(const Name &name, const RPC_Stats_Measurement& m);
```

```c++
static void RecordRPC(const Name &name, const RPC_Stats_Measurement& m,
                      WallTime now);
```

clientchannel.cc

```c++
const WallTime now = WallTime_Now();
...
RPC_Stats::RecordRPC(stats_name, m);
```

```c++
const WallTime now = WallTime_Now();
...
RPC_Stats::RecordRPC(stats_name, m, now);
```

### 執行緒相容與執行緒安全類型

一個類型可以是執行緒相容的(外部同步)或執行緒安全的(內部同步)。大多數通常使用的類型應該是執行緒相容的。這樣不需要執行緒安全的呼叫者就不用為它付費。

使類別執行緒相容,因為呼叫者已經同步了。

hitless-transfer-phase.cc

```c++
TransferPhase HitlessTransferPhase::get() const {
  static CallsiteMetrics cm("HitlessTransferPhase::get");
  MonitoredMutexLock l(&cm, &mutex_);
  return phase_;
}
```

```c++
TransferPhase HitlessTransferPhase::get() const { return phase_; }
```

hitless-transfer-phase.cc

```c++
bool HitlessTransferPhase::AllowAllocate() const {
  static CallsiteMetrics cm("HitlessTransferPhase::AllowAllocate");
  MonitoredMutexLock l(&cm, &mutex_);
  return phase_ == TransferPhase::kNormal || phase_ == TransferPhase::kBrownout;
}
```

```c++
bool HitlessTransferPhase::AllowAllocate() const {
  return phase_ == TransferPhase::kNormal || phase_ == TransferPhase::kBrownout;
}
```

然而,如果類型的典型使用需要同步,最好將同步移到類型內部。這允許根據需要調整同步機制以提高效能(例如,分片以減少競爭),而不影響呼叫者。


## 演算法改善

效能改善最關鍵的機會來自演算法改善,例如,將 O(N²) 演算法轉換為 O(N lg(N)) 或 O(N),避免潛在的指數行為等。這些機會在穩定的程式碼中很少見,但在編寫新程式碼時值得注意。一些顯示對現有程式碼進行此類改善的範例:

以逆後序將節點添加到循環檢測結構中。

我們之前是一次一個地將圖節點和邊添加到循環檢測資料結構中,這需要每條邊進行昂貴的工作。我們現在以逆後序添加整個圖,這使得循環檢測變得微不足道。

graphcycles.h

```c++
class GraphCycles : public util_graph::Graph {
 public:
  GraphCycles();
  ~GraphCycles() override;

  using Node = util_graph::Node;
```

```c++
class GraphCycles : public util_graph::Graph {
 public:
  GraphCycles();
  ~GraphCycles() override;

  using Node = util_graph::Node;

  // InitFrom adds all the nodes and edges from src, returning true if
  // successful, false if a cycle is encountered.
  // REQUIRES: no nodes and edges have been added to GraphCycles yet.
  bool InitFrom(const util_graph::Graph& src);
```

graphcycles.cc

```c++
bool GraphCycles::InitFrom(const util_graph::Graph& src) {
  ...
  // Assign ranks in topological order so we don't need any reordering during
  // initialization. For an acyclic graph, DFS leaves nodes in reverse
  // topological order, so we assign decreasing ranks to nodes as we leave them.
  Rank last_rank = n;
  auto leave = [&](util_graph::Node node) {
    DCHECK(r->rank[node] == kMissingNodeRank);
    NodeInfo* nn = &r->nodes[node];
    nn->in = kNil;
    nn->out = kNil;
    r->rank[node] = --last_rank;
  };
  util_graph::DFSAll(src, std::nullopt, leave);

  // Add all the edges (detect cycles as we go).
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

graph\_partitioner.cc

```c++
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
    if (graph_->HasEdge(e.src, e.dst)) return;  // already added
    if (!graph_->InsertEdge(e.src, e.dst)) {
      s = absl::InvalidArgumentError("cycle in the original graph");
    }
  });
  return s;
}
```

```c++
absl::Status MergeGraph::Init() {
  const Graph& graph = *compiler_->graph();
  if (!graph_->InitFrom(graph)) {
    return absl::InvalidArgumentError("cycle in the original graph");
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

用更好的演算法替換互斥鎖實作中內建的死鎖檢測系統。

用快約 50 倍且可擴展到數百萬個互斥鎖而無問題的演算法替換死鎖檢測演算法(舊演算法依賴於 2K 限制以避免效能懸崖)。新程式碼基於以下論文:A dynamic topological sort algorithm for directed acyclic graphs David J. Pearce, Paul H. J. Kelly Journal of Experimental Algorithmics (JEA) JEA Homepage archive Volume 11, 2006, Article No. 1.7

新演算法佔用 O(|V|+|E|) 空間(而不是舊演算法所需的 O(|V|^2) 位元)。鎖獲取順序圖非常稀疏,所以這占用的空間要少得多。演算法也相當簡單:它的核心約 100 行 C++。由於程式碼現在可以擴展到更大數量的互斥鎖,我們能夠放寬人為的 2K 限制,這揭示了實際程式中一些潛在的死鎖。

基準測試結果:這些在 DEBUG 模式下運行,因為死鎖檢測主要在除錯模式下啟用。基準測試參數(/2k 等)是追蹤的節點數。在舊演算法的預設 2k 限制下,新演算法每次 InsertEdge 只需要 0.5 微秒,而舊演算法需要 22 微秒。新演算法也輕鬆擴展到更大的圖而沒有問題,而舊演算法很快就垮掉了。

```{.old}
DEBUG: Benchmark            Time(ns)    CPU(ns) Iterations
----------------------------------------------------------
DEBUG: BM_StressTest/2k        23553      23566      29086
DEBUG: BM_StressTest/4k        45879      45909      15287
DEBUG: BM_StressTest/16k      776938     777472        817
```

```{.new}
DEBUG: BM_StressTest/2k          392        393   10485760
DEBUG: BM_StressTest/4k          392        393   10485760
DEBUG: BM_StressTest/32k         407        407   10485760
DEBUG: BM_StressTest/256k        456        456   10485760
DEBUG: BM_StressTest/1M          534        534   10485760
```

用雜湊表(O(1) 查找)替換 IntervalMap(O(lg N) 查找)。

初始程式碼使用 IntervalMap,因為它似乎是支援相鄰區塊合併的正確資料結構,但雜湊表就足夠了,因為可以通過雜湊表查找找到相鄰區塊。這(加上 CL 中的其他變更)將 tpu::BestFitAllocator 的效能提高了約 4 倍。

best\_fit\_allocator.h

```c++
using Block = gtl::IntervalMap<int64, BlockState>::Entry;
...
// Map of pairs (address range, BlockState) with one entry for each allocation
// covering the range [0, allocatable_range_end_).  Adjacent kFree and
// kReserved blocks are coalesced. Adjacent kAllocated blocks are not
// coalesced.
gtl::IntervalMap<int64, BlockState> block_list_;

// Set of all free blocks sorted according to the allocation policy. Adjacent
// free blocks are coalesced.
std::set<Block, BlockSelector> free_list_;
```

```c++
// A faster hash function for offsets in the BlockTable
struct OffsetHash {
  ABSL_ATTRIBUTE_ALWAYS_INLINE size_t operator()(int64 value) const {
    uint64 m = value;
    m *= uint64_t{0x9ddfea08eb382d69};
    return static_cast<uint64_t>(m ^ (m >> 32));
  }
};

// Hash table maps from block start address to block info.
// We include the length of the previous block in this info so we
// can find the preceding block to coalesce with.
struct HashTableEntry {
  BlockState state;
  int64 my_length;
  int64 prev_length;  // Zero if there is no previous block.
};
using BlockTable = absl::flat_hash_map<int64, HashTableEntry, OffsetHash>;
```

用雜湊表查找(O(N))替換排序列表交集(O(N log N))。

檢測兩個節點是否共享公共來源的舊程式碼會按排序順序獲取每個節點的來源,然後進行排序交集。新程式碼將一個節點的來源放入雜湊表中,然後迭代另一個節點的來源檢查雜湊表。

```{.bench}
name             old time/op  new time/op  delta
BM_CompileLarge   28.5s ± 2%   22.4s ± 2%  -21.61%  (p=0.008 n=5+5)
```

實作良好的雜湊函數,使事物是 O(1) 而不是 O(N)。

location.h

```c++
// Hasher for Location objects.
struct LocationHash {
  size_t operator()(const Location* key) const {
    return key != nullptr ? util_hash::Hash(key->address()) : 0;
  }
};
```

```c++
size_t HashLocation(const Location& loc);
...
struct LocationHash {
  size_t operator()(const Location* key) const {
    return key != nullptr ? HashLocation(*key) : 0;
  }
};
```

location.cc

```c++
size_t HashLocation(const Location& loc) {
  util_hash::MurmurCat m;

  // Encode some simpler features into a single value.
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

  // We do not include any_of since it is complicated to compute a hash
  // value that is not sensitive to order and duplication.
  return m.GetHash();
}
```

## 更好的記憶體表示

仔細考慮重要資料結構的記憶體佔用和快取佔用通常可以產生巨大的節省。下面的資料結構專注於通過觸及更少的快取行來支援常見操作。這裡所做的努力可以(a)避免昂貴的快取未命中(b)減少記憶體匯流排流量,這加速了有問題的程式以及在同一機器上運行的任何其他東西。它們依賴於一些你在設計自己的資料結構時可能會覺得有用的常見技術。

### 緊湊的資料結構

對經常存取的資料或佔應用程式記憶體使用量很大一部分的資料使用緊湊的表示。緊湊的表示可以顯著減少記憶體使用量並通過觸及更少的快取行和減少記憶體匯流排頻寬使用來提高效能。然而,要注意[快取行競爭](https://abseil.io/fast/hints.html#reduce-false-sharing)。

### 記憶體佈局

仔細考慮具有大記憶體或快取佔用的類型的記憶體佈局。

-   重新排序欄位以減少具有不同對齊要求的欄位之間的填充(參見[類佈局討論](https://stackoverflow.com/questions/9989164/optimizing-memory-layout-of-class-instances-in-c))。
-   在儲存的資料適合較小類型的情況下使用較小的數字類型。
-   除非你小心,否則列舉值有時會佔用整個字。考慮使用較小的表示(例如,使用 `enum class OpType : uint8_t { ... }` 而不是 `enum class OpType { ... }`)。
-   排序欄位,使經常一起存取的欄位彼此更接近 - 這將減少常見操作觸及的快取行數。
-   將熱唯讀欄位放置在遠離熱可變欄位的地方,以便對可變欄位的寫入不會導致唯讀欄位從附近的快取中被逐出。
-   移動冷資料,使其不與熱資料相鄰,可以通過將冷資料放在結構的末尾,或放在間接層後面,或放在單獨的陣列中。
-   考慮通過使用位元和位元組級編碼將事物打包到更少的位元組中。這可能很複雜,所以只有當有問題的資料封裝在經過良好測試的模組內,並且記憶體使用量的總體減少是顯著的時候才這樣做。此外,要注意副作用,如頻繁使用的資料對齊不足,或存取打包表示的程式碼更昂貴。使用基準測試驗證此類變更。

### 索引而不是指標

在現代 64 位元機器上,指標佔用 64 位元。如果你有一個指標豐富的資料結構,你可以輕鬆地用 T\* 的間接引用耗盡大量記憶體。相反,考慮使用整數索引到陣列 T\[\] 或其他資料結構。不僅引用會更小(如果索引數量足夠小以適合 32 位元或更少),而且所有 T\[\] 元素的儲存將是連續的,通常導致更好的快取局部性。

### 批次儲存

避免為每個儲存的元素配置單獨物件的資料結構(例如,C++ 中的 `std::map`、`std::unordered_map`)。相反,考慮使用分塊或平面表示來將多個元素儲存在記憶體中的相近位置的類型(例如,C++ 中的 `std::vector`、`absl::flat_hash_{map,set}`)。這樣的類型往往具有更好的快取行為。此外,它們遇到更少的配置器開銷。

一個有用的技術是將元素分成塊,其中每個塊可以容納固定數量的元素。這種技術可以在保持良好的漸近行為的同時顯著減少資料結構的快取佔用。

對於某些資料結構,單個塊足以容納所有元素(例如,字串和向量)。其他類型(例如,`absl::flat_hash_map`)也使用這種技術。

### 內聯儲存

某些容器類型針對儲存少量元素進行了最佳化。這些類型在頂層為少量元素提供空間,並在元素數量較少時完全避免配置。當此類類型的實例經常被建構時(例如,作為頻繁執行的程式碼中的堆疊變數),或者如果許多實例同時存活,這會非常有幫助。如果容器通常包含少量元素,考慮使用內聯儲存類型之一,例如 InlinedVector。

警告:如果 `sizeof(T)` 很大,內聯儲存容器可能不是最佳選擇,因為內聯後備儲存將很大。

### 不必要的嵌套映射

有時嵌套映射資料結構可以用具有複合鍵的單層映射替換。這可以顯著減少查找和插入的成本。

通過將 btree<a,btree<b,c>> 轉換為 btree<pair<a,b>,c> 來減少配置並改善快取佔用。

graph\_splitter.cc

```c++
absl::btree_map<std::string, absl::btree_map<std::string, OpDef>> ops;
```

```c++
// The btree maps from {package_name, op_name} to its const Opdef*.
absl::btree_map<std::pair<absl::string_view, absl::string_view>,
                const OpDef*>
    ops;
```

警告:如果第一個映射鍵很大,堅持使用嵌套映射可能更好:

切換到嵌套映射在微基準測試中導致 76% 的效能改善。

我們之前有一個單層雜湊表,其中鍵由一個(字串)路徑和一些其他數字子鍵組成。平均每個路徑出現在大約 1000 個鍵中。我們將雜湊表分成兩層,其中第一層由路徑鍵控,每個第二層雜湊表只為特定路徑保留子鍵到資料的映射。這將儲存路徑的記憶體使用量減少了 1000 倍,並且還加快了一起存取同一路徑的許多子鍵的存取速度。

### Arena

Arena 可以幫助減少記憶體配置成本,但它們還具有將獨立配置的項目打包在一起的好處,通常在更少的快取行中,並消除大多數銷毀成本。對於具有許多子物件的複雜資料結構,它們可能最有效。考慮為 arena 提供適當的初始大小,因為這可以幫助減少配置。

警告:很容易誤用 arena,將太多短期物件放入長期 arena 中,這可能不必要地膨脹記憶體佔用。

### 陣列而不是映射

如果映射的定義域可以由小整數表示或是枚舉,或者如果映射將有很少的元素,映射有時可以由某種形式的陣列或向量替換。

使用陣列而不是 flat\_map。

rtp\_controller.h

```c++
const gtl::flat_map<int, int> payload_type_to_clock_frequency_;
```

```c++
// A map (implemented as a simple array) indexed by payload_type to clock freq
// for that paylaod type (or 0)
struct PayloadTypeToClockRateMap {
  int map[128];
};
...
const PayloadTypeToClockRateMap payload_type_to_clock_frequency_;
```

### 位元向量而不是集合

如果集合的定義域可以由小整數表示,集合可以用位元向量替換(InlinedBitVector 通常是一個好選擇)。集合操作在這些表示上也可以使用位元布林操作非常高效(OR 用於聯集,AND 用於交集等)。

Spanner 放置系統。用每個區域一個位元的位元向量替換 dense\_hash\_set<ZoneId>。

zone\_set.h

```c++
class ZoneSet: public dense_hash_set<ZoneId> {
 public:
  ...
  bool Contains(ZoneId zone) const {
    return count(zone) > 0;
  }
```

```c++
class ZoneSet {
  ...
  // Returns true iff "zone" is contained in the set
  bool ContainsZone(ZoneId zone) const {
    return zone < b_.size() && b_.get_bit(zone);
  }
  ...
 private:
  int size_;          // Number of zones inserted
  util::bitmap::InlinedBitVector<256> b_;
```

基準測試結果:

```{.bench}
CPU: AMD Opteron (4 cores) dL1:64KB dL2:1024KB
Benchmark                          Base (ns)  New (ns) Improvement
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

使用位元矩陣來追蹤運算元之間的可達性屬性,而不是雜湊表。

hlo\_computation.h

```c++
using TransitiveOperandMap =
    std::unordered_map<const HloInstruction*,
                       std::unordered_set<const HloInstruction*>>;
```

```c++
class HloComputation::ReachabilityMap {
  ...
  // dense id assignment from HloInstruction* to number
  tensorflow::gtl::FlatMap<const HloInstruction*, int> ids_;
  // matrix_(a,b) is true iff b is reachable from a
  tensorflow::core::Bitmap matrix_;
};
```

## 減少配置

記憶體配置增加成本:

1.  它增加了在配置器中花費的時間。
2.  新配置的物件可能需要昂貴的初始化,有時在不再需要時需要相應昂貴的銷毀。
3.  每次配置往往在新的快取行上,因此分散在許多獨立配置中的資料將比分散在較少配置中的資料具有更大的快取佔用。

垃圾收集執行時期有時通過將連續的配置順序放置在記憶體中來消除問題 #3。

### 避免不必要的配置

減少配置使基準測試吞吐量提高 21%。

memory\_manager.cc

```c++
LiveTensor::LiveTensor(tf::Tensor t, std::shared_ptr<const DeviceInfo> dinfo,
                       bool is_batched)
    : tensor(std::move(t)),
      device_info(dinfo ? std::move(dinfo) : std::make_shared<DeviceInfo>()),
      is_batched(is_batched) {
```

```c++
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

盡可能使用靜態配置的零向量,而不是配置一個向量並用零填充它。

embedding\_executor\_8bit.cc

```c++
// The actual implementation of the EmbeddingLookUpT using template parameters
// instead of object members to improve the performance.
template <bool Mean, bool SymmetricInputRange>
static tensorflow::Status EmbeddingLookUpT(...) {
    ...
  std::unique_ptr<tensorflow::quint8[]> zero_data(
      new tensorflow::quint8[max_embedding_width]);
  memset(zero_data.get(), 0, sizeof(tensorflow::quint8) * max_embedding_width);
```

```c++
// A size large enough to handle most embedding widths
static const int kTypicalMaxEmbedding = 256;
static tensorflow::quint8 static_zero_data[kTypicalMaxEmbedding];  // All zeroes
...
// The actual implementation of the EmbeddingLookUpT using template parameters
// instead of object members to improve the performance.
template <bool Mean, bool SymmetricInputRange>
static tensorflow::Status EmbeddingLookUpT(...) {
    ...
  std::unique_ptr<tensorflow::quint8[]> zero_data_backing(nullptr);

  // Get a pointer to a memory area with at least
  // "max_embedding_width" quint8 zero values.
  tensorflow::quint8* zero_data;
  if (max_embedding_width <= ARRAYSIZE(static_zero_data)) {
    // static_zero_data is big enough so we don't need to allocate zero data
    zero_data = &static_zero_data[0];
  } else {
    // static_zero_data is not big enough: we need to allocate zero data
    zero_data_backing =
        absl::make_unique<tensorflow::quint8[]>(max_embedding_width);
    memset(zero_data_backing.get(), 0,
           sizeof(tensorflow::quint8) * max_embedding_width);
    zero_data = zero_data_backing.get();
  }
```

此外,當物件生命週期受範圍限制時,優先使用堆疊配置而不是堆配置(但對於大物件要小心堆疊框架大小)。

### 調整大小或保留容器

當向量(或某些其他容器類型)的最大或預期最大大小事先已知時,預先調整容器的後備儲存大小(例如,在 C++ 中使用 `resize` 或 `reserve`)。

預先調整向量大小並填充它,而不是 N 次 push\_back 操作。

indexblockdecoder.cc

```c++
for (int i = 0; i < ndocs-1; i++) {
  uint32 delta;
  ERRORCHECK(b->GetRice(rice_base, &delta));
  docs_.push_back(DocId(my_shard_ + (base + delta) * num_shards_));
  base = base + delta + 1;
}
docs_.push_back(last_docid_);
```

```c++
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

警告:不要使用 `resize` 或 `reserve` 一次增長一個元素,因為這可能導致二次行為。另外,如果元素建構很昂貴,優先使用初始 `reserve` 呼叫後跟幾個 `push_back` 或 `emplace_back` 呼叫,而不是初始 `resize`,因為這會使建構子呼叫次數加倍。

### 盡可能避免複製

-   盡可能優先移動而不是複製資料結構。
-   如果生命週期不是問題,在臨時資料結構中儲存指標或索引而不是物件的副本。例如,如果使用本地映射從傳入的 proto 列表中選擇一組 proto,我們可以讓映射只儲存指向傳入 proto 的指標,而不是複製可能深度嵌套的資料。另一個常見的範例是排序索引向量而不是直接排序大物件向量,因為後者會產生大量的複製/移動成本。

通過 gRPC 接收張量時避免額外的複製。

傳送約 400KB 張量的基準測試加速約 10-15%:

```{.old}
Benchmark              Time(ns)    CPU(ns) Iterations
-----------------------------------------------------
BM_RPC/30/98k_mean    148764691 1369998944       1000
```

```{.new}
Benchmark              Time(ns)    CPU(ns) Iterations
-----------------------------------------------------
BM_RPC/30/98k_mean    131595940 1216998084       1000
```

移動大選項結構而不是複製它。

index.cc

```c++
return search_iterators::DocPLIteratorFactory::Create(opts);
```

```c++
return search_iterators::DocPLIteratorFactory::Create(std::move(opts));
```

使用 std::sort 而不是 std::stable\_sort,這避免了穩定排序實作內部的內部複製。

encoded-vector-hits.h

```c++
std::stable_sort(hits_.begin(), hits_.end(),
                 gtl::OrderByField(&HitWithPayloadOffset::docid));
```

```c++
struct HitWithPayloadOffset {
  search_iterators::LocalDocId64 docid;
  int first_payload_offset;  // offset into the payload vector.
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

### 重用臨時物件

在迴圈內部宣告的容器或物件將在每次迴圈迭代中重新建立。這可能導致昂貴的建構、銷毀和調整大小。將宣告提升到迴圈外部可以實現重用並可以提供顯著的效能提升。(編譯器通常由於語言語義或無法確保程式等價性而無法自己進行這樣的提升。)

將變數定義提升到迴圈迭代之外。

autofdo\_profile\_utils.h

```c++
auto iterator = absl::WrapUnique(sstable->GetIterator());
while (!iterator->done()) {
  T profile;
  if (!profile.ParseFromString(iterator->value_view())) {
    return absl::InternalError(
        "Failed to parse mem_block to specified profile type.");
  }
  ...
  iterator->Next();
}
```

```c++
auto iterator = absl::WrapUnique(sstable->GetIterator());
T profile;
while (!iterator->done()) {
  if (!profile.ParseFromString(iterator->value_view())) {
    return absl::InternalError(
        "Failed to parse mem_block to specified profile type.");
  }
  ...
  iterator->Next();
}
```

在迴圈外部定義 protobuf 變數,以便其配置的儲存可以在迴圈迭代中重用。

stats-router.cc

```c++
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

```c++
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


重複序列化到同一個 std::string。

program\_rep.cc

```c++
std::string DeterministicSerialization(const proto2::Message& m) {
  std::string result;
  proto2::io::StringOutputStream sink(&result);
  proto2::io::CodedOutputStream out(&sink);
  out.SetSerializationDeterministic(true);
  m.SerializePartialToCodedStream(&out);
  return result;
}
```

```c++
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

警告:protobuf、string、vector、容器等往往會增長到曾經儲存在它們中的最大值的大小。因此定期重建它們(例如,每 N 次使用後)可以幫助減少記憶體需求和重新初始化成本。

## 避免不必要的工作

也許改善效能最有效的類別之一是避免你不必做的工作。這可以採取多種形式,包括為常見情況建立通過程式碼的專門路徑以避免更通用的昂貴計算、預計算、將工作推遲到真正需要時、將工作提升到較少頻繁執行的程式碼片段中,以及其他類似的方法。下面是這種通用方法的許多範例,分類為幾個代表性類別。

### 常見情況的快速路徑

通常,程式碼被編寫來涵蓋所有情況,但某些情況子集比其他情況簡單得多且更常見。例如,`vector::push_back` 通常有足夠的空間容納新元素,但包含在沒有空間時調整底層儲存大小的程式碼。對程式碼結構的一些關注可以幫助使常見的簡單情況更快,而不會顯著損害不常見情況的效能。

使快速路徑涵蓋更多常見情況。

添加對尾隨單個 ASCII 位元組的處理,而不是只用此例程處理四的倍數位元組。這避免了為全 ASCII 字串(例如 5 位元組)呼叫較慢的通用例程。

utf8statetable.cc

```c++
// Scan a UTF-8 stringpiece based on state table.
// Always scan complete UTF-8 characters
// Set number of bytes scanned. Return reason for exiting
// OPTIMIZED for case of 7-bit ASCII 0000..007f all valid
int UTF8GenericScanFastAscii(const UTF8ScanObj* st, absl::string_view str,
                             int* bytes_consumed) {
                             ...
  int exit_reason;
  do {
    //  Skip 8 bytes of ASCII at a whack; no endianness issue
    while ((src_limit - src >= 8) &&
           (((UNALIGNED_LOAD32(src + 0) | UNALIGNED_LOAD32(src + 4)) &
             0x80808080) == 0)) {
      src += 8;
    }
    //  Run state table on the rest
    int rest_consumed;
    exit_reason = UTF8GenericScan(
        st, absl::ClippedSubstr(str, src - initial_src), &rest_consumed);
    src += rest_consumed;
  } while (exit_reason == kExitDoAgain);

  *bytes_consumed = src - initial_src;
  return exit_reason;
}
```

```c++
// Scan a UTF-8 stringpiece based on state table.
// Always scan complete UTF-8 characters
// Set number of bytes scanned. Return reason for exiting
// OPTIMIZED for case of 7-bit ASCII 0000..007f all valid
int UTF8GenericScanFastAscii(const UTF8ScanObj* st, absl::string_view str,
                             int* bytes_consumed) {
                             ...
  int exit_reason = kExitOK;
  do {
    //  Skip 8 bytes of ASCII at a whack; no endianness issue
    while ((src_limit - src >= 8) &&
           (((UNALIGNED_LOAD32(src + 0) | UNALIGNED_LOAD32(src + 4)) &
             0x80808080) == 0)) {
      src += 8;
    }
    while (src < src_limit && Is7BitAscii(*src)) { // Skip ASCII bytes
      src++;
    }
    if (src < src_limit) {
      //  Run state table on the rest
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

InlinedVector 的更簡單快速路徑。

inlined\_vector.h

```c++
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

```c++
auto Storage<T, N, A>::Resize(ValueAdapter values, size_type new_size) -> void {
  StorageView storage_view = MakeStorageView();
  auto* const base = storage_view.data;
  const size_type size = storage_view.size;
  auto* alloc = GetAllocPtr();
  if (new_size <= size) {
    // Destroy extra old elements.
    inlined_vector_internal::DestroyElements(alloc, base + new_size,
                                             size - new_size);
  } else if (new_size <= storage_view.capacity) {
    // Construct new elements in place.
    inlined_vector_internal::ConstructElements(alloc, base + size, &values,
                                               new_size - size);
  } else {
  ...
  }
```

初始化 1-D 到 4-D 張量的常見情況的快速路徑。

tensor\_shape.cc

```c++
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

```c++
template <class Shape>
void TensorShapeBase<Shape>::InitDims(gtl::ArraySlice<int64> dim_sizes) {
  DCHECK_EQ(tag(), REP16);

  // Allow sizes that are under kint64max^0.25 so that 4-way multiplication
  // below cannot overflow.
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
    // Every size fits in 16 bits; use fast-paths for dims in {1,2,3,4}.
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

使 varint 解析器快速路徑只涵蓋 1 位元組情況,而不是涵蓋 1 位元組和 2 位元組情況。

減少(內聯)快速路徑的大小可減少程式碼大小和 icache 壓力,從而提高效能。

parse\_context.h

```c++
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

```c++
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

parse\_context.cc

```c++
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

```c++
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

如果沒有發生錯誤,則在 RPC\_Stats\_Measurement 加法中跳過大量工作。

rpc-stats.h

```c++
struct RPC_Stats_Measurement {
  ...
  double errors[RPC::NUM_ERRORS];
```

```c++
struct RPC_Stats_Measurement {
  ...
  double get_errors(int index) const { return errors[index]; }
  void set_errors(int index, double value) {
    errors[index] = value;
    any_errors_set = true;
  }
 private:
  ...
  // We make this private so that we can keep track of whether any of
  // these values have been set to non-zero values.
  double errors[RPC::NUM_ERRORS];
  bool any_errors_set;  // True iff any of the errors[i] values are non-zero
```

rpc-stats.cc

```c++
void RPC_Stats_Measurement::operator+=(const RPC_Stats_Measurement& x) {
  ...
  for (int i = 0; i < RPC::NUM_ERRORS; ++i) {
    errors[i] += x.errors[i];
  }
}
```

```c++
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

對字串的第一個位元組進行陣列查找,以通常避免對完整字串進行指紋識別。

soft-tokens-helper.cc

```c++
bool SoftTokensHelper::IsSoftToken(const StringPiece& token) const {
  return soft_tokens_.find(Fingerprint(token.data(), token.size())) !=
      soft_tokens_.end();
}
```

soft-tokens-helper.h

```c++
class SoftTokensHelper {
 ...
 private:
  ...
  // Since soft tokens are mostly punctuation-related, for performance
  // purposes, we keep an array filter_.  filter_[i] is true iff any
  // of the soft tokens start with the byte value 'i'.  This avoids
  // fingerprinting a term in the common case, since we can just do an array
  // lookup based on the first byte, and if filter_[b] is false, then
  // we can return false immediately.
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

```c++
bool SoftTokensHelper::IsSoftTokenFallback(const StringPiece& token) const {
  return soft_tokens_.find(Fingerprint(token.data(), token.size())) !=
      soft_tokens_.end();
}
```

### 預先計算昂貴的資訊一次

預先計算 TensorFlow 圖執行節點屬性,使我們能夠快速排除某些不尋常的情況。

executor.cc

```c++
struct NodeItem {
  ...
  bool kernel_is_expensive = false;  // True iff kernel->IsExpensive()
  bool kernel_is_async = false;      // True iff kernel->AsAsync() != nullptr
  bool is_merge = false;             // True iff IsMerge(node)
  ...
  if (IsEnter(node)) {
  ...
  } else if (IsExit(node)) {
  ...
  } else if (IsNextIteration(node)) {
  ...
  } else {
    // Normal path for most nodes
    ...
  }
```

```c++
struct NodeItem {
  ...
  bool kernel_is_expensive : 1;  // True iff kernel->IsExpensive()
  bool kernel_is_async : 1;      // True iff kernel->AsAsync() != nullptr
  bool is_merge : 1;             // True iff IsMerge(node)
  bool is_enter : 1;             // True iff IsEnter(node)
  bool is_exit : 1;              // True iff IsExit(node)
  bool is_control_trigger : 1;   // True iff IsControlTrigger(node)
  bool is_sink : 1;              // True iff IsSink(node)
  // True iff IsEnter(node) || IsExit(node) || IsNextIteration(node)
  bool is_enter_exit_or_next_iter : 1;
  ...
  if (!item->is_enter_exit_or_next_iter) {
    // Fast path for nodes types that don't need special handling
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

預先計算 256 元素陣列並在 trigram 初始化期間使用。

byte\_trigram\_classifier.cc

```c++
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

```c++
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

一般建議:在模組邊界檢查畸形輸入,而不是在內部重複檢查。

### 將昂貴的計算移出迴圈

將邊界計算移出迴圈。

literal\_linearizer.cc

```c++
for (int64 i = 0; i < src_shape.dimensions(dimension_numbers.front());
     ++i) {
```

```c++
int64 dim_front = src_shape.dimensions(dimension_numbers.front());
const uint8* src_buffer_data = src_buffer.data();
uint8* dst_buffer_data = dst_buffer.data();
for (int64 i = 0; i < dim_front; ++i) {
```

### 推遲昂貴的計算

推遲 GetSubSharding 呼叫直到需要時,這將 43 秒的 CPU 時間減少到 2 秒。

sharding\_propagation.cc

```c++
HloSharding alternative_sub_sharding =
    user.sharding().GetSubSharding(user.shape(), {i});
if (user.operand(i) == &instruction &&
    hlo_sharding_util::IsShardingMoreSpecific(alternative_sub_sharding,
                                              sub_sharding)) {
  sub_sharding = alternative_sub_sharding;
}
```

```c++
if (user.operand(i) == &instruction) {
  // Only evaluate GetSubSharding if this operand is of interest,
  // as it is relatively expensive.
  HloSharding alternative_sub_sharding =
      user.sharding().GetSubSharding(user.shape(), {i});
  if (hlo_sharding_util::IsShardingMoreSpecific(
          alternative_sub_sharding, sub_sharding)) {
    sub_sharding = alternative_sub_sharding;
  }
}
```

不要急切地更新統計資料;按需計算它們。

不要在非常頻繁的配置/釋放呼叫上更新統計資料。相反,當較少頻繁呼叫的 Stats() 方法被呼叫時,按需計算統計資料。

為 Google 網頁伺服器中的查詢處理預先配置 10 個節點而不是 200 個。

一個簡單的變更,使網頁伺服器的 CPU 使用率降低了 7.5%。

querytree.h

```c++
static const int kInitParseTreeSize = 200;   // initial size of querynode pool
```

```c++
static const int kInitParseTreeSize = 10;   // initial size of querynode pool
```

變更搜尋順序以獲得 19% 的吞吐量改善。

一個舊的搜尋系統(約 2000 年)有兩層:一層包含全文索引,另一層只包含標題和錨點詞彙的索引。我們曾經先搜尋較小的標題/錨點層。與直覺相反,我們發現先搜尋較大的全文索引層更便宜,因為如果我們到達全文層的末尾,我們可以完全跳過搜尋標題/錨點層(全文層的子集)。這種情況相當頻繁地發生,使我們能夠減少處理查詢的平均磁碟尋道次數。

參見[大規模超文字網路搜尋引擎的解剖](https://research.google/pubs/the-anatomy-of-a-large-scale-hypertextual-web-search-engine/)中關於標題和錨點文字處理的討論以獲取背景資訊。

### 專門化程式碼

特定的效能敏感呼叫位置可能不需要通用函式庫提供的完整通用性。在這種情況下,如果它提供效能改善,考慮編寫專門的程式碼而不是呼叫通用程式碼。

Histogram 類的自訂列印程式碼比 sprintf 快 4 倍。

此程式碼對效能敏感,因為當監控系統從各種伺服器收集統計資料時會被呼叫。

histogram\_export.cc

```c++
void Histogram::PopulateBuckets(const string &prefix,
                                expvar::MapProto *const var) const {
                                ...
  for (int i = min_bucket; i <= max_bucket; ++i) {
    const double count = BucketCount(i);
    if (!export_empty_buckets && count == 0.0) continue;
    acc += count;
    // The label format of exported buckets for discrete histograms
    // specifies an inclusive upper bound, which is the same as in
    // the original Histogram implementation.  This format is not
    // applicable to non-discrete histograms, so a half-open interval
    // is used for them, with "_" instead of "-" as a separator to
    // make possible to distinguish the formats.
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


```c++
// Format "val" according to format.  If "need_escape" is true, then the
// format can produce output with a '.' in it, and the result will be escaped.
// If "need_escape" is false, then the caller guarantees that format is
// such that the resulting number will not have any '.' characters and
// therefore we can avoid calling EscapeKey.
// The function is free to use "*scratch" for scratch space if necessary,
// and the resulting StringPiece may point into "*scratch".
static StringPiece FormatNumber(const char* format,
                                bool need_escape,
                                double val, string* scratch) {
  // This routine is specialized to work with only a limited number of formats
  DCHECK(StringPiece(format) == "%.0f" || StringPiece(format) == "%.12g");

  scratch->clear();
  if (val == trunc(val) && val >= kint32min && val <= kint32max) {
    // An integer for which we can just use StrAppend
    StrAppend(scratch, static_cast<int32>(val));
    return StringPiece(*scratch);
  } else if (isinf(val)) {
    // Infinity, represent as just 'inf'.
    return StringPiece("inf", 3);
  } else {
    // Format according to "format", and possibly escape.
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
  string key = full_key_prefix;  // Keys will start with "full_key_prefix".
  string start_scratch;
  string limit_scratch;
  const bool cumul_counts = options_.export_cumulative_counts();
  const bool discrete = options_.discrete();
  for (int i = min_bucket; i <= max_bucket; ++i) {
    const double count = BucketCount(i);
    if (!export_empty_buckets && count == 0.0) continue;
    acc += count;
    // The label format of exported buckets for discrete histograms
    // specifies an inclusive upper bound, which is the same as in
    // the original Histogram implementation.  This format is not
    // applicable to non-discrete histograms, so a half-open interval
    // is used for them, with "_" instead of "-" as a separator to
    // make possible to distinguish the formats.
    key.resize(full_key_prefix.size());  // Start with full_key_prefix.
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

    // Add to map var
    expvar::AddMapFloat(key, value * count_mult, var);
  }
}
```

為 VLOG(1)、VLOG(2) 等添加專門化以提高速度和更小的程式碼大小。

`VLOG` 是整個程式碼庫中大量使用的巨集。此變更避免在幾乎每個呼叫點傳遞額外的整數常數(如果日誌級別在呼叫點是常數,幾乎總是如此,如 `VLOG(1) << ...`),這節省了程式碼空間。

vlog\_is\_on.h

```c++
class VLogSite final {
 public:
  ...
  bool IsEnabled(int level) {
    int stale_v = v_.load(std::memory_order_relaxed);
    if (ABSL_PREDICT_TRUE(level > stale_v)) {
      return false;
    }

    // We put everything other than the fast path, i.e. vlogging is initialized
    // but not on, behind an out-of-line function to reduce code size.
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

```c++
class VLogSite final {
 public:
  ...
  bool IsEnabled(int level) {
    int stale_v = v_.load(std::memory_order_relaxed);
    if (ABSL_PREDICT_TRUE(level > stale_v)) {
      return false;
    }

    // We put everything other than the fast path, i.e. vlogging is initialized
    // but not on, behind an out-of-line function to reduce code size.
    // "level" is almost always a call-site constant, so we can save a bit
    // of code space by special-casing for levels 1, 2, and 3.
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

vlog\_is\_on.cc

```c++
bool VLogSite::SlowIsEnabled0(int stale_v) { return SlowIsEnabled(stale_v, 0); }
bool VLogSite::SlowIsEnabled1(int stale_v) { return SlowIsEnabled(stale_v, 1); }
bool VLogSite::SlowIsEnabled2(int stale_v) { return SlowIsEnabled(stale_v, 2); }
bool VLogSite::SlowIsEnabled3(int stale_v) { return SlowIsEnabled(stale_v, 3); }
bool VLogSite::SlowIsEnabled4(int stale_v) { return SlowIsEnabled(stale_v, 4); }
bool VLogSite::SlowIsEnabled5(int stale_v) { return SlowIsEnabled(stale_v, 5); }
```

在可能時用簡單的前綴匹配替換 RE2 呼叫。

read\_matcher.cc

```c++
enum MatchItemType {
  MATCH_TYPE_INVALID,
  MATCH_TYPE_RANGE,
  MATCH_TYPE_EXACT,
  MATCH_TYPE_REGEXP,
};
```

```c++
enum MatchItemType {
  MATCH_TYPE_INVALID,
  MATCH_TYPE_RANGE,
  MATCH_TYPE_EXACT,
  MATCH_TYPE_REGEXP,
  MATCH_TYPE_PREFIX,   // Special type for regexp ".*"
};
```

read\_matcher.cc

```c++
p->type = MATCH_TYPE_REGEXP;
```

```c++
term.NonMetaPrefix().CopyToString(&p->prefix);
if (term.RegexpSuffix() == ".*") {
  // Special case for a regexp that matches anything, so we can
  // bypass RE2::FullMatch
  p->type = MATCH_TYPE_PREFIX;
} else {
  p->type = MATCH_TYPE_REGEXP;
```

使用 StrCat 而不是 StringPrintf 來格式化 IP 地址。

ipaddress.cc

```c++
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
      LOG(DFATAL) << "Calling ToString() on an empty IPAddress";
      return "";
    default:
      LOG(FATAL) << "Unknown address family " << address_family_;
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

```c++
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
      LOG(DFATAL) << "Calling ToString() on an empty IPAddress";
      return "";
    default:
      LOG(FATAL) << "Unknown address family " << address_family_;
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

### 使用快取來避免重複工作

基於大型序列化 proto 的預計算指紋進行快取。

dp\_ops.cc

```c++
InputOutputMappingProto mapping_proto;
PLAQUE_OP_REQUIRES(
    mapping_proto.ParseFromStringPiece(GetAttrMappingProto(state)),
    absl::InternalError("Failed to parse InputOutputMappingProto"));
ParseMapping(mapping_proto);
```

```c++
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
        absl::InternalError("Failed to parse InputOutputMappingProto"));
    auto io_meta = ParseMapping(mapping_proto);
    io_metadata_ = io_meta.get();
    (*fp_to_iometa)[mapping_proto_fp] = std::move(io_meta);
  }
}
```

### 讓編譯器的工作更容易

編譯器可能難以通過抽象層進行最佳化,因為它必須對程式碼的整體行為做出保守的假設,或者可能無法做出正確的速度與大小權衡。應用程式程式設計師通常會對系統的行為有更多了解,並可以通過在較低層級重寫程式碼來幫助編譯器。然而,只有在效能分析顯示問題時才這樣做,因為編譯器通常會自己正確處理事情。查看效能關鍵例程的生成組合程式碼可以幫助你了解編譯器是否「做對了」。Pprof 提供了一個非常有幫助的[原始碼與反組譯交錯顯示](https://github.com/google/pprof/blob/main/doc/README.md#annotated-source-code),並用效能資料註釋。

一些可能有用的技術:

1.  避免在熱函數中進行函數呼叫(允許編譯器避免框架設定成本)。
2.  將慢速路徑程式碼移入單獨的尾呼叫函數。
3.  在大量使用之前將少量資料複製到局部變數中。這可以讓編譯器假設與其他資料沒有別名,這可能改善自動向量化和暫存器配置。
4.  手動展開非常熱的迴圈。

通過用指向底層陣列的原始指標替換 absl::Span 來加速 ShapeUtil::ForEachState。

shape\_util.h

```c++
struct ForEachState {
  ForEachState(const Shape& s, absl::Span<const int64_t> b,
               absl::Span<const int64_t> c, absl::Span<const int64_t> i);
  ~ForEachState();

  const Shape& shape;
  const absl::Span<const int64_t> base;
  const absl::Span<const int64_t> count;
  const absl::Span<const int64_t> incr;
```

```c++
struct ForEachState {
  ForEachState(const Shape& s, absl::Span<const int64_t> b,
               absl::Span<const int64_t> c, absl::Span<const int64_t> i);
  inline ~ForEachState() = default;

  const Shape& shape;
  // Pointers to arrays of the passed-in spans
  const int64_t* const base;
  const int64_t* const count;
  const int64_t* const incr;
```

手動展開[循環冗餘檢查](https://en.wikipedia.org/wiki/Cyclic_redundancy_check)(CRC)計算迴圈。

crc.cc

```c++
void CRC32::Extend(uint64 *lo, uint64 *hi, const void *bytes, size_t length)
                      const {
                      ...
  // Process bytes 4 at a time
  while ((p + 4) <= e) {
    uint32 c = l ^ WORD(p);
    p += 4;
    l = this->table3_[c & 0xff] ^
        this->table2_[(c >> 8) & 0xff] ^
        this->table1_[(c >> 16) & 0xff] ^
        this->table0_[c >> 24];
  }

  // Process the last few bytes
  while (p != e) {
    int c = (l & 0xff) ^ *p++;
    l = this->table0_[c] ^ (l >> 8);
  }
  *lo = l;
}
```

```c++
void CRC32::Extend(uint64 *lo, uint64 *hi, const void *bytes, size_t length)
                      const {
                      ...
#define STEP {                                  \
    uint32 c = l ^ WORD(p);                     \
    p += 4;                                     \
    l = this->table3_[c & 0xff] ^               \
        this->table2_[(c >> 8) & 0xff] ^        \
        this->table1_[(c >> 16) & 0xff] ^       \
        this->table0_[c >> 24];                 \
}

  // Process bytes 16 at a time
  while ((e-p) >= 16) {
    STEP;
    STEP;
    STEP;
    STEP;
  }

  // Process bytes 4 at a time
  while ((p + 4) <= e) {
    STEP;
  }
#undef STEP

  // Process the last few bytes
  while (p != e) {
    int c = (l & 0xff) ^ *p++;
    l = this->table0_[c] ^ (l >> 8);
  }
  *lo = l;
}
```

在解析 Spanner 鍵時一次處理四個字元。

1.  手動展開迴圈以一次處理四個字元,而不是使用 memchr
    
2.  手動展開迴圈以查找名稱的分隔部分
    
3.  向後查找帶有 '#' 分隔符的名稱的分隔部分(而不是向前),因為第一部分可能是名稱中最長的。
    

key.cc

```c++
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

```c++
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

  // We go backwards from the end of the string, rather than forwards,
  // since the directory name might be long and definitely doesn't contain
  // any '#' characters.
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

通過將 ABSL\_LOG(FATAL) 轉換為 ABSL\_DCHECK(false) 來避免框架設定成本。

arena\_cleanup.h

```c++
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
      ABSL_LOG(FATAL) << "Corrupted cleanup tag: " << static_cast<int>(tag);
      return sizeof(DynamicNode);
  }
}
```

```c++
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
      ABSL_DCHECK(false) << "Corrupted cleanup tag: " << static_cast<int>(tag);
      return sizeof(DynamicNode);
  }
}
```

### 減少統計資料收集成本

平衡統計資料和系統其他行為資訊的效用與維護該資訊的成本。額外的資訊通常可以幫助人們理解和改善高層級行為,但維護起來也可能很昂貴。

無用的統計資料可以完全刪除。

停止維護 SelectServer 中關於警報和閉包數量的昂貴統計資料。

作為將設定警報的時間從 771 ns 減少到 271 ns 的變更的一部分。

selectserver.h

```c++
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

```c++
// Selectserver class
class SelectServer {
 ...
 protected:
 ...
};
```

/selectserver.cc

```c++
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

```c++
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

```c++
void SelectServer::RemoveAlarm(Alarmer* alarmer, int id) {
      ...
      alarms_->erase(alarm);
      num_alarms_stat_->IncBy(-1);
      ...
}
```

```c++
void SelectServer::RemoveAlarm(Alarmer* alarmer, int id) {
      ...
      alarms_->Remove(alarm);
      ...
}
```

通常,可以為系統處理的元素樣本(例如,RPC 請求、輸入記錄、使用者)維護統計資料或其他屬性。許多子系統使用這種方法(tcmalloc 配置追蹤、/requestz 狀態頁面、Dapper 樣本)。

在採樣時,考慮在適當時降低採樣率。

只為 doc info 請求的樣本維護統計資料。

採樣使我們能夠避免為大多數請求觸及 39 個直方圖和 MinuteTenMinuteHour 統計資料。

generic-leaf-stats.cc

```c++
... code that touches 39 histograms to update various stats on every request ...
```

```c++
// Add to the histograms periodically
if (TryLockToUpdateHistogramsDocInfo(docinfo_stats, bucket)) {
  // Returns true and grabs bucket->lock only if we should sample this
  // request for maintaining stats
  ... code that touches 39 histograms to update various stats ...
  bucket->lock.Unlock();
}
```

降低採樣率並加快採樣決策。

此變更將採樣率從 1/10 降低到 1/32。此外,我們現在只為採樣事件保留執行時間統計資料,並通過使用二的冪次模數來加快採樣決策。此程式碼在 Google Meet 視訊會議系統中的每個數據包上被呼叫,在 COVID 爆發的第一階段,當使用者快速遷移到進行更多線上會議時,需要進行效能工作以跟上容量需求。

packet\_executor.cc

```c++
class ScopedPerformanceMeasurement {
 public:
  explicit ScopedPerformanceMeasurement(PacketExecutor* packet_executor)
      : packet_executor_(packet_executor),
        tracer_(packet_executor->packet_executor_trace_threshold_,
                kClosureTraceName) {
    // ThreadCPUUsage is an expensive call. At the time of writing,
    // it takes over 400ns, or roughly 30 times slower than absl::Now,
    // so we sample only 10% of closures to keep the cost down.
    if (packet_executor->closures_executed_ % 10 == 0) {
      thread_cpu_usage_start_ = base::ThreadCPUUsage();
    }

    // Sample start time after potentially making the above expensive call,
    // so as not to pollute wall time measurements.
    run_start_time_ = absl::Now();
  }

  ~ScopedPerformanceMeasurement() {
```

```c++
ScopedPerformanceMeasurement::ScopedPerformanceMeasurement(
    PacketExecutor* packet_executor)
    : packet_executor_(packet_executor),
      tracer_(packet_executor->packet_executor_trace_threshold_,
              kClosureTraceName) {
  // ThreadCPUUsage is an expensive call. At the time of writing,
  // it takes over 400ns, or roughly 30 times slower than absl::Now,
  // so we sample only 1 in 32 closures to keep the cost down.
  if (packet_executor->closures_executed_ % 32 == 0) {
    thread_cpu_usage_start_ = base::ThreadCPUUsage();
  }

  // Sample start time after potentially making the above expensive call,
  // so as not to pollute wall time measurements.
  run_start_time_ = absl::Now();
}
```

packet\_executor.cc

```c++
~ScopedPerformanceMeasurement() {
  auto run_end_time = absl::Now();
  auto run_duration = run_end_time - run_start_time_;

  if (thread_cpu_usage_start_.has_value()) {
  ...
  }

  closure_execution_time->Record(absl::ToInt64Microseconds(run_duration));
```

```c++
ScopedPerformanceMeasurement::~ScopedPerformanceMeasurement() {
  auto run_end_time = absl::Now();
  auto run_duration = run_end_time - run_start_time_;

  if (thread_cpu_usage_start_.has_value()) {
    ...
    closure_execution_time->Record(absl::ToInt64Microseconds(run_duration));
  }
```


基準測試結果:

```{.bench}
Run on (40 X 2793 MHz CPUs); 2020-03-24T20:08:19.991412535-07:00
CPU: Intel Ivybridge with HyperThreading (20 cores) dL1:32KB dL2:256KB dL3:25MB
Benchmark                                      Base (ns)    New (ns) Improvement
----------------------------------------------------------------------------
BM_PacketOverhead_mean                               224          85    +62.0%
```

### 避免在熱程式碼路徑上記錄日誌

日誌語句可能很昂貴,即使日誌級別實際上不記錄任何內容。例如,`ABSL_VLOG` 的實作至少需要一次載入和一次比較,這在熱程式碼路徑中可能是個問題。此外,日誌程式碼的存在可能會阻礙編譯器最佳化。考慮從熱程式碼路徑完全刪除日誌記錄。

從記憶體配置器的內部刪除日誌記錄。

這是較大變更的一小部分。

gpu\_bfc\_allocator.cc

```c++
void GPUBFCAllocator::SplitChunk(...) {
  ...
  VLOG(6) << "Adding to chunk map: " << new_chunk->ptr;
  ...
}
...
void GPUBFCAllocator::DeallocateRawInternal(void* ptr) {
  ...
  VLOG(6) << "Chunk at " << c->ptr << " no longer in use";
  ...
}
```

```c++
void GPUBFCAllocator::SplitChunk(...) {
...
}
...
void GPUBFCAllocator::DeallocateRawInternal(void* ptr) {
...
}
```

在嵌套迴圈外部預先計算是否啟用日誌記錄。

image\_similarity.cc

```c++
for (int j = 0; j < output_subimage_size_y; j++) {
  int j1 = j - rad + output_to_integral_subimage_y;
  int j2 = j1 + 2 * rad + 1;
  // Create a pointer for this row's output, taking into account the offset
  // to the full image.
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

```c++
const bool vlog_3 = DEBUG_MODE ? VLOG_IS_ON(3) : false;

for (int j = 0; j < output_subimage_size_y; j++) {
  int j1 = j - rad + output_to_integral_subimage_y;
  int j2 = j1 + 2 * rad + 1;
  // Create a pointer for this row's output, taking into account the offset
  // to the full image.
  double *image_diff_ptr = &(*image_diff)(j + min_j, min_i);

  for (int i = 0; i < output_subimage_size_x; i++) {
    ...
    if (vlog_3) {
    ...
    }
  }
}
```

```{.bench}
Run on (40 X 2801 MHz CPUs); 2016-05-16T15:55:32.250633072-07:00
CPU: Intel Ivybridge with HyperThreading (20 cores) dL1:32KB dL2:256KB dL3:25MB
Benchmark                          Base (ns)  New (ns) Improvement
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

預先計算是否啟用日誌記錄並在輔助例程中使用結果。

periodic\_call.cc

```c++
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
    VLOG(1) << Logid() << "No calls left, entering idle mode";
    next_real_time_ = absl::InfiniteFuture();
    return;
  }
  uint64 next_virtual_time_ms = FindNextVirtualTime(current_virtual_time_ms);
  auto delay =
      absl::Milliseconds(next_virtual_time_ms - current_virtual_time_ms);
  ScheduleAlarm(GetClock().TimeNow(), delay, next_virtual_time_ms);
}

// An alarm scheduled by this function supersedes all previously scheduled
// alarms. This is ensured through `scheduling_sequence_number_`.
void ScheduleAlarm(absl::Time now, absl::Duration delay,
                   uint64 virtual_time_ms)
    ABSL_EXCLUSIVE_LOCKS_REQUIRED(mutex_) {
  next_real_time_ = now + delay;
  next_virtual_time_ms_ = virtual_time_ms;
  ++ref_count_;  // The Alarm holds a reference.
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

```c++
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
      VLOG(1) << Logid() << "No calls left, entering idle mode";
    }
    next_real_time_ = absl::InfiniteFuture();
    return;
  }
  uint64 next_virtual_time_ms = FindNextVirtualTime(current_virtual_time_ms);
  auto delay =
      absl::Milliseconds(next_virtual_time_ms - current_virtual_time_ms);
  ScheduleAlarm(GetClock().TimeNow(), delay, next_virtual_time_ms, vlog_1);
}

// An alarm scheduled by this function supersedes all previously scheduled
// alarms. This is ensured through `scheduling_sequence_number_`.
void ScheduleAlarm(absl::Time now, absl::Duration delay,
                   uint64 virtual_time_ms,
                   bool vlog_1)
    ABSL_EXCLUSIVE_LOCKS_REQUIRED(mutex_) {
  next_real_time_ = now + delay;
  next_virtual_time_ms_ = virtual_time_ms;
  ++ref_count_;  // The Alarm holds a reference.
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

## 程式碼大小考量

效能不僅僅包括執行時速度。有時值得考慮軟體選擇對生成程式碼大小的影響。大的程式碼大小意味著更長的編譯和連結時間、膨脹的二進位檔案、更多的記憶體使用、更多的 icache 壓力,以及對其他微架構結構(如分支預測器)的有時負面影響等。在編寫將在許多地方使用的低層級函式庫程式碼時,或編寫你預期將針對許多不同類型進行實例化的樣板程式碼時,思考這些問題尤其重要。

減少程式碼大小的有用技術在不同程式語言之間有很大差異。以下是我們發現對 C++ 程式碼有用的一些技術(C++ 可能會受到過度使用樣板和內聯的影響)。

### 修剪常見的內聯程式碼

廣泛呼叫的函數結合內聯可能對程式碼大小產生巨大影響。

加速 TF\_CHECK\_OK。

避免建立 Ok 物件,並通過在行外進行致命錯誤訊息的複雜格式化而不是在每個呼叫點進行來節省程式碼空間。

status.h

```c++
#define TF_CHECK_OK(val) CHECK_EQ(::tensorflow::Status::OK(), (val))
#define TF_QCHECK_OK(val) QCHECK_EQ(::tensorflow::Status::OK(), (val))
```

```c++
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

```c++
string* TfCheckOpHelperOutOfLine(const ::tensorflow::Status& v,
                                 const char* msg) {
  string r("Non-OK-status: ");
  r += msg;
  r += " status: ";
  r += v.ToString();
  // Leaks string but this is only to be used in a fatal error message
  return new string(r);
}
```

將每個 RETURN\_IF\_ERROR 呼叫點縮小 79 位元組的程式碼。

1.  添加僅供 RETURN\_IF\_ERROR 使用的特殊適配器類別。
2.  不要在 RETURN\_IF\_ERROR 的快速路徑上建構/銷毀 StatusBuilder。
3.  不要內聯某些 StatusBuilder 方法,因為它們現在不再需要在快速路徑上。
4.  避免不必要的 ~Status 呼叫。

將 CHECK\_GE 的效能提高 4.5 倍並將程式碼大小從 125 位元組縮小到 77 位元組。

logging.h

```c++
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

```c++
struct CheckOpString {
  CheckOpString(string* str) : str_(str) { }
  // No destructor: if str_ is non-NULL, we're about to LOG(FATAL),
  // so there's no point in cleaning up str_.
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

```c++
string* MakeCheckOpStringIntInt(int v1, int v2, const char* names) {
  strstream ss;
  ss << names << " (" << v1 << " vs. " << v2 << ")";
  return new string(ss.str(), ss.pcount());
}
```

### 謹慎內聯

內聯通常可以提高效能,但有時它可以增加程式碼大小而沒有相應的效能回報(在某些情況下,由於指令快取壓力增加,甚至會降低效能)。

減少 TensorFlow 中的內聯。

此變更停止內聯許多對效能不敏感的函數(例如,錯誤路徑和操作註冊程式碼)。此外,一些效能敏感函數的慢速路徑被移到非內聯函數中。

這些變更將典型二進位檔案中的 tensorflow 符號大小減少了 12.2%(從 8814545 位元組減少到 7740233 位元組)

Protocol buffer 函式庫變更。避免為訊息 ≥ 128 位元組編碼訊息長度的昂貴內聯程式碼空間,而是對共享的行外例程進行程序呼叫。

不僅使重要的大型二進位檔案更小,而且更快。

一個大型二進位檔案中大量內聯例程的每行生成的程式碼位元組數。第一個數字表示為特定原始碼行生成的總位元組數,包括該程式碼已內聯的所有位置。

之前:

```c++
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

此變更後的新程式碼大小輸出如下:

```c++
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

coded\_stream.h

```c++
class PROTOBUF_EXPORT CodedOutputStream {
  ...
  // Like WriteVarint32()  but writing directly to the target array, and with the
  // less common-case paths being out of line rather than inlined.
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

coded\_stream.cc

```c++
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
    // Turn on continuation bit in the byte we just wrote.
    target[-1] |= static_cast<uint8>(0x80);
    value >>= 7;
    *target = static_cast<uint8>(value);
    ++target;
  } while (value >= 0x80);
  return target;
}
```

減少 absl::flat\_hash\_set 和 absl::flat\_hash\_map 的程式碼大小。

1.  將不依賴於特定雜湊表類型的程式碼提取到公共(非內聯)函數中。
2.  適當地放置 ABSL\_ATTRIBUTE\_NOINLINE 指令。
3.  將一些慢速路徑移到行外。

將某些大型二進位檔案的大小減少約 0.5%。

在不使用 protobuf arena 時不要內聯字串配置和釋放。

public/arenastring.h

```c++
  if (IsDefault(default_value)) {
    std::string* new_string = new std::string();
    tagged_ptr_.Set(new_string);
    return new_string;
  } else {
    return UnsafeMutablePointer();
  }
}
```

```c++
  if (IsDefault(default_value)) {
    return SetAndReturnNewString();
  } else {
    return UnsafeMutablePointer();
  }
}
```

internal/arenastring.cc

```c++
std::string* ArenaStringPtr::SetAndReturnNewString() {
  std::string* new_string = new std::string();
  tagged_ptr_.Set(new_string);
  return new_string;
}
```

避免內聯某些例程。建立採用 'const char\*' 而不是 'const std::string&' 的例程變體,以避免在每個呼叫點進行 std::string 建構程式碼。

op.h

```c++
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

```c++
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

### 減少樣板實例化

樣板程式碼在實例化時可以針對樣板參數的每個可能組合進行複製。

用常規參數替換樣板參數。

將針對 bool 進行樣板化的大型例程更改為將 bool 作為額外參數。(bool 只在一次選擇兩個字串常數之一時使用,因此執行時檢查就可以了。)這將大型例程的實例化數量從 287 減少到 143。

sharding\_util\_ops.cc

```c++
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

```c++
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

將笨重的程式碼從樣板建構子移到非樣板化的共享基類建構子。

還將樣板實例化的數量從每個 `<T, Device, Rank>` 組合一個減少到每個 `<T>` 一個和每個 `<Rank>` 一個。

sharding\_util\_ops.cc

```c++
template <typename Device, typename T>
class XlaSplitNDBaseOp : public OpKernel {
 public:
  explicit XlaSplitNDBaseOp(OpKernelConstruction* ctx) : OpKernel(ctx) {
    OP_REQUIRES_OK(
        ctx, GetAndValidateAttributes(/*split=*/true, ctx, num_splits_,
                                      num_slices_, paddings_, has_paddings_));
  }
```

```c++
// Shared base class to save code space
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

減少 absl::flat\_hash\_set 和 absl::flat\_hash\_map 的生成程式碼大小。

-   將不依賴於特定雜湊表類型的程式碼提取到公共(非內聯)函數中。
-   適當地放置 ABSL\_ATTRIBUTE\_NOINLINE 指令。
-   將一些慢速路徑移到行外。

### 減少容器操作

考慮映射和其他容器操作的影響,因為對此類操作的每次呼叫都可能產生大量生成的程式碼。

將連續的許多映射插入呼叫轉換為單個批次插入操作以初始化表情符號字元的雜湊表(在許多二進位檔案中連結的函式庫中,從 188KB 的文字減少到 360 位元組)。😊

textfallback\_init.h

```c++
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

```c++
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

停止內聯 InlinedVector 操作的重度使用者。

將正在內聯的非常長的例程從 .h 檔案移到 .cc(從內聯這個沒有真正的效能優勢)。

reduction\_ops\_common.h

```c++
Status Simplify(const Tensor& data, const Tensor& axis,
                const bool keep_dims) {
  ... Eighty line routine body ...
}
```

```c++
Status Simplify(const Tensor& data, const Tensor& axis, const bool keep_dims);
```

## 並行化和同步
### 利用並行性

現代機器有許多核心,它們通常未被充分利用。因此,昂貴的工作可以通過並行化更快地完成。最常見的方法是並行處理不同的項目,並在完成時合併結果。通常,項目首先被分成批次,以避免為每個項目支付並行運行某些內容的成本。

四路並行化將編碼令牌的速率提高約 3.6 倍。

blocked-token-coder.cc

```c++
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

並行化將解碼效能提高 5 倍。

coding.cc

```c++
for (int c = 0; c < clusters->size(); c++) {
  RET_CHECK_OK(DecodeBulkForCluster(...);
}
```

```c++
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

應仔細測量對系統效能的影響 - 如果沒有可用的備用 CPU,或者如果記憶體頻寬已飽和,並行化可能沒有幫助,甚至可能有害。

### 攤銷鎖獲取

避免細粒度鎖定以減少熱路徑中 Mutex 操作的成本。警告:這應該只在變更不增加鎖競爭的情況下進行。

獲取鎖一次以釋放整個查詢節點樹,而不是為樹中的每個節點重新獲取鎖。

mustang-query.cc

```c++
// Pool of query nodes
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

```c++
// Pool of query nodes
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

### 保持臨界區簡短

避免在臨界區內進行昂貴的工作。特別要注意看起來無害但可能正在進行 RPC 或存取檔案的程式碼。

減少臨界區中觸及的快取行數。

仔細的資料結構調整顯著減少了存取的快取行數,並將 ML 訓練運行的效能提高了 3.3%。

1.  將一些每個節點類型屬性預先計算為 NodeItem 資料結構內的位元,這意味著我們可以避免在臨界區中為出站邊觸及 Node\* 物件。
2.  將 ExecutorState::ActivateNodes 更改為使用每個出站邊的目標節點的 NodeItem,而不是觸及 \*item->node 物件中的欄位。通常這意味著我們總共觸及 1 或 2 個快取行來存取所需的邊資料,而不是 `~2 + O(出站邊數)`(對於在許多核心執行它們的大型圖,TLB 壓力也更小)。

在持有 Mutex 時避免 RPC。

trainer.cc

```c++
{
  // Notify the parameter server that we are starting.
  MutexLock l(&lock_);
  model_ = model;
  MaybeRecordProgress(last_global_step_);
}
```

```c++
bool should_start_record_progress = false;
int64 step_for_progress = -1;
{
  // Notify the parameter server that we are starting.
  MutexLock l(&lock_);
  model_ = model;
  should_start_record_progress = ShouldStartRecordProgress();
  step_for_progress = last_global_step_;
}
if (should_start_record_progress) {
  StartRecordProgress(step_for_progress);
}
```

此外,要警惕在 Mutex 解鎖之前將運行的昂貴解構子(這通常會在 Mutex 解鎖由 `~MutexUnlock` 觸發時發生。)在 MutexLock 之前宣告具有昂貴解構子的物件可能會有所幫助(假設它是執行緒安全的)。

### 通過分片減少競爭

有時,受 Mutex 保護並表現出高競爭的資料結構可以安全地分成多個分片,每個分片都有自己的 Mutex。(注意:這要求不同分片之間沒有跨分片不變性。)

將快取分成 16 個分片,這在多執行緒負載下將吞吐量提高約 2 倍。


cache.cc

```c++
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

分片 spanner 資料結構以追蹤呼叫。

transaction\_manager.cc

```c++
absl::MutexLock l(&active_calls_in_mu_);
ActiveCallMap::const_iterator iter = active_calls_in_.find(m->tid());
if (iter != active_calls_in_.end()) {
  iter->second.ExtractElements(&m->tmp_calls_);
}
```

```c++
ActiveCalls::LockedShard shard(active_calls_in_, m->tid());
const ActiveCallMap& active_calls_map = shard.active_calls_map();
ActiveCallMap::const_iterator iter = active_calls_map.find(m->tid());
if (iter != active_calls_map.end()) {
  iter->second.ExtractElements(&m->tmp_calls_);
}
```

如果有問題的資料結構是映射,考慮改用並行雜湊表實作。

小心用於分片選擇的資訊。例如,如果你使用雜湊值的某些位元進行分片選擇,然後這些相同的位元後來再次被使用,後者的使用可能會表現不佳,因為它看到的是傾斜的雜湊值分布。

修復用於分片選擇的資訊以防止雜湊表問題。

netmon\_map\_impl.h

```c++
ConnectionBucket* GetBucket(Index index) {
  // Rehash the hash to make sure we are not partitioning the buckets based on
  // the original hash. If num_buckets_ is a power of 2 that would drop the
  // entropy of the buckets.
  size_t original_hash = absl::Hash<Index>()(index);
  int hash = absl::Hash<size_t>()(original_hash) % num_buckets_;
  return &buckets_[hash];
}
```

```c++
ConnectionBucket* GetBucket(Index index) {
  absl::Hash<std::pair<Index, size_t>> hasher{};
  // Combine the hash with 42 to prevent shard selection using the same bits
  // as the underlying hashtable.
  return &buckets_[hasher({index, 42}) % num_buckets_];
}
```

分片用於追蹤呼叫的 Spanner 資料結構。

此 CL 將 ActiveCallMap 分成 64 個分片。每個分片由單獨的 mutex 保護。給定的事務將被映射到恰好一個分片。添加了一個新的介面 LockedShard(tid) 用於以執行緒安全的方式存取事務的 ActiveCallMap。範例用法:

transaction\_manager.cc

```c++
{
  absl::MutexLock l(&active_calls_in_mu_);
  delayed_locks_timer_ring_.Add(delayed_locks_flush_time_ms, tid);
}
```

```c++
{
  ActiveCalls::LockedShard shard(active_calls_in_, tid);
  shard.delayed_locks_timer_ring().Add(delayed_locks_flush_time_ms, tid);
}
```

結果顯示在使用 8192 個 fiber 運行基準測試時,整體掛鐘時間減少了 69%

```{.old}
Benchmark                   Time(ns)        CPU(ns)     Iterations
------------------------------------------------------------------
BM_ActiveCalls/8k        11854633492     98766564676            10
BM_ActiveCalls/16k       26356203552    217325836709            10
```

```{.new}
Benchmark                   Time(ns)        CPU(ns)     Iterations
------------------------------------------------------------------
BM_ActiveCalls/8k         3696794642     39670670110            10
BM_ActiveCalls/16k        7366284437     79435705713            10
```

### SIMD 指令

探索使用現代 CPU 上可用的 [SIMD](https://en.wikipedia.org/wiki/Single_instruction,_multiple_data) 指令一次處理多個項目是否可以帶來加速(例如,參見下面[批次操作](https://abseil.io/fast/hints.html#bulk-operations)部分中的 `absl::flat_hash_map` 討論)。

### 減少錯誤共享

如果不同的執行緒存取不同的可變資料,考慮將不同的資料項目放在不同的快取行上,例如,在 C++ 中使用 `alignas` 指令。然而,這些指令很容易誤用,可能會顯著增加物件大小,所以確保效能測量證明它們的使用是合理的。

將常變異的欄位隔離在與其他欄位不同的快取行中。

histogram.h

```c++
 HistogramOptions options_;
...
internal::HistogramBoundaries *boundaries_;
...
std::vector<double> buckets_;

double min_;             // Minimum.
double max_;             // Maximum.
double count_;           // Total count of occurrences.
double sum_;             // Sum of values.
double sum_of_squares_;  // Sum of squares of values.
...
RegisterVariableExporter *exporter_;
```

```c++
  HistogramOptions options_;
  ...
  internal::HistogramBoundaries *boundaries_;
  ...
  RegisterVariableExporter *exporter_;
  ...
  // Place the following fields in a dedicated cacheline as they are frequently
  // mutated, so we can avoid potential false sharing.
  ...
#ifndef SWIG
  alignas(ABSL_CACHELINE_SIZE)
#endif
  std::vector<double> buckets_;

  double min_;             // Minimum.
  double max_;             // Maximum.
  double count_;           // Total count of occurrences.
  double sum_;             // Sum of values.
  double sum_of_squares_;  // Sum of squares of values.
```

### 減少上下文切換頻率

內聯處理小型工作項而不是在設備執行緒池上處理。

cast\_op.cc

```c++
template <typename Device, typename Tout, typename Tin>
void CastMaybeInline(const Device& d, typename TTypes<Tout>::Flat o,
                     typename TTypes<Tin>::ConstFlat i) {
  if (o.size() * (sizeof(Tin) + sizeof(Tout)) < 16384) {
    // Small cast on a CPU: do inline
    o = i.template cast<Tout>();
  } else {
    o.device(d) = i.template cast<Tout>();
  }
}
```

### 使用緩衝通道進行流水線處理

通道可以是無緩衝的,這意味著寫入者會阻塞,直到讀取者準備好取得項目。當通道用於同步時,無緩衝通道可能很有用,但當通道用於增加並行性時則不然。

### 考慮無鎖方法

有時無鎖資料結構可以優於更傳統的受 mutex 保護的資料結構。然而,直接的原子變數操作可能[很危險](https://abseil.io/docs/cpp/atomic_danger)。優先使用更高層級的抽象。

使用無鎖映射來管理 RPC 通道的快取。

RPC 存根快取中的條目每秒被讀取數千次,很少被修改。切換到適當的無鎖映射可將搜尋延遲減少 3%-5%。

使用固定詞典+無鎖雜湊表來加速判斷 IsValidTokenId。

dynamic\_token\_class\_manager.h

```c++
mutable Mutex mutex_;

// The density of this hash map is guaranteed by the fact that the
// dynamic lexicon reuses previously allocated TokenIds before trying
// to allocate new ones.
dense_hash_map<TokenId, common::LocalTokenClassId> tid_to_cid_
    GUARDED_BY(mutex_);
```

```c++
// Read accesses to this hash-map should be done using
// 'epoch_gc_'::(EnterFast / LeaveFast). The writers should periodically
// GC the deleted entries, by simply invoking LockFreeHashMap::CreateGC.
typedef util::gtl::LockFreeHashMap<TokenId, common::LocalTokenClassId>
    TokenIdTokenClassIdMap;
TokenIdTokenClassIdMap tid_to_cid_;
```

## Protocol Buffer 建議

Protobuf 是資料的便利表示,特別是如果資料將通過網路傳送或持久儲存時。然而,它們可能有顯著的效能成本。例如,一段填充 1000 個點列表然後加總 Y 座標的程式碼,當從 protobuf 轉換為結構的 C++ std::vector 時,速度提高了 **20 倍**！

兩個版本的基準測試程式碼。

```{.bench}
name                old time/op  new time/op  delta
BenchmarkIteration  17.4µs ± 5%   0.8µs ± 1%  -95.30%  (p=0.000 n=11+12)
```

Protobuf 版本:

```proto
message PointProto {
  int32 x = 1;
  int32 y = 2;
}
message PointListProto {
  repeated PointProto points = 1;
}
```

```c++
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

非 protobuf 版本:

```c++
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

此外,protobuf 版本向二進位檔案添加了幾千位元組的程式碼和資料,這可能看起來不多,但在具有許多 protobuf 類型的系統中會快速累積。這種增加的大小通過建立 i-cache 和 d-cache 壓力而造成效能問題。

以下是與 protobuf 效能相關的一些技巧:

不要不必要地使用 protobufs。

鑑於上述 20 倍的效能差異,如果某些資料從未被序列化或解析,你可能不應該將其放入 protocol buffer 中。Protocol buffer 的目的是使序列化和反序列化資料結構變得容易,但它們可能有顯著的程式碼大小、記憶體和 CPU 開銷。如果你只想要其他一些好處,如 `DebugString` 和可複製性,請不要使用它們。

避免不必要的訊息層次結構。

訊息層次結構可以有用地以更可讀的方式組織資訊。然而,額外的訊息層次結構級別會產生開銷,如記憶體配置、函數呼叫、快取未命中、更大的序列化訊息等。

例如,而不是:

```proto
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

優先使用:

```proto
message Foo {
  optional int32 count = 1;
}
```

Protocol buffer 訊息對應於 C++ 生成程式碼中的訊息類別,並在線上發出標籤和有效負載的長度。要攜帶一個整數,舊形式需要更多配置(和釋放)並發出更大量的生成程式碼。因此,所有 protocol buffer 操作(解析、序列化、大小等)變得更昂貴,必須遍歷訊息樹。新形式沒有這樣的開銷,更有效率。

對頻繁出現的欄位使用小的欄位編號。

Protobuf 對欄位編號和線格式的組合使用可變長度整數表示(參見 [protobuf 編碼文件](https://protobuf.dev/programming-guides/encoding/))。對於 1 到 15 之間的欄位編號,此表示為 1 位元組,對於 16 到 2047 之間的欄位編號為兩位元組。(應該通常避免 2048 或更大的欄位編號。)

考慮為效能敏感的 protobuf 的未來擴展預留一些小欄位編號。

在 int32、sint32、fixed32 和 uint32 之間仔細選擇(對於 64 位元變體同樣如此)。

通常使用 `int32` 或 `int64`,但對於大值(如雜湊碼)使用 `fixed32` 或 `fixed64`,對於經常為負的值使用 `sint32` 或 `sint64`。

varint 佔用更少的位元組來編碼小整數,可以以更昂貴的解碼為代價節省空間。然而,對於負值或大值,它可能佔用更多空間。在這種情況下,使用 fixed32 或 fixed64(而不是 uint32 或 uint64)可以減少大小,並且編碼和解碼成本要便宜得多。對於小的負整數,使用 sint32 或 sint64 而不是 int32 或 int64。

對於 proto2,通過用 `[packed=true]` 註釋重複的數字欄位來打包它們。

在 proto2 中,重複值預設序列化為一系列(標籤,值)對。這是低效的,因為必須為每個元素解碼標籤。

打包的重複基本類型首先序列化有效負載的長度,然後是沒有標籤的值。當使用固定寬度的值時,我們可以通過在開始解析時知道最終大小來避免重新配置；即,沒有重新配置成本。我們仍然不知道有效負載中有多少 varint,可能必須支付重新配置成本。

在 proto3 中,重複欄位預設是打包的。

打包對固定寬度值(如 fixed32、fixed64、float、double 等)效果最好,因為可以通過將元素數量乘以固定值大小來預先確定整個編碼長度,而不必計算每個單獨元素的長度。

對二進位資料和大值使用 `bytes` 而不是 `string`。

`string` 類型保存 UTF8 編碼的文字,有時可能需要驗證。`bytes` 類型可以保存任意位元組序列(非文字資料),通常比 `string` 更合適且更有效率。

考慮使用 `string_type = VIEW` 來避免複製。

在解析期間複製大的 string 或 bytes 欄位是昂貴的。通過用 `string_type = VIEW` 標記欄位,通常可以避免這種成本。

```proto
message Image {
  ...
  bytes jpeg_encoding = 4 [features.(pb.cpp).string_type=VIEW];
}
```

沒有 `VIEW` 註釋時,當解析 protocol buffer 時,可能很大的欄位內容會從序列化的 protocol buffer 複製到記憶體中的字串物件。根據字串或 bytes 欄位的數量以及這些欄位的大小,複製的開銷可能很顯著。

與其複製大型二進位 blob,像 `ParseFromStringWithAliasing` 這樣的例程使用 `absl::string_view` 來引用原始後備字串。請注意,後備字串(序列化的 protocol buffer)必須比包含別名的 protocol buffer 實例活得更久。

考慮對大欄位使用 `Cord` 以減少複製成本。

用 `[ctype=CORD]` 註釋大的 `bytes` 和 `string` 欄位可能會減少複製成本。此註釋將欄位的表示從 `std::string` 更改為 `absl::Cord`。`absl::Cord` 使用引用計數和基於樹的儲存來減少複製和附加成本。如果 protocol buffer 序列化為 cord,解析帶有 `[ctype=CORD]` 的字串或 bytes 欄位可以避免複製欄位內容。

```proto
message Document {
  ...
  bytes html = 4 [ctype = CORD];
}
```

Cord 欄位的效能取決於長度分布和存取模式。使用基準測試來驗證此類變更。

在 C++ 程式碼中使用 protobuf arena。

考慮使用 arena 來節省配置和釋放成本,特別是對於包含重複、字串或訊息欄位的 protobuf。

訊息和字串欄位是堆配置的(即使頂層 protocol buffer 物件是堆疊配置的)。如果 protocol buffer 訊息有許多子訊息欄位和字串欄位,配置和釋放成本可能很顯著。Arena 攤銷配置成本並使釋放實際上免費。它還通過從連續的記憶體塊配置來改善記憶體局部性。

保持 .proto 檔案小。

不要在單個 .proto 檔案中放入太多訊息。一旦你依賴 .proto 檔案中的任何東西,連結器就會引入整個檔案,即使它大部分未使用。這會增加建置時間和二進位檔案大小。你可以使用擴展和 `Any` 來避免建立對具有許多訊息類型的大型 .proto 檔案的硬依賴。

考慮以序列化形式儲存 protocol buffer,即使在記憶體中。

記憶體中的 protobuf 物件具有大的記憶體佔用(通常是線格式大小的 5 倍),可能分散在許多快取行上。因此,如果你的應用程式將長時間保持許多 protobuf 物件存活,考慮以序列化形式儲存它們。

避免 protobuf 映射欄位。

Protobuf 映射欄位有效能問題,通常超過它們提供的小語法便利性。優先使用從 protobuf 內容初始化的非 protobuf 映射:

msg.proto

```proto
map<string, bytes> env_variables = 5;
```

```proto
message Var {
  string key = 1;
  bytes value = 2;
}
repeated Var env_variables = 5;
```

使用具有欄位子集的 protobuf 訊息定義。

如果你只想存取大型訊息類型的幾個欄位,考慮定義你自己的 protocol buffer 訊息類型,它模仿原始類型,但只定義你關心的欄位。這是一個範例:

```proto
message FullMessage {
  optional int32 field1 = 1;
  optional BigMessage field2 = 2;
  optional int32 field3 = 3;
  repeater AnotherBigMessage field4 = 4;
  ...
  optional int32 field100 = 100;
}
```

```proto
message SubsetMessage {
  optional int32 field3 = 3;
  optional int32 field88 = 88;
}
```

通過將序列化的 `FullMessage` 解析為 `SubsetMessage`,只解析一百個欄位中的兩個,其他欄位被視為未知欄位。考慮在適當時使用丟棄未知欄位的 API 來進一步提高效能。

盡可能重用 protobuf 物件。

在迴圈外部宣告 protobuf 物件,以便它們的配置儲存可以在迴圈迭代中重用。

## C++ 特定建議
### absl::flat\_hash\_map (和 set)

[Absl 雜湊表](https://abseil.io/docs/cpp/guides/container)通常優於 C++ 標準函式庫容器,如 `std::map` 和 `std::unordered_map`。

加速 LanguageFromCode(使用 absl::flat\_hash\_map 而不是 \_\_gnu\_cxx::hash\_map)。

languages.cc

```c++
class CodeToLanguage
    ...
    : public __gnu_cxx::hash_map<absl::string_view, i18n::languages::Language,
                                 CodeHash, CodeCompare> {
```

```c++
class CodeToLanguage
    ...
    : public absl::flat_hash_map<absl::string_view, i18n::languages::Language,
                                 CodeHash, CodeCompare> {
```

基準測試結果:

```{.bench}
name               old time/op  new time/op  delta
BM_CodeToLanguage  19.4ns ± 1%  10.2ns ± 3%  -47.47%  (p=0.000 n=8+10)
```

加速統計發布/取消發布(較舊的變更,因此使用 dense\_hash\_map 而不是當時不存在的 absl::flat\_hash\_map)。

publish.cc

```c++
typedef hash_map<uint64, Publication*> PublicationMap;
static PublicationMap* publications = NULL;
```

```c++
typedef dense_hash_map<uint64, Publication*> PublicationMap;;
static PublicationMap* publications GUARDED_BY(mu) = NULL;
```

使用 dense\_hash\_map 而不是 hash\_map 來追蹤 SelectServer 警報(今天會使用 absl::flat\_hash\_map)。

alarmer.h

```c++
typedef hash_map<int, Alarm*> AlarmList;
```

```c++
typedef dense_hash_map<int, Alarm*> AlarmList;
```

### absl::btree\_map/absl::btree\_set

absl::btree\_map 和 absl::btree\_set 每個樹節點儲存多個條目。這相對於有序的 C++ 標準函式庫容器(如 `std::map`)有許多優勢。首先,指向子樹節點的指標開銷通常顯著減少。其次,因為給定 btree 樹節點的條目或鍵/值在記憶體中連續儲存,快取效率通常要好得多。

使用 btree\_set 而不是 std::set 來表示一個非常大量使用的工作佇列。

register\_allocator.h

```c++
using container_type = std::set<WorklistItem>;
```

```c++
using container_type = absl::btree_set<WorklistItem>;
```

### util::bitmap::InlinedBitVector

`util::bitmap::InlinedBitvector` 可以內聯儲存短位元向量,因此通常比 `std::vector<bool>` 或其他點陣圖類型更好。

使用 InlinedBitVector 而不是 std::vector<bool>,然後使用 FindNextBitSet 來查找下一個感興趣的項目。

block\_encoder.cc

```c++
vector<bool> live_reads(nreads);
...
for (int offset = 0; offset < b_.block_width(); offset++) {
  ...
  for (int r = 0; r < nreads; r++) {
    if (live_reads[r]) {
```

```c++
util::bitmap::InlinedBitVector<4096> live_reads(nreads);
...
for (int offset = 0; offset < b_.block_width(); offset++) {
  ...
  for (size_t r = 0; live_reads.FindNextSetBit(&r); r++) {
    DCHECK(live_reads[r]);
```

### absl::InlinedVector

absl::InlinedVector 內聯儲存少量元素(可通過第二個樣板參數配置)。這使得達到此元素數量的小向量通常具有更好的快取效率,並且當元素數量較少時還可以完全避免配置後備儲存陣列。

在各個地方使用 InlinedVector 而不是 std::vector。

bundle.h

```c++
class Bundle {
 public:
 ...
 private:
  // Sequence of (slotted instruction, unslotted immediate operands).
  std::vector<InstructionRecord> instructions_;
  ...
};
```

```c++
class Bundle {
 public:
 ...
 private:
  // Sequence of (slotted instruction, unslotted immediate operands).
  absl::InlinedVector<InstructionRecord, 2> instructions_;
  ...
};
```

### gtl::vector32

通過使用只支援適合 32 位元大小的客製化向量類型來節省空間。

簡單的類型更改在 Spanner 中節省約 8TiB 記憶體。

table\_ply.h

```c++
class TablePly {
    ...
    // Returns the set of data columns stored in this file for this table.
    const std::vector<FamilyId>& modified_data_columns() const {
      return modified_data_columns_;
    }
    ...
   private:
    ...
    std::vector<FamilyId> modified_data_columns_;  // Data columns in the table.
```

```c++
#include "util/gtl/vector32.h"
    ...
    // Returns the set of data columns stored in this file for this table.
    absl::Span<const FamilyId> modified_data_columns() const {
      return modified_data_columns_;
    }
    ...

    ...
    // Data columns in the table.
    gtl::vector32<FamilyId> modified_data_columns_;
```

### gtl::small\_map

gtl::small\_map 使用內聯陣列來儲存一定數量的唯一鍵值對元素,但當空間不足時,它會自動升級為由使用者指定的映射類型支援。

在 tflite\_model 中使用 gtl::small\_map。

tflite\_model.cc

```c++
using ChoiceIdToContextMap = gtl::flat_hash_map<int, TFLiteContext*>;
```

```c++
using ChoiceIdToContextMap =
    gtl::small_map<gtl::flat_hash_map<int, TFLiteContext*>>;
```

### gtl::small\_ordered\_set

gtl::small\_ordered\_set 是關聯容器(如 std::set 或 absl::btree\_multiset)的最佳化。它使用固定陣列來儲存一定數量的元素,然後在空間不足時恢復使用 set 或 multiset。對於通常很小的集合,這可以比直接使用 set 快得多,因為 set 針對大資料集進行了最佳化。此變更縮小了快取佔用並減少了臨界區長度。

使用 gtl::small\_ordered\_set 來保存監聽器集合。

broadcast\_stream.h

```c++
class BroadcastStream : public ParsedRtpTransport {
 ...
 private:
  ...
  std::set<ParsedRtpTransport*> listeners_ ABSL_GUARDED_BY(listeners_mutex_);
};
```

```c++
class BroadcastStream : public ParsedRtpTransport {
 ...
 private:
  ...
  using ListenersSet =
      gtl::small_ordered_set<std::set<ParsedRtpTransport*>, 10>;
  ListenersSet listeners_ ABSL_GUARDED_BY(listeners_mutex_);
```

### gtl::intrusive\_list

`gtl::intrusive_list<T>` 是一個雙向連結串列,其中連結指標嵌入在類型 T 的元素中。與 `std::list<T*>` 相比,它每個元素節省一個快取行+間接引用。

使用 intrusive\_list 來追蹤每個索引行更新的進行中請求。

row-update-sender-inflight-set.h

```c++
std::set<int64> inflight_requests_ GUARDED_BY(mu_);
```

```c++
class SeqNum : public gtl::intrusive_link<SeqNum> {
  ...
  int64 val_ = -1;
  ...
};
...
gtl::intrusive_list<SeqNum> inflight_requests_ GUARDED_BY(mu_);
```

### 限制 absl::Status 和 absl::StatusOr 的使用

即使 `absl::Status` 和 `absl::StatusOr` 類型相當有效率,它們即使在成功路徑上也有非零開銷,因此應該避免用於不需要返回任何有意義的錯誤詳情的熱例程(或者甚至可能永遠不會失敗！):

避免 RoundUpToAlignment() 函數的 StatusOr<int64> 返回類型。

best\_fit\_allocator.cc

```c++
absl::StatusOr<int64> BestFitAllocator::RoundUpToAlignment(int64 bytes) const {
  TPU_RET_CHECK_GE(bytes, 0);

  const int64 max_aligned = MathUtil::RoundDownTo<int64>(
      std::numeric_limits<int64>::max(), alignment_in_bytes_);
  if (bytes > max_aligned) {
    return util::ResourceExhaustedErrorBuilder(ABSL_LOC)
           << "Attempted to allocate "
           << strings::HumanReadableNumBytes::ToString(bytes)
           << " which after aligning to "
           << strings::HumanReadableNumBytes::ToString(alignment_in_bytes_)
           << " cannot be expressed as an int64.";
  }

  return MathUtil::RoundUpTo<int64>(bytes, alignment_in_bytes_);
}
```

best\_fit\_allocator.h

```c++
// Rounds bytes up to nearest multiple of alignment_.
// REQUIRES: bytes >= 0.
// REQUIRES: result does not overflow int64.
// REQUIRES: alignment_in_bytes_ is a power of 2 (checked in constructor).
int64 RoundUpToAlignment(int64 bytes) const {
  DCHECK_GE(bytes, 0);
  DCHECK_LE(bytes, max_aligned_bytes_);
  int64 result =
      ((bytes + (alignment_in_bytes_ - 1)) & ~(alignment_in_bytes_ - 1));
  DCHECK_EQ(result, MathUtil::RoundUpTo<int64>(bytes, alignment_in_bytes_));
  return result;
}
```

添加 ShapeUtil::ForEachIndexNoStatus 以避免為張量的每個元素建立 Status 返回物件。

shape\_util.h

```c++
using ForEachVisitorFunction =
    absl::FunctionRef<StatusOr<bool>(absl::Span<const int64_t>)>;
    ...
static void ForEachIndex(const Shape& shape, absl::Span<const int64_t> base,
                         absl::Span<const int64_t> count,
                         absl::Span<const int64_t> incr,
                         const ForEachVisitorFunction& visitor_function);
```

```c++
using ForEachVisitorFunctionNoStatus =
    absl::FunctionRef<bool(absl::Span<const int64_t>)>;
    ...
static void ForEachIndexNoStatus(
    const Shape& shape, absl::Span<const int64_t> base,
    absl::Span<const int64_t> count, absl::Span<const int64_t> incr,
    const ForEachVisitorFunctionNoStatus& visitor_function);
```

literal.cc

```c++
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

```c++
ShapeUtil::ForEachIndexNoStatus(
    result_shape, [&](absl::Span<const int64_t> output_index) {
      // Compute dest_index
      int64_t dest_index = IndexUtil::MultidimensionalIndexToLinearIndex(
          result_shape, result_minor_to_major, output_index);

      // Compute source_index
      int64_t source_index;
      for (int64_t i = 0, end = dimensions.size(); i < end; ++i) {
        scratch_source_array[i] = output_index[dimensions[i]];
      }
      if (src_shape_dims == 1) {
        // Fast path for this case
        source_index = scratch_source_array[0];
        DCHECK_EQ(source_index,
                  IndexUtil::MultidimensionalIndexToLinearIndex(
                      src_shape, src_minor_to_major, scratch_source_span));
      } else {
        source_index = IndexUtil::MultidimensionalIndexToLinearIndex(
            src_shape, src_minor_to_major, scratch_source_span);
      }
      // Move one element from source_index in source to dest_index in dest
      memcpy(dest_data + PRIMITIVE_SIZE * dest_index,
             source_data + PRIMITIVE_SIZE * source_index, PRIMITIVE_SIZE);
      return true;
    });
```

在 TF\_CHECK\_OK 中,避免建立 Ok 物件以測試 ok()。

status.h

```c++
#define TF_CHECK_OK(val) CHECK_EQ(::tensorflow::Status::OK(), (val))
#define TF_QCHECK_OK(val) QCHECK_EQ(::tensorflow::Status::OK(), (val))
```

```c++
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

從遠端程序呼叫(RPC)的熱路徑中移除 StatusOr。

從熱路徑移除 StatusOr 消除了先前變更在 RPC 基準測試中造成的 14% CPU 回歸。

privacy\_context.h

```c++
absl::StatusOr<privacy::context::PrivacyContext> GetRawPrivacyContext(
    const CensusHandle& h);
```

privacy\_context\_statusfree.h

```c++
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

## 批次操作

如果可能,一次處理多個項目而不是一次只處理一個。

absl::flat\_hash\_map 使用單個 SIMD 指令從一組鍵中比較每個鍵的一個雜湊位元組。

參見 [Swiss Table 設計說明](https://abseil.io/about/design/swisstables)和 Matt Kulukundis 在 [CppCon 2017](https://www.youtube.com/watch?v=ncHmEUmJZf4) 和 [CppCon 2019](https://www.youtube.com/watch?v=JZE3_0qvrMg) 上的相關演講。

raw\_hash\_set.h

```c++
// Returns a bitmask representing the positions of slots that match hash.
BitMask<uint32_t> Match(h2_t hash) const {
  auto ctrl = _mm_loadu_si128(reinterpret_cast<const __m128i*>(pos));
  auto match = _mm_set1_epi8(hash);
  return BitMask<uint32_t>(_mm_movemask_epi8(_mm_cmpeq_epi8(match, ctrl)));
}
```

執行單個操作來處理許多位元組並修復事物,而不是檢查每個位元組該做什麼。

ordered-code.cc

```c++
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

```c++
BigEndian::Store(val, buf + 1);  // buf[0] may be needed for length
const unsigned int length = OrderedNumLength(val);
char* start = buf + 9 - length - 1;
*start = length;
AppendUpto9(dest, start, length + 1);
```

通過更有效地分塊處理多個交錯輸入緩衝區來提高 Reed-Solomon 處理速度。

```{.bench}
Run on (12 X 3501 MHz CPUs); 2016-09-27T16:04:55.065995192-04:00
CPU: Intel Haswell with HyperThreading (6 cores) dL1:32KB dL2:256KB dL3:15MB
Benchmark                          Base (ns)  New (ns) Improvement
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

一次解碼四個整數(約 2004 年)。

引入了 [GroupVarInt 格式](https://static.googleusercontent.com/media/research.google.com/en//people/jeff/WSDM09-keynote.pdf),一次編碼/解碼 4 個可變長度整數組,而不是一次一個整數,以 5-17 位元組表示。解碼新格式中的一組 4 個整數所需時間約為解碼 4 個單獨 varint 編碼整數的 1/3。

groupvarint.cc

```c++
const char* DecodeGroupVar(const char* p, int N, uint32* dest) {
  assert(groupvar_initialized);
  assert(N % 4 == 0);
  while (N) {
    uint8 tag = *p;
    p++;

    uint8* lenptr = &groupvar_table[tag].length[0];

#define GET_NEXT                                        \
    do {                                                \
      uint8 len = *lenptr;                              \
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

一次編碼 4 個 k 位元數字組。

添加了 KBitStreamEncoder 和 KBitStreamDecoder 類別,一次將 4 個 k 位元數字編碼/解碼到位元流中。由於 K 在編譯時已知,編碼和解碼可以非常有效率。例如,由於一次編碼四個數字,程式碼可以假設流始終是位元組對齊的(對於偶數 k),或半位元組對齊的(對於奇數 k)。

## 展示多種技術的 CL

有時單個 CL 包含許多使用前述許多技術的效能改善變更。查看這些 CL 中的變更類型有時是一個很好的方式,可以進入在某個部分被識別為瓶頸後對系統的某些部分進行通用變更以加速效能的思維模式。

通過約 40% 加速 GPU 記憶體配置器。

GPUBFCAllocator 的配置/釋放速度提高 36-48%:

1.  通過句柄編號而不是指向 Chunk 的指標來識別塊。Chunk 資料結構現在配置在 `vector<Chunk>` 中,句柄是此向量中的索引以引用特定塊。這允許 Chunk 中的 next 和 prev 指標為 ChunkHandle(4 位元組),而不是 `Chunk*`(8 位元組)。
    
2.  當 Chunk 物件不再使用時,我們維護一個 Chunk 物件的空閒列表,其頭部由 ChunkHandle `free_chunks_list_` 指定,並使用 `Chunk->next` 指向下一個空閒列表條目。與(1)一起,這允許我們避免配置器中 Chunk 物件的堆配置/釋放,除了(很少)當 `vector<Chunk>` 增長時。它還使 Chunk 物件的所有記憶體連續。
    
3.  而不是讓 bins\_ 資料結構成為 std::set 並使用 lower\_bound 來定位給定 byte\_size 的適當 bin,我們改為有一個 bin 陣列,由 log₂(byte\_size/256) 函數索引。這允許通過幾個位元操作來定位 bin,而不是二叉搜尋樹查找。它還允許我們在連續陣列中配置所有 Bin 資料結構的儲存,而不是在許多不同的快取行中。這減少了當多個執行緒進行配置時必須在核心之間移動的快取行數。
    
4.  添加了 GPUBFCAllocator::AllocateRaw 的快速路徑,首先嘗試在不涉及 retry\_helper\_ 的情況下配置記憶體。如果初始嘗試失敗(返回 nullptr),那麼我們通過 retry\_helper\_,但通常我們可以避免幾個層級的程序呼叫以及具有多個參數的 std::function 的配置/釋放。
    
5.  註釋掉了大多數 VLOG 呼叫。當需要用於除錯時,可以通過取消註釋和重新編譯來有選擇地重新啟用這些。
    

添加了多執行緒基準測試以測試競爭下的配置。

在我的配有 Titan X 卡的桌面機器上,將 ptb\_word\_lm 的速度從每秒 8036 個單詞提高到每秒 8272 個單詞(+2.9%)。

```{.bench}
Run on (40 X 2801 MHz CPUs); 2016/02/16-15:12:49
CPU: Intel Ivybridge with HyperThreading (20 cores) dL1:32KB dL2:256KB dL3:25MB
Benchmark                          Base (ns)  New (ns) Improvement
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

通過一系列雜項變更將 Pathways 吞吐量提高約 20%。

-   將一堆特殊的快速描述符解析函數統一為單個 ParsedDescriptor 類別,並在更多地方使用此類別以避免昂貴的完整解析呼叫。
    
-   將幾個 protocol buffer 欄位從 string 更改為 bytes(避免不必要的 utf-8 檢查和相關的錯誤處理程式碼)。
    
-   DescriptorProto.inlined\_contents 現在是 string,不是 Cord(它預期僅用於較小的張量)。這需要在 tensor\_util.cc 中添加一堆複製輔助函數(現在需要支援 string 和 Cord)。
    
-   在幾個地方使用 flat\_hash\_map 而不是 std::unordered\_map。
    
-   添加了 MemoryManager::LookupMany 供 Stack op 使用,而不是每個批次元素呼叫 Lookup。此變更減少了設定開銷,如鎖定。
    
-   在 TransferDispatchOp 中刪除了一些不必要的字串建立。
    
-   在同一進程中將 1000 個 1KB 張量批次從一個元件傳輸到另一個元件的效能結果:
    

```{.bench}
Before: 227.01 steps/sec
After:  272.52 steps/sec (+20% throughput)
```

通過一系列變更提高約 15% 的 XLA 編譯器效能。

一些加速 XLA 編譯的變更:


1.  在 SortComputationsByContent 中,如果 a == b,在比較函數中回傳 false,以避免序列化和指紋計算長的計算字串。
    
2.  將 CHECK 改為 DCHECK,以避免在 HloComputation::ComputeInstructionPostOrder 中存取額外的快取行。
    
3.  在 CoreSequencer::IsVectorSyncHoldSatisfied() 中避免對前端指令進行昂貴的複製。
    
4.  重新設計兩參數的 HloComputation::ToString 和 HloComputation::ToCord 例程,將大部分工作改為附加到 std::string,而不是附加到 Cord。
    
5.  將 PerformanceCounterSet::Increment 改為僅執行一次雜湊表查找而不是兩次。
    
6.  精簡 Scoreboard::Update 程式碼
    

一個重要模型的 XLA 編譯時間總體加速 14%。

加速 Google Meet 應用程式碼中的低階日誌記錄。

加速 ScopedLogId,它位於每個封包的關鍵路徑上。

-   移除了似乎僅用於檢視是否違反不變量的 `LOG_EVERY_N(ERROR, ...)` 訊息。
-   內聯了 PushLogId 和 PopLogid() 例程(因為沒有 `LOG_EVERY_N_SECONDS(ERROR, ...)` 語句後,它們現在足夠小可以內聯)。
-   改用大小為 4 的固定陣列和一個 'int size' 變數,而不是用 `InlinedVector<...>` 來維護執行緒本地狀態。因為我們從未超過大小 4,所以 InlinedVector 的功能比需要的更通用。

```{.bench}
Base: 基準加上 scoped_logid_test.cc 中的程式碼以添加基準測試
New: 此變更清單

CPU: Intel Ivybridge with HyperThreading (20 cores) dL1:32KB dL2:256KB dL3:25MB
Benchmark                                      Base (ns)    New (ns) Improvement
----------------------------------------------------------------------------
BM_ScopedLogId/threads:1                               8           4    +52.6%
BM_ScopedLogId/threads:2                               8           4    +51.9%
BM_ScopedLogId/threads:4                               8           4    +52.9%
BM_ScopedLogId/threads:8                               8           4    +52.1%
BM_ScopedLogId/threads:16                             11           6    +44.0%
```

透過改進 Shape 處理,將 XLA 編譯時間減少約 31%。

幾項改進 XLA 編譯器效能的變更:

1.  透過多種方式改進了 ShapeUtil::ForEachIndex... 迭代的效能:
    
    -   在 ShapeUtil::ForEachState 中,僅儲存由 span 表示的陣列的指標,而不是完整的 span 物件。
        
    -   預先形成一個 ShapeUtil::ForEachState::indexes\_span 指向 ShapeUtil::ForEachState::indexes 向量,而不是在每次迴圈迭代中從向量構建此 span。
        
    -   儲存一個 ShapeUtil::ForEachState::indexes\_ptr 指標指向 ShapeUtil::ForEachState::indexes 向量的後備儲存,允許在 ShapeUtil::ForEachState::IncrementDim() 中進行簡單的陣列操作,而不是更昂貴的 vector::operator\[\] 操作。
        
    -   儲存一個在建構函式中透過呼叫 shape.layout().minor\_to\_major().data() 初始化的 ShapeUtil::ForEachState::minor\_to\_major 陣列指標,而不是為每個維度的每次迭代呼叫 LayoutUtil::Minor(...)。
        
    -   內聯了 ShapeUtil::ForEachState 建構函式和 ShapeUtil::ForEachState::IncrementDim() 例程
        
2.  改進了不需要在傳入函數中回傳 Status 功能的呼叫端的 ShapeUtil::ForEachIndex 迭代效能。透過引入 ShapeUtil::ForEachIndexNoStatus 變體來實現這一點,它接受 ForEachVisitorFunctionNoStatus(回傳純 bool)。這比接受 ForEachVisitorFunction(回傳 `StatusOr<bool>`,每個我們迭代的元素都需要昂貴的 `StatusOr<bool>` 解構函式呼叫)的 ShapeUtil::ForEachIndex 例程更快。
    
    -   在 LiteralBase::Broadcast 和 GenerateReduceOutputElement 中使用此 ShapeUtil::ForEachIndexNoStatus 變體。
3.  透過多種方式改進了 LiteralBase::Broadcast 的效能:
    
    -   在 literal.cc 中引入了模板化的 BroadcastHelper 例程,針對不同的原始位元組大小進行專門化(沒有這個,primitive\_size 是一個執行時變數,所以編譯器無法很好地優化每個元素發生的 memcpy,並且會呼叫通用的 memcpy 路徑,該路徑假設位元組計數相當大,即使在我們的情況下它是一個小的 2 的冪(通常是 1、2、4 或 8))。
        
    -   透過在 LiteralBase::Broadcast 例程開始時對 'shape()' 進行一次呼叫,避免了每次 Broadcast 呼叫約 ~(5 + num\_dimensions + num\_result\_elements) 個虛擬呼叫。散布在各處的看似無害的 'shape()' 呼叫最終歸結為 "root\_piece().subshape()",其中 subshape() 是一個虛擬函數。
        
    -   在 BroadcastHelper 例程中,對來源維度為 1 的情況進行特殊處理,並避免為此情況呼叫 IndexUtil::MultiDimensionalIndexToLinearIndex。
        
    -   在 BroadcastHelper 中,使用一個 scratch\_source\_array 指標變數指向 scratch\_source\_index 向量的後備儲存,並直接使用它以避免在每個元素程式碼內部進行 vector::operator\[\] 操作。還在 BroadcastHelper 中的每個元素迴圈外預先計算了一個 scratch\_source\_span 指向 scratch\_source\_index 向量,以避免在每個元素上從向量構建 span。
        
    -   引入了 IndexUtil::MultiDimensionalIndexToLinearIndex 的新三參數變體,其中呼叫者傳入與 shape 參數關聯的 minor\_to\_major span。在 BroadcastHelper 中使用此變體,為 src 和 dst shape 每次 Broadcast 計算一次,而不是每個複製的元素計算一次。
        
4.  在 ShardingPropagation::GetShardingFromUser 中,對於 HloOpcode::kTuple 情況,僅在我們發現運算元有興趣時呼叫 user.sharding().GetSubSharding(...)。避免急切呼叫它,將此例程的 CPU 時間從一次冗長編譯的 43.7s 減少到 2.0s。
    
5.  為 ShapeUtil::ForEachIndex 和 Literal::Broadcast 以及新的 ShapeUtil::ForEachIndexNoStatus 添加了基準測試。
    

```{.bench}
Base 是添加了 BM_ForEachIndex 和 BM_BroadcastVectorToMatrix 基準測試
(以及 BUILD 檔案變更以添加基準測試依賴),但沒有其他變更。

New 是此變更清單

Run on (72 X 1357.56 MHz CPU s) CPU Caches: L1 Data 32 KiB (x36)
L1 Instruction 32 KiB (x36) L2 Unified 1024 KiB (x36) L3 Unified 25344 KiB (x2)

Benchmark                                      Base (ns)    New (ns) Improvement
----------------------------------------------------------------------------
BM_MakeShape                                       18.40       18.90     -2.7%
BM_MakeValidatedShape                              35.80       35.60     +0.6%
BM_ForEachIndex/0                                  57.80       55.80     +3.5%
BM_ForEachIndex/1                                  90.90       85.50     +5.9%
BM_ForEachIndex/2                               1973606     1642197     +16.8%
```

新添加的 ForEachIndexNoStatus 比 ForEachIndex 變體快得多(它僅存在於此新變更清單中,但 BM\_ForEachIndexNoStatus/NUM 完成的基準測試工作與上述 BM\_ForEachIndex/NUM 結果相當)。

```{.bench}
Benchmark                                      Base (ns)    New (ns) Improvement
----------------------------------------------------------------------------
BM_ForEachIndexNoStatus/0                             0        46.90    ----
BM_ForEachIndexNoStatus/1                             0        65.60    ----
BM_ForEachIndexNoStatus/2                             0     1001277     ----
```

Broadcast 效能提高約 58%。

```{.bench}
Benchmark                                      Base (ns)    New (ns) Improvement
----------------------------------------------------------------------------
BM_BroadcastVectorToMatrix/16/16                   5556        2374     +57.3%
BM_BroadcastVectorToMatrix/16/1024               319510      131075     +59.0%
BM_BroadcastVectorToMatrix/1024/1024           20216949     8408188     +58.4%
```

對大型語言模型進行提前編譯的巨觀結果(程式不僅僅做 XLA 編譯,但花費不到一半的時間在 XLA 相關程式碼上):

基準程式整體: 573 秒 使用此變更清單程式整體: 465 秒 (+19% 改進)

執行此程式時編譯兩個最大 XLA 程式所花費的時間:

基準: 141s + 143s = 284s 使用此變更清單: 99s + 95s = 194s (+31% 改進)

在 Plaque(一個分散式執行框架)中,將大型程式的編譯時間減少約 22%。

透過小調整將編譯速度提高約 22%。

1.  加速檢測兩個節點是否共享公共來源。以前,我們會按排序順序獲取每個節點的來源,然後進行排序的交集。我們現在將一個節點的來源放入雜湊表中,然後迭代另一個節點的來源,檢查雜湊表。
2.  在步驟 1 中重用相同的臨時雜湊表。
3.  生成編譯的 proto 時,保留一個由 `pair<package, opname>` 鍵控的單個 btree,而不是 btree 的 btree。
4.  在前面的 btree 中儲存指向 opdef 的指標,而不是將 opdef 複製到 btree 中。

在大型程式(約 45K 個操作)上的速度測量:

```{.bench}
name             old time/op  new time/op  delta
BM_CompileLarge   28.5s ± 2%   22.4s ± 2%  -21.61%  (p=0.008 n=5+5)
```

MapReduce 改進(wordcount 基準測試速度提高約 2 倍)。

Mapreduce 加速:

1.  SafeCombinerMapOutput 類別的組合器資料結構已更改。我們使用 `hash_map<SafeCombinerKey, ValuePtr*>`(其中 ValuePtr 是值和重複計數的鏈結串列),而不是使用 `hash_multimap<SafeCombinerKey, StringPiece>`(表中插入的每個唯一鍵/值都有一個雜湊表條目)。這在三個方面有幫助:
    
    -   它顯著減少了記憶體使用量,因為我們每個值僅使用 "sizeof(ValuePtr) + value\_len" 位元組,而不是每個值使用 "sizeof(SafeCombinerKey) + sizeof(StringPiece) + value\_len + 新雜湊表條目開銷" 位元組。這意味著我們更少刷新 reducer 緩衝區。
        
    -   它明顯更快,因為當我們為表中已存在的鍵插入新值時,我們避免了額外的雜湊表條目(相反,我們只是將值掛鉤到該鍵的值鏈結串列中)。
        
    -   由於我們將重複計數與鏈結串列中的每個值關聯,我們可以表示此序列:
        
        ```c++
        Output(key, "1");
        Output(key, "1");
        Output(key, "1");
        Output(key, "1");
        Output(key, "1");
        ```
        
    
    作為 "key" 的鏈結串列中的單個條目,重複計數為 5。在內部,我們向使用者級組合函數產生 "1" 五次。(類似的技巧可能可以應用於 reduce 端)。
    
2.  (次要)在預設的 MapReductionBase::KeyFingerprintSharding 函數中添加了對 "nshards == 1" 的測試,如果我們僅使用 1 個 reduce 分片,則完全避免對鍵進行指紋計算(因為在這種情況下,我們可以直接回傳 0,而無需檢查鍵)。
    
3.  在為添加到組合器的每個鍵/值呼叫的程式碼路徑中,將一些 VLOG(3) 語句改為 DVLOG(3)。
    

將一個 wordcount 基準測試的時間從 12.56s 減少到 6.55s。

重新設計 SelectServer 中的警報處理程式碼以顯著改進其效能(從 771 ns 添加+移除警報到 271 ns)。

重新設計了 SelectServer 中的警報處理程式碼以顯著改進其效能。

變更:

1.  對 `AlarmQueue` 改用 `AdjustablePriorityQueue<Alarm>` 而不是 `set<Alarm*>`。這顯著加速了警報處理,將添加和移除警報所需的時間從 771 奈秒減少到 281 奈秒。此變更避免了每次設定警報的分配/釋放(用於 STL set 物件中的紅黑樹節點),並且還提供了更好的快取局部性(因為 AdjustablePriorityQueue 是在向量中實現的堆,而不是紅黑樹),在每次通過 selectserver 迴圈時操作 `AlarmQueue` 時觸及的快取行更少。
    
2.  將 Alarmer 中的 AlarmList 從 hash\_map 轉換為 dense\_hash\_map,以避免每次添加/刪除警報時的另一次分配/釋放(這也改善了添加/移除警報時的快取局部性)。
    
3.  移除了 `num_alarms_stat_` 和 `num_closures_stat_` MinuteTenMinuteHourStat 物件,以及相應的匯出變數。儘管監視這些看起來不錯,但在實踐中它們為關鍵網路程式碼添加了顯著的開銷。如果我將這些變數保留為 Atomic32 變數而不是 MinuteTenMinuteHourStat,它們仍然會將添加和移除警報的成本從 281 奈秒增加到 340 奈秒。
    

基準測試結果

```{.old}
Benchmark                      Time(ns)  CPU(ns) Iterations
-----------------------------------------------------------
BM_AddAlarm/1                       902      771     777777
```

使用此變更

```{.new}
Benchmark                      Time(ns)  CPU(ns) Iterations
-----------------------------------------------------------
BM_AddAlarm/1                       324      281    2239999
```

索引服務速度提高 3.3 倍!

我們在 2001 年計劃從磁碟索引服務切換到記憶體內索引服務時發現了許多效能問題。此變更修復了許多這些問題,並使我們從每秒 150 次查詢提高到每秒超過 500 次記憶體內查詢(對於雙處理器 Pentium III 機器上的 2 GB 記憶體內索引)。

-   對索引區塊解碼速度進行了大量效能改進(從微基準測試的 8.9 MB/s 到 13.1 MB/s)。
-   我們現在在解碼期間對區塊進行校驗和。這允許我們實現所有 getsymbol 操作,而無需任何邊界檢查。
-   我們有粗糙的巨集,將 BitDecoder 的各個欄位保存在整個迴圈的本地變數中,然後在迴圈結束時將它們儲存回去。
-   我們使用內聯組合語言來存取 Intel 晶片上的 'bsf' 指令以進行 getUnary(找到字中第一個 1 位元的索引)
-   當將值解碼到向量中時,我們在迴圈外調整向量大小,只是沿向量走指標,而不是進行邊界檢查的存取來儲存每個值。
-   在 docid 解碼期間,我們將 docid 保持在本地 docid 空間中,以避免乘以 num\_shards\_。只有當我們需要實際的 docid 值時,我們才乘以 num\_shards\_ 並加上 my\_shard\_。
-   IndexBlockDecoder 現在匯出一個介面 'AdvanceToDocid',它回傳第一個 docid ≥ "d" 的索引。這允許掃描以本地 docid 的形式完成,而不是在客戶端為區塊中的每個索引呼叫 GetDocid(index) 時強制將每個本地 docid 轉換為全域 docid。
-   現在按需解碼文件的位置資料,而不是在客戶端請求區塊內任何文件的位置資料時急切地為整個區塊解碼。
-   如果正在解碼的索引區塊在頁面邊界的 4 個位元組內結束,我們將其複製到本地緩衝區。這允許我們始終透過 4 位元組載入來載入我們的位元解碼緩衝區,而無需擔心如果我們超出 mmapped 頁面的末尾會出現段錯誤。
-   我們僅初始化各種評分資料結構的前 nterms\_ 個元素,而不是初始化所有 MAX\_TERMS 個(在某些情況下,我們不必要地為每個文件評分 memset 了 20K 到 100K 的資料)。
-   當正在計算的值為 0 時,避免對中間評分值進行 round\_to\_int 和後續計算(後續計算只是在這些情況下寫入 '0' 覆蓋我們 memset 的 0,而這是最常見的情況)。
-   將評分資料結構上的邊界檢查改為除錯模式斷言。

## 延伸閱讀

不按特定順序,這是作者發現有幫助的效能相關書籍和文章清單:

-   [Optimizing software in C++](https://www.agner.org/optimize/optimizing_cpp.pdf) by Agner Fog. 描述了許多用於改進效能的有用低階技術。
-   [Understanding Software Dynamics](https://www.oreilly.com/library/view/understanding-software-dynamics/9780137589692/) by Richard L. Sites. 涵蓋了診斷和修復效能問題的專家方法和進階工具。
-   [Performance tips of the week](https://abseil.io/fast/) - 有用技巧的集合。
-   [Performance Matters](https://travisdowns.github.io/) - 關於效能的文章集合。
-   [Daniel Lemire's blog](https://lemire.me/blog/) - 有趣演算法的高效能實現。
-   [Building Software Systems at Google and Lessons Learned](https://www.youtube.com/watch?v=modXC5IWTJI) - 一個影片,描述了 Google 十多年來遇到的系統效能問題。
-   [Programming Pearls](https://books.google.com/books/about/Programming_Pearls.html?id=kse_7qbWbjsC) and [More Programming Pearls: Confessions of a Coder](https://books.google.com/books/about/More_Programming_Pearls.html?id=a2AZAQAAIAAJ) by Jon Bentley. 關於從演算法開始並以簡單高效的實現結束的文章。
-   [Hacker's Delight](https://en.wikipedia.org/wiki/Hacker%27s_Delight) by Henry S. Warren. 用於解決一些常見問題的位元級和算術演算法。
-   [Computer Architecture: A Quantitative Approach](https://books.google.com/books/about/Computer_Architecture.html?id=cM8mDwAAQBAJ) by John L. Hennessy and David A. Patterson - 涵蓋電腦架構的許多方面,包括注重效能的軟體開發人員應該了解的方面,如快取、分支預測器、TLB 等。

## 建議引用

如果您想引用此文件,我們建議:

```
Jeffrey Dean & Sanjay Ghemawat, Performance Hints, 2025, https://abseil.io/fast/hints.html
```

或以 BibTeX 格式:

```
@misc{DeanGhemawatPerformance2025,
  author = {Dean, Jeffrey and Ghemawat, Sanjay},
  title = {Performance Hints},
  year = {2025},
  howpublished = {\url{https://abseil.io/fast/hints.html}},
}
```

## 致謝

許多同事對此文件提供了有益的回饋,包括:

-   Adrian Ulrich
-   Alexander Kuzmin
-   Alexei Bendebury
-   Alexey Alexandrov
-   Amer Diwan
-   Austin Sims
-   Benoit Boissinot
-   Brooks Moses
-   Chris Kennelly
-   Chris Ruemmler
-   Danila Kutenin
-   Darryl Gove
-   David Majnemer
-   Dmitry Vyukov
-   Emanuel Taropa
-   Felix Broberg
-   Francis Birck Moreira
-   Gideon Glass
-   Henrik Stewenius
-   Jeremy Dorfman
-   John Dethridge
-   Kurt Kluever
-   Kyle Konrad
-   Lucas Pereira
-   Marc Eaddy
-   Michael Marty
-   Michael Whittaker
-   Mircea Trofin
-   Misha Brukman
-   Nicolas Hillegeer
-   Ranjit Mathew
-   Rasmus Larsen
-   Soheil Hassas Yeganeh
-   Srdjan Petrovic
-   Steinar H. Gunderson
-   Stergios Stergiou
-   Steven Timotius
-   Sylvain Vignaud
-   Thomas Etter
-   Thomas Köppe
-   Tim Chestnutt
-   Todd Lipcon
-   Vance Lankhaar
-   Victor Costan
-   Yao Zuo
-   Zhou Fang
-   Zuguang Yang

-   [Performance Hints](https://abseil.io/fast/hints.html#performance-hints)
    -   [The importance of thinking about performance](https://abseil.io/fast/hints.html#the-importance-of-thinking-about-performance)
    -   [Estimation](https://abseil.io/fast/hints.html#estimation)
        -   [Example: Time to quicksort a billion 4 byte numbers](https://abseil.io/fast/hints.html#example-time-to-quicksort-a-billion-4-byte-numbers)
        -   [Example: Time to generate a web page with 30 image thumbnails](https://abseil.io/fast/hints.html#example-time-to-generate-a-web-page-with-30-image-thumbnails)
    -   [Measurement](https://abseil.io/fast/hints.html#measurement)
        -   [Profiling tools and tips](https://abseil.io/fast/hints.html#profiling-tools-and-tips)
        -   [What to do when profiles are flat](https://abseil.io/fast/hints.html#what-to-do-when-profiles-are-flat)
    -   [API considerations](https://abseil.io/fast/hints.html#api-considerations)
        -   [Bulk APIs](https://abseil.io/fast/hints.html#bulk-apis)
        -   [View types](https://abseil.io/fast/hints.html#view-types)
        -   [Pre-allocated/pre-computed arguments](https://abseil.io/fast/hints.html#pre-allocatedpre-computed-arguments)
        -   [Thread-compatible vs. Thread-safe types](https://abseil.io/fast/hints.html#thread-compatible-vs-thread-safe-types)
    -   [Algorithmic improvements](https://abseil.io/fast/hints.html#algorithmic-improvements)
    -   [Better memory representation](https://abseil.io/fast/hints.html#better-memory-representation)
        -   [Compact data structures](https://abseil.io/fast/hints.html#compact-data-structures)
        -   [Memory layout](https://abseil.io/fast/hints.html#memory-layout)
        -   [Indices instead of pointers](https://abseil.io/fast/hints.html#indices-instead-of-pointers)
        -   [Batched storage](https://abseil.io/fast/hints.html#batched-storage)
        -   [Inlined storage](https://abseil.io/fast/hints.html#inlined-storage)
        -   [Unnecessarily nested maps](https://abseil.io/fast/hints.html#unnecessarily-nested-maps)
        -   [Arenas](https://abseil.io/fast/hints.html#arenas)
        -   [Arrays instead of maps](https://abseil.io/fast/hints.html#arrays-instead-of-maps)
        -   [Bit vectors instead of sets](https://abseil.io/fast/hints.html#bit-vectors-instead-of-sets)
    -   [Reduce allocations](https://abseil.io/fast/hints.html#reduce-allocations)
        -   [Avoid unnecessary allocations](https://abseil.io/fast/hints.html#avoid-unnecessary-allocations)
        -   [Resize or reserve containers](https://abseil.io/fast/hints.html#resize-or-reserve-containers)
        -   [Avoid copying when possible](https://abseil.io/fast/hints.html#avoid-copying-when-possible)
        -   [Reuse temporary objects](https://abseil.io/fast/hints.html#reuse-temporary-objects)
    -   [Avoid unnecessary work](https://abseil.io/fast/hints.html#avoid-unnecessary-work)
        -   [Fast paths for common cases](https://abseil.io/fast/hints.html#fast-paths-for-common-cases)
        -   [Precompute expensive information once](https://abseil.io/fast/hints.html#precompute-expensive-information-once)
        -   [Move expensive computations outside loops](https://abseil.io/fast/hints.html#move-expensive-computations-outside-loops)
        -   [Defer expensive computation](https://abseil.io/fast/hints.html#defer-expensive-computation)
        -   [Specialize code](https://abseil.io/fast/hints.html#specialize-code)
        -   [Use caching to avoid repeated work](https://abseil.io/fast/hints.html#use-caching-to-avoid-repeated-work)
        -   [Make the compiler's job easier](https://abseil.io/fast/hints.html#make-the-compilers-job-easier)
        -   [Reduce stats collection costs](https://abseil.io/fast/hints.html#reduce-stats-collection-costs)
        -   [Avoid logging on hot code paths](https://abseil.io/fast/hints.html#avoid-logging-on-hot-code-paths)
    -   [Code size considerations](https://abseil.io/fast/hints.html#code-size-considerations)
        -   [Trim commonly inlined code](https://abseil.io/fast/hints.html#trim-commonly-inlined-code)
        -   [Inline with care](https://abseil.io/fast/hints.html#inline-with-care)
        -   [Reduce template instantiations](https://abseil.io/fast/hints.html#reduce-template-instantiations)
        -   [Reduce container operations](https://abseil.io/fast/hints.html#reduce-container-operations)
    -   [Parallelization and synchronization](https://abseil.io/fast/hints.html#parallelization-and-synchronization)
        -   [Exploit parallelism](https://abseil.io/fast/hints.html#exploit-parallelism)
        -   [Amortize lock acquisition](https://abseil.io/fast/hints.html#amortize-lock-acquisition)
        -   [Keep critical sections short](https://abseil.io/fast/hints.html#keep-critical-sections-short)
        -   [Reduce contention by sharding](https://abseil.io/fast/hints.html#reduce-contention-by-sharding)
        -   [SIMD Instructions](https://abseil.io/fast/hints.html#simd-instructions)
        -   [Reduce false sharing](https://abseil.io/fast/hints.html#reduce-false-sharing)
        -   [Reduce frequency of context switches](https://abseil.io/fast/hints.html#reduce-frequency-of-context-switches)
        -   [Use buffered channels for pipelining](https://abseil.io/fast/hints.html#use-buffered-channels-for-pipelining)
        -   [Consider lock-free approaches](https://abseil.io/fast/hints.html#consider-lock-free-approaches)
    -   [Protocol Buffer advice](https://abseil.io/fast/hints.html#protobuf-advice)
    -   [C++-Specific advice](https://abseil.io/fast/hints.html#c-specific-advice)
        -   [absl::flat\_hash\_map (and set)](https://abseil.io/fast/hints.html#abslflat_hash_map-and-set)
        -   [absl::btree\_map/absl::btree\_set](https://abseil.io/fast/hints.html#abslbtree_mapabslbtree_set)
        -   [util::bitmap::InlinedBitVector](https://abseil.io/fast/hints.html#utilbitmapinlinedbitvector)
        -   [absl::InlinedVector](https://abseil.io/fast/hints.html#abslinlinedvector)
        -   [gtl::vector32](https://abseil.io/fast/hints.html#gtlvector32)
        -   [gtl::small\_map](https://abseil.io/fast/hints.html#gtlsmall_map)
        -   [gtl::small\_ordered\_set](https://abseil.io/fast/hints.html#gtlsmall_ordered_set)
        -   [gtl::intrusive\_list](https://abseil.io/fast/hints.html#gtl-intrusive_list)
        -   [Limit absl::Status and absl::StatusOr usage](https://abseil.io/fast/hints.html#limit-abslstatus-and-abslstatusor-usage)
    -   [Bulk operations](https://abseil.io/fast/hints.html#bulk-operations)
    -   [CLs that demonstrate multiple techniques](https://abseil.io/fast/hints.html#cls-that-demonstrate-multiple-techniques)
    -   [Further reading](https://abseil.io/fast/hints.html#further-reading)
    -   [Suggested citation](https://abseil.io/fast/hints.html#suggested-citation)
    -   [Acknowledgments](https://abseil.io/fast/hints.html#acknowledgments)

![](/img/typography_white.png)

[©2017 Abseil | Live at Head](https://abseil.io/fast/hints.html#)

[Privacy Policy](https://policies.google.com/privacy)

[About Abseil](https://abseil.io/about/)-   [Introduction](https://abseil.io/about/intro)
-   [Philosophy](https://abseil.io/about/philosophy)
-   [Compatibility](https://abseil.io/about/compatibility)
-   [Design Notes](https://abseil.io/about/design/)

* * *

[Dev Guides](https://abseil.io/docs/)-   [C++](https://abseil.io/docs/cpp/)
-   [Abseil Blog](https://abseil.io/blog/)

* * *

[Community](https://abseil.io/community/)-   [GitHub](https://github.com/abseil/)
-   [Twitter](https://twitter.com/abseilio)
