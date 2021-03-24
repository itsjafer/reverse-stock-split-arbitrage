import requests
import collections
import string
import sys
import os
import alpaca_trade_api as tradeapi
import ally
import json
import pyotp
import time
import argparse
from pathlib import Path
from dotenv import load_dotenv
from dump_env import dumper
from datetime import datetime, timezone
from webull import webull
from ticker import getStockTicker
from trading import tradeAlpaca, tradeRobinhood, tradeWebull, tradeAlly
from setup_credentials import setup
import robin_stocks.robinhood as r
# load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

def request_response(request):
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
        return ('', 204, headers)
    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    # Default responses
    responseFail = {
        "success": "false" 
    }
    response = {
        "success": "true" 
    }
    # Get the tweet from the post request
    request_json = request.get_json()
    tweet = request_json['tweet'].lower()
    print(tweet) # for logging
    
    success = parse_tweet(tweet)

    if success:
        return (json.dumps(response, default=str), 200, headers)
    return (json.dumps(responseFail, default=str), 200, headers)

def parse_tweet(tweet, dryrun):
    tweet = tweet.lower()
    # Initialize alpaca, webull, and robinhood
    alpaca = initAlpaca()
    robinhood = initRobinhood()
    wb1, wb2 = initWebull()
    a = initAlly()

    # Get the stock ticker from the tweet
    ticker, qty = getStockTicker(tweet)

    # If we have no ticker in the tweet, there's nothing to do
    if ticker == "":
        print("No ticker found, nothing to do")
        return False
    # if we have a ticker but no quantity, we might want to sell
    elif len(ticker) > 0 and qty <= 0:
        # Let's see if we mentioned any relevant keywords
        if ("sell" not in tweet and "sold" not in tweet and "selling" not in tweet):
            return False

        alpacaSold = tradeAlpaca(alpaca, ticker, dryrun=dryrun)
        if not alpacaSold:
            print(f"Unable to sell {ticker} on Alpaca")
        robinhoodSold = tradeRobinhood(r, ticker, dryrun=dryrun)
        if not robinhoodSold:
            print(f"Unable to sell {ticker} on robinhood")
        webull1Sold = tradeWebull(wb1, ticker, dryrun=dryrun)
        if not webull1Sold:
            print(f"Unable to sell {ticker} on webull account #1")
        webull2Sold = tradeWebull(wb2, ticker, dryrun=dryrun)
        if not webull2Sold:
            print(f"Unable to sell {ticker} on webull account #2")
        allySold = tradeAlly(a, ticker, dryrun=dryrun)
        if not allySold:
            print(f"Unable to sell {ticker} on ally")
        if alpacaSold and robinhoodSold and webull1Sold and webull2Sold and allySold:
            return True

        return False 

    # Otherwise, we have a ticker, and we have a quantity
    # Get a price at which we want to buy
    bars = alpaca.get_barset(ticker, "minute", 1)
    price = float(bars[ticker][0].c)

    alpacaBuy = tradeAlpaca(alpaca, ticker, price, qty, dryrun=dryrun)
    if not alpacaBuy:
        print(f"Unable to buy {ticker} on Alpaca")
    robinhoodBuy = tradeRobinhood(r, ticker, price, qty, dryrun=dryrun)
    if not robinhoodBuy:
        print(f"Unable to buy {ticker} on robinhood")
    webull1Buy = tradeWebull(wb1, ticker, price, qty, dryrun=dryrun)
    if not webull1Buy:
        print(f"Unable to buy {ticker} on Webull account #1")
    webull2Buy = tradeWebull(wb2, ticker, price, qty, dryrun=dryrun)
    if not webull2Buy:
        print(f"Unable to buy {ticker} on Webull account #2")
    allyBuy = tradeAlly(a, ticker, price, qty, dryrun=dryrun)
    if not allyBuy:
        print(f"Unable to buy {ticker} on ally")
        
    if alpacaBuy and robinhoodBuy and webull1Buy and webull2Buy and allyBuy:
        return True 

    return False 

"""
Initialize our trading modules
"""

def initAlpaca():
    ALPACA_ACCESS_KEY_ID = os.getenv("ALPACA_ACCESS_KEY_ID")
    ALPACA_SECRET_ACCESS_KEY = os.getenv("ALPACA_SECRET_ACCESS_KEY")
    if len(ALPACA_ACCESS_KEY_ID) <= 0 or len(ALPACA_SECRET_ACCESS_KEY) <= 0:
        print("No Alpaca credentials supplied, skipping")
        return None
    # Set up alpaca
    alpaca = tradeapi.REST(
        ALPACA_ACCESS_KEY_ID,
        ALPACA_SECRET_ACCESS_KEY,
        base_url="https://api.alpaca.markets"
    )

    return alpaca

