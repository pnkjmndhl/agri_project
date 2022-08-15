import csv
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
import googlemaps
from variables import *
from math import pi, sqrt, sin, cos, atan2

recno = "RECNO"
xton = "XTON"
xcar = "XCAR"
orr = "ORR"
orra = "ORRA"
trr = "TRR"
trra = "TRRA"
stcc = "STCC"
ofip = "OFIP"
tfip = "TFIP"
aarcar = "AARCAR"
ozip = "OZIP"
tzip = "TZIP"
rncg = "cmdty_12"
orrcc = "ORR_CC"
trrcc = "TRR_CC"
rail_dist = "dist_rr"


orr_i = "int_orra"
oloc_i =  "int_oloc"
trr_i =  "int_trra"
tloc_i = "int_tloc"

o_splc = "OSPLC"
t_splc = "TSPLC"


geolocator = Nominatim(user_agent='pdahal')

# Requires API key AIzaSyChD37gN3pUDQoLXB_sW3NcX6MOedEmoQ0

#gmaps = googlemaps.Client(key='AIzaSyAkVJMNDBOqmjZG8rNMaS3-t2iag0LgWGk') #fusion.pankaj
gmaps = googlemaps.Client(key='AIzaSyBzcfAgCVHfVJQFyHVlAlN6z_dSk3OodSU') #pnkjmndhl

# Note: To convert rows from sas to python, (x-1,y)

conv_df = pd.read_csv("../../shortlines_project/input/conversion.csv")
STCG_df1 = pd.ExcelFile("../../shortlines_project/input/SCTG.xlsx").parse("STCC 4-digit").append(
    pd.ExcelFile("../../shortlines_project/input/SCTG.xlsx").parse("STCC 5-digit")).reset_index()[['STCC', 'SCTG']]
STCG_49 = pd.ExcelFile("../../shortlines_project/input/49.xlsx").parse("Sheet1").reset_index()[['STCC', 'SCTG']]
stcg_dict = STCG_df1.transpose().to_dict()
stcg_dict = {y['STCC']: y['SCTG'] for x, y in stcg_dict.iteritems() if y['SCTG'] != '""'}

stcg_49_dict = STCG_49.transpose().to_dict()
stcg_49_dict = {y['STCC']: y['SCTG'] for x, y in stcg_49_dict.iteritems()}

commodity_new = "SCTG_CODE"

class1 = [103, 105, 400, 555, 712, 777, 802, 978]



files = ["WB2018_900_Pass1.txt"]


def f(a, b):
    if a in class1:
        if b in class1:
            return 1
    else:
        return 0

#(o,d ) = ((31.1862, -85.0034),(30.195424, -85.66458)) #this should work

def get_distance_time(o, d):
    if (o, d) in od_dist_time_dict.keys():
        return od_dist_time_dict[(o, d)]
    if ((o == 0 or d == 0)):
        return np.nan
    if ((o == (0, 0)) or (d == (0, 0))):
        return np.nan
    print "New Coordinate Found"
    print("{0}->{1}".format(o, d))
    try:
        result = gmaps.distance_matrix(o, d)
        #time = result['rows'][0]['elements'][0]['duration']['text']
        dist = float((result['rows'][0]['elements'][0]['distance']['text'].split(" ")[0]).replace(",", "")) / 1.6
        od_dist_time_dict[(o, d)] = dist #save only distance
        return dist
    except:
        print ("ERROR")
        return np.nan


def get_commo(value):
    if pd.isnull(value):
        return np.nan
    value4 = '"' + value[0:4] + '"'
    value5 = '"' + value[0:5] + '"'
    if value4 in stcg_dict:
        dumm = stcg_dict[value4]
        found_dict[value] = dumm
        return dumm
    elif value5 in stcg_dict:
        dumm = stcg_dict[value5]
        found_dict[value] = dumm
        return dumm
    else:
        value = '"' + value + '"'
        if value in stcg_49_dict:
            dumm = stcg_49_dict[value]
            found_dict[value] = dumm
            return dumm
        else:
            not_found_dict[value] = [value4, value5]


