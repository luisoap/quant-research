import datetime as dt
import pandas as pd
import pandas_datareader.data as pdr

def yahoo_adj_close(stocks_list, start, debug=True):
    """
    Recover the adjusted closing price of a list of stocks
    :param stocks_list: List. List of stocks you want to recover information
    :param start: Integer. Number of previous years you want to recover data
    :param debug: Bool. If True, shows the progress of the data recovery
    :return: DataFrame with the adjusted closing prices
    """
    today = dt.datetime.now().strftime("%Y-%m-%d")  # getting today's date
    start = (dt.datetime.now() - dt.timedelta(start*365)).strftime("%Y-%m-%d")
    prices = pd.DataFrame()
    for stk in stocks_list:
        try:
            prices[stk] = pdr.DataReader(stk + '.SA', data_source='yahoo', start=start, end=today)['Adj Close']
        except:
            if debug:
                print("Error recovering data from ", stk)
        else:
            if debug:
                print("Successfully recovered data from ", stk)
    # filling nan
    for stk in prices.columns:
        ini_pos = prices[stk].first_valid_index()
        end_pos = prices[stk].last_valid_index()
        if ini_pos != prices.index[0]:
            begin_list = list(prices.loc[:ini_pos, stk].iloc[:-1])
        else:
            begin_list = []
        if end_pos != prices.index[-1]:
            end_list = list(prices.loc[end_pos:, stk].iloc[1:])
        else:
            end_list = []
        middle_list = list(prices.loc[ini_pos:end_pos, stk].fillna(method='ffill'))
        replacement_list = begin_list + middle_list + end_list
        prices.loc[:, stk] = replacement_list
    return prices