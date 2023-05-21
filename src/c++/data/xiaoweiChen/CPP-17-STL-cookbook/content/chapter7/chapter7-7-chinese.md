# 使用輸入文件初始化複雜對象

將整型、浮點型和字符串分開讀取不是困難，因為流操作符`>>`對於基礎類型有重載的版本，並且輸入流會將輸入中的空格去除。

不過，對於更加複雜的結構體來說，我們應該如何將其從輸入流中讀取出來，並且當我們的字符串中需要多個單詞的時候應該怎麼做呢(在空格處不斷開)？

對於任意類型，我們都可以對輸入流`operator>>`操作符進行重載，接下來我們就要看下如何做這件事：

## How to do it...

本節，我們將定義一個數據結構，並從標準輸入中獲取數據：

1. 包含必要的頭文件和聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <iomanip>
   #include <string>
   #include <algorithm>
   #include <iterator>
   #include <vector>
   
   using namespace std; 
   ```

2. 創建一個複雜的對象，我們定義了一個名為`city`的結構體。城市需要有名字，人口數量和經緯座標。

   ```c++
   struct city {
       string name;
       size_t population;
       double latitude;
       double longitude;
   };
   ```

3. 為了從輸入流中讀取一個城市的信息，這時我們就需要對`operator>>`進行重載。對於操作符來說，會跳過`ws`開頭的所有空格，我們不希望空格來汙染城市的名稱。然後，會對一整行的文本進行讀取。這樣類似於從輸入文件中讀取一整行，行中只包含城市的信息。然後，我們就可以用空格將人口，經緯度進行區分：

   ```c++
   istream& operator>>(istream &is, city &c)
   {
       is >> ws;
       getline(is, c.name);
       is >> c.population
           >> c.latitude
           >> c.longitude;
       return is;
   }
   ```

4. 主函數中，我們創建一個`vector`，其包含了若干城市元素，使用`std::copy`將其進行填充。我們會將輸入的內容拷貝到`istream_iterato`中。通過給定的`city`結構體作為模板參數，其會使用重載過的`operator>>`進行數據的讀取：

   ```c++
   int main()
   {
       vector<city> l;
       
       copy(istream_iterator<city>{cin}, {},
       	back_inserter(l)); 
   ```

5. 為了瞭解城市信息是否被正確解析，我們會將其進行打印。使用格式化輸出`left << setw(15) <<`，城市名稱左邊必有很多的空格，這樣我們的輸出看起來就很漂亮：

    ```c++
       for (const auto &[name, pop, lat, lon] : l) {
           cout << left << setw(15) << name
               << " population=" << pop
               << " lat=" << lat
               << " lon=" << lon << '\n';
       }
      }
    ```

6. 例程中所用到的文件內容如下。我們將四個城市的信息寫入文件：

   ```c++
   Braunschweig
   250000 52.268874 10.526770
   Berlin
   4000000 52.520007 13.404954
   New York City
   8406000 40.712784 -74.005941
   Mexico City
   8851000 19.432608 -99.133208
   ```

7. 編譯並運行程序，將會得到如下輸入。我們在輸入文件中為城市名稱前添加一些不必要的空白，以查看空格是如何被過濾掉的：

   ```c++
   $ cat cities.txt| ./initialize_complex_objects
   Braunschweig    population = 250000 lat = 52.2689 lon = 10.5268
   Berlin          population = 4000000 lat = 52.52 lon = 13.405
   New York City   population = 8406000 lat = 40.7128 lon = -74.0059
   Mexico City     population = 8851000 lat = 19.4326 lon = -99.1332
   ```

## How it works...

本節也非常短。我們只是創建了一個新的結構體`city`，我們對`std::istream`迭代器的`operator>>`操作符進行重載。這樣也就允許我們使用`istream_iterator<city>`對數據進行反序列化。

關於錯誤檢查則是一個開放性的問題。我們現在再來看下`operator>>`實現：

```c++
istream& operator>>(istream &is, city &c)
{
    is >> ws;
    getline(is, c.name);
    is >> c.population >> c.latitude >> c.longitude;
    return is;
}
```

我們讀取了很多不同的東西。讀取數據發生了錯誤，下一個應該怎麼辦？這是不是意味著我們有可能讀取到錯誤的數據？不會的，這不可能發生。即便是其中一個元素沒有被輸入流進行解析，那麼輸入流對象則會置於錯誤的狀態，並且拒絕對剩下的輸入進行解析。這樣就意味著，如果`c.population`或`c.latitude`沒有被解析出來，那麼對應的輸入數據將會被丟棄，並且我們可以看到反序列了一半的`city`對象。

站在調用者的角度，我們需要注意這句`if(input_stream >> city_object)`。這也就表面流表達式將會被隱式轉換成一個布爾值。當其返回false時，輸入流對象則處於錯誤狀態。如果出現錯誤，就需要採取相應的措施對流進行重置。

本節中沒有使用`if`判斷，因為我們讓`  std::istream_iterator<city>`進行反序列化。`operator++`在迭代器的實現中，會在解析時對其狀態進行檢查。當遇到錯誤時，其將會停止之後的所有迭代。當前迭代器與`end`迭代器比較返回true時，將終止`copy`算法的執行。如此，我們的代碼就很安全了。