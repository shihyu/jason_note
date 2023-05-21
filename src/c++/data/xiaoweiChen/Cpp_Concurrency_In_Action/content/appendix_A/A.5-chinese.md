# A.5 Lambda函數

lambda函數在`C++`11中的加入很是令人興奮，因為lambda函數能夠大大簡化代碼複雜度(語法糖：利於理解具體的功能)，避免實現調用對象。`C++`11的lambda函數語法允許在需要使用的時候進行定義。能為等待函數，例如`std::condition_variable`(如同4.1.1節中的例子)提供很好謂詞函數，其語義可以用來快速的表示可訪問的變量，而非使用類中函數來對成員變量進行捕獲。

最簡單的情況下，lambda表達式就一個自給自足的函數，不需要傳入函數僅依賴管局變量和函數，甚至都可以不用返回一個值。這樣的lambda表達式的一系列語義都需要封閉在括號中，還要以方括號作為前綴：

```
[]{  // lambda表達式以[]開始
  do_stuff();
  do_more_stuff();
}();  // 表達式結束，可以直接調用
```

例子中，lambda表達式通過後面的括號調用，不過這種方式不常用。一方面，如果想要直接調用，可以在寫完對應的語句後，就對函數進行調用。對於函數模板，傳遞一個參數進去時很常見的事情，甚至可以將可調用對象作為其參數傳入；可調用對象通常也需要一些參數，或返回一個值，亦或兩者都有。如果想給lambda函數傳遞參數，可以參考下面的lambda函數，其使用起來就像是一個普通函數。例如，下面代碼是將vector中的元素使用`std::cout`進行打印：

```
std::vector<int> data=make_data();
std::for_each(data.begin(),data.end(),[](int i){std::cout<<i<<"\n";});
```

返回值也是很簡單的，當lambda函數體包括一個return語句，返回值的類型就作為lambda表達式的返回類型。例如，使用一個簡單的lambda函數來等待`std::condition_variable`(見4.1.1節)中的標誌被設置。

清單A.4 lambda函數推導返回類型

```
std::condition_variable cond;
bool data_ready;
std::mutex m;
void wait_for_data()
{
  std::unique_lock<std::mutex> lk(m);
  cond.wait(lk,[]{return data_ready;});  // 1
}
```

lambda的返回值傳遞給cond.wait()①，函數就能推斷出data_ready的類型是bool。當條件變量從等待中甦醒後，上鎖階段會調用lambda函數，並且當data_ready為true時，僅返回到wait()中。

當lambda函數體中有多個return語句，就需要顯式的指定返回類型。只有一個返回語句的時候，也可以這樣做，不過這樣可能會讓你的lambda函數體看起來更復雜。返回類型可以使用跟在參數列表後面的箭頭(->)進行設置。如果lambda函數沒有任何參數，還需要包含(空)的參數列表，這樣做是為了能顯式的對返回類型進行指定。對條件變量的預測可以寫成下面這種方式：

```
cond.wait(lk,[]()->bool{return data_ready;});
```

還可以對lambda函數進行擴展，比如：加上log信息的打印，或做更加複雜的操作：

```
cond.wait(lk,[]()->bool{
  if(data_ready)
  {
    std::cout<<”Data ready”<<std::endl;
    return true;
  }
  else
  {
    std::cout<<”Data not ready, resuming wait”<<std::endl;
    return false;
  }
});
```

雖然簡單的lambda函數很強大，能簡化代碼，不過其真正的強大的地方在於對本地變量的捕獲。

## A.5.1 引用本地變量的Lambda函數

lambda函數使用空的`[]`(lambda introducer)就不能引用當前範圍內的本地變量；其只能使用全局變量，或將其他值以參數的形式進行傳遞。當想要訪問一個本地變量，需要對其進行捕獲。最簡單的方式就是將範圍內的所有本地變量都進行捕獲，使用`[=]`就可以完成這樣的功能。函數被創建的時候，就能對本地變量的副本進行訪問了。

實踐一下，看一下下面的例子：

```
std::function<int(int)> make_offseter(int offset)
{
  return [=](int j){return offset+j;};
}
```

當調用make_offseter時，就會通過`std::function<>`函數包裝返回一個新的lambda函數體。

這個帶有返回的函數添加了對參數的偏移功能。例如：

```
int main()
{
  std::function<int(int)> offset_42=make_offseter(42);
  std::function<int(int)> offset_123=make_offseter(123);
  std::cout<<offset_42(12)<<”,“<<offset_123(12)<<std::endl;
  std::cout<<offset_42(12)<<”,“<<offset_123(12)<<std::endl;
}
```

