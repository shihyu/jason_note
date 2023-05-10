import talib as ta
import pandas as pd


class TI():

    def __init__(self) -> None:
        pass

    def ema(self, base: list, length: int):
        alpha = 2 / (length + 1)
        ls = []
        for i in range(length):
            if i == length - 1:
                ls.append(base[i] * (1 - alpha)**i)
                break
            else:
                ls.append(base[i] * alpha * (1 - alpha)**i)

        return sum(ls)

    def tr(self, bars_list: list):  # list 新到舊
        '''
        輸入包含kbars的list
        '''
        ls = []

        for i in range(len(bars_list) - 1):
            tr = max(
                float(bars_list[i]['high']) - float(bars_list[i]['low']),
                abs(float(bars_list[i]['high']) - float(bars_list[i+1]['close'])),
                abs(float(bars_list[i]['low']) - float(bars_list[i+1]['close']))
                )
            ls.append(tr)
        return ls

    def atr(self, kbars_list: list, length: int):
        '''
        length should < len(kbars_list)
        '''
        each_tr = self.tr(kbars_list)
        average_tr = self.ema(each_tr, length)

        return average_tr

    def lastest_sma(self, kbar_list: list, length: int):
        df_kbar = pd.DataFrame(kbar_list)
        df_kbar = df_kbar.set_index('timestamp')
        out = ta.SMA(df_kbar.close, timeperiod=length)
        print(float(out[-1:]))
