# asciinema 把終端操作錄製成 gif 動畫

[asciinema](https://asciinema.org/) 是一個開源工具，可以把終端上的操作錄制下來轉換成 git 動畫，也可以進一步使用 ffmpeg 將動畫圖片轉換成 mp4 視頻。

## 安裝

macOS

```shell
brew install asciinema
```

Shell

Ubuntu/Debian

```shell
sudo apt install asciinema
```

Shell

## 使用

### 錄制

```shell
asciinema rec demo.cast
```

Shell

使用 ctrl + d 或 `exit` 停止錄制

### 回放

```shell
asciinema play demo.cast
```

Shell

### 生成 gif 動畫

按照 asciinema 項目的使用建議，錄制好的配置文件可以上傳到官網，然後使用官方的腳本和連接嵌入到自己的網頁。如果需要離線使用，可以通過 asciinema2gif 生成動圖。

[asciinema2gif](https://github.com/asciinema/asciicast2gif) 基於 nodejs 開發，配合 Docker 更簡單。

#### 拉取鏡像

```shell
docker pull asciinema/asciicast2gif
```

Shell

#### 製作 gif

```shell
docker run --rm -v $PWD:/data asciinema/asciicast2gif demo.cast demo.gif
```

Shell

注意 `-v $PWD:/data` 即宿主機與容器映射存儲的設置，$PWD 代表當前目錄，要確保 `demo.cast` 文件在當前路徑中。

#### 轉換成 mp4

可以使用 ffmpeg 進一步將 gif 動圖轉換成 mp4 視頻：

```shell
ffmpeg -i demo.gif demo.mp4
```