#!/usr/bin/python
# -*-coding=utf-8-*-
import os
import re
import time
import datetime
from datetime import datetime
from datetime import timedelta
import requests
import pandas as pd
from pandas import Series
import numpy as np
from requests.api import get
import tushare as ts
import queue
import threading
import logging
import matplotlib as mpl
import matplotlib.pyplot as plt
import mplfinance as mpfs
from matplotlib import ticker
from matplotlib.pylab import date2num
from mplfinance.original_flavor import candlestick_ochl

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(filename='my.log', level=logging.INFO, format=LOG_FORMAT)

# 解决mplfinance绘制输出中文乱码
plt.rcParams['font.sans-serif'] = ['Songti SC']
plt.rcParams['axes.unicode_minus'] = False
s = mpfs.make_mpf_style(base_mpf_style='yahoo', rc={
                        'font.family': 'Songti SC'})

debug = False
exitFlag = 0

# pd.set_option()就是pycharm输出控制显示的设置
pd.set_option('expand_frame_repr', False)  # True就是可以换行显示。设置成False的时候不允许换行
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.max_rows', 4)  # 显示所有行
pd.set_option('colheader_justify', 'centre')  # 显示居中
pd.options.display.float_format = '{:,.2f}'.format

date = datetime.now().strftime('%Y%m%d')
# filename = "data/vcp/"+date+".txt"
filename = date + ".txt"
f = open(filename, "a+", buffering=8096)

code_list = []


