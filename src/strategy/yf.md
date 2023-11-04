### Python 學習筆記 : 用 yfinance 套件取得股票資料 

出處: https://yhhuang1966.blogspot.com/2022/09/python-yfinance.html

yfinance 的原始碼寄存於 GitHub :

\# https://github.com/ranaroussi/yfinance

本篇測試參考了下面的文章 : 

\# [如何使用Python取得歷史股價，簡介yfinance、ffn、FinMind](https://havocfuture.tw/blog/python-stock-history)

\# [使用Python及Yahoo Finance API抓取臺股歷史資料](https://aronhack.com/zh/retrieve-stock-historical-data-with-python-and-yahoo-finance-api/)

\# [Free Stock Data for Python Using Yahoo Finance API](https://towardsdatascience.com/free-stock-data-for-python-using-yahoo-finance-api-9dafd96cad2e)

\# [yfinance 攻略！Python 下載股票價格數據無難度](https://pythonviz.com/finance/yfinance-download-stock-data/)

根據第二篇與第三篇的說明, Yahoo Finance API 的限制是 :

- 每個 IP 每小時的請求上限是 2000 次
- 每個 IP 單日請求上限是 48000 次

比較務實的做法是自己建立資料庫, 利用 yfinance 擷取資料後儲存於資料庫, 以後就只要抓當日的新資料添加到資料庫中即可. 

**1. 在 Windows 上安裝 yfinance :** 

Windows 的安裝指令如下 : 

**pip install yfinance**  

可見 yfinance 是建立在 requests,lxml, numpy 與 Pandas 等套件的基礎上. 

**2. 在樹莓派上安裝 yfinance :** 

由於程式最終是要在樹莓派上奔跑, 所以也要在 Raspbian 上安裝看看, 安裝指令要用 pip3, 因為 pip 是給內建的 Python 2 用的 : 

pi@raspberrypi:~ $ **pip3 install yfinance**   

基本上不會有問題, 有的話可能是其相依套件例如 requests 等之版本匹配問題. 

**3. 在 Colab 上安裝 yfinance :** 

在 Colab 也可以安裝 yfinance, 指令如下 :

**!pip install yfinance**  

[![img](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiuqeNyEu3bwFMwRNZCdD4Ghi8dTk-95Hsz3gdje0ztWSfNMgp5MEhOOJR3mIhEOt8CFZJgxjCU2A37j6czOSK0_u21TWRrD1v_4vADQ4hZ-Fe6g4OwS1BrCl03awLlEpy6PjZDYVHBP1Do2svE21PsoVlUj5zCEvcvlAQfWgfpYusjquM3F6zktdIlfw/s320/colab-install-yfinance.jpg)](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiuqeNyEu3bwFMwRNZCdD4Ghi8dTk-95Hsz3gdje0ztWSfNMgp5MEhOOJR3mIhEOt8CFZJgxjCU2A37j6czOSK0_u21TWRrD1v_4vADQ4hZ-Fe6g4OwS1BrCl03awLlEpy6PjZDYVHBP1Do2svE21PsoVlUj5zCEvcvlAQfWgfpYusjquM3F6zktdIlfw/s1315/colab-install-yfinance.jpg)

在 Colab 上跑 Python 的一個好處是列印格式很整齊. 關於 Colab 用法參考 :

\# [Python 學習筆記 : 谷歌版的線上 Jupyter Notebook (Colaboratory)](https://yhhuang1966.blogspot.com/2020/04/python-jupyter-notebook-colaborator.html)

**4. 檢視 yfinance 的內容 :** 

先來檢視 ylfinance 套件的內容, 以下使用一個自訂模組 members, 其 list_members() 函式會列出模組或套件中的公開成員 (即屬性與方法), 參考 :

\# [Python 學習筆記 : 檢視物件成員與取得變數名稱字串的方法](https://yhhuang1966.blogspot.com/2022/03/python.html)

使用 yfinance 前須先用 import 匯入, 通常取別名為 yf :

\>>> **import yfinance as yf**   

\>>> **import members**  

\>>> **members.list_members(yf)**  

Ticker <class 'type'>

Tickers <class 'type'>

base <class 'module'>

download <class 'function'>

multi <class 'module'>

pdr_override <class 'function'>

shared <class 'module'>

ticker <class 'module'>

tickers <class 'module'>

utils <class 'module'>

version <class 'module'>

其中 download() 函式與 Ticker 類別是最常用的, 利用 download() 函式可取得股票的歷史價量資料; 而使用 Ticker 類別則不僅可取得歷史價量資料, 還可取得股票更詳細的金融資訊, 例如公司基本資訊, 大戶與法人持股比例, 損益表, 資產負債表, 現金流量表等財報資料. 

**5. 用 yf.download() 下載股票日收盤價量資料 :** 

呼叫 yf.download() 函式可取得 Yahoo Finance 提供的股票歷史日收盤價量資訊, 其傳回值為一個 Pandas 的 DataFrame 物件, 這對進行技術分析與線圖繪製非常方便, 語法如下 : 

**df=yf.download(symbol [, start, end] [, period, interval])** 

其參數說明如下表 :

| download() 參數 | 說明                                                         |
| --------------- | ------------------------------------------------------------ |
| symbol          | 股票代號 (字串), 美股例如 'AMD' (超微), 臺股後面要加 '.tw', 例如 '0050.tw' |
| start           | 起始日期 YYYY-MM-DD (字串), 例如 '2022-08-22'                |
| end             | 結束日期 YYYY-MM-DD (字串), 例如 '2022-09-06', 注意, 不包含此日資料 |
| period          | 期間, 可用 d (日), mo(月), y(年), ytd, max(全部), 例如 5d (5 天), 3mo(三個月) |
| interval        | 頻率, 可用 m(分), h(小時), d(日), wk(周), mo(月), 例如 1m(一分線) |

必要參數 symbol 表示商品名稱代號, 例如特斯拉是 'TSLA', 微軟是 'MSF' 等, 如果是臺股, 必須在臺股股票代號後面要加上 '.TW' 或 '.tw' (大小寫均可), 例如臺積電是 '2330.TW', 臺灣五十是 '0050.TW' 等等. 

四個備選參數有三個使用模式, 第一組是 [start, end] 用於指定特定起迄日期的日收盤資料 (end 不含); 第二組是 [period, interval] 用來指定最近一段時間內某個頻率的歷史資料 (ticker); 第三組是 [start, end, interval] 用來指定特定起迄日期內特定頻率的資料. 

如果只傳入 symbol 參數, 則會傳回該股票所有的歷史日收盤價量資料之 DataFrame 物件, 例如 :

\>>> **import pandas as pd**  

\>>> **import yfinance as yf**  

\>>> **df=yf.download('TSLA')**    # 下載特斯拉 TSLA 全部歷史價量資料 

[*********************100%***********************] 1 of 1 completed

\>>> **type(df)**  

<class 'pandas.core.frame.DataFrame'>    

\>>> **df**  

​         Open    High ...  Adj Close   Volume

Date                ...            

2010-06-29  1.266667  1.666667 ...  1.592667 281494500

2010-06-30  1.719333  2.028000 ...  1.588667 257806500

2010-07-01  1.666667  1.728000 ...  1.464000 123282000

2010-07-02  1.533333  1.540000 ...  1.280000  77097000

2010-07-06  1.333333  1.333333 ...  1.074000 103003500

...        ...     ... ...     ...    ...

2022-08-30 287.869995 288.480011 ... 277.700012  50541800

2022-08-31 280.619995 281.250000 ... 275.609985  52107300

2022-09-01 272.579987 277.579987 ... 277.160004  54287000

