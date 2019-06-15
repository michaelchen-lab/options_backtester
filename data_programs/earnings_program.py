import pandas as pd
from datetime import datetime,timedelta
import os
os.chdir('C:\\Users\\Michael\\Desktop\\Options\\earnings_data')

def exec(symbols,strat_params):
    ## Parameters
    entry = strat_params['Max/Min Entry Days bef. Earnings'].split(',')
    days_bef_earnings_pref = strat_params['Preference: Days bef. Earnings'].replace(' ','')
    exit_days_pref = strat_params['Exit Days bef. Earnings']
    exit_range = strat_params['Max/Min DTE aft. Earnings'].split(',')
    exit_pref = strat_params['Preference: DTE aft. Earnings'].replace(' ','')

    ## Processing data
    sym_entry_dates,sym_exit_dates,sym_exp_range = {},{},{}
    tradingdays = tools.getTradingDays()
    for symbol in symbols:
        df = findData(symbol)
        ## Get entry dates
        entry_dates = find.entrydate(df,entry[0],entry[1],days_bef_earnings_pref,tradingdays)
        sym_entry_dates[symbol] = entry_dates
        ## Get exit dates
        exit_dates = find.exitdate(df,int(exit_days_pref),tradingdays)
        sym_exit_dates[symbol] = exit_dates
        ## Get option contract expiration dates max and min
        exp_range = find.max_exp(df,exit_range[0],exit_range[1],exit_pref)
        sym_exp_range[symbol] = exp_range
    return sym_entry_dates, sym_exit_dates, sym_exp_range

def findData(symbol): ## Get earnings data
    os.chdir('C:\\Users\\Michael\\Desktop\\Options\\earnings_data')
    df = pd.read_csv(symbol+'.csv')
    df['Date'] =  pd.to_datetime(df['Date'], format='%m/%d/%Y')
    df = df.loc[df['Date'] < datetime(2018,11,1)]
    return df

class find:
    def entrydate(df,max_DBE,min_DBE,pref,tradingdays):
        ## Returns the list of entry dates
        data = []
        for index,row in df.iterrows():
            #date = datetime.strptime(row['Date'],"%m/%d/%Y")
            date = row['Date']
            dates = tools.datetime_range(date-timedelta(int(max_DBE)),date-timedelta(int(min_DBE)))
            if pref == 'min':
                data.append(dates[::-1])
            else:
                data.append(dates)

        ## Make sure the selected dates are trading days
        final_dates = []
        for date_range in data:
            for date in date_range:
                if date in tradingdays:
                    final_dates.append(date)
                    break
        ## Reverse the dates from earlier to later
        final_dates = list(reversed(final_dates))
        return final_dates

    def exitdate(df,pref,tradingdays):
        ## Return the exit date of each earnings trade
        exit_dates = []
        for index,row in df.iterrows():
            date,time = row['Date'], row['Time']
            exit_date = 0
            while exit_date == 0: ## Get the exit day of earnings event
                if time == 'BO' or time == '-':
                    if date - timedelta(pref) in tradingdays:
                        exit_date = date - timedelta(pref)
                    else:
                        date = date - timedelta(1)
                elif time == 'AC':
                    if date - timedelta(pref-1) in tradingdays:
                        exit_date = date - timedelta(pref-1)
                    else:
                        date = date - timedelta(1)
            exit_dates.append(exit_date)
        return exit_dates[::1]

    def max_exp(df,max_exit,min_exit,pref):
        ## Return the range of possible expirations for option
        exp_range = []
        for index,row in df.iterrows():
            date = row['Date']
            if pref == 'min':
                exp_range.append([date+timedelta(int(min_exit)), date+timedelta(int(max_exit))])
            else:
                exp_range.append([date+timedelta(int(max_exit)), date+timedelta(int(min_exit))])
        return exp_range

class tools:
    def __init__():
        pass

    def getTradingDays():
        ## Get list of trading days from tradingdays.txt
        os.chdir('C:\\Users\\Michael\\Desktop\\Options\\programs\\backtester')
        tradingdays = open('tradingdays.txt', 'r')
        tradingdays = [line.split(',') for line in tradingdays.readlines()]
        tradingdays = [datetime.strptime(date[0][:-1],"%Y%m%d") for date in tradingdays]
        return tradingdays

    def datetime_range(start=None, end=None):
        span = end - start
        dates = []
        for i in range(span.days + 1):
            dates.append(start + timedelta(days=i))
        return dates

strat_params = {'Max/Min DTE aft. Earnings': '10,1',
                'Preference: DTE aft. Earnings': 'min',
                'Max/Min Entry Days bef. Earnings': '11,7',
                'Preference: Days bef. Earnings': 'min',
                'Exit Days bef. Earnings': '1'}
#print(exec(['AMAT'],strat_params))
