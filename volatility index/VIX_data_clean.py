# -*- coding: utf-8 -*-
"""
Created on Thu Sep 27 14:45:19 2018

@author: 54326
"""

import pandas as pd
import os

# import basic contract info
# basic = pd.read_excel(os.getcwd()+'\\data\\50ETF期权合约基本资料.xlsx', parse_date=True)
basic = pd.read_excel(os.getcwd()+'\\data\\沪300ETF期权合约基本资料.xlsx', parse_date=True)
basic = basic.loc[:, ['trade_code', 'type', 'expire']]

# import daily quotes
# data2015 = pd.read_excel(os.getcwd()+'\\data\\50ETF期权日行情2015-2016.xlsx', parse_date=True)
# data2017 = pd.read_excel(os.getcwd()+'\\data\\50ETF期权日行情2017-2018.xlsx', parse_date=True)
# data2018 = pd.read_excel(os.getcwd()+'\\data\\50ETF期权日行情2018补.xlsx', parse_date=True)
# data2019 = pd.read_excel(os.getcwd()+'\\data\\50ETF期权日行情2019.xlsx', parse_date=True)
# data2020 = pd.read_excel(os.getcwd()+'\\data\\50ETF期权日行情2020.xlsx', parse_date=True)
# data2015 = data2015.loc[:, ['date', 'trade_code', 'strike', 'settle']]
# data2017 = data2017.loc[:, ['date', 'trade_code', 'strike', 'settle']]
# data2018 = data2018.loc[:, ['date', 'trade_code', 'strike', 'settle']]
# data2020 = data2020.loc[:, ['date', 'trade_code', 'strike', 'settle']]
# data = pd.concat([data2015, data2017, data2018, data2019, data2020])

# import daily quotes(sse 300etf)
data2020 = pd.read_excel(os.getcwd()+'\\data\\沪300ETF期权日行情2019-2020.xlsx', parse_date=True)
data2020 = data2020.loc[:, ['date', 'trade_code', 'strike', 'settle']]
data = data2020

# separate call and put options
datas = pd.merge(data, basic, how='left')  # 按trade_code合并
datas.drop(columns='trade_code', inplace=True)  # 删除trade_code列
calls = datas[datas['type'] == '认购']  # 分离出认购期权的数据
puts = datas[datas['type'] == '认沽']  # 分离出认沽期权的数据
calls.rename(columns={'settle': 'call'}, inplace=True)
puts.rename(columns={'settle': 'put'}, inplace=True)

# 按交易日期、到期日、执行价为连接键合并，并删除重复数据
options = pd.merge(calls, puts.loc[:, ['date', 'expire', 'strike', 'put']], 
                   on=['date', 'expire', 'strike'], how='left').drop_duplicates()
# 计算剩余到期的天数（自然日）
options = options.loc[:, ['date', 'expire', 'strike', 'call', 'put']]
options['T_days'] = (options['expire'] - options['date']).apply(lambda x: x.days)


def small(x, s):
    '''确定第（s+1）小的值'''
    ts = list(set(x))
    ts.sort()
    return ts[s]


last1 = options.groupby('date')['T_days'].apply(small, s=0)  # 交易日第一短到期天数
last2 = options.groupby('date')['T_days'].apply(small, s=1)  # 交易日第二短到期天数
last3 = options.groupby('date')['T_days'].apply(small, s=2)  # 交易日第三短到期天数
last = pd.concat([last1, last2, last3], axis=1)
last.columns = ['last1', 'last2', 'last3']
for i in range(len(last)):
    if last['last1'][i] <= 7: # 近月合约到期期限必须不少于1个星期
        last.loc[last.index[i], 'last1'] = last.loc[last.index[i], 'last2']
        last.loc[last.index[i], 'last2'] = last.loc[last.index[i], 'last3']
options = pd.merge(options, last, on='date', how='left')

# options.to_excel(os.getcwd()+'\\data\\50ETF_option_VIX_2020.xlsx')
options.to_excel(os.getcwd()+'\\data\\沪300ETF_option_VIX_2020.xlsx')
data_file = os.getcwd()+'\\data\\market_300_2020.h5'
shibor = pd.read_excel(os.getcwd()+'\\data\\shibor_3M.xlsx', index_col='date')
with pd.HDFStore(data_file) as store:
    store['SSE300ETF_option_VIX'] = options
    store['shibor_3M'] = shibor
