import csv
import datetime
import os
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

# import talib
# NOTICE: Check newest FR
# TODO: Error in newest FR
# TODO: Chrome Driver
# NOTICE: bin->1h, fixed or dynamic?


class histData():
    dayOfMonthNotYear = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    dayOfMonthYear = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    fundingRateHistory = {}
    bin1mHistory = []
    recorded = []
    url = "https://www.bitmex.com/api/v1/trade/bucketed?" \
        "binSize=1m&partial=false&symbol={0}USD" \
        "&count=720&reverse=false&startTime={1}"

    def requestJSON(self, url):
        return requests.get(url).json()

    def getFundingRate(self, timestamp):
        timestamp_datetime = datetime.datetime.strptime(
            timestamp, '%Y-%m-%dT%H:%M:00.000Z')
        hour = timestamp_datetime.hour
        minute = timestamp_datetime.minute
        seconds = timestamp_datetime.second
        microsecond = timestamp_datetime.microsecond

        secondsOfDay = hour * 3600 + minute * 60 + seconds
        secondsOfDay = (secondsOfDay + microsecond) / 1000000
        # Get Funding Rate
        if secondsOfDay <= 43200 and secondsOfDay > 14400:
            tmpStr = 'T12:00:00.000Z'
        # p.m.12:00 to p.m. 20:00
        elif secondsOfDay <= 72000 and secondsOfDay > 43200:
            tmpStr = 'T20:00:00.000Z'
        # a.m.00:00 to a.m. 04:00
        elif secondsOfDay <= 14400:
            tmpStr = 'T04:00:00.000Z'
        # p.m.20:00 to a.m. 00:00
        elif secondsOfDay > 72000:
            tmpStr = 'T04:00:00.000Z'
            timestamp = datetime.datetime.strptime(
                str(timestamp)[:10], '%Y-%m-%d') + datetime.timedelta(days=1)
        else:
            print("Get funding rate error!")

        timeFR = str(timestamp)[:10] + tmpStr
        if timeFR in histData.fundingRateHistory.keys():
            return histData.fundingRateHistory[timeFR]
        else:
            return 0

    def writeFile(self, filename):
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            length = len(histData.bin1mHistory)
            for i in range(0, length):
                writer.writerow(histData.bin1mHistory[i])

    def isYear(self, year):
        if year % 4 == 0 & year % 100 != 0:
            return True
        elif year % 400 == 0:
            return True
        else:
            return False

    def crawlFR(self):
        # Earlist:2016-05-14T12:00:00.000Z
        print("Start to crawl funding rate history....")
        i = 0
        go = True
        while (go):
            print("Crawling funding rate(" + str(i + 1) + ")...")
            url = "https://www.bitmex.com/api/v1/funding?count=500&start="
            if self.coin == "BTC":
                url += str(
                    500 * i
                ) + "&reverse=true&filter=%7B%22symbol%22%3A%22XBTUSD%22%7D"
            elif self.coin == "ETH":
                url += str(
                    500 * i
                ) + "&reverse=true&filter=%7B%22symbol%22%3A%22ETHUSD%22%7D"

            fundingRate = self.requestJSON(url)
            for index in range(0, len(fundingRate)):
                histData.fundingRateHistory[
                    fundingRate[index]
                    ['timestamp']] = fundingRate[index]['fundingRate'] * 100
                if (fundingRate[index]['timestamp'] ==
                        '2016-05-14T12:00:00.000Z' and self.coin == "BTC"):
                    go = False
                    break
                if (fundingRate[index]['timestamp'] ==
                        '2018-08-02T12:00:00.000Z' and self.coin == "ETH"):
                    go = False
                    break
            i += 1

    def crawlAll(self,
                 Coin="BTC",
                 filename="BTC.csv",
                 sleep=0.5,
                 fromYear=2017,
                 fromMonth=1,
                 fromDay=1):
        self.coin = Coin
        if Coin == "ETH":
            fromYear = 2018
            fromMonth = 8
            fromDay = 3
        self.crawlFR()
        print("Median of FR:",
              np.median(list(self.fundingRateHistory.values())))
        histData.bin1mHistory = []
        histData.recorded = []
        if os.path.exists(filename):
            os.remove(filename)
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'timestamp', 'symbol', 'open', 'high', 'low', 'close',
                'trades', 'volume', 'vwap', 'lastSize', 'turnover',
                'homeNotional', 'foreignNotional', 'fundingRate'
            ])
        for year in range(fromYear, 2020):
            startMonth = fromMonth if year == fromYear else 1
            dayOfMonth = histData.dayOfMonthYear if self.isYear(
                year) else histData.dayOfMonthNotYear
            for month in range(startMonth, 13):
                startDay = fromDay if (year == fromYear
                                       and month == fromMonth) else 1
                for day in range(startDay, dayOfMonth[month - 1] + 1):
                    for hour in range(0, 2):
                        hour = str(hour * 12).zfill(2)
                        month = str(month).zfill(2)
                        timestamp = "%d-%s-%dT%s:00:00.000Z" % (year, month,
                                                                day, hour)
                        timestamp = datetime.datetime.strptime(
                            timestamp, '%Y-%m-%dT%H:%M:00.000Z')
                        if (datetime.datetime.utcnow() -
                                timestamp).total_seconds() < 60:
                            break
                        else:
                            if self.coin == "BTC":
                                coin = "XBT"
                                crawl_url = histData.url.format(
                                    coin, str(timestamp))
                            elif self.coin == "ETH":
                                coin = "ETH"
                                crawl_url = histData.url.format(
                                    coin, str(timestamp))
                            while True:
                                time.sleep(sleep)
                                result = self.requestJSON(crawl_url)
                                if len(result
                                       ) > 0 and result[0]['timestamp'] != '':
                                    for i in range(0, len(result)):
                                        if (result[i]['timestamp'] not in
                                                histData.recorded[-720:]):
                                            fundingRate = self.getFundingRate(
                                                result[i]['timestamp'])
                                            histData.bin1mHistory.append(
                                                list(result[i].values()) +
                                                [float(fundingRate)])
                                            histData.recorded.append(
                                                result[i]['timestamp'])
                                    print(
                                        datetime.datetime.now(), "Crawling " +
                                        str(timestamp) + ".... Total: " +
                                        str(len(result)) + " data")
                                    break
                                else:
                                    print("Request ", str(timestamp),
                                          " Error! .... Total: ",
                                          str(len(result)), " data")
        self.writeFile(filename)

    def complement(self, Coin="BTC", filename="BTC.csv", sleep=0.5):
        self.coin = Coin
        df = pd.read_csv(filename, header=0)
        lastTimeStamp = df.iloc[-1, 0]
        lastDateTime = datetime.datetime.strptime(lastTimeStamp,
                                                  "%Y-%m-%dT%H:%M:%S.000Z")
        fromYear = lastDateTime.year
        fromMonth = lastDateTime.month
        fromDay = lastDateTime.day

        print("Crawling from", lastTimeStamp)

        histData.recorded = list(df.timestamp)
        histData.bin1mHistory = []
        self.crawlFR()

        for year in range(fromYear, 2021):
            startMonth = fromMonth if year == fromYear else 1
            dayOfMonth = histData.dayOfMonthYear if self.isYear(
                year) else histData.dayOfMonthNotYear
            for month in range(startMonth, 13):
                startDay = fromDay if (year == fromYear
                                       and month == fromMonth) else 1
                for day in range(startDay, dayOfMonth[month - 1] + 1):
                    for hour in range(0, 2):
                        hour = str(hour * 12).zfill(2)
                        month = str(month).zfill(2)
                        timestamp = "%d-%s-%dT%s:00:00.000Z" % (year, month,
                                                                day, hour)
                        timestamp = datetime.datetime.strptime(
                            timestamp, '%Y-%m-%dT%H:%M:00.000Z')
                        if (datetime.datetime.utcnow() -
                                timestamp).total_seconds() < 60:
                            break
                        else:
                            if self.coin == "BTC":
                                coin = "XBT"
                                crawl_url = histData.url.format(
                                    coin, str(timestamp))
                            elif self.coin == "ETH":
                                coin = "ETH"
                                crawl_url = histData.url.format(
                                    coin, str(timestamp))
                            while True:
                                time.sleep(sleep)
                                result = self.requestJSON(crawl_url)
                                if len(result
                                       ) > 0 and result[0]['timestamp'] != '':
                                    for i in range(0, len(result)):
                                        if (result[i]['timestamp'] not in
                                                histData.recorded[-7200:]):
                                            fundingRate = self.getFundingRate(
                                                result[i]['timestamp'])
                                            histData.bin1mHistory.append(
                                                list(result[i].values()) +
                                                [float(fundingRate)])
                                            histData.recorded.append(
                                                result[i]['timestamp'])
                                    print(
                                        datetime.datetime.now(), "Crawling " +
                                        str(timestamp) + ".... Total: " +
                                        str(len(result)) + " data")
                                    break
                                else:
                                    print("Request ", str(timestamp),
                                          " Error! .... Total: ",
                                          str(len(result)), " data")
        self.writeFile(filename)

    def plot(self, filename):
        rawData = pd.read_csv(filename)
        rawData['timestamp'] = pd.to_datetime(rawData['timestamp'])
        rawData.index = rawData['timestamp']
        rawData['volume'].plot()
        (rawData['vwap'] * 4500).plot(color="red")
        plt.show()


if __name__ == '__main__':
    # TODO: VWAP=NA?
    history = histData()
    # history.crawlAll("ETH","ETH.csv")
    history.complement("BTC", "BTC.csv")
    history.complement("ETH", "ETH.csv")
