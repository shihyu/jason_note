# 神奇又美好的 Decorator ，嗷嗚！


# 【導言】

由於 Python 的基本語法過於簡潔，所以大部分的設計與技巧都會為了強化其架構的依賴性與開發性，而讓 Python 的語法變得比原先的繁複。

這次要介紹一個少數「化繁為簡」的語法 — — Decorator ！

Decorator 本身的概念非常簡單，但簡單語法與使用背後還有一個**小魔王就是 Closure**！不過 Closure 這個部份較為複雜，不適合一併放入這篇文章，所以會在之後的文章內介紹其原理！**今天大家就著重在 Decorator 如何使用，以及 Decorator 使用時機吧**！



# 【本文章節】

- 【壹、什麼是 Decorator ?!】
- 【貳、Decorator 的 Syntax Candy — @小老鼠】
- 【參、Decorator 的有序性】
- 【肆、Decorator 如何帶參數 ?】
- 【伍、Decorator 也可以是 Class !?】



# 【開發環境與建議先備知識】

**OS** *Ubuntu 16.04*

**Python** *3.6*

**Required Knowledge**

- First Class Function (一級函數)
- 熟悉 Python function 概念

# 【壹、什麼是 Decorator ?!】

長話不如直接看一下範例 code ：



```python
def print_func_name(func):
    def wrap():
        print("Now use function '{}'".format(func.__name__))
        func()
    return wrap


def dog_bark():
    print("Bark !!!")


def cat_miaow():
    print("Miaow ~~~")


if __name__ == "__main__":
    print_func_name(dog_bark)()
    # > Now use function 'dog_bark'
    # > Bark !!!

    print_func_name(cat_miaow)()
    # > Now use function 'cat_miaow'
    # > Miaow ~~~
```

sample-1 https://gist.github.com/JackInTaiwan/8779504fbcbd0d8420e9996fab3c8641

以上的範例可以看到我們有兩個主要的 functions： `dog_bark()` 和 `cat_miaow()` 要執行，但兩個 functions 都有一個共同要做的事情，都想要先 print 出自己的 function name，所以對於共同要做的事情我們抽出來用 function `print_func_name(func)` 來完成。

邏輯是這樣的， `print_func_name(func)` 會把傳入的 function 再利用一個我們命為 `warp()` 的內部 function「加工修飾加上一些我們要的功能」，然後在用 `return wrap` 吐出修飾過的 function `wrap` ，如此就完成「修飾」的任務啦！最後記得在 `print_func_name(dog_bark)` 和 `print_func_name(cat_miaow)` 只會 return function 本身，所以要在後面加上 `()` 來 call function 喔！！

額外要注意，**在 Python 中，function 的地位和 C++、Java等不同，是屬於 ”First-class Citizen” (一等公民)，故稱作 ”First-class function” (一級函數、頭等函數)。**簡單來說，就是 function 也可以當成參數傳遞並執行。另外，JavaScript 等語言也都是採用 First-class Function 的概念喔！

以上的範例，基本上是一個「藉由抽出相同或相似邏輯來簡化」的簡單到不行的範例（當然現實世界中的例子可複雜得想放棄…）。但這麼簡單的一件事情，我們就稱 function `print_func_name(func)` 是一個 「Decorator」(裝飾器)！

# 【貳、Decorator 的 Syntax Candy — @小老鼠】

在上一節中明示了什麼叫做 Decorator，這裡就要介紹它的 syntax candy — @小老鼠！

這邊簡單快速補充一下，syntax candy（語法糖、語法糖衣）就是讓語法簡化的語法，可能原先要寫數十行的 code，若該語言有提供對應的 syntax candy，很可能寫個幾行或是寫個符號上去，就可以輕鬆完成了。這在多數語言中都是極度常見的語法！

補充完畢。老師，範例請下（音樂聲起）：

```python
def print_func_name(func):
    def warp():
        print("Now use function '{}'".format(func.__name__))
        func()
    return warp


@print_func_name
def dog_bark():
    print("Bark !!!")


@print_func_name
def cat_miaow():
    print("Miaow ~~~")


if __name__ == "__main__":
    dog_bark()
    # > Now use function 'dog_bark'
    # > Bark !!!

    cat_miaow()
    # > Now use function 'cat_miaow'
    # > Miaow ~~~
```


sample-2 https://gist.github.com/JackInTaiwan/8c27ec000a5ab6f8f4ad124f9b5d9f5e

上面的範例中，我們在兩個主要的 functions 前面加上 decorator `@print_func_name` ，如此就發揮了 syntax candy 化簡語法的功效，用更簡單的語法來完成一模一樣的事情囉！

