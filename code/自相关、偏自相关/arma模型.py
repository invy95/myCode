# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 10:26:06 2018

@author: 倪风昌
"""

import math 
import tushare as ts
import scipy as sp
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
import statsmodels.tsa.stattools as st
from statsmodels.tsa.stattools import adfuller as ADF#平稳性检验
from statsmodels.graphics.tsaplots import plot_acf,plot_pacf
from statsmodels.tsa.arima_model import ARMA

data=ts.get_hist_data('600000',start='2017-04-20',end='2018-04-20')
df=pd.DataFrame()
df['close']=data['close'].sort_index(ascending=True)
plt.xlabel('time')
plt.ylabel('price')
#绘制收盘价和时间折现图
plt.plot(df['close'],'y',linestyle='-')
plt.show()

#绘制每天的收益-时间折线图
plt.xlabel('time')
plt.ylabel('rate')
df['rate']=(df['close']-df['close'].shift(1))/df['close'].shift(1)
plt.plot(df['rate'])
plt.show()
#绘制收益自相关，偏自相关图
plot_acf(df.rate[1:],lags=31)
plot_pacf(df.rate[1:],lags=31)


r1=df.rate[1:-5]

'''由于自相关函数和偏自相关函数均为拖尾，因此为ARMA模型。'''
#检验序列平稳性
t = st.adfuller(r1)  # ADF检验
print("p-value:",t[1])
#检验是否为白噪声
def whitenoise_test(data):
    data1 = data.copy()
#白噪声检测
    from statsmodels.stats.diagnostic import acorr_ljungbox
    [[lb], [p]] = acorr_ljungbox(data1, lags = 1)
    if p < 0.05:
        print(u'原始序列为非白噪声序列，对应的p值为：%s' %p)
    else:
        print(u'原始该序列为白噪声序列，对应的p值为：%s' %p)
    [[lb], [p]] = acorr_ljungbox(data1.diff().dropna(), lags = 1)
    if p < 0.05:
        print(u'一阶差分序列为非白噪声序列，对应的p值为：%s' %p)
    else:
        print(u'一阶差分该序列为白噪声序列，对应的p值为：%s' %p)
whitenoise_test(r1)
#一阶差分处理
r2=r1.diff().dropna()
plot_acf(r2,lags=31)
plot_pacf(r2,lags=31)
#一阶差分使用ARMA模型
order=st.arma_order_select_ic(r2,max_ar=5,max_ma=5,ic=['aic','bic','hqic'])
model=ARMA(r2,order=order.bic_min_order)
print(order.bic_min_order)

#预测后5天的收益率
r3=df.rate[1:]
r3[-6:]
r4=r3.diff().dropna()
model = ARMA(r4,order=(0,1))
result= model.fit(disp=-1,method='css')
predict = result.predict(len(r4)-5,len(r4)-1)
r5=[]
r5.append(r3[-6])
for i in range(5):
    r5.append(predict[i]+r5[i])
#可视化  
plt.plot(list(r3[-5:]),label='Real Data')
plt.plot(r5[1:],label='Prediction')
plt.legend()
plt.show()
#计算RMSE
RMSE =np.sqrt(((np.array(r5[1:])-np.array(r3[-5:]))**2).sum()/5)
print(RMSE)
