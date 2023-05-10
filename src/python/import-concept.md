# [Python] import 概念



# 基礎介紹

- package (套件/包) : 資料夾，含有 `__init__.py`
- module (模塊) : 檔案
- import 的方式有兩種 : 絕對路徑 / 相對路徑
- sys.modules : 是個 dictionary，用於存放已經 import 過的 modules
- sys.path : 是個 list，用於搜尋 import module 的各種路徑



# import 流程

雖然 import 的**方式**有兩種 : 絕對路徑 / 相對路徑
但是 import 的**流程**是相同的

```
import xxxModule
```

1. 檢查 `xxxModule` 是否存在於 `sys.modules`
2. 若存在，則直接從 `sys.modules` 取出使用即可
3. 若不存在，則依據 import 的**方式**來搜尋 `xxxModule.py` 的檔案位置
4. 接著生成 `xxxModule`
5. 再來放入 `sys.modules`
6. 最後執行 `xxxModule.py` 裡面的 source code (以剛生成的 `xxxModule` 作為 scope 來執行)



# syntax 比較

```python
# 絕對路徑
import xxxModule
from xxxModule import xxxMethod

# 相對路徑
from . import xxxModule # 同一層目錄
from .. import xxxModule # 上一層目錄
from ... import xxxModule # 上上層目錄
from .xxxModule import xxxMethod

# 錯誤寫法
import .xxxModule # . 只能出現在 from 後面 
```



# 絕對路徑

