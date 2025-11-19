# DuckDNS 註冊與自動更新 IP 教學

## 🧾 步驟一：註冊帳號

1. 前往 [https://www.duckdns.org/](https://www.duckdns.org/)
2. 使用 **Google** 或 **GitHub** 其中一個帳號登入

---

## 🌐 步驟二：建立子網域

1. 登入後，在首頁輸入你想要的子網域名稱（例如：`gamegame`）
2. 點選 **add domain**，建立 `gamegame.duckdns.org`

---

## 🛠️ 步驟三：取得你的 Token

- 登入後首頁會顯示你的專屬 **Token**（例如：`xxxxxxxxxxxxxxxxxxxxxxxxx`）

---

## 🔄 步驟四：設定自動更新 IP

> 建議在家用伺服器或樹莓派上設定，讓 DDNS 持續更新 IP

### 1. 建立資料夾與更新指令

```bash
mkdir -p ~/duckdns
echo url="https://www.duckdns.org/update?domains=gamegame&token=xxxxxxxxxxxxxxxxxxxxxxxxx&ip=" | curl -k -o ~/duckdns/duck.log -K -
```

- `gamegame` 請換成你自己的子網域
- `token=` 後面換成你自己的 Token

---

### 2. 設定 crontab 每 5 分鐘自動更新

```bash
crontab -e
```

在打開的編輯器中加上以下一行：

```bash
*/5 * * * * echo url="https://www.duckdns.org/update?domains=gamegame&token=xxxxxxxxxxxxxxxxxxxxxxxxx&ip=" | curl -k -o ~/duckdns/duck.log -K -
```

> 儲存後即可每 5 分鐘更新一次 IP，讓你的子網域自動指向你目前的公網 IP。

---

## ✅ 測試確認

你可以在瀏覽器中打開：

```
https://www.duckdns.org/update?domains=gamegame&token=xxxxxxxxxxxxxxxxxxxxxxxxx&ip=
```

如果回傳 `OK` 表示成功！
