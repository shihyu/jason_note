from abc import ABC, abstractmethod


class BaseExchange(ABC):
    def __init__(self, exchange_name, public_key, secret_key):
        self.exchange_name = exchange_name
        self.init(public_key, secret_key)

    @abstractmethod
    def init(self, public_key, secret_key):
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def get_ohlc_data(self, timeframe, stm, limit, params):
        raise NotImplementedError("Subclasses must implement this method")

    # @abstractmethod
    # def get_position_data(self):
    #    raise NotImplementedError("Subclasses must implement this method")

    # def get_balance_data(self):
    #    raise NotImplementedError("Subclasses must implement this method")

    # def get_ticker_data(self):
    #    raise NotImplementedError("Subclasses must implement this method")

    # def get_orders_data(self):
    #    raise NotImplementedError("Subclasses must implement this method")

    # def create_limit_order(self, hand_type, amount, price):
    #    raise NotImplementedError("Subclasses must implement this method")

    # def create_market_order(self, hand_type, amount):
    #    raise NotImplementedError("Subclasses must implement this method")

    # def cancel_order(self, order_id):
    #    raise NotImplementedError("Subclasses must implement this method")

    # def close_position(self, symbol, price=None):
    #    raise NotImplementedError("Subclasses must implement this method")

    # def get_wallet_history_data(self):
    #    raise NotImplementedError("Subclasses must implement this method")

    # def refresh_data(self):
    #    raise NotImplementedError("Subclasses must implement this method")

    # def post_order(self, side, order_type, price, check_price, amount):
    #    raise NotImplementedError("Subclasses must implement this method")

    # def get_min_order_size(self):
    #    raise NotImplementedError("Subclasses must implement this method")
