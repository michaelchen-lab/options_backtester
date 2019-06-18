import pandas as pd
import sympy as sp
import numpy as np
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
import os, glob

def exec(symbols =[],criteria=[],startDate='',endDate='2018-10-30'):
    ## Inputs list of symbols, criteria for stock VIX and the start date of backtest
    ## criteria Format: [Mode: value/percent_change,
    ##                   Change: +20%/-5,
    ##                   Indicator (optional): [Name: SMA, Parameter(s): 5]

    ## DATA COLLECTION (Output: A DataFrame for each symbol)
    months = tools.duration(startDate,endDate)
    data = []
    for month in months:
        monthlystats = file.open(month)
        data.append(monthlystats)
    all_vix = pd.concat(data)
    vix_df = {}
    for symbol in symbols:
        symbol_df = all_vix[all_vix['Symbol'] == 'SPY']
        vix_df[symbol] = pd.DataFrame({'Date':symbol_df['Date'].tolist(), 'VIX':symbol_df['VIX'].tolist()})

    ## CRITERIA (Output: A list of dates for each symbol)
    sym_dates = {}
    for symbol,df in vix_df.items():
        if criteria[0] == 'percent_change':
            change = tools.p2f(criteria[1])
            if len(criteria) == 2:
                df['prev_VIX'] = df['VIX'].shift(1)
                df.drop([0], inplace=True)
                df[["prev_VIX", "VIX"]] = df[["prev_VIX", "VIX"]].apply(pd.to_numeric)
                df['Change'] = (df['VIX'] - df['prev_VIX']) / df['prev_VIX']

                if change > 0:
                    df['Criteria'] = df['Change'] > change
                else:
                    df['Criteria'] = df['Change'] < change

                sym_dates[symbol] = [str(date) for date in df.loc[df['Criteria'] == True]['Date'].tolist()]
            else:
                indi = criteria[2:][0]
                if indi[0] == 'SMA':
                    df['SMA'] = df['VIX'].rolling(window=indi[1]).mean() ## Implement SMA to new column
                    df = df.iloc[indi[1]-1:] ## Remove columns without SMA value
                else:
                    pass
                criteria = df.loc[(df['VIX'] - df[indi[0]]) / df[indi[0]] > change]['Date'].tolist()
                sym_dates[symbol] = criteria

        elif criteria[0] == 'value':
            pass
    return sym_dates

class file:
    def __init__():
        pass

    def open(month):
        ## Get all files in a particular month and year
        df = pd.read_csv(month+'_optionstats.csv')
        return df

class tools:
    def __init__():
        pass

    def duration(startDate,endDate):
        ## Format: %Y-%m-%d

        cur_date = start = datetime.strptime(startDate, '%Y-%m-%d').date()
        end = datetime.strptime(endDate, '%Y-%m-%d').date()+timedelta(1)

        dates = []
        while cur_date < end:
            date = cur_date.strftime('%Y%m%d')
            dates.append(date[:-2])
            cur_date += relativedelta(months=1)
        return dates

    def p2f(x):
        return float(x.strip('%'))/100

#print(exec(symbols=['SPY'],criteria=['percent_change','+20%',['SMA',5]],startDate='2018-01-01'))