2022-09-02 281.070007 282.350006 ... 270.209991  50752200

2022-09-06 272.679993 275.989990 ... 274.420013  55762000

[3069 rows x 6 columns]

可見 yf.download('TSLA') 會傳回特斯拉自 2010-06-29 上市以來的全部歷史價量資料 (10 年來股價上漲 200 多倍, 嚇鼠), 但因資料總欄寬與總列數超過 Pandas 的預設值, 故會用 ... 表示隱藏省略掉的欄位. 總資料筆數共 3069 筆, 但只會顯示頭尾各五筆. 若要顯示全部欄位須要用下列 Pandas 的 set_option() 函式設定 : 

**pd.set_option('display.max_columns', None)**   # 顯示全部欄位

**pd.set_option('display.width', 1000)**          # 設定總欄寬為 1000 px

注意,總欄寬若設得太小, 後面超出的欄位會反折, 故可能需要嘗試將 display.width 再放寬. 

參考 : 

\# [How to show all columns / rows of a Pandas Dataframe?](https://towardsdatascience.com/how-to-show-all-columns-rows-of-a-pandas-dataframe-c49d4507fcf)

\# [How do I expand the output display to see more columns of a Pandas DataFrame?](https://stackoverflow.com/questions/11707586/how-do-i-expand-the-output-display-to-see-more-columns-of-a-pandas-dataframe)

例如 : 

\>>> **pd.set_option('display.max_columns', None)**  

\>>> **pd.set_option('display.width', 1000)**    

\>>> **df**  

​         Open    High     Low    Close  Adj Close   Volume

Date                                       

2010-06-29  1.266667  1.666667  1.169333  1.592667  1.592667 281494500

2010-06-30  1.719333  2.028000  1.553333  1.588667  1.588667 257806500

2010-07-01  1.666667  1.728000  1.351333  1.464000  1.464000 123282000

2010-07-02  1.533333  1.540000  1.247333  1.280000  1.280000  77097000

2010-07-06  1.333333  1.333333  1.055333  1.074000  1.074000 103003500

...        ...     ...     ...     ...     ...    ...

2022-08-30 287.869995 288.480011 272.649994 277.700012 277.700012  50541800

2022-08-31 280.619995 281.250000 271.809998 275.609985 275.609985  52107300

2022-09-01 272.579987 277.579987 266.149994 277.160004 277.160004  54287000

2022-09-02 281.070007 282.350006 269.079987 270.209991 270.209991  50752200

2022-09-06 272.679993 275.989990 265.739990 274.420013 274.420013  55762000

[3069 rows x 6 columns]

這樣就能顯示全部欄位了, 可見 yf.download() 所下載的資料總共包含七個欄位 :

- Date (日期)
- Open (開盤價) 
- High (最高價)
- Low (最低價)
- Close (收盤價)
- Adj Close (調整後之收盤價)
- Volumn (成交量 : 股數)

這些資料可以直接拿來繪製技術分析線圖.

頭尾五筆也可以用 pd.head() 與 pd.tail() 顯示 (也可傳入筆數) :

\>>> **df.head()**  

​        Open   High    Low   Close Adj Close   Volume

Date                                  

2010-06-29 1.266667 1.666667 1.169333 1.592667  1.592667 281494500

2010-06-30 1.719333 2.028000 1.553333 1.588667  1.588667 257806500

2010-07-01 1.666667 1.728000 1.351333 1.464000  1.464000 123282000

2010-07-02 1.533333 1.540000 1.247333 1.280000  1.280000  77097000

2010-07-06 1.333333 1.333333 1.055333 1.074000  1.074000 103003500

\>>> **df.tail()**  

​         Open    High     Low    Close  Adj Close  Volume

Date                                      

2022-08-30 287.869995 288.480011 272.649994 277.700012 277.700012 50541800

2022-08-31 280.619995 281.250000 271.809998 275.609985 275.609985 52107300

2022-09-01 272.579987 277.579987 266.149994 277.160004 277.160004 54287000

2022-09-02 281.070007 282.350006 269.079987 270.209991 270.209991 50752200

2022-09-06 272.679993 275.989990 265.739990 274.420013 274.420013 55762000

如果使用 JupyterLab 或 Colab 會完整顯示所有欄位, 不需要設定 Pandas : 

yf.download() 可以傳入的備選參數來指定資料期間或頻率, 這些參數地用法分成 [start, end], [period, interval], 與 [start, end, interval] 兩個模式 :

**(1). Start-end 模式 :** 

呼叫 yf.download() 時傳入起始 start 與結束 end 日期兩個參數, 這會傳回該期間日收盤之價量資料 (注意, 所下載的資料不含 end 那天, 只到其前一天), 例如指定下載 2022-08-24 至 2022-09-07 的歷史資料 :

\>>> **import yfinance as yf** 

\>>> **df=yf.download('0050.tw', start='2022-08-24', end='2022-09-07')**  

[*********************100%***********************] 1 of 1 completed

\>>> **df**  

```
         Open    High     Low    Close  Adj Close  Volume
Date                                      
2022-08-24 118.800003 118.949997 117.650002 117.900002 117.900002  7063478
2022-08-25 118.500000 119.449997 118.449997 119.000000 119.000000  4893719
```

因為 end='2022-09-07' 這天的資料不包含, 故只會抓 '2022-08-24' 至 '2022-09-06' 的資料. 一般來說, 當日臺股資料大約 16:00 左右就可以抓到了. 

也可以搭配 datetime 模組來設定 start 與 end 參數, 例如下載過去 60 天的資料 :

\>>> **import datetime**  

\>>> **import yfinance as yf** 

\>>> **start=datetime.datetime.now() - datetime.timedelta(days=60)**  

\>>> **end=datetime.date.today()**  

\>>> **df=yf.download('2330.tw', start, end)**  

[*********************100%***********************] 1 of 1 completed

\>>> **df.head()**  

```
       Open  High  Low Close  Adj Close  Volume
Date                            
2022-07-18 495.5 498.5 488.5 495.5 492.661224 39179575
2022-07-19 487.5 493.0 486.5 491.0 488.186981 19874865
```

此處使用 datetime.timedelta() 來設定過去一段時間間隔以取得那時的時戳. 

**(2). Period-interval 模式 :** 

此模式是傳入 period 與 interval 兩個參數, period 是一個表示最近的一段期間的字串, 由一個整數與單位字串組成, 可用的單位如下 :

- 'd' : 天數, 例如 '5d' 表示近五日, '20d' 表示近 20 日
- 'mo' : 月數, 例如 '1mo' 表示近一個月, '3mo' 表示近 3 個月
- 'y' : 年數, 例如 '1y' 表示近一年, '3y' 表示近 3 年
- 'ytd' : 今年以來, 即自年初第一個交易日至今
- 'max' : 所有時間資料

 而 interval 則是用來指定資料的頻率, 也是由一個整數與單位字串組成, 可用的單位如下 :

- 'm' : 每幾分鐘, 例如 '1m' 為每一分鐘
- 'h' : 每幾小時, 例如 '3h' 為每三小時
- 'd' : 每幾天, 例如 '1d' 為每天
- 'wk' : 每幾周, 例如 '1wk' 為每週
- 'mo' : 每幾月, 例如 '1mo' 為每個月

例如要抓過去十天每日價量資料 :

\>>> **df=yf.download('0050.TW', period='10d', interval='1d')**   # 過去 10 天, 每天

[*********************100%***********************] 1 of 1 completed

\>>> **df**  

```
         Open    High     Low    Close  Adj Close  Volume
Date                                      
2022-08-25 118.500000 119.449997 118.449997 119.000000 119.000000  4893719
2022-08-26 119.849998 120.099998 119.449997 119.599998 119.599998  9959737
```

