
import datetime
import requests
import pandas as pd

from logger.exchange_logger import ExchangeLogger

stats_host = 'https://stats.permaswap.network'
router_host = 'https://router.permaswap.network'

logger = ExchangeLogger("ps_everpay_utils")

symbol_to_tag = {
    'ar': 'arweave,ethereum-ar-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA,0x4fadc7a98f2dc96510e42dd1a74141eeae0c1543',
    'usdc': 'ethereum-usdc-0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
    'usdt': 'ethereum-usdt-0xdac17f958d2ee523a2206206994597c13d831ec7',
    'eth': 'ethereum-eth-0x0000000000000000000000000000000000000000',
    'ardrive': 'arweave-ardrive--8A6RexFkpfWwuyVO98wzSFZh0d6VJuI-buTJvlwOJQ',
    'trunk': 'aostest-trunk-OT9qTE2467gcozb2g8R6D6N3nQS94ENcaAIJfUzHCww',
    '0rbt': 'aostest-0rbt-BUhZLMwQ6yZHguLtJYA5lLUa9LQzLXMXRfaq9FVcPJc',
    'Halo':'psntest-halo-0x0000000000000000000000000000000000000000',
    'BP': 'aostest-bp-_HbnZH5blAZH0CNT1k_dpRrGXWCzBg34hjMUkoDrXr0'
}

tag_to_symbol = {value: key for key, value in symbol_to_tag.items()}

def _get_one_page_orders(url:str):
    data = requests.get(url).json()
    return data

def get_orders(logger: ExchangeLogger, end: datetime.datetime, start: datetime.datetime ='', duration: int=30):
    orders = []
    if start == '':
        start = end - datetime.timedelta(days=duration)
    for page in range(1, 50000):
        url = '%s/orders?start=%s&end=%s&count=200&page=%i'%(router_host, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'), page)
        try:
            data = _get_one_page_orders(url)
        except:
            logger.error('get_orders failed: %s'%url)
            continue

        orders.extend(data['orders'])

        # no more pages
        if len(data['orders']) < 200:
            break

    return orders

def get_volume(order, order_ref):
    try:
        token_in = tag_to_symbol[order['token_in_tag']]
        token_out = tag_to_symbol[order['token_out_tag']]
    except:
        return -1
    
    amount_in = float(order['token_in_amount'])
    amount_out = float(order['token_out_amount'])
    
    try:
        token_in_ref = tag_to_symbol[order_ref['token_in_tag']]
        token_out_ref = tag_to_symbol[order_ref['token_out_tag']]
    except:
        return -1
    
    amount_in_ref = float(order_ref['token_in_amount'])
    amount_out_ref = float(order_ref['token_out_amount'])
    
    if token_in == token_in_ref and token_out_ref in ['usdc', 'usdt']:
        price_token_in = amount_out_ref/amount_in_ref
        volume = price_token_in * amount_in
        return volume
    
    if token_out == token_in_ref and token_out_ref in ['usdc', 'usdt']:
        price_token_out = amount_out_ref/amount_in_ref
        volume = price_token_out * amount_out
        return volume
           
                
    if token_in == token_out_ref and token_in_ref in ['usdc', 'usdt']:
        price_token_in = amount_in_ref/amount_out_ref
        volume = price_token_in * amount_in
        return volume
       
    if token_out == token_out_ref and token_in_ref in ['usdc', 'usdt']:
        price_token_out = amount_in_ref/amount_out_ref
        volume = price_token_out * amount_out
        return volume
    
    return -1
            
def process_orders(orders):
    new_orders = []
    n = len(orders)
    
    for index, order in enumerate(orders):
        try:
            token_in = tag_to_symbol[order['token_in_tag']]
            token_out = tag_to_symbol[order['token_out_tag']]
        except:
            continue
        amount_in = float(order['token_in_amount'])
        amount_out = float(order['token_out_amount'])
        volume = 0

        new_order = {
            'time': order['timestamp'],
            'address': order['address'],
            'ever_hash': order['ever_hash'],
            'token_in': token_in,
            'token_out': token_out,
            'amount_in': amount_in,
            'amount_out': amount_out,
        }
        
        if token_in in ['usdc', 'usdt']:
            volume = float(order["token_in_amount"])
            new_order['volume'] = volume
            new_orders.append(new_order)
            continue

        if token_out in ['usdc', 'usdt']:
            volume = float(order["token_out_amount"])
            new_order['volume'] = volume
            new_orders.append(new_order)
            continue
            
        for i in range(100):
            if index + i < n - 1:
                order_next = orders[index + i]
                try:
                    volume = get_volume(order, order_next)
                except Exception as e:
                    print(e)
                    continue
                if volume > 0:
                    new_order['volume'] = volume
                    new_orders.append(new_order)
                    break
                
            if index - i > 0:
                order_prev = orders[index - i]
                try:
                    volume = get_volume(order, order_prev)
                except Exception as e:
                    print(e)
                    continue
                 
                if volume > 0:
                    new_order['volume'] = volume
                    new_orders.append(new_order)
                    break
    
    return new_orders

def get_kline(orders, token, period):
    df = pd.DataFrame(orders)
    print(df.head())
    df.set_index('time', inplace=True)
    df.index = pd.to_datetime(df.index, unit='ms')

    df1 = df[(df['token_in'] == token)].copy()
    df1.loc[:, 'price'] = df1['volume'] / df1['amount_in']
    df2 = df[(df['token_out'] == token)].copy()
    df2.loc[:, 'price'] = df2['volume'] / df2['amount_out']

    df3 = pd.concat([df1,df2])
    df4 = df3.resample(rule=period).agg(
        {'price': ['first', 'max', 'min', 'last'],     
        'volume': 'sum'
    })

    prev = df4['price']['last'].shift(1)
    df4['price', 'last'] = df4['price']['last'].fillna(prev)
    df4['price', 'min'] = df4['price']['min'].fillna(prev)
    df4['price', 'max'] = df4['price']['max'].fillna(prev)
    df4['price', 'first'] = df4['price']['first'].fillna(prev)
    df4 = df4.fillna(method='ffill')

    return df4

