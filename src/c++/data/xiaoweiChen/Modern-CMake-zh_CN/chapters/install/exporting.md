# 導出

{% hint style='danger' %}

CMake 3.15 中，導出的默認行為發生了變化。由於更改用戶主目錄中的文件是“令人驚訝的”（確實如此，這就是本章存在的原因），因此不再是默認行為。若將 CMake 的最小或最大版本設置為 3.15+，這種情況將不再發生，除非將 `CMAKE_EXPORT_PACKAGE_REGISTRY` 設置為`ON`。

{% endhint %}

CMake 訪問項目有三種方式：子目錄、導出構建目錄和安裝。要使用項目的構建目錄，就需要導出目標。正確的安裝需要導出目標，使用構建目錄只需要再增加了兩行代碼，但這並不是我推薦的工作方式。不過，對於開發和安裝過程來說的確好用。

還需要創建導出集，可能要放在主 `CMakeLists.txt` 文件的末尾:

```cmake
export(TARGETS MyLib1 MyLib2 NAMESPACE MyLib:: FILE MyLibTargets.cmake)
```

這將把列出的目標放到構建目錄的文件中，還可以給添加一個命名空間作為前綴。現在，CMake 可以找到這個包了，並將這個包導出到 `$HOME/.cmake/packages` 文件夾下:

```cmake
set(CMAKE_EXPORT_PACKAGE_REGISTRY ON)
export(PACKAGE MyLib)
```

現在，`find_package(MyLib)`就可以找到構建文件夾了。來看看生成的`MyLibTargets.cmake`文件到底做了什麼。它只是一個普通的CMake文件，但帶有導出的目標。

注意，這種方式有一個缺點：若導入了依賴項，則需要在 `find_package` 之前導入它們。這個問題將在後面的章節中解決。
