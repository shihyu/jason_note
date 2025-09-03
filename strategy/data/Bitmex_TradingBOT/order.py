from record import historyRecord


class order(historyRecord):
    '''
        orderBook = {
            'price': amount:
        }
    '''
    marketFee = 0.00075
    limitFee = -0.00025
    orderBook = dict()
    print_Order = True

    def removeOrder(self, price):
        self.orderBook.pop(price, None)

    def cancelAllOrders(self):
        self.orderBook = dict()

    def putMarketOrder(self, amount, price=0):
        if price == 0:
            price = self.vwap
        self.calculteExecution(price, amount, 'Market')
        if self.print_Order:
            print(f"{self.timestamp}:"
                  f" Market executed @{round(price, 2)}"
                  f" for ${round(amount, 2)}"
                  f", Capital: {round(self.capital, 2)}"
                  f"({round(self.revenueThisTime, 2)})"
                  f", Postion: {round(self.position,2)}"
                  f"@{round(self.positionPrice,2)}")

    def putLimitOrder(self, price, amount):
        self.orderBook[price] = amount

    def executeLimitOrder(self):
        # o > c
        # o -> h -> l -> c
        if self.open > self.close:
            self.executeRangeLimit(self.open, self.high)
            self.executeRangeLimit(self.high, self.low)
            self.executeRangeLimit(self.low, self.close)
        # o < c
        # o -> l -> h -> c
        else:
            self.executeRangeLimit(self.open, self.low)
            self.executeRangeLimit(self.low, self.high)
            self.executeRangeLimit(self.high, self.close)

    def executeRangeLimit(self, fromPrice, toPrice):
        orderPrices = self.orderBook.keys()
        orders_to_remove = []
        for orderPrice in orderPrices:
            if fromPrice < orderPrice < toPrice:
                executeAmount = self.orderBook[orderPrice]
                self.calculteExecution(orderPrice, executeAmount, 'Limit')
                if self.print_Order:
                    print(f"{self.timestamp}:"
                          f" Limit executed @{round(orderPrice, 2)}"
                          f" for ${round(executeAmount, 2)}"
                          f", Capital: {round(self.capital, 2)}"
                          f"({round(self.revenueThisTime, 2)})"
                          f", Postion: {round(self.position,2)}"
                          f"@{round(self.positionPrice,2)}")
                orders_to_remove.append(orderPrice)
        for order in orders_to_remove:
            self.removeOrder(order)

    def calculteExecution(self, price, amount, orderType):
        if orderType == 'Market':
            self.revenueFee = -1 * abs(amount) * self.marketFee
            self.revenueTotal_Fee += self.revenueFee
        elif orderType == 'Limit':
            self.revenueFee = -1 * abs(amount) * self.limitFee
            self.revenueTotal_Fee += self.revenueFee

        if amount == 0:
            self.revenuePrice = 0
        # 第一次開倉
        elif self.position == 0:
            self.position = amount
            self.positionPrice = price
            self.revenuePrice = 0
        # 加倉
        elif amount * self.position > 0:
            self.revenuePrice = 0
            self.positionPrice = \
                (price * amount + self.positionPrice * self.position) \
                / (amount + self.position)
            self.position += amount
        elif amount * self.position < 0:
            # 反倉
            if abs(amount) > abs(self.position):
                self.revenuePrice = \
                    self.position * (price - self.positionPrice) \
                    / self.positionPrice
                self.positionPrice = price
            # 減倉
            else:
                self.revenuePrice = \
                    amount * (self.positionPrice - price) / self.positionPrice
            self.position += amount

        self.revenueFunding = 0
        self.revenueThisTime = self.revenuePrice + self.revenueFee
        self.revenueTotal_Price += self.revenuePrice
        self.revenueTotal += self.revenueThisTime
        self.capital += self.revenueThisTime
        self.amount = amount
        self.price = price
        self.orderType = orderType
        self.turnOver += abs(amount)
        self.lastTradeTime = self.timestamp

    def getOrders(self):
        return self.orderBook
