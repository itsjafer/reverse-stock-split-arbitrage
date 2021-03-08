import os
from webull import webull
from dotenv import load_dotenv
from dump_env import dumper
from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

"""
Setting up our login information for the first time
"""
def setup():
    print("Starting credentials set up...")
    print("Credentials will be saved to .env")
    print("=" * 10 + "Robinhood" + "=" * 10)
    print("**Leave empty to skip or keep old credentials**")
    # Get robinhood information
    RH_USERNAME = input("Robinhood Username: ")
    RH_PASSWORD = input("Robinhood Password: ")
    RH_MFA_TOKEN = input("Robinhood Two Factor Authentication Key (See README!): ")

    os.environ["RSA_RH_USERNAME"] = RH_USERNAME or os.getenv("RH_USERNAME") or ""
    os.environ["RSA_RH_PASSWORD"] = RH_PASSWORD or os.getenv("RH_PASSWORD") or ""
    os.environ["RSA_RH_MFA_TOKEN"] = RH_MFA_TOKEN or os.getenv("RH_MFA_TOKEN") or ""

    print("=" * 10 + "Alpaca" + "=" * 10)
    print("**Leave empty to skip or keep old credentials**")
    # Get alpaca information
    ALPACA_ACCESS_KEY_ID = input("Alpaca Access Key: ")
    ALPACA_SECRET_ACCESS_KEY = input("Alpaca Secret Key: ")

    os.environ["RSA_ALPACA_ACCESS_KEY_ID"] = ALPACA_ACCESS_KEY_ID or os.getenv("ALPACA_ACCESS_KEY_ID") or ""
    os.environ["RSA_ALPACA_SECRET_ACCESS_KEY"] = ALPACA_SECRET_ACCESS_KEY or os.getenv("ALPACA_SECRET_ACCESS_KEY") or ""
    
    print("=" * 10 + "Webull Account #1" + "=" * 10)
    print("**Leave empty to skip or keep old credentials**")
    # Get webull information
    setupWebull()

    print("=" * 10 + "Webull Account #2" + "=" * 10)
    print("**Leave empty to skip or keep old credentials**")
    # Get webull information
    setupWebull(2)    
    
    print("=" * 10 + "Ally Account" + "=" * 10)
    
    ALLY_ACCOUNT_NBR = input("Ally Account Number: ")

    print("Follow the instructions here to get your credentials: https://alienbrett.github.io/PyAlly/installing.html#get-the-library")
    ALLY_CONSUMER_KEY = input("ALLY_CONSUMER_KEY: ")
    ALLY_CONSUMER_SECRET = input("ALLY_CONSUMER_SECRET: ")
    ALLY_OAUTH_TOKEN = input("ALLY_OAUTH_TOKEN: ")
    ALLY_OAUTH_SECRET = input("ALLY_OAUTH_SECRET_TOKEN: ")
    os.environ["RSA_ALLY_ACCOUNT_NBR"] = ALLY_ACCOUNT_NBR or os.getenv("ALLY_ACCOUNT_NBR") or ""
    os.environ["RSA_ALLY_CONSUMER_KEY"] = ALLY_CONSUMER_KEY or os.getenv("ALLY_CONSUMER_KEY") or ""
    os.environ["RSA_ALLY_CONSUMER_SECRET"] = ALLY_CONSUMER_SECRET or os.getenv("ALLY_CONSUMER_SECRET") or ""
    os.environ["RSA_ALLY_OAUTH_TOKEN"] = ALLY_OAUTH_TOKEN or os.getenv("ALLY_OAUTH_TOKEN") or ""
    os.environ["RSA_ALLY_OAUTH_SECRET"] = ALLY_OAUTH_SECRET or os.getenv("ALLY_OAUTH_SECRET") or ""
    
    print("=" * 5 + "Saving credentials to .env (DO NOT SHARE THIS FILE!)" + "=" * 5)
    variables = dumper.dump(prefixes=["RSA_"])
      
    with open(".env", 'w') as f:  
        for env_name, env_value in variables.items():
            f.write('{0}={1}\n'.format(env_name, env_value))

    print("Credentials saved to .env")    

def setupWebull(account=1):
    # Get webull information
    WB1_USERNAME = input(f"Webull Account #{account} Username (email/phone): ")
    WB1_PASSWORD = input(f"Webull Account #{account} Password: ")
    WB1_TRADE_TOKEN = input(f"Webull Account #{account} Trade Token (6 digit trading code): ")
    WB1_QUESTION = ""
    WB1_QUESTION_ID = ""

    WB1_ACCESS_TOKEN = os.environ.get(f"WB{account}_ACCESS_TOKEN")
    WB1_REFRESH_TOKEN = os.environ.get(f"WB{account}_REFRESH_TOKEN")
    WB1_TOKEN_EXPIRATION = os.environ.get(f"WB{account}_TOKEN_EXPIRATION")
    WB1_UUID = os.environ.get(f"WB{account}_UUID")

    if WB1_USERNAME:
        wb = webull()
        data = wb.get_security(WB1_USERNAME) #get your security question.
        wb.get_mfa(WB1_USERNAME) #mobile number should be okay as well.
        WB1_CODE = input("You will receive a verification code to your email / phone number. Please enter it now: ")
        WB1_QUESTION_ID = data[0]['questionId']
        WB1_QUESTION = data[0]['questionName']
        print("Webull requested an answer to the following security question: ")
        WB1_ANSWER = input(WB1_QUESTION + " ")
        wb.login(
            username=WB1_USERNAME,
            password=WB1_PASSWORD,
            device_name="RSA",
            mfa=WB1_CODE,
            question_id=WB1_QUESTION_ID,
            question_answer=WB1_ANSWER
        )

        WB1_UUID = wb._uuid
        WB1_ACCESS_TOKEN = wb._access_token
        WB1_REFRESH_TOKEN = wb._refresh_token
        WB1_TOKEN_EXPIRATION = wb._token_expire

    os.environ[f'RSA_WB{account}_ACCESS_TOKEN'] = WB1_ACCESS_TOKEN or ""
    os.environ[f'RSA_WB{account}_REFRESH_TOKEN'] = WB1_REFRESH_TOKEN or ""
    os.environ[f'RSA_WB{account}_TOKEN_EXPIRATION'] = WB1_TOKEN_EXPIRATION or ""
    os.environ[f'RSA_WB{account}_UUID'] = WB1_UUID or ""
    os.environ[f'RSA_WB{account}_TRADE_TOKEN'] = WB1_TRADE_TOKEN or os.getenv(f"WB{account}_TRADE_TOKEN") or ""
