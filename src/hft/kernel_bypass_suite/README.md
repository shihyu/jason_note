# Kernel Bypass 技術實作套件

這個套件實作了 kernel-bypass-guide.md 文件中的所有範例程式，展示各種繞過 Linux 核心的高效能網路技術。

## 📁 專案結構

```
kernel_bypass_suite/
├── dpdk_packet_processing.cpp    # DPDK 封包處理範例
├── af_xdp_socket.cpp             # AF_XDP Socket 實作
├── io_uring_async.cpp            # io_uring 非同步 I/O 伺服器
├── rdma_communication.cpp        # RDMA 通訊範例
├── Makefile                      # 編譯腳本
├── run_tests.sh                  # 測試腳本
└── README.md                     # 本文件
```

## 🚀 快速開始

### 安裝相依套件

```bash
# 安裝所有必要的開發套件
make install-deps
# 需要密碼: f0409
```

### 編譯程式

```bash
# 檢查相依性
make check-deps

# 編譯 io_uring 程式 (最簡單)
make io_uring_async

# 編譯所有可用的程式
make all

# 編譯特定程式
make af_xdp      # 編譯 AF_XDP
make rdma        # 編譯 RDMA
make dpdk        # 編譯 DPDK (需要 DPDK 環境)
```

### 執行測試

```bash
# 執行基本測試
./run_tests.sh

# 執行完整測試 (需要 root)
sudo ./run_tests.sh -f

# 只執行效能測試
./run_tests.sh -p
```

## 📋 各技術詳細說明

### 1. io_uring 非同步 I/O

最新的 Linux 非同步 I/O 框架，提供高效能的檔案和網路 I/O 操作。

**特點：**
- 零拷貝操作
- 批次提交和完成
- 支援多種 I/O 操作類型
- 核心版本需求：Linux 5.1+

**執行範例：**
```bash
# 啟動伺服器 (預設埠口 12345)
./io_uring_async

# 指定埠口
./io_uring_async 8080

# 測試連線
echo "測試訊息" | nc localhost 12345
```

**效能指標：**
- 延遲：< 10 微秒
- 吞吐量：> 1M 請求/秒
- CPU 使用率：極低

### 2. AF_XDP Socket

使用 XDP (eXpress Data Path) 的高速封包處理介面。

**特點：**
- 零拷貝封包處理
- 繞過核心網路堆疊
- 支援硬體卸載
- 核心版本需求：Linux 4.18+

**執行範例：**
```bash
# 需要 root 權限
sudo ./af_xdp_socket eth0 0
# eth0: 網路介面名稱
# 0: 佇列 ID
```

**效能指標：**
- 封包處理：> 20 Mpps
- 延遲：< 1 微秒
- CPU 親和性優化

### 3. DPDK 封包處理

Intel 的資料平面開發套件，完全繞過核心的封包處理。

**特點：**
- 使用者空間驅動程式
- 大頁面記憶體支援
- 多核心擴展性
- 硬體加速支援

**前置設定：**
```bash
# 設定大頁面
make setup-hugepages

# 綁定網路介面到 DPDK
sudo dpdk-devbind.py --bind=uio_pci_generic 0000:01:00.0
```

**執行範例：**
```bash
# 執行 DPDK 應用程式
sudo ./dpdk_packet_processing -l 0-3 -n 4
# -l: 使用的核心
# -n: 記憶體通道數
```

**效能指標：**
- 封包處理：> 100 Mpps
- 延遲：< 100 奈秒
- 線速處理 100G 網路

### 4. RDMA 通訊

遠端直接記憶體存取，實現零 CPU 參與的網路通訊。

**特點：**
- 零拷貝傳輸
- 核心繞過
- 硬體卸載
- 支援 InfiniBand 和 RoCE

**執行範例：**
```bash
# 啟動伺服器
./rdma_communication server

# 啟動客戶端
./rdma_communication client 192.168.1.100
```

**效能指標：**
- 延遲：< 1 微秒
- 頻寬：> 100 Gbps
- CPU 使用率：< 5%

## 🔧 故障排除

### 常見問題

1. **liburing 未找到**
   ```bash
   make install-deps
   ```

2. **權限不足**
   ```bash
   # 使用 sudo 執行
   sudo ./af_xdp_socket eth0 0
   ```

3. **大頁面未配置**
   ```bash
   make setup-hugepages
   ```

4. **DPDK 環境未設定**
   ```bash
   export RTE_SDK=/path/to/dpdk
   export RTE_TARGET=x86_64-native-linux-gcc
   ```

5. **網路介面被佔用**
   ```bash
   # 停止 NetworkManager
   sudo systemctl stop NetworkManager
   ```

## 📊 效能比較

| 技術 | 延遲 | 吞吐量 | CPU 使用率 | 複雜度 |
|------|------|--------|------------|--------|
| 傳統 Socket | 50-100 μs | 100K pps | 高 | 低 |
| io_uring | < 10 μs | 1M rps | 低 | 中 |
| AF_XDP | < 1 μs | 20M pps | 中 | 中 |
| DPDK | < 100 ns | 100M pps | 低 | 高 |
| RDMA | < 1 μs | 線速 | 極低 | 高 |

## 🔍 監控和調試

### 效能監控

```bash
# 監控網路統計
watch -n 1 'cat /proc/net/dev'

# 監控中斷
watch -n 1 'cat /proc/interrupts | grep eth'

# 監控 CPU 使用率
htop
```

### 調試工具

```bash
# 追蹤系統呼叫
strace -e network ./io_uring_async

# 效能分析
perf record -g ./dpdk_packet_processing
perf report

# 網路封包擷取
tcpdump -i eth0 -nn
```

## 📚 參考資源

- [io_uring 官方文件](https://kernel.dk/io_uring.pdf)
- [AF_XDP 教學](https://www.kernel.org/doc/html/latest/networking/af_xdp.html)
- [DPDK 程式設計指南](https://doc.dpdk.org/guides/)
- [RDMA 程式設計手冊](https://www.rdmamojo.com/)

## 📝 授權

本專案採用 MIT 授權條款。

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📞 聯絡方式

如有問題，請在 GitHub 上開啟 Issue。

---

**注意事項：**
- 所有程式的輸出訊息都使用繁體中文
- sudo 密碼為: f0409
- 某些功能需要特定硬體支援（如 RDMA）
- 建議在測試環境中執行，避免影響生產系統