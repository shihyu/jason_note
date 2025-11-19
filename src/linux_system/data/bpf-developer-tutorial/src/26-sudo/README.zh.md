# 使用 eBPF 添加 sudo 用戶

本文完整的源代碼：<https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/26-sudo>

關於如何安裝依賴，請參考：<https://eunomia.dev/tutorials/11-bootstrap/>

編譯：

```bash
make
```

使用方式：

```sh
sudo ./sudoadd --username lowpriv-user
```

這個程序允許一個通常權限較低的用戶使用 `sudo` 成為 root。

它通過攔截 `sudo` 讀取 `/etc/sudoers` 文件，並將第一行覆蓋為 `<username> ALL=(ALL:ALL) NOPASSWD:ALL #` 的方式工作。這欺騙了 sudo，使其認為用戶被允許成為 root。其他程序如 `cat` 或 `sudoedit` 不受影響，所以對於這些程序來說，文件未改變，用戶並沒有這些權限。行尾的 `#` 確保行的其餘部分被當作註釋處理，因此不會破壞文件的邏輯。

## 參考資料

- <https://github.com/pathtofile/bad-bpf>