這與 start='2022-08-25', end='2022-09-08' 的結果一樣, 例如 :

\>>> **df=yf.download('0050.tw', start='2022-08-25', end='2022-09-08')**   

[*********************100%***********************] 1 of 1 completed

\>>> **df**  

```
         Open    High     Low    Close  Adj Close  Volume
Date                                      
2022-08-25 118.500000 119.449997 118.449997 119.000000 119.000000  4893719
2022-08-26 119.849998 120.099998 119.449997 119.599998 119.599998  9959737
```

如果要取得今年以來的月收盤歷史資料, period 可用 'ytd', interval 則用 '1mo' : 

\>>> **df=yf.download('0050.TW', period='ytd', interval='1mo')**   

[*********************100%***********************] 1 of 1 completed

\>>> **df**  

```
         Open    High     Low    Close  Adj Close   Volume
Date                                       
2022-02-01 141.550003 145.050003 137.850006 138.500000 138.500000 167881702
2022-03-01 139.050003 140.800003 131.000000 138.100006 138.100006 310811068
```

如果將 interval 設為 '1m' 則可取得每分鐘報價 (即一分 K 線), 不過 Yahoo Finance 只提供近七日內的一分 K 高頻交易數據, 例如 :

\>>> **df=yf.download('0050.TW', period='1d', interval='1m')**   

[*********************100%***********************] 1 of 1 completed

\>>> **df**  

```
                 Open    High     Low    Close  Adj Close Volume

Datetime                                           
2022-09-07 09:00:00+08:00 113.099998 113.150002 113.000000 113.150002 113.150002    0
2022-09-07 09:01:00+08:00 113.099998 113.150002 113.000000 113.000000 113.000000 222000
2022-09-07 13:30:00+08:00 112.199997 112.199997 112.199997 112.199997 112.199997    0

[266 rows x 6 columns]
```



若試圖下載超過 7 天的一分 K 資料會被拒絕 : 

\>>> **df=yf.download('0050.TW', period='8d', interval='1m')**

[*********************100%***********************] 1 of 1 completed

1 Failed download:

\- 0050.TW: 1m data not available for startTime=1661902806 and endTime=1662594006. Only 7 days worth of 1m granularity data are allowed to be fetched per request.

**(3). Start-end-interval 模式 :** 

其實 Start-end 模式也可以傳入 interval 參數來指定期間內的資料頻率, 例如下載 2022-09-06 與 2022-09-07 這兩天的五分 K 資料 (interval='5m') 可以這麼做 : 

\>>> **df=yf.download('0050.TW', start='2022-09-06', end='2022-09-08', interval='5m')**  

[*********************100%***********************] 1 of 1 completed

\>>> **df**  

```
                 Open    High     Low    Close  Adj Close Volume
Datetime                                           
2022-09-06 09:00:00+08:00 114.800003 115.250000 114.800003 115.250000 115.250000    0
2022-09-06 09:05:00+08:00 115.300003 115.400002 115.099998 115.150002 115.150002 150000
```



如果要取得周收盤資料可以用 interval='1wk', 傳回資料的列索引會以週一那天為代表, 開盤價取週一的 Open, 收盤價取週五那天的 Close, 最高價取週一至週五的 High 中最大的, 最低價取週一至週五的 Low 中最小的, 而周成交量則是週一至週五成交量總和. 

例如 2022-07-04 到 2022-09-08 的周收盤資料 : 

\>>> **df=yf.download('0050.TW', start='2022-07-04', end='2022-09-09', interval='1wk')**   

[*********************100%***********************] 1 of 1 completed

\>>> **df**  

```
         Open    High     Low    Close  Adj Close  Volume

Date                                      
2022-07-04 111.250000 113.900002 108.449997 113.250000 113.250000 81880198
2022-07-11 113.650002 115.650002 109.150002 115.500000 115.500000 76837034
2022-07-18 114.650002 117.199997 113.599998 116.800003 116.800003 76713181
```

以其中的第一週 2022-07-04 這列為例, 周開盤價 111.25, 最高價 113.9, 最低價 108.45, 收盤價 113.25, 這可查詢這一週的日收盤價來印證 : 

\>>> **df=yf.download('0050.TW', start='2022-07-04', end='2022-07-09')**  

[*********************100%***********************] 1 of 1 completed

\>>> **df**  

```
         Open    High     Low    Close  Adj Close  Volume

Date                                      
2022-07-04 111.250000 112.199997 110.000000 110.449997 110.449997 26442712
2022-07-05 112.550003 112.949997 109.000000 111.000000 111.000000 16214458
2022-07-06 111.000000 111.050003 108.449997 108.849998 108.849998 15611981
2022-07-07 109.449997 112.150002 108.550003 112.099998 112.099998 13433190
2022-07-08 113.300003 113.900002 112.300003 113.250000 113.250000 10177857
```

可見周開盤價 111.25 取自週一 (2022-07-04) 的開盤價; 周最高價 113.9 出現在週五 (2022-07-08); 周最低價 118.45 出現在週三 (2022-07-06); 周收盤價 113.25 取自週五 (2022-07-08) 的收盤價; 而周成交量 81880198 則是週一至週五成交量之總和 :

\>>> **sum(df['Volume'])**  

81880198

月收盤資料也是類似, 月開盤價是該月第一個交易日的開盤價 (一律以 1 日為索引); 月最高價是該月每日 High 之最大者; 月最低價是該月每日 Low 之最小者; 月收盤價是該月最後一個交易日的收盤價; 月成交量則是該月每日成交量之總和, 以 2022 年七月為例 : 

\>>> **df=yf.download('0050.TW', start='2022-07-01', end='2022-09-01', interval='1mo')**  

[*********************100%***********************] 1 of 1 completed

\>>> **df**  

```
         Open    High     Low    Close  Adj Close   Volume

Date                                       

2022-07-01 115.650002 118.500000 108.449997 118.000000 118.000000 317571855
2022-08-01 118.099998 122.300003 115.099998 117.599998 117.599998 208948196
2022-09-01 115.500000 115.599998 113.699997 114.900002 114.900002  50409932
```



月收盤資料一律會以該月 1 日當列索引, 以第一列的七月收盤為例, 可從檢視七月的日收盤資料來印證 : 

\>>> **df=yf.download('0050.TW', start='2022-07-01', end='2022-08-01')**  

[*********************100%***********************] 1 of 1 completed

\>>> **df**   

```
         Open    High     Low    Close  Adj Close  Volume

Date                                      
2022-07-01 115.650002 115.650002 111.199997 111.550003 111.550003 34719560
2022-07-04 111.250000 112.199997 110.000000 110.449997 110.449997 26442712
2022-07-05 112.550003 112.949997 109.000000 111.000000 111.000000 16214458
```

可見月開盤價 115.65 為七月第一個交易日 2022-07-01 之開盤價; 月最高價 118.5 出現在最後交易日 2022-07-29 的 High; 月最低價 108.45 出現在 2022-07-06 的 Low; 月收盤價 118.0 為七月最後一個交易日 2022-07-29 之收盤價: 月成交量則是七月每個交易日成交量之總和, 可用內建函式 max(), min(), 與 sum() 來求得 : 

```
>>> **max(df['High'])**  
118.5  
>>> **min(df['Low'])**  
108.44999694824219  
>>> **sum(df['Volume'])**  
317571855
```

**6. 用 Ticker 物件取得更多金融資訊 :** 

