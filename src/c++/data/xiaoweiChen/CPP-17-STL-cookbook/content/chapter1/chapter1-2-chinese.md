# 將變量作用域限制在if和switch區域內

將變量的生命週期儘可能的限制在指定區域內，是一種非常好的代碼風格。有時我們需要在滿足某些條件時獲得某個值，然後對這個值進行操作。

為了讓這個過程更簡單，C++17中為if和switch配備了初始化區域。

## How to do it...

這個案例中，我們使用初始化語句，來瞭解下其使用方式：

- `if`：假設我們要在一個字母表中查找一個字母，我們`std::map`的成員`find`完成這個操作：

```c++
if (auto itr (character_map.find(c)); itr != character_map.end()) {
  // *itr is valid. Do something with it.
} else {
  // itr is the end-iterator. Don't dereference.
}
// itr is not available here at all
```

- `switch`：這個例子看起來像是從玩家輸入的字母決定某個遊戲中的行為。通過使用`switch`查找字母相對應的操作：

```c++
switch (char c (getchar()); c) {
  case 'a': move_left(); break;
  case 's': move_back(); break;
  case 'w': move_fwd(); break;
  case 'd': move_right(); break;
  case 'q': quit_game(); break;
  case '0'...'9': select_tool('0' - c); break;
  default:
    std::cout << "invalid input: " << c << '\n';
}
```

## How it works...

帶有初始化的`if`和`switch`相當於語法糖一樣。

```c++
// if: before C++17
{
    auto var(init_value);
    if (condition){
        // branch A. var is accessible
    } else {
        // branch B. var is accessible
    }
    // var is still accessible
}
```

```c++
// if: since C++17
if (auto var (init_value); condition){
    // branch A. var is accessible
} else {
    // branch B. var is accessible
}
// var is not accessible any longer
```

```c++
// switch: before C++17
{
    auto var (init_value);
    switch (var) {
      case 1: ...
      case 2: ...
      ...
    }
    // var is still accessible
}
```

```c++
// switch: since C++17
switch(auto var (init_value); var){
    case 1: ...
    case 2: ...
    ...
}
// var is not accessible any longer
```

這些有用的特性保證了代碼的簡潔性。C++17之前只能使用外部括號將代碼包圍，就像上面的例子中展示的那樣。減短變量的生命週期，能幫助我們保持代碼的整潔性，並且更加易於重構。

## There's more...

另一個有趣的例子是臨界區限定變量生命週期。

先來看個栗子：

```c++
if (std::lock_guard<std::mutex> lg {my_mutex}; some_condition) {
  // Do something
}
```

首先，創建一個`std::lock_guard`。這個類接收一個互斥量和作為其構造函數的參數。這個類在其構造函數中對互斥量上鎖，之後當代碼運行完這段區域後，其會在析構函數中對互斥量進行解鎖。這種方式避免了忘記解鎖互斥量而導致的錯誤。C++17之前，為了確定解鎖的範圍，需要一對額外的括號對。

另一個例子中對弱指針進行區域限制：

```c++
if (auto shared_pointer (weak_pointer.lock()); shared_pointer != nullptr) {
  // Yes, the shared object does still exist
} else {
  // shared_pointer var is accessible, but a null pointer
}
// shared_pointer is not accessible any longer
```

這個例子中有一個臨時的`shared_pointer`變量，雖然`if`條件塊或外部括號會讓其保持一個無用的狀態，但是這個變量確實會“洩漏”到當前範圍內。

當要使用傳統API的輸出參數時，`if`初始化段就很有用：

```c++
if (DWORD exit_code; GetExitCodeProcess(process_handle, &exit_code)) {
  std::cout << "Exit code of process was: " << exit_code << '\n';
}
// No useless exit_code variable outside the if-conditional
```

`GetExitCodeProcess`函數是Windows操作系統的內核API函數。其通過返回碼來判斷給定的進程是否合法的處理完成。當離開條件域，變量就沒用了，也就可以銷燬這個變量了。

具有初始化段的`if`代碼塊在很多情況下都特別有用，尤其是在使用傳統API的輸出參數進行初始化時。

> Note:
>
> 使用帶有初始化段的`if`和`switch`能保證代碼的緊湊性。這使您的代碼緊湊，更易於閱讀，在重構過程中，會更容易改動。



