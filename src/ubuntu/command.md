# 常用指令

## 檔案管理

### 查找大檔案
```sh
find . -type f -size +10M  ! -name '*.cpp' ! -name '*.c' ! -name '*.rs' ! -name '*.java'
```

### 清理非代碼檔案
```sh
find . -not -path '*/\.git/*' -not -path '*readme*' -type f    ! -name '*.cpp' ! -name '*.c' ! -name '*.rs' ! -name '*.java' ! -name '*.go' ! -name '*.cc' ! -name '*.h' ! -name '*.kt' ! -name '*.py'  ! -name '*.sh'  ! -name '*.asm' ! -name '*.pl' ! -name '*.sed'  ! -name '*.hpp'  ! -name '*.cxx' ! -name '*makefile*'  ! -name '*.json' -exec rm {} \;
```

### 查找超過 1MB 的檔案
```sh
find . -type f -not -path '*/\.git/*' -size +1M
```

## 檔案傳輸工具

### Transfer.sh
使用 [transfer.sh](https://github.com/dutchcoders/transfer.sh) 快速分享檔案

#### 安裝 transfer 函數
```sh
transfer(){ 
    if [ $# -eq 0 ];then 
        echo "No arguments specified.\nUsage:\n transfer <file|directory>\n ... | transfer <file_name>">&2
        return 1
    fi
    if tty -s;then 
        file="$1"
        file_name=$(basename "$file")
        if [ ! -e "$file" ];then 
            echo "$file: No such file or directory">&2
            return 1
        fi
        if [ -d "$file" ];then 
            file_name="$file_name.zip"
            (cd "$file"&&zip -r -q - .)|curl --progress-bar --upload-file "-" "https://transfer.sh/$file_name"|tee /dev/null
        else 
            cat "$file"|curl --progress-bar --upload-file "-" "https://transfer.sh/$file_name"|tee /dev/null
        fi
    else 
        file_name=$1
        curl --progress-bar --upload-file "-" "https://transfer.sh/$file_name"|tee /dev/null
    fi
}
```

#### 使用範例
```sh
# 使用 cURL 直接上傳
curl --upload-file ./hello.txt https://transfer.sh/hello.txt

# 使用 transfer 函數
transfer hello.txt
# 輸出: ##################################################### 100.0% https://transfer.sh/zmlFh3/hello.txt

# 網頁上傳
# 將檔案拖拽到 transfer.sh 網站或點擊選擇檔案
```

以下是將 `ccusage` CLI 工具的使用說明整理成 Markdown 格式的內容，方便閱讀或加入到文件中：

---

# `ccusage` 使用說明

## 安裝

```bash
npm install -g ccusage
```

---

## 📊 基本用法

| 指令                | 說明                 |
| ----------------- | ------------------ |
| `ccusage`         | 顯示每日報告（預設）         |
| `ccusage daily`   | 顯示每日 Token 使用量與費用  |
| `ccusage monthly` | 顯示每月彙總報告           |
| `ccusage session` | 依對話 Session 顯示使用情況 |
| `ccusage blocks`  | 顯示每 5 小時的計費區間報告    |

---

## 📺 即時監控

```bash
ccusage blocks --live
```

顯示即時的使用儀表板。

---

## 🧰 過濾與選項

| 指令                   | 說明          |
| -------------------- | ----------- |
| `--since <YYYYMMDD>` | 從指定日期起查詢    |
| `--until <YYYYMMDD>` | 查詢到指定日期止    |
| `--json`             | 以 JSON 格式輸出 |
| `--breakdown`        | 顯示各模型詳細費用明細 |

範例：

```bash
ccusage daily --since 20250525 --until 20250530
ccusage daily --json
ccusage daily --breakdown
```

---

## 📁 專案分析

| 指令                                    | 說明        |
| ------------------------------------- | --------- |
| `--instances`                         | 依實例分組顯示   |
| `--project <name>`                    | 篩選指定專案    |
| `--instances --project <name> --json` | 結合篩選與格式輸出 |

範例：

```bash
ccusage daily --instances
ccusage daily --project myproject
ccusage daily --instances --project myproject --json
```

---

需要我幫你加入範例畫面或轉成 GitHub README 模板嗎？