Ticker 是 yfinance 套件中的一個類別, 呼叫其建構子 Ticker() 並傳入商品代號 (例如 'TSLA') 即可建立該商品之 Ticker 物件, 再用其屬性與方法取得歷史交易價量與財報資訊. 注意, 如果是查詢臺股標的, 須在臺股代號後面添加 ".TW", 例如 :

\>>> **import yfinance as yf**  

\>>> **type(yf.Ticker)**  

<class 'type'>

\>>> **tsla=yf.Ticker('TSLA')**          # 美股 Tesla

\>>> type(tsla) 

<class 'yfinance.ticker.Ticker'>    

\>>> **tw2330=yf.Ticker("2330.TW")**    # 臺積電 

\>>> **type(tw2330)**  

<class 'yfinance.ticker.Ticker'>   

可見 Ticker() 會建立並傳回一個 Ticker 物件, 以下使用一個自訂模組 members 來檢視 Ticker 物件的內容, 其 list_members() 函式會列出模組或套件中的公開成員 (即屬性與方法), 參考 :

\# [Python 學習筆記 : 檢視物件成員與取得變數名稱字串的方法](https://yhhuang1966.blogspot.com/2022/03/python.html)

例如 : 

\>>> **import members**  

\>>> **tw2330=yf.Ticker("2330.tw")**     # 臺積電 

\>>> **members.list_members(tw2330)**   

```
actions <class 'pandas.core.frame.DataFrame'>

analysis <class 'NoneType'>

balance_sheet <class 'pandas.core.frame.DataFrame'>

balancesheet <class 'pandas.core.frame.DataFrame'>

calendar <class 'NoneType'>

cashflow <class 'pandas.core.frame.DataFrame'>

dividends <class 'pandas.core.series.Series'>

earnings <class 'pandas.core.frame.DataFrame'>

earnings_dates <class 'pandas.core.frame.DataFrame'>

earnings_history <class 'NoneType'>

financials <class 'pandas.core.frame.DataFrame'>

get_actions <class 'method'>

get_analysis <class 'method'>

get_balance_sheet <class 'method'>

get_balancesheet <class 'method'>

get_calendar <class 'method'>

get_cashflow <class 'method'>

get_dividends <class 'method'>

get_earnings <class 'method'>

get_earnings_dates <class 'method'>

get_earnings_history <class 'method'>

get_financials <class 'method'>

get_info <class 'method'>

get_institutional_holders <class 'method'>

get_isin <class 'method'>

get_major_holders <class 'method'>

get_mutualfund_holders <class 'method'>

get_news <class 'method'>

get_recommendations <class 'method'>

get_shares <class 'method'>

get_splits <class 'method'>

get_sustainability <class 'method'>

history <class 'method'>

info <class 'dict'>

institutional_holders <class 'pandas.core.frame.DataFrame'>

isin <class 'str'>

major_holders <class 'pandas.core.frame.DataFrame'>

mutualfund_holders <class 'NoneType'>

news <class 'list'>

option_chain <class 'method'>

options <class 'tuple'>

quarterly_balance_sheet <class 'pandas.core.frame.DataFrame'>

quarterly_balancesheet <class 'pandas.core.frame.DataFrame'>

quarterly_cashflow <class 'pandas.core.frame.DataFrame'>

quarterly_earnings <class 'pandas.core.frame.DataFrame'>

quarterly_financials <class 'pandas.core.frame.DataFrame'>

recommendations <class 'NoneType'>

session <class 'NoneType'>

shares <class 'NoneType'>

splits <class 'pandas.core.series.Series'>

stats <class 'method'>

sustainability <class 'NoneType'>

ticker <class 'str'>
```

常用屬性如下表 :

| Ticker 物件常用屬性    | 說明                         |
| ---------------------- | ---------------------------- |
| info                   | 商品之綜合資訊 (字典)        |
| major_holders          | 大戶持股比例                 |
| institutional_holders  | 機構法人持股比例             |
| financials             | 近四年損益表 (DataFrame)     |
| balance_sheet          | 近四年資產負債表 (DataFrame) |
| cashflow               | 近四年現金流量表 (DataFrame) |
| quarterly_financials   | 近四季損益表 (DataFrame)     |
| quarterly_balancesheet | 近四季資產負債表 (DataFrame) |
| quarterly_cashflow     | 近四季現金流量表 (DataFrame) |
| quarterly_earnings     | 近四年營收與獲利 (DataFrame) |
| recommendations        | 投資建議 (DataFrame)         |
| dividends              | 歷年股息 (DataFrame)         |
| earnings               | 歷年獲利 (DataFrame)         |
| actions                | 歷年股息與股利 (DataFrame)   |

常用方法如下表 : 

| Ticker 物件常用方法         | 說明                             |
| --------------------------- | -------------------------------- |
| history()                   | 傳回歷史價量資料                 |
| get_info()                  | 傳回商品之綜合資訊 (字典)        |
| get_financials()            | 傳回近四年損益表 (DataFrame)     |
| get_balance_sheet()         | 傳回近四年資產負債表 (DataFrame) |
| get_cashflow()              | 傳回近四年現金流量表 (DataFrame) |
| get_shares()                | 傳回近四年流通股數 (DataFrame)   |
| get_dividends()             | 傳回歷年股利 (DataFrame)         |
| get_earnings()              | 傳回歷年獲利 (DataFrame)         |
| get_major_holders()         | 傳回大戶持股比例 (DataFrame)     |
| get_institutional_holders() | 傳回機構法人持股比例 (DataFrame) |
| get_actions()               | 傳回歷年股息與股利 (DataFrame)   |

其中最重要的是用來取得歷史價量資料的 history() 方法. 財報資料例如損益表 (financials), 資產負債表 (balance_sheet), 現金流量表 (cashflow), 流通股數 (shares), 股利 (dividends), 獲利 (earnings) 等可用屬性取得, 也可以呼叫方法取得. 以下會交替使用屬性與方法呼叫來取得這些資料.

**(1). 呼叫 history() 方法取得歷史價量資料 :**

history() 方法的功能與 download() 函式類似, 都是用來取得商品的價量資料, 同樣會傳回一個 Pandas 的 DataFrame, 語法如下 :

**df=ticker.history([start, end] [, period, interval])** 

 

參數說明如下表 : 

| history() 參數 | 說明                                                         |
| -------------- | ------------------------------------------------------------ |
| start          | 起始日期 YYYY-MM-DD (字串), 例如 '2022-08-22'                |
| end            | 結束日期 YYYY-MM-DD (字串), 例如 '2022-09-06', 注意, 不包含此日資料 |
| period         | 期間, 可用 d (日), mo(月), y(年), ytd, max(全部), 例如 5d (5 天), 3mo(三個月) |
| interval       | 頻率, 可用 m(分), h(小時), d(日), wk(周), mo(月), 例如 1m(一分線) |
| actions        | 是否下載配息與配股事件 (布林值, 預設 True)                   |
| auto_adjust    | 是否自動調整所有 OHLC 值 (布林值, 預設 True)                 |
| prepost        | 是否包含 Pre 與 Post 之市場資料 (布林值, 預設 False)         |

常用的參數為前四個 (後三個都是有預設值的布林值), 用法與 download() 函式一樣, 同樣分成 Start-end, Period-interval, 以及 Start-end-interval 三種模式, 如果沒有傳入任何參數, 預設傳回近一個月的歷史資料, 例如 : 

\>>> **tw2330.history()**   

```
       Open  High  Low Close  Volume Dividends Stock Splits
Date                                   
2022-08-08 510.0 515.0 509.0 512.0 19333128     0       0
2022-08-09 507.0 511.0 504.0 510.0 21164373     0       0
2022-08-10 500.0 503.0 499.5 500.0 20861380     0       0
```

