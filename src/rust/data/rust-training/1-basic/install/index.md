Rust 的安裝非常簡單，只需要下載並安裝 Rust 的官方編譯器即可。

```sh
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```
安裝過程根據網絡情況可能需要一點時間。如果一次不成功，可以換個時間再重試。

安裝完成後，開啟個新控制檯即可使用。如果想在當前控制檯使用，需要將 Rust 的命令行工具添加到環境變量中。
```sh
source $HOME/.cargo/env
```

如果想更新到最新版本，可以使用以下命令：

```sh
rustup update
```

安裝完成後，可以使用以下命令測試是否安裝成功：

```sh
rustc
```