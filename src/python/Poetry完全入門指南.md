# 再見了 pip！最佳 Python 套件管理器——Poetry 完全入門指南



前陣子工作上的專案從原先的 pip 改用 Poetry 管理 Python 套件，由於採用 Poetry 正是我的提議，所以必須身先士卒，研究 Poetry 使用上的重點與學習成本，並評估是否真有所值——講白了就是至少要利大於弊，不然會徒增團隊適應上的負擔。

拜這個機會所賜，我對 Poetry 總算有了一個較為全面的理解。

習慣以後，現在我所有的個人開發也都改用 Poetry 來管理套件及虛擬環境，對於 Poetry 這個略嫌複雜的工具（相比於 pip），上手的同時我也感受到它確實存在一些學習門檻，間接促使了本文的誕生。

有鑑於 Poetry 真的有點複雜，如果要推薦別人使用，我想還是有必要好好介紹一下。



本文除了講解如何使用 Poetry，還會先不厭其煩地闡述它所解決的痛點，若興趣不大，可以直接跳到「[從零開始使用 Poetry](https://blog.kyomind.tw/python-poetry/#從零開始使用-Poetry)」章節，但看完前導部分，相信能更加體會 Poetry 的必要性。

為了讓你無痛上手！這將會是一篇超過 8000 字的長文，還請多多擔待。🙏

### 主要目錄

供快速跳轉（桌面版用戶可和右下角的「回到最上方」搭配使用）：

- [Poetry 是什麼？](https://blog.kyomind.tw/python-poetry/#Poetry-是什麼？)
- [名詞解釋：虛擬環境管理、套件管理、相依性管理](https://blog.kyomind.tw/python-poetry/#名詞解釋：虛擬環境管理、套件管理、相依性管理)
- [pip 的最大不足](https://blog.kyomind.tw/python-poetry/#pip-的最大不足)
- [pip 替代方案選擇](https://blog.kyomind.tw/python-poetry/#pip-替代方案選擇)
- [從零開始使用 Poetry](https://blog.kyomind.tw/python-poetry/#從零開始使用-Poetry)
- [安裝 Poetry](https://blog.kyomind.tw/python-poetry/#安裝-Poetry)
- [初始化 Poetry 專案](https://blog.kyomind.tw/python-poetry/#初始化-Poetry-專案)
- [管理 Poetry 虛擬環境](https://blog.kyomind.tw/python-poetry/#管理-Poetry-虛擬環境)
- [Poetry 常用指令](https://blog.kyomind.tw/python-poetry/#Poetry-常用指令)
- [Poetry 常見使用情境與操作 QA](https://blog.kyomind.tw/python-poetry/#Poetry-常見使用情境與操作-QA)
- [結語](https://blog.kyomind.tw/python-poetry/#結語)

## Poetry 是什麼？

比起 [Poetry GitHub](https://github.com/python-poetry/poetry#poetry-dependency-management-for-python) 的說明：

> **Poetry: Dependency Management for Python**
> Poetry helps you declare, manage and install dependencies of Python projects, ensuring you have the right stack everywhere.

我覺得 [Poetry 官網](https://python-poetry.org/)的 slogan 更加簡潔有力：

![](images/qTTgg0U.png)

簡單來說，**Poetry 類似 pip，能協助你進行套件管理**（dependency management），**但又比 pip 強大得多**，因為它還包含了 pip 所未有的功能：

- 虛擬環境管理
- 套件相依性管理
- 套件的打包與發布

其中**最為關鍵**的是「**套件的相依性管理**」，也是本文的重點，而「套件的打包與發布」與本文主題較無關係，所以不會提及。

## 名詞解釋：虛擬環境管理、套件管理、相依性管理

開始前，要先大致說明標題中這三者的區別，才不易混淆文中的內容。這裡的定義可能不盡準確，但至少對理解文中的表達能有所幫助。

### 虛擬環境管理

指的是使用內建的 venv 或 vituralenv 套件來建立及管理 Python 的虛擬環境，不同的虛擬環境間各自獨立，講白了就是指向的路徑各不相同。

### 套件管理、依賴管理（dependency management）

指的是使用 pip 這類的套件管理器來管理 Python 環境（未必是虛擬環境），即管理環境中所安裝的全部套件（package、dependency）及其版本。

在這個語境下，dependency 基本上就是指安裝的 package。

### 「套件的」相依性管理、依賴解析

這個有點難定義，它並不是一個非常通俗且有共識的名詞，我在英文中也還難找到對應的名詞。本文使用它時，主要指的是**套件與套件之間的依賴關係及版本衝突管理**，也就是套件的「**相依性管理**」。在下文提及的 Podcast 中，又稱為「**依賴解析**」。

所謂套件的「版本衝突」指的是單一套件被兩個以上的套件所依賴，但不同的套件對依賴的套件有著不同的**最低或最高版本要求**，若兩者的要求沒有「交集」，則會產生衝突而導致套件失效或無法安裝。

## pip 的最大不足

大概在 2 年前就知道了 Poetry 的存在，不過那時我還沒有套件相依性管理的強烈需求，加上看起來需要一些學習成本（確實如此），所以就一直擱在一旁，直到真正體會到了 pip 的不足。

pip 是 Python 內建的套件管理工具，而它的最大罩門，就是對於「套件間的相依性管理」能力不足。尤其是在「移除」套件時的依賴解析——可以說基本沒有。這也是我提議改用 Poetry 的根本原因。

怎麼說？看完下面的例子就能明白。

### `pip uninstall`的困境：以 Flask 為例

假設現在你的工作專案中有開發 API 的需求，經過一番研究與討論，決定使用 [Flask](https://github.com/pallets/flask) 網頁框架來進行開發。

我們知道，很多套件都有依賴的套件，也就是使用「別人已經造好的輪子」來構成套件功能的一部分。

安裝主套件時，這些依賴套件也必須一併安裝，主套件才能正常運作，這裡的 Flask 就是如此。安裝 Flask 時，不僅會安裝單一個套件`flask`，還會安裝所有 Flask 的必要構成部分，如下：

```
❯ pip install flask
Collecting flask
  Downloading Flask-2.1.1-py3-none-any.whl (95 kB)
     |████████████████████████████████| 95 kB 993 kB/s
Collecting importlib-metadata>=3.6.0
  Using cached importlib_metadata-4.11.3-py3-none-any.whl (18 kB)
Collecting itsdangerous>=2.0
  Downloading itsdangerous-2.1.2-py3-none-any.whl (15 kB)
Collecting Werkzeug>=2.0
  Downloading Werkzeug-2.1.1-py3-none-any.whl (224 kB)
     |████████████████████████████████| 224 kB 2.8 MB/s
Collecting click>=8.0
  Downloading click-8.1.2-py3-none-any.whl (96 kB)
     |████████████████████████████████| 96 kB 1.9 MB/s
Collecting Jinja2>=3.0
  Downloading Jinja2-3.1.1-py3-none-any.whl (132 kB)
     |████████████████████████████████| 132 kB 3.7 MB/s
Collecting zipp>=0.5
  Using cached zipp-3.7.0-py3-none-any.whl (5.3 kB)
Collecting MarkupSafe>=2.0
  Downloading MarkupSafe-2.1.1-cp38-cp38-macosx_10_9_x86_64.whl (13 kB)
Installing collected packages: zipp, MarkupSafe, Werkzeug, Jinja2, itsdangerous, importlib-metadata, click, flask
Successfully installed Jinja2-3.1.1 MarkupSafe-2.1.1 Werkzeug-2.1.1 click-8.1.2 flask-2.1.1 importlib-metadata-4.11.3 itsdangerous-2.1.2 zipp-3.7.0
```

從上可知，`pip install flask`還會一併安裝`importlib-metadata`、`itsdangerous`等 7 個依賴套件，實際上總共安裝了 8 個套件！

pip 在「安裝」套件時的相依性管理還是可以的，這並不難，因為套件的依賴要求都寫在安裝檔裡了，根本不需要「解析」。

------

附帶一提，這 8 個套件包括`flask`，除了`importlib-metadata`和`zipp`外，其餘 6 個實際上都是 [Flask 團隊自行開發的套件](https://palletsprojects.com/p/)。

但是並不是隻有 Flask 框架會使用（依賴）這些套件。

比如其中的 [Click](https://palletsprojects.com/p/click/) 就是一個廣泛使用的命令製作工具。套件官網是這麼介紹的：

> Click is a Python package for **creating beautiful command line interfaces** in a composable way with as little code as necessary.

別的套件也可能依賴`click`來提供命令列的功能，換句話說，主套件的依賴套件也可能被其他第三方套件所依賴、使用。

------

好，一切都很美好，就這樣一年過去，團隊決定改用火紅的 FastAPI 取代 Flask 來實作專案的 API，作為 API 的主要開發人員，你興高採列地安裝了 FastAPI，更新了所有程式碼，最後要移除 Flask，這時問題就來了。

安裝 Flask 的時候，只需要`pip install flask`，pip 就會幫你一併安裝所有依賴套件。現在要移除它，也只要`pip uninstall flask`就可以了嗎？

很遺憾，**答案是否定的**。

### pip 的致命缺陷：缺乏移除套件時的依賴解析（相依性管理）

僅執行`pip uninstall flask`的話，pip 就**真的只會**幫你移除`flask`這個套件**本身**而已。那剩下的、再也用不到的套件怎麼辦？你只能一個一個手動移除！

但你千萬不要真的嘗試手動移除依賴套件！——因為你無法確定這些依賴套件**是否同時被別的套件所依賴**。

### pip 手動移除依賴套件的潛在風險：以 Flask + Black 為例

繼續以 Flask 為例，還記得其中一個依賴套件是`click`，如前所述，它是一個協助製作命令列界面的工具。

假設專案中同時也使用 [Black](https://github.com/psf/black) 這個 formatter 進行程式碼風格管理（沒錯！我現在個人開發也都改用 Black 取代 [yapf](https://github.com/google/yapf) 了），Black 是一個可以透過 CLI 執行的工具，很巧的，它也是使用`click`來實作命令列界面。

可想而知，移除 Flask 時，如果你同時把`click`也跟著一併移除，會發生什麼樣的悲劇——你的 Black 壞了。

簡言之，直接 pip 手動移除依賴套件存在下列兩大疑慮，不建議輕易嘗試：

**一、無法確定想移除的套件還有多少依賴套件**

正常而言，你不會去注意安裝時總共一併安裝了多少依賴套件。雖然有`pip show`這類的指令可以大概知曉套件的依賴，但這指令只會顯示「**直接**依賴套件」而不會顯示「依賴套件的依賴」，所以列出來的結果未必準確：

```
❯ pip show flask
Name: Flask
Version: 2.1.1
Summary: A simple framework for building complex web applications.
Home-page: https://palletsprojects.com/p/flask
Author: Armin Ronacher
Author-email: armin.ronacher@active-4.com
License: BSD-3-Clause
Location: /Users/kyo/.pyenv/versions/3.8.12/envs/test/lib/python3.8/site-packages
Requires: importlib-metadata, Werkzeug, click, Jinja2, itsdangerous
Required-by:
```

可以看到，`Requires:`只顯示了 5 個依賴套件，因為剩下的 2 個（`zipp`、`markupsafe`）是「**依賴的依賴**」，在更下層，並未顯示。

**二、即使確定所有依賴套件，也無法確定這些套件是否還被其他套件所依賴**

好繞口啊！上述的`click`例子就是解釋這個困境。

### 小結：pip 只適合小型專案或「只新增不移除」套件的專案

以前我的個人或工作上的專案往往規模不大，pip 就真的只負責新增，鮮少需要考慮移除套件的情況，所以缺少移除套件時的依賴解析，似乎也沒什麼大問題。

但稍具模規的專案往往就需要考慮套件的退場，以維持開發及部署環境的簡潔，尤其在使用容器化部署時，過多不必要的套件會徒增 image 的肥大，產生額外的成本與浪費。

然而透過上面的例子可知，僅靠 pip 想要乾淨移除過時的套件，且不影響既有的套件，簡直是不可能的任務！所以我們需要有完整套件**依賴解析、相依性管理**的套件管理器。

## pip 替代方案選擇

因為 pip 存在這樣的致命弱點，所以很早就有相關的方案提出想要解決它，最知名的莫過於 [Pipenv](https://pipenv.pypa.io/en/latest/)！

關於 pip 的前世今生，以及為何它難以演化成理想的、可以完美管理套件相依性的版本，可以參考〈[告別 Anaconda：在 macOS 上使用 pyenv + pyenv-virtualenv 建立 Python 開發環境](https://blog.kyomind.tw/pyenv-setup/)〉中推薦過的單集 Podcast：[《捕蛇者說》Ep 15. 和 PyPA 的成員聊聊 Python 開發工作流](https://pythonhunter.org/episodes/ep15)。

從 Podcast 網頁「時間節點」目錄中可知，該集對 Python 的虛擬環境與套件管理機制及相關工具，有著非常廣泛的討論，十分精彩，強力推薦！（為了寫這篇又聽了第 3 次）

[![img](https://i.imgur.com/gzcAU7e.png)](https://i.imgur.com/gzcAU7e.png)

### Pipenv vs Poetry

講到需要有充分「套件相依性管理」功能的套件管理器，你基本上也只能從 Pipenv 和 Poetry 兩者之中二擇一了。

如果是在兩年前，這個選擇難題恐怕不容易回答，而且 Pipenv 會有較大的機率勝出，但兩年後的今天，我建議你毫不猶豫地選擇 Poetry。

### 我選擇 Poetry 的第一個理由

第一個理由：不要選擇 Pipenv。

乍看之下有點鬧，但卻不失為一個具體的理由，因為當你搜尋「python poetry」關鍵字的時候，那些教你怎麼使用 Poetry 的文章往往也會一併提及為何不選擇 Pipenv。

以下兩篇有著較為完整的說明，請容我直接引用。

〈[Python - 取代 Pipenv 的新套件管理器 Poetry](https://note.koko.guru/posts/using-poetry-manage-python-package-environments)〉：

> Pipenv 雖然強大，卻也暴露出了一些問題如 Lock 過慢、Windows 支援性差、對 PyPI 套件打包的友善度差…等更多其他問題，甚至有越來越多人表明 [不要使用 Pipenv](http://greyli.com/do-not-use-pipenv/) 或 [pipenv 的凋零與替代方案 poetry](https://blog.gslin.org/archives/2019/12/21/9347/pipenv-的凋零與替代方案-poetry/) 等。

> 同時 Pipenv 的社群維護狀況也越來越差，有許多的 PR 都沒有被 Release，導致許多貢獻者抱怨，甚至有人發出了該篇 [If this project is dead, just tell us](https://github.com/pypa/pipenv/issues/4058) issue 想知道是否專案已經不在維護。

〈[相比 Pipenv，Poetry 是一個更好的選擇](https://greyli.com/poetry-a-better-choice-than-pipenv/)〉（本文作者[李輝](https://greyli.com/about/)為 Flask 團隊成員）：

> Pipenv 描繪了一個美夢，讓我們以為 Python 也有了其他語言那樣完善的包管理器，不過這一切卻在後來者 Poetry 這裡得到了更好的實現。

> 這幾年 Pipenv 收獲了很多用戶，但是也暴露了很多問題。雖然 Lock 太慢、Windows 支持不好和 bug 太多的問題都已經改進了很多，但對我來說，仍然不能接受隨時更新鎖定依賴的設定，在上一篇文章《[不要用 Pipenv](http://greyli.com/do-not-use-pipenv/)》裡也吐槽了很多相關的問題。

兩篇的內容總結就是一句話：不要用 Pipenv。

目前 Pipenv 已經由 [PyPA](https://github.com/pypa)（同時也維護 pip 及 vituralenv）接手，上述「擺爛」的情況應該是有所好轉，不過我似乎還沒看到有什麼文章大力鼓吹或宣告 Pipenv 已經「great again」，所以個人對它的未來發展還是持保留態度。

### 選擇 Poetry 的第二個理由：pyproject.toml

pyproject.toml 是 [PEP 518](https://peps.python.org/pep-0518/) 所提出的新標準：

> The build system dependencies will be stored in a file named `pyproject.toml` that is written in the TOML format.

雖然原意是作為套件打包的標準，但後來又有了 [PEP 621](https://peps.python.org/pep-0621/)，擴充定性為 Python 生態系工具的共同設定檔標準，現在已經被愈來愈多套件所支援，詳細可參考[這個清單](https://github.com/carlosperate/awesome-pyproject)及頁面中的說明：

> `pyproject.toml` is a new configuration file defined in [PEP 518](https://www.python.org/dev/peps/pep-0518/) and expanded in [PEP 621](https://www.python.org/dev/peps/pep-0621/). It is design to store build system requirements, but it can also store any tool configuration for your Python project, possibly replacing the need for `setup.cfg` or other tool-specific files.

作為規範控，我很願意追隨這個標準。

並且，Poetry 使用`pyproject.toml`可遠遠不止是設定檔的程度，基本上相當於 Pipenv 的`Pipfile`或 npm 的`package.json`。

少了`pyproject.toml`，Poetry 是無法運作的。

好，漫長的前言到此結束，讓我們進入正題，開始學習上手 Poetry。

------

## 從零開始使用 Poetry

本文所有的參考資料會放在文末的「參考」一欄中，不過在此還是要特別提及主要的參考對象，總共有二：

- [Poetry 官方文件](https://python-poetry.org/docs/)
- [Dependency Management With Python Poetry](https://realpython.com/dependency-management-python-poetry/)

在本文找不到你需要的內容，以上二處可能會有，所以特別提及。

另外本文主要以 macOS 和 Linux 環境來進行教學及安裝，Windows 用戶如果有無法順利安裝的情況，建議參考官方文件內容修正。相信如果有問題，應該也只會集中在安裝設定階段，本文其餘部分仍可適用。

## 安裝 Poetry

Poetry 和 pip、git、pyenv 等工具一樣，都是典型的命令列工具，需要先安裝才能下達指令`poetry`。

### 安裝方式選擇

而 Poetry 提供了兩種安裝方式：

1. **全域安裝**至使用者的家目錄。
2. **pip 安裝**至專案的 Python 環境。

**個人推薦使用全域安裝**，連[官方文件也這麼說](https://python-poetry.org/docs/#alternative-installation-methods-not-recommended)。

因為 pip 安裝是直接安裝到專案所屬的 Python 環境裡，而且 Poetry 所依賴的套件非常多，**總計超過 30 個，會嚴重影響專案環境的整潔度**。文件中也警告這些依賴套件的版本可能和專案既有的版本**產生衝突**：

> Be aware that it will also install Poetry’s dependencies which might cause conflicts with other packages.

### 全域安裝至家目錄

所以我們就使用全域安裝吧！參考 Poetry 的 [GitHub 說明](https://github.com/python-poetry/poetry#installation)。

macOS / Linux：

```
curl -sSL https://install.python-poetry.org | python3 -
```

Windows：

```
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

文件表示安裝的路徑如下：

> The installer installs the `poetry` tool to Poetry’s `bin` directory. This location depends on your system:

- `$HOME/.local/bin` for Unix
- `%APPDATA%\Python\Scripts` on Windows

以 macOS 為例，此時如果要下指令，就需要打完整路徑`$HOME/.local/bin/poetry`，顯然不太方便，所以我們需要設定 PATH。

### 設定 PATH

新增`poetry`指令執行檔所在的路徑至 PATH。

在`.zshrc`或`.bashrc`或`.bash_profile`新增：

```
export PATH=$PATH:$HOME/.local/bin
```

存檔後重啟 shell 即可使用。直接在命令列打上`poetry`指令測試：

```
❯ poetry
Poetry version 1.1.13

USAGE
  poetry [-h] [-q] [-v [<...>]] [-V] [--ansi] [--no-ansi] [-n] <command> [<arg1>] ... [<argN>]

...
```

### 設定 alias

比起`pip`，`poetry`這個指令顯然太冗長了！我們還是給它一個 alias 吧！

基於它是我非常常用的指令，我願意賦與它「單字母」alias 的特權，我使用`p`：

```
alias p='poetry'
```

測試結果：

```
❯ p
Poetry version 1.1.13

USAGE
  poetry [-h] [-q] [-v [<...>]] [-V] [--ansi] [--no-ansi] [-n] <command> [<arg1>] ... [<argN>]
```

alias 是方便自己使用，但本文基於表達清晰考量，下面的解說原則上並不會使用 alias 表示。

## 初始化 Poetry 專案

為了方便解說，我們先建立一個全新的專案，名為`poetry-demo`。

指令都很簡單，但還是建議可以一步一步跟著操作。

就像 git 專案需要初始化，Poetry 也需要，因為每一個使用了 Poetry 的專案中一定要有一個`pyproject.toml`。所以先來初始化，使用`poetry init`：

```
mkdir poetry-demo
cd poetry-demo
poetry init
```

此時會跳出一連串的互動對話，協助你建立專案的資料，大部分可以直接`enter`跳過：

```
This command will guide you through creating your pyproject.toml config.

Package name [poetry-demo]:
Version [0.1.0]:
Description []:
Author [kyo <odinxp@gmail.com>, n to skip]:
License []:
Compatible Python versions [^3.8]:

Would you like to define your main dependencies interactively? (yes/no) [yes]
```

直到出現「Would you like to define your main dependencies interactively? (yes/no) [yes]」，我會選「no」，隨即讓你確認本次產生的`toml`檔內容：

```
Would you like to define your development dependencies interactively? (yes/no) [yes] no
Generated file

[tool.poetry]
name = "poetry-demo"
version = "0.1.0"
description = ""
authors = ["kyo <odinxp@gmail.com>"]

[tool.poetry.dependencies]
python = "^3.8"

[tool.poetry.dev-dependencies]

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

並詢問你「Do you confirm generation? (yes/no) [yes]」，按`enter`使用預設選項或回答「yes」則`pyproject.toml`建立完成。

此時專案目錄結構如下：

```
poetry-demo
└── pyproject.toml

0 directories, 1 file
```

## 管理 Poetry 虛擬環境

我覺得學習 Poetry 的第一道關卡，就是它對於虛擬環境的管理。

### 強制虛擬環境

Poetry 預設上（可透過`poetry config`修改）會強制套件都要安裝在虛擬環境中，以免汙染全域，所以它整合了`vitrualenv`。

在執行`poetry add、install`等指令時，Poetry 都會自動檢查**是否正在使用虛擬環境：**

- 如果是，則會直接安裝套件至當前的虛擬環境。
- 如果否，則會自行幫你建立一個獨立的虛擬環境，再進行套件安裝。

### 容易混淆的虛擬環境

Poetry 直接整合的虛擬環境管理算是立意良善，相當於把`pip`+`venv`的功能整合在一起，但如此也帶來一定的複雜度，尤其在你已經自行使用了`venv`、`vitrualenv`或 `pyenv-vitrualenv`或`conda`來管理虛擬環境的情況下！

沒錯，Python 的虛擬環境管理就是這麼麻煩。

個人建議，對新手而言，於 Poetry 的專案中，**一律使用 Poetry** 來管理虛擬環境即可。

### 以指令建立虛擬環境

使用指令`poetry env use python`：

```
❯ poetry env use python
Creating virtualenv poetry-demo-IEWSZKSE-py3.8 in /Users/kyo/Library/Caches/pypoetry/virtualenvs
Using virtualenv: /Users/kyo/Library/Caches/pypoetry/virtualenvs/poetry-demo-IEWSZKSE-py3.8
```

重點說明：

- Poetry 原則上會使用目前的 Python 版本來建立虛擬環境，這取決於`python`在你的 PATH 是連結到哪個版本，也可以明示為`python3`或`python3.8`，前提是 PATH 中確實存在這些連結。
- Poetry 會統一將虛擬環境建立在「特定目錄」下，本例中是`/Users/kyo/Library/Caches/pypoetry/virtualenvs`。
- 虛擬環境的命名模式固定為`專案名稱-亂數-Python版本`。

老實說我個人不是很喜歡這樣的做法，因為如此一來單一專案允許建立複數個虛擬環境（Python 3.7、 3.8、3.9 可以各來一個），彈性之餘也增加了混亂程度，且命名模式我也不喜歡，太冗長了。

既然 Poetry 管理的套件環境是高度綁定專案本身的，我更偏好`venv`式的做法，也就是**把虛擬環境放到專案目錄內**，而不是統一放在獨立的目錄下，讓虛擬環境與專案呈現**直觀的一對一關係**。

所幸 Poetry 具備這樣的選項。

### 修改`config`，建立專案內的`.venv`虛擬環境

讓我們使用`poetry config`指令來查看 Poetry 目前幾個主要的設定，需要使用`--list`這個參數：

```
❯ poetry config --list
cache-dir = "/Users/kyo/Library/Caches/pypoetry"
experimental.new-installer = true
installer.parallel = true
virtualenvs.create = true
virtualenvs.in-project = false
virtualenvs.path = "{cache-dir}/virtualenvs"
```

其中`virtualenvs.create = true`若改成`false`，則可以停止 Poetry 在「偵測不到虛擬環境時會自行建立」的行為模式，但建議還是不要更動。

而`virtualenvs.in-project = false`就是我們要修改的目標：

```
poetry config virtualenvs.in-project true
```

好，我們先把之前建立的虛擬環境刪除：

```
❯ poetry env remove python
Deleted virtualenv: /Users/kyo/Library/Caches/pypoetry/virtualenvs/poetry-demo-IEWSZKSE-py3.8
```

重新建立，看看行為有何差異：

```
❯ poetry env use python
Creating virtualenv poetry-demo in /Users/kyo/Documents/code/poetry-demo/.venv
Using virtualenv: /Users/kyo/Documents/code/poetry-demo/.venv
```

可以看出：

- 虛擬環境的路徑改為「專案的根目錄」。
- 名稱固定為`.venv`。

我覺得這樣的設定更加簡潔。

### 啟動與退出虛擬環境

啟動虛擬環境，需移至專案目錄底下，使用指令`poetry shell`：

```
❯ poetry shell
Spawning shell within /Users/kyo/Documents/code/poetry-demo/.venv
❯ . /Users/kyo/Documents/code/poetry-demo/.venv/bin/activate 
```

`poetry shell`指令會偵測當前目錄或所屬上層目錄是否存在`pyproject.toml`來確定所要啟動的虛擬環境，所以如果不移至專案目錄，則會出現下列錯誤：

```
❯ poetry shell

  RuntimeError

  Poetry could not find a pyproject.toml file in /Users/kyo/Documents/code or its parents

  at ~/Library/Application Support/pypoetry/venv/lib/python3.8/site-packages/poetry/core/factory.py:369 in locate
      365│             if poetry_file.exists():
      366│                 return poetry_file
      367│
      368│         else:
    → 369│             raise RuntimeError(
      370│                 "Poetry could not find a pyproject.toml file in {} or its parents".format(
      371│                     cwd
      372│                 )
      373│             )
```

可以看出 Poetry 的錯誤訊息非常清楚，讓你很容易知曉修正的方向，這是作為一個命令列工具的必要優點。

退出就簡單多了，只需要`exit`即可。

## Poetry 常用指令

Poetry 是一個獨立的命令列工具，就像 pyenv，它有自己的指令，需要花費額外的心力學習。這可能是使用 Poetry 的第二道關卡。所幸和 pyenv 一樣，常用的指令就那幾個而已，所以不用擔心，下面會一一介紹。

繼續使用前面提過的 Flask 和 Black 這兩個套件來加以來示範並說明 Poetry 的優勢與和 pip 的不同之處。本文的示範就只會安裝或移除這兩個套件而已。

### Poetry 新增套件

使用指令：

```
poetry add
```

相當於`pip install`，我們來試著安裝 Flask 看看會有什麼變化：

[![img](https://i.imgur.com/H7pPtsk.png)](https://i.imgur.com/H7pPtsk.png)

圖中可以看出 Poetry 漂亮的命令列資訊呈現，會清楚告知總共新增了幾個套件。

此時專案中的`pyproject.toml`也會發生變化：

```
...
[tool.poetry.dependencies]
python = "^3.8"
Flask = "^2.1.1"

[tool.poetry.dev-dependencies]

[build-system]
...
```

這裡要說明，安裝 Flask，則`pyproject.toml`就只會顯示`Flask = "^2.1.1"`這個 **top-level** 的 package 項目，其餘的依賴套件**不會**直接記錄在`toml`檔中。

我覺得這是一大優點，方便區分哪些是你**主動安裝**的主要套件，而哪些又是基於套件的依賴關係而一併安裝的依賴套件。

### poetry.lock 與更新順序

除了`pyproject.toml`，此時專案中還會增加一個新增檔案，名為`poetry.lock`，它實際上就相當於 pip 中的`requirements.txt`，詳細記載了所有安裝的套件與版本。

當你使用`poetry add`指令時，Poetry 會自動依序幫你做完這三件事：

- 更新`pyproject.toml`。
- 依照`pyproject.toml`的內容，更新`poetry.lock`。
- 依照`poetry.lock`的內容，更新虛擬環境。

換句話說，`poetry.lock`的內容主要是取決於`pyproject.toml`，但兩者並不會自己連動，一定要基於特定指令才會進行同步與更新，`poetry add`就是一個典型案例。

此時專案目錄結構如下：

```
poetry-demo
├── poetry.lock
└── pyproject.toml

0 directories, 2 files
```

### 更新 poetry.lock

當你自行修改了`pyproject.toml`內容，比如變更特定套件的版本與範圍（這是有可能的，尤其在手動處理版本衝突的時候），此時`poetry.lock`的內容與`pyproject.toml`出現了脫鉤，必須讓它依照新的`pyproject.toml`內容來自我更新，使用指令：

```
poetry lock
```

如此一來，手動修改的內容，才能確保也更新到`poetry.lock`，畢竟虛擬環境如果要重新建立，是基於`poetry.lock`的內容來安裝套件，而非`pyproject.toml`。

再次強調，`poetry.lock`相當於 Poetry 的`requirements.txt`。

### 列出全部套件清單 + 樹狀顯示

類似`pip list`，這裡使用`poetry show`：

```
❯ poetry show
click              8.1.2  Composable command line interface toolkit
flask              2.1.1  A simple framework for building complex web applications.
importlib-metadata 4.11.3 Read metadata from Python packages
itsdangerous       2.1.2  Safely pass data to untrusted environments and back.
jinja2             3.1.1  A very fast and expressive template engine.
markupsafe         2.1.1  Safely add untrusted strings to HTML/XML markup.
werkzeug           2.1.1  The comprehensive WSGI web application library.
zipp               3.8.0  Backport of pathlib-compatible object wrapper for zip files
```

特別提醒的是，這裡的清單內容並不是來自於虛擬環境，這點和 pip 不同，而是來自於`poetry.lock`的內容。

而 Poetry 最為人津津樂道的就是它的樹狀顯示`poetry show --tree`：

```
❯ poetry show --tree
flask 2.1.1 A simple framework for building complex web applications.
├── click >=8.0
│   └── colorama *
├── importlib-metadata >=3.6.0
│   └── zipp >=0.5
├── itsdangerous >=2.0
├── jinja2 >=3.0
│   └── markupsafe >=2.0
└── werkzeug >=2.0
```

讓主要套件與其依賴套件的關係層次，一目瞭然。

### 安裝套件至 dev-dependencies

有些套件，比如`pytest`、`flake8`等等，只會在開發環境中使用，產品的部署環境並不需要，Poetry 允許你區分這兩者，將上述的套件安裝至`dev-dependencies`區塊，方便讓你輕鬆建立一份沒有這些套件的虛擬環境。

在此以 Black 為例，安裝方式如下：

```
poetry add black -D
```

或

```
poetry add black --dev
```

結果的區別顯示在`pyproject.toml`裡：

```
...
[tool.poetry.dependencies]
python = "^3.8"
Flask = "^2.1.1"

[tool.poetry.dev-dependencies]
black = "^22.3.0"
...
```

可以看到`black`被列在不同區塊：`tool.poetry.dev-dependencies`。

然而這是記載上的差異，使用上具體的差別為何？下面會再次提及，可以理解為「輸出套件環境」上的差異。

### Poetry 移除套件

使用`poetry remove`指令。和`poetry add`一樣，可以加上`-D`參數來移除置於開發區的套件。

而移除套件時的「依賴解析」能力，正是 Poetry 遠遠優於 pip 的主要環節，因為 pip 沒有嘛！也是為何我提議改用 Poetry 的關鍵理由——為了順利移除套件。

前面已經提過，pip 的`pip uninstall`只會移除你所指定的套件，而不會連同依賴套件一起移除——因為 pip 沒有「依賴解析」功能。如果貿然移除「安裝時所有一併安裝」的依賴套件，可能會造成巨大的災難，讓別的套件失去效用。

前面也舉了 Flask 和 Black 都共同依賴`click`這個套件的例子，在人為手動移除的情況下，你可能未曾注意 Black 也依賴了`click`，結果為了「徹底移除」Flask 的所有相關套件，不小心把`click`也移除掉了。

當然，我知道，絕大部分的真實情況是——你根本不會去移除一段時間前安裝但已不再使用的套件。

------

好，解釋了很多，接下來就是 Poetry 的表演了，它會幫你處理這些棘手的「套件相依性」難題，讓你輕鬆移除 Flask 而不影響 Black：

[![img](https://i.imgur.com/79TycuL.png)](https://i.imgur.com/79TycuL.png)

可以對比上面安裝 Flask 時的截圖，總共安裝了 8 個套件，但現在移除卻只有 7 個——沒錯，因為 Poetry 知道 Black 還需要`click`！不能移除：

```
❯ poetry show --tree
black 22.3.0 The uncompromising code formatter.
├── click >=8.0.0
│   └── colorama *
├── mypy-extensions >=0.4.3
├── pathspec >=0.9.0
├── platformdirs >=2
├── tomli >=1.1.0
└── typing-extensions >=3.10.0.0
```

一個套件直到環境中的**其餘套件都不再依賴它**，Poetry 才會安心讓它被移除。

### 輸出 Poetry 虛擬環境的 requirements.txt

理論上，全面改用 Poetry 後，專案中是不需要存在`requirements.txt`，因為它的角色已經完全被`poetry.lock`所取代。

但事實是，你還是很可能需要它，甚至還需要隨著`poetry.lock`同步更新它的內容！至少對我而言就是如此，我在 Docker 部署環境中並不使用 Poetry，所以我需要一份完全等價於`poetry.lock`的`requirements.txt`用於 Docker 部署。

如果你想說，那我就在 Poetry 的虛擬環境下，使用以往熟悉的指令`pip freeze > requirements.txt`，來產生一份不就好了？我本來也是這麼想的。但實際的產出卻是如此（目前 poetry-demo 專案僅剩下 Black）：

```
black @ file:///Users/kyo/Library/Caches/pypoetry/artifacts/11/4c/fc/cd6d885e9f5be135b161e365b11312cff5920d7574c8446833d7a9b1a3/black-22.3.0-cp38-cp38-macosx_10_9_x86_64.whl
click @ file:///Users/kyo/Library/Caches/pypoetry/artifacts/f0/23/09/b13d61d1fa8b3cd7c26f67505638d55002e7105849de4c4432c28e1c0d/click-8.1.2-py3-none-any.whl
mypy-extensions @ file:///Users/kyo/Library/Caches/pypoetry/artifacts/b6/a0/b0/a5dc9acd6fd12aba308634f21bb7cf0571448f20848797d7ecb327aa12/mypy_extensions-0.4.3-py2.py3-none-any.whl
...
```

這呈現好像不是我們以前熟悉的那種：

```
black==22.3.0
click==8.1.2
mypy_extensions==0.4.3
...
```

沒錯，只要是使用`poetry add`安裝的套件，在`pip freeze`就會變成這樣。此時想輸出類似`requirements.txt`的樣式，需要使用`poetry export`。

預設輸出會有 hash 值，不想納入則要加上參數去除。現在我都是用以下指令來輸出：

```
poetry export -f requirements.txt -o requirements.txt --without-hashes
```

我們再看一下輸出結果，雖然不盡相同，但也相去不遠了…嗎？等等，怎麼是空白？

------

因為`poetry export`預設只會輸出`toml`中的`[tool.poetry.dependencies]`區塊的套件！還記得上面我們把 Black 安裝到`[tool.poetry.dev-dependencies]`了嗎？

顯然 Poetry 認為你的 export 需求基本上就為了部署，並不需要開發區的套件。這倒是沒錯，不過基於演示需求，我們必須輸出`[tool.poetry.dev-dependencies]`的套件，才能看到 Black。

加上`—-dev`參數即可：

```
poetry export -f requirements.txt -o requirements.txt --without-hashes --dev
```

輸出的`requirements.txt`內容：

```
black==22.3.0; python_full_version >= "3.6.2"
click==8.1.2; python_version >= "3.7" and python_full_version >= "3.6.2"
colorama==0.4.4; python_version >= "3.7" and python_full_version >= "3.6.2" and platform_system == "Windows"
...
```

雖然長得有點不一樣，但這個檔案確實是可以`pip install`的。

從這裡也可以看出前面提及的「區分套件安裝區塊」的價值了——有些時候並不需要輸出開發專用套件。

`poetry export`所有參數用法與說明，請參考[文件](https://python-poetry.org/docs/cli/#export)。

此時專案目錄結構如下：

```
poetry-demo
├── poetry.lock
├── pyproject.toml
└── requirements.txt

0 directories, 3 files
```

### 小結：Poetry 常用指令清單

算來算去，Poetry 的常用指令主要有下面幾個：

- `poetry add`
- `poetry remove`
- `poetry export`
- `poetry env use`
- `poetry shell`
- `poetry show`
- `poetry init`
- `poetry install`

其中一半以上，單一專案可能只會用個一兩次而已，比如`init`、`install`和`env use`，實際上需要學習的指令並不多。

那麼，只要知曉這些指令，就可以順利運用 Poetry 了嗎？可能是，也可能否，所以我下面還會再補充 Poetry 的常見使用情境與操作方式，讓你接納 Poetry 的阻力可以進一步下降！

## Poetry 常見使用情境與操作 QA

這部分會以「使用場景」的角度切入，介紹 Poetry 應用情境與操作說明，還包括一些自問自答，如下：

1. [新增專案並使用 Poetry](https://blog.kyomind.tw/python-poetry/#一、新增專案並使用-Poetry)
2. [現有專案改用 Poetry](https://blog.kyomind.tw/python-poetry/#二、現有專案改用-Poetry)
3. [在別臺主機回復專案狀態](https://blog.kyomind.tw/python-poetry/#三、在別臺主機回復專案狀態)
4. [我想要重建虛擬環境](https://blog.kyomind.tw/python-poetry/#四、我想要重建虛擬環境)
5. [為什麼我不在 Docker 環境中使用 Poetry？](https://blog.kyomind.tw/python-poetry/#五、為什麼我不在-Docker-環境中使用-Poetry？)
6. [我可以使用自己習慣的 vituralenv 嗎？](https://blog.kyomind.tw/python-poetry/#六、我可以使用自己習慣的-vituralenv-嗎？)

### 一、新增專案並使用 Poetry

這是最理想的狀態，沒有過去的「包袱」，可謂是最能輕鬆採用 Poetry 的情境。

使用順序不外乎是：

1. `poetry init`：初始化，建立`pyproject.toml`。
2. `poetry env use python`：建立專案虛擬環境並使用。
3. `poetry shell`：進入專案但虛擬環境還未啟動，以這個指令啟動。如果使用本指令時虛擬環境**還不存在或已移除**，則會直接自動幫你建立虛擬環境並使用。
4. `poetry add`：新增套件，必要使用`-D`參數新增至 dev 區塊。
5. `poetry remove`：移除套件，若是移除 dev 區塊的套件，需要加上`-D`參數。

這部分和前面內容沒有差別，因為前面內容就是以全新專案作為基礎。

### 二、現有專案改用 Poetry

這是極為常見的需求，但並沒有很正式的做法，因為不存在`poetry import`之類的指令。

首先要考量的就是：要怎麼把`requirements.txt`的所有項目加到`pyproject.toml`中呢？經過一番 Google，基本上[只能土法煉鋼](https://stackoverflow.com/questions/62764148/how-to-import-requirements-txt-from-an-existing-project-using-poetry)：

```
cat requirements.txt | xargs poetry add
```

在這個過程是有可能遇到問題的，因為 Poetry 對套件的版本衝突比較敏感，所以在`requirements.txt`能正常安裝的項目，在上述指令的過程中可能會出錯。

那怎麼辦？只能照著錯誤訊息去修正`requirements.txt`中的套件版本。

並且，這個 import 做法實在是不得已，因為我們最早介紹`pyproject.toml`時有提到，原則上它只會記載「主套件」，但這個做法相當於把`requirements.txt`中的**所有套件都當作主套件**來`add`了！——畢竟`requirements.txt`沒有能力區分主套案與依賴套件，都是「一視同仁」地列出。

如此做法讓專案的套件失去了主從之分，日後想要移除主套件時，就需要比較多心力去分辨主從，比如使用`poetry show --tree`去一一檢視，終究是麻煩的事。

完成轉換後，保險起見，重建一個虛擬環境會比較合適。

### 三、在別臺主機回復專案狀態

這也是非常常見的需求。

第一步當然是`git clone`專案，此時專案中已經有 Poetry 所需的必要資訊了——也就是`pyproject.toml`和`poetry.lock`。

你還缺少的僅僅是虛擬環境。如果是全新的主機，則還得先安裝、設定好 Poetry。

移至專案目錄底下，然後依序操作：

1. `poetry env use python`：建立專案虛擬環境並使用。如果你懶得打這麼長的指令，直接`poetry shell`也是可以。
2. `poetry install`：因為是舊專案，不再需要`init`，直接從`poetry.lock`安裝套件！使用的就是這個指令，類似`npm install`。

### 四、我想要重建虛擬環境

在使用專案內虛擬環境方案，也就是`.venv`的前提下，想要刪除這個虛擬環境並加以重建，也不需要使用`poetry env remove python`指令了，因為會出錯。

還有更簡單暴力的方式，是什麼呢？當然是直接刪除`.venv`資料夾即可。

然後再`poetry env use python`或`poetry shell`建一個新的就好。

### 五、為什麼我不在 Docker 環境中使用 Poetry？

因為啟動容器後需要先安裝 Poetry 到全域，或打包一個帶有 Poetry 的 image，兩者都會增加新的藕合與依賴，我覺得並不妥當。

所幸 Poetry 依舊可以輸出`requirements.txt`，Docker 部署環境就繼續使用舊方案即可，而且 Poetry 本來主要就是用於「開發」時的套件管理，對部署差別不大。

### 六、我可以使用自己習慣的 vituralenv 嗎？

當然可以。

我本來也繼續使用`pyenv`的`vituralenv`，但兩者有時候也是會小小打架，後來還是索性用 Poetry 的虛擬環境就好。一個專案對應一個虛擬環境，我認為還是比較簡潔的做法。

------

## 結語

使用 Poetry 來管理專案的套件與虛擬環境，雖然需要一定的學習成本，但帶來的效益還是相當可觀的，尤其在你希望能乾淨且安心地移除套件的時候。

別再猶豫，從今天起，加入 Poetry 的行列吧！

### 參考

- https://python-poetry.org/docs/
- https://github.com/python-poetry/poetry
- https://github.com/python-poetry/poetry/issues/3248
- https://github.com/python-poetry/poetry/issues/5185
- [Python - 取代 Pipenv 的新套件管理器 Poetry](https://note.koko.guru/posts/using-poetry-manage-python-package-environments)
- [相比 Pipenv，Poetry 是一個更好的選擇](https://greyli.com/poetry-a-better-choice-than-pipenv/)
- [pip, pipenv 和 poetry 的選擇](https://shazi.info/pip-pipenv-和-poetry-的選擇/)
- [Dependency Management With Python Poetry](https://realpython.com/dependency-management-python-poetry/)
- [Ep 15. 和 PyPA 的成員聊聊 Python 開發工作流](https://pythonhunter.org/episodes/ep15)