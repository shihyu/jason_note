from kBar import kBar


class status(kBar):
    coin = 'BTC'
    margin = 0.5
    capital = 1000
    turnOver = 0
    position = 0
    positionPrice = 0
    revenueTotal = 0
    revenueTotal_Fee = 0
    revenueTotal_Price = 0
    revenueTotal_Funding = 0
    maxLoss = 0
    liquidationPrice = 0
    lastTradeTime = 0
    print_Funding = True

    def __init__(self, coinUsed='BTC', startCapital=1000):
        self.coin = coinUsed
        if coinUsed == 'BTC':
            self.margin = 0.5  # %
        else:
            self.margin = 1  # %
        self.capital = startCapital

    # Ref:https://kknews.cc/zh-tw/finance/e4ka5ay.html
    # 维持保证金=仓位*开仓价格*2.5%=100000*0.000012*2.5%=0.03
    # 保证金余额=钱包余额-维持保证金=1-0.03=0.97
    # 假设强平价格为X，100000*（0.000012-X）=0.97，X=0.0000023
    def getLiquidationPrice(self):
        maintainMargin = self.capital \
            - self.margin * self.position / 100
        liquidationPrice = self.positionPrice \
            * (1 - maintainMargin / self.position)
        return liquidationPrice

    def unrealisedPNL(self, price):
        uPNL = (price - self.positionPrice) * self.position
        uPNL /= self.positionPrice
        return uPNL

    def calculateFunding(self, FR):
        self.revenueFunding = self.position * FR / -100
        self.revenuePrice = 0
        self.revenueFee = 0
        self.revenueThisTime = self.revenueFunding
        self.capital += self.revenueThisTime
        self.revenueTotal += self.revenueThisTime
        self.revenueTotal_Funding += self.revenueFunding
        if self.print_Funding:
            print(f"{self.timestamp}: Funding executed"
                  f", Funding rate: {round(FR, 3)}"
                  f", Capital: {round(self.capital, 2)}"
                  f"({round(self.revenueFunding, 3)})"
                  f", Postion: {round(self.position,2)}"
                  f"@{round(self.positionPrice,2)}")

    def checkLiquidation(self):
        if self.position == 0:
            return False
        liquidationPrice = self.getLiquidationPrice()
        if self.position > 0 and self.low <= liquidationPrice:
            return True
        elif self.position < 0 and self.high >= liquidationPrice:
            return True
        else:
            return False

    def printStatus(self):
        print(f'Capital: {self.capital}')
        print(f'Total revenue: {self.revenueTotal}')
        print(f'Total revenue(Price): {self.revenueTotal_Price}')
        print(f'Total revenue(Funding): {self.revenueTotal_Funding}')
        print(f'Total revenue(Fee): {self.revenueTotal_Fee}')
        print(f'Unrealised PNL: {self.unrealisedPNL(self.vwap)}')
        print(f'TurnOver: {self.turnOver}')
        print(f'Last trade time: {self.lastTradeTime}')
        print(f'Max loss: {self.maxLoss}')
        print(f'Position: {self.position}')
        print(f'Position Price: {self.positionPrice}')
        print(f'Liquidation price: {self.getLiquidationPrice()}')


if __name__ == "__main__":
    Test = status()
    Test.capital = 1000
    Test.position = 10000
    Test.positionPrice = 10000
    print(Test.getLiquidationPrice())
    print(Test.unrealisedPNL(10500))
