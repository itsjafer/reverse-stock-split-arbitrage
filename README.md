# Reverse Stock Split Arbitrage

![Past performance](performance.png)

Reverse Stock Split Arbitrage is a method by which an investor purchases fractional shares of a company that is expected to offer a reverse stock split in the hopes of receiving "rounded up" shares. 

For example, if $ABC announces a 10-for-1 reverse stock split, purchasing 1 share before the split will result in brokers (such as Robinhood, Alpaca, and WeBull) rounding up your single share to 10 in order to perform the reverse stock split resulting in an effective gain of 9 shares.

For more information, check out the [reverse split arbitrage](https://www.reversesplitarbitrage.com/) website, which is run by [@reverseSplitArb](https://twitter.com/reverseSplitArb)

This repo is a GCP Cloud Functions script that connects to several brokerage accounts and automatically buys and sells stocks that are going to reverse stock split soon (based on information provided by @reverseSplitArb) in order to generate a profit.

## How it works

1. Whenever @reverseSplitArb tweets, a post request is made to Google Cloud Functions. (This can be set up using IFTTT or a custom tweepy listener).
2. Google Cloud Functions runs `main.py` which purchases the stock mentioned in the tweet on all supported brokers.
3. When a reverse stock split happens, our accounts should have rounded up shares that we previously bought.
4. When @reverseSplitArb tweets again to signal that the stock split happened as expected, our google cloud functions runs again and sell the shares.
5. Profit!

## Currently supported brokers

* **Robinhood**: requires setting up multifactor authentication
  * Sign into your robinhood account and turn on two factor authentication. Robinhood will ask you which two factor authorization app you want to use. Select "other". Robinhood will present you with an alphanumeric code. This is your `MFA TOKEN`. Make sure to put this into Google Authenticator, Duo, or an authenticator of your choice.
* **Alpaca**: requires secret and public access key (available on the dashboard)
* **Webull**: requires access token, refresh token, token expiration, UUID, and trade token (follow [this guide](https://github.com/tedchou12/webull/wiki/MFA-&-Security))
* **Webull** (second account) - WeBull allows for two accounts (one margin, one cash)
* **Ally Invest** (Untested while I wait for my funds to clear) - Follow the instructions [here](https://alienbrett.github.io/PyAlly/installing.html#get-the-library) to get credentials.


## Getting set up

First, we need to get our credentials set up. Run `python main.py --setup` and follow the prompts to save your credentials to `.env` so we're able to place orders.

If you'd prefer to set the environment variables yourself, the script requires the following environment variables set:
```
RH_MFA_TOKEN # The robinhood MFA token found under the security section of your account
RH_USERNAME
RH_PASSWORD
ALPACA_ACCESS_KEY_ID # Alpaca's access key id
ALPACA_SECRET_ACCESS_KEY # Alpaca's secret key
WB1_ACCESS_TOKEN # webull
WB1_REFRESH_TOKEN # webull
WB1_TOKEN_EXPIRATION # webull
WB1_UUID # webull
WB1_TRADE_TOKEN # six digit trading pass code for webull
WB2_ACCESS_TOKEN # webull
WB2_REFRESH_TOKEN # webull
WB2_TOKEN_EXPIRATION # webull
WB2_UUID # webull
WB2_TRADE_TOKEN # six digit trading pass code for webull
```

Once you've got credentials set up, you can call the script by running `python main.py --tweet text of the message goes here`. For example, `python main.py --dryrun --tweet "I'm buying 4 shares of \$TSLA"` will trigger the script to do a dryrun attempt to buy 4 shares of TSLA on all accounts linked. Note that the dollar sign had to be escaped because bash interprets `$TSLA` as a variable.

## To Do

* Add a Tweepy listener to this repo so that anyone can run the entire process on their local machine without having to set anything else up (like GCP/IFTTT)
* Set up this script as a package that can be installed and used from the commandline or programmatically
* Add more brokers 
* Add a front end to show returns/results
* Find stock splits using an API rather than a twitter account

### Future broker support

Currently, I've investigated APIs for these brokerages:
* ~~Tradier~~ - Authentication for the API requires human intervention every 24 hours
* ~~TradeStation~~ -- API use requires a $10k deposit so this is a no go until I'm rich
* ~~Tastyworks~~ -- Unofficial API doesn't support equity trading

I'm also planning to look into using headless chromium to place orders with brokers that don't have public APIs.
