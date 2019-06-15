from data_programs import earnings_program,stocks_program,term_structure_program,vix_program
from execution import execution,portfolio
import pandas as pd

import os
os.chdir('C:\\Users\\Michael\\Desktop\\Options\\Programs\\backtester')

def start(file):
    """
    Function: The overall operations manager of backtester

    Parameters: file (string) -- Name of csv file that includes all setting for backtest
    """

    ## Getting user pref. and dates
    symbols,strategy,exec_params,strat_params = config(file)
    print(strat_params)
    if strategy == 'earnings':
        ## Get dates of position entries
        entry_dates,exit_dates,DTE_range = getDates.earnings(symbols,strat_params)
    elif strategy == 'calendar':
        pass

    ## Execute Program
    print(strat_params)
    print('done')
    results = execution.main_backtest(entry_dates,symbols,DTE_range,strategy,exec_params,strat_params)

    return entry_dates

def config(file):
    """
    Function: Open settings csv file and save all parameters
    Parameters: file (string) -- Name of csv file to open
    Returns: symbols (list), strategy (string), exec_params (dict), strat_params (dict)
    """
    try:
        df = pd.read_csv(file)
    except:
        print('setting file not found')

    ## Key Parameters
    strategy,symbols = df.iloc[0]['Value1'], df.iloc[1]['Value1'].split(',')
    ## Get Execution Parameters
    exec_start,exec_end = df.index[df['Variable'] == 'Time Period'].tolist()[0],df.index[df['Variable'] == 'Bid-Ask Slippage'].tolist()[0]
    exec_indexes = list(range(exec_start,exec_end+1))
    exec_params = df.iloc[exec_indexes]
    exec_params = dict(zip(exec_params.Variable,exec_params.Value1))
    ## Get Startegy Parameters
    strat_params = df.tail(len(df.index)-exec_end-1)
    strat_params = dict(zip(strat_params.Variable,strat_params.Value1))

    return symbols,strategy,exec_params,strat_params

class getDates:
    """
    Function: A group of functions for finding the dates to open positions on each stock of each strategy
    """
    def __init__():
        pass

    def earnings(symbols,strat_params):
        """
        Function: A wrapper for using earnings_program to find dates for the earnings strategy
        Parameters:
            symbols (list) -- all symbols
            strat_params (dict) -- parameters unique to each strategy
        """
        ## Use earnings_program to get dates
        #dates = earnings_program.exec(symbols,entry[0],entry[1],pref)
        entry_dates,exit_dates,max_min_exp_dates = earnings_program.exec(symbols,strat_params)

        return entry_dates,exit_dates,max_min_exp_dates

    def stocks():
        pass

    def term_structure():
        pass

    def vix_program():
        pass

print(start('earnings_config.csv'))

# ['BAC', 'AMAT']
# earnings
#
# Execution Parameters:
#            Variable   Value1
# 2       Time Period     Full
# 3    Init.Liquidity  100,000
# 4     Position Size      10%
# 5      Prof. Target      10%
# 6         Stop Loss      10%
# 7       Commissions      1.5
# 8  Bid-Ask Slippage        1
#
# Strategy Paramters:
#                             Variable Value1
# 9          Max/Min DTE aft. Earnings   10,1
# 10     Preference: DTE aft. Earnings    Min
# 11  Max/Min Entry Days bef. Earnings   11,7
# 12    Preference: Days bef. Earnings    min (shortest possible days bef. earnings)
# 13           Exit Days bef. Earnings      1

# Result:
# {
#     'BAC': [datetime.datetime(2009, 7, 10, 0, 0), datetime.datetime(2009, 10, 9, 0, 0)],
#     'AMAT': [datetime.datetime(2009, 5, 5, 0, 0), datetime.datetime(2009, 8, 4, 0, 0)]
# }
