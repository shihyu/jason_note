# VS Code 安裝配置

[VS Code](https://code.visualstudio.com/) 是微軟出的一款開源代碼編輯器，秉承了微軟在IDE領域的一慣優秀基因，是一款潛力相當大的編輯器/IDE。

VScode 目前也對 Rust 也有良好的支持。



## 下載 VScode

請打開官網 https://code.visualstudio.com/ 下載編輯器。

## 依賴

如本章第一節所述，準備好 `racer`，`rust 源代碼`，`rustfmt`，`rls` 這四樣東西，並且配置好相應的環境變量，此不贅述。

## 安裝 Rust 擴展 Rust

1. 打開 VScode 編輯器；
2. 按 Ctrl + p 打開命令面板；
3. 在編輯器中上部浮現出的輸入框中，輸入 `ext install vscode-rust`，會自動搜索可用的插件，搜索出來後，點擊進行安裝；
4. 使用`VScode`打開任意一個`.rs`文件，插件首次啟動會自動引導用戶完成配置。

注:推薦使用RLS模式，即使用[Rust Langular Server](https://github.com/rust-lang-nursery/rls)提供各項功能支持
