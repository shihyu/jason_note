# 安全的標識失敗——std::optional

當程序與外界的聯繫只依賴於一些變量時，那麼各種失敗都可能發生。

也就是，我們寫了一個函數，其會返回一個值，但是當函數接口進行變更後，可能就無法獲取這個返回值了。我們來看下對一個返回字符串的函數，怎樣的接口會容易出現失敗的情況：

- 使用引用值作為返回值：`bool get_string(string&);`
- 返回一個可以被設置為nullptr的指針(或智能指針)：`string* get_string();`
- 當函數出錯時，直接拋出異常：`string get_string();`

以上的方式有缺點，也有優點。在C++17之後，我們會使用一種新類型來解決這個問題：`std::optional`。可選值的概念來自於純函數式編程語言(在純函數式語言中，這個類型為Maybe類型)，並且可以讓代碼看上去很優雅。

我們可以將`optional`包裝到我們的類型中，其可以表示空值或錯誤值。本節中，我們就會來學習怎麼使用這個類型。

## How to do it...

本節，我們將實現一個程序用於從用戶輸入中讀取整型數，然後將這些數字加起來。因為不確定用戶會輸入什麼，所以我們會使用`optional`進行錯誤處理：

1. 包含必要的頭文件，並聲明所使用的命名空間。

   ```c++
   #include <iostream>
   #include <optional>
   
   using namespace std; 
   ```

2. 定義一個整型類型，其可能會包含一個值，使用`std::optional`類型來完成這件事。將目標類型包裝進`optional`，我們會給其一個附加狀態，其表示當前對象中沒有值：

   ```c++
   using oint = optional<int>;
   ```

3. 使用包裝後的整型類型，我們用其來表示函數返回失敗的情況。當從用戶輸入中獲取一個整數時，這個函數可能會失敗，因為用戶可能輸入的就不是我們想要的東西，返回可選整型就能很好的解決這個問題。當成功的讀取一個整數，我們會將其放入`optional<int>`的構造函數中。否則，我們將返回一個默認構造的`optional`，其代表沒有獲取成功：

   ```c++
   oint read_int()
   {
       int i;
       if (cin >> i) { return {i}; }
       return {};
   }
   ```

4. 除了獲取整數，我們還能做的更多。那怎麼使用兩個可選整數進行相加呢？如果兩個可選整數中具有相應的整數值，那麼使用實際的數值直接相加。存在有空的可選變量時，我們會返回一個空的可選變量。這個函數需要簡單的來解釋一下：通過隱式轉換，將`optional<int>`變量a和b轉化成一個布爾表達式(寫成!a和!b)，這就能讓我們確定可選變量中是否有值。如果其中有值，我們將對其使用指針或是迭代器的方式，對a和b直接解引用：

   ```c++
   oint operator+(oint a, oint b)
   {
       if (!a || !b) { return {}; }
       return {*a + *b};
   }
   ```

5. 重載加法操作，可以直接和一個普通整數進行相加：

   ```c++
   oint operator+(oint a, int b)
   {
       if (!a) { return {}; }
       
       return {*a + b};
   }
   ```

6. 現在來完成主函數部分，我們會讓用戶輸入兩個數值：

   ```c++
   int main()
   {
       cout << "Please enter 2 integers.\n> ";
       
       auto a {read_int()};
       auto b {read_int()}; 
   ```

7. 然後，將獲取的數值進行相加，並再與10進行相加。這裡`a`和`b`為可選整型類變量，`sum`也為可選整型類變量：

   ```c++
   	auto sum (a + b + 10);
   ```

8. 當`a`和/或`b`中不包含一個值時，`sum`就也不包含任何值。可選整型可依然我們不必顯式的對`a`和`b`進行檢查。當遇到空值的時，我們定義的操作符能很完美的處理這樣的情況。這樣，我們只需要對結果可選整型變量進行檢查即可。如果包含一個值，那就可以安全的對這個值進行訪問，並將其進行打印：

   ```c++
   if (sum) {
   	cout << *a << " + " << *b << " + 10 = "
   		<< *sum << '\n';
   ```

9. 當用戶輸入了非數字內容，我們將會輸出錯誤信息：

   ```c++
       } else {
           cout << "sorry, the input was "
           		"something else than 2 numbers.\n";
       }
   }
   ```

10. 完成了！編譯並運行程序，我們將會得到如下輸出：

    ```c++
    $ ./optional
    Please enter 2 integers.
    > 1 2
    1 + 2 + 10 = 13
    ```

11. 當輸入中包含非數字元素，我們將會得到如下輸出：

    ```c++
    $ ./optional
    Please enter 2 integers.
    > 2 z
    sorry, the input was something else than 2 numbers.
    ```

## How it works...

`optional`非常簡單易用。其可以幫助我們對錯誤的情況進行處理，當我們所需要的類型為T時，可以將其特化`std::optional<T>`版本類型進行封裝。

當需要從一些地方獲取一些值時，我們可以用其來檢查我們是否成功的獲取了對應的數值。`bool optional::has_value()`可以幫助我們完成這件事。當其包含值時，其會返回true，我們就能直接對數值進行訪問，對可選類型的值訪問也可以通過函數`T& optional::value()`進行。

例子中，使用`  if (x) {...}`和`*x`來替代`if (x.has_value()) {...}`和`x.value() `。`std::optonal`類型可以隱式的轉換成`bool`類型，並且使用解引用操作符的方式和普通指針差不多。

另一個方便輔助操作符就是對`optional`的`operator->`操作符進行重載。當有一個結構體`  struct Foo { int a; string b; }`類型，並且我們想要通過一個`optional<Foo>`來訪問其成員變量x，那麼就可以寫成`x->a`或`x->b`。當然，需要對x和b進行檢查，確定其是否有值。

當可選變量中沒有值時，我們還要對其進行訪問，其就會拋出一個`std::logic_error`異常。這樣，就可以對大量的可選值在不進行檢查的情況下進行使用。`try-catch`塊的代碼如下：

```c++
cout << "Please enter 3 numbers:\n";

try {
	cout << "Sum: "
		<< (*read_int() + *read_int() + *read_int())
		<< '\n';
} catch (const std::bad_optional_access &) {
	cout << "Unfortunately you did not enter 3 numbers\n";
}
```

`std::optional`具有一個有趣的`optional::value_or`操作。當我們想要在失敗的時候，可選變量包含一個默認值進行返回時，這個操作就很有用了。`x = optional_var.value_or(123) `就能將123作為可選變量失敗時的默認數值。