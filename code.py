import signal
import requests
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from time import sleep

# this class definition allows us to print error messages and stop the program when needed

class ApiException(Exception):
    pass
# this signal handler allows for a graceful shutdown when CTRL+C is pressed

def signal_handler(signum, frame):
    global shutdown
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    shutdown = True

API_KEY = {'X-API-Key': 'B4TS6TGN'}
shutdown = False

def get_tick(session):
    resp = session.get('http://localhost:9999/v1/case')
    if resp.ok:
        case = resp.json()
        return case['tick']
    raise ApiException('The API key provided in this Python code must match that in \
the RIT client (please refer to the API hyperlink in the client toolbar and/or the \
RIT – User Guide – REST API Documentation.pdf)')

def ticker_bid_ask(session, ticker):
    payload = {'ticker': ticker}
    resp = session.get('http://localhost:9999/v1/securities/book', params=payload)
    if resp.ok:
        book = resp.json()
        return book['bids'][0]['price'], book['asks'][0]['price']
    raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')

# setting up dataframe to collect data

def get_close(session, ticker, period = 1, limit = 1):
    par = {"ticker": ticker, "period": period, "limit": limit}
    resp = session.get('http://localhost:9999/v1/securities/history', params = par)
    if resp.ok:
        quote = resp.json()
        return quote[0]['close']
    raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')

# strategy definition

volume = 10000
orderdata = pd.DataFrame()

def dataregister(dataframe):
    with requests.Session() as s:
        s.headers.update(API_KEY)
        tick = get_tick(s)

        CRZY_m_prices = np.array([])
        CRZY_a_prices = np.array([])
        tickregister = np.array([])

        while tick > 5 and tick < 295 and not shutdown:

            # recording close 
            
            crzy_m_close = get_close(s, "CRZY_M")
            crzy_a_close = get_close(s, "CRZY_A")
            print("CRZY_A close is",crzy_a_close,"CRZY_M close is",crzy_m_close)
            CRZY_m_prices = np.append(CRZY_m_prices, crzy_m_close)
            CRZY_a_prices = np.append(CRZY_a_prices, crzy_a_close)
            tickregister = np.append(tickregister, tick)

            print(CRZY_m_prices, CRZY_a_prices,tickregister)

        dataframe = pd.DataFrame({"time": tickregister, "CRZY_A": CRZY_m_prices, "CRZY_M": CRZY_a_prices})


def main():
    with requests.Session() as s:
        s.headers.update(API_KEY)
        tick = get_tick(s)

        while tick > 5 and tick < 295 and not shutdown:
            
            crzy_m_bid, crzy_m_ask = ticker_bid_ask(s, 'CRZY_M')
            crzy_a_bid, crzy_a_ask = ticker_bid_ask(s, 'CRZY_A')
            
            if crzy_m_bid > crzy_a_ask:
                buy_params = {'ticker': 'CRZY_A', 'type': 'MARKET', 'quantity': volume, 'action': 'BUY'}
                sell_params = {'ticker': 'CRZY_M', 'type': 'MARKET', 'quantity': volume, 'action': 'SELL'}
                s.post('http://localhost:9999/v1/orders', params=buy_params)
                s.post('http://localhost:9999/v1/orders', params=sell_params)
                print('Bought for',crzy_a_ask,'Sold for', crzy_m_bid)

            if crzy_a_bid > crzy_m_ask:
                buy_params = {'ticker': 'CRZY_M', 'type': 'MARKET', 'quantity': volume, 'action': 'BUY'}
                sell_params = {'ticker': 'CRZY_A', 'type': 'MARKET', 'quantity': volume, 'action': 'SELL'}
                s.post('http://localhost:9999/v1/orders', params=buy_params)
                s.post('http://localhost:9999/v1/orders', params=sell_params)
                print('Bought for',crzy_m_ask,'Sold for', crzy_a_bid)

            sleep(1)
                
            # IMPORTANT to update the tick at the end of the loop to check that the algorithm should still run or not
            tick = get_tick(s)

if __name__ == '__main__':
    # register the custom signal handler for graceful shutdowns
    signal.signal(signal.SIGINT, signal_handler)
    main()
    dataregister(orderdata)
    
