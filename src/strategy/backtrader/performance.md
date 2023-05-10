## 如何提高BACKTRADER回測性能1倍以上且最佳化記憶體

出處：https://www.itbook5.com/12372/

### 使用200萬條K線的資料，測試backtrader的回測性能如何？

為了做到這一點，第一件事就是產生的足夠的K線。所以，我們會做以下動作：

- 產生100支股票
- 每支股票 20000條K線資料

100個股票資料檔案總計200萬 根K線資料.

程式碼：

```python
import numpy as np
import pandas as pd

COLUMNS = ['open', 'high', 'low', 'close', 'volume', 'openinterest']
CANDLES = 20000
STOCKS

dateindex = pd.date_range(start='2010-01-01', periods=CANDLES, freq='15min')

for i in range(STOCKS):

    data = np.random.randint(10, 20, size=(CANDLES, len(COLUMNS)))
    df = pd.DataFrame(data * 1.01, dateindex, columns=COLUMNS)
    df = df.rename_axis('datetime')
    df.to_csv('candles{:02d}.csv'.format(i))
```

這會生成 100 個檔案，從`candles00.csv到``candles99.csv`. 其中實際值並不重要。擁有標準 `datetime`、`OHLCV`（和`OpenInterest`）才是最重要的。

## 測試系統

- *硬體/作業系統*：將使用配備 Intel i7 和 32 GB 記憶體的*Windows 10的 15.6″筆記型電腦。*
- *Python* : CPython`3.6.1`和`pypy3 6.0.0`
- *其他*：持續運行並佔用大約 20% 的 CPU 的應用程式。正在運行著Chrome（102 個處理程序）、Edge、Word、Powerpoint、Excel 和一些小型應用程式等通常的程序。

## 默認組態

讓我們回顧一下*backtrader*的默認執行階段組態是什麼：

- 如果可能，預載入所有資料饋送
- 如果可以預載入所有資料饋送，則以批處理模式運行（命名為`runonce`）
- 首先預先計算所有指標
- 逐步瞭解策略邏輯和經紀人

## `runonce`在默認批處理模式下執行

我們的測試指令碼（完整原始碼見底部）將打開這 100 個檔案並使用backtrader默認的組態運行。

```sh
$ ./two-million-candles.py
Cerebro Start Time:          2019-10-26 08:33:15.563088
Strat Init Time:             2019-10-26 08:34:31.845349
Time Loading Data Feeds:     76.28
Number of data feeds:        100
Strat Start Time:            2019-10-26 08:34:31.864349
Pre-Next Start Time:         2019-10-26 08:34:32.670352
Time Calculating Indicators: 0.81
Next Start Time:             2019-10-26 08:34:32.671351
Strat warm-up period Time:   0.00
Time to Strat Next Logic:    77.11
End Time:                    2019-10-26 08:35:31.493349
Time in Strategy Next Logic: 58.82
Total Time in Strategy:      58.82
Total Time:                  135.93
Length of data feeds:        20000
```

**記憶體使用**：觀察到 348 MB 的峰值

大部分時間實際上都花在預載入資料（`98.63`秒）上，其餘時間花在策略上，包括在每次迭代中通過代理（`73.63`秒）。總時間為`173.26`秒。

根據您想要計算它的方式，性能是：

- 考慮到整個執行階段間:`14,713`根K線/秒

說明以這樣的資料量backtrader處理起來，基本沒有壓力，記憶體的處理上，還可以通過參數的設定進行最佳化。將在後面做更多的探索。

### `比較使用pypy的方案`

使用pypy的情況下，運行結果如下：

```sh
$ ./two-million-candles.py
Cerebro Start Time:          2019-10-26 08:39:42.958689
Strat Init Time:             2019-10-26 08:40:31.260691
Time Loading Data Feeds:     48.30
Number of data feeds:        100
Strat Start Time:            2019-10-26 08:40:31.338692
Pre-Next Start Time:         2019-10-26 08:40:31.612688
Time Calculating Indicators: 0.27
Next Start Time:             2019-10-26 08:40:31.612688
Strat warm-up period Time:   0.00
Time to Strat Next Logic:    48.65
End Time:                    2019-10-26 08:40:40.150689
Time in Strategy Next Logic: 8.54
Total Time in Strategy:      8.54
Total Time:                  57.19
Length of data feeds:        20000
```

