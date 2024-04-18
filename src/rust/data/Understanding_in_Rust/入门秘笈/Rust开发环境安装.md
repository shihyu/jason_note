# Rust開發環境安裝

在學習Rust之前。首先，需要安裝Rust，通過 `rustup`

## Windows上Rust安裝

在Windows上，開啟連結 按照所有說明操作後，將安裝Rust並顯示螢幕：`rustup-init.exe`

![img](https://tw511.com/upload/images/201910/20191014013900370.png)



接著回車 -

![img](https://tw511.com/upload/images/201910/20191014013900371.png)



然後開始下載並安裝Rust 環境。

安裝後，Rust的PATH變數會自動新增到系統PATH中。開啟命令提示字元然後執行以下命令：

```shell
$ rustc --version
```

執行此命令後，應該看到版本號，提交的雜湊值和提交日期。如果看到類似的結果，則表示Rust已成功安裝。

結果如下所示 -

```
C:\Users\hema>rustc --version
rustc 1.30.0 (da5f414c2 2018-10-24)
```

> 注意：使用C++工具安裝visual studio是執行rust程式的必要條件。

## Linux或macOS中的Rust安裝

如果使用的是Linux或macOS，請開啟終端然後使用以下命令：

```shell
$ curl https://sh.rustup.rs -sSf | sh
```

上面的命令下載指令碼並開始安裝Rust工具，它將安裝最新版本的Rust。如果安裝成功完成，則會顯示以下訊息：

```shell
Rust is installed now. Great!
```

下次登入後，此安裝會自動將Rust新增到系統路徑中。如果要立即執行Rust而不重新啟動終端，請執行以下命令到`shell`

```shell
$ source $HOME/.cargo/env
```

安裝後，需要一個連結器。當嘗試執行Rust程式時，將收到連結器無法執行的錯誤。這意味著系統中未安裝連結器。C編譯器總是提出正確的編譯器。安裝C編譯器。另外，一些Rust包依賴於C程式碼，需要一個C編譯器。

## 更新和解除安裝

**更新：執行以下命令以更新到最新版本：**

```shell
$ rustup update
```

**解除安裝：**

```shell
$ rustup self uninstall
```
