# -*- coding: utf-8 -*-
"""
Created on Sun May 27 21:50:36 2018

@author: Administrator
"""

#选股策略
from WindPy import w
import math
import pandas as pd
import xlrd
import statsmodels.api as sm
import tushare as ts
import numpy as np 
import matplotlib.pyplot as plt
data1=pd.DataFrame()
w.start()

#选股范围
stocklist=['000541.SZ','000021.SZ','600682.SH','000530.SZ','600655.SH','600642.SH','000539.SZ','000022.SZ','000538.SZ','000002.SZ']

#持仓时间
date=w.tdays("2016-12-30", "2017-12-31", "Period=M").Times

#针对每个调仓周期执行选股策略
#计算10只股票每只股票增长率g
div=pd.read_excel(r'F:\div.xls')
b=[]
X0=[]
for i in range(1,21):
    X0.append(i)
X=sm.add_constant(X0)
div0=[]
for m in range(1,11):
    Y=[]
    for i in range(1,21):
        Y.append(math.log(div.iloc[i,m]/div.iloc[0,m]))
    div0.append(div.iloc[20,m])
    result=sm.OLS(Y,X).fit()
    a1,b1=result.params
    b.append(b1)

#计算离散复利下的增长率g1
g=[]
for n in range(len(b)):
    g.append(math.exp(b[n])-1)

#计算β值，由于2015年中国股市的异常波动，跳过该年数据，选择2016年周度收益率测算β
df=pd.DataFrame()
xls=xlrd.open_workbook(r'F:/rate.xlsx')
y1=xls.sheets()[3].col_values(12)[2:len(xls.sheets()[3].col_values(12))]
x1=xls.sheets()[3].col_values(13)[2:len(xls.sheets()[3].col_values(13))]
y2=xls.sheets()[4].col_values(12)[2:len(xls.sheets()[4].col_values(12))]
x2=xls.sheets()[4].col_values(13)[2:len(xls.sheets()[4].col_values(13))]
y3=xls.sheets()[5].col_values(12)[2:len(xls.sheets()[5].col_values(12))]
x3=xls.sheets()[5].col_values(13)[2:len(xls.sheets()[5].col_values(13))]
y4=xls.sheets()[6].col_values(12)[2:len(xls.sheets()[6].col_values(12))]
x4=xls.sheets()[6].col_values(13)[2:len(xls.sheets()[6].col_values(13))]
y5=xls.sheets()[7].col_values(12)[2:len(xls.sheets()[7].col_values(12))]
x5=xls.sheets()[7].col_values(13)[2:len(xls.sheets()[7].col_values(13))]
y6=xls.sheets()[8].col_values(12)[2:len(xls.sheets()[8].col_values(12))]
x6=xls.sheets()[8].col_values(13)[2:len(xls.sheets()[8].col_values(13))]
y7=xls.sheets()[9].col_values(12)[2:len(xls.sheets()[9].col_values(12))]
x7=xls.sheets()[9].col_values(13)[2:len(xls.sheets()[9].col_values(13))]
y8=xls.sheets()[10].col_values(12)[2:len(xls.sheets()[10].col_values(12))]
x8=xls.sheets()[10].col_values(13)[2:len(xls.sheets()[10].col_values(13))]
y9=xls.sheets()[11].col_values(12)[2:len(xls.sheets()[11].col_values(12))]
x9=xls.sheets()[11].col_values(13)[2:len(xls.sheets()[11].col_values(13))]
y10=xls.sheets()[12].col_values(12)[2:len(xls.sheets()[12].col_values(12))]
x10=xls.sheets()[12].col_values(13)[2:len(xls.sheets()[12].col_values(13))]
beta=[]
beta.append(sm.OLS(y1,x1).fit().params)
beta.append(sm.OLS(y2,x2).fit().params)
beta.append(sm.OLS(y3,x3).fit().params)
beta.append(sm.OLS(y4,x4).fit().params)
beta.append(sm.OLS(y5,x5).fit().params)
beta.append(sm.OLS(y6,x6).fit().params)
beta.append(sm.OLS(y7,x7).fit().params)
beta.append(sm.OLS(y8,x8).fit().params)
beta.append(sm.OLS(y9,x9).fit().params)
beta.append(sm.OLS(y10,x10).fit().params)

#在2017年的每个月度选取价值被低估的股票
time=w.tdays("2016-12-01", "2017-11-30", "Period=M").Times
p=[]
m=1
#使用2016年上证综指收益率代表预期未来市场组合收益率rm，使用2016年发行3年期国债收益率代表预期未来无风险收益率）
rm=(w.wsd("000001.SH", "close", "2017-01-20", "2017-01-20", "PriceAdj=F").Data[0][0]-w.wsd("000001.SH", "close", "2016-01-21", "2016-01-21", "PriceAdj=F").Data[0][0])/w.wsd("000001.SH", "close", "2016-01-21", "2016-01-21", "PriceAdj=F").Data[0][0]
rf=0.0365
choosen=[]
rs=[]
for i in range(10):
    rs.append(beta[i]*(rm-rf)+rf)
    
