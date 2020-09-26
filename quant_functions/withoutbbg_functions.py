from datetime import datetime, timedelta
import math
import pandas as pd

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


########################################################################################################################
# Backtest
########################################################################################################################

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
