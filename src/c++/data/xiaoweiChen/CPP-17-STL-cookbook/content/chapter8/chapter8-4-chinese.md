# 對元組使用函數

C++11中，STL添加了`std::tuple`，這種類型可以用來將多個不同類型的值捆綁在一起。元組這種類型已經存在與很多編程語言中，本書的一些章節已經在使用這種類型，這種類型的用途很廣泛。

不過，我們有時會將一些值捆綁在一個元組中，然後我們需要調用函數來獲取其中每一個元素。對於元素的解包的代碼看起來非常的冗長(並且易於出錯)。其冗長的方式類似這樣：`func(get<0>(tup), get<1>(tup), get<2>(tup), ...);`。

本節中，你將瞭解如何使用一種優雅地方式對元組進行打包和解包。調用函數時，你無需對元組特別地瞭解。

## How to do it...

我們將實現一個程序，其能對元組值進行打包和解包。然後，我們將看到在不瞭解元組中元素的情況下，如何使用元組：

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <iomanip>
   #include <tuple>
   #include <functional>
   #include <string>
   #include <list>
   
   using namespace std;
   ```

2. 首先定義一個函數，這個函數能接受多個參數，其描述的是一個學生，並將學生的相關信息進行打印。其和C風格的函數看起來差不多：

   ```c++
   static void print_student(size_t id, const string &name, double gpa)
   {
       cout << "Student " << quoted(name)
           << ", ID: " << id
           << ", GPA: " << gpa << '\n';
   }
   ```

3. 主函數中，將對一種元組類型進行別名，然後將具體學生的信息填入到這種類型的實例中：

   ```c++
   int main()
   {
       using student = tuple<size_t, string, double>;
       student john {123, "John Doe"s, 3.7};
   ```

4. 為了打印這種類型的實例，我們將會對元組中的元素進行分解，然後調用`print_student`函數將這些值分別進行打印：

   ```c++
   	{
           const auto &[id, name, gpa] = john;
           print_student(id, name, gpa);
       }
       cout << "-----\n";
   ```

5. 然後，我們來創建一個以元組為基礎類型的多個學生：

   ```c++
       auto arguments_for_later = {
           make_tuple(234, "John Doe"s, 3.7),
           make_tuple(345, "Billy Foo"s, 4.0),
           make_tuple(456, "Cathy Bar"s, 3.5),
       };
   ```

6. 這裡，我們依舊可以通過對元素進行分解，然後對其進行打印。當要寫這樣的代碼時，我們需要在函數接口變化時，對代碼進行重構：

   ```c++
       for (const auto &[id, name, gpa] : arguments_for_later) {
      		print_student(id, name, gpa);
       }
       cout << "-----\n";
   ```

7. 當然可以做的更好，我們無需知道`print_student`的參數的個數，或學生元組中元素的個數，我們使用`std::apply`對直接將元組應用於函數。這個函數能夠接受一個函數指針或一個函數對象和一個元組，然後會將元組進行解包，然後與函數參數進行對應，並傳入函數：

   ```c++
   	apply(print_student, john);
   	cout << "-----\n";
   ```

8. 循環中可以這樣用：

   ```c++
       for (const auto &args : arguments_for_later) {
       	apply(print_student, args);
       }
       cout << "-----\n";
   }
   ```

9. 編譯並運行程序，我們就能得到如下的輸出：

   ```c++
   $ ./apply_functions_on_tuples
   Student "John Doe", ID: 123, GPA: 3.7
   -----
   Student "John Doe", ID: 234, GPA: 3.7
   Student "Billy Foo", ID: 345, GPA: 4
   Student "Cathy Bar", ID: 456, GPA: 3.5
   -----
   Student "John Doe", ID: 123, GPA: 3.7
   -----
   Student "John Doe", ID: 234, GPA: 3.7
   Student "Billy Foo", ID: 345, GPA: 4
   Student "Cathy Bar", ID: 456, GPA: 3.5
   -----
   ```

## How it works...

`std::apply`是一個編譯時輔助函數，可以幫助我們處理不確定的類型參數。

試想，我們有一個元組`t`，其有元素`(123, "abc"s, 456.0)`。那麼這個元組的類型為` tuple<int, string, double>`。另外，有一個函數`f`的簽名為`int f(int, string, double)`(參數類型也可以為引用)。

然後，我們就可以這樣調用函數`x = apply(f, t)`，其和`x = f(123, "abc"s, 456.0)`等價。`apply`方法還是會返回`f`的返回值。

