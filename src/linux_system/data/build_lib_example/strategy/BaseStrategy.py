from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    def __init__(self, client):
        self.client = client

    @abstractmethod
    def execute_strategy(self):
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def enter_trade_signal(self):
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def exit_trade_signal(self):
        raise NotImplementedError("Subclasses must implement this method")