j = 0
file = open("./input/" + files[j]).readlines()
# file[1]->line1
d = {}
for i in range(len(file)):
    d.setdefault(recno, []).append(file[i][0:6])
    d.setdefault(rail_dist, []).append(file[i][534:539])
    d.setdefault(total_wt, []).append(file[i][390:398])
    #
    #
    d.setdefault(no_of_cars, []).append(file[i][377:383])  # use expanded
    #
    d.setdefault(orra, []).append(file[i][317:321])  # start rr
    #
    d.setdefault(trra, []).append(file[i][345:349])
    d.setdefault(stcc, []).append(file[i][310:317])
    d.setdefault(ofip, []).append(file[i][563:568])
    d.setdefault(tfip, []).append(file[i][568:573])
    d.setdefault(aarcar, []).append(file[i][285:286])
    #
    d.setdefault(orrcc, []).append(file[i][780:782])  # 556-557
    d.setdefault(trrcc, []).append(file[i][794:796])  # 556-557
    # d.setdefault('trabf', []).append(file[i][779:780]) #556-557
    d.setdefault(ozip, []).append(file[i][717:726])  # 556-557
    d.setdefault(tzip, []).append(file[i][726:735])  # 556-557
    #
    d.setdefault(orr_i, []).append(file[i][587:590])  # 556-557
    d.setdefault(oloc_i, []).append(file[i][590:595])  # 556-557
    d.setdefault(tloc_i, []).append(file[i][595:600])  # 556-557
    d.setdefault(trr_i, []).append(file[i][600:603])  # 556-557
    #
    d.setdefault(o_splc, []).append(file[i][298:304])  # 556-557
    d.setdefault(t_splc, []).append(file[i][304:310])  # 556-557
#
#

df = pd.DataFrame.from_dict(d)
#
del d#
#
df[rail_dist] = df[rail_dist].astype(float) / 10

df[total_wt] = df[total_wt].astype(int)
df[no_of_cars] = df[no_of_cars].astype(int)
df[ozip] = df[ozip].str.strip()
df[tzip] = df[tzip].str.strip()

df[aarcar] = np.where(df[aarcar] != "T", "X", df[aarcar])

# #
zip_to_coord = np.load(zip_to_coord_loc).item()
zip_to_coord = {(x[0].strip().lstrip("0"), x[1]): eval(y) for x, y in zip_to_coord.iteritems() if not pd.isnull(y)}

##
splc_to_coord = np.load("intermediate/splc_to_coord.npy").item()
splc_to_coord = {(str(x[0]), x[1]): eval(y) for x, y in splc_to_coord.iteritems()}

splc_coord = {x:z for (x,y),z in splc_to_coord.iteritems()}



not_found_dict = {}
found_dict = {}

df[orra] = df[orra].str.strip()
df[trra] = df[trra].str.strip()
#
df[ozip] = df[ozip].str.lstrip("0").str.strip()
df[tzip] = df[tzip].str.lstrip("0").str.strip()
#


zip_splc_coord_dict = {}
def get_coordinates(zip, splc, orrcc, orr):
    if (zip, splc, orrcc, orr) in zip_splc_coord_dict:
        return zip_splc_coord_dict[(zip, splc, orrcc, orr)]
    elif (splc, orr) in splc_to_coord:
        #found_dict[(splc, orr)] = (zip, orrcc)
        zip_splc_coord_dict[(zip, splc, orrcc, orr)] = splc_to_coord[(splc, orr)]
        return splc_to_coord[(splc, orr)]
    elif splc in splc_coord:
        #found_dict[splc] = (zip, orrcc)
        zip_splc_coord_dict[(zip, splc, orrcc, orr)] = splc_coord[splc]
        return splc_coord[splc]
    else:
        not_found_dict[(splc, orr)] = (zip, orrcc)
        return zip_to_coord[(zip, orrcc)]


df[start_coord] = df.apply(lambda x: get_coordinates(x[ozip], x[o_splc], x[orrcc], x[orra]), axis=1)
df[end_coord] = df.apply(lambda x: get_coordinates(x[tzip], x[t_splc], x[trrcc], x[trra]), axis=1)


