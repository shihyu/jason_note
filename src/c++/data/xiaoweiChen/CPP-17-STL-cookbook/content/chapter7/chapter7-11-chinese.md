# 通過集成std::char_traits創建自定義字符串類

我們知道`std::string`非常好用。不過，對於一些朋友來說他們需要對自己定義的字符串類型進行處理。

使用它們自己的字符串類型顯然不是一個好主意，因為對於字符串的安全處理是很困難的。幸運的是，`std::string`是`std::basic_string`類型的一個特化版本。這個類中包含了所有複雜的內存處理，不過其對字符串的拷貝和比較沒有添加任何條件。所以我們可以基於`basic_string`，將其所需要包含的自定義類作為一個模板參數傳入。

本節中，我們將來看下如何傳入自定義類型。然後，在不實現任何東西的情況下，如何對自定義字符串進行創建。

## How to do it...

我們將實現兩個自定義字符串類：`lc_string`和`ci_string`。第一個類將通過輸入創建一個全是小寫字母的字符串。另一個字符串類型不會對輸入進行任何變化，不過其會對字符串進行大小寫不敏感的比較：

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <algorithm>
   #include <string>
   
   using namespace std;
   ```

2. 然後要對`std::tolower`函數進行實現，其已經定義在頭文件`<cctype>`中。其函數也是現成的，不過其不是`constexpr`類型。C++17中一些`string`函數可以聲明成`constexpr`類型，但是還要使用自定義的類型。所以對於輸入字符串，只將大寫字母轉換為小寫，而其他字符則不進行修改：

   ```c++
   static constexpr char tolow(char c) {
       switch (c) {
       case 'A'...'Z': return c - 'A' + 'a'; // 讀者自行將case展開
       default: 	    return c;
       }
   }
   ```

3.  `std::basic_string`類可以接受三個模板參數：字符類型、字符特化類和分配器類型。本節中我們只會修改字符特化類，因為其定義了字符串的行為。為了重新實現與普通字符串不同的部分，我們會以`public`方式繼承標準字符特化類：

   ```c++
   class lc_traits : public char_traits<char> {
   public:
   ```

4. 我們類能接受輸入字符串，並將其轉化成小寫字母。這裡有一個函數，其是字符級別的，所以我們可以對其使用`tolow`函數。我們的這個函數為`constexpr`：

   ```c++
   	static constexpr
   	void assign(char_type& r, const char_type& a ) {
   		r = tolow(a);
   	}
   ```

5. 另一個函數將整個字符串拷貝到我們的緩衝區內。使用`std::transform`將所有字符從源字符串中拷貝到內部的目標字符串中，同時將每個字符與其小寫版本進行映射：

   ```c++
       static char_type* copy(char_type* dest,
      						 const char_type* src,
       					 size_t count) {
       	transform(src, src + count, dest, tolow);
       	return dest;
       }
   };
   ```

6. 上面的特化類可以幫助我們創建一個字符串類，其能有效的將字符串轉換成小寫。接下來我們在實現一個類，其不會對原始字符串進行修改，但是其能對字符串做大小寫敏感的比較。其繼承於標準字符串特徵類，這次將對一些函數進行重新實現：

   ```c++
   class ci_traits : public char_traits<char> {
   public:
   ```

7. `eq`函數會告訴我們兩個字符是否相等。我們也會實現一個這樣的函數，但是我們只實現小寫字母的版本。這樣'A'與'a'就是相等的：

   ```c++
       static constexpr bool eq(char_type a, char_type b) {
       	return tolow(a) == tolow(b);
       }
   ```

8. `lt`函數會告訴我們兩個字符在字母表中的大小情況。這裡使用了邏輯操作符，並繼續對兩個字符使用轉換成小寫的函數：

   ```c++
       static constexpr bool lt(char_type a, char_type b) {
       	return tolow(a) < tolow(b);
       }	
   ```

9. 最後兩個函數都是字符級別的函數，接下來兩個函數都為字符串級別的函數。`compare`函數與`strncmp`函數差不多。當兩個字符串的長度`count`相等，那麼就返回0。如果不相等，會返回一個負數或一個正數，返回值就代表了其中哪一個在字母表中更小。並計算兩個字符串中所有字符之間的距離，當然這些都是在小寫情況下進行的操作。C++14後，這個函數可以聲明成`constexpr`類型：

   ```c++
    	static constexpr int compare(const char_type* s1,
       						   const char_type* s2,
       						   size_t count) {
           for (; count; ++s1, ++s2, --count) {
               const char_type diff (tolow(*s1) - tolow(*s2));
               if (diff < 0) { return -1; }
               else if (diff > 0) { return +1; }
           }
       	return 0;
       }
   ```

10. 我們所需要實現的最後一個函數就是大小寫不敏感的`find`函數。對於給定輸入字符串`p`，其長度為`count`，我們會對某個字符`ch`的位置進行查找。然後，其會返回一個指向第一個匹配字符位置的指針，如果沒有找到則返回`nullptr`。這個函數比較過程中我們需要使用`tolow`函數將字符串轉換成小寫，以匹配大小寫不敏感的查找。不幸的是，我們不能使用`std::find_if`來做這件事，因為其是非`constexpr`函數，所以我們需要自己去寫一個循環：

    ```c++
        static constexpr
        const char_type* find(const char_type* p,
                              size_t count,
                              const char_type& ch) {
        const char_type find_c {tolow(ch)};
        
        for (; count != 0; --count, ++p) {
        	if (find_c == tolow(*p)) { return p; }
        }
        	return nullptr;
        }
    };
    ```

11. OK，所有自定義類都完成了。這裡我們可以定義兩種新字符串類的類型。`lc_string`代表小寫字符串，`ci_string`代表大小寫不敏感字符串。這兩種類型與`std::string`都有所不同：

    ```c++
    using lc_string = basic_string<char, lc_traits>;
    using ci_string = basic_string<char, ci_traits>;
    ```

12. 為了能讓輸出流接受新類，我們需要對輸出流操作符進行重載：

    ```c++
    ostream& operator<<(ostream& os, const lc_string& str) {
    	return os.write(str.data(), str.size());
    }
    
    ostream& operator<<(ostream& os, const ci_string& str) {
    	return os.write(str.data(), str.size());
    }
    ```

13. 現在我們來對主函數進行編寫。先讓我們創建一個普通字符串、小寫字符串和大小寫不敏感字符串的實例，然後直接將其進行打印。其在終端上看起來都很正常，不過小寫字符串將所有字符轉換成了小寫：

    ```c++
    int main()
    {
        cout << " string: "
            << string{"Foo Bar Baz"} << '\n'
            << "lc_string: "
            << lc_string{"Foo Bar Baz"} << '\n'
            << "ci_string: "
            << ci_string{"Foo Bar Baz"} << '\n';
    ```

14. 為了測試大小寫不敏感字符串，可以實例化兩個字符串，這兩個字符串只有在大小寫方面有所不同。當我們將這兩個字符串進行比較時，其應該是相等的：

    ```c++
    	ci_string user_input {"MaGiC PaSsWoRd!"};
    	ci_string password {"magic password!"};
    ```

15. 之後，對其進行比較，然後將匹配的結果進行打印：

    ```c++
        if (user_input == password) {
            cout << "Passwords match: \"" << user_input
            	 << "\" == \"" << password << "\"\n";
        }
    }
    ```

16. 編譯並運行程序，其輸出和我們期望的相符。開始的三行並未對輸入進行修改，除了`lc_string`將所有字符轉換成了小寫。最後的比較，在大小寫不敏感的前提下，也是相等的：

    ```c++
    $ ./custom_string
    string: Foo Bar Baz
    lc_string: foo bar baz
    ci_string: Foo Bar Baz
    Passwords match: "MaGiC PaSsWoRd!" == "magic password!"
    ```

## How it works...

我們完成的所有子類和函數實現，在新手看來十分的不可思議。這些函數簽名都來自於哪裡？為什麼我們為了函數簽名，就要對相關功能性的函數進行重新實現呢？

首先，來看一下`std::string`的類聲明：

```c++
template <
    class CharT,
    class Traits = std::char_traits<CharT>,
    class Allocator = std::allocator<CharT>
    >
class basic_string;
```

可以看出`std::string`其實就是一個`std::basic_string<char>` 類，並且其可以擴展為`std::basic_string<char, std::char_traits<char>, std::allocator<char>> `。OK，這是一個非常長的類型描述，不過其意義何在呢？這就表示字符串可以不限於有符號類型`char`，也可以是其他類型。其對於字符串類型都是有效的，這樣就不限於處理ASCII字符集。當然，這不是我們的關注點。

` char_traits<char>`類包含`basic_string`所需要的算法。` char_traits<char>`可以進行字符串間的比較、查找和拷貝。

`allocator<char>`類也是一個特化類，不過其運行時給字符串進行空間的分配和回收。這對於現在的我們來說並不重要，我們只使用其默認的方式就好。

當我們想要一個不同的字符串類型是，可以嘗試對`basic_string`和`char_traits`類中提供的方法進行復用。我們實現了兩個`char_traits`子類：`case_insentitive`和`lower_caser`類。我們可以將這兩個字符串類替換標準`char_traits`類型。

> Note：
>
> 為了探尋`basic_string`適配的可能性，我們需要查詢C++ STL文檔中關於`std::char_traits`的章節，然後去了解還有那些函數需要重新實現。