可見 history() 方法與 download() 函式取得的資料類似, 都有 OHLCV (但缺了調整收盤價), 而且多出 Dividends 與 Stock Splits 欄位 (因為 actions 參數預設為 True, 如果傳入 actions=False 就不會出現這兩欄了). 可惜臺股似乎只是聊備一格沒資料, 但美股就有, 例如 : 

\>>> **tsla.history()**  

```
         Open    High     Low    Close  Volume Dividends Stock Splits
Date                                             
2022-08-10 297.066681 297.510010 283.369995 294.356659 94918800     0      0.0
2022-08-11 296.513336 298.236664 285.833344 286.630005 70155000     0      0.0
2022-08-12 289.416656 300.160004 285.033325 300.029999 79657200     0      0.0
```

特斯拉的 Dividends 都是 0, 這不是沒資料, 而是該公司從未配息. 

Start-end 模式是傳入起迄日期內的歷史資料 (不含 end 那一天), 例如 : 

\>>> **tw2330.history(start='2022-08-24', end='2022-09-07')**   

​       Open  High  Low Close  Volume Dividends Stock Splits

Date                                   

2022-08-24 504.0 508.0 503.0 503.0 14363212     0       0

2022-08-25 505.0 510.0 504.0 508.0  9357138     0       0

2022-08-26 513.0 515.0 511.0 512.0 12914846     0       0

2022-08-29 497.0 502.0 496.0 498.5 26590824     0       0

2022-08-30 497.5 500.0 496.0 496.0 24214535     0       0

2022-08-31 492.0 505.0 492.0 505.0 39357089     0       0

2022-09-01 495.0 495.5 490.0 490.5 39168672     0       0

2022-09-02 488.0 489.5 485.0 485.0 29982959     0       0

2022-09-05 485.0 488.0 484.0 486.0 15903415     0       0

2022-09-06 488.5 491.5 486.5 489.0 16700285     0       0

Period-Interval 模式會傳回最近一段期間特定頻率的價量資料 : 

\>>> **tw2330.history(period='10d', interval='1d')**  

​       Open  High  Low Close  Volume Dividends Stock Splits

Date                                   

2022-08-26 513.0 515.0 511.0 512.0 12914846     0       0

2022-08-29 497.0 502.0 496.0 498.5 26590824     0       0

2022-08-30 497.5 500.0 496.0 496.0 24214535     0       0

2022-08-31 492.0 505.0 492.0 505.0 39357089     0       0

2022-09-01 495.0 495.5 490.0 490.5 39168672     0       0

2022-09-02 488.0 489.5 485.0 485.0 29982959     0       0

2022-09-05 485.0 488.0 484.0 486.0 15903415     0       0

2022-09-06 488.5 491.5 486.5 489.0 16700285     0       0

2022-09-07 477.0 478.0 472.0 472.5 34678562     0       0

2022-09-08 473.0 475.0 472.0 475.0 27931552     0       0

傳入 period='max' 會下載股票上市以來的全部價量資料, 例如 Tesla : 

\>>> **df=tsla.history(period='max')**  

\>>> **df**   

​         Open    High ... Dividends Stock Splits

Date                ...             

2010-06-29  1.266667  1.666667 ...     0      0.0

2010-06-30  1.719333  2.028000 ...     0      0.0

2010-07-01  1.666667  1.728000 ...     0      0.0

2010-07-02  1.533333  1.540000 ...     0      0.0

2010-07-06  1.333333  1.333333 ...     0      0.0

...        ...     ... ...    ...      ...

2022-09-01 272.579987 277.579987 ...     0      0.0

2022-09-02 281.070007 282.350006 ...     0      0.0

2022-09-06 272.679993 275.989990 ...     0      0.0

2022-09-07 273.100006 283.839996 ...     0      0.0

2022-09-08 281.299988 289.500000 ...     0      0.0

[3071 rows x 7 columns]

此處將傳回的 DataFrame 儲存在 df 變數中, 可用 Matplotlib 來繪製全部歷史收盤價圖形 :

\>>> **import matplotlib.pyplot as plt**  

\>>> **df['Close'].plot(figsize=(16, 9))**  

<matplotlib.axes._subplots.AxesSubplot object at 0x00000188333272B0>

\>>> **plt.show()**    

結果如下 : 

[![img](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhh4MrX2ucq7k3YVQxqc5lQNyIz59-j-sR0r6VDwStHdz9GrBbiHSi2tH4_clVdEUGgkUh_dvYva_D5NMIkpb1Nw_Ql70jrUyTtYwyGDIR9vVicgKQBexQflorh5_joBRy2a5eYMljBDnZb0URJE0Akm5OUe1LKWrSiBxyb48ZI9TiA3h4qhC67_Fo0_w/s320/yfinance-tsla-history-close.jpg)](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhh4MrX2ucq7k3YVQxqc5lQNyIz59-j-sR0r6VDwStHdz9GrBbiHSi2tH4_clVdEUGgkUh_dvYva_D5NMIkpb1Nw_Ql70jrUyTtYwyGDIR9vVicgKQBexQflorh5_joBRy2a5eYMljBDnZb0URJE0Akm5OUe1LKWrSiBxyb48ZI9TiA3h4qhC67_Fo0_w/s1301/yfinance-tsla-history-close.jpg)

如果要畫得漂亮些可用 Seaborn, 用法參考 :

\# [Python 學習筆記 : Seaborn 資料視覺化 (二)](https://yhhuang1966.blogspot.com/2022/07/python-seaborn_22.html)

\# [How to change the figure size of a seaborn axes or figure level plot](https://stackoverflow.com/questions/31594549/how-to-change-the-figure-size-of-a-seaborn-axes-or-figure-level-plot)

 

例如 : 

\>>> **import seaborn as sns**  

\>>> **sns.set(rc={'figure.figsize':(16, 9)})**  

\>>> **sns.lineplot(x='Date', y="Close", data=df)**   

<matplotlib.axes._subplots.AxesSubplot object at 0x000001884337A828>

\>>> **plt.show()**  

結果如下 : 

[![img](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiDU-nSfATIdlalMkYPpC7kqkQKJwwmHQQh4JRnAmQWh9kwE1MRdupwZaGsdvXMOgi2Zr3j3ERlVENDeMyB_0pi3-tmtke_V9Z7uTqYqkybqxbYfgsOuPe5WIxvE9QspeA8Grw_2r887xz8_anOGqVB48EV-j1Z747ZmGV1o8a8HvuyA-mWfOjuVulqJA/s320/yfinance-tsla-history-close-seaborn.jpg)](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiDU-nSfATIdlalMkYPpC7kqkQKJwwmHQQh4JRnAmQWh9kwE1MRdupwZaGsdvXMOgi2Zr3j3ERlVENDeMyB_0pi3-tmtke_V9Z7uTqYqkybqxbYfgsOuPe5WIxvE9QspeA8Grw_2r887xz8_anOGqVB48EV-j1Z747ZmGV1o8a8HvuyA-mWfOjuVulqJA/s1319/yfinance-tsla-history-close-seaborn.jpg)

哇, 如果在 2020 年買進特斯拉就賺爆了. 

用 Period-interval 模式下載月收盤資料 :

\>>> **tw2330.history(period='ytd', interval='1mo')**  

​         Open    High     Low    Close    Volume Dividends Stock Splits

Date                                              

2022-02-01 637.363946 643.302119 593.817341 597.776123 554354568.0    0.00       0

2022-03-01 592.827658 603.714309 549.281052 590.848267 976978169.0    0.00       0

2022-03-16     NaN     NaN     NaN     NaN     NaN    2.75       0

2022-04-01 581.839394 585.817783 520.174364 535.093323 613866812.0    0.00       0

