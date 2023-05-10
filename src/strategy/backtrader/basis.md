# Backtrader交易基礎

查看帳戶情況：

```python
class TestStrategy(bt.Strategy):
    def next(self):
        print('當前可用資金', self.broker.getcash())
        print('當前總資產', self.broker.getvalue())
        print('當前持倉量', self.broker.getposition(self.data).size)
        print('當前持倉成本', self.broker.getposition(self.data).price)
        # 也可以直接獲取持倉
        print('當前持倉量', self.getposition(self.data).size)
        print('當前持倉成本', self.getposition(self.data).price)
        # 註：getposition() 需要指定具體的標的資料集
```

滑點設定：

```python
# 方式1：通過 BackBroker 類中的 slip_perc 參數設定百分比滑點
cerebro.broker = bt.brokers.BackBroker(slip_perc=0.0001)
# 方式2：通過呼叫 brokers 的 set_slippage_perc 方法設定百分比滑點
cerebro.broker.set_slippage_perc(perc=0.0001)

# 方式1：通過 BackBroker 類中的 slip_fixed 參數設定固定滑點
cerebro.broker = bt.brokers.BackBroker(slip_fixed=0.001)
# 方式2：通過呼叫 brokers 的 set_slippage_fixed 方法設定固定滑點
cerebro.broker = cerebro.broker.set_slippage_fixed(fixed=0.001)
```

參數說明：

有關滑點的其他設定
slip_open：是否對開盤價做滑點處理，該參數在 BackBroker() 類中默認為 False，在 set_slippage_perc 和set_slippage_fixed 方法中默認為 True；
slip_match：是否將滑點處理後的新成交價與成交當天的價格區間 low ~ high 做匹配，如果為 True，則根據新成交價重新匹配調整價格區間，確保訂單能被執行；如果為 False，則不會與價格區間做匹配，訂單不會執行，但會在下一日執行一個空訂單；默認取值為 True；
slip_out：如果新成交價高於最高價或低於最高價，是否以超出的價格成交，如果為 True，則允許以超出的價格成交；如果為 False，實際成交價將被限制在價格區間內  low ~ high；默認取值為 False；
slip_limit：是否對限價單執行滑點，如果為 True，即使 slip_match 為Fasle，也會對價格做匹配，確保訂單被執行；如果為 False，則不做價格匹配；默認取值為 True。

```python
# 情況1：
set_slippage_fixed(fixed=0.35,
                   slip_open=False,
                   slip_match=True,
                   slip_out=False)
# 由於 slip_open=False ，不會對開盤價做滑點處理，所以仍然以原始開盤價 32.63307367 成交

# 情況2：
set_slippage_fixed(fixed=0.35,
                   slip_open=True,
                   slip_match=True,
                   slip_out=False)

# 情況3：
set_slippage_fixed(fixed=0.35,
                   slip_open=True,
                   slip_match=True,
                   slip_out=True)
# 滑點調整的新成交價為 32.63307367+0.35 = 32.98307367，超出了當天最高價 32.94151482
# 允許做價格匹配 slip_match=True, 而且運行以超出價格區間的新成交價執行 slip_out=True
# 最終以新成交價 32.98307367 成交

# 情況4：
set_slippage_fixed(fixed=0.35,
                   slip_open=True,
                   slip_match=False,
                   slip_out=True)
# 滑點調整的新成交價為 32.63307367+0.35 = 32.98307367，超出了當天最高價 32.94151482
# 由於不進行價格匹配 slip_match=False，新成交價超出價格區間無法成交
# 2019-01-17 這一天訂單不會執行，但會在下一日 2019-01-18 執行一個空訂單
# 再往後的 2019-07-02，也未執行訂單，下一日 2019-07-03 執行空訂單
# 即使 2019-07-03的 open 39.96627412+0.35 < high 42.0866713 滿足成交條件，也不會補充成交
```

交易稅費管理

