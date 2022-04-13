import requests
import time
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

#setup environment file
env_file = '.env'
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
path = ROOT_DIR + '/' + env_file
dotenv_path = Path(path)
if not os.path.exists(path):
    print('NO ENV FILE FOUND')
    key = input("Enter your API key:")
    portfolio = input("Enter your stock symbols seperated by commas: ")
    SYMBOLS = portfolio.split(',')
    API_KEY = f'{key}'
    with open('.env', 'w') as f:
        f.write(f'API_KEY="{API_KEY}"\nSYMBOLS="{SYMBOLS}"')

#load env file
load_dotenv(dotenv_path=dotenv_path)
API_KEY = os.getenv('API_KEY')
SYMBOLS = json.loads(os.getenv('SYMBOLS'))


class Quote:
    def __init__(self, data):
        self.symbol = data['01. symbol']
        self.high = data['03. high']
        self.low = data['04. low']
        self.open = data['02. open']
        self.price = data['05. price']
        self.volume = data['06. volume']
        self.change = data['09. change']
        self.pct_change = data['10. change percent']
        self.raw_data = data

    def __str__(self):
        return f"{self.symbol} - Open: {self.open}, High: {self.high}, Low: {self.low}, Price: {self.price}, Volume: {self.volume}, Change: {self.change}, Change %: {self.pct_change}"

    def json(self):
        print(self.raw_data)
        pass

    def calculate_daily_change(self):
        change = float(self.price) - float(self.open)
        return str(round(change, 4))

    def calculate_daily_change_percent(self):
        change = float(self.price) - float(self.open)
        open = float(self.open)
        pct = change/open * 100
        return str(round(pct, 4))

    def report(self):
        return f'''
        {self.symbol} | ${self.price}
        Open: ${self.open}
        Last Price Change: {self.change} | {self.pct_change}
        Price Change Since Open: {self.calculate_daily_change()} | {self.calculate_daily_change_percent()}%
        Range: ${self.low} -> ${self.high}
        Volume: {self.volume} trades.
        '''

def build_request_url(function, symbol):
    return f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={API_KEY}'

def get_stock_quote(stock_symbol):
    function = "GLOBAL_QUOTE"
    url = build_request_url(function, stock_symbol)
    r = requests.get(url)
    try:
        if r.json()['Global Quote']:
            quote = Quote(r.json()['Global Quote'])
        else:
            quote = f"Could Not Get Quote for {stock_symbol}."
    except KeyError:
        quote = r.text
    return quote

def main():
    keep_running = True
    while(keep_running):
        inp = input("Enter a stock symbol, type 'report' to generate a portfolio report or type 'quit' to quit: ")
        if inp.lower() == 'quit':
            keep_running = False
            continue
        elif inp.lower() == 'report':
            symbols =  SYMBOLS
            with open('report.txt', 'w') as file:
                file.write(f'Report for {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            for symbol in symbols:
                quote = get_stock_quote(symbol)
                print(quote.report())
                with open('report.txt', 'a') as file:
                    file.write(quote.report() + '\n')
                time.sleep(12) # using this api for free you can only make 5 calls/min
        else:
            quote = get_stock_quote(inp)
            print(quote.report())

if __name__ == "__main__":
    main()


#function = "TIME_SERIES_MONTHLY"




