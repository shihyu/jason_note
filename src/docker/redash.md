## Redash 入門

出處:https://zhuanlan.zhihu.com/p/444590189

- 下載程式碼

```bash
git clone https://github.com/getredash/redash.git
cd redash/
git checkout v10.1.0
```

- 啟動docker服務

在docker-compose.yml 的同級目錄，新建檔案 .env，內容如下：

```python3
REDASH_SECRET_KEY=隨機字串1
REDASH_COOKIE_SECRET=隨機字串2
GOOGLE_CLIENT_ID=隨機字串3
```

不要把這個檔案提交到git中。然後在命令列輸入：

```bash
docker-compose up -d
```

- 安裝node packages

```text
npm install -g yarn
```

- 建立資料庫

```text
# 建表
docker-compose -f docker-compose.yml run --rm redash create_db

# 建測試資料
docker-compose run --rm postgres psql -h postgres -U postgres -c "create database tests"
```

- 然後訪問[http://127.0.0.1:5000/](https://link.zhihu.com/?target=http%3A//127.0.0.1%3A5000/)就可以打開頁面了。

![img](https://pic3.zhimg.com/80/v2-c24bc51dc72343e6cab27df2a2bbeec2_720w.webp)

- 常見問題

- - 使用`docker-compose up -d`啟動時遇到`Error response from daemon: OCI runtime create failed: container_linux.go:367: starting container process caused: exec: "/app/bin/docker-entrypoint": permission denied: unknown`。

解決：修改宿主機上的檔案權限：

```text
 sudo chmod 755 /bin/docker-entrypoint
 sudo chmod 755 manager.py
```

- `yarn --frozen-lockfile` 時出現node版本不滿足。

使用nvm 管理node版本。nvm 簡單使用方法如下：

```text
nvm list
nvm install 12.0.0
nvm use 12.0.0
node -v 
nvm uninstall 12.0.0
```

- 前端報錯：`Ineffective mark-compacts near heap limit Allocation failed - JavaScript heap out of memory` 。

在執行相關命令但shell中執行如下命令

```
export NODE_OPTIONS="--max-old-space-size=8192"
```

增加記憶體：如8192，16384這樣。

- 個人感受

程式碼比較清晰明瞭，但是每次生成可視化圖表都要徒手寫query，和[superset](https://link.zhihu.com/?target=https%3A//superset.apache.org/)相比工作量太大。如果習慣於點點滑鼠就生成chart，我還是推薦superset，包括二次開發，儘管superset的code有些疊床架屋的感覺。