from datetime import datetime, timedelta
import math
import pandas as pd
import pandas_datareader.data as pdr
from pandas.tseries.offsets import BDay
import pdblp

con = pdblp.BCon(debug=True, port=8194, timeout=10000)
con.start()
con.debug = False

def yahoo_adj_close(stocks_list, start, debug=True):
    """
    Recover the adjusted closing price of a list of stocks
    :param stocks_list: List. List of stocks you want to recover information
    :param start: Integer. Number of previous years you want to recover data
    :param debug: Bool. If True, shows the progress of the data recovery
    :return: DataFrame with the adjusted closing prices
    """
    today = datetime.now().strftime("%Y-%m-%d")  # getting today's date
    start = (datetime.now() - timedelta(start*365)).strftime("%Y-%m-%d")
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

########################################################################################################################
# Data

def index_composition_h(index, start):
    """
    This is a function that recovers from Bloomberg the index composition of an Index of your choice
    :param index: The index you want to recover. Example: 'IBRA Index'
    :param start: How many years, before today you want to recover the data. Integer. Example: 2
    :return: Returns a DataFrame with the composition and a list with the union of the composition in the period.
    """
    # Starting and ending day
    end_dt = pd.to_datetime('today').strftime('%Y%m%d')
    start_dt = (pd.to_datetime('today') - timedelta(start*365)).strftime('%Y%m%d')

    # Defining the calendar
    df_price = con.bdh(index, 'PX_LAST', start_dt, end_dt)
    df_price.columns = ['price']
    calendar = [df_price.index[0]]
    month = df_price.index[0].month
    for ind in df_price.index[1:]:
        if ind.month != month:
            calendar.append(ind)
            month = ind.month

    # Recovering data and storing in a DataFrame
    comp_list = []
    for d in calendar:
        print('recovered composition of date', d)
        comp = con.bulkref(index, 'INDX_MWEIGHT_HIST', [('END_DATE_OVERRIDE', d.strftime('%Y%m%d'))])
        comp = list(comp[comp['name'] == 'Index Member']['value'])
        comp = [x[:-2]+'BZ Equity' for x in comp]
        comp_list.append(comp)
    df_composition = pd.DataFrame(comp_list)
    df_composition.index = calendar

    # Finding the union of equities in the Index..
    df_compostion_all = {}
    for d in df_composition.index:
        if not df_compostion_all:
            df_compostion_all = set(df_composition.loc[d])
        else:
            df_compostion_all = df_compostion_all.union(set(df_composition.loc[d]))
    df_compostion_all = list(df_compostion_all)
    df_compostion_all = [x for x in df_compostion_all if x]
    return df_composition, df_compostion_all

def prices_bbg(equities, start):
    """
    Recover the adjusted prices for the select equities
    :param equities: List of equities
    :param start: How many years, before today you want to recover the data. Integer. Example: 2
    :return: DataFrame with the prices for the selected equities.
    """
    # Starting and ending day
    end_dt = pd.to_datetime('today').strftime('%Y%m%d')
    start_dt = (pd.to_datetime('today') - timedelta(start*365)).strftime('%Y%m%d')

    # Recovering the prices for the selected equities
    try:
        df_price = con.bdh(equities, 'PX_LAST', start_dt, end_dt)
    except:
        print('failed to recover prices for the indicated list')
    else:
        print('recovered prices for the indicated list')
    return df_price

########################################################################################################################
# Strategies

"""
Authors: Luis Otávio Abrahão Pinto
"""
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


def momentum_equities(df, period_lookback=12, period_reversal=1, n=15):
    """
    Function to select equities based on momentum factor
    :param df: DataFrame with the prices
    :param period_lookback: Lookback period
    :param period_reversal: Reversal period
    :param n: Number os equities to be included
    :return: Returns a list with n equities ranked based on momentum
    """
    period_lookback = 21 * period_lookback
    period_reversal = 21 * period_reversal
    return_lookback = df.pct_change(period_lookback)
    return_lookback = return_lookback + 1
    return_reversal = df.pct_change(period_reversal)
    return_reversal = return_reversal + 1
    return_momentum = return_lookback / return_reversal - 1
    return_momentum = return_momentum.iloc[-1]
    list_equities = return_momentum.sort_values(ascending=False).index[:n]
    return list_equities


def book_market(tickers, path, n=15, debug=True):
    results = pd.DataFrame()
    i = 0
    for tck in tickers:
        url = 'https://www.fundamentus.com.br/detalhes.php?papel=' + tck
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(executable_path=path, options=chrome_options)
        driver.get(url)
        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        pvp = soup.find_all('table')[2].find_all('tr')[2].find_all('td')[2].text
        pvp_value = soup.find_all('table')[2].find_all('tr')[2].find_all('td')[3].text
        # Saving the results in a dataframe
        results.loc[i, 'Ticker'] = tck
        results.loc[i, 'P/VP'] = pvp[1:]
        results.loc[i, 'P/VP Value'] = float(pvp_value.replace(',', '.'))
        if float(pvp_value.replace(',', '.')) != 0:
            results.loc[i, 'Book to Market'] = 1/float(pvp_value.replace(',', '.'))
        if debug:
            print(results)
        driver.quit()
        i = i + 1
    results = list(results.sort_values(by='Book to Market', ascending=False)['Ticker'])[:n]
    return results

