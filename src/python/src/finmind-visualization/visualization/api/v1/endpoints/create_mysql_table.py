from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import UJSONResponse

from visualization.backend import db
from loguru import logger


router = APIRouter()


def create_taiwan_stock_day_trading_table():
    sql = """
        CREATE TABLE `TaiwanStockDayTrading` (
            `date` date NOT NULL,
            `stock_id` varchar(10) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
            `BuyAfterSale` varchar(2) COLLATE utf8_unicode_ci DEFAULT NULL,
            `Volume` bigint DEFAULT NULL,
            `BuyAmount` bigint DEFAULT NULL,
            `SellAmount` bigint DEFAULT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8_unicode_ci
        PARTITION BY KEY (stock_id)
        PARTITIONS 10;
    """
    db.commit(sql)
    sql = """
        ALTER TABLE `TaiwanStockDayTrading`
        ADD PRIMARY KEY (`stock_id`,`date`);
    """
    db.commit(sql)
    logger.info("create TaiwanStockDayTrading table")


def create_taiwan_stock_holding_shares_per_table():
    sql = """
        CREATE TABLE `TaiwanStockHoldingSharesPer` (
            `HoldingSharesLevel` varchar(50) NOT NULL,
            `people` int DEFAULT NULL,
            `unit` bigint DEFAULT NULL,
            `percent` float DEFAULT NULL,
            `stock_id` varchar(10) NOT NULL,
            `date` date NOT NULL,
            `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
        PARTITION BY KEY (stock_id)
        PARTITIONS 10;
    """
    db.commit(sql)
    sql = """
        ALTER TABLE `TaiwanStockHoldingSharesPer`
        ADD PRIMARY KEY (`stock_id`,`date`,`HoldingSharesLevel`);
    """
    db.commit(sql)
    logger.info("create TaiwanStockHoldingSharesPer table")


def create_taiwan_stock_info_table():
    sql = """
        CREATE TABLE `TaiwanStockInfo` (
            `industry_category` varchar(30) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
            `stock_id` varchar(50) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
            `stock_name` varchar(30) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
            `type` varchar(10) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT '上市twse/上櫃tpex',
            `date` date DEFAULT NULL,
            `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8_unicode_ci;
    """
    db.commit(sql)
    sql = """
        ALTER TABLE `TaiwanStockInfo`
        ADD PRIMARY KEY (`stock_id`,`industry_category`);
    """
    db.commit(sql)
    logger.info("create TaiwanStockInfo table")


def create_taiwan_stock_institutional_investors_buy_sell_table():
    sql = """
        CREATE TABLE `TaiwanStockInstitutionalInvestorsBuySell` (
            `name` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
            `buy` bigint DEFAULT NULL,
            `sell` bigint DEFAULT NULL,
            `stock_id` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
            `date` date NOT NULL,
            `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8_unicode_ci
        PARTITION BY KEY (stock_id)
        PARTITIONS 10;
    """
    db.commit(sql)
    sql = """
        ALTER TABLE `TaiwanStockInstitutionalInvestorsBuySell`
        ADD PRIMARY KEY (`stock_id`,`date`,`name`);
    """
    db.commit(sql)
    logger.info("create TaiwanStockInstitutionalInvestorsBuySell table")


def create_taiwan_stock_margin_purchaseShortSale_table():
    sql = """
        CREATE TABLE `TaiwanStockMarginPurchaseShortSale` (
            `stock_id` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
            `MarginPurchaseBuy` bigint DEFAULT NULL,
            `MarginPurchaseSell` bigint DEFAULT NULL,
            `MarginPurchaseCashRepayment` bigint DEFAULT NULL,
            `MarginPurchaseYesterdayBalance` bigint DEFAULT NULL,
            `MarginPurchaseTodayBalance` bigint DEFAULT NULL,
            `MarginPurchaseLimit` bigint DEFAULT NULL,
            `ShortSaleBuy` bigint DEFAULT NULL,
            `ShortSaleSell` bigint DEFAULT NULL,
            `ShortSaleCashRepayment` bigint DEFAULT NULL,
            `ShortSaleYesterdayBalance` bigint DEFAULT NULL,
            `ShortSaleTodayBalance` bigint DEFAULT NULL,
            `ShortSaleLimit` bigint DEFAULT NULL,
            `OffsetLoanAndShort` bigint DEFAULT NULL,
            `Note` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
            `date` date NOT NULL,
            `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8_unicode_ci
        PARTITION BY KEY (stock_id)
        PARTITIONS 10;
    """
    db.commit(sql)
    sql = """
        ALTER TABLE `TaiwanStockMarginPurchaseShortSale`
        ADD PRIMARY KEY (`stock_id`,`date`);
    """
    db.commit(sql)
    logger.info("create TaiwanStockMarginPurchaseShortSale table")