for i in time:
    t=0;
    choosen1=[]
    print(m,'month select:')
    for s in stocklist:
        p0=w.wsd(s, "close", i, i, "PriceAdj=F").Data[0]
        g0=(p0*rs[t]-div0[t])/(div0[t]+p0)
        if g0<g[t]:
            print(stocklist[t])
            choosen1.append(stocklist[t])
        t=t+1
    choosen.append(choosen1)
    m=m+1

p0=[]
for i in range(len(g)):
    p0.append(div0[i]*(1+g[i])/(rs[i]-g[i]))
#可知调仓结果为每个月月末均买入以下两只股票:000022.SZ、000538.SZ
#按照市值加权平均测算每月持仓比例矩阵p
ev=[]
for i in range(len(choosen)):
    ev1=[]
    for m in range(len(choosen[i])):
        ev1.append( w.wsd(choosen[i][m], "ev", time[i], time[i], "unit=1;PriceAdj=F").Data[0][0])
    ev.append(ev1)
p=[]
for i in range(len(ev)):
    p1=[]
    for s in range(len(ev[i])):
        p1.append(ev[i][s]/sum(ev[i]))
    p.append(p1)
    
#择时策略：从2016年12月底开始每个月月末买入上述两只股票，在持仓期间若实时股价使得：p>=p0,则卖出，否则则持有。
data=np.array([div0,rs,g,p0]).T  
columns=['d0','rs','g','p0']
index=stocklist
df=pd.DataFrame(data,index=index,columns=columns)

#先选出卖点，如果一个月中没有出现卖点，则该月不调仓。
selltime=[]
for i in range(len(choosen)):
    selltime1=[]
    for m in range(len(choosen[i])):
        selltime2=[]
        for day in w.tdays(date[i], date[i+1], "").Times:
            if w.wsd(choosen[i][m], "high", day, day, "PriceAdj=F").Data[0][0]>=df.p0[choosen[i][m]]:
                selltime2.append(day)
        if len(selltime2)==0:
            selltime2.append(day)
            print(i+1,"month",choosen[i][m],'不调仓')
        selltime1.append(selltime2)
    selltime.append(selltime1)

#由于12个月没有月份需要调仓，表示市价一直位于估值以下，一直处于被低估的状态，因此一直持有。
#计算该12个月每个月的持仓收益rt
rt=[]
for i in range(len(choosen)):
    rt1=[]
    for m in range(len(choosen[i])):
        rt1.append((w.wsd(choosen[i][m], "close", selltime[i][m][0], selltime[i][m][0], "PriceAdj=F").Data[0][0]-w.wsd(choosen[i][m], "close", date[i], date[i], "PriceAdj=F").Data[0][0])/w.wsd(choosen[i][m], "close", date[i], date[i], "PriceAdj=F").Data[0][0])
    rt.append(rt1)   
rt_w=np.array(rt)*np.array(p)
r_pool=[]
s=1
for i in range(12):
    s=s*(sum(rt_w[i])+1)
    r_pool.append(s-1)
    
#计算该12个月每个月的大盘收益rmt
rmt=[]
s0=1
for i in range(12):
    s0=s0*((w.wsd("000001.SH", "close", date[i+1], date[i+1], "PriceAdj=F").Data[0][0]-w.wsd("000001.SH", "close", date[i], date[i], "PriceAdj=F").Data[0][0])/w.wsd("000001.SH", "close", date[i], date[i], "PriceAdj=F").Data[0][0]+1)
    rmt.append(s0-1)
    
#找出12个月内跑赢大盘的月份数以及概率
winmonth=[]
win=0
for i in range(12):
    if r_pool[i]>rmt[i]:
        winmonth.append(i+1)
        win+=1
winrate=win/12
#winmonth=[3, 4, 5, 6, 7, 8, 9, 10, 11, 12]；winrate=0.83
#大盘年收益率为rmt[-1]=0.066
#股票池年收益率r_pool[-1]=0.343

#收益率可视化
df2=pd.DataFrame()
columns=['rmt','r_pool']
index=date[1:]
data1=np.array([rmt,r_pool]).T
df2=pd.DataFrame(data1,index=index,columns=columns)
plt.xlabel('time')
plt.ylabel('return rate')
plt.plot(df2.rmt[:],'b',linestyle='-',label='rm')
plt.plot(df2.r_pool[:],'r',linestyle='--',label='r_pool')
plt.legend()
plt.title("r_pool vs rm")
plt.show()
