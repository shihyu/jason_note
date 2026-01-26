"""
數據載入模組
負責從 FinLab 載入台股族群輪動所需的所有數據
"""
from finlab import data
from dotenv import load_dotenv
import os


class DataLoader:
    """FinLab 數據載入器"""

    # 台股 30 個主要族群
    CATEGORIES = [
        '半導體', '電子零組件', '電腦及週邊', '光電業', '通信網路業',
        '電子通路業', '資訊服務業', '其他電子業', '水泥工業', '食品工業',
        '塑膠工業', '紡織纖維', '電機機械', '電器電纜', '化學工業',
        '生技醫療業', '玻璃陶瓷', '造紙工業', '鋼鐵工業', '橡膠工業',
        '汽車工業', '建材營造', '航運業', '觀光事業', '金融', '貿易百貨',
        '油電燃氣業', '文化創意業', '農業科技', '電子商務'
    ]

    def __init__(self, start_date='2020-01-01'):
        """
        初始化數據載入器

        Args:
            start_date: 回測起始日期，格式 'YYYY-MM-DD'
        """
        # 載入環境變數（FinLab API Token）
        load_dotenv()

        self.start_date = start_date
        self._close = None
        self._volume = None
        self._pb_ratio = None

    def get_categories(self):
        """
        取得族群列表

        Returns:
            list: 30 個族群名稱
        """
        return self.CATEGORIES

    def get_close_price(self):
        """
        載入收盤價數據

        Returns:
            DataFrame: 收盤價（index=日期, columns=股票代碼）
        """
        if self._close is None:
            self._close = data.get('price:收盤價')

            # 過濾起始日期
            self._close = self._close[self._close.index >= self.start_date]

        return self._close

    def get_volume(self):
        """
        載入成交量數據

        Returns:
            DataFrame: 成交股數（index=日期, columns=股票代碼）
        """
        if self._volume is None:
            self._volume = data.get('price:成交股數')

            # 過濾起始日期
            self._volume = self._volume[self._volume.index >= self.start_date]

        return self._volume

    def get_pb_ratio(self):
        """
        載入股價淨值比數據

        Returns:
            DataFrame: PB Ratio（index=日期, columns=股票代碼）
        """
        if self._pb_ratio is None:
            self._pb_ratio = data.get('price_earning_ratio:股價淨值比')

            # 過濾起始日期
            self._pb_ratio = self._pb_ratio[self._pb_ratio.index >= self.start_date]

        return self._pb_ratio

    def get_benchmark_return(self):
        """
        載入大盤報酬指數（用於計算相對強弱）

        Returns:
            Series: 加權指數報酬
        """
        import pandas as pd

        benchmark = data.get('benchmark_return:發行量加權股價報酬指數')

        # 確保是 Series（FinLab 可能返回單列 DataFrame）
        if isinstance(benchmark, pd.DataFrame):
            benchmark = benchmark.iloc[:, 0]

        return benchmark[benchmark.index >= self.start_date]
