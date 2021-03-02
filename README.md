# Reverse Split Automation

Reverse Stock Split Arbitrage is a method by which an investor purchases fractional shares of a company that is expected to offer a reverse stock split in the hopes of receiving "rounded up" shares. 



For example, if $ABC announces a 10-for-1 reverse stock split, purchasing 1 share before the split will result in brokers (such as Robinhood, Alpaca, and WeBull) rounding up your single share to 10 in order to perform the reverse stock split resulting in an effective gain of 9 shares.

For more information, check out the [reverse split arbitrage](https://www.reversesplitarbitrage.com/) website, which is run by [@reverseSplitArb](https://twitter.com/reverseSplitArb)

## How it works

1. Whenever @reverseSplitArb tweets, a post request is made to Google Cloud Functions. (This can be set up using IFTTT or a custom tweepy listener).
2. Google Cloud Functions runs `main.py` which purchases the stock mentioned in the tweet on all supported brokers.
3. When a reverse stock split happens, our accounts should have rounded up shares that we previously bought.
4. When @reverseSplitArb tweets again to signal that the stock split happened as expected, our google cloud functions runs again and sell the shares.
5. Profit!

## Getting set up

### Currently supported brokers

* **Robinhood**: requires setting up multifactor authentication (follow [this guide](https://github.com/jmfernandes/robin_stocks/blob/master/Robinhood.rst#with-mfa-entered-programmatically-from-time-based-one-time-password-totp))
* **Alpaca**: requires secret and public access key (available on the dashboard)
* **Webull**: requires access token, refresh token, token expiration, UUID, and trade token (follow [this guide](https://github.com/tedchou12/webull/wiki/MFA-&-Security))

### Future broker support

Currently, I'm looking at incorporating the following brokerages:
* **Webull** (second account) - WeBull allows for two accounts (one margin, one cash)
* **Tradier** - It's unclear whether they charge any fees on reverse stock splits
* **Ally Invest**
* **TradeStation** -- Their API documentation seems to have a lot of red tape
* **Interactive Brokers** -- Uncomfirmed whether they round up
* **Tastyworks** -- Unofficial API seems to be focused on options trading not stocks

The script requires the following environment variables set:

```
MFA_TOKEN # The robinhood MFA token found under the security section of your account
RH_USERNAME
RH_PASSWORD
ACCESS_KEY_ID # Alpaca's access key id
SECRET_ACCESS_KEY # Alpaca's secret key
ACCESS_TOKEN # webull
REFRESH_TOKEN # webull
TOKEN_EXPIRATION # webull
UUID # webull
TRADE_TOKEN # six digit trading pass code for webull

```

