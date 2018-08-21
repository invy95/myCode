# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 19:02:42 2018

@author: 倪风昌
"""
#批量处理年化到期收益率、久期、凸性

import numpy as np
import pandas as pd
import xlrd
import datetime
import time

#输入起始计算的时间
date=datetime.datetime(2018, 7, 17, 0, 0)

df1=pd.DataFrame()
df=pd.read_excel('D://ywdata//20180717evaluation.xls')#将当天价格信息表.xls写入df
df.rename(columns={'NJ3049民生银行估值表20180717': 'id', 'Unnamed: 6': 'price'}, inplace=True)#重命名df中的id,price列
df1['id']=df.id[28:73]#将需要的df.id的特定行存到df1.id中
df1['price']=df.price[28:73]#将需要的df.price的特定行存到df1.price中
df1=df1.reset_index(drop=True) #重置df1的序号
#债券编号处理：将df1.id仅取后六位
for i in range(len(df1['id'])):
    df1.id[i]=df.id[i+28][-6:]

df3=pd.read_excel('D://ywdata//data1.xls')#读取每只债券的具体支付情况

dff=pd.DataFrame()#创建年化到期收益率表
dff=pd.DataFrame(columns=['基金编码','年化到期收益率'])

dff1=pd.DataFrame()#创建久期表
dff1=pd.DataFrame(columns=['基金编码','久期'])

dff2=pd.DataFrame()#创建凸性表
dff2=pd.DataFrame(columns=['基金编码','凸性'])



for n in range(len(df1['id'])):  #循环每一个待计算的债券id 
    m=0
    df2=pd.DataFrame()#创建一个空的df2以备存取支付时间及现金流数据
    for i in range(len(df3['S_INFO_WINDCODE'])):#存取支付时间及现金流数据
        if df3.S_INFO_WINDCODE[i][:6]==df1.id[n]:
            df2.loc[m,'B_INFO_PAYMENTDATE']=datetime.datetime.strptime(str(df3.B_INFO_PAYMENTDATE[i]),'%Y%m%d')
            df2.loc[m,'B_INFO_PAYMENTSUM']=df3.B_INFO_PAYMENTSUM[i]
            m+=1
    if m>0:                
        price=df1.price[n]#记录价格
        df6=df2.sort_values(by='B_INFO_PAYMENTDATE',ascending=True)#按照支付日期升序对df2进行排序
        paydate=list(df6['B_INFO_PAYMENTDATE'])#将支付日期存入paydate
        cashflow=list(df6['B_INFO_PAYMENTSUM'])#将现金流存入cashflow
        df5=pd.DataFrame()#创建一个空dataframe以便对cashflow进行合理排序
        df5.loc[0,'cashflow']=0-float(price)
        for i in range(len(cashflow)):
            df5.loc[i+1,'cashflow']=cashflow[i]
        cashflow=list(df5['cashflow'])
    
        def npv_f(rate,paydate,cashflow):#计算净现金流
            npv=cashflow[0]
            for i in range(len(paydate)):
                diff_day= paydate[i].to_pydatetime()-date
                t=diff_day.days
                if t>0:
                    npv+=cashflow[i+1]/pow(1+rate,t)
            return npv
    
        def f_YTM(paydate,cashflows,interations=1000):#计算到期收益率（日计）
            rate=0.01
            investment=cashflows[0]
            for i in range(1,interations+1):
                rate*=(1-npv_f(rate,paydate,cashflows)/investment)
            return rate
        YTM=f_YTM(paydate,cashflow)#计算日计到期收益率
        dff.loc[n,'基金编码']=df1.id[n]
        dff.loc[n,'年化到期收益率']=pow(YTM+1,365)-1
        ytm=pow(1+YTM,365)-1#计算年化到期收益率
        
        
        def dur_f(ytm,price,paydate,cashflow):#计算久期
            s=0.0
            for i in range(len(paydate)):
                diff_day= paydate[i].to_pydatetime()-date
                t=diff_day.days
                if t>0:
                    t=float(t/365)
                    s+=cashflow[i+1]/pow(1+ytm,t)*t
            dur=s/float(price)
            return dur
        dur=dur_f(ytm,price,paydate,cashflow)
        dff.loc[n,'久期']=dur
        
        def dur_f1(ytm,price,paydate,cashflow):#计算修正久期
            s=0.0
            for i in range(len(paydate)):
                diff_day= paydate[i].to_pydatetime()-date
                t=diff_day.days
                if t>0:
                    t=float(t/365)
                    s+=cashflow[i+1]/pow(1+ytm,t+1)*t
            dur=s/float(price)
            return dur
        dur1=dur_f1(ytm,price,paydate,cashflow)
        dff.loc[n,'修正久期']=dur1
        
              
        def conv_f(ytm,price,paydate,cashflow):#计算凸性
            s=0.0
            for i in range(len(paydate)):
                diff_day= paydate[i].to_pydatetime()-date
                t=diff_day.days
                if t>0:
                    t=float(t/365)
                    s+=cashflow[i+1]*t*(t+1)/pow(1+ytm,t)
            conv=s/float(price)
            return conv
        conv=conv_f(ytm,price,paydate,cashflow)
        dff.loc[n,'凸性']=conv
        
        def conv_f1(ytm,price,paydate,cashflow):#计算修正凸性
            s=0.0
            for i in range(len(paydate)):
                diff_day= paydate[i].to_pydatetime()-date
                t=diff_day.days
                if t>0:
                    t=float(t/365)
                    s+=cashflow[i+1]*t*(t+1)/pow(1+ytm,t+2)
            conv=s/float(price)
            return conv
        conv1=conv_f1(ytm,price,paydate,cashflow)
        dff.loc[n,'修正凸性']=conv1

        
dff.to_excel('修改版到期收益率、久期、凸性表1.xls',sheet_name='sheet1')#将债券id、到期收益率、久期、修正久期、凸性、修正凸性组成的dff放入excel表格中    

    