總時間已經從 `135.93`秒減少到`57.19`秒。性能提高了**一倍多**。

性能：`34,971`根K線/秒

**記憶體使用**：觀察到 269 MB 的峰值。

這也是對標準 CPython 直譯器的重要改進。

 

## Handling 2M的蠟燭出核心[memory](https://www.itbook5.com/tag/memory/)

如果考慮到*backtrader*有多個用於執行回測會話的組態選項，所有這些都可以得到改進，包括最佳化緩衝區和僅使用所需的最少資料集（理想情況下僅使用 size 的緩衝區，這只會發生在理想場景）

```python
class backtrader.Cerebro()
參數：

preload（默認True：）
是否預加載data feeds傳遞給 cerebro

runonce（默認：True）
以矢量化模式運行Indicators以加速整個系統。策略和觀察者將始終基於事件運行

live（默認：False）
默認是回測數據。

當使用實時數據時設置成True（或通過數據的islive 方法）

這將同時停用preload和runonce。它對內存節省方案沒有影響。

以矢量化模式運行Indicators以加速整個系統。策略和觀察者將始終基於事件運行

maxcpus（默認值：None -> 所有可用內核）
同時使用多少個內核進行優化

stdstats（默認：True）
默認將添加真正的默認觀察員：經紀人（現金和價值）、交易和買入賣出

oldbuysell（默認：False）（與畫圖相關）
如果stdstatsis：True 時觀察者自動添加，則此開關使用BuySell

False：其中買入/賣出信號分別繪製在低/高價下方/上方，以避免混亂

True：在該行為中繪製買入/賣出信號在給定時間的訂單執行的平均價格。這當然會在 OHLC 條的頂部或在 Close 的 Line 上，從而難以識別。

oldtrades（默認：False）（與畫圖相關）
如果stdstatsis：True時觀察者自動添加，則此開關控制Trades 

False：其中所有數據的交易都用不同的標記繪製

True：同一方向的交易用相同的標記繪製交易，僅區分它們是正數還是負數

exactbars（默認：False）
使用默認值，存儲在一行中的每個值都保存在內存中

`True` 或 `1`：所有“行”對象將內存使用量減少到自動計算的最小週期。

  如果簡單移動平均線的週期為 30，則基礎數據將始終具有 30 個柱的運行緩衝區，以允許計算簡單移動平均線

  * 此設置將停用 `preload` 和 `runonce` 

  * 使用此設置也會停用**繪圖** 

objcache (default: False)
如果為True實現line對象的緩存。

writer（默認: False）
如果設置為True時 它將標準信息的輸出生成一個默認文件

tradehistory（默認: False）
如果設置為True，它將在所有策略的每筆交易中激活更新事件記錄log。這也可以在每個策略的上使用set_tradehistory來實現

optdatas（默認：True）
如果True優化（並且preload和runonce也是True），數據預加載將在主進程中只進行一次，以節省時間和資源。

optreturn（默認：True）
如果True優化結果只有params屬性和analyzers指標，而不是完整Strategy 對象（以及所有數據、指標、觀察者……），這樣可以優化速度，測試顯示改善13% - 15%的執行時間

oldsync（默認False：）
從版本 1.9.0.99 開始，多個數據（相同或不同時間範圍）的同步已更改為允許不同長度的數據。

如果希望使用 data0 作為系統主控的舊行為，請將此參數設置為 true

tz（默認：None）
為策略添加全球時區。論據tz可以是

* `None`：在這種情況下，策略顯示的日期時間將採用UTC，這是標準行為

* `pytz` 實例。它將用於將 UTC 時間轉換為所選時區

* `string`。將嘗試實例化 `pytz` 實例。

* `整數`。
  對於策略，使用與 `self.datas` 迭代中相應的 `data`相同的時區（`0` 將使用來自 `data0` 的時區）

cheat_on_open（默認：False）
當為True時next_open調用發生在next方法調用之前。此時指標尚未重新計算。這允許發佈一個考慮前一天指標但使用open價格計算的訂單

對於 cheat_on_open 訂單執行，還需要調用cerebro.broker.set_coo(True)或實例化一個經紀人 BackBroker(coo=True)（其中coo代表 cheat-on-open）或將broker_coo參數設置為True. 除非在下面禁用，否則 Cerebro 會自動執行此操作。

broker_coo（默認：True）
這將自動調用set_coo代理的方法True來激活cheat_on_open執行。cheat_on_open要同時為True

quicknotify（默認：False）
經紀人通知在下一個價格交付之前交付 。對於回溯測試，這沒有任何影響，但是對於實時經紀人，可以在柱線交付之前很久就發出通知。設置為True通知將盡快發送（請參閱qcheck實時提要）

設置False為兼容性。可以改為True
```

