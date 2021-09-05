import time
from threading import Thread
from statistics import mean
import requests
from luno_python.client import Client

from config import *
from uwsgidecorators import *
import uwsgi

from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

avg_min = 30
hash_rates = [0 for x in range(avg_min)]
daily_btc_profits = [0 for x in range(avg_min)]
btc_price = [0 for x in range(avg_min)]

info = {}


def get_btc_price():
    luno_api = Client(api_key_id=luno_key_id, api_key_secret=luno_key_secret)
    xbt_zar = float(luno_api.get_ticker(pair='XBTZAR')['last_trade'])
    return xbt_zar

def get_nh_info():

    return info


@timer(60)
def update_info_worker(*args):
    global info
    global hash_rates
    nh_info = requests.get(f"https://api2.nicehash.com/main/api/v2/mining/external/{nh_btc_addr}/rigs/activeWorkers").json()
    workers = len(nh_info['workers'])

    cur_speed = 0
    for worker in nh_info['workers']:
        cur_speed += worker['speedAccepted']

    hash_rates.pop(0)
    hash_rates.append(cur_speed)
    avg_hash = mean(hash_rates)

    cur_profit_btc_day = 0
    for worker in nh_info['workers']:
        cur_profit_btc_day += worker['profitability']

    daily_btc_profits.pop(0)
    daily_btc_profits.append(cur_profit_btc_day)
    avg_profit_btc_day = mean(daily_btc_profits)

    btc_price.pop(0)
    btc_price.append(get_btc_price())
    avg_btc_price = mean(btc_price)



    profit_zar_day = avg_profit_btc_day * avg_btc_price

    profit_zar_month = profit_zar_day * 30.41

    info = {
        'speed': f'{avg_hash:.2f}',
        'workers': workers,
        'profit_day': f'{profit_zar_day:.0f}',
        'profit_month': f'{profit_zar_month:.0f}',
        'btc_price': avg_btc_price,
    }
    print(f"{hash_rates=}\n{daily_btc_profits=}\n{btc_price=}\n{info=}\n \n")

update_info_worker()




@app.route('/')
def home():
    return render_template('index.html', info=info)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

