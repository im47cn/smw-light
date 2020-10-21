# -*-coding=utf-8-*-
import os
import re
import datetime
from datetime import datetime
import requests
import pandas as pd
from pandas import Series
import csv

pd.options.display.float_format = '{:,.2f}'.format


def write_data(df2, data_type):
    date = datetime.now().strftime('%Y%m%d')
    filename = "data/bb_long/"+data_type+'_'+date+'.csv'
    df2.to_csv(filename, sep=',', mode='a', index=0, header=0, float_format='%.2f')


class get():
    def __init__(self, url, data, **kwargs):
        self.url = url
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        self.data = data

    '''外部调用'''

    def run(self):
        # 签到接口
        res = requests.post(
            url=self.url, headers=self.headers,  data=self.data)
        jdata = res.json()
        if res.status_code == 200:
            # print('[INFO]: data: %s' % (jdata))
            # print('jdata type: %s' % (type(jdata)))
            print('keys: %s' % (jdata.keys()))
            print('fetch %s items' % (jdata['totalCount']))

            df = pd.DataFrame(jdata['data'])['d']
            df1 = pd.DataFrame(df.dropna().values.tolist(), columns=[
                               'sector', 'industry', 'name', 'description', 'RecommendMA', 'close', 'ema20', 'close.1', 'ema20.1', 'BB.upper', 'sma50', 'sma50.1', 'sma100', 'sma100.1', 'sma200', 'sma200.1', 'CCI20'])
            # df1.reset_index()
            # print(df1)

            # 趋势过滤
            # df1['trend'] = df1.apply(lambda x: x['close'] > x['sma50'] and x['sma50'] > x['sma100'] and x['sma100'] > x['sma200'], axis=1)
            df1['trend'] = df1.apply(lambda x: x['sma50'] >= x['sma50.1'], axis=1)
            df1.drop(df1[~df1.trend].index, inplace=True)
            df1.drop(['trend'], axis=1, inplace=True)
            # print(df1)

            # 买入区间
            if df1.empty:
                return
            
            df1['buy_line'] = df1.apply(lambda x: x['ema20'] + (x['BB.upper'] - x['ema20'])/4, axis=1)
            df1['prepare_zone'] = df1.apply(lambda x: x['close'] >= x['ema20'] and x['close'] <= x['buy_line'], axis=1)
            df1.drop(df1[~df1.prepare_zone].index, inplace=True)
            df1.drop(['prepare_zone'], axis=1, inplace=True)
            # print(df1)

            # df1['prepare_zone2'] = df1.apply(lambda x: (x['buy_line'] - x['close.1']) > (x['buy_line'] - x['close']) and (x['close.1'] - x['ema20']) < (x['close'] - x['ema20']), axis=1)
            # df1.drop(df1[~df1.prepare_zone2].index, inplace=True)
            # df1.drop(['prepare_zone2'], axis=1, inplace=True)
            # print(df1)

            if df1.empty:
                return

            df1.drop(['RecommendMA', 'close.1', 'ema20.1', 'sma50.1'], axis=1, inplace=True)
            
            df1['reward_rate'] = df1.apply(lambda x: (x['BB.upper'] - x['close'])/(x['close'] - x['ema20']), axis=1)
            df1.sort_values(by='reward_rate', ascending=False, inplace=True)
            print(df1)

            # df1.dropna(inplace=True)
            # print(df1)

            write_data(df1, 'bb_long')
        else:
            print('[INFO]: 失败原因: %s' % (jdata.get('msg')))


'''run'''
# if __name__ == '__main__':
#     url = os.environ["SCAN_URL"]
#     data = os.environ["BB_LONG_PARAM"]
#     sign_in = get(url=url, data=data)
#     sign_in.run()




# curl 'https://scanner.tradingview.com/china/scan' \
# -X 'POST' \
# -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
# --data '{"filter":[{"left":"name","operation":"nempty"},{"left":"EMA20","operation":"eless","right":"close"},{"left":"SMA50","operation":"eless","right":"close"},{"left":"BB.upper","operation":"egreater","right":"close"},{"left":"basic_eps_net_income","operation":"egreater","right":0.3}],"options":{"active_symbols_only":true,"lang":"zh"},"symbols":{"query":{"types":[]},"tickers":[]},"columns":["sector","industry","Recommend.MA","close","EMA20","BB.upper","SMA50","CCI20"],"sort":{"sortBy":"name","sortOrder":"asc"},"range":[0,4000]}'

'''run'''
if __name__ == '__main__':
    url = 'https://scanner.tradingview.com/china/scan'

    # 超绩投资客
    data = '{"filter":[{"left":"industry","operation":"nempty"},{"left":"type","operation":"equal","right":"stock"},{"left":"subtype","operation":"equal","right":"common"},{"left":"sector","operation":"in_range","right":["Commercial Services","Communications","Consumer Durables","Consumer Non-Durables","Consumer Services","Distribution Services","Electronic Technology","Energy Minerals","Finance","Health Services","Health Technology","Industrial Services","Non-Energy Minerals","Process Industries","Producer Manufacturing","Retail Trade","Technology Services","Transportation"]},{"left":"market_cap_basic","operation":"in_range","right":[1000000000,200000000000]},{"left":"volume","operation":"eless","right":10000000},{"left":"average_volume_10d_calc","operation":"in_range","right":[50000,20000000]},{"left":"average_volume_30d_calc","operation":"egreater","right":50000},{"left":"average_volume_60d_calc","operation":"egreater","right":50000},{"left":"average_volume_90d_calc","operation":"egreater","right":50000},{"left":"close","operation":"greater","right":10},{"left":"earnings_per_share_basic_ttm","operation":"greater","right":0.5},{"left":"SMA50","operation":"less","right":"close"},{"left":"SMA100","operation":"less","right":"SMA50"},{"left":"SMA200","operation":"less","right":"SMA100"}],"options":{"active_symbols_only":true,"lang":"zh"},"symbols":{"query":{"types":[]},"tickers":[]},"columns":["sector","industry","name","description","Recommend.MA","close","EMA20","close|1","EMA20|1","BB.upper","SMA50","SMA50|1","SMA100","SMA100|1","SMA200","SMA200|1","CCI20"],"sort":{"sortBy":"industry","sortOrder":"asc"},"range":[0,3500]}'
    sign_in = get(url=url, data=data)
    sign_in.run()