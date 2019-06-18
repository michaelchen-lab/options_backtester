import pandas as pd
pd.options.mode.chained_assignment = None
from datetime import datetime
import itertools

def main_backtest(profile, lg):
    """
    Function: The main program responsible for executing the backtest

    Parameters:
        profile.
            entry_dates (dict) -- {'BAC':[Timestamp('2009-07-10 00:00:00'), ...], 'AMAT':[...]}
            exit_dates (list) -- ['BAC','AMAT']
            DTE_range (dict) --
            List of max and min DTE for each trade, arranged according to preference
            Example: {'BAC':[[Timestamp('2009-07-10 00:00:00'), ...],[..., ...]], 'AMAT':[...]}
            symbols (list) -- ['AAPL','BAC'...]
            strategy (string) -- 'earnings'/'calendar'
            exec_params (dict) -- Generic execution parameters
            strat_params (dict) -- Strategy specific parameters
                (Example for both params are at the bottom)
        lg --- class of logs.py

    """
    pf = portfolio(profile, lg)
    #lg = logs.create()
    tradingdays_stamp, tradingdays_dir = tools.getTradingDays(pf)

    read_count = 0 ## to delete

    ## ---- START TIME LOOP ----
    for date_dir, date_stamp in zip(tradingdays_dir, tradingdays_stamp):
        ## If there are positions open or the date is an entry date, file will be opened.

        entry_symbols, open_sym = pf.check_event(date_stamp)

        ## NOTE: update_balance should always be before review_pos
        ##       (since close_pos does not change balance according to option prices)
        if entry_symbols == [] and open_sym == []: ## If there are no events
            pf.balance_history.append(pf.balance) ## Update history
        elif entry_symbols != [] and open_sym == []:
            data = tools.getOptions('hdf5', profile.data_dir, date_dir)
            pf.balance_history.append(pf.balance)
            pf.open_pos(data, entry_symbols, date_stamp)
        elif entry_symbols == [] and open_sym != []:
            read_count += 1

            data = tools.getOptions('hdf5', profile.data_dir, date_dir)
            pf.update_balance(data, open_sym)
            pf.review_pos(data, open_sym, date_stamp)
        elif entry_symbosl != [] and open_sym != []:
            read_count += 1

            data = tools.getOptions('hdf5', profile.data_dir, date_dir)
            pf.update_balance(data, open_sym)
            pf.review_pos(data, open_sym, date_stamp)
            pf.open_pos(data, entry_symbols, date_stamp)

    print(read_count)
    return pf

