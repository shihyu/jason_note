# 使用 eBPF 替換任意程序讀取或寫入的文本

完整源代碼：<https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/27-replace> 

關於如何安裝依賴，請參考：<https://eunomia.dev/tutorials/11-bootstrap/>

編譯：

```bash
make
```

使用方式：

```sh
sudo ./replace --filename /path/to/file --input foo --replace bar
```

這個程序將文件中所有與 `input` 匹配的文本替換為 `replace` 文本。
這有很多用途，例如：

隱藏內核模塊 `joydev`，避免被如 `lsmod` 這樣的工具發現：

```bash
./replace -f /proc/modules -i 'joydev' -r 'cryptd'
```

偽造 `eth0` 接口的 MAC 地址：

```bash
./replace -f /sys/class/net/eth0/address -i '00:15:5d:01:ca:05' -r '00:00:00:00:00:00'
```

惡意軟件進行反沙箱檢查可能會檢查 MAC 地址，尋找是否正在虛擬機或沙箱內運行，而不是在“真實”的機器上運行的跡象。

**注意：** `input` 和 `replace` 的長度必須相同，以避免在文本塊的中間添加 NULL 字符。在 bash 提示符下輸入換行符，使用 `$'\n'`，例如 `--replace $'text\n'`。

## 參考資料

- <https://github.com/pathtofile/bad-bpf>