股票：目前 A 股的交易費用分為 2 部分：佣金和印花稅，
其中佣金雙邊徵收，不同證券公司收取的佣金各不相同，一般在 0.02%-0.03% 左右，單筆佣金不少於 5 元；
印花稅只在賣出時收取，稅率為 0.1%。


期貨：期貨交易費用包括交易所收取手續費和期貨公司收取佣金 2 部分，交易所手續費較為固定，
不同期貨公司佣金不一致，而且不同期貨品種的收取方式不相同，有的按照固定費用收取，有的按成交金額的固定百分比收取：
合約現價*合約乘數*手續費費率。除了交易費用外，期貨交易時還需上交一定比例的保證金 。



Backtrader 也提供了多種交易費設定方式，既可以簡單的通過參數進行設定，也可以結合交易條件自訂費用函數：

根據交易品種的不同，Backtrader 將交易費用分為 股票 Stock-like 模式和期貨 Futures-like 種模式；
根據計算方式的不同，Backtrader 將交易費用分為 PERC 百分比費用模式 和 FIXED 固定費用模式 ；

Stock-like 模式與 PERC 百分比費用模式對應，期貨 Futures-like 與 FIXED 固定費用模式對應；

在設定交易費用時，最常涉及如下 3 個參數：

commission：手續費 / 佣金；

mult：乘數；

margin：保證金 / 保證金比率 。

雙邊徵收：買入和賣出操作都要收取相同的交易費用 。

```python
cerebro.broker.setcommission(
    # 交易手續費，根據margin取值情況區分是百分比手續費還是固定手續費
    commission=0.0,
    # 期貨保證金，決定著交易費用的類型,只有在stocklike=False時起作用
    margin=None,
    # 乘數，盈虧會按該乘數進行放大
    mult=1.0,
    # 交易費用計算方式，取值有：
    # 1.CommInfoBase.COMM_PERC 百分比費用
    # 2.CommInfoBase.COMM_FIXED 固定費用
    # 3.None 根據 margin 取值來確定類型
    commtype=None,
    # 當交易費用處於百分比模式下時，commission 是否為 % 形式
    # True，表示不以 % 為單位，0.XX 形式；False，表示以 % 為單位，XX% 形式
    percabs=True,
    # 是否為股票模式，該模式通常由margin和commtype參數決定
    # margin=None或COMM_PERC模式時，就會stocklike=True，對應股票手續費；
    # margin設定了取值或COMM_FIXED模式時,就會stocklike=False，對應期貨手續費
    stocklike=False,
    # 計算持有的空頭頭寸的年化利息
    # days * price * abs(size) * (interest / 365)
    interest=0.0,
    # 計算持有的多頭頭寸的年化利息
    interest_long=False,
    # 槓桿比率，交易時按該槓桿調整所需現金
    leverage=1.0,
    # 自動計算保證金
    # 如果False,則通過margin參數確定保證金
    # 如果automargin<0,通過mult*price確定保證金
    # 如果automargin>0,如果automargin*price確定保證金
    automargin=False,
    # 交易費用設定作用的資料集(也就是作用的標的)
    # 如果取值為None，則默認作用於所有資料集(也就是作用於所有assets)
    name=None)
```

從上述各參數的含義和作用可知，margin 、commtype、stocklike 存在 2 種默認的組態規則：股票百分比費用、期貨固定費用，具體如下：
第 1 條規則：未設定 margin（即 margin 為 0 / None / False）→ commtype 會指向 COMM_PERC 百分比費用 → 底層的 _stocklike 屬性會設定為 True → 對應的是“股票百分比費用”。
所以如果想為股票設定交易費用，就令 margin = 0 / None / False，或者令 stocklike=True；

第 2 條規則：為 margin 設定了取值 →  commtype 會指向 COMM_FIXED 固定費用 → 底層的 _stocklike 屬性會設定為 False → 對應的是“期貨固定費用”，因為只有期貨才會涉及保證金。
所以如果想為期貨設定交易費用，就需要設定 margin，此外還需令 stocklike=True，margin 參數才會起作用 。



