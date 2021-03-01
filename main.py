import requests
import collections
import string
import os
import alpaca_trade_api as tradeapi
import json
import pyotp
import time
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone
from webull import webull
import robin_stocks.robinhood as r

def hello_world(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        print("options")
        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    responseFail = {
        "success": "false" 
    }
    response = {
        "success": "true" 
    }

    request_json = request.get_json()
    tweet = request_json['tweet'].lower()
    print(tweet) # for logging
    
    # load environment variables
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)

    # Initialize alpaca, webull, and robinhood 
    alpaca, wb = init()

    # Get the stock ticker from the tweet
    ticker, qty = getStockTicker(tweet)
    print(ticker, qty)

    # If we have no ticker in the tweet, there's nothing to do
    if ticker == "":
        return (json.dumps(responseFail, default=str), 200, headers)
    # if we have a ticker but no quantity, we might want to sell
    elif len(ticker) > 0 and qty <= 0:
        # Let's see if we mentioned any relevant keywords
        if ("sell" not in tweet and "sold" not in tweet and "selling" not in tweet):
            return (json.dumps(responseFail, default=str), 200, headers)

        alpacaSold = tradeAlpaca(alpaca, ticker)
        if not alpacaSold:
            print("Unable to sell on Alpaca")
        robinhoodSold = tradeRobinhood(ticker)
        if not robinhoodSold:
            print("Unable to sell on robinhood")
        webullSold = tradeWebull(wb, ticker)
        if not webullSold:
            print("Unable to sell on webull")
        if alpacaSold and robinhoodSold and webullSold:
            return (json.dumps(response, default=str), 200, headers)

        return (json.dumps(responseFail, default=str), 200, headers)

    # Otherwise, we have a ticker, and we have a quantity
    # Get a price at which we want to buy
    bars = alpaca.get_barset(ticker, "minute", 1)
    price = float(bars[ticker][0].c)

    order = None
    alpacaBuy = tradeAlpaca(alpaca, ticker, price, qty)
    if not alpacaBuy:
        print("Unable to buy on Alpaca")
    robinhoodBuy = tradeRobinhood(ticker, price, qty)
    if not robinhoodBuy:
        print("Unable to buy on robinhood")
    webullBuy = tradeWebull(wb, ticker, price, qty)
    if not webullBuy:
        print("Unable to buy on Webull")
    exit()

    if alpacaBuy and robinhoodBuy and webullBuy:
        return (json.dumps(response, default=str), 200, headers)

    return (json.dumps(responseFail, default=str), 200, headers)

def init():
    # Set up alpaca
    alpaca = tradeapi.REST(
        os.getenv("ACCESS_KEY_ID"),
        os.getenv("SECRET_ACCESS_KEY"),
        base_url="https://paper-api.alpaca.markets"
    )

    # Set up robinhood
    totp  = pyotp.TOTP(os.getenv("MFA_TOKEN")).now()
    print("Current OTP:", totp)
    login = r.login(os.getenv("RH_USERNAME"), os.getenv("RH_PASSWORD"), mfa_code=totp)

    # set up webull
    wb = webull()
    wb.api_login(
        access_token=os.environ.get("ACCESS_TOKEN"), 
        refresh_token=os.environ.get("REFRESH_TOKEN"), 
        token_expire=os.environ.get("TOKEN_EXPIRATION"), 
        uuid=os.environ.get("UUID")
    )
    wb.get_trade_token(os.environ.get("TRADE_TOKEN"))

    return alpaca, wb


def tradeAlpaca(alpaca, ticker, price=0, qty=0):
    # if we're given a quantity, we're looking to buy
    if qty > 0 and price > 0:
    # buy the stock on Alpaca
        try:
            order = alpaca.submit_order(
                symbol=ticker,
                qty=qty,
                side='buy',
                type='limit',
                limit_price=price*1.1,
                extended_hours=True,
                time_in_force='day'
            )
            print(order)
            return True
        except:
            return False

    # If quantity is 0 or not given, we assume we're looking to sell
    # Get see if we have it in our alpaca portfolio
    try:
        position = alpaca.get_position(ticker) # Try to get a position for this ticker
        qty = int(float(position.qty))
        if qty <= 0:
            raise Exception()
    except:
        return False

    try:
        # Sell on Alpaca
        alpaca.submit_order(
            symbol=ticker,
            qty=qty,
            side="sell",
            type="market",
            time_in_force="gtc"
        )
    except:
        return False
    return True

