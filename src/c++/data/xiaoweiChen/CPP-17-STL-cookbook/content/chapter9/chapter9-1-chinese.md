# 標準算法的自動並行

C++17對並行化的一個重要的擴展，就是對標準函數的執行策略進行了修改。69個標準算法都能並行到不同的核上運行，甚至是向量化。

對於使用者來說，如果經常使用STL中的算法，那麼就能很輕易的進行並行。可以通過基於現存的STL算法一個執行策略，然後就能享受並行帶來的好處。

本節中，我們將實現一個簡單的程序(通過一個不太嚴謹的使用場景)，其中使用了多個STL算法。使用這些算法時，我們將看到如何在C++17中，使用執行策略讓這些算法並行化。本節最後一個子節中，我們會了解不同執行策略的區別。

## How to do it...

本節，將使用標準算法來完成一個程序。這個程序本身就是在模擬我們實際工作中的場景。當使用這些標準算法時，我們為了得到更快的性能，將執行策略嵌入其中：

1. 包含必要的頭文件，並聲明所使用的命名空間。其中`execution`頭文件是C++17之後加入的：

   ```c++
   #include <iostream>
   #include <vector>
   #include <random>
   #include <algorithm>
   #include <execution>
   
   using namespace std;
   ```

2. 這裡聲明一個謂詞函數，其用來判斷給定數值的奇偶：

   ```c++
   static bool odd(int n) { return n % 2; }
   ```

3. 主函數中先來定義一個很大的`vector`。我們將對其進行填充，並對其中數值進行計算。這個代碼的執行速度是非常非常慢的。對於不同配置的電腦來說，這個`vector`的尺寸可能會有變化：

   ```c++
   int main()
   {
   	vector<int> d (50000000);
   ```

4. 為了向`vector`中塞入隨機值，我們對隨機數生成器進行了實例化，並選擇了一種分佈進行生成，並且將其打包成為一個可調用的對象。如果你對隨機數生成器不太熟，那麼你可以回看一下本書的第8章：

   ```c++
   	mt19937 gen;
   
   	uniform_int_distribution<int> dis(0, 100000);
   	auto rand_num ([=] () mutable { return dis(gen); }); 
   ```

5. 現在，`std::generate`算法會用隨機值將`vector`填滿。這個算法是C++17新加入的算法，其能接受一種新的參數——執行策略。我們在這個位置上填入`std::execution::par`，其能讓代碼進行自動化並行。通過這個參數的傳入，可以使用多線程的方式對`vector`進行填充，如果我們的電腦有多核CPU，那麼就可以大大節約我們的時間：

   ```c++
   	generate(execution::par, begin(d), end(d), rand_num);
   ```

6. `std::sort`想必大家都是非常熟悉了。C++17對其也提供了執行策略的參數：

   ```c++
   	sort(execution::par, begin(d), end(d));
   ```

7. 還有`std::reverse`:

   ```c++
   	reverse(execution::par, begin(d), end(d));
   ```

8. 然後，我們使用`std::count_if`來計算`vector`中奇數的個數。並且也可以通過添加執行策略參數對該算法進行加速：

   ```c++
   	auto odds (count_if(execution::par, begin(d), end(d), odd));
   ```

9. 最後，將結果進行打印：

   ```c++
   	cout << (100.0 * odds / d.size())
   		<< "% of the numbers are odd.\n";
   }
   ```

10. 編譯並運行程序，就能得到下面的輸出。整個程序中我們就使用了一種執行策略，我們對不同執行策略之間的差異也是非常感興趣。這個就留給讀者當做作業。去了解一下不同的執行策略，比如`seq`，`par`和`par_vec`。 不過，對於不同的執行策略，我們肯定會得到不同的執行時間：

    ```c++
    $ ./auto_parallel
    50.4% of the numbers are odd.
    ```

## How it works...

本節並沒有設計特別複雜的使用場景，這樣就能讓我們集中精力與標準庫函數的調用上。並行版本的算法和標準串行的算法並沒有什麼區別。其差別就是多了一個參數，也就是執行策略。

讓我們結合以下代碼，來看三個核心問題：

```c++
generate(execution::par, begin(d), end(d), rand_num);
sort( execution::par, begin(d), end(d));
reverse( execution::par, begin(d), end(d));

auto odds (count_if(execution::par, begin(d), end(d), odd));
```

**哪些STL可以使用這種方式進行並行？**

69種存在的STL算法在C++17標準中，都可以使用這種方式進行並行，還有7種新算法也支持並行。雖然這種升級對於很多實現來說很傷，但是也只是在接口上增加了一個參數——執行策略參數。這也不是意味著我們總要提供一個執行策略參數。並且執行策略參數放在了第一個參數的位置上。

