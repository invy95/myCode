# -*- coding: utf-8 -*-
"""
Created on Sat Aug 18 21:50:11 2018

@author: Administrator
"""

import math 
import tushare as ts 
import numpy as np 
from scipy import stats
import statsmodels.api as sm
#编写函数进行OLS回归，T检验及F检验

#获取数据
Y=ts.get_hist_data('600000',start='2018-03-16',end='2018-04-04') 
X=ts.get_hist_data('sh',start='2018-03-16',end='2018-04-04') 
x1=np.array(X['close']) 
y1=np.array(Y['close']) 
x0=[] 
y0=[] 
for i in range(len(x1)):
     x0.append(math.log(x1[i]))
     y0.append(math.log(y1[i]))
#OLS回归
def ols_f(x0,y0):
    s1=np.float(0)
    s2=np.float(0)
    for i in range(len(x0)):
         s1+=x0[i]*y0[i]
         s2+=x0[i]**2
    T=len(x0)
    b=[s1-T*np.mean(x0)*np.mean(y0)]/(s2-T*np.mean(x0)**2)
    a=np.mean(y0)-b*np.mean(x0)
    return a,b
a,b=ols_f(x0,y0)
print('a=',float(a),'b=',float(b)) 

#直接调用OLS函数
X=sm.add_constant(x0)
est=sm.OLS(y0,X).fit()
est.summary()

#求T值
s3=np.float(0) 
for i in range(len(y0)):
    s3+=(y0[i]-a-b*x0[i])**2
s3=s3/(len(x0)-2)
def t_test(x0,y0):
    s1=np.float(0)
    s2=np.float(0)
    for i in range(len(x0)):
        s1+=x0[i]*x0[i]
        s2+=(x0[i]-np.mean(x0))*(x0[i]-np.mean(x0))
    T=len(x0)
    SE1=math.sqrt(s3*s1/(T*s2))
    SE2=math.sqrt(s3/s2)
    return a/SE1,b/SE2
t1,t2=t_test(x0,y0) 
print('ta=',float(t1),'tb=',float(t2))
#求P值
def p_value(t):
    if t>0:
        p=1-stats.t.cdf(t,df=len(x0)-2) 
    else:
        p=stats.t.cdf(t,df=len(x0)-2)
    return p
print('pa=',p_value(t1),'pb=',p_value(t2))
#求置信区间
def sig_f(p,df):
    a1=stats.t.ppf((1-p)/2,df=len(x0)-2)
    a2=stats.t.ppf((1-p)/2+p,df=len(x0)-2)
    return a1,a2
df=len(x0)-2
a1,a2=sig_f(0.95,df)
print('significant 95% area is from',a1,'to',a2)