class portfolio:
    """
    Function: The main handler of portfolio execution and storing positions
    """
    def __init__(self, profile, lg):
        self.profile = profile
        self.lg = lg

        self.open_positions = dict(zip(self.profile.symbols, [[] for sym in self.profile.symbols]))
        self.closed_positions = dict(zip(self.profile.symbols, [[] for sym in self.profile.symbols]))

        ## Current balance must be reflected in balance history
        self.balance = int(self.profile.exec_params['Init.Liquidity'])
        self.balance_history = [int(self.profile.exec_params['Init.Liquidity'])]

    def check_event(self, date):
        """
        Function: Check for entry dates and open positions
        Parameters:
            date (datetime) -- Example: Timestamp('2016-07-06 00:00:00')
        Returns:
            entry_symbols (list) -- List of symbols to trade on that day
            open_pos (Boolean) -- True if there are open positions on that day
        """
        ## Check for entry dates
        entry_symbols = []
        for symbol, dates in self.profile.entry_dates.items():
            if date in dates:
                entry_symbols.append(symbol)
        for sym in entry_symbols: ## Remove all previous dates for entry and exit dates of each symbol
            self.profile.entry_dates[sym] = self.profile.entry_dates[sym][self.profile.entry_dates[sym].index(date):]
            self.profile.exit_dates[sym] = self.profile.exit_dates[sym][-len(self.profile.entry_dates[sym]):]

        ## Get symbols with open positions
        open_pos = [sym for sym in self.open_positions.keys() if self.open_positions[sym] != []]

        return entry_symbols,open_pos

    def update_balance(self, data, open_symbols):
        """
        Function: Update balance according to market value of existing positions
        Parameters:
            data (Pandas df) --- Options data of that day
            open_symbols (list) --- Symbols with open positions
        """
        total_change = 0
        for sym in open_symbols:
            for pos, original_cost in self.open_positions[sym]:
                option_roots = pos['OptionRoot'].tolist()
                data_pos = data[data['OptionRoot'].isin(option_roots)]
                mid_prices = [(bid + ask)/2 for bid, ask in zip(data_pos['Bid'].tolist(), data_pos['Ask'].tolist())]
                prev_mid_prices = pos['Prev_Mid'].tolist()

                ## Update mid prices
                pos.drop('Prev_Mid', axis=1)
                pos['Prev_Mid'] = mid_prices

                ## Get change in total cost of trade
                prev_total = round(sum(prev_mid_prices) * 100)
                current_total = round(sum(mid_prices) * 100)
                total_change += current_total - prev_total
                total_change = total_change * int(int(pos['Quantity'].tolist()[0]))

        self.balance += total_change
        self.balance_history.append(self.balance)

    def open_pos(self, data, entry_symbols, exec_date):
        """
        Function: Opens new positions.
        Parameters:
            all_data (Pandas df) --- the options data of that day
            entry_symbols (list) --- the symbols to use to add positions
            exec_date (datetime) --- Date to open position
        """
        if self.profile.strategy == 'earnings': ## Execution based on earnings parameters
            for sym in entry_symbols:
                symbol_df = data.loc[data['UnderlyingSymbol'] == sym]

                for date_range in self.profile.DTE_range[sym]: ## Get DTE range
                    if date_range[0] > exec_date:
                        exp_range = date_range
                        break
                sym_exp = list(dict.fromkeys(symbol_df['Expiration'].tolist()))
                sym_datetime_exp = [datetime.strptime(str_date, '%m/%d/%Y') for str_date in sym_exp]

                ## Get options contract expiration (pos_exp)
                pos_exp = False
                for option_exp in sym_datetime_exp:
                    if exp_range[0] < option_exp < exp_range[1]:
                        pos_exp = option_exp
                if not pos_exp: ## No suitable options expiration date has been found
                    print('No option contracts with expirations between '+str(exp_range[0])+' and '+str(exp_range[1])+'.')

                ## Get exact options contract (the more ATM the better)
                symbol_df = symbol_df.loc[symbol_df['Expiration'] == pos_exp.strftime('%m/%d/%Y')]
                sym_price = symbol_df['UnderlyingPrice'].tolist()[0]
                sym_strikes = list(dict.fromkeys(symbol_df['Strike'].tolist())) ## all strike prices of given exp date
                pos_strike = min(sym_strikes, key=lambda x:abs(x - sym_price)) ## Get strike closest to symbol price

                ## Get position size by creating 'Quantity' column
                strike_df = symbol_df.loc[symbol_df['Strike'] == pos_strike]

                max_cost = self.balance * float(self.profile.exec_params['Position Size'])
                mid_prices = [(bid + ask)/2 for bid, ask in zip(strike_df['Bid'].tolist(), strike_df['Ask'].tolist())]
                strike_df['Prev_Mid'] = mid_prices
                cost_per_trade = round(sum(mid_prices) * 100)
                num_trade = max_cost // cost_per_trade
                strike_df['Quantity'] = num_trade

                ## Saving data
                self.lg.add_open_msg(exec_date, 'Position opened with '+sym+'.', strike_df['OptionRoot'].tolist())
                self.open_positions[sym].append([strike_df, cost_per_trade])

    def review_pos(self, data, open_sym, date):
        """
        Function: Reviews existing positions according to strategy parameters
        Parameters:
            data (Pandas df) --- the options data of the day
            open_sym (list) --- list of all symbols with open positions
            date (datetime) --- current date
        """
        for sym in open_sym:
            for pos, original_cost in self.open_positions[sym]:
                if self.profile.strategy == 'earnings':
                    option_root = pos['OptionRoot'].tolist()
                    data_pos = data[data['OptionRoot'].isin(option_root)]
                    if len(data_pos.index) != 2:
                        self.lg.add_error_msg(date, 'Unable to get contracts with roots ('+str(option_root)+') on option data of current date.')

                    if date == self.profile.exit_dates[sym][0]: ## When exit day is reached
                        self.lg.add_close_msg(date, 'Position with '+sym+' has closed due to exit_date', option_root)
                        self.close_pos(data_pos, sym, pos, original_cost)
                        continue

                    current_cost = round(sum([(bid + ask)/2 for bid, ask in zip(data_pos['Bid'].tolist(), data_pos['Ask'].tolist())]) * 100)
                    if (current_cost - original_cost) / original_cost >= float(self.profile.exec_params['Position Size']):
                        self.lg.add_close_msg(date, 'Profit Target reached', option_root)
                        self.close_pos(data_pos, sym, pos, original_cost)

    def close_pos(self, current_pos, sym, orig_pos, orig_cost):
        ## Update positions
        self.open_positions[sym].remove([orig_pos, orig_cost])
        self.closed_positions[sym].append([current_pos])

        ## Deduct transaction costs
        total_commissions = sum(orig_pos['Quantity'].tolist()) * 1.5
        self.balance -= total_commissions
        self.balance_history[-1] = self.balance ## Originally entered by update_balance

class tools:
    def getTradingDays(pf):
        """
        Function: Get list of trading days from tradingdays.txt
        Returns:
            Timestamp -- [Timestamp('2016-07-06 00:00:00'), Timestamp('2016-07-07 00:00:00'), ...]
            Directory -- ['/2016/201607/20160706_edited.h5', '/2016/201607/20160707_edited.h5', ...]
        """
        ## Get all trading days
        tradingdays = open('tradingdays.txt', 'r')
        tradingdays = [line.split(',') for line in tradingdays.readlines()]

        tradingdays = tradingdays[-600:] ## TEMPORARY
        ## Convert to directory
        tradingdays_dir = [tools.url(day[0][:8]) for day in tradingdays]
        ## Convert to Timestamp
        tradingdays_timestamp = [pd.to_datetime(day[0][:8],format='%Y%m%d') for day in tradingdays]
        return tradingdays_timestamp,tradingdays_dir

    def url(date):
        """
        Function: convert date to file dir of date
        Parameters:
            date (string, must be h5 format) -- '20190104' (Example)
        Returns: '/2019/201901/20190104_edited.h5' (Example)
        """
        url = r'\\'+date[:4]+r'\\'+date[:6]+r'\\'+date+'_edited.h5'
        return url

    def getOptions(format,data_dir,date_dir):
        if format == 'csv':
            return pd.read_csv(r'C:/'+data_dir+date_dir)
        elif format == 'hdf5':
            #print(data_dir+date_dir)
            columns = ['UnderlyingSymbol', 'UnderlyingPrice', 'OptionRoot', 'Type', 'Expiration', 'DataDate', 'Strike', 'Last', 'Bid', 'Ask', 'Volume', 'OpenInterest']
            return pd.read_hdf(data_dir+date_dir, usecols=columns)
