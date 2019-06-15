import pandas as pd
import sympy as sp
import numpy as np
import statistics, collections

import os
os.chdir('C:\\Users\\Michael\\Desktop\\Options\\Programs\\backtester\\data_programs')

def exec(stocks,indicators,criterias):
    ## FORMAT:
    ## Indicators ---- [List of indicators used]
    ## Criteria ---- [[Criteria for 1st indicator],[]...]
    ##               Example: [+20%,SMA,5] (If the indicator is 20% above 15-day SMA of indicator)
    ## Example: exec(['AMAT','BAC'] , [['ATR',14],['ULT']] , [[+20%,SMA,5],['<40']])

    global test

    sym_dates = {}
    for stock in stocks:
        ## Get data for indicators
        TA_data = {}
        for indi in indicators:
            if len(indi) > 1:
                TA_data[indi[0]] = data.getTA(stock=stock,function=indi[0],period=indi[1])
            else:
                TA_data[indi[0]] = data.getTA(stock=stock,function=indi[0],period=0)

        ## Find dates where the criteria set for TA is met
        TA_dates = []
        for indi, values in TA_data.items():
            criteria = criterias[indi]
            if criteria[0] == 'values': ##e.g. ULT, less than 40
                if criteria[1] == 'crossover':
                    if criteria[2] == 'less':
                        TA_data[indi]['Previous'] = TA_data[indi][indi] > criteria[3]
                        TA_data[indi]['Previous'] = TA_data[indi]['Previous'].shift(1)
                        TA_data[indi]['Current'] = TA_data[indi][indi] < criteria[3]
                    else:
                        TA_data[indi]['Previous'] = TA_data[indi][indi] < criteria[3]
                        TA_data[indi]['Previous'] = TA_data[indi]['Previous'].shift(1)
                        TA_data[indi]['Current'] = TA_data[indi][indi] > criteria[3]
                    TA_data[indi]['Criteria'] = np.where((TA_data[indi]['Previous'] == True) & (TA_data[indi]['Current'] == True),True,False)

                elif criteria[1] == 'all':
                    if criteria[2] == 'less':
                        TA_data[indi]['Criteria'] = TA_data[indi][indi] < criteria[3]
                    else:
                        TA_data[indi]['Criteria'] = TA_data[indi][indi] > criteria[3]

                ## Collect dates where criteria is met for all TAs
                TA_dates.append(TA_data[indi].loc[TA_data[indi]['Criteria'] == True]['time'].tolist())

            elif criteria[0] == 'percent_change':
                test = criteria[1:]
                change = calc.p2f(test[0]) ## Change criteria set by user
                dates = processing.setCriteria(TA_data[indi],indi,change)
                ## Collect dates where criteria is met for all TAs
                TA_dates.append(dates)

        ## Find dates where all TA criterias are met
        final_dates = []
        for x in range(1,len(TA_dates)):
            if final_dates == []:
                final_dates = set(TA_dates[x-1]) & set(TA_dates[x])
            else:
                final_dates = final_dates & set(TA_dates[x])
        sym_dates[stock] = list(final_dates)
    return sym_dates

class processing:
    def __init__():
        pass

    ## Create an extra column according to setting for comparison
    def setCriteria(df,indi,change):
        ## Returns 1 if num passes test
        if len(test) == 1:
            df['Previous'] = df[indi].shift(1)
        else:
            if test[1] == 'SMA':
                df['SMA'] = df[indi].rolling(window=test[2]).mean()
                df = df.iloc[test[2]-1:] ## Remove columns without SMA value
        previous = list(df)[-1] ## Get name of last column
        criteria = df.loc[(df[indi] - df[previous]) / df[previous] > change]['time'].tolist()
        return criteria

class data:
    ## Uses the ALPHAVANTAGE API
    ## Returns a CSV file
    def __init__():
        pass

    ## From API
    def getPrice(stock):
        try:
            url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&outputsize=full&symbol='+stock+'&apikey=3VWEA280OOGR9AL4&datatype=csv'
            df = pd.read_csv(url)
            df = df[::-1]
        except:
            return None
        return df

    def getTA(stock='',function='ATR',period=0):
        try:
            period = str(period)
            if period != '0':
                ## If there is time period variable
                url = 'https://www.alphavantage.co/query?function='+function+'&symbol='+stock+'&interval=daily&time_period='+period+'&apikey=3VWEA280OOGR9AL4&datatype=csv'
                df = pd.read_csv(url)
            else:
                ## If there isn't time period variable
                url = 'https://www.alphavantage.co/query?function='+function+'&symbol='+stock+'&interval=daily&apikey=3VWEA280OOGR9AL4&datatype=csv'
                df = pd.read_csv(url)
            df = df[::-1]
            df = df.reset_index(drop=True)
        except:
            return None
        return df

class calc:
    def __init__():
        pass

    def getSMA(close,num):
        ## Calculates Simple MA
        stock_MA = []
        for x in range(len(close)-num+1):
            period = close[x:num+x]
            stock_MA.append(statistics.mean(period))

        return stock_MA

    def getChange(current, previous):
        if current == previous:
            return 0
        try:
            return (current - previous) / previous
        except:
            return 0

    def p2f(x):
        return float(x.strip('%'))/100

#print(exec(['AMAT'] , [['ATR',14],['ULTOSC']] , {'ATR':['percent_change','+20%','SMA',5],'ULTOSC':['values','all','more',40]}))
#print(exec(['AAPL'] , [['ATR',14],['ULTOSC']] , {'ATR':['percent_change','+20%','SMA',5],'ULTOSC':['values','all','less',40]}))