要使用的選項是`exactbars=True`. 從文件中 `exactbars`（這是`Cerebro`在實例化或呼叫時給出的參數`run`）

為了最大程度的最佳化並且停用繪圖，也將使用`stdstats=False`，停用現金、價值和交易的標準觀察者

```sh
$ ./two-million-candles.py --cerebro exactbars=False,stdstats=False
Cerebro Start Time:          2019-10-26 08:37:08.014348
Strat Init Time:             2019-10-26 08:38:21.850392
Time Loading Data Feeds:     73.84
Number of data feeds:        100
Strat Start Time:            2019-10-26 08:38:21.851394
Pre-Next Start Time:         2019-10-26 08:38:21.857393
Time Calculating Indicators: 0.01
Next Start Time:             2019-10-26 08:38:21.857393
Strat warm-up period Time:   0.00
Time to Strat Next Logic:    73.84
End Time:                    2019-10-26 08:39:02.334936
Time in Strategy Next Logic: 40.48
Total Time in Strategy:      40.48
Total Time:                  114.32
Length of data feeds:        20000
```

性能：`17,494`根K線/秒

**記憶體使用**：75M位元組（從開始回測開始到結束，穩定在這個數值）

讓我們與之前的非最佳化運行進行比較

- 無需花費`76`秒鐘預載入資料，而是立即開始回測。
- 總時間是`114.32`秒 比 `135.93秒`改進`15.90%`。
- 使用記憶體改進了`68.5%`。

### 再次`pypy`

既然我們知道如何最佳化，讓我們照著做一次`pypy`。

```sh
$ ./two-million-candles.py --cerebro exactbars=True,stdstats=False 
Cerebro Start Time: 2019-10-26 08:44:32.309689 
Strat Init Time: 2019-10-26 08:44:32.406689
時間加載數據饋送：0.10
數據饋送數量：100 
Strat 開始時間：2019-10-26 08:44:32.409689 
Pre-Next Start Time：2019-10-26 08:44:32.451689
時間計算指標：0.04 
Next Start Time：2019 -10-26 08:44:32.451689 戰略
預熱期時間：0.00戰略下一個邏輯時間
：0.14
結束時間：2019-10-26 08:45:38.918693
戰略下一個邏輯時間：66.47
戰略總時間：66.47
總時間：66.61
數據饋送長度：20000
```

性能：`30,025`根K線/秒

**記憶體使用**：恆定在`49 M位元組`

將其與之前運行進行比較：

- `66.61`秒 比`114.32t秒，在執行階段間上有``41.73%`的改進。
- `49 M位元組比``75 M位元組`，在記憶體上有`34.6%`的改進。

在這種情況下，與批處理模式`pypy`相比，它無法擊敗自己的時間。這是意料之中的，因為在預載入時，計算器指示是在**向量化**模式下完成的。

無論如何，它仍然做得非常好，並且記憶體消耗有了重要的**改善**

