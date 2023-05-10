# 理解 Python 裝飾器看這一篇就夠了

講 Python 裝飾器前，我想先舉個例子，雖有點汙，但跟裝飾器這個話題很貼切。

每個人都有的內褲主要功能是用來遮羞，但是到了冬天它沒法為我們防風禦寒，咋辦？我們想到的一個辦法就是把內褲改造一下，讓它變得更厚更長，這樣一來，它不僅有遮羞功能，還能提供保暖，不過有個問題，這個內褲被我們改造成了長褲後，雖然還有遮羞功能，但本質上它不再是一條真正的內褲了。於是聰明的人們發明長褲，在不影響內褲的前提下，直接把長褲套在了內褲外面，這樣內褲還是內褲，有了長褲後寶寶再也不冷了。裝飾器就像我們這裡說的長褲，在不影響內褲作用的前提下，給我們的身子提供了保暖的功效。

談裝飾器前，還要先要明白一件事，Python 中的函數和 Java、C++不太一樣，Python 中的函數可以像普通變量一樣當做參數傳遞給另外一個函數，例如：

```python
def foo():
    print("foo")

def bar(func):
    func()

bar(foo)
```

正式回到我們的主題。裝飾器本質上是一個 Python 函數或類，它可以讓其他函數或類在不需要做任何代碼修改的前提下增加額外功能，裝飾器的返回值也是一個函數/類對象。它經常用於有切面需求的場景，比如：插入日誌、性能測試、事務處理、緩存、權限校驗等場景，裝飾器是解決這類問題的絕佳設計。有了裝飾器，我們就可以抽離出大量與函數功能本身無關的雷同代碼到裝飾器中並繼續重用。概括的講，裝飾器的作用就是為已經存在的對象添加額外的功能。

先來看一個簡單例子，雖然實際代碼可能比這復雜很多：

```python
def foo():
    print('i am foo')
```

現在有一個新的需求，希望可以記錄下函數的執行日誌，於是在代碼中添加日誌代碼：

```python
def foo():
    print('i am foo')
    logging.info("foo is running")
```

如果函數 bar()、bar2() 也有類似的需求，怎麼做？再寫一個 logging 在 bar 函數裡？這樣就造成大量雷同的代碼，為了減少重復寫代碼，我們可以這樣做，重新定義一個新的函數：專門處理日誌 ，日誌處理完之後再執行真正的業務代碼

```python
def use_logging(func):
    logging.warn("%s is running" % func.__name__)
    func()

def foo():
    print('i am foo')

use_logging(foo)
```

這樣做邏輯上是沒問題的，功能是實現了，但是我們調用的時候不再是調用真正的業務邏輯 foo 函數，而是換成了 use_logging 函數，這就破壞了原有的代碼結構， 現在我們不得不每次都要把原來的那個 foo 函數作為參數傳遞給 use_logging 函數，那麼有沒有更好的方式的呢？當然有，答案就是裝飾器。

### 簡單裝飾器

```python
def use_logging(func):

    def wrapper():
        logging.warn("%s is running" % func.__name__)
        return func()   # 把 foo 當做參數傳遞進來時，執行func()就相當於執行foo()
    return wrapper

def foo():
    print('i am foo')

foo = use_logging(foo)  # 因為裝飾器 use_logging(foo) 返回的時函數對象 wrapper，這條語句相當於  foo = wrapper
foo()                   # 執行foo()就相當於執行 wrapper()
```

use_logging 就是一個裝飾器，它一個普通的函數，它把執行真正業務邏輯的函數 func 包裹在其中，看起來像 foo 被 use_logging 裝飾了一樣，use_logging 返回的也是一個函數，這個函數的名字叫 wrapper。在這個例子中，函數進入和退出時 ，被稱為一個橫切面，這種編程方式被稱為面向切面的編程。

### @ 語法糖

如果你接觸 Python 有一段時間了的話，想必你對 @ 符號一定不陌生了，沒錯 @ 符號就是裝飾器的語法糖，它放在函數開始定義的地方，這樣就可以省略最後一步再次賦值的操作。

```python
def use_logging(func):

    def wrapper():
        logging.warn("%s is running" % func.__name__)
        return func()
    return wrapper

@use_logging
def foo():
    print("i am foo")

foo()
```

如上所示，有了 @ ，我們就可以省去`foo = use_logging(foo)`這一句了，直接調用 foo() 即可得到想要的結果。你們看到了沒有，foo() 函數不需要做任何修改，只需在定義的地方加上裝飾器，調用的時候還是和以前一樣，如果我們有其他的類似函數，我們可以繼續調用裝飾器來修飾函數，而不用重復修改函數或者增加新的封裝。這樣，我們就提高了程序的可重復利用性，並增加了程序的可讀性。

