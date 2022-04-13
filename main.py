#!/usr/bin/env python3

import requests
import time
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from termcolor import colored

# setup environment file
env_file = '.env'
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
path = ROOT_DIR + '/' + env_file
dotenv_path = Path(path)
if not os.path.exists(path):
    print('NO ENV FILE FOUND')
    key = input("Enter your API key:")
    portfolio = input("Enter your stock symbols seperated by commas: ")
    PORTFOLIO = portfolio.split(',')
    watchlist = input("Enter your stock symbols to watch: ")
    WATCHLIST = portfolio.split(',')
    API_KEY = f'{key}'
    with open('.env', 'w') as f:
        f.write(f'API_KEY="{API_KEY}"\nPORTFOLIO="{PORTFOLIO}"\nWATCHLIST="{WATCHLIST}"')

# load env file
load_dotenv(dotenv_path=dotenv_path)
API_KEY = os.getenv('API_KEY')
PORTFOLIO = json.loads(os.getenv('PORTFOLIO'))


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
        return f"{self.symbol} - Open: {self.open}, High: {self.high}, Low: {self.low}, Price: {self.price}, " \
               f"Volume: {self.volume}, Change: {self.change}, Change %: {self.pct_change}"

    def json(self):
        print(self.raw_data)
        pass

    def calculate_daily_change(self):
        change = float(self.price) - float(self.open)
        return str(round(change, 4))

    def calculate_daily_change_percent(self):
        change = float(self.price) - float(self.open)
        day_open = float(self.open)
        pct = change / day_open * 100
        return str(round(pct, 4))

    def report(self):
        return f'''
        {self.symbol} | ${self.price}
        Open: ${self.open}
        Price Change Since Open: {self.calculate_daily_change()} | {self.calculate_daily_change_percent()}%
        Last Price Change: {self.change} | {self.pct_change}
        Range: ${self.low} -> ${self.high}
        Volume: {self.volume} trades.
        '''

    def print_daily_change_in_price(self):
        if self.price > self.open:
            print(colored(f'{self.calculate_daily_change()} | {self.calculate_daily_change_percent()}%', 'green'))
        elif self.price < self.open:
            print(colored(f'{self.calculate_daily_change()} | {self.calculate_daily_change_percent()}%', 'red'))
        elif self.price == self.open:
            print(f'{self.calculate_daily_change()} | {self.calculate_daily_change_percent()}%')

    def print_stock_price(self):
        if self.price > self.open:
            print(colored(f'${self.price}', 'green'))
        elif self.price < self.open:
            print(colored(f'${self.price}', 'red'))
        elif self.price == self.open:
            print(f'${self.price}')

    def print_last_change(self):
        if float(self.change) > 0:
            print(colored(f'{self.change} | {self.pct_change}%', 'green'))
        elif float(self.change) < 0:
            print(colored(f'{self.change} | {self.pct_change}%', 'red'))
        elif float(self.change) == 0:
            print(f'{self.change} | {self.pct_change}%')

    def show_quote(self):
        print('---------------------------')
        print(f'{self.symbol} |  ',end="")
        self.print_stock_price()
        print('Last', end=" ")
        self.print_last_change()
        print('Day:',end=" ")
        self.print_daily_change_in_price()
        print('---------------------------')
        print(f'Open: ${self.open}')
        print(f'Range: ${self.low} -> ${self.high}')
        print(f'Volume: {self.volume} trades.')
        print('---------------------------')

def build_request_url(function, symbol):
    return f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={API_KEY}'

def print_company_name(symbol):
    url = build_request_url('OVERVIEW', symbol)
    r = requests.get(url)
    data = r.json()
    try:
        print('---------------------------')
        print(data['Name'])
        print(data['Industry'])
    except KeyError:
        print(data)


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
    while keep_running:
        inp = input("Enter a stock symbol or type help for more options:")
        if inp.lower() == 'help':
            print('''
            'report' to generate portfolio report
            'watchlist' to generate a watchlist report
            'quit' to quit
            ''')
        elif inp.lower() == 'quit':
            keep_running = False
            continue
        elif inp.lower() == 'report':
            symbols = PORTFOLIO
            with open('report.txt', 'w') as file:
                file.write(f'Report for {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            for symbol in symbols:
                quote = get_stock_quote(symbol)
                print(quote.report())
                with open('report.txt', 'a') as file:
                    file.write(quote.report() + '\n')
                time.sleep(12)  # using this api for free you can only make 5 calls/min
            print("Portfolio Report Completed")
        elif inp.lower() == 'watchlist':
            symbols = WATCHLIST
            with open('report.txt', 'w') as file:
                file.write(f'Report for {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            for symbol in symbols:
                quote = get_stock_quote(symbol)
                print(quote.report())
                with open('watchlist.txt', 'a') as file:
                    file.write(quote.report() + '\n')
                time.sleep(12)  # using this api for free you can only make 5 calls/min
            print("Watchlist Report Completed")
        else:
            quote = get_stock_quote(inp.upper())
            print_company_name(inp.upper())
            quote.show_quote()


if __name__ == "__main__":
    main()
