import pandas as pd

year_sandbox = [1986]  # sandbox

for year in year_sandbox:
# for year in range(2012,2020):
    path = r'data\B3\COTAHIST_A'+str(year)+'.TXT'
    path = "D:\Google Drive\Quant Research\data\B3\COTAHIST.A1986"

    data = pd.read_csv(path, encoding='latin-1')

    df = pd.DataFrame()

    df['tipo de registro'] = data[data.columns[0]].str[:2]
    df['data do pregao'] = data[data.columns[0]].str[2:10]
    df['CODBDI'] = data[data.columns[0]].str[10:12]
    df['CODNEG'] = data[data.columns[0]].str[12:24]
    df['TPMERC'] = data[data.columns[0]].str[24:27]
    df['NOMRES'] = data[data.columns[0]].str[27:39]
    df['ESPECI'] = data[data.columns[0]].str[39:49]
    df['PRAZOT'] = data[data.columns[0]].str[49:52]
    df['MODREF'] = data[data.columns[0]].str[52:56]
    df['PREABE'] = data[data.columns[0]].str[56:69]
    df['PREMAX'] = data[data.columns[0]].str[69:82]
    df['PREMIN'] = data[data.columns[0]].str[82:95]
    df['PREMED'] = data[data.columns[0]].str[95:108]
    df['PREULT'] = data[data.columns[0]].str[108:121]
    df['PREOFC'] = data[data.columns[0]].str[121:134]
    df['PREOFV'] = data[data.columns[0]].str[134:147]
    df['TOTNEG'] = data[data.columns[0]].str[147:152]
    df['QUATOT'] = data[data.columns[0]].str[152:170]
    df['VOLTOT'] = data[data.columns[0]].str[170:188]
    df['PREEXE'] = data[data.columns[0]].str[189:201]
    df['INDOPC'] = data[data.columns[0]].str[201]
    df['DATVEN'] = data[data.columns[0]].str[202:210]
    df['FATCOT'] = data[data.columns[0]].str[210:217]
    df['PTOEXE'] = data[data.columns[0]].str[217:230]
    df['CODISI'] = data[data.columns[0]].str[230:242]
    df['DISMES'] = data[data.columns[0]].str[242:245]

    df = df[df['TPMERC']=='010']


