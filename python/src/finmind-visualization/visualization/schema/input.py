from enum import Enum


class DataSetInput(str, Enum):
    TaiwanStockDayTrading = "TaiwanStockDayTrading"
    TaiwanStockHoldingSharesPer = "TaiwanStockHoldingSharesPer"
    TaiwanStockInfo = "TaiwanStockInfo"
    TaiwanStockInstitutionalInvestorsBuySell = (
        "TaiwanStockInstitutionalInvestorsBuySell"
    )
    TaiwanStockMarginPurchaseShortSale = "TaiwanStockMarginPurchaseShortSale"
    TaiwanStockPrice = "TaiwanStockPrice"
    TaiwanStockShareholding = "TaiwanStockShareholding"
    TaiwanStockNews = "TaiwanStockNews"
    # TaiwanStockTradingDailyReport = "TaiwanStockTradingDailyReport"