## 完整的交易運行

該指令碼可以建立指標（移動平均線）並使用移動平均線的交叉*短期/長期策略*對 100 個股票執行回測*。*讓我們用`pypy`來做，並且知道使用批處理模式會更好，就這樣吧。

```sh
$ ./two-million-candles.py --strat indicators=True,trade=True
Cerebro Start Time:          2019-10-26 08:57:36.114415
Strat Init Time:             2019-10-26 08:58:25.569448
Time Loading Data Feeds:     49.46
Number of data feeds:        100
Total indicators:            300
Moving Average to be used:   SMA
Indicators period 1:         10
Indicators period 2:         50
Strat Start Time:            2019-10-26 08:58:26.230445
Pre-Next Start Time:         2019-10-26 08:58:40.850447
Time Calculating Indicators: 14.62
Next Start Time:             2019-10-26 08:58:41.005446
Strat warm-up period Time:   0.15
Time to Strat Next Logic:    64.89
End Time:                    2019-10-26 09:00:13.057955
Time in Strategy Next Logic: 92.05
Total Time in Strategy:      92.21
Total Time:                  156.94
Length of data feeds:        20000
```

性能：`12,743`根K線/秒

**記憶體使用**：`1300 M位元組`觀察到一個峰值。

由於增加了指標和交易，執行時間明顯增加了，但是為什麼記憶體使用也增加了？

在得出任何結論之前，讓我們嘗試建立指標但不進行交易

```sh
$ ./two-million-candles.py --strat indicators=True
Cerebro Start Time:          2019-10-26 09:05:55.967969
Strat Init Time:             2019-10-26 09:06:44.072969
Time Loading Data Feeds:     48.10
Number of data feeds:        100
Total indicators:            300
Moving Average to be used:   SMA
Indicators period 1:         10
Indicators period 2:         50
Strat Start Time:            2019-10-26 09:06:44.779971
Pre-Next Start Time:         2019-10-26 09:06:59.208969
Time Calculating Indicators: 14.43
Next Start Time:             2019-10-26 09:06:59.360969
Strat warm-up period Time:   0.15
Time to Strat Next Logic:    63.39
End Time:                    2019-10-26 09:07:09.151838
Time in Strategy Next Logic: 9.79
Total Time in Strategy:      9.94
Total Time:                  73.18
Length of data feeds:        20000
```

性能：`27,329` 根K線/秒

**記憶體使用**：（`600 M位元組`在最佳化`exactbars`模式下做同樣的事情只會消耗`60 M位元組`，但會增加執行時間，因為 `pypy`它本身不能最佳化這麼多）

有了**交易，記憶體使用量確實增加**了。原因是對像是由代理建立、傳遞和保存的`Order和``Trade。`

還有該資料集包含隨機值，其產生數量龐大交叉的，因此有大量的訂單和交易。對於常規資料集，不會有類似的行為。

## 結論

1. 1. *backtrader*可以使用默認組態輕鬆處理`2M`蠟燭圖（預載入記憶體資料）
   2. *backtrader*可以在非預載入最佳化模式下運行，將緩衝區減少到最小，以進行減少記憶體使用進行回測
   3. 在*最佳化*的非預載入模式下進行回測時，記憶體消耗的增加來自於代理產生的管理開銷。
   4. 即使交易、使用指標和經紀人不斷阻礙，表現也是`12,473`根K線/秒
   5. 儘可能使用`pypy`（如果您不需要繪圖的時候）

## 測試指令碼

這裡是原始碼