或許有沒有使用 syntax candy 對於這兩份範例 code 差不了幾行，但這是因為範例 code 太簡略，而且 function 都只被 call 過一次，所以才會感受不出來。syntax candy 是真實讓人愛不釋手的！

其實對於大部分的讀者來說，最先接觸到 Decorator 的很可能是它的 syntax candy，而不是在上一節【壹、什麼是 Decorator ?!】範例 code 中的形式。不過這地方不需要拘泥於人們口中所說的 decorator 是指原先的形式，還是它的 syntax candy，因為本質真的都一樣啦！所以本篇文章除非特別強調，否則都是指 syntax candy 形式的 decorator 。

# 【參、Decorator 的有序性】

如果之前有閱讀過 [Python進階技巧 (2) — Static/Class/Abstract Methods之實現](https://medium.com/p/1e3b3998bccf/edit) 的讀者，可能會記得（應該會有人記得的對吧？！）我提醒過 decorator 彼此間是有順序關係的，要額外注意！

來，老師下音樂，哦不，是下範例：

```python
def print_func_name(func):
    def warp_1():
        print("Now use function '{}'".format(func.__name__))
        func()
    return warp_1


def print_time(func):
    import time
    def warp_2():
        print("Now the Unix time is {}".format(int(time.time())))
        func()
    return warp_2


@print_func_name
@print_time
def dog_bark():
    print("Bark !!!")



if __name__ == "__main__":
    dog_bark()
    # > Now use function 'warp_2'
    # > Now the Unix time is 1541239747
    # > Bark !!!
```


sample-3 https://gist.github.com/JackInTaiwan/15ebaa7abe6312ae12215bf56b6f2d5f

這裡會有一咪咪的複雜，大家要專心跟著 code 的順序看過一遍喔！

**decorators 多層的話是採 ”recursive” 的方式處理，如果一個 function 有兩個以上的 decorators ，邏輯上則會先合併「最靠近」的 decorator 吐出新的 function 再由上面一個的 decorator 吃進去！**

所以 `dog_bark()` 會先被 `@print_time` 吃進去，然後吐出一個叫做 `wrap_2` 的function，而這個 `warp_2` function 又會被 `@print_func_name` 吃進去，吐出一個叫做 `wrap_1` 的 function。

所以最後執行的結果順序是先 print `Now use function 'wrap_2'` 再 print `Now the Unix time is 1541239747` 。而且你會發現由於最外層的 `@print_func_name` 真正吃進去的 function 是已經被 `@print_time` 修飾過的 function，所以 print 的是`Now use function 'wrap_2'` 而不是 `Now use function 'dog_bark'` ！！

再來一個範例，檢驗大家是不是有跟上了～建議大家看完 code 先在心裡寫好答案再看結果。

下一段範例：

```python
def print_func_name(func):
    def warp_1():
        print("Now use function '{}'".format(func.__name__))
        func()
    return warp_1


def print_time(func):
    import time
    def warp_2():
        print("Now the Unix time is {}".format(int(time.time())))
        func()
    return warp_2


@print_func_name
@print_time
def dog_bark():
    print("Bark !!!")


@print_time
@print_func_name
def cat_miaow():
    print("Miaow !!!")


if __name__ == "__main__":
    dog_bark()
    # > Now use function 'warp_2'
    # > Now the Unix time is 1541239747
    # > Bark !!!

    cat_miaow()
    # > Now the Unix time is 1541239747
    # > Now use function 'cat_miaow'
    # > Miaow !!!
```


sample-4 https://gist.github.com/JackInTaiwan/41ded88d4c8c13c53c56f4455534e71b

和上一個範例（sample-3 ）相同，只是多了 `cat_miaow()` 而已。這次 `cat_miaow()` 上的 decorators 順序和 `dog_bark()` 的順序是相反的。

範例結果顯示，call `cat_miaow()` 會先 print `Now the Unix time is 1541239747` 再 print `Now use function'cat_miaow'` 最後才 print 主要 function 的 `Miaow !!!` 。

如果結果和你所想都完全符合，那恭喜你順利瞭解 decorator 的順序性問題惹！！！

# 【肆、Decorator 如何帶參數 ?】

除了上面最簡單的用法之外，還可以在 decorator 處傳入參數，非常靈活好用！

請看以下範例：

```python
import time



def print_func_name(time):
    def decorator(func):
        def wrap():
            print("Now use function '{}'".format(func.__name__))
            print("Now Unix time is {}.".format(int(time)))
            func()
        return wrap
    return decorator


@print_func_name(time=(time.time()))
def dog_bark():
    print("Bark !!!")



if __name__ == "__main__":
    dog_bark()
    # > Now use function 'dog_bark'
    # > Now Unix time is 1639491313.
    # > Bark !!!
```


sample-5 https://gist.github.com/JackInTaiwan/3fda507a8803d4d30a9a0f13df834f9c

從上面的範例可以知道要讓 decorator 傳入參數，只需要改成 `@print_func_name(param=param_variable)` 形式即可。此處可用 arguments 的形式也可以用 key arguments 的形式傳入參數。

值得注意的是，這種 decorator 帶參的寫法：function 內還有 function，且呈現 recursive 的對稱形式。這種形式就和 “Closure” 有關，之後的文章會詳細解說，這邊先不多加說明。第一層 `def print_func_name(time)` 是用來解析 decorator 傳入的參數的，第二層 `def decorator(func)` 是吃進主要要修飾的function，和前面的範例一樣。

**所以這個寫法的結論是：把原本的 code 外面多加一層用來傳入 decorator 的參數。**

# 【伍、Decorator 也可以是 Class !?】

Decorator 除了有 function decorator ，也有 class decorator！畢竟 function 和 class 在 Python 裡頭都屬於 objects 呀！

再勞煩客倌看一回範例：

```python
class Dog:
    def __init__(self, func):
        self.age = 10
        self.talent = func

    def bark(self):
        print("Bark !!!")

@Dog
def dog_can_pee():
    print("I can pee very hard......")



if __name__ == "__main__":
    dog = dog_can_pee

    print(dog.age)
    # > 10

    dog.bark()
    # > Bark !!!

    dog.talent()
    # > I can pee very hard......
```

sample-6 https://gist.github.com/JackInTaiwan/6f70279c19ed337a58c875f8f2f75cae

由上述範例可以得知，當我們的 decorator 是一個 class decorator 時，要傳入的 function 主體 `dog_can_pee` 就會從 class 裡頭的 `__init__` initializer 被吃進去，然後執行你想操作的動作：在這個例子裡，我將傳入的 function `dog_can_pee` 以 assign`self.talent` 的方式宣告為 class 的 instance method。

**這是一個非常重要、靈活而優雅的技巧，將 function** `**dog_can_pee**` **「封裝」到 class** `**Dog**` **的一種寫法。**

延續這個例子，再稍微完整一點的示範，為什麼這個寫法非常優雅：

```python
class Dog:
    def __init__(self, func):
        self.talent = func

    def bark(self):
        print("Bark !!!")


@Dog
def dog_can_pee():
    print("I can pee very hard......")


@Dog
def dog_can_jump():
    print("I can jump uselessly QQQ")


@Dog
def dog_can_poo():
    print("I can poo like a super pooping machine!")



if __name__ == "__main__":
    dog_1 = dog_can_pee
    dog_1.talent()
    # > I can pee very hard......

    dog_2 = dog_can_jump
    dog_2.talent()
    # > I can jump uselessly QQQ

    dog_3 = dog_can_poo
    dog_3.talent()
    # > I can poo like a super pooping machine!
```


sample-7 https://gist.github.com/JackInTaiwan/4557776e4d04a398258d19b5bab4ef08

這個例子透過使用 class decorator 把不同的 function 封裝到這個原本的 class裡頭了。所以 `dog_1，` `dog_2` 和`dog_3` 這三隻狗明明都是 class `Dog` 會的才藝卻都不同！

達到同樣效果的寫法有很多種，其中一種是利用 class 繼承的方式達成，**不過如果在此處使用 class 繼承可能會過於冗餘、臃種且擴充性低，用簡潔的 decorator 反而有簡單、重複率低且擴充高的優點！**

# 【結語】

Decorator 被大量廣泛的使用在各方 library/package 中，具有幾個最主要的優點：

- 靈活度高
- 易讀性高
- 協助封裝效果好
- 程式碼重複率低/簡潔度高

有於篇幅有限，只能提供非常簡單的例子讓大家小酌一下，**decorator 如果大家願意多花點時間結合各種寫法，相信大家一定會更能感受除了上面簡單的範例以外，它帶來的各種優點！**

另外， decorator 中會使用到 closure ，這是一個非常重要的概念，會在下一篇文章中解說，大家稍待一會兒！

# 【飯後餐點】

最後附上一些延伸相關資料。

- [First-class function on Wiki](https://zh.wikipedia.org/wiki/頭等函數)
- [理解 Python 裝飾器看這一篇就夠了](https://foofish.net/python-decorator.html)

如果你也喜歡我們的文章，幫我們動動手部肌肉，按下掌聲Clap，讓我們有動力繼續煮下一頓料理！
