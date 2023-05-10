## Sizers模組

出處：https://ithelp.ithome.com.tw/articles/10243685

### 前言

前面在使用backtrader的時候，沒有特別針對交易部位的計算作介紹。主要是因為想先簡化實作過程，快速寫完幾個簡單的策略。這篇就要來深入研究，當交易訊號產生的時候，怎麼樣使用backtrader的Sizers模組，撰寫我們要買賣多少部位，不管是all-in、每次買進固定股數...等等，都可以化成一行一行的程式碼，真的是非常神奇呢！

### 首先，看看document

之前看過很多人寫的Sizers範例，用法真的是千變萬化，所以我覺得要理解他到底有哪些用法，最快速的方式就是去看[document](https://www.backtrader.com/docu/sizers/sizers/)。

#### 回顧一下 Day10 - backtrader回測框架實作(一)均線交叉策略

```python
def next(self):
        # 帳戶沒有部位
        if not self.position:
            # 5ma往上穿越20ma
            if self.crossover > 0:
                # 印出買賣日期與價位
                self.log('BUY ' + ', Price: ' + str(self.dataopen[0]))
                # 使用開盤價買入標的
                self.buy(price=self.dataopen[0])
        # 5ma往下穿越20ma
        elif self.crossover < 0:
            # 印出買賣日期與價位
            self.log('SELL ' + ', Price: ' + str(self.dataopen[0]))
            # 使用開盤價賣出標的
            self.close(price=self.dataopen[0])
```

上面這段程式碼中，self.buy的參數只有指定price，其他都是使用預設參數，那麼預設的交易量是多少呢？得要看一下說明書：

```python
class SizerFix(SizerBase):
    params = (('stake', 1),)
```

上面表示：如果buy跟sell沒有指定size是多少，那就會是1單位。但是我們通常不會只有買賣1單位，所以就需要寫sizer。

### 如何使用Sizer

這邊就介紹兩個Sizer用法，一種是寫在回測函數內，另一個則是寫在策略函數內：

- **寫在回測函數(cerebro)內**

```python
cerebro = bt.Cerebro()
cerebro.addsizer(bt.sizers.SizerFix, stake=20)
```

這邊addsizer裡面就是指定買賣的size是固定的，每次交易都是20單位

- **寫在策略函數內**

> The Strategy class offers an API: setsizer and getsizer (and a property sizer) to manage the Sizer

上面這句話表示可以在Strategy裡面，用setsizer或getsizer來管理交易量，下面就以之前寫的sma cross解釋setsizer的方式：

```python
# sma cross strategy
class SmaCross(bt.Strategy):
    ...

    def __init__(self):
        # 均線交叉策略
        sma1 = bt.ind.SMA(period=self.p.ma_period_short)
        sma2 = bt.ind.SMA(period=self.p.ma_period_long)
        self.crossover = bt.ind.CrossOver(sma1, sma2)
        
        # 使用自訂的sizer函數，將帳上的錢all-in
        self.setsizer(sizer())
        
    ...
```

方法相當簡單，就是在init裡面寫setsizer，再定義一個sizer class就完成了。詳細的文件可以看官網的Size Development的部份，這邊就先用all-in法做解說，所謂all-in就是帳上有多少錢就買多少：

```python
# 計算交易部位
class sizer(bt.Sizer):
    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy:
            return math.floor(cash/data.open)
        else:
            return self.broker.getposition(data)
```

> Override the method _getsizing(self, comminfo, cash, data, isbuy)
> 意思就是可以用自己定義的交易量去覆蓋掉原本的method，而上面寫的cash / data.open，就是指用開盤價來計算帳上的cash可以買多少的量，再四捨五入後就是真正交易的量了。

**本篇總結**
那麼以上就是sizers的介紹，有了sizer，就可以寫各式各樣的交易量配置，資金運用會再更靈活一些，下一篇將介紹Observers，就是回測成果的觀測工具，請繼續收看囉！