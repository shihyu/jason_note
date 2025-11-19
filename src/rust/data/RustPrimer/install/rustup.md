# Rust 版本管理工具: rustup

rustup 是rust官方的版本管理工具。應當作為安裝 Rust 的首選。

項目主頁是: <https://github.com/rust-lang-nursery/rustup.rs>

## Features

* 管理安裝多個官方版本的 Rust 二進製程序。
* 配置基於目錄的 Rust 工具鏈。
* 安裝和更新來自 Rust 的發佈通道: nightly, beta 和 stable。
* 接收來自發布通道更新的通知。
* 從官方安裝歷史版本的 nightly 工具鏈。
* 通過指定 stable 版本來安裝。
* 安裝額外的 std 用於交叉編譯。
* 安裝自定義的工具鏈。
* 獨立每個安裝的 Cargo metadata。
* 校驗下載的 hash 值。
* 校驗簽名 (如果 GPG 存在)。
* 斷點續傳。
* 只依賴 bash, curl 和常見 unix 工具。
* 支持 Linux, OS X, Windows(via MSYS2)。

## 安裝

### Windows

在[rustup的主頁](http://www.rustup.rs)下載並運行[rustup-init.exe](https://win.rustup.rs/),並按照提示選擇選項。

```
Welcome to Rust!

This will download and install the official compiler for the Rust programming
language, and its package manager, Cargo.

It will add the cargo, rustc, rustup and other commands to Cargo's bin
directory, located at:

  C:\Users\Liqueur Librazy\.cargo\bin

This path will then be added to your PATH environment variable by modifying the
HKEY_CURRENT_USER/Environment/PATH registry key.

You can uninstall at any time with rustup self uninstall and these changes will
be reverted.

Current installation options:

   default host triple: x86_64-pc-windows-msvc
     default toolchain: stable
  modify PATH variable: yes

1) Proceed with installation (default)
2) Customize installation
3) Cancel installation
```

三個選項分別是

1) 開始安裝（默認選項）
2) 自定義安裝
3) 取消

其中自定義安裝可以更改默認架構與工具鏈、是否添加 PATH。例如想要選擇 nightly 工具鏈可以進行以下自定義

```
I'm going to ask you the value of each these installation options.
You may simply press the Enter key to leave unchanged.

Default host triple?


Default toolchain? (stable/beta/nightly)
nightly

Modify PATH variable? (y/n)

```

設置完畢後，選擇 1 以開始安裝。

### Linux & macOS

運行以下命令

```
curl https://sh.rustup.rs -sSf | sh
```

這個命令將會編譯和安裝 rustup, 安裝過程中可能會提示你輸入 sudo 的密碼。 然後, 他會下載和安裝 stable 版本的工具鏈, 當執行 rustc, rustdoc 和 cargo 時, 將會配置他為默認工具鏈。

`Unix` 上安裝後工具鏈會被安裝到 `$HOME/.cargo/bin` 目錄。

`.cargo/bin` 目錄會被添加到系統的 `$PATH` 環境變量,重新登錄後即可使用 `rustc`，`cargo` 等命令。

## 卸載

```
rustup self uninstall
```

## 用法

安裝後會得到一個 rustup 命令, 多使用命令自帶的幫助提示, 可以快速定位你需要功能。

### 幫助

運行 ` rustup -h` 你將會得到如下提示:

```
❯ rustup -h
rustup 1.5.0 (92d0d1e9e 2017-06-24)
The Rust toolchain installer

USAGE:
    rustup.exe [FLAGS] [SUBCOMMAND]

FLAGS:
    -v, --verbose    Enable verbose output
    -h, --help       Prints help information
    -V, --version    Prints version information

SUBCOMMANDS:
    show           Show the active and installed toolchains
    update         Update Rust toolchains and rustup
    default        Set the default toolchain
    toolchain      Modify or query the installed toolchains
    target         Modify a toolchain's supported targets
    component      Modify a toolchain's installed components
    override       Modify directory toolchain overrides
    run            Run a command with an environment configured for a given toolchain
    which          Display which binary will be run for a given command
    doc            Open the documentation for the current toolchain
    self           Modify the rustup installation
    set            Alter rustup settings
    completions    Generate completion scripts for your shell
    help           Prints this message or the help of the given subcommand(s)

DISCUSSION:
    rustup installs The Rust Programming Language from the official
    release channels, enabling you to easily switch between stable,
    beta, and nightly compilers and keep them updated. It makes
    cross-compiling simpler with binary builds of the standard library
    for common platforms.

    If you are new to Rust consider running `rustup doc --book` to
    learn Rust.

```

根據提示, 使用 `rust help <command>` 來查看子命令的幫助。

`rustup doc --book` 會打開英文版的 [The Rust Programming Language](https://doc.rust-lang.org/book/)。

### 常用命令

`rustup default <toolchain>` 配置默認工具鏈。

`rustup show` 顯示當前安裝的工具鏈信息。

`rustup update` 檢查安裝更新。

`rustup toolchain [SUBCOMMAND]` 配置工具鏈

> * `rustup toolchain install <toolchain>` 安裝工具鏈。
> * `rustup toolchain uninstall <toolchain>` 卸載工具鏈。
> * `rustup toolchain link <toolchain-name> "<toolchain-path>"` 設置[自定義工具鏈](https://github.com/rust-lang-nursery/rustup.rs#working-with-custom-toolchains-and-local-builds)。
> 
> 其中標準的 `<toolchain>`具有如下的形式
> ```
> `<channel>[-<date>][-<host>]`
> <channel>       = stable|beta|nightly|<version>
> <date>          = YYYY-MM-DD
> <host>          = <target-triple>
> ```
> 如 `stable-x86_64-pc-windows-msvc` `nightly-2017-7-25` `1.18.0` 等都是合法的toolchain名稱。

`rustup override [SUBCOMMAND]` 配置一個目錄以及其子目錄的默認工具鏈

> 使用 `--path <path>` 指定目錄或在某個目錄下運行以下命令
> 
> * `rustup override set <toolchain>` 設置該目錄以及其子目錄的默認工具鏈。
> * `rustup override unset` 取消目錄以及其子目錄的默認工具鏈。
> 
> 使用 `rustup override list` 查看已設置的默認工具鏈。

`rustup target [SUBCOMMAND]` 配置工具鏈的可用目標

> * `rustup target add <target>` 安裝目標。
> * `rustup target remove <target>` 卸載目標。
> * `rustup target add --toolchain <toolchain> <target>` 為特定工具鏈安裝目標。

`rustup component` 配置 rustup 安裝的組件

> * `rustup component add <component>` 安裝組件
> * `rustup component remove <component>` 卸載組件
> * `rustup component list` 列出可用組件
>
> 常用組件：
> * Rust 源代碼 `rustup component add rust-src`
> * Rust Langular Server (RLS) `rustup component add rls`