# df["start_coord_1"] = df.apply(lambda x: zip_to_coord[(x[ozip], x[orrcc])], axis=1)
# df["end_coord_1"] = df.apply(lambda x: zip_to_coord[(x[tzip], x[trrcc])], axis=1)



# def haversine(pos1, pos2):
#     lat1 = float(pos1[1])
#     long1 = float(pos1[0])
#     lat2 = float(pos2[1])
#     long2 = float(pos2[0])
#     degree_to_rad = float(pi / 180.0)
#     d_lat = (lat2 - lat1) * degree_to_rad
#     d_long = (long2 - long1) * degree_to_rad
#     a = pow(sin(d_lat / 2), 2) + cos(lat1 * degree_to_rad) * cos(lat2 * degree_to_rad) * pow(sin(d_long / 2), 2)
#     c = 2 * atan2(sqrt(a), sqrt(1 - a))
#     miles = 3956 * c  # miles
#     return miles



# df["oo_dist"] = df.apply(lambda x: haversine(x[start_coord], x["start_coord_1"]), axis=1)
# df["dd_dist"] = df.apply(lambda x: haversine(x[end_coord], x["end_coord_1"]), axis=1)


df.drop([orrcc, trrcc], axis=1, inplace=True)

found_dict = {}

df[commodity] = df[stcc].map(get_commo)
# #
od_dist_time_dict = np.load(od_dist_time_loc).item()
# #
#df[google_maps_dist] = df.apply(lambda x: get_distance_time(x[start_coord], x[end_coord])[1], axis=1)
#
#od_dist_time_dict = {x:y for x,y in od_dist_time_dict.iteritems() if type(y) == type(1.1)}
#
df[google_maps_dist] = ("(" + df[start_coord].astype(str) + ", " + df[end_coord].astype(str) + ")").map(od_dist_time_dict)
df[google_maps_dist] = df.apply(lambda x: get_distance_time(x[start_coord], x[end_coord]) if pd.isnull(x[google_maps_dist]) else x[google_maps_dist], axis=1)
#
#
#
#od_dist_time_dict = {x:y for x,y in od_dist_time_dict.iteritems() if not pd.isnull(y[0])}

np.save(od_dist_time_loc, np.array(dict(od_dist_time_dict)))
#
# convert coordinates to fips
df.to_csv("./intermediate/base_raw.csv")  # with recno
df.drop([recno, ofip, tfip], inplace=True, axis=1)

data0 = pd.pivot_table(df, values=[total_wt, no_of_cars],
                       index=[commodity, stcc, orra, trra, rail_dist, start_coord, end_coord, google_maps_dist, aarcar, orr_i, oloc_i, tloc_i, trr_i],
                       aggfunc={total_wt: np.sum, no_of_cars: np.sum}).reset_index()

#correct distance

circuity_threshold = 3
loop_threshold_range = 0.2
very_small_distance = 200 # miles


rail_dist = "dist_rr"

#data0.to_csv("ddd.csv")

#exceptions
condition1 = (data0[rail_dist] >= very_small_distance) & (data0[rail_dist] > data0[google_maps_dist]*circuity_threshold)
condition2 = (data0[rail_dist] >= very_small_distance) & (((data0[rail_dist] - 2*data0[google_maps_dist])/data0[rail_dist]).abs() <= loop_threshold_range)

print ("circuitous adjusted: {0}".format(condition1.sum()))
print ("Loop adjusted: {0}".format(condition2.sum()))


(data0[rail_dist], data0[google_maps_dist]) = np.where(condition1, ((data0[rail_dist] + data0[google_maps_dist])/2, ((data0[rail_dist] + data0[google_maps_dist])/2)),
                                                             (data0[rail_dist], data0[google_maps_dist]))

data0[rail_dist] = np.where(condition2,(data0[rail_dist])/2, data0[rail_dist])
data0.to_csv("./intermediate/base.csv")  # with recno

# add commodities
pd.DataFrame(not_found_dict).transpose().to_csv("intermediate/not_found_dict.csv")

