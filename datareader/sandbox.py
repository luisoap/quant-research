import datetime
import numpy as np
import pandas as pd
from pandas.tseries.offsets import BDay
import pdblp
import statsmodels.api as sm
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

con = pdblp.BCon(debug=True, port=8194, timeout=10000)
con.start()
con.debug = False

df_price = con.bdh('IBRA Index', 'PX_LAST', '20000101', pd.to_datetime('today').strftime('%Y%m%d'))