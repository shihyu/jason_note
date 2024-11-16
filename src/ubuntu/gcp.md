# GCP SSH 設定

1. 首先生成 SSH 金鑰：
```bash
# 替換 your.email@gmail.com 為你的 Gmail
ssh-keygen -t rsa -b 2048 -C "your.email@gmail.com" -f ~/.ssh/myssh/gcp_new
```

2. 查看並複製公鑰內容：
```bash
cat ~/.ssh/myssh/gcp_new.pub
```

3. 修改公鑰格式：
- 原本格式可能是：
  ```
  ssh-rsa AAAAB3Nza... user@hostname
  ```
- 需要改成：
  ```
  ssh-rsa AAAAB3Nza... autoicash2023
  ```
  (把最後的 user@hostname 改成你要用來登入 VM 的使用者名稱)

4. 在 GCP 主控台設定：
- 前往：Compute Engine > 中繼資料 > SSH 金鑰
- 點選「編輯」
- 貼上修改後的公鑰內容

5. 測試連線：
```bash
# 使用私鑰連線
ssh -i ~/.ssh/myssh/gcp_new autoicash2023@35.185.159.162
```

重要提醒：
- 金鑰最後的使用者名稱必須和你 SSH 連線時使用的使用者名稱相同
- 確保私鑰權限為 600：`chmod 600 ~/.ssh/myssh/gcp_new`
- 公鑰內容必須是單行，不能有換行符號

需要我解釋哪個部分嗎？
