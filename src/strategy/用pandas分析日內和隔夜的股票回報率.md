我最近看到一些關於討論隔夜和日內股票收益對比的技術[論文](https://link.juejin.cn?target=https%3A%2F%2Farxiv.org%2Fpdf%2F2201.00223.pdf)的[議論](https://link.juejin.cn?target=https%3A%2F%2Fwww.reddit.com%2Fr%2FSuperstonk%2Fcomments%2Fs2a8fh%2Fthey_still_havent_told_you%2F)。在這篇論文中，我們瞭解到，隔夜股票的回報遠遠超過正常交易時間內的日內回報。換句話說，當市場沒有開盤時，股票波動最大，但當交易進行時，淨收益似乎接近零。該檔案稱這是一個陰謀，大型對沖基金正在操縱市場。在這篇文章中，我將嘗試重現文章中的基本結果，並看看文章中沒有討論的隔夜回報的一個部分。

針對這篇論文，我看到一些人給出了隔夜回報較大的原因，在未來的文章中，我希望能看一下其中的幾個原因。但在這第一篇文章中，我只想介紹一些基本情況。

1. 使用兩個不同的資料來源，重現論文中看到的基本結果
2. 如果出現任何不一致的地方，就解決它們

事實證明，涵蓋這兩個基本步驟將使我們在一篇文章中獲得足夠的工作機會。在這個過程中，我們將使用兩個股票價格資料來源，在這個過程中犯一個錯誤，瞭解股票紅利，並建立一個向量的計算。讓我們開始吧。

## 前提

首先，我鼓勵你考慮瀏覽一下這篇論文。很多時候，閱讀一篇技術論文可以是一個很好的思路來源，即使該論文有一些缺陷。在這種情況下，作者提供了一些原始碼的連結，所以你可以嘗試直接複製他的結果。我確實在修改了一些程式碼後下載並運行了這些程式碼，將一些程式碼升級到Python 3。但在這種情況下，我認為從頭開始嘗試重現資料更容易，因為它是一個簡單的計算。

首先，我將從AlphaVantage獲取資料，你可以在[我之前的](https://link.juejin.cn?target=https%3A%2F%2Fwww.wrighters.io%2Ffinancial-market-data-analysis-with-pandas%2F) [文章](https://link.juejin.cn?target=https%3A%2F%2Fwww.wrighters.io%2Fanalyzing-stock-data-events-with-pandas%2F)中讀到更多關於它和如何獲取你自己的資料。在這些文章中，我還談到了一點SPY，即標準普爾500指數交易所交易基金（ETF）。我們將用它作為我們的例子資料。

因此，讓我們先獲得資料，並繪製SPY的收盤價：

```python
python複製程式碼import pandas as pd
import numpy as np
import os

import matplotlib.pyplot as plt

try:
    API_KEY = open(os.path.expanduser("~/.alphavantage.key"), 'r').readline().strip()
except Exception as ex:
    print("Put your AlphaVantage API key in the file '.alphavantage.key' in your home directory: ", ex)
    API_KEY = "demo"

def get_daily_bars(symbol):
    function = "TIME_SERIES_DAILY"          # daily data
    outputsize = "full"                     # all of it
    datatype = "csv"                        # CSV - comma separated values
    url = f"https://www.alphavantage.co/query?function={function}&symbol=SPY&outputsize=full&apikey={API_KEY}&datatype={datatype}"
    return pd.read_csv(url, parse_dates=['timestamp'], index_col='timestamp').sort_index()

spy_daily = get_daily_bars("SPY")

spy_daily['close'].plot();
```

![SPY price](https://i0.wp.com/www.wrighters.io/wp-content/uploads/2022/03/image.png?resize=375%2C252&ssl=1)

正如我們在以前的文章中所做的那樣，讓我們繪製常規回報。我們稱之為 "收盤價到收盤價 "的回報，或者說只看連續收盤價看到的回報。收盤價是指每天常規交易時段結束時的價格。我們在這裡使用一個簡單的百分比回報。

```scss
scss複製程式碼spy_daily['close_to_close_return'] = spy_daily['close'].pct_change()
spy_daily['close_to_close_return'].cumsum().plot()
```

![SPY returns](https://i0.wp.com/www.wrighters.io/wp-content/uploads/2022/03/image-1.png?resize=380%2C252&ssl=1)

## 日內回報

該檔案談到了日內和隔夜回報的區別。某一天的日內回報是指從當天交易開始（開盤）到同一天交易結束（收盤）產生的回報。一種方法是用收盤價減去開盤價，再除以開盤價。你也可以重新排列術語，得到一個稍微簡單的表達：

```css
css複製程式碼# for intraday return, we want the return from open to close
# one way
spy_daily['open_to_close_return'] = (spy_daily['close'] - spy_daily['open'])/spy_daily['open']
spy_daily['open_to_close_return'].cumsum().plot()
# can also do it like this (by just re-arranging terms)
(spy_daily['close']/spy_daily['open'] - 1).cumsum().plot();
```

![intraday SPY returns](https://i0.wp.com/www.wrighters.io/wp-content/uploads/2022/03/image-2.png?resize=380%2C252&ssl=1)

## 隔夜收益

現在，隔夜回報是由一天的收盤價到第二天的開盤價的變化產生的。為了得到前一天的收盤價，我們使用`Series.shift()` 方法將其移動一天。這將收盤價向前移動了一天，與開盤價保持一致，使我們能夠看到總的隔夜收益：

```css
css複製程式碼# overnight (close to open) returns
spy_daily['close_to_open_return'] = (spy_daily['open']/spy_daily['close'].shift() - 1).shift()
spy_daily['close_to_open_return'].cumsum().plot()
```

![overnight SPY returns](https://i0.wp.com/www.wrighters.io/wp-content/uploads/2022/03/image-3.png?resize=372%2C252&ssl=1)

現在，讓我們把所有這些都放在一個圖上：

```ini
ini複製程式碼# put them all together
spy_daily['close_to_close_return'].cumsum().plot(label="Close to Close")
spy_daily['close_to_open_return'].cumsum().plot(label="Close to Open (overnight)")
spy_daily['open_to_close_return'].cumsum().plot(label="Open to Close (intraday)")
plt.legend()
```

![split SPY returns](https://i0.wp.com/www.wrighters.io/wp-content/uploads/2022/03/image-4.png?resize=380%2C252&ssl=1)

## 成功嗎？

這看起來就像我們開始看到論文中建議的那樣的圖。我們可以看到SPY盤中的總回報接近於0，甚至在資料集的大部分時間裡是負數。隔夜回報有時甚至更糟，但自2009年以來，隔夜回報要高得多。有趣的是。

## 另一個資料來源

現在，我們不使用AlphaVantage，而是使用另一個免費的資料來源，雅虎財經。這篇論文的作者使用雅虎作為論文中所有計算的來源，所以讓我們看看那個資料是什麼樣子。

我通常使用一個[很好的Python庫來](https://link.juejin.cn?target=https%3A%2F%2Fpypi.org%2Fproject%2Fyfinance%2F)訪問雅虎，它使程式碼稍微容易閱讀，並以pandas類型返回資料。它還為我們提供了一個很好的方法來抓取其他一些有趣的資料，比如分叉和分紅。你可以用`pip install yfinance` 來安裝它。

我將只是重現結果，但有第二個資料集：

```scss
scss複製程式碼# author used Yahoo! finance for data, so let's do that as well
import yfinance as yf

spy_yf = yf.Ticker("SPY")
spy_yf_hist = spy_yf.history(period="max")

# calc them
spy_yf_hist['close_to_close_return'] = spy_yf_hist['Close'].pct_change()
spy_yf_hist['close_to_open_return'] = spy_yf_hist['Open']/spy_yf_hist['Close'].shift() - 1
spy_yf_hist['open_to_close_return'] = spy_yf_hist['Close']/spy_yf_hist['Open'] - 1

# plot them
spy_yf_hist['close_to_close_return'].cumsum().plot(label="Close to Close")
spy_yf_hist['close_to_open_return'].cumsum().plot(label="Close to Open (overnight)")
spy_yf_hist['open_to_close_return'].cumsum().plot(label="Open to Close (intraday)")
plt.legend()
```

![splity SPY returns (longer history)](https://i0.wp.com/www.wrighters.io/wp-content/uploads/2022/03/image-5.png?resize=372%2C252&ssl=1)

### 資料差異

首先，我們可以看到，這看起來比我們在AlphaVantage中看到的要戲劇性得多，因為資料一直可以追溯到1992年。隔夜回報是總回報的大部分，日內回報甚至在很多時候都是負的。使用雅虎資料的一個好處是，我們至少看到了論文作者看到的東西。讓我們把AlphaVantage的資料與雅虎的資料進行比較。

註：我把雅虎的資料切斷，使之與AlphaVantage的起始日期相同。如果你有關於索引時間序列資料的問題，你可以查看[這篇文章](https://link.juejin.cn?target=https%3A%2F%2Fwww.wrighters.io%2Findexing-time-series-data-in-pandas%2F)。

我還做了一份資料的副本。好奇我為什麼這樣做？那麼[這篇文章](https://link.juejin.cn?target=https%3A%2F%2Fwww.wrighters.io%2Fviews-copies-and-that-annoying-settingwithcopywarning%2F)可能會讓你感興趣：

```ini
ini複製程式碼# we make a copy so we can modify it later
spy_yf_short = spy_yf_hist[spy_daily.index[0]:].copy()

for c in ['close_to_close_return', 'open_to_close_return', 'close_to_open_return']:
    spy_daily[c].cumsum().plot(label=f"{c} (AV)")
    spy_yf_short[c].cumsum().plot(label=f"{c} (Yahoo!)")
plt.legend()
```

![comparing SPY returns between sources](https://i0.wp.com/www.wrighters.io/wp-content/uploads/2022/03/image-6.png?resize=380%2C252&ssl=1)

我們可以看到，這兩個回報並不匹配。雅虎的回報率比AlphaVantage的高。想知道為什麼嗎？

## 公司行動

每當你在看股票價格資料時，重要的是要瞭解價格是否包括拆分和分紅，這有時也被稱為*公司行動*。

最簡單的例子是一個簡單的股票分割。如果股票的價格很高，董事會可能會決定將股票分割成更小的規模。因此，一股`$100` 的股票將變成10股`$10` 的股票。如果你只看價格，似乎已經下降到1/10的數量。

作為另一個例子，你可能擁有一家公司的股票，而董事會決定將他們的一個業務部門分拆為一個獨立的公司。董事會可以決定，每個股東每擁有一份舊公司的股票，就可以得到一份新公司的股票，但是股票的價格會在拆分當天發生變化以反映這一點。例如，`$20` 的股票可能會變成`$18` 的股票，而新的`$2` 的股票會給股東。如果你*只*看交易時的價格，看起來那天會有額外的損失`$2` 。實際上，股東收到的是新公司的股份，而且該股份將在未來單獨交易。這有點過於簡化了，但關鍵是你不要在資料中忽視這一點。

就股息而言，只要股東在有資格獲得股息的最後一天，即*除息日*，擁有股票，就能從公司獲得股息付款。這通常是在記錄股息的前兩天。

現在我們為什麼要關心這個問題？嗯，首先，對於一些股票來說，這實際上可以增加相當多的錢。而且，由於SPY是一個交易所交易基金，它持有一些*確實*支付股息的股票，它也支付股息，這是ETF中的股票的股息之和。

請注意，AlphaVantage對包括價格歷史中的股息的高級服務收取額外費用。你在上述資料中得到的價格是 "交易時 "的價格。換句話說，這個價格與你在歷史上看到的那一天的價格完全一樣，而紅利都沒有。另一方面，雅虎給我們的是包含股息的價格。

現在我們知道了這一點，上面的圖就有意義了，因為只有一個圖包括了股息。讓我們把它們加起來。如果我們把回報相加，目前的價格中有多少是紅利？

```scss
scss複製程式碼spy_yf_hist['Dividends'].cumsum().plot()
spy_yf_hist['Close'].plot()
print((spy_yf_hist['Dividends'].cumsum()/spy_yf_hist['Close'])[-1])
print(spy_yf_hist['Dividends'].sum())
複製程式碼0.19159901587041897
80.485
```

![Dividends over time](https://i0.wp.com/www.wrighters.io/wp-content/uploads/2022/03/image-7.png?resize=375%2C256&ssl=1)

## 隔夜回報的一個來源--紅利

在我們1992年以來的資料中，有80美元的紅利支付，約佔價格的20%（截至運行源筆記本的時間）。

首先，有多少日期有紅利？讓我們通過找到有非零股息的行來計算。如果你不確定索引是如何工作的，請查看關於索引的系列文章中的[第一篇](https://link.juejin.cn?target=https%3A%2F%2Fwww.wrighters.io%2Findexing-and-selecting-in-pandas-part-1%2F)。在這種情況下，我建立一個布林值索引，選擇非0的行：

```css
css
複製程式碼spy_yf_hist.loc[spy_yf_hist['Dividends'] != 0].shape
scss
複製程式碼(117, 10)
```

歷史上有117次派發的股息。傳統上，股票會每季度支付一次股息。讓我們來看看AlphaVantage（無紅利）和雅虎（有紅利）資料中紅利發放時的資料。注意，我看的是完整的資料集來得到這個日期。

```css
css
複製程式碼spy_yf_hist.loc['2021-12-16':'2021-12-20', ['Open', 'Close', 'Dividends', 'close_to_open_return']]
sql複製程式碼                  Open       Close  Dividends  close_to_open_return
Date                                                               
2021-12-16  470.915555  464.816986      0.000              0.004186
2021-12-17  461.549988  459.869995      1.633             -0.007029
2021-12-20  454.480011  454.980011      0.000             -0.011721
css
複製程式碼spy_daily.loc['2021-12-16':'2021-12-20', ['open', 'close', 'close_to_open_return']]
sql複製程式碼              open   close  close_to_open_return
timestamp                                       
2021-12-16  472.57  466.45              0.000129
2021-12-17  461.55  459.87              0.004186
2021-12-20  454.48  454.98             -0.010505
```

看一下這些資料，我們似乎可以看到股息是如何應用的。對於雅虎的資料（最上面的那個），價格似乎都被歷史上的股息數額所調整。對於派發股息的日子，你可以看到雅虎的回報高於Alpha Vantage的回報，因為它包括了股息的回報。SPY只是一堆股票放在一起，所以它支付的股息與單個股息的總和相匹配（大致如此）。那麼，有多少回報是單單由於分紅而產生的？

```css
css複製程式碼spy_daily['close_to_open_return'].cumsum().plot(label="Close to Close (AV)")
spy_yf_short['close_to_open_return'].cumsum().plot(label="Close to Close (Y!)")
plt.legend()
without_dividends = spy_daily['close_to_open_return'].sum()
with_dividends = spy_yf_short['close_to_open_return'].sum()
print(f"with: {with_dividends * 100:.2f}%, without: {without_dividends* 100:.2f}, difference: {(with_dividends - without_dividends)*100:.2f}%")
yaml
複製程式碼with: 173.23%, without: 134.50, difference: 38.73%
```

![difference between sources](https://i0.wp.com/www.wrighters.io/wp-content/uploads/2022/03/image-8.png?resize=378%2C252&ssl=1)

因此，SPY的隔夜回報中大約有20%是單獨來自股息。顯然，隔夜和日內回報之間仍有鮮明的對比，我們需要繼續思考這個問題。但紅利是一個很大的貢獻因素。在報紙上進行文字搜尋，甚至沒有提到它們。

## 仔細檢查結果

確保你有正確答案的一個方法是重複檢查你的結果。我喜歡做的一個方法是，看看我是否可以將一個資料集的資料轉化為第二個資料集的資料。讓我們使用雅虎股息資料，並嘗試使用AlphaVantage的價格得出調整後的價格。首先，讓我們使用雅虎的API來獲取股息資料。我們將忽略一個事實，即我們已經在價格資料中擁有它。事實證明，這是微不足道的：

```
複製程式碼spy_yf.dividends
yaml複製程式碼Date
1993-03-19    0.213
1993-06-18    0.318
1993-09-17    0.286
1993-12-17    0.317
1994-03-18    0.271
              ...  
2020-12-18    1.580
2021-03-19    1.278
2021-06-18    1.376
2021-09-17    1.428
2021-12-17    1.633
Name: Dividends, Length: 117, dtype: float64
```

現在，為了計算去除紅利後的價格，我們應該只需要去除歷史價格中的紅利部分。這樣做的效果是使我們的回報率更高。要做到這一點，我們首先要在我們的`DataFrame` ，新增一個紅利列。由於這個資料很稀疏（記得每年只有4次付款），大部分行中都會有`NaN`s。

```css
css
複製程式碼spy_daily['dividend'] = spy_yf.dividends
```

為了抵消價格，我們將做三件事：

1. 將它們相加
2. 將它們與正確的日期對齊
3. 從價格中減去股息

關於總和的一個注意事項，它需要通過時間向後增加，因為你越往後走，從價格中去除的紅利就越多。記住，在你的價格資料中包含股息，必須使它看起來像你在過去以較低的價格買入股票，所以它現在更有價值。這是因為實際價格在支付股息時被交易所本身的股息金額降低了。

我做了一份資料的副本，看看包括股息回報的資料會是什麼樣子。請注意，下面的程式碼有許多鏈式方法。我不是一下子就打出來的，我不得不嘗試了幾次反覆，才想出了正確的組合。但這展示了你如何在pandas中使用連鎖方法來轉換你的資料。如果你不瞭解這些方法，我鼓勵你一個一個地去看，看看如何轉換資料。

下面是我們所做的，一步步來：

1. `fillna` 用 "0 "來填充空值
2. `sort_index(ascending=False)` 按逆時針順序對數值進行排序
3. `cumsum` 將紅利做一個累積的總和
4. `sort_index` 將指數按時間順序重新排序
5. `shift(-1)` 將數值向後移動一天，以便在其生效日期進行。

```scss
scss複製程式碼spy_daily_r = spy_daily.copy()
spy_daily_r['total_dividend'] = spy_daily_r['dividend'].fillna(0).sort_index(ascending=False).cumsum().sort_index().shift(-1)
spy_daily_r.loc['2021-12-16':'2021-12-20', ['open', 'close', 'close_to_open_return', 'total_dividend']]
sql複製程式碼              open   close  close_to_open_return  total_dividend
timestamp                                                       
2021-12-16  472.57  466.45              0.000129           1.633
2021-12-17  461.55  459.87              0.004186           0.000
2021-12-20  454.48  454.98             -0.010505           0.000
```

現在，我們將更新我們的價格以去除總紅利。我只是通過我們的四個價格（最高價、最低價、開盤價、收盤價），把總紅利退掉，然後繪製結果：

```less
less複製程式碼for c in ['high', 'low', 'open', 'close']:
    spy_daily_r[c] = spy_daily_r[c] - spy_daily_r['total_dividend']

spy_yf_short['Close'].plot(label="Yahoo")
spy_daily['close'].plot(label="AlphaVantage")
spy_daily_r['close'].plot(label="AlphaVantage (with dividends applied)")
plt.legend()
```

![failed attempt to add dividends](https://i0.wp.com/www.wrighters.io/wp-content/uploads/2022/03/image-9.png?resize=375%2C256&ssl=1)

## 實際計算紅利

哦，不，它沒有工作!應用於AlphaVantage資料的紅利與雅虎的資料不匹配。 會是什麼問題呢？在做了一些調查後，我意識到我天真的從價格中退去紅利的方法並不是正確的方法。考慮下面的例子：假設一隻股票的價格是`$10` ，每季度支付`$0.25` 股息。價格在15年內保持在`$10` 。調整後的價格將是多少？如果我們只從當前價格中減去累計股息，我們最終會得到一個負的價格，即`$-5` ，或`$10-(4x$0.25)*15` 。要使價格保持在0以上，我們將需要另一種方法。

事實證明，雅虎的計算方法是使用了證券價格研究中心（CRSP）的一種標準化技術，[這裡](https://link.juejin.cn?target=https%3A%2F%2Fhelp.yahoo.com%2Fkb%2FSLN28256.html)的解釋有點不到位。不是從價格中減去總的紅利價值，而是根據紅利和紅利發放前的最近收盤價計算出一個乘數。這個係數總是大於0，小於1，將被應用於所有的價格，直到下一次分紅的時間追溯。在下一次分紅時，會計算一個新的係數。

這個係數總是計算為`1 - (dividend/price)` ，所有的係數都是向後相乘的，然後應用於所有的價格。請注意，累積因子每季度只改變一次。

為了在pandas中應用這種技術，我們只需要為每一行獲得正確的價格和紅利。價格將是分紅前一天的收盤價。

注意，程式設計師可能會想寫一個函數，遍歷`DataFrame` 中的所有行來計算這個值。如果你有典型的Python程式設計經驗，這對你來說可能是非常直接的。但是一個更好的方法是建立一個向量的解決方案。關於為什麼這樣做更好，請看[這篇文章](https://link.juejin.cn?target=https%3A%2F%2Fwww.wrighters.io%2Fhow-to-iterate-over-dataframe-rows-and-should-you%2F)。

首先，我們需要找到分紅前一天的收盤價。像先前一樣，我們使用一個布林值指數，但我們把它往後移一天：

```bash
bash複製程式碼# shift the dividends back 1 day, use them to obtain the rows with the prices to use
spy_daily_d = spy_daily.copy()
spy_daily_d.loc[~pd.isnull(spy_daily_d['dividend'].shift(-1)), 'close']
yaml複製程式碼timestamp
1999-12-16    142.1250
2000-03-16    146.3437
2000-06-15    148.1562
2000-09-14    149.6406
2000-12-14    134.4062
                ...   
2020-12-17    372.2400
2021-03-18    391.4800
2021-06-17    421.9700
2021-09-16    447.1700
2021-12-16    466.4500
Name: close, Length: 90, dtype: float64
```

注意，這些價格有一個索引值（一個日期），是這個價格開始往後使用的日期。我們現在只需要計算我們的係數，用每個價格的紅利來計算。我們使用與上面相同的概念抓取紅利：

```arduino
arduino
複製程式碼spy_daily_d.loc[~pd.isnull(spy_daily_d['dividend']), 'dividend']
yaml複製程式碼timestamp
1999-12-17    0.348
2000-03-17    0.371
2000-06-16    0.348
2000-09-15    0.375
2000-12-15    0.411
              ...  
2020-12-18    1.580
2021-03-19    1.278
2021-06-18    1.376
2021-09-17    1.428
2021-12-17    1.633
Name: dividend, Length: 90, dtype: float64
```

注意，這裡的指數偏離了一天，這是股息本身的日期。我們現在可以計算因子了，但是我們必須注意我們的指數我們希望使用來自價格的指數，而不是來自股息的指數，所以我們只是從股息中抓取`values` 。因子已經準備好了，可以一次性計算：

```bash
bash複製程式碼factor = 1 - (spy_daily_d.loc[~pd.isnull(spy_daily_d['dividend']), 'dividend'].values/
              spy_daily_d.loc[~pd.isnull(spy_daily_d['dividend'].shift(-1)), 'close'])
factor
yaml複製程式碼timestamp
1999-12-16    0.997551
2000-03-16    0.997465
2000-06-15    0.997651
2000-09-14    0.997494
2000-12-14    0.996942
                ...   
2020-12-17    0.995755
2021-03-18    0.996735
2021-06-17    0.996739
2021-09-16    0.996807
2021-12-16    0.996499
Name: close, Length: 90, dtype: float64
```

你可以在這裡看到，我們現在有一系列的因素和它們生效的日期。我們的最後一步是通過將這些因子相乘來回溯應用。你可以在pandas中使用`cumprod` ，它的工作原理與`cumsum` 相似，但它不是求和，而是求積。同樣，我們需要做我們在錯誤的解決方案中所做的`sort_index` ，以使其在時間上向後而不是向前：

```ini
ini
複製程式碼factor.sort_index(ascending=False).cumprod().sort_index()
yaml複製程式碼timestamp
1999-12-16    0.664324
2000-03-16    0.665955
2000-06-15    0.667648
2000-09-14    0.669219
2000-12-14    0.670901
                ...   
2020-12-17    0.982657
2021-03-18    0.986846
2021-06-17    0.990078
2021-09-16    0.993317
2021-12-16    0.996499
Name: close, Length: 90, dtype: float64
```

只是抽查一下，這是有意義的。我們越往後走，係數應該越小，使過去的價格更低，所以由於紅利的影響，我們的回報更高。最後，讓我們把它應用於我們的價格，看看我們是否能與雅虎的資料相匹配：

```ini
ini複製程式碼# second attempt. Make a new copy of the original source data that is pristine
spy_daily_r2 = spy_daily.copy()
spy_daily_r2['factor'] = factor.sort_index(ascending=False).cumprod().sort_index()
# backfill the missing values with the most recent value (i.e the factor from that dividend)
spy_daily_r2['factor'].bfill(inplace=True)  
spy_daily_r2['factor'].fillna(1, inplace=True)  # base case

for c in ['high', 'low', 'open', 'close']:
    spy_daily_r2[c] = spy_daily_r2[c] * spy_daily_r2['factor']

spy_yf_short['Close'].plot(label="Yahoo")
spy_daily['close'].plot(label="AlphaVantage")
spy_daily_r2['close'].plot(label="AlphaVantage (with dividends applied)")
plt.legend()
```

![correct SPY dividends](https://i0.wp.com/www.wrighters.io/wp-content/uploads/2022/03/image-10.png?resize=375%2C252&ssl=1)

現在我們有了一個匹配的結果!我承認，我花了不少時間來偵錯，才把它弄好。這裡有一些關於如何不犯我在弄清這個問題時所犯的同樣錯誤的提示。

### 不要重複使用你修改過的資料

如果你從一個原始來源（在我的例子中是雅虎和AlphaVantage）獲取了資料，然後在一次失敗的嘗試中對其進行了修改，那麼就不要在另一次嘗試中使用這個`DataFrame` ，從頭開始。在我的例子中，我重新使用了我的資料，從我糾正後的實施中的不正確的方法倒出紅利，我仍然是錯誤的（因為我的價格已經被修改了）。確保你能從頭到尾拉出資料，並知道所有的修改。做到這一點的一個方法是把你的筆記本分成獨立的筆記本，用於每次嘗試。

### 好好利用可視化的錯誤

如果你有兩個應該匹配的資料集，繪製它們的比率，看看它們有多接近對方。如果它們不是真的接近於1，你就知道你有問題了。然後尋找它們分歧的日期。對我來說，我注意到這些分歧發生在分紅日期，所以我意識到我在某一點上破壞了資料。

### 考慮一下`matplotlib notebook`

默認情況下，matplotlib的圖在Jupyter中是內聯顯示的。在Jupyter中，有一個特殊的魔法，可以在你的瀏覽器中生成互動式的圖，`%matplotlib notebook` 。把這個放在你繪製資料的筆記本儲存格的頂部，你想與之互動。你可以放大差異。

### 詳細查看個別行

我對單行進行了手工計算，直到我確信正確的數值應該是什麼。一旦我有了一個知道的好結果，我就可以看那些行來仔細檢查我的計算結果。如果你覺得有幫助的話，你甚至可以把這個放在電子表格裡。

好了，我們已經談得夠多了。希望在這一點上，你對紅利的瞭解比你開始時更多，而且不應忽視它們！這就是紅利。

還有什麼原因會導致隔夜收益主導日內收益呢？我將在以後的文章中再看一些潛在的原因。那些文章將包括下載、清理和分析資料的程式碼和技術，就像這篇文章一樣。

作者：后端之巅
链接：https://juejin.cn/post/7128195311796748296
来源：稀土掘金
著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。