有了以上的概念後，接著我們利用範例來實際操作下 ([範例下載](https://github.com/hochun836/python_absolute_import))
為求簡單，這邊 import 的方式都先使用絕對路徑

- [基礎練習 1](https://blog.hochun836.com/2020/10/03/python/import-concept.html#基礎練習-1)
- [基礎練習 2](https://blog.hochun836.com/2020/10/03/python/import-concept.html#基礎練習-2)
- [基礎練習 3](https://blog.hochun836.com/2020/10/03/python/import-concept.html#基礎練習-3)
- [基礎練習 4](https://blog.hochun836.com/2020/10/03/python/import-concept.html#基礎練習-4)
- [基礎練習 5](https://blog.hochun836.com/2020/10/03/python/import-concept.html#基礎練習-5)



## 基礎練習 1

執行 `D:\hochun\example\python_absolute_import>python app1.py`

```python
# 檔案結構
python_absolute_import
│  app1.py
│
└─packageA
  │  moduleA.py
  │  __init__.py
  │
  └─packageB
      │  moduleB.py
      └─  __init__.py
```

```python
# packageA/__init__.py
print('& packageA')

# packageA/moduleA.py
print('& moduleA')

# packageA/packageB/__init__.py
print('& packageB')

# packageA/packageB/moduleB.py
print('& moduleB')
```

```python
# app1.py
import sys
for idx, path in enumerate(sys.path):
    print(f'sys.path[{idx}]: {path}')

print('========== phase1 ==========')
print('"packageA" in sys.modules:', 'packageA' in sys.modules)
print('"packageA.moduleA" in sys.modules:', 'packageA.moduleA' in sys.modules)
print('"packageA.packageB" in sys.modules:', 'packageA.packageB' in sys.modules)
print('"packageA.packageB.moduleB" in sys.modules:', 'packageA.packageB.moduleB' in sys.modules)

print('========== phase2 ==========')
from packageA.packageB import moduleB
print('"packageA" in sys.modules:', 'packageA' in sys.modules)
print('"packageA.moduleA" in sys.modules:', 'packageA.moduleA' in sys.modules)
print('"packageA.packageB" in sys.modules:', 'packageA.packageB' in sys.modules)
print('"packageA.packageB.moduleB" in sys.modules:', 'packageA.packageB.moduleB' in sys.modules)

print('========== phase3 ==========')
from packageA import moduleA
print('"packageA" in sys.modules:', 'packageA' in sys.modules)
print('"packageA.moduleA" in sys.modules:', 'packageA.moduleA' in sys.modules)
print('"packageA.packageB" in sys.modules:', 'packageA.packageB' in sys.modules)
print('"packageA.packageB.moduleB" in sys.modules:', 'packageA.packageB.moduleB' in sys.modules)

print('========== phase4 ==========')
import packageA
print('packageA:', packageA)
```

輸出

```sh
& app1.py
sys.path[0]: D:\hochun\example\python_absolute_import #sys.path[0] 是當前路徑
sys.path[1]: C:\ProgramData\Anaconda3\python38.zip
sys.path[2]: C:\ProgramData\Anaconda3\DLLs
sys.path[3]: C:\ProgramData\Anaconda3\lib
sys.path[4]: C:\ProgramData\Anaconda3
sys.path[5]: C:\ProgramData\Anaconda3\lib\site-packages
sys.path[6]: C:\ProgramData\Anaconda3\lib\site-packages\win32
sys.path[7]: C:\ProgramData\Anaconda3\lib\site-packages\win32\lib
sys.path[8]: C:\ProgramData\Anaconda3\lib\site-packages\Pythonwin
========== phase1 ==========
"packageA" in sys.modules: False
"packageA.moduleA" in sys.modules: False
"packageA.packageB" in sys.modules: False
"packageA.packageB.moduleB" in sys.modules: False
========== phase2 ==========
& packageA # from packageA.packageB import moduleB 先執行 packageA.py
& packageB # from packageA.packageB import moduleB 再執行 packageB.py
& moduleB # from packageA.packageB import moduleB 最後執行 moduleB.py
"packageA" in sys.modules: True # False 改變為 True
"packageA.moduleA" in sys.modules: False
"packageA.packageB" in sys.modules: True # False 改變為 True
"packageA.packageB.moduleB" in sys.modules: True # False 改變為 True
========== phase3 ==========
& moduleA # 由於 sys.modules 已經有了 packageA，所以不會再執行 packageA.py
"packageA" in sys.modules: True
"packageA.moduleA" in sys.modules: True # False 改變為 True
"packageA.packageB" in sys.modules: True
"packageA.packageB.moduleB" in sys.modules: True
========== phase4 ==========
packageA: <module 'packageA' from 'D:\hochun\example\python_absolute_import\packageA\__init__.py'>
```



說明

- ```plaintext
  from packageA.packageB import moduleB
  ```

  1. 檢查 `packageA` / `packageB` / `moduleB` 是否存在於 `sys.modules`
  2. 發現沒有，所以依據 import 的方式來搜尋 `packageA.py` / `packageB.py` / `moduleB.py` 的檔案位置
  3. 此處用的是絕對路徑，所以會利用 `sys.path` 來尋找檔案位置
  4. 有看到 `sys.path[0]` 就是根目錄嗎 ? 就是因為這個路徑，才找的到 `packageA.py` / `packageB.py` / `moduleB.py`
  5. 如果在 `sys.path` 中都找不到的話，就會出現 `ModuleNotFoundError`

- ```plaintext
  from packageA import moduleA
  ```

  1. 由於 `packageA` 已存在於 `sys.modules`，所以不會執行 `packageA.py`
  2. 但是 `moduleA` 還不存在於 `sys.modules`，所以會依據 import 的方式來搜尋 `moduleA.py` 的檔案位置
  3. 此處用的是絕對路徑，所以會利用 `sys.path` 來尋找檔案位置

- ```plaintext
  import packageA
  ```

  1. 經過上面的說明，很清楚知道 import 同樣的 package or module，只要 `sys.modules` 中還存在，就不會執行第二次

- ```plaintext
  print(packageA)
  ```

  1. 有注意到嗎 ? 輸出的結果是一個名叫 `packageA` 的 `module` from `__init__.py`



## 基礎練習 2

執行 `D:\hochun\example\python_absolute_import>python app2.py`

```python
# app2.py
print('& app2.py')

print('dir():', dir())

import sys
print('dir():', dir())

a = 101
print('a be loaded')

b = 102
print('b be loaded')

c = 103
print('c be loaded')

print('dir():', dir())
```

輸出

```python
& app2.py
dir(): ['__annotations__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__']
dir(): ['__annotations__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', 'sys'] # 增加 'sys'
a be loaded
b be loaded
c be loaded
dir(): ['__annotations__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', 'a', 'b', 'c', 'sys'] # 增加 'a', 'b', 'c'
```

觀察

1. import 之後，或是宣告一個變數之後，我們可以在 `dir()` 中看到增加的名稱

## 基礎練習 3

執行 `D:\hochun\example\python_absolute_import>python app3_1.py`

```python
# 檔案結構
python_absolute_import
│  app3_1.py
└─ app3_2.py
```

```python
# app3_1.py
print('& app3_1.py')

import sys

import app3_2

print('sys == app3_2.sys:', sys == app3_2.sys)
```

```python
# app3_2.py
print('& app3_2.py')

import sys
```

輸出

```python
& app3_1.py
& app3_2.py
sys == app3_2.sys: True # 兩者的 sys 是相同的
```

觀察

1. 不論在哪隻 module 中， `import sys` 後的 `sys` 是指向相同的記憶體位置
2. 所以，不論在哪隻 module 中，我們常用的 `sys.modules` / `sys.path` 也都會指向相同的記憶體位置



## 基礎練習 4

執行 `D:\hochun\example\python_absolute_import>python app4_1.py`

```python
# 檔案結構
python_absolute_import
│  app4_1.py
└─ app4_2.py
```

```python
# app4_1.py
print('& app4_1.py')

import sys

print('[in app4_1.py] "app4_1" in sys.modules:', 'app4_1' in sys.modules)
print('[in app4_1.py] "app4_2" in sys.modules:', 'app4_2' in sys.modules)

import app4_2

print('[in app4_1.py] "app4_1" in sys.modules:', 'app4_1' in sys.modules)
print('[in app4_1.py] "app4_2" in sys.modules:', 'app4_2' in sys.modules)
```

```python
# app4_2.py
print('& app4_2.py')

import sys

print('[in app4_2.py] "app4_1" in sys.modules:', 'app4_1' in sys.modules)
print('[in app4_2.py] "app4_2" in sys.modules:', 'app4_2' in sys.modules)
```

輸出

```python
& app4_1.py
[in app4_1.py] "app4_1" in sys.modules: False # 一開始都是 False
[in app4_1.py] "app4_2" in sys.modules: False # 一開始都是 False
& app4_2.py
[in app4_2.py] "app4_1" in sys.modules: False
[in app4_2.py] "app4_2" in sys.modules: True # False 變成 True，因為 import app4_2
[in app4_1.py] "app4_1" in sys.modules: False
[in app4_1.py] "app4_2" in sys.modules: True
```

觀察

1. `app4_1.py` 依賴於 `app4_2.py`
2. 想想看如果情況變成兩隻 module 互相依賴，那該怎麼辦 ? (別擔心，待下面範例解釋)



## 基礎練習 5

執行 `D:\hochun\example\python_absolute_import>python app5_1.py`

```python
# 檔案結構
python_absolute_import
│  app5_1.py
└─ app5_2.py
```

```python
# app5_1.py
print('& app5_1.py')

firstName = 'peter'

print('[in app5_1.py] before import app5_2.py')

# (A)
import app5_2

# (B)
# import app5_2
# print('[in app5_1.py] name:', firstName, app5_2.lastName)

# (C)
# from app5_2 import lastName
# print('[in app5_1.py] name:', firstName, lastName)
```

```python
# app5_2.py
print('& app5_2.py')

print('[in app5_2.py] before import app5_1.py')

import app5_1

lastName = 'kang'

print('[in app5_2.py] after import app5_1.py')
```

輸出

```python
# (A)
& app5_1.py
[in app5_1.py] before import app5_2.py
& app5_2.py
[in app5_2.py] before import app5_1.py
& app5_1.py
[in app5_1.py] before import app5_2.py
[in app5_2.py] after import app5_1.py
[in app5_2.py] name: peter kang
```

```python
# (B)
& app5_1.py
[in app5_1.py] before import app5_2.py
& app5_2.py
[in app5_2.py] before import app5_1.py
& app5_1.py
[in app5_1.py] before import app5_2.py # 在這之前都與 (A) 一致
Traceback (most recent call last):
  File "app5_1.py", line 14, in <module>
    import app5_2
  File "D:\hochun\example\python_absolute_import\app5_2.py", line 5, in <module>
    import app5_1
  File "D:\hochun\example\python_absolute_import\app5_1.py", line 15, in <module>
    print('[in app5_1.py] name:', firstName, app5_2.lastName)
AttributeError: partially initialized module 'app5_2' has no attribute 'lastName'
(most likely due to a circular import)
```

```python
# (C)
& app5_1.py
[in app5_1.py] before import app5_2.py
& app5_2.py
[in app5_2.py] before import app5_1.py
& app5_1.py
[in app5_1.py] before import app5_2.py # 在這之前都與 (A) 一致
Traceback (most recent call last):
  File "app5_1.py", line 18, in <module>
    from app5_2 import lastName
  File "D:\hochun\example\python_absolute_import\app5_2.py", line 5, in <module>
    import app5_1
  File "D:\hochun\example\python_absolute_import\app5_1.py", line 18, in <module>
    from app5_2 import lastName
ImportError: cannot import name 'lastName' from partially initialized module 'app5_2' (most likely due to a circular import) (D:\hochun\example\python_absolute_import\app5_2.py)
```

觀察

1. `app5_1.py` / `app5_2.py` 互相依賴
2. 依據 `app5_1.py` 不同的寫法 (A) / (B) / (C)，輸出結果也不同
3. (A) 不會報錯
4. (B) 報錯 `AttributeError`，因為在 `app5_2.py` 中， `lastName = 'kang'` 寫在 `import app5_1` 之後
5. (C) 報錯 `ImportError`，同理 (B)
6. 那如果將 `app5_2.py` 中的 `lastName = 'kang'` 寫在 `import app5_1` 之前，是不是就不會報錯了呢 ? (留給大家 try 看看)



# 相對路徑

複習下，在[import 流程](https://blog.hochun836.com/2020/10/03/python/import-concept.html#import-流程)中有提到，雖然 import 的**方式**有兩種，但是 import 的**流程**是相同的
前面學習完了 import 的流程與 import 方式之一的**絕對路徑**
接下來，讓我們把**相對路徑**也一併搞定吧 ! ([範例下載](https://github.com/hochun836/python_relative_import))

- [進階練習 1](https://blog.hochun836.com/2020/10/03/python/import-concept.html#進階練習-1)
- [進階練習 2-1](https://blog.hochun836.com/2020/10/03/python/import-concept.html#進階練習-2-1)
- [進階練習 2-2](https://blog.hochun836.com/2020/10/03/python/import-concept.html#進階練習-2-2)
- [進階練習 3](https://blog.hochun836.com/2020/10/03/python/import-concept.html#進階練習-3)

```python
# 檔案結構
python_relative_import
│
├─level1
│  │  __init__.py
│  │
│  ├─level2
│  │  │  app1.py
│  │  │  app2.py
│  │  │  __init__.py
│  │  │
│  │  ├─level3
│  │  │      app3.py
│  │  │      __init__.py
│  │  │
│  │  └─utils
│  │          tool.py
│  │          __init__.py
│  │
│  └─utils
│          tool.py
│          __init__.py
│
└─utils
        tool.py
        __init__.py
```

```python
# utils/__init__.py
print('& [utils] __init__.py')

# utils/tool.py
print('& [utils] tool.py')
name = 'chen'

# level1/__init__.py
print('& [level1] __init__.py')

# level1/utils/__init__.py
print('& [level1/utils] __init__.py')

# level1/utils/tool.py
print('& [level1/utils] tool.py')
name = 'bob'

# level1/level2/__init__.py
print('& [level1/level2] __init__.py')

# level1/level2/utils/__init__.py
print('& [level1/level2/utils] __init__.py')

# level1/level2/utils/tool.py
print('& [level1/level2/utils] tool.py')
name = 'peter'

# level1/level2/level3/__init__.py
print('& [level1/level2/level3] __init__.py')
```

## 進階練習 1

執行 `D:\hochun\example\python_relative_import\level1\level2>python app1.py`

```python
# app1.py
print('& [level1/level2] app1.py')

print('__name__:', __name__)
print('__package__:', __package__)

import sys
sys.path.append('../..') # 增加新的 path
sys.path = sys.path[1:] # 刪除 sys.path[0]

from utils.tool import name
print(name)
```

輸出

```python
& [level1/level2] app1.py
__name__: __main__
__package__: None
& [utils] __init__.py
& [utils] tool.py
chen # in utils/tool.py
```

觀察

1. 當下路徑為 `D:\hochun\example\python_relative_import\level1\level2`
2. `sys.path.append('../..')`，增加**上上層路徑**到 `sys.path`
3. `sys.path = sys.path[1:]`，刪除 `sys.path[0]` **(當層路徑)**

坑

1. 這個範例其實還是**絕對路徑**，所以尋找 module 會利用 `sys.path`
2. 若改為執行 `D:\hochun\example\python_relative_import>python level1/level2/app1.py`，則會報錯 `ModuleNotFoundError: No module named 'utils'`，因為我們修改了 `sys.path`，進而造成在 `sys.path` 中找不到 module `utils`，所以才會報錯



## 進階練習 2-1

執行 `D:\hochun\example\python_relative_import\level1\level2>python app2.py`

```python
# app2.py
print('& [level1/level2] app2.py')

import sys

print('__name__:', __name__)
print('__package__:', __package__)

from ..utils import tool # 相對路徑
```

輸出

```python
& [level1/level2] app2.py
__name__: __main__ # 關鍵
__package__: None # 關鍵
Traceback (most recent call last):
  File "app2.py", line 8, in <module>
    from ..utils import tool
ImportError: attempted relative import with no known parent package
```

觀察

1. 當下路徑為 `D:\hochun\example\python_relative_import\level1\level2`
2. `__name__` 為 `__main__`
3. `__package__` 為 `None`
4. `from ..utils import tool` 為 import 方式的**相對路徑**

坑

1. 若 import 方式為**相對路徑**，則利用的不是 `sys.path`，而是 `__name__` / `__package__`
2. 因為 `__package__` 為 `None`，這被視為**最上層路徑**，所以無法再用 `from ..utils import tool`，即便改成 `from .utils import tool` 也一樣會報錯
3. 換句話說，若 module 中有寫到相對路徑，則不能直接下 `python` 指令去 run 該程式，除非使用 `python -m` (如下)



## 進階練習 2-2

執行 `D:\hochun\example\python_relative_import>python -m level1.level2.app2`

輸出

```python
& [level1] __init__.py
& [level1/level2] __init__.py
& [level1/level2] app2.py
__name__: __main__
__package__: level1.level2 # 關鍵，不是 None 了
& [level1/utils] __init__.py
& [level1/utils] tool.py
```

觀察

1. 當下路徑為 `D:\hochun\example\python_relative_import`
2. `python -m` 後面跟的是 `level1.level2.app2` 而非 `level1/level2/app2.py`
3. `__package__` 為 `level1.level2`，因為如此 import 方式的**相對路徑**才能做到**相對**的作用

經由上述解釋後，現在的你應該能說出以下兩者的差異吧 !

1. `D:\hochun\example\python_relative_import>python -m level1.level2.app2`
2. `D:\hochun\example\python_relative_import>python level1/level2/app2.py`

## 進階練習 3

```python
# app3.py
print('& [level1/level2/level3] app3.py')

import sys

print('__name__:', __name__)
print('__package__:', __package__)

from ...utils.tool import name

print(name)
```

最後這個練習就讓大家動手玩玩看囉

# 參考文章

1. [Python 的 Import 陷阱](https://medium.com/pyladies-taiwan/python-的-import-陷阱-3538e74f57e3)
2. [理解Python的 relative 和 absolute import](https://carsonwah.github.io/15213187969322.html)



# Python-import導入上級目錄文件

假設有如下目錄結構：

```text
-- dir0
　　| file1.py
　　| file2.py
　　| dir3
　　　| file3.py
　　| dir4
　　　| file4.py
```

dir0文件夾下有file1.py、file2.py兩個文件和dir3、dir4兩個子文件夾，dir3中有file3.py文件，dir4中有file4.py文件。

## 1.導入同級模塊

python導入同級模塊（在同一個文件夾中的py文件）直接導入即可。

```python
import xxx
```

如在file1.py中想導入file2.py，注意無需加後綴".py"：

```python
import file2
# 使用file2中函數時需加上前綴"file2."，即：
# file2.fuction_name()
```

## 2.導入下級模塊

導入下級目錄模塊也很容易，需在下級目錄中新建一個空白的__init__.py文件再導入：

```python
from dirname import xxx
```

如在file1.py中想導入dir3下的file3.py，首先要在dir3中新建一個空白的__init*__*.py文件。

```text
-- dir0
　　| file1.py
　　| file2.py
　　| dir3
　　　| __init__.py
　　　| file3.py
　　| dir4
　　　| file4.py
```

再使用如下語句：

```python
# plan A
from dir3 import file3
```

或是

```python
# plan B
import dir3.file3
# import dir3.file3 as df3
```

但使用第二種方式則下文需要一直帶著路徑dir3書寫，較為累贅，建議可以另起一個別名。

## 3.導入上級模塊

要導入上級目錄下模塊，可以使用sys.path： 　

```python
import sys 
sys.path.append("..") 
import xxx
```

如在file4.py中想引入import上級目錄下的file1.py：

```python
import sys 
sys.path.append("..") 
import file1
```

**sys.path的作用：**當使用import語句導入模塊時，解釋器會搜索當前模塊所在目錄以及sys.path指定的路徑去找需要import的模塊，所以這裡是直接把上級目錄加到了sys.path裡。

**“..”的含義：**等同於linux裡的‘..’，表示當前工作目錄的上級目錄。實際上python中的‘.’也和linux中一致，表示當前目錄。

## 4.導入隔壁文件夾下的模塊

如在file4.py中想引入import在dir3目錄下的file3.py。

這其實是前面兩個操作的組合，其思路本質上是將上級目錄加到sys.path裡，再按照對下級目錄模塊的方式導入。

同樣需要被引文件夾也就是dir3下有空的__init__.py文件。

```text
-- dir
　　| file1.py
　　| file2.py
　　| dir3
　　　| __init__.py
　　　| file3.py
　　| dir4
　　　| file4.py
```

同時也要將上級目錄加到sys.path裡：

```python
import sys
sys.path.append("..")
from dir3 import file3
```

## 5.常見錯誤及import原理：

在使用直接從上級目錄引入模塊的操作時：

```python
from .. import xxx
```

經常會報錯:

```python3
ValueError: attempted relative import beyond top-level package
```

這是由於相對導入時，文件夾實質上充當的是package，也就是包的角色（比如我們常用的numpy、pandas都是包）。如果python解釋器沒有認同該文件夾是package，那麼這就是一個普通的文件夾，無法實現相對導入。

文件夾作為package需要滿足如下兩個條件：

1. 文件夾中必須存在有__init__.py文件，可以為空。
2. 不能作為頂層模塊來執行該文件夾中的py文件。