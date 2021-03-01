# Reverse Split Automation

Reverse Stock Split Arbitrage is a method by which an investor purchases fractional shares of a company that is expected to offer a reverse stock split in the hopes of receiving "rounded up" shares.

For example is $ABC announces a 10-for-1 reverse stock split, purchasing 1 share before the split will result in brokers (such as Robinhood, Alpaca, and WeBull) to round up the single share to 10, and then perform the reverse stock split resulting in an effective gain of 9 shares. Since only one share can be bought the profits are generally quite low in absolute value.

For more information, check out @reversesplitarb on twitter; this cloud function makes purchase decisions directly based on reverse stock splits reported by @reversesplitarb.

## How it works

1. Whenever @reverseSplitArb tweets, a post request is made to Google Cloud Functions. (This can be set up using IFTTT or a custom tweepy listener).
2. Google Cloud Functions runs `main.py` which purchases (or sells) the stock mentioned in the tweet on robinhood and alpaca.
3. Profit!

## Getting set up

### Currently supported brokers

* Robinhood: requires setting up multifactor authentication (follow [this guide](https://github.com/jmfernandes/robin_stocks/blob/master/Robinhood.rst#with-mfa-entered-programmatically-from-time-based-one-time-password-totp))
* Alpaca: requires secret and public access key (available on the dashboard)
* Webull: requires access token, refresh token, token expiration, UUID, and trade token (follow [this guide](https://github.com/tedchou12/webull/wiki/MFA-&-Security))

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

