import asyncio
import requests
import twstock
import pandas as pd
from bs4 import BeautifulSoup

async def fetch_data(stock):
    url = f"https://tw.stock.yahoo.com/quote/{stock}/broker-trading"
    print(url)
    response = await loop.run_in_executor(None, requests.get, url)
    soup = BeautifulSoup(response.content, "html.parser")
    span_tags = soup.find("div", {"class": "D(f) Fld(c)--mobile"})
    if span_tags is None:
        return
    span_tags = [span for span in span_tags]
    buy_tags = span_tags[0].find_all("span")
    sell_tags = span_tags[1].find_all("span")
    parse_data(buy_tags, ["買超券商", "買進", "賣出", "買超張數"])
    parse_data(sell_tags, ["賣超券商", "買進", "賣出", "賣超張數"])

def parse_data(tags, column_names):
    data = []
    tmp = []
    for tag in tags:
        if (
            tag.get_text() in column_names
        ):
            continue
        if tag.get_text().strip() != "":
            tmp.append(tag.get_text().strip())
        if len(tmp) == len(column_names):
            data.append(tmp)
            tmp = []
    df = pd.DataFrame(data, columns=column_names)
    if not df.empty:
        print(df.to_markdown())

if __name__ == "__main__":
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