2022-05-01 535.093347 556.974487 502.271636 556.974487 597891764.0    0.00       0

2022-06-01 547.028479 552.001465 473.428284 473.428284 619492801.0    0.00       0

2022-06-16     NaN     NaN     NaN     NaN     NaN    2.75       0

2022-07-01 471.500000 510.000000 433.000000 509.000000 718989084.0    0.00       0

2022-08-01 506.000000 527.000000 488.500000 505.000000 513479662.0    0.00       0

2022-09-01 495.000000 495.500000 472.000000 475.000000 164365445.0    0.00       0

2022-09-08 473.000000 475.000000 472.000000 475.000000  28881358.0    0.00       0

不知何故會出現 2022-03-16 與 2022-06-16 的 NaN 資料, 這是與 download() 不同之處. 

高頻交易數據 (例如 1 分 K) 同樣只能下載近 7 天資料 : 

\>>> **tw2330.history(period='7d', interval='1m')**  

​              Open  High  Low Close Volume Dividends Stock Splits

Datetime                                       

2022-08-31 09:00:00+08:00 492.0 493.0 492.0 492.5    0     0       0

2022-08-31 09:01:00+08:00 492.5 493.0 492.0 492.5 392000     0       0

2022-08-31 09:02:00+08:00 492.5 493.0 492.0 492.5 233000     0       0

2022-08-31 09:03:00+08:00 492.5 493.5 492.5 493.0 254000     0       0

2022-08-31 09:04:00+08:00 493.5 493.5 493.0 493.5 243000     0       0

...             ...  ...  ...  ...   ...    ...      ...

2022-09-08 13:21:00+08:00 474.5 474.5 474.0 474.0 103000     0       0

2022-09-08 13:22:00+08:00 474.0 474.5 474.0 474.0 168093     0       0

2022-09-08 13:23:00+08:00 474.0 474.5 473.5 474.0 243000     0       0

2022-09-08 13:24:00+08:00 474.5 474.5 474.0 474.0 120643     0       0

2022-09-08 13:30:00+08:00 475.0 475.0 475.0 475.0    0     0       0

[1845 rows x 7 columns]

\>>> **tw2330.history(period='8d', interval='1m')**  

\- 2330.TW: 1m data not available for startTime=1662085882 and endTime=1662777082. Only 7 days worth of 1m granularity data are allowed to be fetched per request.

Empty DataFrame

Columns: [Open, High, Low, Close, Adj Close, Volume]

Index: []

Start-end-interval 模式是 Start-end 模式加上 interval 參數指定期間內的資料頻率, 例如下載 2022-09-06 與 2022-09-07 這兩天的五分 K 資料 (interval='5m') 

\>>> **tw2330.history(start='2022-09-06', end='2022-09-08', interval='5m')**   

​              Open  High  Low Close  Volume Dividends Stock Splits

Datetime                                        

2022-09-06 09:00:00+08:00 488.5 491.0 488.0 491.0    0     0       0

2022-09-06 09:05:00+08:00 491.0 491.5 489.5 489.5  477000     0       0

2022-09-06 09:10:00+08:00 489.5 490.5 489.5 490.0  543911     0       0

2022-09-06 09:15:00+08:00 490.0 490.5 489.0 489.0  711856     0       0

2022-09-06 09:20:00+08:00 489.0 489.5 488.0 489.0  396767     0       0

...             ...  ...  ...  ...   ...    ...      ...

2022-09-07 13:05:00+08:00 473.5 474.0 473.0 473.0 1531608     0       0

2022-09-07 13:10:00+08:00 473.0 473.5 472.5 472.5  869565     0       0

2022-09-07 13:15:00+08:00 472.5 474.5 472.0 473.0 1845877     0       0

2022-09-07 13:20:00+08:00 473.0 475.0 473.0 473.0 1243638     0       0

2022-09-07 13:25:00+08:00 473.0 473.0 473.0 473.0  81857     0       0

[107 rows x 7 columns]

下載周收盤資料 (繪製周 K 線用) :

\>>> **tw2330.history(start='2022-07-04', end='2022-09-09', interval='1wk')**  

​       Open  High  Low Close   Volume Dividends Stock Splits

Date                                   

2022-07-04 443.0 470.5 433.0 467.0 229129023     0       0

2022-07-11 468.0 494.0 449.5 492.5 172796995     0       0

2022-07-18 495.5 505.0 486.5 503.0 141993085     0       0

2022-07-25 500.0 510.0 491.0 509.0 113325604     0       0

2022-08-01 506.0 516.0 488.5 516.0 150371495     0       0

2022-08-08 510.0 518.0 499.5 517.0 104634837     0       0

2022-08-15 520.0 527.0 517.0 519.0 100990578     0       0

2022-08-22 511.0 515.0 502.0 512.0  67320304     0       0

2022-08-29 497.0 505.0 485.0 485.0 159314079     0       0

2022-09-05 485.0 491.5 472.0 475.0  95213814     0       0

2022-09-08 473.0 475.0 472.0 475.0  28881358     0       0

下載月收盤資料 (繪製月 K 線用) :

\>>> **tw2330.history(start='2022-01-01', end='2022-09-01', interval='1mo')**  

​         Open    High     Low    Close    Volume Dividends Stock Splits

Date                                              

2022-01-01 612.621586 680.910583 611.631890 629.446411 922313952.0    0.00       0

2022-02-01 637.363946 643.302119 593.817341 597.776123 554354568.0    0.00       0

2022-03-01 592.827658 603.714309 549.281052 590.848267 976978169.0    0.00       0

2022-03-16     NaN     NaN     NaN     NaN     NaN    2.75       0

2022-04-01 581.839394 585.817783 520.174364 535.093323 613866812.0    0.00       0

2022-05-01 535.093347 556.974487 502.271636 556.974487 597891764.0    0.00       0

2022-06-01 547.028479 552.001465 473.428284 473.428284 619492801.0    0.00       0

2022-06-16     NaN     NaN     NaN     NaN     NaN    2.75       0

2022-07-01 471.500000 510.000000 433.000000 509.000000 718989084.0    0.00       0

2022-08-01 506.000000 527.000000 488.500000 505.000000 513479662.0    0.00       0

2022-09-01 495.000000 495.500000 472.000000 475.000000 164365445.0    0.00       0

除了上面常用的三種參數組合模式外, start/end 也可以與 period 合用, 例如 Start-period 模式可指定開始日期至今頻率為 period 的價量資料; 或 End-period 模式可指定自上市起至 end 日期頻率為 period 的價量資料. 

**(2). 商品綜合資訊 info :**

Ticker 物件的 info 屬性以字典型態儲存商品之綜合資訊, 呼叫方法 get_info() 也會傳回相同的資料, 此字典的項目非常多, 如果直接 print 不會顯示全部內容, 必須用 for 迴圈走訪 items() 傳回的字典鍵與值. 

\>>> **for k, v in tw2330.info.items():**   # 也可以用 tw2330.get_info().items()

  **print(f'{k}:\t{v}')**  

  

zip:	300096

sector:	Technology

fullTimeEmployees:	54193

longBusinessSummary:	Taiwan Semiconductor Manufacturing Company Limited manufactures, packages, tests, and sells integrated circuits and other semiconductor devices in Taiwan, China, Europe, the Middle East, Africa, Japan, the United States, and internationally. It provides complementary metal oxide silicon wafer fabrication processes to manufacture logic, mixed-signal, radio frequency, and embedded memory semiconductors. The company also offers customer support, account management, and engineering services, as well as manufactures masks. Its products are used in mobile devices, high performance computing, automotive electronics, and internet of things markets. The company was incorporated in 1987 and is headquartered in Hsinchu City, Taiwan.