屏幕上將打印出54,135兩次，因為第一次從make_offseter中返回，都是對參數加42的；第二次調用後，make_offseter會對參數加上123。所以，會打印兩次相同的值。

這種本地變量捕獲的方式相當安全，所有的東西都進行了拷貝，所以可以通過lambda函數對錶達式的值進行返回，並且可在原始函數之外的地方對其進行調用。這也不是唯一的選擇，也可以通過選擇通過引用的方式捕獲本地變量。在本地變量被銷燬的時候，lambda函數會出現未定義的行為。

下面的例子，就介紹一下怎麼使用`[&]`對所有本地變量進行引用：

```
int main()
{
  int offset=42;  // 1
  std::function<int(int)> offset_a=[&](int j){return offset+j;};  // 2
  offset=123;  // 3
  std::function<int(int)> offset_b=[&](int j){return offset+j;};  // 4
  std::cout<<offset_a(12)<<”,”<<offset_b(12)<<std::endl;  // 5
  offset=99;  // 6
  std::cout<<offset_a(12)<<”,”<<offset_b(12)<<std::endl;  // 7
}
```

之前的例子中，使用`[=]`來對要偏移的變量進行拷貝，offset_a函數就是個使用`[&]`捕獲offset的引用的例子②。所以，offset初始化成42也沒什麼關係①；offset_a(12)的例子通常會依賴與當前offset的值。在③上，offset的值會變為123，offset_b④函數將會使用到這個值，同樣第二個函數也是使用引用的方式。

現在，第一行打印信息⑤，offset為123，所以輸出為135,135。不過，第二行打印信息⑦就有所不同，offset變成99⑥，所以輸出為111,111。offset_a和offset_b都對當前值進行了加12的操作。

塵歸塵，土歸土，`C++`還是`C++`；這些選項不會讓你感覺到特別困惑，你可以選擇以引用或拷貝的方式對變量進行捕獲，並且你還可以通過調整中括號中的表達式，來對特定的變量進行顯式捕獲。如果想要拷貝所有變量，而非一兩個，可以使用`[=]`，通過參考中括號中的符號，對變量進行捕獲。下面的例子將會打印出1239，因為i是拷貝進lambda函數中的，而j和k是通過引用的方式進行捕獲的：

```
int main()
{
  int i=1234,j=5678,k=9;
  std::function<int()> f=[=,&j,&k]{return i+j+k;};
  i=1;
  j=2;
  k=3;
  std::cout<<f()<<std::endl;
}
```

或者，也可以通過默認引用方式對一些變量做引用，而對一些特別的變量進行拷貝。這種情況下，就要使用`[&]`與拷貝符號相結合的方式對列表中的變量進行拷貝捕獲。下面的例子將打印出5688，因為i通過引用捕獲，但j和k
通過拷貝捕獲：

```
int main()
{
  int i=1234,j=5678,k=9;
  std::function<int()> f=[&,j,k]{return i+j+k;};
  i=1;
  j=2;
  k=3;
  std::cout<<f()<<std::endl;
}
```

如果你只想捕獲某些變量，那麼你可以忽略=或&，僅使用變量名進行捕獲就行；加上&前綴，是將對應變量以引用的方式進行捕獲，而非拷貝的方式。下面的例子將打印出5682，因為i和k是通過引用的範式獲取的，而j是通過拷貝的方式：

```
int main()
{
  int i=1234,j=5678,k=9;
  std::function<int()> f=[&i,j,&k]{return i+j+k;};
  i=1;
  j=2;
  k=3;
  std::cout<<f()<<std::endl;
}
```

最後一種方式，是為了確保預期的變量能被捕獲，在捕獲列表中引用任何不存在的變量都會引起編譯錯誤。當選擇這種方式，就要小心類成員的訪問方式，確定類中是否包含一個lambda函數的成員變量。類成員變量不能直接捕獲，如果想通過lambda方式訪問類中的成員，需要在捕獲列表中添加this指針，以便捕獲。下面的例子中，lambda捕獲this後，就能訪問到some_data類中的成員：

```
struct X
{
  int some_data;
  void foo(std::vector<int>& vec)
  {
    std::for_each(vec.begin(),vec.end(),
         [this](int& i){i+=some_data;});
  }
};
```

併發的上下文中，lambda是很有用的，其可以作為謂詞放在`std::condition_variable::wait()`(見4.1.1節)和`std::packaged_task<>`(見4.2.1節)中；或是用在線程池中，對小任務進行打包。也可以線程函數的方式`std::thread`的構造函數(見2.1.1)，以及作為一個並行算法實現，在parallel_for_each()(見8.5.1節)中使用。
