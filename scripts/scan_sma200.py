# -*-coding=utf-8-*-
import os
import datetime
from datetime import datetime
import requests
import pandas as pd
import logging

pd.options.display.float_format = '{:,.2f}'.format


def read_data(file):
    try:
        df = pd.read_csv(file, header=None, nrows=300, names=['sector', 'data'])
        df.set_index('sector', inplace=True)
    except Exception as e:
        print(e)
        df = pd.DataFrame()
    return df


def write_data(df, data_type='sma200'):
    date = datetime.now().strftime('%Y%m%d')
    filename = 'data/' + data_type + '/' + date + '.csv'
    df.to_csv(filename, sep=',', header=1, float_format='%.2f')


class SMA200():
    def __init__(self, url, data, **kwargs):
        self.url = url
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        self.data = data

    '''外部调用'''

    def run(self, period='1W'):
        # 签到接口
        res = requests.post(
            url=self.url, headers=self.headers, data=self.data)
        if res.status_code == 200:
            jdata = res.json()
            logging.info('[INFO]: data: %s' % (jdata))
            logging.info('jdata type: %s' % (type(jdata)))
            logging.info('keys: %s' % (jdata.keys()))
            logging.info('fetch %s items' % (jdata['totalCount']))

            # .str.split(',', expand=True)
            df = pd.DataFrame(jdata['data'])['d']
            # logging.info(df)

            df1 = pd.DataFrame(
                df.dropna().values.tolist(),
                columns=[
                    'sector',
                    'industry',
                    'code',
                    'name',
                    'RecommendMA',
                    'close',
                    'sma200',
                    'sma200_5',
                    'sma200_15',
                    'sma200_60',
                    'sma200_240',
                    'sma200_1w',
                    'sma200_1m',
                    'ema5',
                    'ema10'])
            df1.reset_index()

            # 排除200开头的
            df1.drop(df1[~df1.code.str.startswith('200')].index, inplace=True)

            # 上涨趋势
            df1['up_trend'] = df1.apply(lambda x: x['close'] >= x['sma200'], axis=1)
            df1.drop(df1[~df1.up_trend].index, inplace=True)
            logging.info('up_trend:{}'.format(df1))

            # 突破形态
            df1['prepare_zone'] = df1.apply(lambda x: x['close'] >= x['sma200_240']
                                            and x['close'] >= x['sma200_60']
                                            and x['close'] >= x['sma200_15']
                                            and x['close'] >= x['sma200_5'], axis=1)
            df1.drop(df1[~df1.prepare_zone].index, inplace=True)
            logging.info('prepare_zone:{}'.format(df1))

            write_data(df1)
        else:
            logging.info('[INFO]: 失败原因: %s' % (res))


'''run'''
if __name__ == '__main__':
    url = os.environ["SCAN_URL"]
    data = os.environ["SCAN_SMA200_PARAM"]
    sign_in = SMA200(url=url, data=data)
    sign_in.run()
