import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
import os, glob
os.chdir('C:\\Users\\Michael\\Desktop\\Options\\vix_data\\all')

def plotVIX(symbols=[],startMonth='',endMonth=''):
    ## DATA COLLECTION
    months = tools.duration(startMonth+'01',endMonth+'01') ## Get all months
    date,vix = {},{}
    for sym in symbols:
        date[sym],vix[sym] = [],[]
    for month in months:
        df = pd.read_csv(month+'_optionstats.csv')
        for sym in symbols:
            symbol_df = df[df['Symbol'] == sym]
            vix[sym].extend(symbol_df['VIX'].tolist())
            date[sym].extend([str(date) for date in symbol_df['Date'].tolist()])

    ## PLOTTING
    for sym in symbols:
        plt.plot(date[sym],vix[sym],label=sym)
    plt.legend()
    plt.xlabel('Date')
    plt.ylabel('VIX')
    plt.show()

class tools:
    def __init__():
        pass

    def duration(startDate,endDate):
        ## Format: %Y-%m-%d
        cur_date = start = datetime.strptime(startDate, '%Y%m%d').date()
        end = datetime.strptime(endDate, '%Y%m%d').date()+timedelta(1)

        dates = []
        while cur_date < end:
            date = cur_date.strftime('%Y%m%d')
            dates.append(date[:-2])
            cur_date += relativedelta(months=1)
        return dates
plotVIX(symbols=['SPY','QQQ'],startMonth='201801',endMonth='201810')
