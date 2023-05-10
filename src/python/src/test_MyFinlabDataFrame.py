from finlab import data
import datetime
import numpy as np
import pandas as pd
import finlab
import functools


class MyFinlabDataFrame(pd.DataFrame):
    """回測語法糖
    除了使用熟悉的 Pandas 語法外，我們也提供很多語法糖，讓大家開發程式時，可以用簡易的語法完成複雜的功能，讓開發策略更簡潔！
    我們將所有的語法糖包裹在 `MyFinlabDataFrame` 中，用起來跟 `pd.DataFrame` 一樣，但是多了很多功能！
    只要使用 `finlab.data.get()` 所獲得的資料，皆為 `MyFinlabDataFrame` 格式，
    接下來我們就來看看， `MyFinlabDataFrame` 有哪些好用的語法糖吧！

    當資料日期沒有對齊（例如: 財報 vs 收盤價 vs 月報）時，在使用以下運算符號：`+`, `-`, `*`, `/`, `>`, `>=`, `==`, `<`, `<=`, `&`, `|`, `~`，不需要先將資料對齊，因為 `MyFinlabDataFrame` 會自動幫你處理，以下是示意圖。

    <img src="https://i.ibb.co/pQr5yx5/Screen-Shot-2021-10-26-at-5-32-44-AM.png" alt="Screen-Shot-2021-10-26-at-5-32-44-AM">

    以下是範例：`cond1` 與 `cond2` 分別為「每天」，和「每季」的資料，假如要取交集的時間，可以用以下語法：

    ```py
    from finlab import data
    # 取得 MyFinlabDataFrame
    close = data.get('price:收盤價')
    roa = data.get('fundamental_features:ROA稅後息前')

    # 運算兩個選股條件交集
    cond1 = close > 37
    cond2 = roa > 0
    cond_1_2 = cond1 & cond2

    擷取 1101 台泥 的訊號如下圖，可以看到 `cond1` 跟 `cond2` 訊號的頻率雖然不相同，但是由於 `cond1` 跟 `cond2` 是 `MyFinlabDataFrame`，所以可以直接取交集，而不用處理資料頻率對齊的問題。
    <br />
    <img src="https://i.ibb.co/m9chXSQ/imageconds.png" alt="imageconds">
    
    總結來說，MyFinlabDataFrame 與一般 dataframe 唯二不同之處：
    1. 多了一些 method，如`df.is_largest()`, `df.sustain()`...等。
    2. 在做四則運算、不等式運算前，會將 df1、df2 的 index 取聯集，column 取交集。
    """

    @property
    def _constructor(self):
        return MyFinlabDataFrame

    @staticmethod
    def reshape(df1, df2):

        isfdf1 = isinstance(df1, MyFinlabDataFrame)
        isfdf2 = isinstance(df2, MyFinlabDataFrame)
        isdf1 = isinstance(df1, pd.DataFrame)
        isdf2 = isinstance(df2, pd.DataFrame)

        both_are_dataframe = (isfdf1 + isdf1) * (isfdf2 + isdf2) != 0

        d1_index_freq = df1.get_index_str_frequency() if isfdf1 else None
        d2_index_freq = df2.get_index_str_frequency() if isfdf2 else None

        if (
            (d1_index_freq or d2_index_freq)
            and (d1_index_freq != d2_index_freq)
            and both_are_dataframe
        ):

            df1 = df1.index_str_to_date() if isfdf1 else df1
            df2 = df2.index_str_to_date() if isfdf2 else df2

        if isinstance(df2, pd.Series):
            df2 = pd.DataFrame({c: df2 for c in df1.columns})

        if both_are_dataframe:
            index = df1.index.union(df2.index)
            columns = df1.columns.intersection(df2.columns)

            if len(df1.index) * len(df2.index) != 0:
                index_start = max(df1.index[0], df2.index[0])
                index = [t for t in index if index_start <= t]

            return (
                df1.reindex(index=index, method="ffill")[columns],
                df2.reindex(index=index, method="ffill")[columns],
            )
        else:
            return df1, df2

    def __lt__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__lt__(df1, df2)

    def __gt__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__gt__(df1, df2)

    def __le__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__le__(df1, df2)

    def __ge__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__ge__(df1, df2)

    def __eq__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__eq__(df1, df2)

    def __ne__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__ne__(df1, df2)

    def __sub__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__sub__(df1, df2)

    def __add__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__add__(df1, df2)

    def __mul__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__mul__(df1, df2)

    def __truediv__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__truediv__(df1, df2)

    def __rshift__(self, other):
        return self.shift(-other)

    def __lshift__(self, other):
        return self.shift(other)

    def __and__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__and__(df1, df2)

    def __or__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__or__(df1, df2)

    def __getitem__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__getitem__(df1, df2)

    def index_str_to_date(self):
        """財務月季報索引格式轉換
    
        將以下資料的索引轉換成datetime格式:
    
        月營收 (ex:2022-M1) 從文字格式轉為公告截止日。
    
        財務季報 (ex:2022-Q1) 從文字格式轉為財報電子檔資料上傳日。
    
        通常使用情境為對不同週期的dataframe做reindex，常用於以公告截止日作為訊號產生日。
    
        Returns:
          (pd.DataFrame): data
        Examples:
    
            ```py
            data.get('monthly_revenue:當月營收').index_str_to_date()
            data.get('financial_statement:現金及約當現金').index_str_to_date()
            ```
      """
        if len(self.index) == 0 or not isinstance(self.index[0], str):
            return self

        if self.index[0].find("M") != -1:
            return self._index_str_to_date_month()
        elif self.index[0].find("Q") != -1:
            return self._index_str_to_date_season()

        return self

    @staticmethod
    def to_business_day(date):
        def skip_weekend(d):
            add_days = {5: 2, 6: 1}
            wd = d.weekday()
            if wd in add_days:
                d += datetime.timedelta(days=add_days[wd])
            return d

        close = data.get("price:收盤價")
        return (
            pd.Series(date)
            .apply(
                lambda d: skip_weekend(d)
                if d in close.index or d < close.index[0] or d > close.index[-1]
                else close.loc[d:].index[0]
            )
            .values
        )

    def get_index_str_frequency(self):

        if len(self.index) == 0:
            return None

        if not isinstance(self.index[0], str):
            return None

        if (self.index.str.find("M") != -1).all():
            return "month"

        if (self.index.str.find("Q") != -1).all():
            return "season"

        return None

    def _index_date_to_str_month(self):

        # index is already str
        if len(self.index) == 0 or not isinstance(self.index[0], pd.Timestamp):
            return self

        index = (self.index - datetime.timedelta(days=30)).strftime("%Y-M%m")
        return MyFinlabDataFrame(self.values, index=index, columns=self.columns)

    def _index_str_to_date_month(self):

        # index is already timestamps
        if len(self.index) == 0 or not isinstance(self.index[0], str):
            return self

        if not (self.index.str.find("M") != -1).all():
            logger.warning(
                "MyFinlabDataFrame: invalid index, cannot format index to monthly timestamp."
            )
            return self

        index = (
            pd.to_datetime(self.index, format="%Y-M%m")
            + pd.offsets.MonthBegin()
            + datetime.timedelta(days=9)
        )
        # chinese new year and covid-19 impact monthly revenue deadline
        replacements = {
            datetime.datetime(2020, 2, 10): datetime.datetime(2020, 2, 15),
            datetime.datetime(2021, 2, 10): datetime.datetime(2021, 2, 15),
            datetime.datetime(2022, 2, 10): datetime.datetime(2022, 2, 14),
        }
        replacer = replacements.get
        index = [replacer(n, n) for n in index]

        index = self.to_business_day(index)

        ret = MyFinlabDataFrame(self.values, index=index, columns=self.columns)
        ret.index.name = "date"

        return ret

    def _index_date_to_str_season(self):

        # index is already str
        if len(self.index) == 0 or not isinstance(self.index[0], pd.Timestamp):
            return self

        q = (
            self.index.strftime("%m")
            .astype(int)
            .map({5: 1, 8: 2, 9: 2, 10: 3, 11: 3, 3: 4, 4: 4})
        )
        year = self.index.year.copy()
        year -= q == 4
        index = year.astype(str) + "-Q" + q.astype(str)

        return MyFinlabDataFrame(self.values, index=index, columns=self.columns)

    def deadline(self):
        """財務季報索引轉換成公告截止日
    
          將財務季報 (ex:2022Q1) 從文字格式轉為公告截止日的datetime格式，
          通常使用情境為對不同週期的dataframe做reindex，常用於以公告截止日作為訊號產生日。
          Returns:
            (pd.DataFrame): data
          Examples:
              ```py
              data.get('financial_statement:現金及約當現金').deadline()
              ```
        """
        return self._index_str_to_date_season(detail=False)

    def _index_str_to_date_season(self, detail=True):

        disclosure_dates = calc_disclosure_dates(detail).reindex_like(self).unstack()

        self.columns.name = "stock_id"

        unstacked = self.unstack()

        ret = (
            pd.DataFrame(
                {"value": unstacked.values, "disclosures": disclosure_dates.values,},
                unstacked.index,
            )
            .reset_index()
            .drop_duplicates(["disclosures", "stock_id"])
            .pivot(index="disclosures", columns="stock_id", values="value")
            .ffill()
            .pipe(lambda df: df.loc[df.index.notna()])
            .pipe(lambda df: MyFinlabDataFrame(df))
            .rename_axis("date")
        )

        if not detail:
            ret.index = self.to_business_day(ret.index)

        return ret

    def average(self, n):
        """取 n 筆移動平均
    
        若股票在時間窗格內，有 N/2 筆 NaN，則會產生 NaN。
        Args:
          n (positive-int): 設定移動窗格數。
        Returns:
          (pd.DataFrame): data
        Examples:
            股價在均線之上
            ```py
            from finlab import data
            close = data.get('price:收盤價')
            sma = close.average(10)
            cond = close > sma
            ```
            只需要簡單的語法，就可以將其中一部分的訊號繪製出來檢查：
            ```py
            import matplotlib.pyplot as plt
    
            close.loc['2021', '2330'].plot()
            sma.loc['2021', '2330'].plot()
            cond.loc['2021', '2330'].mul(20).add(500).plot()
    
            plt.legend(['close', 'sma', 'cond'])
            ```
            <img src="https://i.ibb.co/Mg1P85y/sma.png" alt="sma">
        """
        return self.rolling(n, min_periods=int(n / 2)).mean()

    def is_largest(self, n):
        """取每列前 n 筆大的數值
    
        若符合 `True` ，反之為 `False` 。用來篩選每天數值最大的股票。
    
        <img src="https://i.ibb.co/8rh3tbt/is-largest.png" alt="is-largest">
        Args:
          n (positive-int): 設定每列前 n 筆大的數值。
        Returns:
          (pd.DataFrame): data
        Examples:
            每季 ROA 前 10 名的股票
            ```py
            from finlab import data
    
            roa = data.get('fundamental_features:ROA稅後息前')
            good_stocks = roa.is_largest(10)
            ```
        """
        return (
            self.astype(float)
            .apply(lambda s: s.nlargest(n), axis=1)
            .reindex_like(self)
            .notna()
        )

    def is_smallest(self, n):
        """取每列前 n 筆小的數值
    
        若符合 `True` ，反之為 `False` 。用來篩選每天數值最小的股票。
        Args:
          n (positive-int): 設定每列前 n 筆小的數值。
        Returns:
          (pd.DataFrame): data
        Examples:
            股價淨值比最小的 10 檔股票
            ```py
            from finlab import data
    
            pb = data.get('price_earning_ratio:股價淨值比')
            cheap_stocks = pb.is_smallest(10)
            ```
        """
        return (
            self.astype(float)
            .apply(lambda s: s.nsmallest(n), axis=1)
            .reindex_like(self)
            .notna()
        )

    def is_entry(self):
        """進場點
    
        取進場訊號點，若符合條件的值則為True，反之為False。
        Returns:
          (pd.DataFrame): data
        Examples:
          策略為每日收盤價前10高，取進場點。
            ```py
            from finlab import data
            data.get('price:收盤價').is_largest(10).is_entry()
            ```
        """
        return self & ~self.shift(fill_value=False)

    def is_exit(self):
        """出場點
    
        取出場訊號點，若符合條件的值則為 True，反之為 False。
        Returns:
          (pd.DataFrame): data
        Examples:
          策略為每日收盤價前10高，取出場點。
            ```py
            from finlab import data
            data.get('price:收盤價').is_largest(10).is_exit()
            ```
        """
        return ~self & self.shift(fill_value=False)

    def rise(self, n=1):
        """數值上升中
    
        取是否比前第n筆高，若符合條件的值則為True，反之為False。
        <img src="https://i.ibb.co/Y72bN5v/Screen-Shot-2021-10-26-at-6-43-41-AM.png" alt="Screen-Shot-2021-10-26-at-6-43-41-AM">
        Args:
          n (positive-int): 設定比較前第n筆高。
        Returns:
          (pd.DataFrame): data
        Examples:
            收盤價是否高於10日前股價
            ```py
            from finlab import data
            data.get('price:收盤價').rise(10)
            ```
        """
        return self > self.shift(n)

    def fall(self, n=1):
        """數值下降中
    
        取是否比前第n筆低，若符合條件的值則為True，反之為False。
        <img src="https://i.ibb.co/Y72bN5v/Screen-Shot-2021-10-26-at-6-43-41-AM.png" alt="Screen-Shot-2021-10-26-at-6-43-41-AM">
        Args:
          n (positive-int): 設定比較前第n筆低。
        Returns:
          (pd.DataFrame): data
        Examples:
            收盤價是否低於10日前股價
            ```py
            from finlab import data
            data.get('price:收盤價').fall(10)
            ```
        """
        return self < self.shift(n)

    def groupby_category(self):
        """資料按產業分群
    
        類似 `pd.DataFrame.groupby()`的處理效果。
        Returns:
          (pd.DataFrame): data
        Examples:
          半導體平均股價淨值比時間序列
            ```py
            from finlab import data
            pe = data.get('price_earning_ratio:股價淨值比')
            pe.groupby_category().mean()['半導體'].plot()
            ```
            <img src="https://i.ibb.co/Tq2fKBp/pbmean.png" alt="pbmean">
    
            全球 2020 量化寬鬆加上晶片短缺，使得半導體股價淨值比衝高。
        """
        categories = data.get("security_categories")
        cat = categories.set_index("stock_id").category.to_dict()
        org_set = set(cat.values())
        set_remove_illegal = set(
            o for o in org_set if isinstance(o, str) and o != "nan"
        )
        set_remove_illegal

        refine_cat = {}
        for s, c in cat.items():
            if c == None or c == "nan":
                refine_cat[s] = "其他"
                continue

            if c == "電腦及週邊":
                refine_cat[s] = "電腦及週邊設備業"
                continue

            if c[-1] == "業" and c[:-1] in set_remove_illegal:
                refine_cat[s] = c[:-1]
            else:
                refine_cat[s] = c

        col_categories = pd.Series(
            self.columns.map(lambda s: refine_cat[s] if s in cat else "其他")
        )

        return self.groupby(col_categories.values, axis=1)

    def entry_price(self, trade_at="close"):

        signal = self.is_entry()
        adj = (
            data.get("etl:adj_close")
            if trade_at == "close"
            else data.get("etl:adj_open")
        )
        adj, signal = adj.reshape(adj.loc[signal.index[0] : signal.index[-1]], signal)
        return adj.bfill()[signal.shift(fill_value=False)].ffill()

    def sustain(self, nwindow, nsatisfy=None):
        """持續 N 天滿足條件
    
        取移動 nwindow 筆加總大於等於nsatisfy，若符合條件的值則為True，反之為False。
    
        Args:
          nwindow (positive-int): 設定移動窗格。
          nsatisfy (positive-int): 設定移動窗格計算後最低滿足數值。
        Returns:
          (pd.DataFrame): data
        Examples:
            收盤價是否連兩日上漲
            ```py
            from finlab import data
            data.get('price:收盤價').rise().sustain(2)
            ```
        """
        nsatisfy = nsatisfy or nwindow
        return self.rolling(nwindow).sum() >= nsatisfy

    def industry_rank(self, categories=None):
        """計算產業 ranking 排名，0 代表產業內最低，1 代表產業內最高
        Args:
          categories (list of str): 欲考慮的產業，ex: ['貿易百貨', '雲端運算']，預設為全產業，請參考 `data.get('security_industry_themes')` 中的產業項目。
        Examples:
            本意比產業排名分數
            ```py
            from finlab import data
    
            pe = data.get('price_earning_ratio:本益比')
            pe_rank = pe.industry_rank()
            print(pe_rank)
            ```
        """

        themes = (
            data.get("security_industry_themes")
            .copy()  # 複製
            .assign(
                category=lambda self: self.category.apply(lambda s: eval(s))
            )  # 從文字格式轉成陣列格
            .explode("category")  # 展開資料
        )

        categories = categories or set(
            themes.category[themes.category.str.find(":") == -1]
        )

        def calc_rank(ind):
            stock_ids = themes.stock_id[themes.category == ind]
            return self[stock_ids].pipe(lambda self: self.rank(axis=1, pct=True))

        return (
            pd.concat([calc_rank(ind) for ind in categories], axis=1)
            .groupby(level=0, axis=1)
            .mean()
        )

    def quantile_row(self, c):
        """股票當天數值分位數
    
        取得每列c定分位數的值。
        Args:
          c (positive-int): 設定每列 n 定分位數的值。
        Returns:
          (pd.DataFrame): data
        Examples:
            取每日股價前90％分位數
            ```py
            from finlab import data
            data.get('price:收盤價').quantile_row(0.9)
            ```
        """
        s = self.quantile(c, axis=1)
        return s

    def exit_when(self, exit):

        df, exit = self.reshape(self, exit)

        df.fillna(False, inplace=True)
        exit.fillna(False, inplace=True)

        entry_signal = df.is_entry()
        exit_signal = df.is_exit()
        exit_signal |= exit

        # build position using entry_signal and exit_signal
        position = pd.DataFrame(np.nan, index=df.index, columns=df.columns)
        position[entry_signal] = 1
        position[exit_signal] = 0

        position.ffill(inplace=True)
        position = position == 1
        position.fillna(False)
        return position

    def hold_until(
        self,
        exit,
        nstocks_limit=None,
        stop_loss=-np.inf,
        take_profit=np.inf,
        trade_at="close",
        rank=None,
    ):
        """訊號進出場
    
        這大概是所有策略撰寫中，最重要的語法糖，上述語法中 `entries` 為進場訊號，而 `exits` 是出場訊號。所以 `entries.hold_until(exits)` ，就是進場訊號為 `True` 時，買入並持有該檔股票，直到出場訊號為 `True ` 則賣出。
        <img src="https://i.ibb.co/PCt4hPd/Screen-Shot-2021-10-26-at-6-35-05-AM.png" alt="Screen-Shot-2021-10-26-at-6-35-05-AM">
        此函式有很多細部設定，可以讓你最多選擇 N 檔股票做輪動。另外，當超過 N 檔進場訊號發生，也可以按照客制化的排序，選擇優先選入的股票。最後，可以設定價格波動當輪動訊號，來增加出場的時機點。
    
        Args:
          exit (pd.Dataframe): 出場訊號。
          nstocks_limit (int)`: 輪動檔數上限，預設為None。
          stop_loss (float): 價格波動輪動訊號，預設為None，不生成輪動訊號。範例：0.1，代表成本價下跌 10% 時產生出場訊號。
          take_profit (float): 價格波動輪動訊號，預設為None，不生成輪動訊號。範例：0.1，代表成本價上漲 10% 時產生出場訊號。
          trade_at (str): 價格波動輪動訊號參考價，預設為'close'。可選 `close` 或 `open`。
          rank (pd.Dataframe): 當天進場訊號數量超過 nstocks_limit 時，以 rank 數值越大的股票優先進場。
        Returns:
          (pd.DataFrame): data
        Examples:
            價格 > 20 日均線入場, 價格 < 60 日均線出場，最多持有10檔，超過 10 個進場訊號，則以股價淨值比小的股票優先選入。
    
            ```python
            from finlab import data
            from finlab.backtest import sim
    
            close = data.get('price:收盤價')
            pb = data.get('price_earning_ratio:股價淨值比')
    
            sma20 = close.average(20)
            sma60 = close.average(60)
    
            entries = close > sma20
            exits = close < sma60
    
            ＃pb前10小的標的做輪動
            position = entries.hold_until(exits, nstocks_limit=10, rank=-pb)
            sim(position)
            ```
        """
        if nstocks_limit is None:
            nstocks_limit = len(self.columns)

        union_index = self.index.union(exit.index)
        intersect_col = self.columns.intersection(exit.columns)

        if stop_loss != -np.inf or take_profit != np.inf:
            price = data.get(f"etl:adj_{trade_at}")
            union_index = union_index.union(
                price.loc[union_index[0] : union_index[-1]].index
            )
            intersect_col = intersect_col.intersection(price.columns)
        else:
            price = pd.DataFrame()

        if rank is not None:
            union_index = union_index.union(rank.index)
            intersect_col = intersect_col.intersection(rank.columns)

        entry = (
            self.reindex(union_index, columns=intersect_col, method="ffill")
            .ffill()
            .fillna(False)
        )
        exit = (
            exit.reindex(union_index, columns=intersect_col, method="ffill")
            .ffill()
            .fillna(False)
        )

        if price is not None:
            price = price.reindex(union_index, columns=intersect_col, method="ffill")

        if rank is not None:
            rank = rank.reindex(union_index, columns=intersect_col, method="ffill")
        else:
            rank = pd.DataFrame(1, index=union_index, columns=intersect_col)

        max_rank = rank.max().max()
        min_rank = rank.min().min()
        rank = (rank - min_rank) / (max_rank - min_rank)
        rank.fillna(0, inplace=True)

        def rotate_stocks(
            ret,
            entry,
            exit,
            nstocks_limit,
            stop_loss=-np.inf,
            take_profit=np.inf,
            price=None,
            ranking=None,
        ):

            nstocks = 0

            ret[0][np.argsort(entry[0])[-nstocks_limit:]] = 1
            ret[0][exit[0] == 1] = 0
            ret[0][entry[0] == 0] = 0

            entry_price = np.empty(entry.shape[1])
            entry_price[:] = np.nan

            for i in range(1, entry.shape[0]):

                # regitser entry price
                if stop_loss != -np.inf or take_profit != np.inf:
                    is_entry = (ret[i - 2] == 0) if i > 1 else (ret[i - 1] == 1)

                    is_waiting_for_entry = np.isnan(entry_price) & (ret[i - 1] == 1)

                    is_entry |= is_waiting_for_entry

                    entry_price[is_entry == 1] = price[i][is_entry == 1]

                    # check stop_loss and take_profit
                    returns = price[i] / entry_price
                    stop = (returns > 1 + abs(take_profit)) | (
                        returns < 1 - abs(stop_loss)
                    )
                    exit[i] |= stop

                # run signal
                rank = entry[i] * ranking[i] + ret[i - 1] * 3
                rank[exit[i] == 1] = -1
                rank[(entry[i] == 0) & (ret[i - 1] == 0)] = -1

                ret[i][np.argsort(rank)[-nstocks_limit:]] = 1
                ret[i][rank == -1] = 0

            return ret

        ret = pd.DataFrame(0, index=entry.index, columns=entry.columns)
        ret = rotate_stocks(
            ret.values,
            entry.astype(int).values,
            exit.astype(int).values,
            nstocks_limit,
            stop_loss,
            take_profit,
            price=price.values,
            ranking=rank.values,
        )

        return pd.DataFrame(ret, index=entry.index, columns=entry.columns)


