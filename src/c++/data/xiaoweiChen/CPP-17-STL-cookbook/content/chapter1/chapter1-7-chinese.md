# 使用摺疊表達式實現輔助函數

自C++11起，加入了變長模板參數包，能讓函數結構任意數量的參數。有時，這些參數都組合成一個表達式，從中得出函數結果。C++17中使用摺疊表達式，可以讓這項任務變得更加簡單。

## How to do it...

首先，實現一個函數，用於將所有參數進行累加：

1. 聲明該函數：

   ```c++
   template <typename ... Ts>
   auto sum(Ts ... ts);
   ```

2. 那麼現在我們擁有一個參數包`ts`，並且函數必須將參數包展開，然後使用表達式進行求和。如果我們對這些參數進行某個操作(比如：加法)，那麼為了將這個操作應用於該參數包，就需要使用括號將表達式包圍：

   ```c++
   template<typename ... Ts>
   auto sum(Ts ... ts){
   	return (ts + ...);
   }
   ```

3. 現在我們可以調用這個函數：

   ```c++
   int the_sum {sum(1, 2, 3, 4, 5)}; // value: 15
   ```

4. 這個操作不僅對`int`類型起作用，我們能對任何支持加號的類型使用這個函數，比如`std::string`:

   ```c++
   std::string a{"Hello "};
   std::string b{"World"};

   std::cout << sum(a, b) << '\n'; // output: Hello World
   ```

## How it works...

這裡只是簡單的對參數集進行簡單的遞歸，然後應用二元操作符`+`將每個參數加在一起。這稱為摺疊操作。C++17中添加了**摺疊表達式**，其能用更少的代碼量，達到相同的結果。

其中有種稱為**一元摺疊**的表達式。C++17中的摺疊參數包支持如下二元操作符：`+` `-` ` *` `/` `%` `^` `&` `|` `=` `<` `>` `<<` `>>` `+=` `-= ` `*=` `/=` `%= ` `^=` `&=` `|=` `<<=` `>>=` `==` `!=` `<=` `>=` `&&` `||` `, ` `.*` `->*`。

這樣的話，在我們的例子中表達式`(ts+...)`和`(...+ts)`等價。不過，對於某些其他的例子，這就所有不同了——當`...`在操作符右側時，稱為有“右摺疊”；當`...`在操作符左側時，稱為”左摺疊“。

我們sum例子中，一元左摺疊的擴展表達式為`1+(2+(3+(4+5)))`，一元右摺疊的擴展表達式為`(((1+2)+3)+4)+5`。根據操作符的使用，我們就能看出差別。當用來進行整數相加，那麼就沒有區別。

## There's more...

如果在調用sum函數的時候沒有傳入參數，那麼可變參數包中就沒有可以被摺疊的參數。對於大多數操作來說，這將導致錯誤(對於一些例子來說，可能會是另外一種情況，我們後面就能看到)。這時我們就需要決定，這時一個錯誤，還是返回一個特定的值。如果是特定值，顯而易見應該是0。

如何返回一個特定值：

```c++
template <typenme ... Ts>
auto sume(Ts ... ts){
	return (ts + ... + 0);
}
```

`sum()`會返回0，`sum(1, 2, 3)`返回`(1+(2+(3+0)))`。這樣具有初始值的摺疊表達式稱為**二元摺疊**。

當我們寫成`(ts + ... + 0)`或`(0 + ... + ts)`時，不同的寫法就會讓二元摺疊表達式處於不同的位置(二元右摺疊或二元左摺疊)。下圖可能更有助於理解左右二元摺疊：

![](../../images/chapter1/1-7-1.png)

為了應對無參數傳入的情況，我們使用二元摺疊表達式，這裡標識元素這個概念很重要——本例中，將0加到其他數字上不會有任何改變，那麼0就一個標識元素。因為有這個屬性，對於加減操作來說，可以將0添加入任何一個摺疊表達式，當參數包中沒有任何參數時，我們將返回0。從數學的角度來看，這沒問題。但從工程的角度，我們需要根據我們需求，定義什麼是正確的。

同樣的原理也適用於乘法。這裡，標識元素為1：

```c++
template <typename ... Ts>
auto product(Ts ... ts){
	return (ts * ... * 1);
}
```

`product(2, 3)`的結果是6，`product()`的結果是1。

邏輯操作符`and(&&)`和`or(||)`具有內置的標識元素。`&&`操作符為true，`||`操作符為false。

對於逗號表達式來說，其標識元素為`void()`。

為了更好的理解這特性，讓我們可以使用這個特性來實現的輔助函數。

**匹配範圍內的單個元素**

如何告訴函數在一定範圍內，我們提供的可變參數至少包含一個值：

