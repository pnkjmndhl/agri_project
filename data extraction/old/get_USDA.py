import csv
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
import googlemaps
from variables import *


geolocator = Nominatim(user_agent='pdahal')



# Requires API key AIzaSyChD37gN3pUDQoLXB_sW3NcX6MOedEmoQ0

gmaps = googlemaps.Client(key='AIzaSyAkVJMNDBOqmjZG8rNMaS3-t2iag0LgWGk')


# Note: To convert rows from sas to python, (x-1,y)

conv_df = pd.read_csv("../../shortlines_project/input/conversion.csv")
STCG_df1 = pd.ExcelFile("../../shortlines_project/input/SCTG.xlsx").parse("STCC 4-digit").append(
    pd.ExcelFile("../../shortlines_project/input/SCTG.xlsx").parse("STCC 5-digit")).reset_index()[['STCC', 'SCTG']]
STCG_49 = pd.ExcelFile("../../shortlines_project/input/49.xlsx").parse("Sheet1").reset_index()[['STCC', 'SCTG']]
stcg_dict = STCG_df1.transpose().to_dict()
stcg_dict = {y['STCC']: y['SCTG'] for x, y in stcg_dict.iteritems()}
stcg_49_dict = STCG_49.transpose().to_dict()
stcg_49_dict = {y['STCC']: y['SCTG'] for x, y in stcg_49_dict.iteritems()}

commodity_new = "SCTG_CODE"

distance_bins = [50, 100, 200, 400, 600, 800, 1000, 1200]
class1 = [103, 105, 400, 555, 712, 777, 802, 978]

list_49 = ['4904240', '4904250', '4904275', '4918310', '4918311', '4918774', '4930234', '4930247', '4930270',
           '4944108']
ag_prod_list = ['01131', '01132', '01133', '01135', '01136', '01137', '01139', '01144', '01341', '01342', '01343']

files = ["CWS16UM.txt", "WB2017_900_Unmasked.txt", "WB2018_900_Unmasked.txt"]


def f(a, b):
    if a in class1:
        if b in class1:
            return 1
    else:
        return 0

def get_distance_time(o, d):
    try:
        if (np.isnan(o)):
            return (np.nan, np.nan)
    except:
        pass
    try:
        if (np.isnan(d)):
            return (np.nan, np.nan)
    except:
        pass
    if ((o == 0 or d == 0)):
        return (np.nan, np.nan)
    if ((o == (0, 0)) or (d == (0, 0))):
        return (np.nan, np.nan)
    if (o, d) in od_dist_time_dict.keys():
        return od_dist_time_dict[(o, d)]
    print "New Coordinate Found"
    print("{0}->{1}".format(o, d))
    result = gmaps.distance_matrix(o, d)
    try:
        time = result['rows'][0]['elements'][0]['duration']['text']
        dist = float((result['rows'][0]['elements'][0]['distance']['text'].split(" ")[0]).replace(",", "")) / 1.6
    except:
        print ("ERROR")
        od_dist_time_dict[(o, d)] = np.nan, np.nan
        return np.nan, np.nan
    od_dist_time_dict[(o, d)] = time, dist
    return (time, dist)



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