city:	Hsinchu City

phone:	886 3 563 6688

country:	Taiwan

companyOfficers:	[]

website:	https://www.tsmc.com

maxAge:	1

address1:	Hsinchu Science Park

fax:	886 3 563 7000

industry:	Semiconductors

address2:	No. 8, Li-Hsin Road 6

ebitdaMargins:	0.67949

profitMargins:	0.40587002

grossMargins:	0.54959

operatingCashflow:	1407924699136

revenueGrowth:	0.435

operatingMargins:	0.44752

ebitda:	1276140847104

targetLowPrice:	500

recommendationKey:	buy

grossProfits:	819537266000

freeCashflow:	143859351552

targetMedianPrice:	650

currentPrice:	475

earningsGrowth:	0.764

currentRatio:	2.255

returnOnAssets:	0.14123

numberOfAnalystOpinions:	29

targetMeanPrice:	675.37

debtToEquity:	36.432

returnOnEquity:	0.33964002

targetHighPrice:	860

totalCash:	1450175234048

totalDebt:	914603245568

totalRevenue:	1878076424192

totalCashPerShare:	55.926

financialCurrency:	TWD

revenuePerShare:	72.429

quickRatio:	1.981

recommendationMean:	1.8

exchange:	TAI

shortName:	TAIWAN SEMICONDUCTOR MANUFACTUR

longName:	Taiwan Semiconductor Manufacturing Company Limited

exchangeTimezoneName:	Asia/Taipei

exchangeTimezoneShortName:	CST

isEsgPopulated:	False

gmtOffSetMilliseconds:	28800000

quoteType:	EQUITY

symbol:	2330.TW

messageBoardId:	finmb_380075

market:	tw_market

annualHoldingsTurnover:	None

enterpriseToRevenue:	6.419

beta3Year:	None

enterpriseToEbitda:	9.446

52WeekChange:	-0.23667204

morningStarRiskRating:	None

forwardEps:	37.85

revenueQuarterlyGrowth:	None

sharesOutstanding:	25930399744

fundInceptionDate:	None

annualReportExpenseRatio:	None

totalAssets:	None

bookValue:	96.271

sharesShort:	None

sharesPercentSharesOut:	None

fundFamily:	None

lastFiscalYearEnd:	1640908800

heldPercentInstitutions:	0.42201

netIncomeToCommon:	762250854400

trailingEps:	29.23

lastDividendValue:	2.75

SandP52WeekChange:	-0.13021445

priceToBook:	4.933988

heldPercentInsiders:	0

nextFiscalYearEnd:	1703980800

yield:	None

mostRecentQuarter:	1656547200

shortRatio:	None

sharesShortPreviousMonthDate:	None

floatShares:	24181894477

beta:	1.117948

enterpriseValue:	12054771531776

priceHint:	2

threeYearAverageReturn:	None

lastSplitDate:	1247616000

lastSplitFactor:	1:1

legalType:	None

lastDividendDate:	1671062400

morningStarOverallRating:	None

earningsQuarterlyGrowth:	0.764

priceToSalesTrailing12Months:	6.6326323

dateShortInterest:	None

pegRatio:	0.58

ytdReturn:	None

forwardPE:	12.549539

lastCapGain:	None

shortPercentOfFloat:	None

sharesShortPriorMonth:	None

impliedSharesOutstanding:	0

category:	None

fiveYearAverageReturn:	None

previousClose:	472.5

regularMarketOpen:	473

twoHundredDayAverage:	559.825

trailingAnnualDividendYield:	0.023280423

payoutRatio:	0.3763

volume24Hr:	None

regularMarketDayHigh:	475

navPrice:	None

averageDailyVolume10Day:	24886832   (近 10 日均量)

regularMarketPreviousClose:	472.5

fiftyDayAverage:	493.17

trailingAnnualDividendRate:	11

open:	473

toCurrency:	None

averageVolume10days:	24886832

expireDate:	None

algorithm:	None

dividendRate:	11

exDividendDate:	1663200000

circulatingSupply:	None

startDate:	None

regularMarketDayLow:	472

currency:	TWD

trailingPE:	16.250427

regularMarketVolume:	28881358

lastMarket:	None

maxSupply:	None

openInterest:	None

marketCap:	12456590049280

volumeAllCurrencies:	None

strikePrice:	None

averageVolume:	28951866

dayLow:	472

ask:	475.5

askSize:	0

volume:	28881358

fiftyTwoWeekHigh:	688   (近 52 周最高價)

fromCurrency:	None

fiveYearAvgDividendYield:	2.78  (近 5 年平均現金股息)

fiftyTwoWeekLow:	433    (近 52 周最低價)

bid:	475

tradeable:	False

dividendYield:	0.0227

bidSize:	0

dayHigh:	475

coinMarketCapLink:	None

regularMarketPrice:	475

preMarketPrice:	None

logo_url:	https://logo.clearbit.com/tsmc.com

trailingPegRatio:	0.788

如果用 Colab 就可以直接 print, 不須用迴圈走訪 items() : 

[![img](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiIfaKY_gI29eiX9Vq-e4j9eo3O8hFRg9X09RG8IUCW_uLOvhvriUjqMGWuYpjEGXddxiBkSPSpseflJPiEaHtiXBQVqJY0MRX062amnWXybzWgCpKBvnV6RLBl9glyI741qF8lFkcuIjEzkI-plS_FWn5Ti4KU90F98YY1bvCUJj_C4BzUri9AqJgPkA/s320/yfinance-tw2330.info.jpg)](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiIfaKY_gI29eiX9Vq-e4j9eo3O8hFRg9X09RG8IUCW_uLOvhvriUjqMGWuYpjEGXddxiBkSPSpseflJPiEaHtiXBQVqJY0MRX062amnWXybzWgCpKBvnV6RLBl9glyI741qF8lFkcuIjEzkI-plS_FWn5Ti4KU90F98YY1bvCUJj_C4BzUri9AqJgPkA/s914/yfinance-tw2330.info.jpg)

此資料也可以用 get_info() 方法取得. 

**(3). 內部人士與大戶持股比例 major_holders :**

Ticker 物件的 major_holders 屬性以 DataFrame 型態儲存商品之大戶持股比例 : 

\>>> **tw2330.major_holders**   

​    0                   1

0  0.00%    % of Shares Held by All Insider

1 42.20%    % of Shares Held by Institutions

2 42.20%    % of Float Held by Institutions

3   641 Number of Institutions Holding Shares

此資料也可以呼叫 get_major_holders() 取得, 例如 :

\>>> **tsla.get_major_holders()**  

​    0                   1

0 16.43%    % of Shares Held by All Insider

1 44.43%    % of Shares Held by Institutions

2 53.17%    % of Float Held by Institutions

3  3304 Number of Institutions Holding Shares

**(4). 機構法人持股比例 major_holders :**

不知為何, 這個資料對臺股來說不論用屬性或方法都傳回 None : 

\>>> **print(tw2330.institutional_holders)**  

None

\>>> **print(tw2330.get_institutional_holders())**  

None

但美股則有資料, 例如特斯拉 :

\>>> **tsla.get_institutional_holders()**   

