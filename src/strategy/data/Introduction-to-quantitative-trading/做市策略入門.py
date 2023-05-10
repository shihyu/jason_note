#!/usr/bin/env python
# coding: utf-8

# # 做市策略
# ### 1、對敲做量
# ### 2、盤口高頻吃利潤
# ### 3、緩步先買後賣抬高品種價格
# ### 4、緩步先賣後買拉低品種價格

# In[2]:


class mid_class():
    def __init__(self, this_exchange):
        '''
        初始化數據填充交易所的信息，首次獲取價格，首次獲取account信息
        設定好密鑰……
        
        Args:
            this_exchange: FMZ的交易所結構
        
        '''
        self.init_timestamp = time.time()
        self.exchange = this_exchange
        self.name = self.exchange.GetName()
        self.jyd = self.exchange.GetCurrency()        
    
    def get_account(self):
        '''
        獲取賬戶信息
        
        Returns:
            獲取信息成功返回True，獲取信息失敗返回False
        '''
        self.Balance = '---'
        self.Amount = '---'
        self.FrozenBalance = '---'
        self.FrozenStocks = '---'
        
        try:
            self.account = self.exchange.GetAccount()

            self.Balance =  self.account['Balance']
            self.Amount = self.account['Stocks']
            self.FrozenBalance =  self.account['FrozenBalance']
            self.FrozenStocks = self.account['FrozenStocks']
            return True
        except:
            return False
    
    def get_ticker(self):
        '''
        獲取市價信息
        
        Returns:
            獲取信息成功返回True，獲取信息失敗返回False
        '''
        self.high = '---'
        self.low = '---'
        self.Sell =  '---'
        self.Buy =  '---'
        self.last =  '---'
        self.Volume = '---'
        
        try:
            self.ticker = self.exchange.GetTicker()
        
            self.high = self.ticker['High']
            self.low = self.ticker['Low']
            self.Sell =  self.ticker['Sell']
            self.Buy =  self.ticker['Buy']
            self.last =  self.ticker['Last']
            self.Volume = self.ticker['Volume']
            return True
        except:
            return False
        
        
    def get_depth(self):
        '''
        獲取深度信息
        
        Returns:
            獲取信息成功返回True，獲取信息失敗返回False
        '''
        self.Ask = '---'
        self.Bids = '---'
        
        try:
            self.Depth = self.exchange.GetDepth()
            self.Ask = self.Depth['Asks']
            self.Bids = self.Depth ['Bids']
            return True
        except:
            return False
        
        
    
    def get_ohlc_data(self, period = PERIOD_M5):
        '''
        獲取K線信息
        
        Args:
            period: K線週期，PERIOD_M1 指1分鐘, PERIOD_M5 指5分鐘, PERIOD_M15 指15分鐘,
            PERIOD_M30 指30分鐘, PERIOD_H1 指1小時, PERIOD_D1 指一天。
        '''
        self.ohlc_data = exchange.GetRecords(period)
        
        
    
    def create_order(self, order_type, price, amount):
        '''
        post一個掛單信息
        
        Args:
            order_type：掛單類型，'buy'指掛買單，'sell'指掛賣單
            price：掛單價格
            amount:掛單數量
            
        Returns:
            掛單Id號，可用以取消掛單
        '''
        if order_type == 'buy':
            try:
                order_id = self.exchange.Buy( price, amount)
            except:
                return False
            
        elif order_type == 'sell':
            try:
                order_id = self.exchange.Sell( price, amount)
            except:
                return False
        
        return order_id
    
    def get_orders(self):
        self.undo_ordes = self.exchange.GetOrders()
        return self.undo_ordes
    
    def cancel_order(self, order_id):
        '''
        取消一個掛單信息
        
        Args:
            order_id：希望取消的掛單ID號
            
        Returns:
            取消掛單成功返回True，取消掛單失敗返回False
        '''
        return self.exchange.CancelOrder(order_id)
        
    def refreash_data(self):
        '''
        刷新信息
        
        Returns:
            刷新信息成功返回 'refreash_data_finish!' 否則返回相應刷新失敗的信息提示
        '''

        if not self.get_account():
            return 'false_get_account'
        
        if not self.get_ticker():
            return 'false_get_ticker'
        if not self.get_depth():
            return 'false_get_depth'
        try:
            self.get_ohlc_data()
        except:
            return 'false_get_K_line_info'
        
        return 'refreash_data_finish!'


# In[5]:


class zuoshi():
    def __init__(self, mid_class, amount_N, price_N):
        self.jys = mid_class
        self.done_amount = 0
        self.init_time = time.time()
        self.last_time = time.time()
        self.amount_N = amount_N
        self.price_N = price_N
        
    def trade_duiqiao(self, trade_dict):
        
        self.jys.create_order( 'buy', trade_dict['price'] , trade_dict['amount'] ) 
        self.jys.create_order( 'sell',trade_dict['price'] , trade_dict['amount'] ) 
        self.done_amount += trade_dict['amount']
        self.last_time = time.time()
        
    def make_duiqiao_trade_dict(self, set_amount, every_time_amount):
        self.jys.refreash_data()
        
        trade_price = ( self.jys.Sell + self.jys.Buy )/2
        trade_price = round(trade_price, self.price_N)
        if trade_price > self.jys.Buy and trade_price< self.jys.Sell:            
            self.B = self.jys.Amount
            self.money = self.jys.Balance
            self.can_buy_B = self.money/ trade_price
            do_trade = self.B > every_time_amount
            do_trade = do_trade and self.can_buy_B > every_time_amount
            trade_dict = {'do_trade':do_trade,
                          'price': trade_price,
                          'amount':every_time_amount }
            return trade_dict
        
    def deal_with_frozen(self):
        undo_orders = self.jys.get_orders()
        if len( undo_orders) > 0:
            for i in undo_orders:
                self.jys.cancel_order(i['Id'])


# In[ ]:


def main():
    Set_amount_N = 4
    Set_price_N = 4
    set_amount = 10
    every_time_amount = 0.1
    
    test_mid = mid_class(exchange)
    Log(test_mid.refreash_data())
    test_duiqiao = zuoshi(test_mid, Set_amount_N, Set_price_N)
    
    while(test_duiqiao.done_amount < set_amount):
        test_duiqiao.deal_with_frozen()
        Sleep(1000)
        trade_dict = test_duiqiao.make_duiqiao_trade_dict(set_amount, every_time_amount)
        if trade_dict['do_trade']:
            test_duiqiao.trade_duiqiao( trade_dict )
            
    Log(test_duiqiao.done_amount)
    Log(test_duiqiao.B)

