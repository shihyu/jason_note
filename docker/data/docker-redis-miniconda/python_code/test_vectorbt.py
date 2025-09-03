import vectorbt as vbt

price = vbt.YFData.download('BTC-USD').get('Close')

pf = vbt.Portfolio.from_holding(price, init_cash=100)
print(pf.total_profit())
