from .BaseExchange import BaseExchange
import ccxt


class BinanceExchange(BaseExchange):
    def __init__(self, exchange_name, public_key=None, secret_key=None):
        super().__init__(exchange_name, public_key, secret_key)

    def init(self, public_key, secret_key):
        self._client = ccxt.binance()
        # Additional setup specific to Binance

    def get_ohlc_data(self, symbol, timeframe):
        return self._client.fetch_ohlcv(symbol, timeframe)
