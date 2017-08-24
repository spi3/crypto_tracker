import sqlite3
import re
import urllib.request
from urllib.error import HTTPError
import json

conn = sqlite3.connect('.crypto.db')
db = conn.cursor()

track_command = re.compile('Track|T',re.I)
untrack_command = re.compile('Untrack|stoptracking',re.I)
new_command = re.compile('New|N',re.I)
list_command = re.compile('ls|list|l',re.I)
remove_command = re.compile('remove|delete|r',re.I)
clear_command = re.compile('Clear|C',re.I)
exit_command = re.compile('Exit',re.I)
url_pattern = 'https://api.coinmarketcap.com/v1/ticker/{0}/'

#Validate the name of the coin based on coins avaliable on coinmarketcap
def validate_coin(coinName):
    api_url = 'https://api.coinmarketcap.com/v1/ticker/'
    with urllib.request.urlopen(api_url) as url:
        data = json.loads(url.read().decode())
        for d in data:
            coin = d['id']
            if coin == coinName:
                return True
        return False

while True:
    command = input('Enter command(Track,Untrack,New,Remove,List,Clear,Exit): ')
    if track_command.match(command):
        coinName = input('Please enter the name of the coin to track: ')
        if not validate_coin(coinName):
            print('Invalid coin.')
            continue
        coinUrl = url_pattern.format(coinName)
        db.execute('INSERT INTO tracked_coins (coin,api_url) VALUES (?,?)',(coinName,coinUrl))
        conn.commit()
    elif new_command.match(command):
        coinName = input('Enter coin name: ')
        if not validate_coin(coinName):
            print('Invalid coin. Please enter a valid cryptocurrency.')
            continue
        amount = input('Enter purchase amount: ')
        purchasePrice = input('Enter purchase price: ')
        currency = input('Enter currency puchased with(USD,btc): ')
        if not validate_coin(currency):
            if currency.lower() != 'usd':
                print('Invalid Currency. Please enter a valid cryptocurrency or USD')
                continue
        db.execute('INSERT INTO purchases (coin, amount, purchase_price, purchased_with) VALUES (?,?,?,?)',(coinName,amount,purchasePrice,currency))
        conn.commit()
    elif untrack_command.match(command):
        coinName = input('Enter coin name: ')
        if len(db.execute('SELECT * FROM purchases WHERE coin=?',(coinName,)).fetchall()):
            print('Cannot stop tracking {0}. Remove holdings before un-tracking.'.format(coinName))
            continue
        db.execute('DELETE FROM tracked_coins WHERE coin=?',(coinName,))
        conn.commit()
    elif list_command.match(command):
        entries = db.execute('SELECT * FROM purchases').fetchall()
        for entry in entries:
            print(entry)
    elif remove_command.match(command):
        transaction_id = input('Enter transaction id: ')
        db.execute('DELETE FROM purchases WHERE entry_id=?',(transaction_id,))
        conn.commit()
    elif clear_command.match(command):
        print("\033c")
    elif exit_command.match(command):
        break
    else:
        print('Invalid Command. Valid Commands: Track, Buy(B), Trade, Sell(S)')
