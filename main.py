import datetime as dt
import pandas as pd
import numpy as np
import math
import pandas_datareader.data as pdr
# my packages
import strategies
import datareader

#path = r'C:\Users\luiso\chromedriver.exe'

# This file has the daily composition of the Ibovespa since 2000
stocks = pd.read_csv('./data/ibov_composition.csv',index_col=0)

# This file has the daily prices of all stocks that participated the Ibovespa
prices = pd.read_csv('./data/prices_ibov_composition.csv')
prices.drop('FIELD', axis=1, inplace=True)
prices.set_index('TRADE_DATE', inplace=True)

# Using Yahoo Finance to recover the most recent data
stocks_all_list = []
for ind0 in stocks.index:
    for ind1 in stocks.loc[ind0]:
        if not ind1 in stocks_all_list:
            stocks_all_list.append(ind1)

stocks_list = stocks.iloc[-1]
stocks_list = [x[:-3] for x in stocks_list]
stocks_all_list = [x[:-3] for x in stocks_all_list if str(x) != 'nan']

prices = datareader.yahoo_adj_close(stocks_all_list, 3)

momentum = strategies.momentum_equities(prices, 6, 1, 15)
bm = strategies.book_market(stocks_list, path, 15)

########################################################################################################################
# Sending email

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP

port = 465  # For SSL
sender_email = "luisoap.email@gmail.com"
password = '1020ABCDEF'
#recipients = ["luisoap2@gmail.com",
#              "leonardosiqueira86@gmail.com",
#              "vhalexs@gmail.com",
#              "adrecaluz@gmail.com",
#              "valentinaccc@icloud.com",
#              "guilhermeleitepaiva@gmail.com"]
recipients = ["cefasgarciapereira@gmail.com"]
emaillist = [elem.strip().split(',') for elem in recipients]

msg = MIMEMultipart()
msg['Subject'] = "Value and Momentum - " + dt.datetime.now().strftime("%d/%m/%Y")
msg['From'] = "luisoap.email@gmail.com"

intro = "Value and momentum portfolios. :\n\n"

changes = "Momentum: "

for stock in momentum:
    changes = changes + stock + " "

changes = changes + "\n\nValue: "

for stock in bm:
    changes = changes + stock + " "

changes = changes + "\n\nEsta não é uma recomendação de investimentos."

part1 = MIMEText(intro, 'plain')
part3 = MIMEText(changes, 'plain')

msg.attach(part1)
msg.attach(part3)

# Send email here

# Create a secure SSL context

context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
    server.login("luisoap.email@gmail.com", password)
    print('connected')
    server.sendmail(sender_email, emaillist, msg.as_string())
    print('email sent')
