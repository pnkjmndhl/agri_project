import csv
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
import googlemaps
from variables import *
import arcpy


arcpy.env.overwriteOutput = True

def convert_coordinates_to_fips(points):
    sr_g = arcpy.SpatialReference(4326)
    m1 = "C:/gis/pushpush.shp"
    m = "C:/gis/tempo.shp"
    point = arcpy.Point()
    pointGeometryList = []
    for pt in points:
        point.X = pt[1]
        point.Y = pt[0]
        pointGeometry = arcpy.PointGeometry(point).projectAs(sr_g)
        pointGeometryList.append(pointGeometry)
    # arcpy.CopyFeatures_management(pointGeometryList, m)
    arcpy.Delete_management(m)
    arcpy.CopyFeatures_management(pointGeometryList, m)
    arcpy.AddField_management(m, "X", "DOUBLE")
    arcpy.AddField_management(m, "Y", "DOUBLE")
    with arcpy.da.UpdateCursor(m, ["OID@", "X", "Y"]) as cursor:
        for row in cursor:
            row[1] = points[row[0]][0]
            row[2] = points[row[0]][1]
            cursor.updateRow(row)
    #
    boundary_features = "./../shp/tl_2017_us_county.shp"
    # overwrite table
    arcpy.SpatialJoin_analysis(m, boundary_features, m1, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "COMPLETELY_WITHIN")
    _dict_ = {str((f[1], f[2])): f[0] for f in arcpy.da.SearchCursor(m1, ['GEOID', "X", "Y"], "")}
    return _dict_





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

o_coord = "o_coord"
t_coord = "t_coord"


df = pd.read_csv("./intermediate/base_raw.csv")

#df.drop([recno, ofip, tfip], inplace=True, axis=1)



coord_overwrite_dict = pd.DataFrame.from_csv("input/border_interchanges.csv").transpose().to_dict()
coord_overwrite_dict = {x: y['coord'] for x,y in coord_overwrite_dict.iteritems() if not pd.isnull(y['coord'])}

coord_overwrite_dict = {x: eval(y) for x,y in coord_overwrite_dict.iteritems() }
#coord_overwrite_dict = {x: str((y[1], y[0])) for x,y in coord_overwrite_dict.iteritems() }
coord_overwrite_dict = {x: str((y[0], y[1])) for x,y in coord_overwrite_dict.iteritems() }


#adjust
df[orr_i].replace(0, np.nan, inplace=True)
df[trr_i].replace(0, np.nan, inplace=True)
df[oloc_i].replace("     ", np.nan, inplace=True)
df[tloc_i].replace("     ", np.nan, inplace=True)

df1= df.copy()
df = df1.copy()



#newly adopted
(df['o_coord1'], df[orra]) = np.where(~pd.isnull(df[oloc_i]), (df[oloc_i].str.strip().map(coord_overwrite_dict), df[orr_i]), (df[o_coord], df[orra]) )
(df['t_coord1'], df[trra]) = np.where(~pd.isnull(df[tloc_i]), (df[tloc_i].str.strip().map(coord_overwrite_dict), df[trr_i]), (df[t_coord], df[trra]) )

#df.to_csv("apple23.csv")
# conversion to fips
list_all_coords = list(set(list(df[o_coord].unique()) + list(df.t_coord.unique()) + list(df.o_coord1.unique()) + list(df.t_coord1.unique())))
list_all_coords.remove(np.nan)
list_all_coords = [eval(x) for x in list_all_coords]
#
#
coordinates_to_fips = convert_coordinates_to_fips(list_all_coords)
#
#test
list_all_coords = list(set(list(list(df.o_coord1.unique()) + list(df.t_coord1.unique()))))
list_all_coords.remove(np.nan)
list_all_coords = [eval(x) for x in list_all_coords]




pd.DataFrame(list(set({x:y for x,y in coordinates_to_fips.iteritems() if y == " "}.keys())))



df['OFIPS'] = df[o_coord].map(coordinates_to_fips)
df['TFIPS'] = df[t_coord].map(coordinates_to_fips)
#
df['OFIPS1'] = df["o_coord1"].map(coordinates_to_fips)
df['TFIPS1'] = df["t_coord1"].map(coordinates_to_fips)

df_1 = df.copy()

df_1[['OFIPS1', 'TFIPS1']] = df_1[['OFIPS1', 'TFIPS1']].replace({'':np.nan, 0:np.nan, " ": np.nan})


discarded_df = df_1[df_1['OFIPS1'].isnull() | df_1['TFIPS1'].isnull()]

discarded_df.to_csv("discarded_records.csv")


#create a remaining df



recno_ids = [str(x) for x in list(discarded_df["RECNO"].unique())]


all_lines = []
with open ('input/original/WB2018_900_UNMASKED.PWB', 'rt') as myfile:    # Open lorem.txt for reading text.
    for myline in myfile:                   # For each line in the file,
        all_lines.append(myline)

my_lines = [y for y in all_lines if y[0:6] in recno_ids]



text_file = "WB2018_900_UNMASKED.REM"
with open(text_file, 'w') as f:
    for item in my_lines:
        f.write("%s" % item)