```c++
template <typename R, typename ... Ts>
auto matches(const R& range, Ts ... ts)
{
	return (std::count(std::begin(range), std::end(range), ts) + ...);
}
```

輔助函數中使用STL中的`std::count`函數。這個函數需要三個參數：前兩個參數定義了迭代器所要遍歷的範圍，第三個參數則用於與範圍內的元素進行比較。`std::count`函數會返回範圍內與第三個參數相同元素的個數。

在我們的摺疊表達式中，我們也會將開始和結束迭代器作為確定範圍的參數傳入`std::count`函數。不過，對於第三個參數，我們將會每次從參數包中放入一個不同參數。最後，函數會將結果相加返回給調用者。

可以這樣使用:

```c++
std::vector<int> v{1, 2, 3, 4, 5};

matches(v, 2, 5); // return 2
matches(v, 100, 200); // return 0
matches("abcdefg", 'x', 'y', 'z'); // return 0
matches("abcdefg", 'a', 'b', 'f'); // return 3
```

如我們所見，`matches`輔助函數十分靈活——可以直接傳入`vector`或`string`直接調用。其對於初始化列表也同樣適用，也適用於`std::list`，`std::array`，`std::set`等STL容器的實例。

**檢查集合中的多個插入操作是否成功**

我們完成了一個輔助函數，用於將任意數量參數插入`std::set`實例中，並且返回是否所有插入操作都成功完成：

```c++
template <typename T, typename ... Ts>
bool insert_all(T &set, Ts ... ts)
{
	return (set.insert(ts).second && ...);
}
```

那麼這個函數如何工作呢？`std::set`的`insert`成員函數聲明如下：

```c++
std::pair<iterator, bool> insert(const value_type& value);
```

手冊上所述，當我們使用`insert`函數插入一個元素時，該函數會使用一個包含一個迭代器和一個布爾值的組對作為返回值。當該操作成功，那麼迭代器指向的就是新元素在`set`實例中的位置。否則，迭代器指向某個已經存在的元素，這個元素與插入項有衝突。

我們的輔助函數在完成插入後，會訪問`.second`區域，這裡的布爾值反映了插入操作成功與否。如果所有插入操作都為true，那麼都是成功的。摺疊標識使用邏輯操作符`&&`鏈接所有插入結果的狀態，並且返回計算之後的結果。

可以這樣使用它：

```c++
std::set<int> my_set{1, 2, 3};

insert_all(my_set, 4, 5, 6); // Returns true
insert_all(my_set, 7, 8, 2); // Returns false, because the 2 collides
```

需要注意的是，當在插入3個元素時，第2個元素沒有插入成功，那麼`&&`會根據短路特性，終止插入剩餘元素：

```c++
std::set<int> my_set{1, 2, 3};

insert_all(my_set, 4, 2, 5); // Returns flase
// set contains {1, 2, 3, 4} now, without the 5!
```

**檢查所有參數是否在範圍內**

當要檢查多個變量是否在某個範圍內時，可以多次使用查找單個變量是否在某個範圍的方式。這裡我們可以使用摺疊表達式進行表示：

```c++
template <typename T, typename ... Ts>
bool within(T min, T max, Ts ...ts)
{
	return ((min <= ts && ts <= max) && ...);
}
```

表達式`(min <= ts && ts <= max) `將會告訴調用者參數包中的每一個元素是否在這個範圍內。我們使用`&&`操作符對每次的結果進行處理，從而返回最終的結果。

如何使用這個輔助函數：

```c++
within(10, 20, 1, 15, 30); // --> false
within(10, 20, 11, 12, 13); // --> true
within(5.0, 5.5, 5.1, 5.2, 5.3) // --> true
```

這個函數也是很靈活的，其只需要傳入的參數類型可以進行比較，且支持`<=`操作符即可。並且該規則對於`std::string`都是適用的：

```c++
std::string aaa {"aaa"};
std::string bcd {"bcd"};
std::string def {"def"};
std::string zzz {"zzz"};

within(aaa, zzz, bcd, def); // --> true
within(aaa, def, bcd, zzz); // --> false
```

**將多個元素推入vector中**

可以編寫一個輔助函數，不會減少任何結果，又能同時處理同一類的多個操作。比如向`std::vector`傳入元素:

```c++
template <typename T, typename ... Ts>
void insert_all(std::vector<T> &vec, Ts ... ts){
	(vec.push_back(ts), ...);
}

int main(){
	std::vector<int> v{1, 2, 3};
	insert_all(v, 4, 5, 6);
}
```

需要注意的是，使用了逗號操作符將參數包展開，然後推入vector中。該函數也不懼空參數包，因為逗號表達式具有隱式標識元素，`void()`可以翻譯為*什麼都沒做*。

