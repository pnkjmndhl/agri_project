import pandas as pd
import numpy as np
from variables import *
import re
import arcpy
from math import pi, sqrt, sin, cos, atan2

#
#


def get_coordinates_to_fips_dict(shp):
    m = "C:/gis/pushpush.shp"
    # if its completely inside, do one thing, if its completely outside, do other.
    boundary_features = "./../shp/tl_2017_us_county.shp"
    # overwrite table
    arcpy.SpatialJoin_analysis(shp, boundary_features, m, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "COMPLETELY_WITHIN")
    _dict_ = {str((f[2], f[1])): f[0] for f in arcpy.da.SearchCursor(m, ['GEOID', "X", "Y"], "")}
    return _dict_



def get_shp_from_coordinates(points):
    #
    sr_g = arcpy.SpatialReference(4326)
    m = "C:/gis/tempo.shp"
    point = arcpy.Point()
    pointGeometryList = []
    for pt in points:
        point.X = pt[0]
        point.Y = pt[1]
        pointGeometry = arcpy.PointGeometry(point).projectAs(sr_g)
        pointGeometryList.append(pointGeometry)
    # arcpy.CopyFeatures_management(pointGeometryList, m)
    #
    #
    arcpy.Delete_management(m)
    arcpy.CopyFeatures_management(pointGeometryList, m)
    arcpy.AddField_management(m, "X", "DOUBLE")
    arcpy.AddField_management(m, "Y", "DOUBLE")
    #
    with arcpy.da.UpdateCursor(m, ["OID@", "X", "Y"]) as cursor:
        for row in cursor:
            row[1] = points[row[0]][0]
            row[2] = points[row[0]][1]
            cursor.updateRow(row)
    return m


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

o_coord = "o_coord"
t_coord = "t_coord"

transfer_pt = "transfer_pt"
transfer_rr = "transfer_rr"

i1 = "i1"
brr1 = "brr1"
i2 = "i2"
brr2 = "brr2"
i3 = "i3"
brr3 = "brr3"
i4 = "i4"
brr4 = "brr4"
i5 = "i5"
brr5 = "brr5"
i6 = "i6"
brr6 = "brr6"
i7 = "i7"
brr7 = "brr7"

files = ["WB2018_900_Unmasked.txt"]

file = open("./input/" + files[0]).readlines()
# file[1]->line1
d = {}

for i in range(len(file)):
    #d.setdefault(recno, []).append(file[i][0:6])
    #
    #d.setdefault(orra, []).append(file[i][317:321])  # start rr
    #
    #d.setdefault(i1, []).append(file[i][157:160])  # start rr
    d.setdefault(brr1, []).append(file[i][160:165])  # start rr
    #d.setdefault(i2, []).append(file[i][165:168])  # start rr
    d.setdefault(brr2, []).append(file[i][168:173])  # start rr
    #d.setdefault(i3, []).append(file[i][173:176])  # start rr
    d.setdefault(brr3, []).append(file[i][176:181])  # start rr
    #d.setdefault(i4, []).append(file[i][181:184])  # start rr
    d.setdefault(brr4, []).append(file[i][184:189])  # start rr
    #d.setdefault(i5, []).append(file[i][189:192])  # start rr
    #d.setdefault(brr5, []).append(file[i][197:200])  # start rr
    #d.setdefault(i6, []).append(file[i][200:205])  # start rr
    #d.setdefault(brr6, []).append(file[i][205:208])  # start rr
    #d.setdefault(i7, []).append(file[i][208:213])  # start rr
    #
    #d.setdefault(trra, []).append(file[i][345:349])
    #
    #
    # d.setdefault('ostate', []).append(file[i][539:541])
    # d.setdefault('tstate', []).append(file[i][555:557]) #556-557
    d.setdefault(orrcc, []).append(file[i][780:782])  # 556-557
    d.setdefault(trrcc, []).append(file[i][794:796])  # 556-557
    # d.setdefault('trabf', []).append(file[i][779:780]) #556-557
    d.setdefault(ozip, []).append(file[i][717:726])  # 556-557
    d.setdefault(tzip, []).append(file[i][726:735])  # 556-557
    #d.setdefault(total_wt, []).append(file[i][390:398])
#
#

df = pd.DataFrame.from_dict(d)
del d
#
#df[total_wt] = df[total_wt].astype(int)
#df[recno] = df[recno].astype(int)
#

df[ozip] = df[ozip].str.strip()
df[tzip] = df[tzip].str.strip()

#df = df[((df[orrcc] != "US") | (df[trrcc] != "US"))]
# #
zip_to_coord = np.load(zip_to_coord_loc).item()
zip_to_coord = {(x[0].strip().lstrip("0"), x[1]): eval(y) for x, y in zip_to_coord.iteritems() if not pd.isnull(y)}

# zip_to_coord = {x: (round(y[0],6), round(y[1],6)) for x,y in zip_to_coord.iteritems()}
# # #

not_found_dict = {}

df[o_coord] = df.apply(lambda x: zip_to_coord[x[ozip].lstrip("0").strip(), x[orrcc]], axis=1)
df[t_coord] = df.apply(lambda x: zip_to_coord[x[tzip].lstrip("0").strip(), x[trrcc]], axis=1)
df.drop([ozip, tzip, orrcc, trrcc], axis=1, inplace=True)
#coord_to_fips
#
list_all_coords = [x for x in list(set(list(df[o_coord].unique()) + list(df[t_coord].unique())))]
list_all_coords = [(y, x) for (x, y) in list_all_coords]

