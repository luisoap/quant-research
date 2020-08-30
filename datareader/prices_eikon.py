import os
import eikon as ek  # the Eikon Python wrapper package
import pandas as pd
from datetime import date
from datetime import datetime, timedelta
import math

# os.chdir(r'C:\Users\luiso\OneDrive - Insper\pacotes_python\data_reader_eikon')

ek.set_app_key('187de016e213433ab116ff348d8c911a0529cab0')

today = date.today()
today = today.strftime("%Y-%m-%d")

start = '1994-01-01'
end = pd.to_datetime('today').strftime('%Y-%m-%d')


def recover_prices(list_tickers, start_date, end_date, field = ['CLOSE'], interval='daily', adjusted='adjusted'):

    d_start = datetime.strptime(start_date, '%Y-%m-%d')
    d_end = datetime.strptime(end_date, '%Y-%m-%d')

    q_rec = (d_end - d_start).days/2000

    prices = pd.DataFrame()

    list_df_prices = []
    list_tickers_success = []

    p = 0
    P = len(list_tickers)

    for ticker in list_tickers:
        list_df = []
        s = 0
        for i in range(math.ceil(q_rec)):
            try:
                prices_aux = ek.get_timeseries([ticker], start_date=d_start + (i * timedelta(2000)), end_date=d_start + ((i + 1) * timedelta(2000)), fields=field, interval=interval, corax=adjusted, normalize=True)
                prices_aux.set_index('Date', inplace=True)
                list_df.append(prices_aux)
            except:
                print(ticker, "wasn't listed yet in ", d_start+((i+1)*timedelta(2000)))
            else:
                print("successfully got data from ", ticker, " from ", d_start+(i*timedelta(2000)))
                s = 1
        if s == 1:
            list_tickers_success.append(ticker)
            prices = pd.concat(list_df)
            prices = prices[~prices.index.duplicated()]
            list_df_prices.append(prices)
        p = p + 1
        print(100 * p/P, "%")

    df_prices = pd.DataFrame(index=list_df_prices[0].index)

    for df in list_df_prices[1:]:
        if df.index[0] < df_prices.index[0]:
            df_prices = pd.DataFrame(index=df.index)

    for ticker, df in zip(list_tickers_success, list_df_prices):
        df_prices[ticker] =  df['Value']

    df_prices.to_csv('prices.csv')

    return df_prices

prices = recover_prices(['VVAR3.SA'], start, end,['CLOSE', 'VOLUME'])