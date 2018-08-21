# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 10:23:34 2018

@author: 倪风昌
"""

import pandas as pd
import tushare as ts
import matplotlib.pyplot as plt
import xlrd
import statsmodels.api as sm
import numpy as np
df=pd.DataFrame()
df1=pd.DataFrame()
xls=xlrd.open_workbook(r'F:\rates.xlsx')
sheet0=xls.sheets()[0]
sheet1=xls.sheets()[1]
sheet2=xls.sheets()[2]
df['rf']=sheet0.col_values(9)
df['gl']=sheet1.col_values(9)
df['sz']=sheet2.col_values(9)
df1['r0']=df.sz[2:]-df.rf[2:]
df1['r1']=df.gl[2:]-df.rf[2:]
df1['rm']=df.sz[2:]
df1['r']=df.gl[2:]
df1['rf']=df.rf[2:]
X=[]
Y=[]
for i in range(2,len(df1.rm)):
    X.append(df1.r0[i])
    Y.append(df1.r1[i])
X=np.array(X)
Y=np.array(Y)
results=sm.OLS(Y,X).fit()
beta=results.params
df1['Er']=df1.r0*beta+df1.rf
plt.title('the return rate of 000651:real and expected')
plt.xlabel('week order')
plt.ylabel('return rate')
plt.plot(df1['r'],'y',linestyle='-',label='real return rate')
plt.plot(df1['Er'],'b',linestyle='-',label='expected return rate')
plt.legend() 
plt.show()  