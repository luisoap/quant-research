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