[![img](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiku_qIfLqYJdoTqglq73KXttuzFFxiN3Qmu-LPLIxF-d9w6CMHd9a1JatrYxLSADg71PZcbET2YzMFTbAK6S7UECBrBlLMzcTRdbm_zsE-MtGYMggE36RHszIS4E42ol50pptQngi-_t8md7T5Y_IWcGs_eY_YglnWBVwyLyg3u5wD8ABGmA3ASX4M8w/s320/yfinance-tsla.major_holders.jpg)](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiku_qIfLqYJdoTqglq73KXttuzFFxiN3Qmu-LPLIxF-d9w6CMHd9a1JatrYxLSADg71PZcbET2YzMFTbAK6S7UECBrBlLMzcTRdbm_zsE-MtGYMggE36RHszIS4E42ol50pptQngi-_t8md7T5Y_IWcGs_eY_YglnWBVwyLyg3u5wD8ABGmA3ASX4M8w/s572/yfinance-tsla.major_holders.jpg)

**(5). 損益表 financials :**

financials 屬性儲存商品過去四年的損益表 (即營收與獲利虧損情形) : 

\>>> **tw2330.financials**  

[![img](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi4UIKzAxqwZpouVnjxQ8jj4dgYkbXzEICnrVMAMjUF58aoSFcS5RQa1rB6jR1ab8b2NBsPvnQm_aJPuS2ERqvqPXr3AXegRvcQr6VV7e0mVgSj-sW1WoUqgAl-rHUaLIdZ8-yQf6JXCP3EJmwWnBZYi3R9fFOrq2G_0gV1rVm_ZhGx1Rg10dNQ7EnPeg/s320/yfinance-tw2330.financials.jpg)](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi4UIKzAxqwZpouVnjxQ8jj4dgYkbXzEICnrVMAMjUF58aoSFcS5RQa1rB6jR1ab8b2NBsPvnQm_aJPuS2ERqvqPXr3AXegRvcQr6VV7e0mVgSj-sW1WoUqgAl-rHUaLIdZ8-yQf6JXCP3EJmwWnBZYi3R9fFOrq2G_0gV1rVm_ZhGx1Rg10dNQ7EnPeg/s1091/yfinance-tw2330.financials.jpg)

此資料也可以用 get_financials() 方法取得, 例如 : 

[![img](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiYnynBabZhipaUn2fGdoA3TbqJUoSFjx82T6VdpEvC_OEvGGIMuSc370lonKJlpmCjwKCDynVbQfWlyqzshUfGwa7MFPI_o4vL3vAVtDjiW07iyH9N3T5rvoyePVhCznVCHKbNGIQrNLKVdy-DMGbhQmOnIqhPhEpZTFCSHIhV_8Ryso6RKCnBHEs4tg/s320/yfinance-tsla_get_financials.jpg)](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiYnynBabZhipaUn2fGdoA3TbqJUoSFjx82T6VdpEvC_OEvGGIMuSc370lonKJlpmCjwKCDynVbQfWlyqzshUfGwa7MFPI_o4vL3vAVtDjiW07iyH9N3T5rvoyePVhCznVCHKbNGIQrNLKVdy-DMGbhQmOnIqhPhEpZTFCSHIhV_8Ryso6RKCnBHEs4tg/s1010/yfinance-tsla_get_financials.jpg)

**(6). 資產負債表 financials :**

balance_sheet 屬性儲存商品過去四年的資產負債表 : 

\>>> **tw2330.balance_sheet**   

[![img](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEigFGSJBIyKKXDnffpiBFkLWYqh3IR05MtkiOjGLJAdt4U9GBl7qdBFFu9cU8KcLQlxFhN5anAVc6V0vfOzH4e1rq4s8Fan3uPAazyb3zRNzITIQ4Ys9F5F7u25AXVMaN4yXTr2PXjiQ3A9w_d9m0eWm2-FGfAcYV-QtWFwLvtPYiDQuZ2v-IUw_TDAVg/s320/yfinance-tw2330.balance_sheet.jpg)](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEigFGSJBIyKKXDnffpiBFkLWYqh3IR05MtkiOjGLJAdt4U9GBl7qdBFFu9cU8KcLQlxFhN5anAVc6V0vfOzH4e1rq4s8Fan3uPAazyb3zRNzITIQ4Ys9F5F7u25AXVMaN4yXTr2PXjiQ3A9w_d9m0eWm2-FGfAcYV-QtWFwLvtPYiDQuZ2v-IUw_TDAVg/s1026/yfinance-tw2330.balance_sheet.jpg)

此資料也可以用 get_balance_sheet() 方法取得, 例如 : 

\>>> **tsla.get_balance_sheet()**  

[![img](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi9Lvv7nn0eQ2oQjN4EMgTeF1BbJjslscFkTfIs-ivY-X1gMfeTetgdoo65-LvH0FMt5gonnokn9gM0IRA3aem9UCRVosLvOm8yKeNGX-CckD2n2JzTcmzZKnhz4pn1SLaS6QgAxuHL-QV4JU_AXOuy80jByqn_gTTUjX04S3mC5ZsWeeV-aXpE8eg0dA/s320/yfinance-tsla.get_balance_sheet.jpg)](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi9Lvv7nn0eQ2oQjN4EMgTeF1BbJjslscFkTfIs-ivY-X1gMfeTetgdoo65-LvH0FMt5gonnokn9gM0IRA3aem9UCRVosLvOm8yKeNGX-CckD2n2JzTcmzZKnhz4pn1SLaS6QgAxuHL-QV4JU_AXOuy80jByqn_gTTUjX04S3mC5ZsWeeV-aXpE8eg0dA/s1018/yfinance-tsla.get_balance_sheet.jpg)

**(7). 現金流量表 cashflow :**

cashflow 屬性儲存商品過去四年的現金流量表 : 

\>>> **tw2330.cashflow**  

[![img](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjh14FwFLXEOP-GJwMfvuRoLkOoFk9ioFAreB-HgnhEeC2fZjtXJjSLeVMIiT-5bwV35b-cgtzziqzSpxbYKfyR02EkzvzTQSzNuzydYunIIQ2z6dQy8EqH9hA1ozBci_DkWmQMHpkhmxp0jzUcsyoPgC_gGSsAWHzZQCDW0sA0mx9ZpnOBo9SrBaCW1g/s320/yfinance-tw2330.cashflow.jpg)](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjh14FwFLXEOP-GJwMfvuRoLkOoFk9ioFAreB-HgnhEeC2fZjtXJjSLeVMIiT-5bwV35b-cgtzziqzSpxbYKfyR02EkzvzTQSzNuzydYunIIQ2z6dQy8EqH9hA1ozBci_DkWmQMHpkhmxp0jzUcsyoPgC_gGSsAWHzZQCDW0sA0mx9ZpnOBo9SrBaCW1g/s1217/yfinance-tw2330.cashflow.jpg)

此資料也可以用 get_cashflow() 方法取得, 例如 : 

[![img](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEitSwSrJu96PFTo1yBKjP-4yzI4r4NcTAaRHXRxNmFlJjMXvkH7xM-x8VYZrltdz1Ce42qvumGZU-Q6sekA7h8_wWQITp9I6sMYGwIGu-3saxe62GHIvg_KRZb3gW_tjqQK-2xBzlkt1qabKJkFslXUp14ifibqR1PmPCR96U0RplwX8SupDMOnWGXCOQ/s320/yfinance-tsla.cashflow.jpg)](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEitSwSrJu96PFTo1yBKjP-4yzI4r4NcTAaRHXRxNmFlJjMXvkH7xM-x8VYZrltdz1Ce42qvumGZU-Q6sekA7h8_wWQITp9I6sMYGwIGu-3saxe62GHIvg_KRZb3gW_tjqQK-2xBzlkt1qabKJkFslXUp14ifibqR1PmPCR96U0RplwX8SupDMOnWGXCOQ/s1000/yfinance-tsla.cashflow.jpg)

以上程式碼均可在 Colab 測試, 參考 : 

\# https://github.com/tony1966/colab/blob/main/yfinance_test.ipynb