class VCP():
    def __init__(self, key, **kwargs):
        self.pro = ts.pro_api(key)
        self.queueLock = threading.Lock()
        self.workQueue = queue.Queue(5000)

    def get_stock_basic(self, ts_code=''):
        '''
        获取所有股票
        '''

        # 本地缓存
        file = 'stock_basic_' + filename
        if os.path.exists(file):
            df = pd.read_csv(file, index_col=0)
            if not None:
                logging.info("stock basic read form csv:\n{}".format(df))
                return df

        for _ in range(300):
            try:
                df = self.pro.stock_basic(ts_code=ts_code, exchange='', list_status='L')
                logging.info("stock basic read from remote:\n{}".format(df))

                # 添加交易所列
                # df.loc[df['ts_code'].str.startswith('3'), 'exchange'] = 'CY'
                # df.loc[df['ts_code'].str.startswith('688'), 'exchange'] = 'KC'
                # df.loc[df['ts_code'].str.startswith('60'), 'exchange'] = 'SH'
                # df.loc[df['ts_code'].str.startswith('0'), 'exchange'] = 'SZ'
            except Exception as e:
                # logging.info('抓取异常 get_stock_basic')
                # logging.info(e.args)
                time.sleep(15)
            else:
                df.to_csv(file)
                return df

        logging.info('抓取异常 get_stock_basic')
        return

    def get_daily_basic(self, ts_code='', trade_date=''):
        ''' 获取所有股票的每日指标
                turnover_rate   float   换手率（%）
                turnover_rate_f float   换手率（自由流通股）
                volume_ratio    float   量比
                pe  float   市盈率（总市值/净利润， 亏损的PE为空）
                pe_ttm  float   市盈率（TTM，亏损的PE为空）
                pb  float   市净率（总市值/净资产）
                ps  float   市销率
                ps_ttm  float   市销率（TTM）
                dv_ratio    float   股息率 （%）
                dv_ttm  float   股息率（TTM）（%）
                total_share float   总股本 （万股）
                float_share float   流通股本 （万股）
                free_share  float   自由流通股本 （万）
                total_mv    float   总市值 （万元）
                circ_mv float   流通市值（万元）
        '''
        # 本地缓存
        file = 'daily_basic_' + trade_date + '.csv'
        if os.path.exists(file):
            df = pd.read_csv(file, index_col=0)
            if not None:
                logging.info("daily basic read form csv:\n{}".format(df))
                return df

        for _ in range(300):
            try:
                df = self.pro.daily_basic(ts_code=ts_code, trade_date=trade_date)
                logging.info("daily basic read form remote:\n{}".format(df))
            except Exception as e:
                # logging.info('抓取异常 get_daily_basic')
                # logging.info(e.args)
                time.sleep(15)
            else:
                df.to_csv(file)
                return df

        logging.info('抓取异常 get_daily_basic')
        return

    def get_stock_daily(self, ts_code, start_date='', end_date='', adj='qfq'):
        # 获取指定股票的交易数据
        for _ in range(300):
            try:
                df = self.pro.daily(ts_code=ts_code,
                                    start_date=start_date, end_date=end_date, adj=adj)
                # if debug:
                #     logging.info("ts_code:{}, start_date:{}, end_date:{}, df: {}".format(
                #         ts_code, start_date, end_date, df))
            except Exception as e:
                # logging.info('抓取异常 get_stock_daily, ts_code:{}'.format(ts_code))
                # logging.info(e.args)
                time.sleep(30)
            else:
                return df

        logging.info('抓取异常 get_stock_daily, ts_code:{}'.format(ts_code))
        return

    def get_fina_indicator(self, ts_code, start_date=''):
        # 获取指定股票的财务指标数据
        for _ in range(300):
            try:
                df = self.pro.fina_indicator(ts_code=ts_code, start_date=start_date)
                # if debug:
                #     logging.info("ts_code:{}, df: {}".format(ts_code, df))
                # logging.info("ts_code:{}, start_date:{}, end_date:{}, df: {}".format(
                #     ts_code, start_date, end_date, df))
            except Exception as e:
                # logging.info('抓取异常 get_stock_daily, ts_code:{}'.format(ts_code))
                # logging.info(e.args)
                time.sleep(30)
            else:
                return df

        logging.info('抓取异常 get_fina_indicator, ts_code:{}'.format(ts_code))
        return

    def get_pro_bar(self, ts_code, start_date='', end_date='', freq='D', ma=[50, 150, 200], factors=[]):
        for _ in range(300):
            try:
                df = ts.pro_bar(
                    ts_code=ts_code,
                    start_date=start_date,
                    end_date=end_date,
                    adj='qfq',
                    freq=freq,
                    ma=ma,
                    factors=factors)
                # logging.info("df:{}".format(df))
            except Exception as e:
                # logging.info('抓取异常 get_pro_bar')
                # logging.info(e.args)
                time.sleep(30)
            else:
                return df

        logging.info('抓取异常 get_pro_bar, ts_code:{}'.format(ts_code))
        return

    def convert_date_to_int(self, dt):
        t = dt.year * 10000 + dt.month * 100 + dt.day
        # t *= 1000000
        return t

    def vcp_search(self, timeframe=260, volTf=50, baseLowerLimit=0.6, pivotLen=5, pivotLimit=0.1):
        df = self.get_stock_basic()

        # IPO Date Filter
        # 过滤掉 52 周内上市的股票
        st_count_before_filter = len(df)
        now = datetime.now()
        deadline = self.convert_date_to_int(now - timedelta(timeframe))
        df.list_date = df.list_date.replace('.', '').astype(int)
        df = df[(df.list_date < deadline)]
        logging.info("IPO Date Filter, before:{}, after:{}".format(
            st_count_before_filter, len(df)))
        # logging.info("df:\n{}\n".format(df))

        # Market Cap Filter
        # 过滤掉市值total_mv 小于 1e2 million（10000万） 和大于 1e4 million（10亿），范围待确认
        st_count_before_filter = len(df)
        trade_date = now.strftime('%Y%m%d')
        if now.hour < 15:
            trade_date = (now - timedelta(1)).strftime('%Y%m%d')
            logging.info("[FAIL] 我整的昨天的数据哈:{}".format(trade_date))
        daily_basic_df = self.get_daily_basic(trade_date=trade_date)
        daily_basic_df.drop(daily_basic_df[daily_basic_df.close < 10].index, inplace=True)
        daily_basic_df.drop(daily_basic_df[(daily_basic_df.total_mv > 100 *
                                            100) & (daily_basic_df.total_mv < 10000 * 100)].index, inplace=True)
        df = pd.merge(df, daily_basic_df, on=['ts_code'], how='inner')
        logging.info("Market Cap Filter, before:{}, after:{}".format(
            st_count_before_filter, len(df)))
        # logging.info("df:\n{}\n".format(df))

        # i = 0
        # for ts_code in df.ts_code:
        #         df = df.drop(df[(df.ts_code == ts_code)].index)

        # df = df[fina_indicator_df[(fina_indicator_df.q_roe > 17)].ts_code]
        # logging.info("ROE Filter, df:\n{}".format(
        #     fina_indicator_df[(fina_indicator_df.q_roe > 17)]))

        #     i = i+1
        #     if i > 10:
        #         break

        # logging.info("df:\n{}".format(df))
        # return

        # Sales QoQ

        # 创建线程池并填充队列
        threads = self.batch()
        self.queueLock.acquire()

        for idx, ts_code in enumerate(df['ts_code']):
            # if int(ts_code[0:6]) < 590:
            #     logging.info('skip ts_code:{}'.format(ts_code))
            #     continue
            self.workQueue.put(["self.vcp_analyse",
                                {"ts_code": ts_code,
                                 "timeframe": timeframe,
                                 "volTf": volTf,
                                 "baseLowerLimit": baseLowerLimit,
                                 "pivotLen": pivotLen,
                                 "pivotLimit": pivotLimit}])

            if idx % 120 == 100:
                self.queueLock.release()
                time.sleep(25)
                self.queueLock.acquire()

        self.queueLock.release()

        # 等待队列清空
        while not self.workQueue.empty():
            pass

        # 通知线程是时候退出
        global exitFlag
        exitFlag = 1

        # 等待所有线程完成
        for t in threads:
            t.join()
        logging.info("退出主线程")
        f.close()

    class myThread (threading.Thread):
        def __init__(self, that, threadID, name, q):
            threading.Thread.__init__(self)
            self.threadID = threadID
            self.name = name
            self.q = q
            self.that = that

        def run(self):
            logging.info("开启线程：" + self.name)
            self.that.process_data(self.name, self.q)
            logging.info("退出线程：" + self.name)

    def process_data(self, threadName, q):
        while not exitFlag:
            if not q.empty():
                self.queueLock.acquire()
                if not q.empty():
                    data = q.get()
                    # logging.info("data: {}".format(data))
                    target = data[0]
                    kwargs = data[1]
                    self.queueLock.release()
                    logging.info("%s processing %s, queue size: %s" %
                                 (threadName, target, q.qsize()))
                    eval(target)(**kwargs)
                else:
                    self.queueLock.release()
            # logging.info("%s waiting, queue size: %s" %
            #       (threadName, q.qsize()))

    # 创建新线程
    def batch(self, ):
        threadList = ["Thread-0", "Thread-1", "Thread-2", "Thread-3"]
        # threadList = ["Thread-0", "Thread-1", "Thread-2", "Thread-3", "Thread-4",
        #               "Thread-5", "Thread-6", "Thread-7", "Thread-8", "Thread-9"]
        threads = []
        threadID = 1
        for tName in threadList:
            thread = self.myThread(self, threadID, tName, self.workQueue)
            thread.start()
            threads.append(thread)
            threadID += 1
        return threads

    def calcSlope(self, src, len):
        sumX = 0.0
        sumY = 0.0
        sumXSqr = 0.0
        sumXY = 0.0
        for i in range(0, len - 1):
            val = src[i]
            per = i + 1.0
            sumX = sumX + per
            sumY = sumY + val
            sumXSqr = sumXSqr + per * per
            sumXY = sumXY + val * per
        slope = (len * sumXY - sumX * sumY) / (len * sumXSqr - sumX * sumX)
        average = sumY / len
        intercept = average - slope * sumX / len + slope
        return slope, average, intercept

    def vcp_analyse(
            self,
            ts_code,
            df=pd.DataFrame(),
            timeframe=252,
            volTf=50,
            baseLowerLimit=0.6,
            pivotLen=5,
            pivotLimit=0.1):
        now = datetime.now()
        if len(df) == 0:
            end_date = now.strftime('%Y%m%d')
            start_date = (now - timedelta(timeframe * 2)).strftime('%Y%m%d')

            df = self.get_pro_bar(ts_code, start_date, end_date)

        if df is None:
            logging.info("[FAIL] ts_code:{} is None".format(ts_code))
            return

        if df['close'][0] < 10:
            logging.error("[FAIL] ts_code:{} price lower then ¥10".format(ts_code))
            return

        # ROE Filter
        # TODO >17
        last_fina_date = (now - timedelta(180)).strftime('%Y%m%d')
        fina_indicator_df = self.get_fina_indicator(ts_code, last_fina_date)
        fina_indicator_df = fina_indicator_df.head(1)
        # logging.info("fina_indicator_df:{}\n".format(fina_indicator_df))

        if fina_indicator_df.q_roe[0] <= 5:
            # logging.info("[FAIL] ts_code:{} roe lower then 5".format(ts_code))
            return

        if len(df) > timeframe:
            df = df.head(timeframe)

        if not self.stage2(ts_code, df):
            return

        # 1.最新价格小于最高价，但跌幅不能太大
        close = df['close'][0]
        highest = df['close'].max()
        # lowest = df['close'].min()
        # logging.info("ts_code:{}, highest:{}, close:{}".format(ts_code, highest, close))

        nearHigh = close < highest and close > highest * baseLowerLimit
        if not nearHigh:
            logging.info("[FAIL] ts_code:{} is in stage2, not near w52Highest".format(ts_code))
            return

        # 2.平均交易量下降
        vma = df['vol'].sort_index(ascending=False).rolling(
            window=volTf).mean().tail(volTf).sort_index(ascending=True)
        # logging.info("ts_code:{}, vma:{}, close:{}".format(ts_code, vma, close))
        if vma.size < volTf:
            logging.warn("ts_code:{}, vma.size:{}, volTf:{}".format(
                ts_code, vma.size, volTf))
            return

        (volSlope, average, intercept) = self.calcSlope(vma, volTf)
        volDecreasing = volSlope < 0
        if not volDecreasing:
            logging.info(
                "[FAIL] ts_code:{} is in stage2, vol not decreasing, volSlope:{:0.2f}, average:{:0.2f}, intercept:{:0.2f}".format(
                    ts_code,
                    volSlope,
                    average,
                    intercept))
            return

        # 3.Pivot Quality
        pivotHighPrice = df['high'].head(pivotLen).max()
        pivotLowPrice = df['low'].head(pivotLen).min()
        pivotWidth = (pivotHighPrice - pivotLowPrice) / close
        pivotStartHP = df['high'][pivotLen - 1]
        isPivot = pivotWidth < pivotLimit and pivotHighPrice <= pivotStartHP * 1.05

        if not isPivot:
            logging.info(
                "[FAIL] ts_code:{} is in stage2, not isPivot, pivotWidth:{}, pivotHighPrice:{}, pivotStartHP:{}" .format(
                    ts_code,
                    pivotWidth,
                    pivotHighPrice,
                    pivotStartHP))
            return

        # 4.ensure volume is below avgrage
        volDryUp = True
        for i in range(0, pivotLen - 1):
            volDryUp = volDryUp and df['vol'][i] < vma[i]
            logging.info(
                "[FAIL] ts_code:{} volDryUp:{}, vol:{}, vma:{}".format(
                    ts_code, volDryUp, df['vol'][i], vma[i]))

        if not volDryUp:
            logging.info("[FAIL] ts_code:{} is in stage2, not volDryUp".format(ts_code))
            return

        f.write("{}\n".format(ts_code))
        logging.info("[SUCCESS] ts_code:{} is in stage2, vis volDryUp:{}".format(ts_code, volDryUp))

        code_list.append(ts_code)

        return volDryUp

    def stage2(
            self,
            ts_code,
            df=pd.DataFrame(),
            timeframe=252,
            volTf=50,
            baseLowerLimit=0.6,
            pivotLen=5,
            pivotLimit=0.1):
        if len(df) == 0:
            now = datetime.now()
            end_date = now.strftime('%Y%m%d')
            start_date = (now - timedelta(timeframe * 2)).strftime('%Y%m%d')

            df = self.get_pro_bar(ts_code, start_date, end_date)
            if len(df) > timeframe:
                df = df.head(timeframe)

        # 交易日期太短
        if len(df) < timeframe:
            logging.debug("[FAIL] ts_code:{} 交易日期太短, len:{}\n".format(ts_code, len(df)))
            return False

        close = df['close'][0]
        highestPrice = df['high'].head(timeframe).max()
        lowestPrice = df['low'].head(timeframe).min()
        w52wkHigh = close > 0.75 * highestPrice and close > lowestPrice * 1.30
        sma50 = df['ma50'][0]
        sma150 = df['ma150'][0]
        sma200 = df['ma200'][0]
        unwrappedSMA = close > sma50 and sma50 > sma150 and sma150 > sma200
        uptrend = sma200 > df['ma200'][21]
        stage2 = w52wkHigh and unwrappedSMA and uptrend

        if not stage2:
            logging.debug("[FAIL] ts_code:{} is not in stage2, w52wkHigh:{}, unwrappedSMA:{}, uptrend:{}".format(
                ts_code, w52wkHigh, unwrappedSMA, uptrend))
            return False

        return stage2

    def loopbackTesting(self, codes, start_date):
        for code in codes:
            df = self.get_stock_daily(code, start_date)
            if 1 == len(df):
                logging.info("ts_code:{} 没有更新的交易数据\n".format(code))
                return

            df_buy = df.tail(1)
            df.drop(df[df.trade_date == start_date].index, inplace=True)
            if debug:
                logging.info("\nts_code:{}\ndf:\n{}\ndf_buy:\n{}".format(code, df, df_buy))

            buy_close = df_buy['close'][1]
            close = df['close'][0]

            highest = df['high'].max()
            lowest = df['low'].min()
            logging.info("ts_code:{}, close:{}, rate:{:0.2f}%, highest:{}, lowest:{}".format(
                code, close, (close - buy_close) * 100 / close, highest, lowest))

    def loopbackTestingFile(self, path, file):
        date = os.path.splitext(file)[0]
        with open(path + "/" + file, 'r') as f1:
            list1 = f1.readlines()
            for i in range(0, len(list1)):
                list1[i] = list1[i].rstrip('\n')
            logging.info("file:{}\nts_code:{}\n".format(file, list1))
            self.loopbackTesting(list1, date)

    def loopbackTestingDir(self, path=os.getcwd() + '/data/vcp'):
        files = os.listdir(path)
        for file in files:
            suffix = os.path.splitext(file)[1]
            if '.txt' == suffix:
                self.loopbackTestingFile(path, file)

    def getcandlecharts(self, codes):
        fig = plt.figure(figsize=(10, 8), facecolor='w')
        index = 1
        for code in codes:
            logging.info("plot {}".format(code))
            df = self.get_stock_daily(code, start_date='20171101')
            df.shape

            df2 = df.query('trade_date >= "20171101"').reset_index()
            df2 = df2.sort_values(by='trade_date', ascending=True)  # 原始数据按照日期降序排列
            df2['dates'] = np.arange(0, len(df2))  # len(df2)指记录数

            ax = fig.add_subplot(4, 4, index)
            candlestick_ochl(ax, quotes=df2[['dates', 'open', 'close', 'high', 'low']].values, width=0.6,
                             colorup="r", colordown="g", alpha=1.0)
            plt.grid(True)
            date_tickers = df2['trade_date'].values

            def format_date(x, pos):
                if (x < 0) or (x > len(date_tickers) - 1):
                    return ''
                return date_tickers[int(x)]
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(
                format_date))  # 按一定规则选取并在水平轴上显示时间刻度
            plt.xticks(rotation=30)
            # plt.title('%s: %.2f' % (get_stock_basic(code).name, codes[code]))
            plt.title('%s: %s' % (self.get_stock_basic(code).name[0], code))
            plt.xlabel("Date")
            plt.ylabel("Price")
            ax.xaxis_date()
            index = index + 1
            if index == 16:
                break
        plt.suptitle('股票池')
        plt.tight_layout(1.5)
        plt.subplots_adjust(top=0.92)
        fig.savefig('scatter.png', dpi=600, format='png')
        plt.show()


'''run'''
if __name__ == '__main__':
    key = os.environ["PRO_KEY"]
    vcp = VCP(key=key)
    vcp.vcp_search()