```python
#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
import argparse
import datetime

import backtrader as bt


class St(bt.Strategy):
    params = dict(
        indicators=False,
        indperiod1=10,
        indperiod2=50,
        indicator=bt.ind.SMA,
        trade=False,
    )

    def __init__(self):
        self.dtinit = datetime.datetime.now()
        print('Strat Init Time:             {}'.format(self.dtinit))
        loaddata = (self.dtinit - self.env.dtcerebro).total_seconds()
        print('Time Loading Data Feeds:     {:.2f}'.format(loaddata))

        print('Number of data feeds:        {}'.format(len(self.datas)))
        if self.p.indicators:
            total_ind = self.p.indicators * 3 * len(self.datas)
            print('Total indicators:            {}'.format(total_ind))
            indname = self.p.indicator.__name__
            print('Moving Average to be used:   {}'.format(indname))
            print('Indicators period 1:         {}'.format(self.p.indperiod1))
            print('Indicators period 2:         {}'.format(self.p.indperiod2))

            self.macross = {}
            for d in self.datas:
                ma1 = self.p.indicator(d, period=self.p.indperiod1)
                ma2 = self.p.indicator(d, period=self.p.indperiod2)
                self.macross[d] = bt.ind.CrossOver(ma1, ma2)

    def start(self):
        self.dtstart = datetime.datetime.now()
        print('Strat Start Time:            {}'.format(self.dtstart))

    def prenext(self):
        if len(self.data0) == 1:  # only 1st time
            self.dtprenext = datetime.datetime.now()
            print('Pre-Next Start Time:         {}'.format(self.dtprenext))
            indcalc = (self.dtprenext - self.dtstart).total_seconds()
            print('Time Calculating Indicators: {:.2f}'.format(indcalc))

    def nextstart(self):
        if len(self.data0) == 1:  # there was no prenext
            self.dtprenext = datetime.datetime.now()
            print('Pre-Next Start Time:         {}'.format(self.dtprenext))
            indcalc = (self.dtprenext - self.dtstart).total_seconds()
            print('Time Calculating Indicators: {:.2f}'.format(indcalc))

        self.dtnextstart = datetime.datetime.now()
        print('Next Start Time:             {}'.format(self.dtnextstart))
        warmup = (self.dtnextstart - self.dtprenext).total_seconds()
        print('Strat warm-up period Time:   {:.2f}'.format(warmup))
        nextstart = (self.dtnextstart - self.env.dtcerebro).total_seconds()
        print('Time to Strat Next Logic:    {:.2f}'.format(nextstart))
        self.next()

    def next(self):
        if not self.p.trade:
            return

        for d, macross in self.macross.items():
            if macross > 0:
                self.order_target_size(data=d, target=1)
            elif macross < 0:
                self.order_target_size(data=d, target=-1)

    def stop(self):
        dtstop = datetime.datetime.now()
        print('End Time:                    {}'.format(dtstop))
        nexttime = (dtstop - self.dtnextstart).total_seconds()
        print('Time in Strategy Next Logic: {:.2f}'.format(nexttime))
        strattime = (dtstop - self.dtprenext).total_seconds()
        print('Total Time in Strategy:      {:.2f}'.format(strattime))
        totaltime = (dtstop - self.env.dtcerebro).total_seconds()
        print('Total Time:                  {:.2f}'.format(totaltime))
        print('Length of data feeds:        {}'.format(len(self.data)))


def run(args=None):
    args = parse_args(args)

    cerebro = bt.Cerebro()

    datakwargs = dict(timeframe=bt.TimeFrame.Minutes, compression=15)
    for i in range(args.numfiles):
        dataname = 'candles{:02d}.csv'.format(i)
        data = bt.feeds.GenericCSVData(dataname=dataname, **datakwargs)
        cerebro.adddata(data)

    cerebro.addstrategy(St, **eval('dict(' + args.strat + ')'))
    cerebro.dtcerebro = dt0 = datetime.datetime.now()
    print('Cerebro Start Time:          {}'.format(dt0))
    cerebro.run(**eval('dict(' + args.cerebro + ')'))


def parse_args(pargs=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=(
            'Backtrader Basic Script'
        )
    )

    parser.add_argument('--numfiles', required=False, default=100, type=int,
                        help='Number of files to rea')

    parser.add_argument('--cerebro', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--strat', '--strategy', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')


    return parser.parse_args(pargs)


if __name__ == '__main__':
    run()
```

