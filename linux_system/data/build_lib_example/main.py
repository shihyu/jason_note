from strategy.SimpleMovingAverageStrategy import SimpleMovingAverageStrategy
from strategy.SimpleMACDStrategy import SimpleMACDStrategy
from exchange.BinanceExchange import BinanceExchange

if __name__ == "__main__":
    exchange_client = BinanceExchange(exchange_name="Binance")
    strategy_ma = SimpleMovingAverageStrategy(client=exchange_client)
    strategy_ma.execute_strategy()

    strategy_macd = SimpleMACDStrategy(client=exchange_client)
    strategy_macd.execute_strategy()
