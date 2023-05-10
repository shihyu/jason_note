

# 別再用 print 來 Debug 啦！來用 Python Debugger 吧！



## 前言

這幾年開發 Python 下來，發現不少人對於 debugger 其實還是有點陌生的。大部分在做除錯的時候，還是會用 print 或是 [Python Logging](https://www.icoding.co/2012/08/logging-html) 來印出程式的變數，或是理解目前程式碼進行的流程，藉此來確認自己程式的行為。在看完這篇文章之後，讀者可以學會如何透過 Python Debugger 來取代原本的 debugging 行為，你將會發現你的 debug 會更加的有效率。

## print 大法好！為什麼要用 debugger？

對於剛開始接觸 Python 的人來說，最常使用的 debug tool 應該就是 print 了。隨著對於 Python 越來越瞭解，可能會透過 [Python 的 logging module](https://www.icoding.co/2012/08/logging-html)，透過像是 `logging.debug` 之類的 code 來印出 debug message. 這樣看似沒問題，但是往往我們用 print 大法來 debug 的流程是這樣子的：

1. 印出某個變數的值 `var1`
2. 發現 `var1` 的變數跟預期不太一樣，但是 `var1` 的值又 depends on `var2`
3. 印出 `var2` 的值，重跑一次程式
4. 發現 `var2` 的變數跟預期不太一樣，但是 `var2` 的值又 depends on `var3` + `var4`
5. 持續下去直到找到問題為止

這來回幾次的過程當中，你會先花費大量的時間印出所有你想要的值，再從這些蛛絲馬跡當中尋找到你想要的資訊，推斷問題的所在。如果你的程式執行起來很方便就算了，但是當你的程式執行起來有些麻煩或是有些久的時候，你就會耗費大量的時間在不斷的修改程式上面。而 debugger 可以幫助你解決這個問題。

當你使用 debugger 的時候，你的除錯行為會變成如下：

1. 在你懷疑出問題的地方設定中斷點
2. 執行程式，遇到中斷點的時候停下來
3. 透過 debugger 的指令，來觀察你想要知道的變數值，或是一步一步的執行你的程式看看問題在哪裡
4. Bug 解掉了！移除中斷點

## pdb 基本指令

Python 就有內建 debugger [pdb](https://docs.python.org/3/library/pdb.html)，要使用 pdb 很簡單，有三種方式：

1. 不用修改原始程式碼的作法

```bash
python3 -m pdb file.py
```

1. 在需要插入中斷點的程式碼中插入 [breakpoint()](https://docs.python.org/3/library/functions.html#breakpoint) function (Python 3.7 之後支援)

Example.

```python
def bug_here(a):
	breakpoint()
  b = a + 3
	return b
```

1. 在需要插入中斷點的程式碼插入 `import pdb;pdb.set_trace()`

Example.

```python
def bug_here(a):
	import pdb;pdb.set_trace()
  b = a + 3
	return b
```

當你看到在 terminal 下面看到出現 `(Pdb)` 出現，就代表你成功的使用了 pdb.

以下是些比較常用的 pdb 指令：

- [b(reak)](https://docs.python.org/3/library/pdb.html#pdbcommand-break) – 添加 breakpoint
- [p](https://docs.python.org/3/library/pdb.html#pdbcommand-p) – 印出變數值
- [l(ist)](https://docs.python.org/3/library/pdb.html#pdbcommand-list) – 印出目前所在 function/frame上下 11 行的程式碼
- [ll (longlist)](https://docs.python.org/3/library/pdb.html#pdbcommand-ll) – 印出目前所在 function/frame 的所有程式碼
- 執行指令
  - [s(tep)](https://docs.python.org/3/library/pdb.html#pdbcommand-step) – 執行下一行程式碼，遇到執行 function 的時候，會進入 function 當中
  - [n(ext)](https://docs.python.org/3/library/pdb.html#pdbcommand-next) – 執行下一行程式碼，遇到執行 function 的時候，不會進入 function 中。
  - [r(eturn)](https://docs.python.org/3/library/pdb.html#pdbcommand-return) – 執行程式直到 function return
  - [c(ontinue)](https://docs.python.org/3/library/pdb.html#pdbcommand-continue) – 持續執行程式碼直到遇到下一個中斷點
  - [unt(il)](https://docs.python.org/3/library/pdb.html#pdbcommand-until) – 持續執行程式直到遇到某一行
- [whatis](https://docs.python.org/3/library/pdb.html#pdbcommand-whatis) – 印出 expression 的型別
- [interact](https://docs.python.org/3/library/pdb.html#pdbcommand-interact) – 啟動一個 Python 的 interpreter
- [w(here)](https://docs.python.org/3/library/pdb.html#pdbcommand-where) – 印出 stack track 狀態
- [q(uit)](https://docs.python.org/3/library/pdb.html#pdbcommand-quit) – 離開 pdb

其他關於 pdb 的指令可以參考 [pdb 官方文件](https://docs.python.org/3/library/pdb.html)有很清楚的說明。

## debugger 進階

Python 內建的 pdb 已經可以滿足不少基本需求，在瞭解 pdb 的基本之後，再介紹以下兩種會讓你除錯生產力更加提升的方法。

### ipdb

對於使用過 Python 一段時間的人，應該都會對 [IPython](https://ipython.org/) 印象深刻。當中提供的 autocomplete, syntax highlight 等功能都會讓我們生產力提升不少。[ipdb](https://pypi.org/project/ipdb/) 就是一個可以增強原本 pdb 功能，為 pdb 帶來跟 [IPython](https://ipython.org/) 一樣的體驗。

要使用 ipdb，首先先安裝

```bash
pip install ipdb
```

我們有幾種方式可以啟動 ipdb

- `python -m ipdb file.py`
- 在想要插入中斷點的地方輸入

```python
import ipdb
ipdb.set_trace()
```

- 同樣利用 Python 3.7 支援的 [breakpoint()](https://docs.python.org/3/library/functions.html#breakpoint)，並且在啟動的時候多設定環境變數

```bash
PYTHONBREAKPOINT=ipdb.set_trace
```

### 透過 IDE 來做 debug

如果你是 IDE 的使用者，那麼目前的 IDE 都有做了很好的整合，官方的說明文件或是網路上的 tutorial 已經很多了，以下附上一些 reference。

- PyCharm
  - https://www.youtube.com/watch?v=QJtWxm12Eo0
  - [Step 2. Debug your first Python application – Help | PyCharm](https://www.jetbrains.com/help/pycharm/debugging-your-first-python-application.html)
- vscode
  - [how to debug python code in visual studio code – YouTube](https://www.youtube.com/watch?v=jHNfzAUccBA)
  - [Debugging configurations for Python apps in Visual Studio Code](https://code.visualstudio.com/docs/python/debugging)

## 結論

學會使用 debugger 之後會讓你的生產力提升不少，當你下次在用 print 大法的時候，別忘記還有 debugger 可以用！