# 代碼說明

只要有合適的編譯器，就可以編譯並運行所有示例源碼。這裡要說明一下，只有在必要時，我才在源文件中使用`using namespace std`。

## 運行程序

編譯和運行本書中C++11和C++14的例子並不難。任何支持新標準的C++編譯器都可以編譯這些例子。[GCC]( https://gcc.gnu.org/) 和[clang]( https://clang.llvm.org/) 編譯器，必須指定C++標準，以及要鏈接的線程庫。 例如，GCC的g++編譯器使用以下命令行創建一個名為thread的可執行程序:

> g++ -std=c++14 -pthread thread.cpp -o thread.

* -std=c++14: 使用C++14標準。
* -pthread: 使用pthread庫作為後端，對多線程進行支持。
* thread.cpp: 源碼文件。
*  -o thread: 可執行程序名。

同樣的命令行也適用於clang++編譯器。Microsoft Visual Studio 17 C++編譯器也支持C++ 14。

如果沒有合適的C++編譯器使用，那麼可以使用在線編譯器。比如：Arne Mertz博客提供的[C++ Online Compiler](https://arne-mertz.de/2017/05/online-compilers)。

C++ 17和C++ 20/23的故事比較複雜。我安裝了[HPX (High Performance ParalleX)](http://stellar.cct.lsu.edu/projects/hpx/)框架，這是個C++通用運行時系統，適用於任何規模的並行和分佈式應用。HPX已經實現了C++ 17並行的STL和C++ 20/23的許多併發特性。可參考“未來：C++ 20/23”一章中相應的內容和代碼。

