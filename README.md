# Reverse Split Automation

Reverse Stock Split Arbitrage is a method by which an investor purchases a single (or sometimes more) share of a company that is expected to offer a reverse stock split. 
In doing so, some brokers will "round up" the shares to keep the investor holding a single share even after the reverse stock split. This results in a profit equal in value to the number of shares that underwent reverse stock splitting.

For more information, check out @reversesplitarb on twitter; this cloud function makes purchase decisions directly based on reverse stock splits reported by @reversesplitarb.

## How it works

1. Whenever @reverseSplitArb tweets, a post request is made to Google Cloud Functions. (This can be set up using IFTTT or a custom tweepy listener).
2. Google Cloud Functions runs `main.py` which purchases the stock mentioned in the tweet (if any) on robinhood and alpaca.
3. In the future, selling decisions will also be made automatically, but currently they must be done manually
4. Profit!