arcpy.env.overwriteOutput = True

# conversion to fips
shp = get_shp_from_coordinates(list_all_coords)
coordinates_to_fips = get_coordinates_to_fips_dict(shp)
#coordinates_to_fips = get_coordinates_to_fips_dict("C:/gis/tempo.shp")

df['OFIPS'] = df[o_coord].astype(str).map(coordinates_to_fips)
df['TFIPS'] = df[t_coord].astype(str).map(coordinates_to_fips)

df = df[(df['OFIPS'] == " ") | (df['TFIPS'] == " ")] #remove everything that doesnot originate or destinate foreign



df1 = df.drop_duplicates().reset_index()
del df




interchanges_dict = pd.read_csv("./input/border_interchanges.csv").transpose().to_dict()
interchanges_dict = {y['Code']: y['coord'] for x, y in interchanges_dict.iteritems()}
interchanges_dict = {x:y for x, y in interchanges_dict.iteritems() if not pd.isnull(y)}

#colnames = [brr1, brr2, brr3, brr4, brr5]
colnames = [brr1, brr2, brr3, brr4]
#colnames = [brr1, brr2, brr3]

for colname in colnames:
    df1[colname + "1"] = df1[colname].str.strip().map(interchanges_dict)

# combine
df1 = df1.fillna("")
# df1["br1"] = df1[brr1] + " " + df1[i1]
# df1["br2"] = df1[brr2] + " " + df1[i2]
# df1["br3"] = df1[brr3] + " " + df1[i3]
# df1["br4"] = df1[brr4] + " " + df1[i4]
# df1["br5"] = df1[brr5] + " " + df1[i5]
# df1["br6"] = df1[brr6] + " " + df1[i6]

#df1['br'] = df1["br1"] + df1['br2'] + df1['br3'] + df1['br4'] + df1['br5']
#df1['br'] = df1["brr1"] + df1['brr2'] + df1['brr3'] + df1['brr4'] + df1['brr5']
df1['br'] = df1["brr11"] + df1['brr21'] + df1['brr31'] + df1['brr41'] #+ df1['brr51']

reg = r'(\([-]*\d+\.\d+,[-]*\d+\.\d+\))'

df1[transfer_pt]= df1['br'].str.extract(reg)


df2 = df1[pd.isnull(df1.transfer_pt)].reset_index()


def haversine(pos1, pos2):
    lat1 = float(pos1[1])
    long1 = float(pos1[0])
    lat2 = float(pos2[1])
    long2 = float(pos2[0])
    degree_to_rad = float(pi / 180.0)
    d_lat = (lat2 - lat1) * degree_to_rad
    d_long = (long2 - long1) * degree_to_rad
    a = pow(sin(d_lat / 2), 2) + cos(lat1 * degree_to_rad) * cos(lat2 * degree_to_rad) * pow(sin(d_long / 2), 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    miles = 3956 * c  # miles
    return miles


def near_yes_no(coord1):
    for coord2 in o_coords:
        if haversine(coord1, coord2) < 50:
            return coord2
    return [0]


#if any origin or destination is closer than 50 miles the range, then use that od
od_dict = {}
o_coords = [eval(y) for x,y in interchanges_dict.iteritems()]

not_found = []
for i in range(len(df2)):
    near_origin = near_yes_no(df2.at[i, o_coord])
    near_destination = near_yes_no(df2.at[i, t_coord])
    if len(near_origin) == 2:
        od_dict[(df2.at[i, o_coord], df2.at[i, t_coord])] = (near_origin, df2.at[i, t_coord]) # origin is changed
    elif len(near_destination) == 2:
        od_dict[(df2.at[i, o_coord], df2.at[i, t_coord])] = (df2.at[i, o_coord], near_destination) # destination is changed
    else:
        pass
        #not_found.append(df2.at[i, recno])


pd.DataFrame(not_found).to_csv("not_found.csv")

df1.dropna(inplace=True)

df2 = df1.copy()
df1 = df2.copy()

df1 = df1[~(((df1.OFIPS == " " ) | (df1.OFIPS == "" ))  & ((df1.TFIPS == " ") | (df1.TFIPS == "")))]
df1 = df1.reset_index()

df1 = df1[['OFIPS', 'TFIPS', o_coord, t_coord, transfer_pt]]

#df1.to_csv("aaaaa.csv")

for i in range(len(df1)):
    origin_is_outside = ((df1.at[i, "OFIPS"] == " ") | (df1.at[i, "OFIPS"] == ""))
    if origin_is_outside:
        od_dict[(df1.at[i, o_coord], df1.at[i, t_coord])] = (eval(df1.at[i, transfer_pt]), df1.at[i, t_coord]) # origin is changed
    else:  # destination is less than origin
        od_dict[(df1.at[i, o_coord], df1.at[i, t_coord])] = (df1.at[i, o_coord], eval(df1.at[i, transfer_pt])) # destination is changed

np.save('./intermediate/od_at_borders_conversion', np.array((od_dict)))