########################################################################################################################
# Backtest
def rebalancing_dates(df_price, rebalancing_frequency, rebalancing_period):


    # defing the first day of the week
    calendar = df_price.index
    df_calendar = pd.DataFrame(index=calendar)
    df_calendar['day_week'] = df_calendar.index.weekday
    df_calendar['selected'] = 0
    mondays = list(df_price[df_price.index.weekday == 0].index)
    tuesdays = list(df_price[df_price.index.weekday == 1].index)
    wednesday = list(df_price[df_price.index.weekday == 2].index)
    thursdays = list(df_price[df_price.index.weekday == 3].index)
    fridays = list(df_price[df_price.index.weekday == 4].index)
    selected_days = [mondays[0]]
    distance_days = [7, 8, 9, 10, 11]
    for dt0 in mondays[1:]:
        succesful = False
        while not succesful:
            if (dt0 - selected_days[-1]).days == distance_days[0]:
                selected_days.append(dt0)
                distance_days = [7, 8, 9, 10, 11]
                succesful = True
            elif selected_days[-1] + timedelta(distance_days[1]) in tuesdays:
                dt = selected_days[-1] + timedelta(distance_days[1])
                selected_days.append(dt)
                distance_days = [6, 7, 8, 9, 10]
            elif selected_days[-1] + timedelta(distance_days[2]) in wednesday:
                dt = selected_days[-1] + timedelta(distance_days[2])
                selected_days.append(dt)
                distance_days = [5, 6, 7, 8, 9]
            elif selected_days[-1] + timedelta(distance_days[3]) in thursdays:
                dt = selected_days[-1] + timedelta(distance_days[3])
                selected_days.append(dt)
                distance_days = [4, 5, 6, 7, 8]
            elif selected_days[-1] + timedelta(distance_days[4]) in fridays:
                dt = selected_days[-1] + timedelta(distance_days[4])
                selected_days.append(dt)
                distance_days = [3, 4, 5, 6, 7]
            else:
                print('week with no trading')
    df_calendar.loc[selected_days, 'selected'] = 1
    # defining which week of the month this date corresponds
    df_calendar.loc[selected_days[0], 'week'] = math.ceil(selected_days[0].day/7)
    for d0, d1 in zip(selected_days[:-1], selected_days[1:]):
        if d1.month != d0.month:
            df_calendar.loc[d1, 'week'] = 1
        else:
            df_calendar.loc[d1, 'week'] = df_calendar.loc[d0, 'week'] + 1
    # getting the dates of rebalancing according to the chosen frequency
    reb_dt_aux = df_calendar.loc[df_calendar.loc[:,'week'] == rebalancing_period].index
    reb_dt = [reb_dt_aux[0]]
    for d in reb_dt_aux[1:]:
        if d.month < reb_dt[-1].month:
            comp_d = d.month + 12
        else:
            comp_d = d.month
        if comp_d - reb_dt[-1].month == rebalancing_frequency:
            reb_dt.append(d)
    return reb_dt

def backtest(strategy, reb_dt, composition, prices, period_lookback=12, period_reversal=1, n=15):
    # strategy = 'momentum'
    # reb_dt = dates.copy()
    # composition = df_compostion.copy()
    # period_lookback = 12
    # period_reversal = 1
    # n = 15
    # prices = df_price.copy()
    prices.columns = prices.columns.get_level_values(0)

    reb_dt = reb_dt[11:]
    df_returns = pd.DataFrame(index=reb_dt[1:], columns=['Return', 'Index'])
    for dt0, dt1 in zip(reb_dt[:-1], reb_dt[1:]):
        if dt1 == reb_dt[1]:
            df_returns.loc[dt1, 'Return'] = 0
            df_returns.loc[dt1, 'Index'] = 1
        else:
            ret = 0
            for stk in port:
                ret_aux = (prices.loc[dt1, stk]/prices.loc[dt0, stk] - 1)
                if math.isnan(ret_aux):
                    end_pos = prices[stk].last_valid_index()
                    ret_aux = (prices.loc[end_pos, stk]/prices.loc[dt0, stk] - 1)
                else:
                    pass
                ret = ret + (1/len(port)) * ret_aux
            df_returns.loc[dt1, 'Return'] = ret
            df_returns.loc[dt1, 'Index'] = df_returns.loc[dt0, 'Index'] * (1 + ret)
        if strategy == 'momentum':
                comp = composition[(composition.index.year == dt1.year) & (composition.index.month == dt1.month)]
                comp = [x for x in comp.values[0] if x is not None]
                prices_aux = prices.loc[:dt0, comp]
                port = momentum_equities(prices_aux, period_lookback=period_lookback, period_reversal=period_reversal, n=n)
                print(dt1)
                print(port)
    return df_returns


# Example of usage
index = 'IBRA Index'
start = 6

df_compostion, list_composition = index_composition_h(index, start)
df_compostion.to_csv(r'data\ibra_composition.csv')

df_price = prices_bbg(list_composition, start)
df_price.to_csv(r'data\ibra_prices.csv')

dates = rebalancing_dates(df_price, 1, 4)

backtest_results = backtest('momentum', dates, df_compostion, df_price, 12, 1, 15)
# next function, create a backtest function that receives composition, prices and rebalancing dates as input. output return series and statistics