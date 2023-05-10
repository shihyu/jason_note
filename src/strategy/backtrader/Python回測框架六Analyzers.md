# Python 回測框架（六）Analyzers

出處：https://stockbuzzai.wordpress.com/2019/07/29/python-%e5%9b%9e%e6%b8%ac%e6%a1%86%e6%9e%b6%ef%bc%88%e5%85%ad%ef%bc%89analyzers/



在跑完策略回測之後，只看淨值曲線圖通常是很難確實分析策略的優劣以及缺失之處。因此 Backtrader 提供了 Analyzers 這組工具來產生一些分析的數據，協助使用者來優化他們的策略。我們先來看下面這段程式碼：

```python
from datetime import datetime
import backtrader
import math
 
 
class AllSizer(backtrader.Sizer):
    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy:
            return math.floor(cash/data.high)
        else:
            return self.broker.getposition(data)
 
 
class SmaCross(backtrader.SignalStrategy):
    def __init__(self):
        sma10 = backtrader.ind.SMA(period=10)
        sma30 = backtrader.ind.SMA(period=30)
        crossover = backtrader.ind.CrossOver(sma10, sma30)
        self.signal_add(backtrader.SIGNAL_LONG, crossover)
 
        self.setsizer(AllSizer())
 
 
cerebro = backtrader.Cerebro()
data = backtrader.feeds.YahooFinanceData(dataname='MSFT',
                                         fromdate=datetime(2011, 1, 1),
                                         todate=datetime(2012, 12, 31))
  
cerebro.adddata(data)
cerebro.addstrategy(SmaCross)
cerebro.addanalyzer(backtrader.analyzers.SharpeRatio, _name = 'SR', timeframe=backtrader.TimeFrame.Years)
results = cerebro.run()
print('Sharpe Ratio:', results[0].analyzers.SR.get_analysis()) 
```

### **分析工具：SharpeRatio, DrawDown, TimeReturn**

這是一個簡單策略，我們根據 10 日均線和 30 日均線的狀態來決定買賣。在這裡我們想要關注夏普比率的資訊，因此我們添加了下列的程式碼：

```python
cerebro.addanalyzer(backtrader.analyzers.SharpeRatio, _name = 'SR', timeframe=backtrader.TimeFrame.Years)
results = cerebro.run()
print('Sharpe Ratio:', results[0].analyzers.SR.get_analysis()) 
```

我們新增了一個 Sharpe Ratio 的 Analyzer，名字為 **SR**。同時我們利用 timeframe=backtrader.TimeFrame.Years 把分析的時間單位設定為年。

接著利用 cerebro.run() 來執行模擬，並用 results 來接 cerebro 回傳的結果。因為我們這邊只有一個 Strategy，所以直接使用 results[0] 的結果就可以了。比較特別是 results[0].analyzers.SR.get_analysis() 中是使用前面設定的 **SR** 當呼叫的名稱，這裡要特別注意。

執行之後我們會得到這個結果：

```python
Sharpe Ratio: OrderedDict([('sharperatio', -0.5071606143998728)])
```

於是我們就得到 Sharpe Ratio 的值了。另外將 timeframe 的參數改為 backtrader.TimeFrame.Months，我們就會得到以月為單位計算的結果。

```python
Sharpe Ratio: OrderedDict([('sharperatio', -0.06338628736023329)])
```

另外 Analyzer 其實不是一次只能只用一個，也能一次使用多個，如下面的程式碼，我們同時使用了 DrawDown、TimeReturn 和 SharpeRatio 三種 Analyzers：

```python
from datetime import datetime
import backtrader
import math
 
 
class AllSizer(backtrader.Sizer):
    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy:
            return math.floor(cash/data.high)
        else:
            return self.broker.getposition(data)
 
 
class SmaCross(backtrader.SignalStrategy):
    def __init__(self):
        sma10 = backtrader.ind.SMA(period=10)
        sma30 = backtrader.ind.SMA(period=30)
        crossover = backtrader.ind.CrossOver(sma10, sma30)
        self.signal_add(backtrader.SIGNAL_LONG, crossover)
 
        self.setsizer(AllSizer())
 
 
cerebro = backtrader.Cerebro()
data = backtrader.feeds.YahooFinanceData(dataname='MSFT',
                                         fromdate=datetime(2011, 1, 1),
                                         todate=datetime(2012, 12, 31))
 
cerebro.adddata(data)
cerebro.addstrategy(SmaCross)
cerebro.addanalyzer(backtrader.analyzers.SharpeRatio, _name = 'SR', timeframe=backtrader.TimeFrame.Years)
cerebro.addanalyzer(backtrader.analyzers.DrawDown, _name = 'DW')
cerebro.addanalyzer(backtrader.analyzers.TimeReturn, _name = 'TR', timeframe=backtrader.TimeFrame.Months)
results = cerebro.run()
print('Sharpe Ratio:', results[0].analyzers.SR.get_analysis())
print('Max DrawDown:', results[0].analyzers.DW.get_analysis().max)
for date, value in  results[0].analyzers.TR.get_analysis().items():
     print(date, value)  
```

DrawDown 是計算回撤率的工具，回傳結果中的 max 則是記錄最大回撤率，結果如下：

```python
Max DrawDown: AutoOrderedDict([('len', 198), ('drawdown', 17.71801465164528), ('moneydown', 1976.4599999999991)]) 
```

這裡我們可以看到，最大回撤總共持續了 198 天，下跌了 19.71%，損失了 1976.46 美元。這可以提供我們在設計停損時的一些依據。

而 TimeReturn 則是計算收益的工具，回傳的結果是一個排序好的 Dict，所以我們把它依序列印出來，結果如下：

```python
2011-01-31 00:00:00 0.0
2011-02-28 00:00:00 0.0
2011-03-31 00:00:00 0.0
2011-04-30 00:00:00 -0.010273999999999783
2011-05-31 00:00:00 -0.024536083724182478
2011-06-30 00:00:00 0.027335665943681864
2011-07-31 00:00:00 0.05368343259399522
2011-08-31 00:00:00 -0.08904885568349952
2011-09-30 00:00:00 -0.042906886971318725
2011-10-31 00:00:00 -0.023389784748569564
2011-11-30 00:00:00 0.0
2011-12-31 00:00:00 -0.0018429968927521356
2012-01-31 00:00:00 0.13663358533688363
2012-02-29 00:00:00 0.0816284079934626
2012-03-31 00:00:00 0.016520373448353
2012-04-30 00:00:00 -0.03730546609310592
2012-05-31 00:00:00 -0.03724447064658454
2012-06-30 00:00:00 -0.011841779134246666
2012-07-31 00:00:00 -0.032471926911606275
2012-08-31 00:00:00 0.017043167076716603
2012-09-30 00:00:00 -0.034276837694325546
2012-10-31 00:00:00 -0.0023662293731249173
2012-11-30 00:00:00 0.0
2012-12-31 00:00:00 -0.03251581227796396 
```

由此我們可以分析每個月的報酬狀況。

除了這些工具之外，Backtrader 其實還有提供很多其他的分析工具，因為分析工具眾多，這裡就不一一介紹，有興趣的朋友可以去 Backtrader 的網頁上看看：
https://www.backtrader.com/docu/analyzers-reference/