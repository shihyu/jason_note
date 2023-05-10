```sh
find . -type f -size +10M  ! -name '*.cpp' ! -name '*.c' ! -name '*.rs' ! -name '*.java'
```



```sh
find . -not -path '*/\.git/*' -not -path '*readme*' -type f    ! -name '*.cpp' ! -name '*.c' ! -name '*.rs' ! -name '*.java' ! -name '*.go' ! -name '*.cc' ! -name '*.h' ! -name '*.kt' ! -name '*.py'  ! -name '*.sh'  ! -name '*.asm' ! -name '*.pl' ! -name '*.sed'  ! -name '*.hpp'  ! -name '*.cxx' ! -name '*makefile*'  ! -name '*.json' -exec rm {} \;
```



- https://github.com/dutchcoders/transfer.sh

```sh
transfer(){ if [ $# -eq 0 ];then echo "No arguments specified.\nUsage:\n transfer <file|directory>\n ... | transfer <file_name>">&2;return 1;fi;if tty -s;then file="$1";file_name=$(basename "$file");if [ ! -e "$file" ];then echo "$file: No such file or directory">&2;return 1;fi;if [ -d "$file" ];then file_name="$file_name.zip" ,;(cd "$file"&&zip -r -q - .)|curl --progress-bar --upload-file "-" "https://transfer.sh/$file_name"|tee /dev/null,;else cat "$file"|curl --progress-bar --upload-file "-" "https://transfer.sh/$file_name"|tee /dev/null;fi;else file_name=$1;curl --progress-bar --upload-file "-" "https://transfer.sh/$file_name"|tee /dev/null;fi;}
```

```sh
# Upload using cURL
$ curl --upload-file ./hello.txt https://transfer.sh/hello.txt https://transfer.sh/wPbvjO/hello.txt

# Using the shell function
$ transfer hello.txt
##################################################### 100.0% https://transfer.sh/zmlFh3/hello.txt

# Upload from web
Drag your files here, or click to browse.
```


```sh
find . -type f -not -path '*/\.git/*' -size +1M
```
