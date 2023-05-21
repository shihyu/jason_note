# A.2 刪除函數

有時讓類去做拷貝是沒有意義的。`std::mutex`就是一個例子——拷貝一個互斥量，意義何在？`std::unique_lock<>`是另一個例子——一個實例只能擁有一個鎖。如果要複製，拷貝的那個實例也能獲取相同的鎖，這樣`std::unique_lock<>`就沒有存在的意義了。實例中轉移所有權(A.1.2節)是有意義的，其並不是使用的拷貝。

為了避免拷貝操作，會將拷貝構造函數和拷貝賦值操作符聲明為私有成員，並且不進行實現。如果對實例進行拷貝，將會引起編譯錯誤。如果有其他成員函數或友元函數想要拷貝一個實例，將會引起鏈接錯誤(因為缺少實現)：

```c++
class no_copies
{
public:
  no_copies(){}
private:
  no_copies(no_copies const&);  // 無實現
  no_copies& operator=(no_copies const&);  // 無實現
};

no_copies a;
no_copies b(a);  // 編譯錯誤
```

C++11中，委員會意識到這種情況。因此，委員會提供了更多的通用機制：可以通過添加`= delete`將一個函數聲明為刪除函數。

no_copise類就可以寫為：

```c++
class no_copies
{
public:
  no_copies(){}
  no_copies(no_copies const&) = delete;
  no_copies& operator=(no_copies const&) = delete;
};
```

這樣的描述要比之前的代碼更加清晰。也允許編譯器提供更多的錯誤信息描述，當成員函數想要執行拷貝操作的時候，可將鏈接錯誤轉移到編譯時。

拷貝構造和拷貝賦值操作刪除後，需要顯式寫一個移動構造函數和移動賦值操作符，與`std::thread`和`std::unique_lock<>`一樣，類是隻移動的。

下面代碼中的例子，就展示了一個只移動的類。

代碼A.2 只移動類

```c++
class move_only
{
  std::unique_ptr<my_class> data;
public:
  move_only(const move_only&) = delete;
  move_only(move_only&& other):
    data(std::move(other.data))
  {}
  move_only& operator=(const move_only&) = delete;
  move_only& operator=(move_only&& other)
  {
    data=std::move(other.data);
    return *this;
  }
};

move_only m1;
move_only m2(m1);  // 錯誤，拷貝構造聲明為“已刪除”
move_only m3(std::move(m1));  // OK，找到移動構造函數
```

只移動對象可以作為函數的參數進行傳遞，並且從函數中返回，不過當想要移動左值，通常需要顯式的使用`std::move()`或`static_cast<T&&>`。

可以為任意函數添加`= delete`說明符，添加後就說明這些函數不能使用。當然，還可以用於很多的地方。刪除函數可以以正常的方式參與重載解析，並且如果使用，就會引起編譯錯誤，這種方式可以用來刪除特定的重載。比如，當函數以short作為參數，為了避免擴展為int類型，可以寫出重載函數(以int為參數)的聲明，然後添加刪除說明符：

```c++
void foo(short);
void foo(int) = delete;
```

現在，任何向foo函數傳遞int類型參數都會產生一個編譯錯誤，不過調用者可以顯式的將其他類型轉化為short：

```c++
foo(42);  // 錯誤，int重載聲明已經刪除
foo((short)42);  // OK
```

