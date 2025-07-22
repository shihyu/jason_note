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
