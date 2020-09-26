from datetime import datetime, timedelta
import pandas as pd
import pdblp

con = pdblp.BCon(debug=True, port=8194, timeout=10000)
con.start()
con.debug = False

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
