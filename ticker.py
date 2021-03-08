from urllib.request import urlopen
import string

def getAllTickers():

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