@functools.lru_cache
def calc_disclosure_dates(detail=True):

    cinfo = data.get("company_basic_info").copy()
    cinfo["id"] = cinfo.stock_id.str.split(" ").str[0]
    cinfo = cinfo.set_index("id")
    cinfo = cinfo[~cinfo.index.duplicated(keep="last")]

    def calc_default_disclosure_dates(s):
        sid = s.name
        cat = cinfo.loc[sid].產業類別 if sid in cinfo.index else "etf"
        short_name = cinfo.loc[sid].公司簡稱 if sid in cinfo.index else "etf"

        if cat == "金融業":
            calendar = {
                "1": "-05-15",
                "2": "-08-31",
                "3": "-11-14",
                "4": "-03-31",
            }
        elif cat == "金融保險業":
            calendar = {
                "1": "-04-30",
                "2": "-08-31",
                "3": "-10-31",
                "4": "-03-31",
            }
        elif "KY" in short_name:
            calendar = {
                "old": {"1": "-05-15", "2": "-08-14", "3": "-11-14", "4": "-03-31",},
                "new": {"1": "-05-15", "2": "-08-31", "3": "-11-14", "4": "-03-31",},
            }
        else:
            calendar = {
                "1": "-05-15",
                "2": "-08-14",
                "3": "-11-14",
                "4": "-03-31",
            }
        get_year = (
            lambda year, season: str(year) if int(season) != 4 else str(int(year) + 1)
        )
        ky_policy_check = lambda year: "new" if year >= "2021" else "old"
        return pd.to_datetime(
            s.index.map(
                lambda d: get_year(d[:4], d[-1])
                + calendar[ky_policy_check(d[:4])][d[-1]]
            )
            if "KY" in short_name
            else s.index.map(lambda d: get_year(d[:4], d[-1]) + calendar[d[-1]])
        )

    def season_end(s):

        calendar = {
            "1": "-3-31",
            "2": "-6-30",
            "3": "-9-30",
            "4": "-12-31",
        }
        return pd.to_datetime(s.index.map(lambda d: d[:4] + calendar[d[-1]]))

    disclosure_dates = data.get("financial_statements_upload_detail:upload_date")
    disclosure_dates = disclosure_dates.apply(pd.to_datetime)

    financial_season_end = disclosure_dates.apply(season_end)
    default_disclosure_dates = disclosure_dates.apply(calc_default_disclosure_dates)

    disclosure_dates[
        (disclosure_dates > default_disclosure_dates)
        | (disclosure_dates < financial_season_end)
    ] = pd.NaT
    disclosure_dates[(disclosure_dates.diff() <= datetime.timedelta(days=0))] = pd.NaT
    disclosure_dates.loc["2019-Q1", "3167"] = pd.NaT
    disclosure_dates.loc["2015-Q1", "5536"] = pd.NaT
    disclosure_dates.loc["2018-Q1", "5876"] = pd.NaT

    disclosure_dates = disclosure_dates.fillna(default_disclosure_dates)
    disclosure_dates.columns.name = "stock_id"

    if detail:
        return disclosure_dates
    return default_disclosure_dates


if __name__ == "__main__":
    # finlab.login("")
    # close = data.get("price:收盤價")
    # close = MyFinlabDataFrame(close)
    # rev = data.get("monthly_revenue:當月營收")
    # rev = MyFinlabDataFrame(rev)

    ## 股價創年新高
    # cond1 = close == close.rolling(250).max()

    ## 確認營收底部，近月營收脫離近年穀底(連續3月的"單月營收近12月最小值/近月營收" < 0.8)
    # cond4 = ((rev.rolling(12).min()) / (rev) < 0.8).sustain(3)
    # print(cond1)
    # print(cond4)
    # print(cond1 & cond4)

    df = MyFinlabDataFrame(
        np.random.randint(0, 100, size=(10, 5)), columns=list("BCDEH")
    )
    df1 = MyFinlabDataFrame(
        np.random.randint(0, 100, size=(5, 4)), columns=list("ABCD")
    )
    df = df > 50
    df1 = df1 > 50
    print(df)
    print(df1)
    print(df & df1)
