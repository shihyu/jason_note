# Burn MNIST 訓練與推論範例
本專案展示如何使用 Rust 的 Burn 框架來構建、訓練並推論一個手寫數字辨識模型。
## ⚠️ 書籍勘誤 (Errata)
在書中執行推論的範例指令中，發生了排版印刷錯誤，少了一個關鍵的空格。
### 書中錯誤寫法：
```bash
# 錯誤：黏在一起會被誤認為是一個名為 --train 的參數
$ cargo run --train
```
由於 `cargo` 不認識 `--train` 這個參數，這行指令會導致錯誤。
`infer` 也是同理。
### 正確執行方式：
請在 `--` 與 `train` 之間加上一個 **空格**。
```bash
# 正確：-- 是分隔符號，train 是傳給程式的子指令
$ cargo run --release -- train
```
> **指令解析**：
> * `cargo run --release`：叫 Cargo 以 Release 模式編譯並執行。
> * `--`：這是「分隔符號」，告訴 Cargo：「後面的東西不是給你的，是給我寫的程式的」。
> * `train`：這才是我們 `main.rs` 真正接收到的字串（程式碼中 `match command` 的部分）。
---
## 快速指令列表
**1. 訓練模型 (Train):**
```bash
$ cargo run --release -- train
```
**2. 進行推論 (Infer):**
```bash
$ cargo run --release -- infer
```