這裡有69個升級了的算法。並且有7個新算法在一開始就支持了併發：

```c++
adjacent difference, adjacent find.
all_of, any_of, none_of
copy
count
equal
fill
find
generate
includes
inner product
in place merge, merge
is heap, is partitioned, is sorted
lexicographical_compare
min element, minmax element
mismatch
move
n-th element
partial sort, sort copy
partition
remove + variations
replace + variations
reverse / rotate
search
set difference / intersection / union /symmetric difference
sort
stable partition
swap ranges
transform
unique
```

詳細的內容可以查看[C++ Reference](http://en.cppreference.com/w/cpp/experimental/parallelism/existing)。([參考頁面](https://www.bfilipek.com/2017/08/cpp17-details-parallel.html))

這些算法的升級是一件令人振奮的事！如果我們之前的程序使用了很多的STL算法，那麼就很容易的將這些算法進行並行。這裡需要注意的是，這樣的的改變並不意味著每個程序自動化運行N次都會很快，因為多核編程更為複雜，所要注意的事情更多。

不過，在這之前我們現在都會用`std::thread`，`std::async`或是第三方庫進行復雜的並行算法設計，而現在我們可以以更加優雅、與操作系統不相關的方式進行算法的並行化。

**執行策略是如何工作的？**

執行策略會告訴我們的標準函數，以何種方式進行自動化並行。

`std::execution`命名空間下面，有三種策略類型：

| 策略                                                         | 含義                                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [sequenced_policy](https://zh.cppreference.com/w/cpp/algorithm/execution_policy_tag_t) | 算法使用串行的方式執行，這與原始執行方式沒有什麼區別。全局可用的實例命名為`std::execution::seq`。 |
| [parallel_policy](https://zh.cppreference.com/w/cpp/algorithm/execution_policy_tag_t) | 算法使用多線程的方式進行執行。全局可用的實例命名為`std::execution::par`。 |
| [parallel_unsequenced_policy](https://zh.cppreference.com/w/cpp/algorithm/execution_policy_tag_t) | 算法使用多線程的方式進行執行。並允許對代碼進行向量化。在這個例子中，線程間可以對內存進行交叉訪問，向量化的內容可以在同一個線程中執行。全局可用的實例命名為`std::execution::par_unseq`。 |

執行策略意味著我們需要進行嚴格限制。嚴格的約定，讓我們有更多並行策略可以使用：

- 並行算法對所有元素的訪問，必須不能導致死鎖或數據競爭。
- 向量化和並行化中，所有可訪問的函數不能使用任何一種阻塞式同步。

我們需要遵守這些規則，這樣才不會將錯誤引入到程序中。

> Note：
>
> STL的自動並行化，並總能保證有加速。因為具體的情況都不一樣，所以可能在很多情況下並行化並沒有加速。多核編程還是很有難度的。

**向量化是什麼意思？**

向量化的特性需要編譯器和CPU都支持，讓我們先來簡單的瞭解一下向量化是如何工作的。假設我們有一個非常大的`vector`。簡單的實現可以寫成如下的方式：

```c++
std::vector<int> v {1, 2, 3, 4, 5, 6, 7 /*...*/};

int sum {std::accumulate(v.begin(), v.end(), 0)};
```

編譯器將會生成一個對`accumulate`調用的循環，其可能與下面代碼類似：

```c++
int sum {0};

for (size_t i {0}; i < v.size(); ++i) {
	sum += v[i];
}
```

從這點說起，當編譯器開啟向量化時，就會生成類似如下的代碼。每次循環會進行4次累加，這樣循環次數就要比之前減少4倍。為了簡單說明問題，我們這裡沒有考慮不為4倍數個元素的情況：

```c++
int sum {0};
for (size_t i {0}; i < v.size() / 4; i += 4) {
	sum += v[i] + v[i+1] + v[i + 2] + v[i + 3];
}
// if v.size() / 4 has a remainder,
// real code has to deal with that also.
```

為什麼要這樣做呢？很多CPU指令都能支持這種操作`sum += v[i] + v[i+1] + v[i+2] + v[i+3]；`，只需要一個指令就能完成。使用盡可能少的指令完成儘可能多的操作，這樣就能加速程序的運行。

自動向量化非常困難，因為編譯器需非常瞭解我們的程序，這樣才能進行加速的情況下，不讓程序的結果出錯。目前，至少可以通過使用標準算法來幫助編譯器。因為這樣能讓編譯器更加了解哪些數據流能夠並行，而不是從複雜的循環中對數據流的依賴進行分析。



