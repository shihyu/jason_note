import asyncio
import requests
import twstock
import pandas as pd
import redis
import pickle

from bs4 import BeautifulSoup


async def fetch_data(stock):
    redis_host = "localhost"
    redis_port = 6379
    redis_db = 0
    redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
    url = f"https://tw.stock.yahoo.com/quote/{stock}/broker-trading"
    print(url)
    response = await loop.run_in_executor(None, requests.get, url)
    soup = BeautifulSoup(response.content, "html.parser")
    time_tag = soup.find("time")
    if time_tag is None:
        return
    # 從<time>標籤中取得日期字串，日期字串在第二個<span>元素內
    date_string = time_tag.find_all("span")[2].text.strip()
    # print(date_string)
    span_tags = soup.find("div", {"class": "D(f) Fld(c)--mobile"})
    if span_tags is None:
        return
    span_tags = [span for span in span_tags]
    buy_tags = span_tags[0].find_all("span")
    sell_tags = span_tags[1].find_all("span")
    parse_data(buy_tags, ["買超券商", "買進", "賣出", "買超張數"], stock, date_string, redis_client)
    parse_data(
        sell_tags, ["賣超券商", "買進", "賣出", "賣超張數"], stock, date_string, redis_client
    )


def parse_data(tags, column_names, stock, date_string, redis_client):
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
        redis_client.set(f"{stock}:{date_string}", pickle.dumps(df))


def test():
    redis_host = "localhost"
    redis_port = 6379
    redis_db = 0
    redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
    data = redis_client.get("2330:2023/07/27")
    if data is not None:
        df = pickle.loads(data)
        print(df.to_markdown())


if __name__ == "__main__":
    test()
    tse_stock_list = []
    otc_stock_list = []

    for stock in twstock.twse:
        if len(stock) == 4:
            tse_stock_list.append(stock)

    for stock in twstock.tpex:
        if len(stock) == 4:
            otc_stock_list.append(stock)

    stock_list = tse_stock_list + otc_stock_list

    loop = asyncio.get_event_loop()
    tasks = [fetch_data(stock) for stock in stock_list]
    loop.run_until_complete(asyncio.gather(*tasks))