裝飾器在 Python 使用如此方便都要歸因於 Python 的函數能像普通的對像一樣能作為參數傳遞給其他函數，可以被賦值給其他變量，可以作為返回值，可以被定義在另外一個函數內。

### *args、**kwargs

可能有人問，如果我的業務邏輯函數 foo 需要參數怎麼辦？比如：

```python
def foo(name):
    print("i am %s" % name)
```

我們可以在定義 wrapper 函數的時候指定參數：

```python
def wrapper(name):
        logging.warn("%s is running" % func.__name__)
        return func(name)
    return wrapper
```

這樣 foo 函數定義的參數就可以定義在 wrapper 函數中。這時，又有人要問了，如果 foo 函數接收兩個參數呢？三個參數呢？更有甚者，我可能傳很多個。當裝飾器不知道 foo 到底有多少個參數時，我們可以用 *args 來代替：

```python
def wrapper(*args):
        logging.warn("%s is running" % func.__name__)
        return func(*args)
    return wrapper
```

如此一來，甭管 foo 定義了多少個參數，我都可以完整地傳遞到 func 中去。這樣就不影響 foo 的業務邏輯了。這時還有讀者會問，如果 foo 函數還定義了一些關鍵字參數呢？比如：

```python
def foo(name, age=None, height=None):
    print("I am %s, age %s, height %s" % (name, age, height))
```

這時，你就可以把 wrapper 函數指定關鍵字函數：

```python
def wrapper(*args, **kwargs):
        # args是一個數組，kwargs一個字典
        logging.warn("%s is running" % func.__name__)
        return func(*args, **kwargs)
    return wrapper
```

### 帶參數的裝飾器

裝飾器還有更大的靈活性，例如帶參數的裝飾器，在上面的裝飾器調用中，該裝飾器接收唯一的參數就是執行業務的函數 foo 。裝飾器的語法允許我們在調用時，提供其它參數，比如`@decorator(a)`。這樣，就為裝飾器的編寫和使用提供了更大的靈活性。比如，我們可以在裝飾器中指定日誌的等級，因為不同業務函數可能需要的日誌級別是不一樣的。

```python
def use_logging(level):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if level == "warn":
                logging.warn("%s is running" % func.__name__)
            elif level == "info":
                logging.info("%s is running" % func.__name__)
            return func(*args)
        return wrapper

    return decorator

@use_logging(level="warn")
def foo(name='foo'):
    print("i am %s" % name)

foo()
```

上面的 use_logging 是允許帶參數的裝飾器。它實際上是對原有裝飾器的一個函數封裝，並返回一個裝飾器。我們可以將它理解為一個含有參數的閉包。當我 們使用`@use_logging(level="warn")`調用的時候，Python 能夠發現這一層的封裝，並把參數傳遞到裝飾器的環境中。

```python
@use_logging(level="warn")`等價於`@decorator
```

### 類裝飾器

沒錯，裝飾器不僅可以是函數，還可以是類，相比函數裝飾器，類裝飾器具有靈活度大、高內聚、封裝性等優點。使用類裝飾器主要依靠類的`__call__`方法，當使用 @ 形式將裝飾器附加到函數上時，就會調用此方法。

```python
class Foo(object):
    def __init__(self, func):
        self._func = func

    def __call__(self):
        print ('class decorator runing')
        self._func()
        print ('class decorator ending')

@Foo
def bar():
    print ('bar')

bar()
```

### functools.wraps

使用裝飾器極大地復用了代碼，但是他有一個缺點就是原函數的元信息不見了，比如函數的`docstring`、`__name__`、參數列表，先看例子：

```python
# 裝飾器
def logged(func):
    def with_logging(*args, **kwargs):
        print func.__name__      # 輸出 'with_logging'
        print func.__doc__       # 輸出 None
        return func(*args, **kwargs)
    return with_logging

# 函數
@logged
def f(x):
   """does some math"""
   return x + x * x

logged(f)
```

不難發現，函數 f 被`with_logging`取代了，當然它的`docstring`，`__name__`就是變成了`with_logging`函數的信息了。好在我們有`functools.wraps`，`wraps`本身也是一個裝飾器，它能把原函數的元信息拷貝到裝飾器裡面的 func 函數中，這使得裝飾器裡面的 func 函數也有和原函數 foo 一樣的元信息了。

```python
from functools import wraps
def logged(func):
    @wraps(func)
    def with_logging(*args, **kwargs):
        print func.__name__      # 輸出 'f'
        print func.__doc__       # 輸出 'does some math'
        return func(*args, **kwargs)
    return with_logging

@logged
def f(x):
   """does some math"""
   return x + x * x
```

### 裝飾器順序

一個函數還可以同時定義多個裝飾器，比如：

```python
@a
@b
@c
def f ():
    pass
```

它的執行順序是從裡到外，最先調用最裡層的裝飾器，最後調用最外層的裝飾器，它等效於

```python
f = a(b(c(f)))
```