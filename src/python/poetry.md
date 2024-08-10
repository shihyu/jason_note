## 從零開始使用 Poetry

出處: https://blog.kyomind.tw/python-poetry/

本文所有的參考資料會放在文末的「參考」一欄中，不過在此還是要特別提及主要的參考對象，總共有二：

- [Poetry 官方文件](https://python-poetry.org/docs/)
- [Dependency Management With Python Poetry](https://realpython.com/dependency-management-python-poetry/)

如果在本文找不到你需要的內容，以上二處可能會有，所以主動列出。

另外本文主要以 macOS 和 Linux（Ubuntu）環境來進行安裝及教學，Windows 用戶如果有無法順利安裝的情況，建議參考官方文件內容修正。不過，即使有問題，應該也是集中在安裝與設定階段，本文其餘部分仍可適用。

## 安裝 Poetry

Poetry 和 pip、git、pyenv 等工具一樣，都是典型的**命令列工具**，需要先安裝才能下達指令——`poetry`。

### 安裝方式選擇

Poetry 主要提供了[兩種安裝方式](https://python-poetry.org/docs/#installation)：

1. **全域安裝**至使用者的家目錄。
2. **pip 安裝**至專案使用的 Python（虛擬）環境，即`pip install poetry`。

**個人推薦使用全域安裝**，官方文件也表示[不推薦使用 pip 安裝](https://python-poetry.org/docs/#alternative-installation-methods-not-recommended)。

因為 pip 安裝是直接安裝到「**專案所屬的 Python 虛擬環境**」裡，而 Poetry 所依賴的套件非常多，**總計超過 30 個，會嚴重影響專案虛擬環境的整潔度**。文件中也警告這些依賴套件可能和專案本身的套件**發生衝突**：

> Be aware that it will also install Poetry’s dependencies which **might cause conflicts with other packages.**

### 全域安裝 Poetry 至家目錄

所以我們就使用全域安裝吧！

#### macOS / Linux / WSL（Windows Subsystem for Linux）

```
curl -sSL https://install.python-poetry.org | python3 -
```

或

```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

#### Windows

```
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

Poetry 實際安裝路徑如下：

> The installer installs the `poetry` tool to Poetry’s `bin` directory. This location depends on your system:

- `$HOME/.local/bin` for Unix
- `%APPDATA%\Python\Scripts` on Windows

以 macOS 為例，如果要下`poetry`指令，就需要打完整路徑`$HOME/.local/bin/poetry`，顯然不太方便，所以我們需要設定 PATH。

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

比起`pip`，`poetry`這個指令實在太冗長了！我們還是給它一個 alias 吧！

基於它是我極為常用的指令，我願意賦與它**「單字母」的 alias 特權**，我使用`p`：

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

alias 是方便自己使用，但本文基於表達清晰考量，下面的解說除了圖片外，原則上並不會使用 alias 表示。

------

## 初始化 Poetry 專案

為了方便解說，我們先建立一個全新的專案，名為`poetry-demo`。

指令都很簡單，但還是建議可以一步一步跟著操作。

就像 git 專案需要初始化，Poetry 也需要，因為每一個使用了 Poetry 的專案中一定要有一個`pyproject.toml`作為它的**設定檔**。否則直接使用`poetry`相關指令就會出現下列錯誤訊息：

> Poetry could not find a pyproject.toml file in {cwd} or its parents

所以一定先初始化，使用`poetry init`：

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

直到出現「`Would you like to define your main dependencies interactively? (yes/no) [yes]`」，我們先選擇「**no**」後，會讓你確認本次產生的`toml`檔內容：

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

並詢問你「`Do you confirm generation? (yes/no) [yes]`」，按`enter`使用預設選項「yes」或直接回答「yes」，則`pyproject.toml`建立完成。

此時專案目錄結構如下：

```
poetry-demo
└── pyproject.toml

0 directories, 1 file
```

## 管理 Poetry 虛擬環境

我覺得學習 Poetry 的**第一道關卡**，就是它對於虛擬環境的管理。

### 「強制」虛擬環境

Poetry 預設上（可透過`poetry config`修改）會強制套件都要安裝在虛擬環境中，以免汙染全域，所以它整合了`virtualenv`。

所以在執行`poetry add、install`等指令時，Poetry 都會自動檢查**當下是否正在使用虛擬環境：**

- 如果**是**，則會直接安裝套件至**當前**的虛擬環境。
- 如果**否**，則會自動幫你建立一個**新的**虛擬環境，再進行套件安裝。

### 容易混淆的虛擬環境

Poetry 主動納入虛擬環境管理算是立意良善，相當於把`pip`+`venv`兩者的功能直接整合在一起，**但也帶來一定的複雜度**，尤其在你已經自行使用了`venv`、`virtualenv`或 `pyenv-virtualenv`或`conda`等工具來管理虛擬環境的情況下！

**沒錯，Python 的虛擬環境管理就是這麼麻煩！**

個人建議，對新手而言，於 Poetry 的專案中，**一律使用 Poetry** 來管理虛擬環境即可。我目前也是這樣，省得麻煩。

### 以指令建立虛擬環境

使用指令`poetry env use python`：

```
❯ poetry env use python
Creating virtualenv poetry-demo-IEWSZKSE-py3.8 in /Users/kyo/Library/Caches/pypoetry/virtualenvs
Using virtualenv: /Users/kyo/Library/Caches/pypoetry/virtualenvs/poetry-demo-IEWSZKSE-py3.8
```

可以看出 Poetry 為我們建立了名為`poetry-demo-IEWSZKSE-py3.8`的虛擬環境。

### 重點說明

- `poetry env use python`建立虛擬環境所使用的 Python 版本，取決於`python`指令在你的 PATH 是連結到哪個版本。同理，你也可以將指令明示為`use python3`或`use python3.8`，只要這些指令確實存在 PATH 中。
- 預設上，Poetry 會統一將虛擬環境建立在「**特定目錄**」裡，比如本例中存放的路徑是`/Users/kyo/Library/Caches/pypoetry/virtualenvs`。
- 虛擬環境的**命名模式為`專案名稱-亂數-Python版本`。**

老實說我個人不是很喜歡這樣的做法，因為這意味著單一專案允許建立複數個虛擬環境（比如 Python 3.7、3.8、3.9 可以各來一個），**彈性之餘也增加了混亂的可能**，而且這命名模式我也不太欣賞，顯得過於僵化且冗長。

既然 Python 的虛擬環境理論上都是**高度綁定專案本身**的，我更偏好`venv`式的做法，也就是**把虛擬環境放到專案目錄內**，而非統一放在獨立的目錄，讓虛擬環境與專案呈現**直觀的一對一關係**。

所幸，Poetry 具備這樣的選項。

------

### 修改`config`，建立專案內的`.venv`虛擬環境

我們先使用`poetry config`指令來查看 Poetry 目前幾個主要的設定，需要`--list`這個參數：

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

而`virtualenvs.in-project = false`就是我們要修改的目標，使用指令：

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

- 虛擬環境的路徑改為「**專案的根目錄**」。
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

可以看到，Poetry 的錯誤訊息非常清楚，讓你很容易知曉修正的方向，這是作為一個優秀命令列工具的必要條件。

退出就簡單多了，只需要`exit`即可。

------

## Poetry 常用指令

Poetry 是一個獨立的命令列工具，就像 pyenv，它有自己的指令，需要花費額外的心力學習，且較 pip 更加複雜，這可能是使用 Poetry 的**第二道關卡**。好在常用的指令，其實也不超過 10 個，下面就來一一介紹。

在此我們繼續使用前面提過的 Flask 和 Black 套件，來示範並說明 Poetry 的優勢以及它和 pip 的不同之處。

## Poetry 新增套件

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
Flask = "^2.1.1"  # 新增部分

[tool.poetry.dev-dependencies]

[build-system]
...
```

這裡要說明，安裝 Flask，則`pyproject.toml`就只會新增記載`Flask = "^2.1.1"`這個 **top-level** 的 package 項目，其餘的依賴套件**不會**直接記錄在`toml`檔中。

我覺得這是一大優點，方便區分哪些是你**主動安裝**的主要套件，而哪些又是基於套件的依賴關係而一併安裝的依賴套件。

### poetry.lock 與更新順序

除了更新`pyproject.toml`，此時專案中還會新增一個檔案，名為`poetry.lock`，它實際上就相當於 pip 的`requirements.txt`，詳細記載了所有安裝的套件與版本。

當你使用`poetry add`指令時，Poetry 會**自動依序**幫你做完這三件事：

1. 更新`pyproject.toml`。
2. 依照`pyproject.toml`的內容，更新`poetry.lock`。
3. 依照`poetry.lock`的內容，更新虛擬環境。

由此可見，`poetry.lock`的內容是取決於`pyproject.toml`，但兩者並不會自己連動，一定要基於特定指令才會進行同步與更新，`poetry add`就是一個典型案例。

此時專案目錄結構如下：

```
poetry-demo
├── poetry.lock
└── pyproject.toml

0 directories, 2 files
```

### 更新 poetry.lock

當你自行修改了`pyproject.toml`內容，比如變更特定套件的版本（這是有可能的，尤其在手動處理版本衝突的時候），此時`poetry.lock`的內容與`pyproject.toml`出現了「**脫鉤**」，必須讓它依照新的`pyproject.toml`內容更新、同步，使用指令：

```
poetry lock
```

如此一來，才能確保手動修改的內容，也更新到`poetry.lock`中，畢竟虛擬環境如果要重新建立，是基於`poetry.lock`的內容來安裝套件，而非`pyproject.toml`。

還是那句話：`poetry.lock`相當於 Poetry 的`requirements.txt`。

------

### 安裝套件至 dev-dependencies

有些套件，比如`pytest`、`flake8`等等，**只會在開發環境中使用**，產品的**部署環境**並不需要。

Poetry 允許你**區分**這兩者，將上述的套件安裝至`dev-dependencies`區塊，方便讓你**輕鬆建立一份「不包含」`dev-dependencies`開發套件的安裝清單**。

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

### 強烈建議：善用 dev-dependencies

善用`-D`參數，明確區分**開發環境專用**的套件，我認為**非常必要**。

首先，這些套件常常屬於「**檢測型**」工具，相關的**依賴套件**著實不少！比如`flake8`，它依賴了`pycodestyle`、`pyflakes`、`mccabe`等等，還有`black`、`pre-commit`，依賴套件數量也都很可觀。

其次，既然它們都只在開發階段才需要，則完全可以從部署環境中**缺席**。如果不分青紅皂白一律安裝到`dependencies`區塊，部署環境容易顯得過於**臃腫**。

常見的`dev-dependencies`區塊項目，例示如下：

```
[tool.poetry.dev-dependencies]
flake8 = "4.0.1"
yapf = "0.32.0"
pytest = "7.1.2"
pytest-django = "4.5.2"
pytest-cov = "3.0.0"
pytest-env = "0.6.2"
pytest-sugar = "0.9.4"
pre-commit = "2.20.0"
```

------

## 列出全部套件清單

類似`pip list`，這裡要使用`poetry show`：

```
❯ poetry show
black              22.3.0 The uncompromising code formatter.
click              8.1.3  Composable command line interface toolkit
flask              2.1.2  A simple framework for building complex web applications.
importlib-metadata 4.11.4 Read metadata from Python packages
itsdangerous       2.1.2  Safely pass data to untrusted environments and back.
jinja2             3.1.2  A very fast and expressive template engine.
markupsafe         2.1.1  Safely add untrusted strings to HTML/XML markup.
mypy-extensions    0.4.3  Experimental type system extensions for programs checked...
pathspec           0.9.0  Utility library for gitignore style pattern matching of ...
platformdirs       2.5.2  A small Python module for determining appropriate platfo...
...
```

特別提醒的是，這裡的清單內容**並不是來自於虛擬環境**，這點和 pip 不同，而是來自於`poetry.lock`的內容。

你可能會想，來自於`poetry.lock`或虛擬環境，有差嗎？兩者不是應該要一致？

沒錯，理論上是，但也有不一致的時候，比如你使用了`pip install`指令安裝套件，就不會記載在`poetry.lock`中，那`poetry show`自然也不會顯示。

### 「樹狀」顯示套件依賴層級

Poetry 最為人津津樂道的就是它的樹狀顯示——`poetry show --tree`。

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
black 22.3.0 The uncompromising code formatter.
├── click >=8.0.0
│   └── colorama *
├── mypy-extensions >=0.4.3
├── pathspec >=0.9.0
├── platformdirs >=2
├── tomli >=1.1.0
└── typing-extensions >=3.10.0.0
```

讓主要套件與其依賴套件的**關係與層次，一目瞭然**。

而且很貼心的是，它也可以**只顯示「指定套件」**的依賴層級，以`celery`為例：

```
❯ poetry show celery --tree
celery 4.4.0 Distributed Task Queue.
├── billiard >=3.6.1,<4.0
├── kombu >=4.6.7,<4.7
│   ├── amqp >=2.6.0,<2.7
│   │   └── vine >=1.1.3,<5.0.0a1
│   └── importlib-metadata >=0.18
│       ├── typing-extensions >=3.6.4
│       └── zipp >=0.5
├── pytz >0.0-dev
└── vine 1.3.0
```

------

## Poetry 移除套件

使用`poetry remove`指令。和`poetry add`一樣，可以加上`-D`參數來移除置於開發區的套件。

而移除套件時的「**依賴解析（相依性管理）**」能力，正是 Poetry 遠優於 pip 的主要環節，因為 pip 沒有嘛！也是我提議改用 Poetry 的關鍵理由——**為了順利移除套件**。

前面已經提過，pip 的`pip uninstall`只會移除你所指定的套件，而不會連同依賴套件一起移除。

這是基於安全考量，因為 pip 沒有「依賴解析」功能。如果貿然移除所有「安裝時一併安裝」的依賴套件，可能會造成巨大災難，讓別的套件失去效用。

前面也舉了 Flask 和 Black 都共同依賴`click`這個套件的例子，在手動移除套件的情況下，你可能未曾注意 Black 也依賴了`click`，結果為了「徹底移除」Flask 的所有相關套件，不小心把`click`也移除掉了。

所以，使用 pip 時，我們鮮少會去移除已經不再使用的套件。畢竟**依賴關係錯綜複雜**，移除套件可能造成許多「**副作用**」，實在是太麻煩了。

### `poetry remove`的依賴解析

好，解釋了很多，接下來就是 Poetry 的表演了，它會幫你處理這些棘手的「套件相依性」難題，讓你輕鬆移除 Flask 而不影響 Black：

[![poetry remove flask](https://i.imgur.com/79TycuL.png)](https://i.imgur.com/79TycuL.png)poetry remove flask

可以對比上面安裝 Flask 時的截圖，那時總共安裝了 8 個套件，但現在移除的卻只有 7 個——沒錯，因為有依賴解析，**Poetry 知道 Black 還需要**`click`！所以不能移除：

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

------

## 輸出 Poetry 虛擬環境的 requirements.txt

理論上，全面改用 Poetry 後，專案中是不需要存在`requirements.txt`，因為它的角色已經完全被`poetry.lock`所取代。

但事實是，你可能**還是需要它**，甚至希望它隨著`poetry.lock`的內容更新！至少對我而言就是如此，我在 Docker 部署環境中並不使用 Poetry，所以我需要一份完全等價於`poetry.lock`的`requirements.txt`，用於 Docker 部署。

你可能想說，那我就在 Poetry 的虛擬環境下，使用以往熟悉的指令`pip freeze > requirements.txt`來產生一份就可以了吧？我本來也是這麼想，但實際的產出卻是如此：（提醒：目前 poetry-demo 專案中**僅剩下 Black 和它的依賴套件**）

```
black @ file:///Users/kyo/Library/Caches/pypoetry/artifacts/11/4c/fc/cd6d885e9f5be135b161e365b11312cff5920d7574c8446833d7a9b1a3/black-22.3.0-cp38-cp38-macosx_10_9_x86_64.whl
click @ file:///Users/kyo/Library/Caches/pypoetry/artifacts/f0/23/09/b13d61d1fa8b3cd7c26f67505638d55002e7105849de4c4432c28e1c0d/click-8.1.2-py3-none-any.whl
mypy-extensions @ file:///Users/kyo/Library/Caches/pypoetry/artifacts/b6/a0/b0/a5dc9acd6fd12aba308634f21bb7cf0571448f20848797d7ecb327aa12/mypy_extensions-0.4.3-py2.py3-none-any.whl
...
```

這呈現好像不是我們以前熟悉的那樣：

```
black==22.3.0
click==8.1.2
mypy_extensions==0.4.3
...
```

沒錯，只要是使用`poetry add`安裝的套件，在`pip freeze`就會變成這樣。此時想輸出類似`requirements.txt`的格式，需要使用`poetry export`。

預設的輸出結果會有 hash 值，很乾擾閱讀。不想納入 hash 則要**加上參數**去除。**以下就是我固定用來輸出`requirements.txt`的指令與參數：**

```
poetry export -f requirements.txt -o requirements.txt --without-hashes
```

`2022/08/24`補充：網友提醒，**hash 有其價值，並建議保留**，詳見[留言區](https://github.com/kyomind/blog-reply/issues/5#issuecomment-1195904820)。

我們再看一下輸出結果，雖然不盡相同，但也相去不遠了……嗎？等等，怎麼是空白？

### 輸出 dev-dependencies

因為`poetry export`**預設**只會輸出`toml`中的`[tool.poetry.dependencies]`區塊的套件！還記得上面我們把 Black 安裝到`[tool.poetry.dev-dependencies]`了嗎？

顯然 Poetry 認為你 export 基本上就為了部署，並不需要開發區的套件。

這倒是沒錯，不過基於演示需求，我們必須輸出`[tool.poetry.dev-dependencies]`的套件，才能看到 Black。

加上`--dev`參數即可：

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

從這裡也可以看出先前一再提及「**區分開發、部署套件**」的價值——大部分時候我們並不需要輸出開發用套件。

`poetry export`所有參數用法與說明，請參考[文件](https://python-poetry.org/docs/cli/#export)。

此時專案目錄結構如下：

```
poetry-demo
├── poetry.lock
├── pyproject.toml
└── requirements.txt

0 directories, 3 files
```

------

## Poetry 常用指令清單

算來算去，Poetry 的常用指令主要有下面幾個：

- `poetry add`
- `poetry remove`
- `poetry export`
- `poetry env use`
- `poetry shell`
- `poetry show`
- `poetry init`
- `poetry install`

其中一半，單一專案可能只會用個一兩次而已，比如`init`、`install`和`env use`，實際上需要學習的指令並不多。

那麼，只要知曉這些指令，就可以順利運用 Poetry 了嗎？可能是，也可能否，所以我下面還會再補充 Poetry 的常見使用情境與操作方式，讓你接納 Poetry 的阻力可以進一步下降！

------

## Poetry 常見使用情境與操作 QA

這部分會以「**使用場景**」的角度切入，介紹 Poetry 應用情境與操作說明，還包括一些自問自答：

1. [新增專案並使用 Poetry](https://blog.kyomind.tw/python-poetry/#一、新增專案並使用-Poetry)
2. [現有專案改用 Poetry](https://blog.kyomind.tw/python-poetry/#二、現有專案改用-Poetry)
3. [在別臺主機回復專案狀態](https://blog.kyomind.tw/python-poetry/#三、在別臺主機回復專案狀態)
4. [我想要重建虛擬環境](https://blog.kyomind.tw/python-poetry/#四、我想要重建虛擬環境)
5. [為什麼我不在 Docker 環境中使用 Poetry？](https://blog.kyomind.tw/python-poetry/#五、為什麼我不在-Docker-環境中使用-Poetry？)
6. [我可以使用自己習慣的 virtualenv 嗎？](https://blog.kyomind.tw/python-poetry/#六、我可以使用自己習慣的-virtualenv-嗎？)

### 一、新增專案並使用 Poetry

這是最理想的狀態，沒有過去的「包袱」，可謂是最能輕鬆採用 Poetry 的情境。

使用順序不外乎是：

1. `poetry init`：初始化，建立`pyproject.toml`。
2. `poetry env use python`：建立專案虛擬環境並使用。
3. `poetry shell`：進入專案但虛擬環境還未啟動，以這個指令啟動。如果使用本指令時虛擬環境**尚未建立或已移除**，則會**直接自動幫你建立虛擬環境**並使用。
4. `poetry add`：新增套件並寫入虛擬環境。必要時使用`-D`參數新增至 dev 區塊。
5. `poetry remove`：移除套件，若是移除 dev 區塊的套件，需要加上`-D`參數。

這部分和前面內容沒有差別，因為前面內容就是以全新專案作為基礎。

### 二、現有專案改用 Poetry

極為常見的需求，但並沒有很正式的做法，因為不存在`poetry import`之類的指令。

首先要考量的就是：要怎麼把`requirements.txt`的所有項目加到`pyproject.toml`中呢？經過一番 Google，基本上[只能土法煉鋼](https://stackoverflow.com/questions/62764148/how-to-import-requirements-txt-from-an-existing-project-using-poetry)：

```
cat requirements.txt | xargs poetry add
```

然而這樣做是有可能遇到一些問題的，因為 Poetry **對套件的版本衝突比較敏感**，所以即便用`pip install -r requirements.txt`都能正常安裝，透過上述指令的遷移過程卻仍有機會出現錯誤。

那怎麼辦？只能照著錯誤訊息手動修正`requirements.txt`中的套件版本。

只能說這個「**手動 import**」做法實在是不得已，因為我們最早介紹`pyproject.toml`時有提到，`poetry add`只會在`pyproject.toml`中寫入「主套件」，但這樣的 import 方式相當於把`requirements.txt`中的**所有套件，都當作主套件**來`add`了！

畢竟在`requirements.txt`中**無從區分**主套件與依賴套件，都是「一視同仁」地列出。

但如此做法也讓專案的套件**失去主從之分**，這樣會有什麼**壞處**？日後要移除主套件時，**需要花額外的心力去區分主從**（因為僅僅移除依賴套件**並不會有移除效果**），比如使用`poetry show --tree`去一個一個檢視，終究是件麻煩事。

完成轉換後，為保險起見，建議透過新的`pyproject.toml`來重建一個虛擬環境。

### 三、在別臺主機上重現專案的 Poetry 虛擬環境

這也是非常常見的需求。

第一步當然是`git clone`專案，此時專案中已經有 Poetry 所需的必要資訊了——也就是`pyproject.toml`和`poetry.lock`。

你還缺少的僅僅是虛擬環境。如果是全新的主機，則還得先安裝、設定好 Poetry。

確定 Poetry 可正常使用後，移至專案目錄底下，依序執行指令：

1. `poetry env use python`：建立專案虛擬環境並使用。如果你懶得打這麼長的指令，直接`poetry shell`也是可以。此時我們會有一個「**空的**」虛擬環境。
2. `poetry install`：因為是舊專案，不需要`init`，會直接依`poetry.lock`記載的套件版本安裝到虛擬環境中！類似`npm install`。

### 四、我想要重建虛擬環境

在使用專案內虛擬環境方案，也就是`.venv`的前提下，想要刪除這個虛擬環境並加以重建，也不需要使用`poetry env remove python`指令了，因為會出錯。

還有更簡單暴力的方式，是什麼呢？——直接刪除`.venv`資料夾即可。

然後再`poetry env use python`或`poetry shell`建一個新的就好。

### 五、為什麼我不在 Docker 環境中使用 Poetry？

因為啟動容器後需要先安裝 Poetry 到全域，或打包一個帶有 Poetry 的 image，兩者都會**增加新的耦合與依賴**，我覺得並不妥當。

所幸 Poetry 依舊可以輸出`requirements.txt`，Docker 部署環境就繼續使用這個舊方案即可，而且 Poetry 本來主要就是用於「開發」時的套件管理，對部署差別不大。

### 六、我可以使用自己習慣的 virtualenv 嗎？

當然可以。

不過我本來也繼續使用`pyenv`的`virtualenv`，但兩者有時候也是會小小打架，後來還是索性用 Poetry 的虛擬環境就好。

一個專案對應一個虛擬環境，應該還是比較簡潔的做法，我的觀察啦！😎

------

## 結語：井然有序的複雜

總的來說，Poetry 是一款優秀的套件管理工具，但並不像 pip 那般簡單、好上手。

使用 Poetry 來管理專案的套件與虛擬環境，需要一定的學習成本，但帶來的效益還是相當可觀的，尤其在你希望能夠乾淨且安心地移除套件之際，可謂莫它莫屬。

所以，別再猶豫，從今天起，加入 Poetry 的行列吧！