自訂交易費用的例子

```python
# 自訂期貨百分比費用
class CommInfo_Fut_Perc_Mult(bt.CommInfoBase):
    params = (
      ('stocklike', False), # 指定為期貨模式
      ('commtype', bt.CommInfoBase.COMM_PERC), # 使用百分比費用
      ('percabs', False), # commission 以 % 為單位
    )

    def _getcommission(self, size, price, pseudoexec):
        # 計算交易費用
        return (abs(size) * price) * (self.p.commission/100) * self.p.mult
    # pseudoexec 用於提示當前是否在真實統計交易費用
    # 如果只是試算費用，pseudoexec=False
    # 如果是真實的統計費用，pseudoexec=True

comminfo = CommInfo_Fut_Perc_Mult(
    commission=0.1, # 0.1%
    mult=10,
    margin=2000) # 實例化
cerebro.broker.addcommissioninfo(comminfo)

# 上述自訂函數，也可以通過 setcommission 來實現
cerebro.broker.setcommission(commission=0.1, #0.1%
                             mult=10,
                             margin=2000,
                             percabs=False,
                             commtype=bt.CommInfoBase.COMM_PERC,
                             stocklike=False)
```

下面是考慮佣金和印花稅的股票百分比費用：

```python
class StockCommission(bt.CommInfoBase):
    params = (
      ('stocklike', True), # 指定為期貨模式
      ('commtype', bt.CommInfoBase.COMM_PERC), # 使用百分比費用模式
      ('percabs', True), # commission 不以 % 為單位
      ('stamp_duty', 0.001),) # 印花稅默認為 0.1%
    
    # 自訂費用計算公式
      def _getcommission(self, size, price, pseudoexec):
            if size > 0: # 買入時，只考慮佣金
                return abs(size) * price * self.p.commission
            elif size < 0: # 賣出時，同時考慮佣金和印花稅
        return abs(size) * price * (self.p.commission + self.p.stamp_duty)
            else:
                return 0
```

成交量限制管理

形式1：bt.broker.fillers.FixedSize(size) 

通過 FixedSize() 方法設定最大的固定成交量：size，該種模式下的成交量限制規則如下：

訂單實際成交量的確定規則：取（size、訂單執行那天的 volume 、訂單中要求的成交數量）中的最小者；

訂單執行那天，如果訂單中要求的成交數量無法全部滿足，則只成交部分數量。第二天不會補單。

```python
# 通過 BackBroker() 類直接設定
cerebro = Cerebro()
filler = bt.broker.fillers.FixedSize(size=xxx)
newbroker = bt.broker.BrokerBack(filler=filler)
cerebro.broker = newbroker

# 通過 set_filler 方法設定
cerebro = Cerebro()
cerebro.broker.set_filler(bt.broker.fillers.FixedSize(size=xxx))

# self.order = self.buy(size=2000) # 每次買入 2000 股
# cerebro.broker.set_filler(bt.broker.fillers.FixedSize(size=3000)) # 固定最大成交量
```

形式2：bt.broker.fillers.FixedBarPerc(perc)

通過 FixedBarPerc(perc) 將 訂單執行當天 bar 的總成交量 volume 的 perc % 設定為最大的固定成交量，該模式的成交量限制規則如下：

訂單實際成交量的確定規則：取 （volume * perc /100、訂單中要求的成交數量） 的 最小者；
訂單執行那天，如果訂單中要求的成交數量無法全部滿足，則只成交部分數量。

```python
# 通過 BackBroker() 類直接設定
cerebro = Cerebro()
filler = bt.broker.fillers.FixedBarPerc(perc=xxx)
newbroker = bt.broker.BrokerBack(filler=filler)
cerebro.broker = newbroker

# 通過 set_filler 方法設定
cerebro = Cerebro()
cerebro.broker.set_filler(bt.broker.fillers.FixedBarPerc(perc=xxx))
# perc 以 % 為單位，取值範圍為[0.0,100.0]

# self.order = self.buy(size=2000) # 以下一日開盤價買入2000股
# cerebro.broker.set_filler(bt.broker.fillers.FixedBarPerc(perc=50))
```

