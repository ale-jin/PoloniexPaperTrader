import urllib.request, urllib.parse, urllib.error
import json
import time
import requests
import hmac,hashlib
from urllib.parse import urlencode

#Refer to https://poloniex.com/support/api/ for more information on the returned data

#This class fetches live market data from Poloniex
class MarketData:
    def __init__(self,currencyPair):

        url = ('https://poloniex.com/public?command=returnTradeHistory' +
        '&currencyPair=%s' % currencyPair)
        ret = requests.get(url)
        current = json.loads(ret.text)[0]

        self._globalTradeID = current['globalTradeID']
        self._tradeID = current['tradeID']
        self._date = current['date']
        self._type = current['type']
        self._rate = current['rate']
        self._amount = current['amount']
        self._total = current['total']

    def getGlobalTradeID(self):
        globalTradeID = self._globalTradeID
        return globalTradeID

    def getTradeID(self):
        tradeID = self._tradeID
        return tradeID

    def getDate(self):
        date = self._date
        return date

    def getTradeType(self):
        tradeType = self._type
        return tradeType

    def getRate(self):
        rate = self._rate
        return rate

    def getAmount(self):
        amount = self._amount
        return amount

    def getTotal(self):
        total = self._total
        return total

#This class fetches chart data from Poloniex
class ChartData:

    def __init__(self, currencyPair, start, end, period):

        url = ('https://poloniex.com/public?command=returnChartData' +
            '&currencyPair=%s&start=%s&end=%s&period=%s' %
            (currencyPair,start,end,period))
        try:
            ret = requests.get(url)
            print(ret)
        except:
            print("Failed to fetch chart data")
            print(ret)

        rawData = json.loads(ret.text)

        self._date = []
        self._high = []
        self._low = []
        self._open = []
        self._close = []
        self._volume = []
        self._quoteVolume = []
        self._weightedAverage = []

        for item in rawData:
            self._date.append(item["date"])
            self._high.append(item["high"])
            self._low.append(item["low"])
            self._open.append(item["open"])
            self._close.append(item["close"])
            self._volume.append(item["volume"])
            self._quoteVolume.append(item["quoteVolume"])
            self._weightedAverage.append(item["weightedAverage"])

    def getDates(self):
        date = self._date
        return date

    def getHigh(self):
        high = self._high
        return high

    def getLow(self):
        low = self._low
        return low

    def getOpen(self):
        p_open = self._open
        return p_open

    def getClose(self):
        close = self._close
        return close

    def getVolume(self):
        volume = self._volume
        return volume

    def getQuoteVolume(self):
        qVolume = self._quoteVolume
        return qVolume

    def getWeightedAverage(self):
        wAverage = self._quoteVolume
        return wAverage

#This class fetches the orderbook from Poloniex
class OrderBook:
    def __init__(self,currencyPair,depth):
        self._asks = []
        self._bids = []
        self._isFrozen = []

        url = ('https://poloniex.com/public?command=returnOrderBook' +
        '&currencyPair=%s&depth=%s' % (currencyPair,depth))
        try:
            ret = requests.get(url)
        except:
            print("Failed to fetch orderbook")

        data = json.loads(ret.text)

        for order in data['asks']:
            self._asks.append(order)

        for order in data['bids']:
            self._bids.append(order)

        for order in data['isFrozen']:
            self._isFrozen.append(order)


    def getAsks(self):
        asks = self._asks
        return asks

    def getBids(self):
        bids = self._bids
        return bids

    def getIsFrozen(self):
        isFrozen = self._isFrozen
        return isFrozen
