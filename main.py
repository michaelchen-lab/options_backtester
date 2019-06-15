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
    profile = config(file)
    ## Get entry_dates, exit_dates, DTE_range
    getDates(profile)

    ## Execute Program
    results = execution.main_backtest(profile)

    return entry_dates

class config():
    """
    Function: Open settings csv file and save all parameters
    Parameters: file (string) -- Name of csv file to open
    Returns: symbols (list), strategy (string), exec_params (dict), strat_params (dict)
    """
    def __init__(self, file):
        symbols,strategy,main_dir,exec_params,strat_params = self.get_params(file)

        self.symbols = symbols
        self.strategy = strategy
        self.main_dir = main_dir
        self.exec_params = exec_params
        self.strat_params = strat_params

    def get_params(self,file):
        try:
            df = pd.read_csv(file, index_col='Variable')
        except:
            print('setting file not found')

        ## Key parameters
        symbols, strategy, main_dir = df.loc['Symbols','Value1'].split(','), df.loc['Strategy','Value1'], df.loc['Main Directory','Value1']
        ## Get Execution parameters
        exec_param_names = ['Time Period','Init.Liquidity','Position Size','Prof. Target','Stop Loss','Commissions','Bid-Ask Slippage']
        exec_df = df[df.index.isin(exec_param_names)]
        exec_params = dict(zip(exec_param_names, exec_df['Value1'].tolist()))
        ## Get Strategy parameters
        strat_param_names = ['Max/Min DTE aft. Earnings','Preference: DTE aft. Earnings','Max/Min Entry Days bef. Earnings','Preference: Days bef. Earnings','Exit Days bef. Earnings']
        strat_df = df[df.index.isin(strat_param_names)]
        strat_params = dict(zip(strat_param_names,strat_df['Value1'].tolist()))

        return symbols, strategy, main_dir, exec_params, strat_params

class getDates():
    """
    Function: A group of functions for finding the dates to open positions on each stock of each strategy
    """
    def __init__(self, profile):
        if profile.strategy == 'earnings':
            entry_dates,exit_dates,max_min_exp_dates = self.earnings(profile.symbols, profile.strat_params)

        profile.entry_dates = entry_dates
        profile.exit_dates = exit_dates
        profile.DTE_range = max_min_exp_dates

    def earnings(self,symbols,strat_params):
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
