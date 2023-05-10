# 使用 Git LFS 上傳大型檔案

https://ithelp.ithome.com.tw/articles/10229654



專案開發過程中，檔案越來越大在所難免，GitHub 限制單一檔案 100 MB 的限制，這時候就需要交由 **LFS** 這個功能，來解決類似以下的錯誤訊息。

```bash
remote: warning: Large files detected.
remote: error: File large_file is 123.00 MB; this exceeds GitHub's file size limit of 100 MB
```

## 安裝 Git LFS

### 安裝命令

- Linux

  依序輸入以下指令

```bash
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
sudo apt-get install git-lfs
git lfs install
```

- MacOS

  依序輸入以下指令，如果不能執行 `brew` 相關指令，參考 [這裡](https://brew.sh/index_zh-tw) 安裝 HomeBrew 。

```bash
brew install git-lfs
git lfs install
```

- Windows

  下載安裝 [Git Large File Storage (LFS)](https://git-lfs.github.com/)

執行安裝檔，安裝完畢後，回到專案終端機，輸入

```bash
git lfs install
```

## 將檔案交由 LFS 管理

`*` 表示所有檔案， `.psd` 表示副檔名為 .psd 的檔案，所以 lfs 會管理所有副檔名為 .psd 的檔案，若有多個附檔名要管理，請一一執行命令，或參考 [這裡](https://www.jianshu.com/p/64e3137cbc22) 的第四點。

```bash
git lfs track "*.psd"
```

## 接著 Push 專案

LFS 管理大型檔案後，繼續執行 `git add` `git commit` `git push` 命令即可。