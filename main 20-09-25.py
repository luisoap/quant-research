import quant_functions
import pandas as pd

# ----------------------------------------------------------------------------------------------------------------------
# Parameters
# ----------------------------------------------------------------------------------------------------------------------
recover_data = False
index = ['IBRA Index', 'IBOV Index']
# index = ['IBOV Index']
start = 6

# ----------------------------------------------------------------------------------------------------------------------
# Using functions that need Bloomberg
# ----------------------------------------------------------------------------------------------------------------------
if recover_data:
    for indx in index:
        df_composition, list_composition = quant_functions.index_composition_h(indx, start)
        df_composition.to_csv(r'data\composition ' + indx + '.csv')
        df_prices = quant_functions.prices_bbg(list_composition, start)
        df_prices.columns = df_prices.columns.get_level_values(0)
        df_prices.to_csv(r'data\prices ' + indx + '.csv')
else:
    for indx in index:
        df_prices = pd.read_csv(r'data\prices ' + indx + '.csv', index_col=0)
        df_prices.index = pd.to_datetime(df_prices.index)
        df_composition = pd.read_csv(r'data\composition ' + indx + '.csv', index_col=0)
        df_composition.index = pd.to_datetime(df_composition.index)
        for ind in df_composition.index:
            list_aux = []
            for x in df_composition.loc[ind]:
                if not pd.isna(x):
                    list_aux.append(x)
                else:
                    list_aux.append(None)
            df_composition.loc[ind] = list_aux

# ----------------------------------------------------------------------------------------------------------------------
# Computing the strategy
# ----------------------------------------------------------------------------------------------------------------------
quant_functions.momentum_equities(df_prices, period_lookback=12, period_reversal=1, n=15)
dates = quant_functions.rebalancing_dates(df_prices, 1, 4)
quant_functions.backtest(strategy='momentum', reb_dt=dates, composition=df_composition, prices=df_prices, period_lookback=6, period_reversal=1, n=15)

