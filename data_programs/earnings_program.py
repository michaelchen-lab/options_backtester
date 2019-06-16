import pandas as pd
from datetime import datetime,timedelta
import os
os.chdir('C:\\Users\\Michael\\Desktop\\Options\\earnings_data')

def exec(symbols,strat_params):
    """
    Returns:
        Entry_dates (dict) --- Which day and symbol to enter trade
        Exit_dates (dict) --- Which day and symbol to exit trade
        DTE_range (range) --- Range of possible expiration dates of trade
                              (helps choose which option contract)
    """
    ## Parameters
    entry = strat_params['Max/Min Entry Days bef. Earnings'].split(',')
    days_bef_earnings_pref = strat_params['Preference: Days bef. Earnings'].replace(' ','')
    exit_days_pref = strat_params['Exit Days bef. Earnings']
    exit_range = strat_params['Max/Min DTE aft. Earnings'].split(',')
    exit_pref = strat_params['Preference: DTE aft. Earnings'].replace(' ','') # min or max DTE

    ## Processing data
    sym_entry_dates,sym_exit_dates,sym_exp_range = {},{},{}
    tradingdays = tools.getTradingDays()
    for symbol in symbols:
        df = findData(symbol) ## earnings data
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
    def entrydate(df, max_DBE, min_DBE, pref, tradingdays):
        ## Returns the list of entry dates
        data = []
        for index,row in df.iterrows(): ## Get a range of possible dates for each event
            #date = datetime.strptime(row['Date'],"%m/%d/%Y")
            date = row['Date'].to_pydatetime()
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
                    final_dates.append(date) ## Only one date for each earnings event
                    break
        ## Reverse the dates from earlier to later
        final_dates = list(reversed(final_dates))
        return final_dates

    def exitdate(df, pref, tradingdays):
        ## Return the exit date of each earnings trade
        exit_dates = []
        for index,row in df.iterrows():
            date, type = row['Date'].to_pydatetime(), row['Time'] ## Earnings date & earnings type
            exit_date = 0
            while exit_date == 0: ## Get the exit day of earnings event
                if type == 'BO' or type == '-': ## Before open
                    if date - timedelta(pref) in tradingdays:
                        exit_date = date - timedelta(pref)
                    else:
                        date = date - timedelta(1)
                elif type == 'AC': ## After close
                    if date - timedelta(pref-1) in tradingdays:
                        exit_date = date - timedelta(pref-1)
                    else:
                        date = date - timedelta(1)
            exit_dates.append(exit_date)
        return exit_dates[::-1] ## reverse dates (to ascending order)

    def max_exp(df, max_exit, min_exit, pref):
        ## Return the range of possible expirations for option
        exp_range = []
        for index,row in df.iterrows():
            date = row['Date'].to_pydatetime()
            if pref == 'min':
                exp_range.append([date+timedelta(int(min_exit)), date+timedelta(int(max_exit))])
            else:
                exp_range.append([date+timedelta(int(max_exit)), date+timedelta(int(min_exit))])
        return exp_range[::-1]

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

#print(exec(['AMAT'],strat_params))
