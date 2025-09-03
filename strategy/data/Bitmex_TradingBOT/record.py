from status import status
# import matplotlib.pyplot as plt


class record(status):
    coin = 'BTC'
    amount = 0
    price = 0
    orderType = 'Market'  # Market or Limit
    time = 0
    revenueThisTime = 0
    revenueFee = 0
    revenueFunding = 0
    revenuePrice = 0


class historyRecord(record):
    tradeHistory = []

    def addRecord(self):
        pass

    def writeToCSV(self):
        pass

    def plotHistory(self):
        # print("RevenuePrice:",self.revenuePrice,"RevenueFee:",self.revenueFee,"RevenueFee:",self.revenueFunding,"TurnOver:",self.turnOver)
        # plt.plot(self.revenueHistory)
        # plt.axis([0,15000000,0,6000])
        # plt.show()
        pass
