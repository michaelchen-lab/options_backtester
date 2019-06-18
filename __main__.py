from backtester import main

if __name__ == '__main__':

    import time
    start_time = time.time()

    print('Starting process...')
    portfolio = main.start('earnings_config.csv')
    print(portfolio.balance)
    print(portfolio.lg.open_pos_msg)

    print("--- %s seconds ---" % (time.time() - start_time))

## In the current config, the program takes about ~150 secs, with file opening taking about 123 sec
