# tools

https://itsfoss.com/rust-cli-tools/

```sh
cargo install bottom procs zoxide du-dust exa tealdeer bat difftastic tokei hyperfine fd-find sshx --locked
```

```
curl -sS https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | bash

~/.bashrc
eval "$(zoxide init bash)"
```

- A very fast implementation of tldr in Rust: Simplified, example based and community-driven man pages.
```sh
tldr strace
```

- bat
```sh
alias cat="bat --theme=\$(defaults read -globalDomain AppleInterfaceStyle &> /dev/null && echo default || echo GitHub)"
```

- tig
```sh
https://github.com/jonas/tig
```

- pandoc 

```sh
pandoc -f markdown -t epub3 -o xxx.epub 1.md 2.md 3.m

最直覺的做法是每章自成一個 HTML 檔，作者原來也是這麼做。但起初 Pandoc 將所有 HTML 併成一個 ch001.xhtml (解壓 ePub 觀察到的)，研究發現是因為作者把章標題放在 <h2>，<h1> 放書名，


而 Pandoc 的分檔是以 <h1> 區隔；故我寫了一段 PowerShell 將 h1 移除，h2 改 h1。h3 改 h2，h4 改 h3，修改後 ePub 也修正為一章一個 .html


。但有個已知問題，Pandoc 產生的目錄連結在 Google 電子書閱讀器套件或 Calibre 閱讀時功能正常，點各層章節都能跳到對映位置，但在我的 Kobo Forma 閱讀器上只能跳到章 (.html 層)，無法跳到節 (.html#section-id)。
```

```sh
使用 ls -1 | cut -d " " -f 10- 命令來只列出檔案名稱，忽略 -rw-r--r-- 1 shihyu shihyu 8973 3月 13 20:06 這部分的檔案權限、所有者等詳細資訊，只顯示檔案名稱。 cut -d " " -f 10- 則是使用分割符號 " " （空格）分割每一行，選取第 10 個欄位到最後一個欄位，也就是檔案名稱。
```

- sed

```sh
find . -type f -name "*" -exec sed -i  "s/hello/fuck/g" {} \;
```

- 更新 git

```bash
#!/bin/bash

# Change to the directory containing the Git repositories
cd /path/to/directory

# Find all .git directories and run Git commands on each one
find . -name ".git" -type d -exec sh -c '
  cd "{}" && cd .. && 
  git stash && git pull
' \;
```

- xelatex

  - XeLaTeX 簡簡單單讓 LaTeX 說中文

  ```latex
  %!TEX encoding = UTF-8 Unicode
  \usepackage{xeCJK}
  %\setCJKmainfont{標楷體}
  %\setCJKmainfont{LiHei Pro}
  \setCJKmainfont{PingFang TC}
  ```
  

- 每個月底執行 command

```sh
0 0 28-31 * * [ "$(date +\%d -d tomorrow)" = "01" ] && command
```


- 解壓 zip

```sh
 find . -type f -name '*.zip' -exec unzip -d unzip {} \;
 ```
