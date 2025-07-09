# LiveKit 環境搭建步驟整理

## 1. 準備工作

### 環境要求
- Go 1.22+ 版本
- GOPATH/bin 在 PATH 環境變量中

## 2. 下載源碼
```bash
git clone https://github.com/livekit/livekit.git
cd livekit
```

## 3. 編譯方式

### 命令行編譯
```bash
# 進入源碼目錄
cd livekit

# 通過 mage 編譯
./bootstrap.sh
mage
```
編譯完成後，會在 `bin` 目錄下生成可執行程序 `livekit-server`

## 4. 安裝 LiveKit CLI

### 下載並安裝 CLI
```bash
git clone https://github.com/livekit/livekit-cli
cd livekit-cli
make install
```

## 5. 生成訪問秘鑰和 Token

### 生成 Token 命令
```bash
lk create-token \
--api-key 356APISejy567Mgg9X7wYzw \
--api-secret 2ll78HjY2MvB2yGSCueswesd28GnuhjGN4c02JuijhclQ \
--join --room my-first-room --identity user1 \
--valid-for 24h
```

### 注意事項
- API key 和 secret 可以自己隨便填寫
- 房間名 `my-first-room` 隨機填寫
- 用戶名 `user1`，建議生成兩個用戶（user1 和 user2）以便測試

### 生成結果示例
```
valid for (mins): 1440
Token grants:
{
  "roomJoin": true,
  "room": "my-first-room"
}
Access token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 6. 啟動 LiveKit Server

### 啟動命令
```bash
./bin/livekit-server --keys "356APISejy567Mgg9X7wYzw: 2ll78HjY2MvB2yGSCueswesd28GnuhjGN4c02JuijhclQ"
```

**注意：** key 和 secret 之間有一個空格

## 7. 測試連接

### 方式一：使用 lk 命令加入房間
```bash
lk room join --identity user1 \
--api-key "356APISejy567Mgg9X7wYzw" \
--api-secret "2ll78HjY2MvB2yGSCueswesd28GnuhjGN4c02JuijhclQ" \
--publish-demo my-first-room
```

### 方式二：通過 Web 界面測試
1. 打開網址：https://meet.livekit.io/?tab=custom
2. 輸入之前生成的 access token
3. 連接成功後即可打開本地攝像頭
4. 兩個用戶（user1 和 user2）都執行相同操作，分別填入各自的 access token

## 8. 測試效果
- 同一房間內的兩個用戶可以互相看到視頻
- 支持本地攝像頭開啟
- 可以進行實時視頻通話

## 總結
LiveKit 是一個功能強大的開源 WebRTC 服務器，支持房間管理、Redis、信令業務、流媒體 SFU 等功能。通過以上步驟可以快速搭建開發環境並進行測試。
