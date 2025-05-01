# GCP SSH 設定

好的，讓我整理完整的 GCP 新機器設定步驟：

1. 生成 SSH 金鑰：
```bash
# 替換 your.email@gmail.com 為你的 Gmail
ssh-keygen -t rsa -b 2048 -C "your.email@gmail.com" -f ~/.ssh/myssh/gcp_new
```

```bash
gcp 帳號 chhi3758
ssh-keygen -t rsa -b 2048 -C "chhi3758" -f ~/.ssh/myssh/gcp_chhi3758
```

2. 修改並複製公鑰：
```bash
# 查看公鑰
cat ~/.ssh/myssh/gcp_new.pub

# 格式應該要像：
ssh-rsa AAAAB3Nza... autoicash2023
# 注意：最後的使用者名稱要改成你的 GCP 登入帳號
```

3. 在 GCP 主控台設定：
- 前往：Compute Engine > 中繼資料 > SSH 金鑰
- 點選「編輯」
- 貼上修改後的公鑰

4. 設定 SSH 金鑰權限：
```bash
chmod 600 ~/.ssh/myssh/gcp_new
ssh-add ~/.ssh/myssh/gcp_new
```

5. SSH 連線：
```bash
ssh -i ~/.ssh/myssh/gcp_new autoicash2023@35.185.159.162
```

6. 設定語系：
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

7. 設定時區：
```bash
# 安裝需要的套件
sudo apt-get install -y util-linux ntpdate

# 設定台北時區
sudo timedatectl set-timezone Asia/Taipei
# 或
sudo ln -sf /usr/share/zoneinfo/Asia/Taipei /etc/localtime

# 更新時間
sudo ntpdate time.stdtime.gov.tw

# 確認設定
date
timedatectl
```

8. 重新登入以套用所有設定：
```bash
exit
# 然後重新 SSH 連線
```

重要提醒：
- 確保公鑰內的使用者名稱與 SSH 連線時使用的相同
- 每個指令執行後最好確認是否成功
- 如果遇到問題，可以查看系統日誌：`sudo tail -f /var/log/syslog`

需要我解釋任何部分嗎？
