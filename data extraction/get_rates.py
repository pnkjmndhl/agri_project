import csv
import pandas as pd
import numpy as np
import arcpy
from variables import *


def f(a, b):
    if a in class1:
        if b in class1:
            return 1
    else:
        return 0


def get_dist_bin(val):
    val = float(val)
    diff_list = {abs(x - val):y for x,y in distance_bins.iteritems()}
    min_val_index = diff_list[min(diff_list.keys())]
    return {value: key for key,value in distance_bins.iteritems() if value == min_val_index}.values()[0]


def get_commo(value):
    if pd.isnull(value):
        return np.nan
    value4 = '"' + value[0:4] + '"'
    value5 = '"' + value[0:5] + '"'
    try:  # search value4, if not found, use value5
        dumm = stcg_dict[value4]
        # print dumm
        if dumm == '""':  # if dumm is empty
            raise ValueError('Bro, did not find')
        found_dict[value] = dumm
        return dumm
    except:
        try:
            # print value5
            dumm = stcg_dict[value5]
            found_dict[value] = dumm
            return dumm
        except:
            value = '"' + value + '"'
            # if not found in both use the 49 dictionary
            try:
                dumm = stcg_49_dict[value]
                found_dict[value] = dumm
                return dumm
            except:
                not_found_dict[value] = [value4, value5]


def get_standardardized_commo(value):
    value = str(value)
    try:
        value = value.strip()
        value = str(value)
    except:
        pass
    try:
        a = int(value)
    except:
        value = live_dict[value.strip().upper()][1]
        if (value == 0) or (value == "NAN") or (pd.isnull(value)):
            return np.nan
    if value[0] == '"':  # removing apostrophies
        value = value[1:-1]
    if len(value) == 6:  # if 6 digits then add 0 in front
        value = '0' + value
    return value


file = open("./input/WB2018_900_Unmasked.txt").readlines()

d = {}
for i in range(len(file)):
    d.setdefault('wayser', []).append(file[i][0:6])
    d.setdefault('tdis', []).append(file[i][534:539])
    d.setdefault('uton', []).append(file[i][383:390]) # in tons
    d.setdefault('ucar', []).append(file[i][26:30])
    d.setdefault('zvar', []).append(file[i][50:51])
    d.setdefault('orr', []).append(file[i][157:160])
    d.setdefault('trr', []).append(file[i][213:216])
    d.setdefault('stcc', []).append(file[i][310:317])
    d.setdefault('urev', []).append(file[i][82:91])

df = pd.DataFrame.from_dict(d)



# next level map

conv_df = pd.read_csv(conv_df_loc)
STCG_df1 = pd.ExcelFile(SCTG_xlsx_loc).parse("STCC 4-digit").append(
    pd.ExcelFile(SCTG_xlsx_loc).parse("STCC 5-digit")).reset_index()[['STCC', 'SCTG']]
STCG_49 = pd.ExcelFile(SP_49).parse("Sheet1").reset_index()[['STCC', 'SCTG']]
stcg_dict = STCG_df1.transpose().to_dict()
stcg_dict = {y['STCC']: y['SCTG'] for x, y in stcg_dict.iteritems()}
stcg_49_dict = STCG_49.transpose().to_dict()
stcg_49_dict = {y['STCC']: y['SCTG'] for x, y in stcg_49_dict.iteritems()}

df = df.reset_index()

not_found_dict = {}
found_dict = {}
commodity_new = 'SCTG'
df[commodity_new] = df["stcc"].map(get_commo)

#all values were used./
df1 = df[(df[commodity_new] == '"02"') | (df[commodity_new] == '"03"') | (df[commodity_new] == '"23"')]

#
df['tdis'] = df.tdis.astype('float') / 10
df['RTM'] = df.urev.astype('float') / (df.tdis.astype('float') * df.uton.astype('float'))

# conditions
df['SUM'] = df.apply(lambda x: f(x.orr, x.trr), axis=1)

#df = df[(df.RTM < 0.5) & (df.SUM == 0)]



# put to bins
df['DGROUP'] = df['tdis'].map(get_dist_bin)

#rates
df['COUNT'] = 1
table = pd.pivot_table(df, values=['RTM', 'COUNT'] , index=['SCTG', 'DGROUP'], aggfunc={'RTM':np.mean, 'COUNT': np.sum}).reset_index()
table['RTM_V'] = pd.pivot_table(df, values=['RTM', 'COUNT'] , index=['SCTG', 'DGROUP'], aggfunc={'RTM':np.var, 'COUNT': np.sum}).reset_index()['RTM']

pd.DataFrame.from_dict(not_found_dict).transpose().to_csv('./intermediate/not_found.csv')
table.to_csv('./intermediate/RATES.csv')


