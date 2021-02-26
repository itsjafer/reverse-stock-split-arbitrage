import requests
import collections
import string
import os
import alpaca_trade_api as tradeapi
import json
import pyotp
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone
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

    request_json = request.get_json()
    tweet = request_json['tweet'].lower()
    print(tweet) # for logging
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)

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

    # Get the tweet
    # Get the stock ticker from the tweet
    ticker, qty = getStockTicker(tweet)
    print(ticker, qty)
    if ticker == "" and qty <= 0:
        response = {
            "success": "false" 
        }
        return (json.dumps(response, default=str), 200, headers)
    elif len(ticker) > 0 and qty <= 0:
        # Looks like maybe a stock was mentioned, let's see if we can sell it
        # Get quantity
        try:
            position = alpaca.get_position(ticker)
            qty = int(float(position.qty))
            if qty <= 0:
                raise Exception()
        except:
            response = {
                "success": "false" 
            }
            return (json.dumps(response, default=str), 200, headers)
        print("Im about to sell", ticker, qty)
        # Sell on Alpaca
        alpaca.submit_order(
            symbol=ticker,
            qty=qty,
            side="sell",
            type="market",
            time_in_force="gtc"
        )

        # Sell on robinhood
        order = r.order_sell_market(
            symbol=ticker,
            quantity=1,
            timeInForce='gtc',
            extendedHours='true'
        )

        response = {
            "success": "true" 
        }

        return (json.dumps(response, default=str), 200, headers)

    bars = alpaca.get_barset(ticker, "minute", 1)
    price = float(bars[ticker][0].c)
    print(price)
    print("Im about to buy", qty, ticker, price)

    # buy the stock on Alpaca
    try:
        alpaca.submit_order(
            symbol=ticker,
            qty=qty,
            side='buy',
            type='limit',
            limit_price=price*1.1,
            extended_hours=True,
            time_in_force='day'
        )
    except:
        print("Unable to purchase on Alpaca")

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
    except:
        print("Unable to purchase on Robinhood")
        
    print(order)

    response = {
        "success": "true" 
    }

    return (json.dumps(response, default=str), 200, headers)

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
# class Object(object):
#     pass

# if __name__ == "__main__":
#     request = Object()
#     request.method = "GET"
#     request.get_json = lambda: {"tweet": "Sold $SXTC today!"}
#     hello_world(request)