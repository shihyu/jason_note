import asyncio
import requests
import twstock
import pandas as pd
import redis
import pickle
import schedule
import time
from bs4 import BeautifulSoup
from line_notify import LineNotify


class StockDataParser:
    def __init__(self):
        self.redis_host = "localhost"
        self.redis_port = 6379
        self.redis_db = 0
        self.redis_client = redis.StrictRedis(
            host=self.redis_host, port=self.redis_port, db=self.redis_db
        )

    async def fetch_data(self, stock):
        url = f"https://tw.stock.yahoo.com/quote/{stock}/broker-trading"
        print(url)
        response = await loop.run_in_executor(None, requests.get, url)
        soup = BeautifulSoup(response.content, "html.parser")
        time_tag = soup.find("time")
        if time_tag is None:
            return
        date_string = time_tag.find_all("span")[2].text.strip()
        span_tags = soup.find("div", {"class": "D(f) Fld(c)--mobile"})
        if span_tags is None:
            return
        span_tags = [span for span in span_tags]
        buy_tags = span_tags[0].find_all("span")
        sell_tags = span_tags[1].find_all("span")
        self.parse_data(buy_tags, ["買超券商", "買進", "賣出", "買超張數"], stock, date_string)
        self.parse_data(sell_tags, ["賣超券商", "買進", "賣出", "賣超張數"], stock, date_string)

    def parse_data(self, tags, column_names, stock, date_string):
        data = []
        tmp = []
        for tag in tags:
            if tag.get_text() in column_names:
                continue
            if tag.get_text().strip() != "":
                tmp.append(tag.get_text().strip())
            if len(tmp) == len(column_names):
                data.append(tmp)
                tmp = []
        df = pd.DataFrame(data, columns=column_names)
        if not df.empty:
            df["股票代號"] = stock
            df["日期"] = date_string
            print(df.to_markdown())
            self.redis_client.set(f"{stock}:{date_string}", pickle.dumps(df))

    def get_stock_data(self, stock, date_string):
        data = self.redis_client.get(f"{stock}:{date_string}")
        if data is not None:
            return pickle.loads(data)
        return None


def run_script():
    loop = asyncio.get_event_loop()
    stock_data_parser = StockDataParser()

    tse_stock_list = [stock for stock in twstock.twse if len(stock) == 4]
    otc_stock_list = [stock for stock in twstock.tpex if len(stock) == 4]

    stock_list = tse_stock_list + otc_stock_list

    tasks = [stock_data_parser.fetch_data(stock) for stock in stock_list]
    loop.run_until_complete(asyncio.gather(*tasks))

    # Test retrieving data
    df = stock_data_parser.get_stock_data("2330", "2023/07/27")
    if df is not None:
        print(df.to_markdown())


def run_job():
    print("Running the stock data fetching job...")
    LineNotify("KXwzqEGtIp1JEkS5GjqXqRAT0D4BdQQvCNcqOa7ySfz").send(
        "Running the stock data fetching job..."
    )
    run_script()


if __name__ == "__main__":
    # Schedule the job to run at the specified times
    schedule.every().day.at("05:00").do(run_job)
    schedule.every().day.at("18:00").do(run_job)
    schedule.every().day.at("22:00").do(run_job)

    while True:
        schedule.run_pending()
        time.sleep(1)
