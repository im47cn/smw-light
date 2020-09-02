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


def write_data(df2):
    date = datetime.now().strftime('%Y%m%d')
    filename = 'data/stochastic/'+date+'.csv'
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
            # print('keys: %s' % (jdata.keys()))
            print('fetch %s items' % (jdata['totalCount']))

            df = pd.DataFrame(jdata['data'])['d']
            df1 = pd.DataFrame(df.dropna().values.tolist(), columns=[
                               'sector', 'industry', 'name', 'description', 'close', 'close.1', 'ema20', 'ema20.1', 'BB.upper', 'sma50', 'sma50.1', 'sma100', 'sma100.1', 'sma200', 'sma200.1', 'Stoch.K', 'Stoch.D', 'Stoch.K.1', 'Stoch.D.1', 'CCI20'])
            # df1.reset_index()
            # print(df1)

            # 趋势极值
            #df1['aboveLine'] = df1.apply(lambda x: x['Stoch.K'] > 80, axis=1)
            #df1['belowLine'] = df1.apply(lambda x: x['Stoch.K'] < 20, axis=1)
            df1['crossUp'] = df1.apply(lambda x: x['Stoch.K.1'] < x['Stoch.D.1'] and x['Stoch.K.1'] < 20 and x['Stoch.K'] > x['Stoch.D'], axis=1)
            df1['crossDown'] = df1.apply(lambda x: x['Stoch.K.1'] > x['Stoch.D.1'] and x['Stoch.K.1'] > 80 and x['Stoch.K'] < x['Stoch.D'], axis=1)
            # df1.drop(df1[~df1.trend].index, inplace=True)
            # df1.drop(['trend'], axis=1, inplace=True)
            # print(df1)s

            # 买入区间
            # df1['buy_line'] = df1.apply(lambda x: x['ema20'] + (x['BB.upper'] - x['ema20'])/4, axis=1)
            # df1['prepare_zone'] = df1.apply(lambda x: x['close'] >= x['ema20'] and x['close'] <= x['buy_line'], axis=1)
            # df1.drop(df1[~df1.prepare_zone].index, inplace=True)
            # print(df1)

            # df1['prepare_zone2'] = df1.apply(lambda x: (x['buy_line'] - x['close.1']) > (x['buy_line'] - x['close']) and (x['close.1'] - x['ema20']) < (x['close'] - x['ema20']), axis=1)
            # df1.drop(df1[~df1.prepare_zone2].index, inplace=True)
            # df1.drop(['prepare_zone2'], axis=1, inplace=True)
            # print(df1)

            # df1.drop(['prepare_zone', 'close.1', 'ema20.1', 'sma50.1'], axis=1, inplace=True)

            df1['reward_rate'] = df1.apply(lambda x: (x['BB.upper'] - x['close'])/(x['close'] - x['ema20']), axis=1)
            df1.sort_values(by=['crossUp', 'reward_rate'], ascending=False, inplace=True)
            print(df1)

            # df1.dropna(inplace=True)
            # print(df1)

            df1.drop(df1[~df1.crossUp].index, inplace=True)
            if df1.empty:
                return
            write_data(df1)
        else:
            print('[INFO]: 失败原因: %s' % (jdata.get('msg')))


'''run'''
if __name__ == '__main__':
    url = os.environ["SCAN_URL"]
    data = os.environ["STOCHASTIC_PARAM"]
    sign_in = get(url=url, data=data)
    sign_in.run()