def create_taiwan_stock_news_table():
    sql = """
        CREATE TABLE `TaiwanStockNews` (
            `stock_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
            `date` datetime NOT NULL,
            `title` varchar(200) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
            `source` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
            `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8_unicode_ci
        PARTITION BY KEY (stock_id)
        PARTITIONS 50;
    """
    db.commit(sql)
    sql = """
        ALTER TABLE `TaiwanStockNews`
        ADD PRIMARY KEY (`stock_id`,`title`,`date`);
    """
    db.commit(sql)
    logger.info("create TaiwanStockNews table")


def create_taiwan_stock_price_table():
    sql = """
        CREATE TABLE `TaiwanStockPrice` (
            `date` date NOT NULL,
            `Trading_Volume` bigint DEFAULT NULL,
            `Trading_money` bigint DEFAULT NULL,
            `open` float DEFAULT NULL,
            `max` float DEFAULT NULL,
            `min` float DEFAULT NULL,
            `close` float DEFAULT NULL,
            `spread` float DEFAULT NULL,
            `Trading_turnover` bigint DEFAULT NULL,
            `stock_id` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8_unicode_ci
        PARTITION BY KEY (stock_id)
        PARTITIONS 10;
    """
    db.commit(sql)
    sql = """
        ALTER TABLE `TaiwanStockPrice`
        ADD PRIMARY KEY (`stock_id`,`date`);
    """
    db.commit(sql)
    logger.info("create TaiwanStockPrice table")


def create_taiwan_stock_shareholding_table():
    sql = """
        CREATE TABLE `TaiwanStockShareholding` (
            `stock_id` varchar(10) NOT NULL,
            `stock_name` varchar(10) NOT NULL,
            `InternationalCode` varchar(100) DEFAULT NULL,
            `NumberOfSharesIssued` float DEFAULT NULL,
            `ForeignInvestmentRemainingShares` float DEFAULT NULL,
            `ForeignInvestmentShares` float DEFAULT NULL,
            `ForeignInvestmentRemainRatio` float DEFAULT NULL,
            `ForeignInvestmentSharesRatio` float DEFAULT NULL,
            `ForeignInvestmentUpperLimitRatio` float DEFAULT NULL,
            `ChineseInvestmentUpperLimitRatio` float DEFAULT NULL,
            `RecentlyDeclareDate` varchar(10) DEFAULT NULL,
            `date` date NOT NULL,
            `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
        PARTITION BY KEY (stock_id)
        PARTITIONS 10;
    """
    db.commit(sql)
    sql = """
        ALTER TABLE `TaiwanStockShareholding`
        ADD PRIMARY KEY (`stock_id`,`stock_name`,`date`);
    """
    db.commit(sql)
    logger.info("create TaiwanStockShareholding table")


def create_scheduler_table():
    sql = """
        CREATE TABLE `scheduler` (
            `dataset` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
            `update_with_data_id` tinyint(1) NOT NULL,
            `start_date` date DEFAULT NULL,
            `is_scheduler` tinyint(1) NOT NULL COMMENT '1=要定時更新\r\n0=不要定時更新',
            `crontab_hour` varchar(10) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    """
    db.commit(sql)
    sql = """
        ALTER TABLE `scheduler`
        ADD PRIMARY KEY (`dataset`);
    """
    db.commit(sql)
    sql = """
        INSERT INTO `scheduler` (`dataset`, `update_with_data_id`, `start_date`, `is_scheduler`, `crontab_hour`) VALUES
        ('TaiwanStockInfo', 0, NULL, 0, '15-22'),
        ('TaiwanStockDayTrading', 0, '2014-01-06', 0, '15-22'),
        ('TaiwanStockHoldingSharesPer', 0, '2017-10-06', 0, '15-22'),
        ('TaiwanStockInstitutionalInvestorsBuySell', 0, '2012-05-02', 0, '15-22'),
        ('TaiwanStockMarginPurchaseShortSale', 0, '2001-01-05', 0, '15-22'),
        ('TaiwanStockNews', 0, '2020-07-28', 0, '15-22'),
        ('TaiwanStockPrice', 0, '1994-09-13', 0, '15-22'),
        ('TaiwanStockShareholding', 0, '2004-02-12', 0, '15-22');
    """
    db.commit(sql)
    logger.info("create scheduler table")


@router.post("/create_mysql_table")
async def create_mysql_table(request: Request,):
    create_taiwan_stock_day_trading_table()
    create_taiwan_stock_holding_shares_per_table()
    create_taiwan_stock_info_table()
    create_taiwan_stock_institutional_investors_buy_sell_table()
    create_taiwan_stock_margin_purchaseShortSale_table()
    create_taiwan_stock_news_table()
    create_taiwan_stock_price_table()
    create_taiwan_stock_shareholding_table()
    create_scheduler_table()
    return UJSONResponse(
        {"msg": "", "status": 200}, headers={"Access-Control-Allow-Origin": "*"},
    )
