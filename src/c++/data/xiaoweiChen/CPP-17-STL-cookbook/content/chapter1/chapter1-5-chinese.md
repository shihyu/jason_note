# 使用constexpr-if簡化編譯

模板化編程中，通常要以不同的方式做某些事情，比如特化模板類型。C++17帶了`constexpr-if`表達式，可以在很多情況下簡化代碼。

## How to do it...

本節中，我們會實現一個很小的輔助模板類。它能處理不同模板類型的特化，因為它可以在完全不同的代碼中，選取相應的片段，依據這些片段的類型對模板進行特化：

1. 完成代碼中的通用部分。在我們的例子中，它是一個簡單的類，它的成員函數`add`，支持對`U`類型值與`T`類型值的加法:

   ```c++
   template <typename T>
   class addable
   {
     T val;
   public:
     addable(T v) : val{v} {}
     template <typename U>
     T add(U x) const {
       return val + x;
     }
   };
   ```

2. 假設類型`T`是`std::vector<something>`，而類型`U`是`int`。這裡就有問題了，為整個`vector`添加整數是為了什麼呢？其應該是對`vector`中的每個元素加上一個整型數。實現這個功能就需要在循環中進行：

   ```c++
   template <typename U>
   T add(U x)
   {
     auto copy (val); // Get a copy of the vector member
     for (auto &n : copy) {
       n += x;
     }
     return copy;
   }
   ```

3. 下一步也是最後一步，將兩種方式結合在一起。如果`T`類型是一個`vector`，其每個元素都是`U`類型，擇進行循環。如果不是，則進行普通的加法：

   ```c++
   template <typename U>
   T add(U x) const{
       if constexpr(std::is_same<T, std::vector<U>>::value){
           auto copy(val);
           for (auto &n : copy){
               n += x;
           }
           return copy;
       } else {
           return val + x;
       }
   }
   ```

4. 現在就可以使用這個類了。讓我們來看下其對不同類型處理的是多麼完美，下面的例子中有`int`,` float`, `std::vector<int>`和`std::vector<string>`:

   ```c++
   addable<int> {1}.add(2); // is 3
   addable<float> {1.f}.add(2); // is 3.0
   addable<std::string> {"aa"}.add("bb"); // is "aabb"

   std::vector<int> v{1, 2, 3};
   addable<std::vector<int>> {v}.add(10); // is std::vector<int> {11, 12, 13}

   std::vector<std::string> sv{"a", "b", "c"};
   addable<std::vector<std::string>> {sv}.add(std::string{"z"}); // is {"az", "bz", "cz"}
   ```


## How it works...

新特性`constexpr-if`的工作機制與傳統的`if-else`類似。不同點就在於前者在編譯時進行判斷，後者在運行時進行判斷。所以，使用`constexpr-if`的代碼在編譯完成後，程序的這一部分其實就不會有分支存在。有種方式類似於`constexpr-if`，那就是`#if-#else`的預編譯方式進行宏替換，不過這種方式在代碼的構成方面不是那麼優雅。組成`constexpr-if`的所有分支結構都是優雅地，沒有使用分支在語義上不要求合法。

為了區分是向`vector`的每個元素加上x，還是普通加法，我們使用`std::is_same`來進行判斷。表達式`std::is_same<A, B>::value`會返回一個布爾值，當A和B為同樣類型時，返回true，反之返回false。我們的例子中就寫為`std::is_same<T, std::vector<U>>::value()`(`is_same_v = is_same<T, U>::value;`)，當返回為true時，且用戶指定的T為`std::vector<X>`，之後試圖調用add，其參數類型`U = X`。

當然，在一個`constexpr-if-else`代碼塊中，可以有多個條件(注意：a和b也可以依賴於模板參數，並不需要其為編譯時常量)：

```c++
if constexpr(a){
    // do something
} else if constexpr(b){
    // do something else
} else {
    // do something completely different
}
```

C++17中，很多元編程的情況更容易表達和閱讀。

## There's more...

這裡對比一下C++17之前的實現和添加`constexpr-if`後的實現，從而體現出這個特性的加入會給C++帶來多大的提升：

```c++
template <typename T>
class addable{
    T val;
public:
    addable(T v):val{v}{}
    
    template <typename U>
    std::enable_if_t<!std::is_same<T, std::vector<U>>::value, T> 
    add(U x) const {
        return val + x;
    }
    
    template <typename U>
    std::enable_if_t<!std::is_same<T, std::vector<U>>::value, std::vector<U>>
    add (U x) const{
        auto copy(val);
        for (auto &n: copy){
            n += x;
        }
        return copy;
    }
};
```

在沒有了`constexpr-if`的幫助下，這個類看起特別複雜，不像我們所期望的那樣。怎麼使用這個類呢？

簡單來看，這裡重載實現了兩個完全不同的`add`函數。其返回值的類型聲明，讓這兩個函數看起裡很複雜；這裡有一個簡化的技巧——表達式，例如`std::enable_if_t<condition, type>`，如果條件為真，那麼就為`type`類型，反之`std::enable_if_t`表達式不會做任何事。這通常被認為是一個錯誤，不過我們能解釋為什麼什麼都沒做。

對於第二個`add`函數，相同的判斷條件，但是為反向。這樣，在兩個實現不能同時為真。

當編譯器看到具有相同名稱的不同模板函數並不得不選擇其中一個時，一個重要的原則就起作用了：替換失敗不是錯誤([SFINAE](http://zh.cppreference.com/w/cpp/language/sfinae), **Substitution Failure is not An  Error**)。這個例子中，就意味著如果函數的返回值來源一個錯誤的模板表示，無法推斷得出，這時編譯器不會將這種情況視為錯誤(和`std::enable_if`中的條件為false時的狀態一樣)。這樣編譯器就會去找函數的另外的實現。

很麻煩是吧，C++17中實現起來就變得簡單多了。