# GCP SSH 連線設定指南

完整的 Google Cloud Platform 虛擬機器 SSH 連線設定步驟：

## 1. 生成 SSH 金鑰
```bash
# 替換 your.email@gmail.com 為你的 Gmail
ssh-keygen -t rsa -b 2048 -C "your.email@gmail.com" -f ~/.ssh/myssh/gcp_new
```

```bash
gcp 帳號 chhi3758
ssh-keygen -t rsa -b 2048 -C "chhi3758" -f ~/.ssh/myssh/gcp_chhi3758
```

## 2. 設定 SSH 公鑰
```bash
# 查看公鑰
cat ~/.ssh/myssh/gcp_new.pub

# 格式應該要像：
ssh-rsa AAAAB3Nza... autoicash2023
# 注意：最後的使用者名稱要改成你的 GCP 登入帳號
```

## 3. GCP 主控臺設定
- 前往：Compute Engine > 中繼資料 > SSH 金鑰
- 點選「編輯」
- 貼上修改後的公鑰

## 4. SSH 金鑰權限設定
```bash
chmod 600 ~/.ssh/myssh/gcp_new
ssh-add ~/.ssh/myssh/gcp_new
```

## 5. SSH 連線測試
```bash
ssh -i ~/.ssh/myssh/gcp_new autoicash2023@35.185.159.162
```

## 6. 系統設定

### 語系設定
```bash
# 安裝語言包
sudo apt-get update
sudo apt-get install -y language-pack-zh-hant language-pack-zh-hans

# 設定 locales
sudo locale-gen zh_TW.UTF-8
sudo update-locale LANG=zh_TW.UTF-8 LC_ALL=zh_TW.UTF-8

# 編輯設定檔
sudo bash -c 'cat > /etc/default/locale << EOF
LANG=zh_TW.UTF-8
LANGUAGE=zh_TW:zh
LC_ALL=zh_TW.UTF-8
EOF'
```

### 時區設定
```bash
# 安裝需要的套件
sudo apt-get install -y util-linux ntpdate

# 設定臺北時區
sudo timedatectl set-timezone Asia/Taipei
# 或
sudo ln -sf /usr/share/zoneinfo/Asia/Taipei /etc/localtime

# 更新時間
sudo ntpdate time.stdtime.gov.tw

# 確認設定
date
timedatectl
```

## 7. 完成設定
```bash
exit
# 然後重新 SSH 連線
```

## 重要提醒
- 確保公鑰內的使用者名稱與 SSH 連線時使用的相同
- 每個指令執行後最好確認是否成功
- 如果遇到問題，可以查看系統日誌：`sudo tail -f /var/log/syslog`

