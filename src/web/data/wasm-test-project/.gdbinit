# GDB 調試設定檔
set architecture wasm32
set confirm off
set pagination off
set print pretty on
set print array on
# WASM 特殊設定
set debug remote 0
# 自動載入除錯符號
set auto-load safe-path /
