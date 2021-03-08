import ally
"""
 Trading Functions 
"""
def tradeAlpaca(alpaca, ticker, price=0, qty=0, dryrun=False):

    if not alpaca:
        return False
    # if we're given a quantity, we're looking to buy
    if qty > 0 and price > 0:

        if dryrun:
            print(f"Dryrun: We would buy {qty} {ticker} on Alpaca for {price}")
            return True
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

    if dryrun:
        print(f"Dryrun: We are selling {qty} {ticker} on Alpaca")
        return True
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

def tradeRobinhood(r, ticker, price=0, qty=0, dryrun=False):
    if not r:
        return False
    # If we're given a quantity, we're looking to buy
    if qty > 0 and price > 0:

        if dryrun:
            print(f"Dryrun: We would buy {qty} {ticker} on Robinhood for {price}")
            return True

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

    if dryrun:
        print(f"Dryrun: We are selling {qty} {ticker} on Robinhood")
        return True

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

def tradeWebull(wb, ticker, price=0, qty=0, dryrun=False):
    if not wb:
        return False
    # If we're given a qty, we buy
    if qty > 0 and price > 0:
        try:
            # Webull requires 100 shares purchase minimum for shares under $1
            if price < 1:

                if dryrun:
                    print(f"Dryrun: We would buy {qty+100} {ticker} on Webull at {price}, then sell 100 shares")
                    return True
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
            

            if dryrun:
                print(f"Dryrun: We would buy {qty} {ticker} on Webull for {price}")
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

    if dryrun:
        print(f"Dryrun: We are selling {qty} {ticker} on Webull")
        return True

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

def tradeAlly(a, ticker, price=0, qty=0, dryrun=False):

    if not a:
        return False
    # if we're given a quantity, we're looking to buy
    if qty > 0 and price > 0:

        if dryrun:
            print(f"Dryrun: We would buy {qty} {ticker} on Ally for {price}")
    # buy the stock on Ally
        try:
            order = ally.Order.Order(
                buysell = 'buy',
                symbol=ticker,
                price=ally.Order.Limit(price*1.1),
                time = 'day',
                qty=qty
            )
            print(str(order))
            if dryrun:
                return True
            a.submit(order)
            return True
        except:
            return False

    # If quantity is 0 or not given, we assume we're looking to sell
    # Get see if we have it in our ally portfolio
    try:
        # Untested because my Ally account hasn't been cleared yet
        qty = 0
        positions = a.holdings(dataframe=False)
        for position in positions:
            if ticker == positions[position]['sym']:
                qty = int(float(positions[position]['qty']))
        if qty <= 0:
            raise Exception()
    except:
        return False

    if dryrun:
        print(f"Dryrun: We are selling {qty} {ticker} on Ally")
    try:
        # Sell on Ally
        order = ally.Order.Order(
            buysell = 'sell',
            symbol=ticker,
            price=ally.Order.Market(),
            time = 'day',
            qty=qty
        )
        print(str(order))
        if dryrun:
            return True
        a.submit(order)
    except:
        return False
    return True