形式3：bt.broker.fillers.BarPointPerc(minmov=0.01，perc=100.0)

BarPointPerc() 在考慮了價格區間的基礎上確定成交量，在訂單執行當天，成交量確定規則為：

通過 minmov 將 當天 bar 的價格區間 low ~ high 進行均勻劃分，得到劃分的份數：

part =  (high -low +minmov)  // minmov  （向下取整）

再對當天 bar 的總成交量 volume 也劃分成相同的份數 part ，這樣就能得到每份的平均成交量：

volume_per = volume // part 

最終，volume_per * （perc / 100）就是允許的最大成交量，實際成交時，對比訂單中要求的成交量，就可以得到最終實際成交量

實際成交量 = min ( volume_per * （perc / 100）, 訂單中要求的成交數量 )

```python
# 通過 BackBroker() 類直接設定
cerebro = Cerebro()
filler = bt.broker.fillers.BarPointPerc(minmov=0.01，perc=100.0)
newbroker = bt.broker.BrokerBack(filler=filler)
cerebro.broker = newbroker

# 通過 set_filler 方法設定
cerebro = Cerebro()
cerebro.broker.set_filler(bt.broker.fillers.BarPointPerc(minmov=0.01，perc=100.0))
# perc 以 % 為單位，取值範圍為[0.0,100.0]


# self.order = self.buy(size=2000) # 以下一日開盤價買入2000股

# cerebro.broker.set_filler(bt.broker.fillers.BarPointPerc(minmov=0.1, perc=50)) # 表示 50%
```

交易時機管理
對於交易訂單生成和執行時間，Backtrader 默認是 “當日收盤後下單，次日以開盤價成交”，這種模式在回測過程中能有效避免使用未來資料。
但對於一些特殊的交易場景，比如“all_in”情況下，當日所下訂單中的數量是用當日收盤價計算的（總資金 / 當日收盤價），次日以開盤價執行訂單時，
如果開盤價比昨天的收盤價提高了，就會出現可用資金不足的情況。
為了應對一些特殊交易場景，Backtrader 還提供了一些 cheating 式的交易時機模式：Cheat-On-Open 和 Cheat-On-Close。

Cheat-On-Open

Cheat-On-Open 是“當日下單，當日以開盤價成交”模式，在該模式下，Strategy 中的交易邏輯不再寫在 next() 方法裡，而是寫在特定的 next_open()、nextstart_open() 、prenext_open() 函數中，具體設定可參考如下案例：

方式1：bt.Cerebro(cheat_on_open=True)；
方式2：cerebro.broker.set_coo(True)；
方式3：BackBroker(coo=True)。

Cheat-On-Close

Cheat-On-Close 是“當日下單，當日以收盤價成交”模式，在該模式下，Strategy 中的交易邏輯仍寫在 next() 中，具體設定如下：

方式1：cerebro.broker.set_coc(True)；
方式2：BackBroker(coc=True)

```python
class TestStrategy(bt.Strategy):
    ......
    def next(self):
        # 取消之前未執行的訂單
        if self.order:
            self.cancel(self.order)
        # 檢查是否有持倉
        if not self.position:
            # 10日均線上穿5日均線，買入
            if self.crossover > 0:
                print('{} Send Buy, open {}'.format(self.data.datetime.date(),self.data.open[0]))
                self.order = self.buy(size=100) # 以下一日開盤價買入100股
        # # 10日均線下穿5日均線，賣出
        elif self.crossover < 0:
            self.order = self.close() # 平倉，以下一日開盤價賣出
    ......

# 實例化大腦
cerebro= bt.Cerebro()
.......
# 當日下單，當日收盤價成交
cerebro.broker.set_coc(True)
```