for j in range(len(files)):
    print j
    print files[j]
    file = open("./input/"+files[j]).readlines()
    # file[1]->line1
    d = {}
    for i in range(len(file)):
        d.setdefault('wayser', []).append(file[i][0:6])
        d.setdefault(shortline_dist, []).append(file[i][534:539])
        d.setdefault(total_wt, []).append(file[i][383:390])
        d.setdefault(no_of_cars, []).append(file[i][26:30])
        #d.setdefault('expn', []).append(file[i][350:353])
        d.setdefault('xcar', []).append(file[i][377:383])
        d.setdefault('urev', []).append(file[i][82:91])
        #d.setdefault('zvar', []).append(file[i][50:51])
        d.setdefault(current_rr, []).append(file[i][157:160]) #start rr
        #d.setdefault('trr', []).append(file[i][213:216])
        d.setdefault('stcc', []).append(file[i][310:317])
        d.setdefault('ofip', []).append(file[i][563:568])
        d.setdefault('tfip', []).append(file[i][568:573])
        d.setdefault('trans', []).append(file[i][112:113])
        d.setdefault('ostate', []).append(file[i][539:541])
        d.setdefault('tstate', []).append(file[i][555:557]) #556-557
        #d.setdefault('orrcc', []).append(file[i][780:782]) #556-557
        #d.setdefault('trrcc', []).append(file[i][794:796]) #556-557
        #d.setdefault('trabf', []).append(file[i][779:780]) #556-557
        d.setdefault('ozip', []).append(file[i][717:726]) #556-557
        d.setdefault('tzip', []).append(file[i][726:735]) #556-557
    #
    #
    df = pd.DataFrame.from_dict(d)
    df[shortline_dist] = df[shortline_dist].astype(float)/10
    #df.to_csv(files[j] + "_csv.csv")
    # ag prod list taken from website
    # Transportation Commodity Codes (STCCs): 01131 (barley), 01132 (corn), 01133 (oats), 01135 (rye), 01136 (sorghum grains), 01137 (wheat), 01139 (grain, not elsewhere classified), 01144 (soybeans), 01341 (beans, dry), 01342 (peas, dry), and 01343 (cowpeas, lentils, or lupines).
    ag_prod_df = df[df.stcc.str[0:5].isin(ag_prod_list)]
    ag_prod_df.ofip = ag_prod_df.ofip.astype(int)
    ag_prod_df.tfip = ag_prod_df.tfip.astype(int)
    # ag_prod_df = df[df['stcc'].str.contains(r'^(011)(3|4)')]
    # origin has to be in the US
    #ag_prod_df_outside = ag_prod_df[(ag_prod_df.ofip == 0) | (ag_prod_df.ofip == 0)]
    #ag_prod_df = ag_prod_df[(ag_prod_df.ofip != 0) & (ag_prod_df.tfip != 0) ]
    list_of_origins = ag_prod_df.ofip.unique()
    #
    fert_df = df[df['stcc'].str.contains(r'(^2871)'|r'(^14713)'|r'(^14714)')]


    #
    fert_49 = df[df.stcc.isin(list_49)]
    fert_df = fert_df.append(fert_49, ignore_index=True)
    #
    # destination cannot be places other than the origin of agri products
    fert_df.tfip = fert_df.tfip.astype(int)
    fert_df.ofip = fert_df.ofip.astype(int)
    #fert_df_outside = fert_df[(fert_df.tfip == 0) | (fert_df.ofip == 0) ]
    #fert_df = fert_df[(fert_df.tfip != 0) & (fert_df.ofip != 0)]
    fert_df = fert_df[fert_df.tfip.isin(list_of_origins)]
    #
    all_df = ag_prod_df.append(fert_df, ignore_index=True)
    #all_df_outside = ag_prod_df_outside.append(fert_df_outside, ignore_index=True)
    # assign to original df(for convenience)
    #
    df = all_df
    #
    df[shortline_dist] = df[shortline_dist].astype('float')
    #
    zip_to_coord = np.load(zip_to_coord_loc).item()
    #
    zip_to_coord = {str(x).strip():y for x,y in zip_to_coord.iteritems()}
    #
    #
    df['ozip'] = df['ozip'].str.strip().str.lstrip("0")
    df['tzip'] = df['tzip'].str.strip().str.lstrip("0")

    df[start_coord] = df['ozip'].map(zip_to_coord)
    df[end_coord] = df['tzip'].map(zip_to_coord)
    df = df.reset_index()
    not_found_dict = {}
    found_dict = {}
    #
    df.stcc = df['stcc'].map(get_standardardized_commo)
    df[commodity] = df['stcc'].map(get_commo)
    #
    od_dist_time_dict = np.load(od_dist_time_loc).item()
    #
    df[google_maps_dist] = df.apply(lambda x: get_distance_time(x[start_coord], x[end_coord])[1], axis=1)
    np.save(od_dist_time_loc, np.array(dict(od_dist_time_dict)))
    #
    df.to_csv("./output/"+files[j].split(".")[0] + ".csv")
    del file





