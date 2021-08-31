import requests
import nicehash
from luno_python.client import Client

from nh_config import *

from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

nh_api = nicehash.private_api(
    "https://api2.nicehash.com", nh_org_id, nh_api_key_code, nh_api_secret_key_code
)

def btc_to_zar(btc):
    luno_api = Client(api_key_id=luno_key_id, api_key_secret=luno_key_secret)
    xbt_zar = float(luno_api.get_ticker(pair='XBTZAR')['bid'])
    return xbt_zar * btc

def get_nh_info():
    nh_info = requests.get(f"https://api2.nicehash.com/main/api/v2/mining/external/{nh_btc_addr}/rigs/activeWorkers").json()
    workers = len(nh_info['workers'])
    speed = 0
    for worker in nh_info['workers']:
        speed += worker['speedAccepted']

    profit_btc_day = 0
    for worker in nh_info['workers']:
        profit_btc_day += worker['profitability']
    profit_zar_day = btc_to_zar(profit_btc_day)

    profit_zar_month = profit_zar_day * 30.41

    info = {
        'speed': f'{speed:.2f}',
        'workers': workers,
        'profit_day': f'{profit_zar_day:.0f}',
        'profit_month': f'{profit_zar_month:.0f}',
    }

    return info


@app.route('/')
def info():
    info = get_nh_info()

    return render_template('index.html', info=info)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