def tradeRobinhood(ticker, price=0, qty=0):
    # If we're given a quantity, we're looking to buy
    if qty > 0 and price > 0:
        # buy the stock on robinhood
        try: 
            order = r.order(
                symbol=ticker,
                quantity=qty,
                side="buy",
                limitPrice=price*1.1,
                timeInForce='gfd',
                extendedHours='true'
            )
            print(order)
            return True
        except:
            print("Unable to purchase on Robinhood")
            return False

    # Otherwise, we're looking to sell
    holdings = r.build_holdings()
    if ticker in holdings:
        try:
            qty = int(float(holdings[ticker]['quantity']))
        except:
            return False
    else:
        return False
    
    if qty <= 0:
        return False

    try:
        order = r.order_sell_market(
            symbol=ticker,
            quantity=qty,
            timeInForce='gtc',
            extendedHours='true'
        )
        print(order)
    except:
        return False

    return True

def tradeWebull(wb, ticker, price=0, qty=0):

    # If we're given a qty, we buy
    if qty > 0 and price > 0:
        try:
            # Webull requires 100 shares purchase minimum for shares under $1
            if price < 1:
                # Buy 100 + qty shares
                order= wb.place_order(
                    stock=ticker,
                    price=price*1.1, 
                    action='BUY', 
                    orderType='LMT', 
                    enforce='GTC', 
                    quant=qty+100
                )
                print(order)

                # Wait until we buy it
                attempts = 10
                while attempts > 0:
                    positions = wb.get_positions()
                    tickers = [position['ticker']['symbol'] for position in positions]
                    if ticker in tickers:
                        print("Found the ticker!")
                        break
                    time.sleep(1)
                    attempts -= 1
                    if attempts <= 1:
                        raise Exception()

                # Sell 100 shares
                order = wb.place_order(
                    stock=ticker,
                    price=price*1.1, 
                    action='BUY', 
                    orderType='LMT', 
                    enforce='GTC', 
                    quant=100
                )
                print(order)
                return True
            
            # Buy qty shares
            order = wb.place_order(
                stock=ticker,
                price=price*1.1, 
                action='BUY', 
                orderType='LMT', 
                enforce='GTC', 
                quant=qty
            )
            print(order)
            return True
            
        except:
            return False

    positions = wb.get_positions()
    tickers = [position['ticker']['symbol'] for position in positions]
    qty = 0
    for position in positions:
        if position['ticker']['symbol'] == ticker:
            qty = int(float(position['position']))

    if qty <= 0:
        return False

    try:
        # Sell on webull
        order = wb.place_order(
            stock=ticker, 
            action='SELL', 
            orderType='MKT',
            enforce='DAY', 
            quant=qty
        )
        print(order)
    except:
        return False

    return True

def getAllTickers():
    from urllib.request import urlopen

    r = urlopen("https://www.sec.gov/include/ticker.txt")

    tickers = {line.decode('UTF-8').split("\t")[0].upper() for line in r}
    return tickers

def getStockTicker(tweet):
    allTickers = getAllTickers()
    try: 
        amount = tweet.split("i'm buying ")
        amount = amount[1] # the part right after "im buying"
        amount = int(amount.split(" ")[0])
    except:
        amount = -1

    for word in tweet.split(" "):
        if '$' not in word:
            continue
        word = word.replace("$", "")
        word = word.translate(str.maketrans('', '', string.punctuation))
        if word.upper() not in allTickers:
            continue
        return word.upper(), amount

    return "", amount

# For local testing
class Object(object):
    pass

# if __name__ == "__main__":
#     request = Object()
#     request.method = "GET"
#     request.get_json = lambda: {"tweet": "i'm selling 1 share of $GHSI today"}
#     hello_world(request)