def initRobinhood():

    RH_MFA_TOKEN = os.getenv("RH_MFA_TOKEN")
    RH_USERNAME = os.getenv("RH_USERNAME")
    RH_PASSWORD = os.getenv("RH_PASSWORD")

    if len(RH_MFA_TOKEN) <= 0 or len(RH_USERNAME) <= 0 or len(RH_PASSWORD) <= 0:
        print("Missing robinhood credentials, skipping")
        return None

    # Set up robinhood
    totp  = pyotp.TOTP(RH_MFA_TOKEN).now()
    login = r.login(RH_USERNAME, RH_PASSWORD, mfa_code=totp)

    return r

def initWebull():

    # set up webull (first account)
    WB1_ACCESS_TOKEN = os.environ.get("WB1_ACCESS_TOKEN")
    WB1_REFRESH_TOKEN = os.environ.get("WB1_REFRESH_TOKEN")
    WB1_TOKEN_EXPIRATION = os.environ.get("WB1_TOKEN_EXPIRATION")
    WB1_UUID = os.environ.get("WB1_UUID")
    WB1_TRADE_TOKEN = os.environ.get("WB1_TRADE_TOKEN")

    if not (WB1_TRADE_TOKEN and WB1_ACCESS_TOKEN and WB1_REFRESH_TOKEN and WB1_TOKEN_EXPIRATION and WB1_UUID):
        print("No WeBull credentials given, skipping")
        return None, None
    wb1 = webull()
    wb1.api_login(
        access_token=WB1_ACCESS_TOKEN, 
        refresh_token=WB1_REFRESH_TOKEN, 
        token_expire=WB1_TOKEN_EXPIRATION, 
        uuid=WB1_UUID
    )
    wb1.get_trade_token(WB1_TRADE_TOKEN)

    # set up webull (second account)
    WB2_ACCESS_TOKEN = os.environ.get("WB2_ACCESS_TOKEN")
    WB2_REFRESH_TOKEN = os.environ.get("WB2_REFRESH_TOKEN")
    WB2_TOKEN_EXPIRATION = os.environ.get("WB2_TOKEN_EXPIRATION")
    WB2_UUID = os.environ.get("WB2_UUID")
    WB2_TRADE_TOKEN = os.environ.get("WB2_TRADE_TOKEN")
    if not (WB2_TRADE_TOKEN and WB2_ACCESS_TOKEN and WB2_REFRESH_TOKEN and WB2_TOKEN_EXPIRATION and WB2_UUID):
        print("Only one Webull account was given, credentials for second account were incomplete")
        return wb1, None
    wb2 = webull()
    wb2.api_login(
        access_token=WB2_ACCESS_TOKEN, 
        refresh_token=WB2_REFRESH_TOKEN, 
        token_expire=WB2_TOKEN_EXPIRATION, 
        uuid=WB2_UUID
    )
    wb2.get_trade_token(WB2_TRADE_TOKEN)

    return wb1, wb2

def initAlly():
    ALLY_CONSUMER_KEY = os.getenv("ALLY_CONSUMER_KEY")
    ALLY_CONSUMER_SECRET = os.getenv("ALLY_CONSUMER_SECRET")
    ALLY_OAUTH_TOKEN = os.getenv("ALLY_OAUTH_TOKEN")
    ALLY_OAUTH_SECRET = os.getenv("ALLY_OAUTH_SECRET")

    if not (ALLY_CONSUMER_KEY and ALLY_CONSUMER_SECRET and ALLY_OAUTH_TOKEN and ALLY_OAUTH_SECRET):
        print("No Ally credentials given, skipping")
        return None
    
    a = ally.Ally()
    # Wow, that was easy!
    return a

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--setup", help="perform first time credentials setup", action="store_true")
    parser.add_argument("tweet", nargs="?", help="the tweet we're using to decide whether to buy/sell")
    parser.add_argument("--dryrun", help="don't actually place orders", action="store_true")
    args = parser.parse_args()
    if args.setup:
        setup()
    if args.tweet:
        parse_tweet(args.tweet, args.dryrun)
