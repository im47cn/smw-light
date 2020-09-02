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


def read_data(file):
    try:
        df = pd.read_csv(file, header=None, nrows=8, names=['sector', 'data'])
        df.set_index('sector', inplace=True)
    except Exception as e:
        print(e)
        df = pd.DataFrame()
    return df


def write_data(df2, data_type):
    grp2 = df2.groupby('sector')[data_type].apply(
        lambda x: ','.join(x))
    df_ma = pd.DataFrame(grp2)
    # df_ma.reset_index(inplace=True)
    df_ma.columns = ['data']
    print('df_ma:========\n%s' % df_ma)

    filename = data_type+'.csv'
    df_ma_csv = read_data(filename)
    print('df_ma_csv:\n%s' % df_ma_csv)
    if not df_ma_csv.empty:
        df_ma = df_ma.append(df_ma_csv, sort=True)
    print('merged:\n%s' % df_ma)
    df_ma.to_csv(filename, sep=',', header=0, float_format='%.2f')


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

            # .str.split(',', expand=True)
            df = pd.DataFrame(jdata['data'])['d']
            # print(df)

            df1 = pd.DataFrame(df.dropna().values.tolist(), columns=[
                               'sector', 'industry', 'code', 'name', 'RecommendMA', 'close', 'ema5', 'sma5', 'ema10', 'sma10', 'ema20', 'sma20'])
            df1.reset_index()

            df1['ma5'] = df1.apply(lambda x: x['close'] > x['sma5'], axis=1)
            df1['ma10'] = df1.apply(lambda x: x['close'] > x['sma10'], axis=1)
            df1['ma20'] = df1.apply(lambda x: x['close'] > x['sma20'], axis=1)
            # print(df1)

            df1.drop(['industry', 'code', 'name', 'RecommendMA', 'close', 'ema5',
                      'sma5', 'ema10', 'sma10', 'ema20', 'sma20'], axis=1, inplace=True)
            df1.dropna(inplace=True)

            grp1 = df1.sort_values(by='sector').groupby('sector')
            # print(grp1)

            def add_prop(group):
                # print(group)
                count = group['ma5'].count()
                group['ma5'] = (group['ma5'].sum()*10000 /
                                count).astype(int).astype(str)
                group['ma10'] = (group['ma10'].sum()*10000 /
                                 count).astype(int).astype(str)
                group['ma20'] = (group['ma20'].sum()*10000 /
                                 count).astype(int).astype(str)
                return group
            df2 = grp1.apply(add_prop)
            df2.drop_duplicates('sector', keep='first',
                                inplace=True)
            df2['sector'] = datetime.now().strftime('%Y%m%d%H%M')

            write_data(df2, 'ma5')
            write_data(df2, 'ma10')
            write_data(df2, 'ma20')
        else:
            print('[INFO]: 失败原因: %s' % (jdata.get('msg')))


'''run'''
if __name__ == '__main__':
    url = os.environ["SCAN_URL"]
    data = os.environ["SCAN_PARAM"]
    sign_in = get(url=url, data=data)
    sign_in.run()
