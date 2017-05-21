import time
import datetime
import numpy as np
import talib
from matplotlib import style
from PoloniexDatabase import MarketData
from PoloniexDatabase import ChartData
from PoloniexDatabase import OrderBook

#CONFIGURE CURRENCYPAIR TO TRADE AND CANDLE SIZE
CURRENCY     = 'BTC'
ASSET        = 'ETH'
PAIR         = ('%s_%s'%(CURRENCY, ASSET))
CANDLE       = [300, 900, 1800, 7200, 14400, 86400]
INTERVAL     = CANDLE[0]
PERIOD       = 1000       #How many candles
END          = 9999999999 #Set when live test will end.
                          #9999999999 is to current; else unix;

# INITIALIZED STORAGE VALUES
storage = {}
storage['trades'] = 0

# STARTING PORTFOLIO
portfolio = {}
portfolio['assets'] = 0
portfolio['currency'] = 1


# ----------- SETTINGS FOR ChartData -----------#

# INFO OBJECTS
info = {}
info['begin'] = int(time.time())-PERIOD*INTERVAL
info['index'] = 0
info['interval'] = INTERVAL
info['current_time'] = info['begin']
info['end']=info['begin']+PERIOD*INTERVAL
SATOSHI = 0.00000001
ANTISAT = 100000000.0

def pullHistoricalData():
    try:
        data = ChartData(PAIR, info['begin'], END, INTERVAL)
    except:
        print("Failed to fetch HistoricalData")

    close_prices = data.getClose()
    ### ------ Uncomment Data You Would Need ------###
    #dates = chartdata.getDates()
    #volume = chartdata.getVolume()
    #high = chartdata.getHigh()
    #low = chartdata.getLow()
    #open_prices = chartdata.getOpen()
    #quoted_volume = chartdata.getQuoteVolume()
    #weighted_average = getWeightedAverage()

    return close_prices
    #return dates, close_prices, volume, high, low, open_prices, quoted_volume, weighted_average

#Helper Methods (from litepresence)
def holdings(initial_price):

    # STORE STARTING PORTFOLIO
    storage['begin_max_assets']=(
        portfolio['currency']/(initial_price)+portfolio['assets'])
    storage['begin_max_currency']=(
        portfolio['currency']+portfolio['assets']*(initial_price))
    storage['start_price'] = initial_price

def test_sell(time, price):

        portfolio['currency'] = portfolio['assets']*price
        print ('[%s] %s SELL %.2f %s at %s sat value %.2f %s' % (time,
            storage['trades'], portfolio['assets'], ASSET, price/SATOSHI,
            portfolio['currency'], CURRENCY))
        portfolio['assets'] = 0
        #ax1.plot(time,price,markersize=8,marker='o',color='coral',label='sell')

def test_buy(time, price):

        portfolio['assets'] = portfolio['currency']/(price)
        print ('[%s] %s BUY %.2f %s at %s sat value %.2f %s' % (time,
            storage['trades'], portfolio['assets'], ASSET, price/SATOSHI,
            portfolio['currency'], CURRENCY))
        portfolio['currency'] = 0
        #ax1.plot(time,price,markersize=8,marker='o',color='lime',label='buy')


#NON MAINLOOP OBJECTS
CANDLESIZE = INTERVAL
CONTEXT = pullHistoricalData()[CANDLESIZE:]

#MAIN LOOP
def main():
    #START = 0
    START = time.time()
    TICK  = START
    SLEEPINTERVAL = 1

    #Set depth of orderbook
    BOOKDEPTH = 20

    #INITIALIZE INITIAL HOLDINGS
    holdings(CONTEXT[-1])

    try:
        while TICK < END:
            try:
                LiveData = MarketData(PAIR)
                Book     = OrderBook(PAIR, BOOKDEPTH)

            except Exception as e:
                print('Failed to fetch live data')
                break

                TICK = TICK + 1

            #Market Vars
            now = time.time()
            price = LiveData.getRate()
            amount = LiveData.getAmount()
            asks = Book.getAsks()
            bids = Book.getBids()

            #Update CONTEXTual Data
            if TICK%CANDLESIZE == 0:
                CONTEXT.append(price)


            #--------------------------------IMPLEMENT STRATEGY HERE--------------------------------------------#
            upper, middle, lower = talib.BBANDS(np.array(CONTEXT), CANDLESIZE, nbdevup=2,nbdevdn=2,matype=0)

            # If price is below the recent lower band and we have
            # no long positions then invest the entire
            #portfolio value into ASSET
            if float(price) < float(lower[0]):
                if portfolio['currency'] > 0:
                    test_buy(time = now, price=asks[0])
                    storage['trades']+=1
             # If price is above the recent upper band and we have
             # no short positions then invest the entire
             # portfolio value to short ASSET
            elif float(price) > float(upper[0]):
               if portfolio['assets'] > 0:
                   test_sell(time = now, price=bids[0])
                   storage['trades']+=1



            #HOUSEKEEPING
            print("TIME: %s, MARKET PRICE: %s, Volume: %s"
                % (datetime.datetime.utcfromtimestamp(now),price,amount))
            if(len(CONTEXT) > CANDLESIZE):
                CONTEXT.pop(0)
            time.sleep(SLEEPINTERVAL)


    except KeyboardInterrupt:
        print ('\nKeyboardinterrupt caught (again)    ')
        print ('\n----------END OF LIVE TEST----------')


#ENDING SUMMARY (from litepresence)
def summary():

    # MOVE TO CURRENCY
    if portfolio['assets'] > 0:
        print('stop() EXIT TO CURRENCY')
        test_sell(info['end'], price = CONTEXT[-1])
    # CALCULATE RETURN ON INVESTMENT
    end_max_assets=(
        portfolio['currency']/(CONTEXT[-1])+portfolio['assets'])
    end_max_currency=(
        portfolio['currency']+portfolio['assets']*(CONTEXT[-1]))
    roi_assets = end_max_assets/storage['begin_max_assets']
    roi_currency = end_max_currency/storage['begin_max_currency']
    # FINAL REPORT
    print('===============================================================')
    print('START DATE........: %s' % time.ctime(info['begin']))
    print('END DATE..........: %s' % time.ctime(info['end']))
    print('START PRICE.......: %s satoshi' % ANTISAT*int(storage['start_price']))
    print('END PRICE.........: %s satoshi' % ANTISAT*int(CONTEXT[-1]))
    print('START MAX ASSET...: %.2f %s' % (storage['begin_max_assets'],ASSET))
    print('END MAX ASSET.....: %.2f %s' % (end_max_assets,ASSET))
    print('ROI ASSET.........: %.1fX' % roi_assets)
    print('START MAX CURRENCY: %.2f %s' % (storage['begin_max_currency'],CURRENCY))
    print('END MAX CURRENCY..: %.2f %s' % (end_max_currency, CURRENCY))
    print('ROI CURRENCY......: %.1fX' % roi_currency)
    print('===============================================================')
    print('~===END BACKTEST=========================~')


main()
summary()
