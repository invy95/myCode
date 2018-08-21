# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 11:54:13 2018

@author: 倪风昌
"""
import pandas as pd
import statsmodels.api as sm
import numpy as np
from sklearn.linear_model import LinearRegression


tp = pd.read_csv('D:\ywdata\liquidity3.csv',chunksize = 1000)
df = pd.concat(tp, ignore_index=True)
stocklist=list(set(df.stockid))

df2=pd.DataFrame()
n=0
for stockid in stocklist:
    df1=pd.DataFrame()
    m=0
    for i in range(len(df.stockid)):
        if df.stockid[i]==stockid:
            df1.loc[m,'rd']=df.returnrate[i]
            df1.loc[m,'vd']=df.vmuls[i]
            df1.loc[m,'red1']=df.afterre[i]
            if m==df.c[i]-1:
                rd=list(df1.rd)
                vd=list(df1.vd)
                Y=np.matrix(df1.red1).T
                X=np.matrix([rd,vd]).T
                regr = LinearRegression()#X为两变量构成的两列，Y为单变量构成的列
                regr.fit(X,Y)
                b2=regr.coef_[0][1]
                df2.loc[n,'stockid']=df.stockid[i]
                df2.loc[n,'monthst']=df.monthst[i]
                df2.loc[n,'liquidity']=b2
                n+=1
            if m<df.c[i]:
                m+=1
            if m==df.c[i]:
                m=0
                df1=pd.DataFrame()        















df0=df[0:6116]
df2=pd.DataFrame()
stocklist=list(['000001.SZ','000039.SZ'])
n=0
df1=pd.DataFrame()
for stockid in stocklist:
    m=0
    for i in range(len(df0.stockid)):
        if df0.stockid[i]==stockid:
            df1.loc[m,'rd']=df0.returnrate[i]
            df1.loc[m,'vd']=df0.vmuls[i]
            df1.loc[m,'red1']=df0.afterre[i]
            if m==df0.c[i]-1:
                rd=list(df1.rd)
                vd=list(df1.vd)
                Y=np.matrix(df1.red1).T
                X=np.matrix([rd,vd]).T
                regr = LinearRegression()#X为两变量构成的两列，Y为单变量构成的列
                regr.fit(X,Y)
                b2=regr.coef_[0][1]
                df2.loc[n,'stockid']=df0.stockid[i]
                df2.loc[n,'monthst']=df0.monthst[i]
                df2.loc[n,'liquidity']=b2
                n+=1
            if m<df0.c[i]:
                m+=1
            if m==df0.c[i]:
                m=0
                df1=pd.DataFrame()



df1=df[0:16]
rd=list(df1.returnrate)
vd=list(df1.vmuls)
X=np.matrix([rd,vd]).T
Y=np.matrix(df1.afterre).T
regr = LinearRegression()#X为两变量构成的两列，Y为单变量构成的列
regr.fit(X,Y)
b2=regr.coef_[0][1]
a=regr.intercept_

df0=df[0:33]
df2=pd.DataFrame()
stockid='000001.SZ'
m=0
n=0
for i in range(len(df0.stockid)):
    if df0.stockid[i]==stockid:
        df1.loc[m,'rd']=df0.returnrate[i]
        df1.loc[m,'vd']=df0.vmuls[i]
        df1.loc[m,'red1']=df0.afterre[i]
    if m==df0.c[i]-1:
        rd=list(df1.rd)
        vd=list(df1.vd)
        Y=np.matrix(df1.red1).T
        X=np.matrix([rd,vd]).T
        regr = LinearRegression()#X为两变量构成的两列，Y为单变量构成的列
        regr.fit(X,Y)
        b2=regr.coef_[0][1]
        df2.loc[n,'stockid']=df0.stockid[i]
        df2.loc[n,'monthst']=df0.monthst[i]
        df2.loc[n,'liquidity']=b2
        n+=1
    if m<df0.c[i]:
        m+=1
    if m==df0.c[i]:
        m=0
        df1=pd.DataFrame()
        
        
        
df0=df[0:4998]
df2=pd.DataFrame()
stocklist=list(['000001.SZ','000002.SZ'])
n=0
for stockid in stocklist:
    df1=pd.DataFrame()
    m=0
    for i in range(len(df0.stockid)):
        if df0.stockid[i]==stockid:
            df1.loc[m,'rd']=df0.returnrate[i]
            df1.loc[m,'vd']=df0.vmuls[i]
            df1.loc[m,'red1']=df0.afterre[i]
            if m==df0.c[i]-1:
                rd=list(df1.rd)
                vd=list(df1.vd)
                Y=np.matrix(df1.red1).T
                X=np.matrix([rd,vd]).T
                regr = LinearRegression()#X为两变量构成的两列，Y为单变量构成的列
                regr.fit(X,Y)
                b2=regr.coef_[0][1]
                df2.loc[n,'stockid']=df0.stockid[i]
                df2.loc[n,'monthst']=df0.monthst[i]
                df2.loc[n,'liquidity']=b2
                n+=1
            if m<df0.c[i]:
                m+=1
            if m==df0.c[i]:
                m=0
                df1=pd.DataFrame()        
            
            
df0=df[0:33]     
df2=pd.DataFrame()
stockid='000001.SZ'
m=0
n=0       
for i in range(len(df0.stockid)):
    if df0.stockid[i]==stockid:
        df1.loc[m,'rd']=df0.returnrate[i]
        df1.loc[m,'vd']=df0.vmuls[i]
        df1.loc[m,'red1']=df0.afterre[i]
    if m==df0.c[i]-1:
        rd=list(df1.rd)
        vd=list(df1.vd)
        Y=np.matrix(df1.red1).T
        X=np.matrix([rd,vd]).T
        regr = LinearRegression()#X为两变量构成的两列，Y为单变量构成的列
        regr.fit(X,Y)
        b2=regr.coef_[0][1]
        df2.loc[n,'stockid']=df0.stockid[i]
        df2.loc[n,'monthst']=df0.monthst[i]
        df2.loc[n,'liquidity']=b2
        n+=1
    if m<df0.c[i]:
        m+=1
    if m==df0.c[i]:
        m=0
        df1=pd.DataFrame()    

            