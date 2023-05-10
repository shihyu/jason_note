import pandas as pd
from order import order
from crawlData import histData
import math


class backTest(order):
    recrawl = False
    print_KBar = False

    liquidation = False
    fundingRate = 0

    def strategy(self):
        if self.position == 0:
            if self.fundingRate < 0:
                self.putMarketOrder(self.capital * 1)
            else:
                self.putMarketOrder(self.capital * -1)
        elif self.position < 0 and self.fundingRate < 0:
            self.putMarketOrder(self.capital * 2)
        elif self.position > 0 and self.fundingRate > 0:
            self.putMarketOrder(self.capital * -2)

    def __init__(self, dataName):
        self.filename = dataName
        self.print_Order = True

    def readData(self):
        self.rawData = pd.read_csv(self.filename, header=0)
        self.rawData['timestamp'] = pd.to_datetime(self.rawData['timestamp'])

    def start(self):
        if self.recrawl:
            history = histData()
            history.complement("BTC", "BTC.csv")
            # history.complement("ETH", "ETH.csv")
        print(f"Start to read data from {self.filename}...")
        self.readData()
        print(f"Start to back test your strategy...")
        for i in range(0, len(self.rawData)):
            # Step 0: Get k bar of this minute
            self.fundingRate = self.rawData.loc[i, 'fundingRate']
            self.open = self.rawData.loc[i, 'open']
            self.close = self.rawData.loc[i, 'close']
            self.high = self.rawData.loc[i, 'high']
            self.low = self.rawData.loc[i, 'low']
            self.vwap = self.rawData.loc[i, 'vwap']
            self.volume = self.rawData.loc[i, 'volume']
            self.timestamp = self.rawData.loc[i, 'timestamp']

            if self.print_KBar:
                self.printKBar()
            if math.isnan(self.vwap):
                continue

            # Step 1: Calculate funding
            if False:
                self.calculateFunding()

            # Step 2: Check liquidation or not
            self.liquidation = self.checkLiquidation()
            if self.liquidation:
                break

            # Step 2: Execute limit order
            self.executeLimitOrder()

            # Step 4: Execute trading strategy
            self.strategy()

        if self.liquidation:
            print("***Your strategy was liquidated.***")
        else:
            print("The back test of your strategy was finished.")
        print("The result of your strategy is:")
        self.printStatus()


if __name__ == '__main__':
    # TODO: VWAP=NA?
    test = backTest("BTC.csv")
    test.start()
