import sqlite3
import json
import urllib.request
from urllib.error import HTTPError
import threading
import re
import time
import os
import math


#init database
conn = sqlite3.connect('.crypto.db')
db = conn.cursor()
db.execute('CREATE TABLE IF NOT EXISTS purchases (entry_id INTEGER PRIMARY KEY AUTOINCREMENT, coin TEXT, amount REAL, purchase_price REAL, purchased_with TEXT)') 
db.execute('CREATE TABLE IF NOT EXISTS tracked_coins (coin TEXT PRIMARY KEY, api_url TEXT)') 
conn.commit()
       
coin_data = {}
while True:
    tracked_coins = db.execute('SELECT * FROM tracked_coins').fetchall()
    transactions = db.execute('SELECT coin,amount,purchase_price,purchased_with FROM purchases').fetchall()
    holdings = {}
    total_value = 0
    total_spent = 0

    #Iterate through all the tracked coins and fetch their api data
    for coin in tracked_coins:
        coin_url = coin[1]
        try:
            with urllib.request.urlopen(coin_url) as url:
                data = json.loads(url.read().decode())[0]
                coin_data[data['id']] = data
        except urllib.error.HTTPError:
            pass
    print("\033c") #clear the contents of the terminal
    for coin in coin_data:
        print('Current price for {0}: ${1}'.format(coin,coin_data[coin]['price_usd']))
        
    
    #Iterate through all purchases and accumulate totals
    for transaction in transactions:
        coin = transaction[0]
        amount = transaction[1]
        purchase_price = transaction[2]
        purchased_with = transaction[3]
        
        #Add to purchased coin
        if coin not in holdings:
            holdings[coin] = 0.0
        holdings[coin] = holdings[coin] + amount

        #Subtract from coin used to purchase
        if purchased_with not in holdings:
            holdings[purchased_with] = 0.0
        holdings[purchased_with] = holdings[purchased_with] - (purchase_price * amount)
    
    #Display current holdings
    for coin in holdings:
        print('{0}: {1}'.format(coin,holdings[coin]))
        if coin.lower() == 'usd':
            total_spent = math.fabs(holdings[coin])
        else:
            coin_amount = float(holdings[coin])
            coin_price = float(coin_data[coin]['price_usd'])
            total_value = total_value + (coin_amount * coin_price)
    
    net_profit = total_value - total_spent
    output = "Total spent: ${0} ----- Total Value: ${1} ----- Net Profit: ${2}".format(total_spent,total_value,net_profit)
    output_length = len(output)
    print('-'*len(output))   
    print(output)
    print('-'*len(output))   
    time.sleep(30)
