

import pandas as pd
from datetime import timezone
from datetime import datetime
import numpy as np
import altair as alt
import streamlit.components.v1 as components
from PIL import Image
from nomics import Nomics
import time
import requests



def smart_num(n):

    """for printing out large numbers. Anything above 100k will be put into units.
    1500000 will become 1.5M, and then billion and then trillion etc etc etc"""

    n = float(n)
    ab = abs(n)
    if ab<1000000:
        n = round(n,2)
        return '{:,}'.format(n)

    # millions i think
    if ab<1000000000:
        z = n/1000000
        z = round(z,2)
        return str(z)+"M"

    if ab < 10**12:
        z = n/(10**9)
        z = round(z,2)
        return str(z)+"B"

    z = n / (10**12)
    z = round(z,2)
    return str(z)+"T"



def get_sumarry_df():

    key = "266dbf914fd18fad344fcf6e0937362695777573"
    nomics = Nomics(key)
    currencies_name = ['BTC', 'ETH', 'BNB', 'USDT', 'SOL', 'ADA', 'XRP', 'USDC', 'DOT', 'DOGE']
    currencies  = nomics.Currencies.get_currencies(ids = 'BTC, ETH, BNB, USDT, SOL, ADA, XRP, USDC, DOT, DOGE')
    currencies = pd.DataFrame(currencies)


    currencies_name = ['BTC', 'ETH', 'BNB', 'USDT', 'SOL', 'ADA', 'XRP', 'USDC', 'DOT', 'DOGE']
    price_change = []
    market_cap = []
    market_cap_change = []
    volume = []
    volume_change = []

    for i in currencies_name:
        df = currencies[currencies['symbol']==i]
        val1 = smart_num(df['price'].iloc[0])
        val2 = smart_num(df['1d'].iloc[0]['price_change'])
        price_change.append(val2)
        val3 = smart_num(df['market_cap'].iloc[0])
        market_cap.append(val3)
        val4 = smart_num(df['1d'].iloc[0]['market_cap_change'])
        val5 = smart_num(df['1d'].iloc[0]['volume'])
        val6 =  smart_num(df['1d'].iloc[0]['volume_change'])
        market_cap_change.append(val4)

        volume.append(val5)
        volume_change.append(val6)
    sample = pd.DataFrame()
    sample['Coin'] = currencies_name
    sample['Price'] = currencies['price']
    sample["Price Change"] = price_change
    sample['Market Cap'] = market_cap
    sample['Market Cap Change (1d)'] = market_cap_change
    sample["Volume"] = volume
    sample['Volume Change'] = volume_change

    return sample
