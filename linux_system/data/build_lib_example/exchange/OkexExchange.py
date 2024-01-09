from .BaseExchange import BaseExchange
import ccxt


class OkexExchange(BaseExchange):
    def __init__(self, exchange_name, public_key=None, secret_key=None):
        super().__init__(exchange_name, public_key, secret_key)

    def init(self, public_key, secret_key):
        self._client = ccxt.okx()
        # Additional setup specific to Okex

    def get_ohlc_data(self, symbol, timeframe, stm, limit, params):
        return self._client.fetch_ohlcv(symbol, timeframe)
