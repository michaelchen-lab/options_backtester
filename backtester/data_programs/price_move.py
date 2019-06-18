import pandas as pd
import os
os.chdir('C:\\Users\\Michael\\Desktop\\Options\\Programs\\backtester\\data_programs')

## This program inputs
    # - a symbol
    # - past pm and max no. of days it occured
    # - Pm after past pm occurance over a set no. of days
def exec(symbols,change,f_days):
    ## Format: symbols -- []; change -- [percent change, days (including start day)]; f_days -- int
    f_changes = []

    for sym in symbols:
        df = data.getPrice(sym)
        df['p_change'] = df['close'].pct_change(periods=change[1]-1)
        df['f_change'] = df['close'].pct_change(periods=f_days-1).shift(-(f_days-1))

        change = calc.p2f(change[0])
        if change > 0:
            df['Criteria'] = df['p_change'] > change
        else:
            df['Criteria'] = df['p_change'] < change

        f_changes.append(df.loc[df['Criteria'] == True][['timestamp','f_change']])

        #print(df.tail(40))
        print(f_changes)

class calc:
    def __init__():
        pass

    def p2f(x):
        return float(x.strip('%'))/100

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
        except:
            return None
        return df

# pm = price move
