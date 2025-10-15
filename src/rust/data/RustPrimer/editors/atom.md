# Atom
本文是rust的Atom編輯器配置。
橫向對比一下，不得不說，Atom無論在易用性還是界面上都比前輩們要好的很多，對於Rust的配置，也是基本上可以做到開箱即用。
雖然本文獨佔一小節，但是其實能寫的東西也就了了。

- [自行配置](#自行配置)
- [使用tokamak](#tokamak)

## 自行配置

## 準備工作

首先，你需要一個可執行的rustc編譯器，一個cargo程序，一個已經編譯好的racer程序和一份已經解壓好的rust源碼。
我們假定你已經將這三個程序安裝完畢，並且能夠自由的從命令行裡調用他們。

另外，本文不講解如何安裝Atom，需要新安裝的同學請自行前往[項目主頁](https://github.com/atom/atom)安裝。

ps:無論是windows用戶還是*nix用戶都需要將以上三個程序加入你的PATH(Windows下叫Path)環境變量裡。

## 需要安裝的插件包

打開Atom，按Ctrl+Shift+p，搜索preference，打開Atom的配置中心，選擇install選項卡。

依次安裝`rust-api-docs-helper`/`racer`/`language-rust`/`linter-rust`/`linter`。

這裡要單獨說的一個就是linter，這是一個基礎的lint組件包，atom的很多以linter為前綴的包都會依賴這個包，但是Atom並不會為我們自動的安裝，因此需要我們自己去安裝。

## 一點配置

以上，我們安裝好了幾個組件包，但是不要著急去打開一個Rust文件。你可能還需要一點點的配置。這裡，我們在配置中心裡打開`Packages`選項卡，在`Installed Packages`裡搜索racer，並點擊其`Setting`。

這裡需要將racer的可執行文件的絕對路徑填入`Path to the Racer executable`裡。同時，我們還需要將rust源碼文件夾下的src目錄加入到`Path to the Rust source code directory`裡。

## 完成安裝

好了，就是這麼簡單。你現在可以打開任意一個rust文件就會發現源碼高亮已經默認打開了，編輯一下，racer也能自動補全，*如果不能*，嘗試一下用`F3`鍵來顯式地呼出racer的補全。

## tokamak

[tokamak](https://github.com/vertexclique/tokamak) 是一個使 atom 搖身一變為 rust IDE 的 atom 插件. 安裝後 atom 即具有語法高亮, 代碼補全與 Lint 等功能, 而且還有個不錯的界面, 看起來確實像個 IDE. 你可以在 atom 中搜索 tokamak 並安裝它.
