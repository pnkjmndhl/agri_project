import pandas as pd
import numpy as np
import pandas
import arcpy
from math import pi, sqrt, sin, cos, atan2

orr_i = "int_orra"
oloc_i = "int_oloc"
trr_i = "int_trra"
tloc_i = "int_tloc"

o_coord = 'o_coord'
t_coord = "t_coord"

orra = "ORRA"
trra = "TRRA"

fertilizers_list = ['2871', '28125', '2879']

ag_prod_list = ['01129',
                '01131', '01132', '01133', '01134', '01135', '01136', '01137', '01139',
                '0114',
                '0115',
                '0119',
                '012',
                '013']


def get_stcc_starts_with(_list_):
    _str_ = ""
    for _l_ in _list_:
        _str_ = _str_ + "^(" + _l_ + ")|"
    return _str_[:-1]


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


def stcc_to_cmdty(stcc, aarcar):
    value = 12
    if int(stcc[0:5]) == 1132:  # corn
        value = 2
    elif int(stcc[0:5]) == 1137:  # grain
        value = 3
    elif int(stcc[0:5]) == 1144:  # soybean
        value = 4
    elif int(stcc[0:2]) == 1:  # if doesnot fall under all three up
        value = 1
    elif int(stcc[0:2]) == 11:
        value = 5
    elif int(stcc[0:2]) in [10, 14, 29, 32, 40, 6]:
        value = 6
    elif int(stcc[0:2]) in [20, 24, 26, 33, 34]:
        value = 7
    elif int(stcc[0:2]) == 28:
        value = 8
    elif int(stcc[0:3]) == 371:
        value = 10
    elif int(stcc[0:2]) in [42, 44, 45, 46, 11]:
        value = 11
    elif aarcar == 'T':
        value = 9
    return value


sctg_to_rncg = {1: 13, 2: 14, 3: 15, 4: 16, 8: 17}


def get_usda_cmdty(rncg, usda):
    if usda in [1, 2]:
        return sctg_to_rncg[rncg]
    else:
        return rncg


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
        if haversine(eval(coord1), eval(coord2)) < 50:
            return 1
    return 0


def get_od(o, d):
    if (eval(o), eval(d)) in coord_overwrite_dict:
        o, d = coord_overwrite_dict[(eval(o), eval(d))]
        return str(o), str(d)
    else:
        return (o, d)


arcpy.env.overwriteOutput = True


for i in range(1, 3):
    df = pd.DataFrame.from_csv("./output/mode_split_pred1_0_" + str(i) + ".csv")

    df.STCC = df.STCC.apply(lambda x: str(x).zfill(7))
    df.STCC = df.STCC.astype(str)

    coord_overwrite_dict = pd.DataFrame.from_csv("input/border_interchanges.csv").transpose().to_dict()
    coord_overwrite_dict = {x: y['coord'] for x, y in coord_overwrite_dict.iteritems() if not pd.isnull(y['coord'])}

    coord_overwrite_dict = {x: eval(y) for x, y in coord_overwrite_dict.iteritems()}
    # coord_overwrite_dict = {x: str((y[1], y[0])) for x,y in coord_overwrite_dict.iteritems() }
    coord_overwrite_dict = {x: str((y[0], y[1])) for x, y in coord_overwrite_dict.iteritems()}


    # adjusting ORR and TRR
    # all_aar_csv = r'../railnet/input/allAARCode.csv'
    # orra_to_orr = pd.read_csv(all_aar_csv)
    # orra_to_orr_dict = dict(zip(orra_to_orr.AARCode, orra_to_orr.ABBR))
    # orra_to_orr_dict = {str(y):x for x,y in orra_to_orr_dict.iteritems()}

    # adjust
    df[orr_i] = df[orr_i].astype(str)
    df[trr_i] = df[trr_i].astype(str)


    df[orr_i].replace('0', np.nan, inplace=True)
    df[trr_i].replace('0', np.nan, inplace=True)
    #
    # df[orr_i] = df[orr_i].map(orra_to_orr_dict)
    # df[trr_i] = df[trr_i].map(orra_to_orr_dict)
    #
    #
    #
    df[oloc_i].replace("     ", np.nan, inplace=True)
    df[tloc_i].replace("     ", np.nan, inplace=True)

    df1 = df.copy()
    df = df1.copy()

    # newly adopted
    (df['o_coord1'], df[orra]) = np.where(~pd.isnull(df[oloc_i]),
                                          (df[oloc_i].str.strip().map(coord_overwrite_dict), df[orr_i]),
                                          (df[o_coord], df[orra]))
    (df['t_coord1'], df[trra]) = np.where(~pd.isnull(df[tloc_i]),
                                          (df[tloc_i].str.strip().map(coord_overwrite_dict), df[trr_i]),
                                          (df[t_coord], df[trra]))

    # df.to_csv("apple23.csv")
    # conversion to fips
    list_all_coords = list(set(
        list(df[o_coord].unique()) + list(df.t_coord.unique()) + list(df.o_coord1.unique()) + list(df.t_coord1.unique())))
    list_all_coords.remove(np.nan)
    list_all_coords = [eval(x) for x in list_all_coords]
    #
    #
    coordinates_to_fips = convert_coordinates_to_fips(list_all_coords)
    #
    # test
    # list_all_coords = list(set(list(list(df.o_coord1.unique()) + list(df.t_coord1.unique()))))
    # list_all_coords.remove(np.nan)
    # list_all_coords = [eval(x) for x in list_all_coords]


    pd.DataFrame(list(set({x: y for x, y in coordinates_to_fips.iteritems() if y == " "}.keys())))

    df['OFIPS'] = df[o_coord].map(coordinates_to_fips)
    df['TFIPS'] = df[t_coord].map(coordinates_to_fips)
    #
    df['OFIPS1'] = df["o_coord1"].map(coordinates_to_fips)
    df['TFIPS1'] = df["t_coord1"].map(coordinates_to_fips)
    #
    #
    # df.to_csv("apple231.csv")
    #

    # origin is inside us for agricultural products
    condition0 = (df.STCC.str.contains(get_stcc_starts_with(ag_prod_list))) & (df.OFIPS != " ")
    condition00 = (df.STCC.str.contains(get_stcc_starts_with(ag_prod_list)))

    df['usda'] = np.where(condition0, 1, 0)  # agri

    # termination is always US for fertilizers
    condition1 = df.STCC.str.contains(get_stcc_starts_with(fertilizers_list)) & (df.TFIPS != " ")
    condition11 = df.STCC.str.contains(get_stcc_starts_with(fertilizers_list))
    # condition2_fips = (df.TFIPS.isin(df[df.usda == 1].OFIPS.unique()))

    o_coords = (df[df.usda == 1].o_coord.unique())

    c1_true = "c1_true"
    df[c1_true] = np.where(condition1, 1, 0)

    # should be inside the us
    condition2 = df.apply(lambda x: near_yes_no(x.t_coord) if (x.c1_true == 1) else 0,
                          axis=1)  # condition 1 (a fertilizer)
    # condition2 = (df.t_coord.isin(df[df.usda == 1].o_coord.unique()))

    # summary
    print ("Summary:")
    print ("All Agricultural Products: {0} tons, nos: {1}".format(df[condition00].wt.sum(), sum(condition00)))
    print ("All Fertilizers: {0} tons, nos: {1}".format(df[condition11].wt.sum(), sum(condition11)))
    print("US Agricultural Products: {0}, nos: {1}".format(df[condition0].wt.sum(), sum(condition0)))
    print("US Fertilizers: {0}, nos: {1}".format(df[condition1 & condition2].wt.sum(), sum(condition1)))
    #
    # df['usda_fips'] = np.where(condition1 & condition2_fips, 2, df['usda'])
    df['usda'] = np.where(condition1 & condition2, 2, df['usda'])
    #
    #
    df['rncg'] = df.apply(lambda x: stcc_to_cmdty(x["STCC"], x["AARCAR"]), axis=1)
    df['rncg1'] = df.apply(lambda x: get_usda_cmdty(x["rncg"], x["usda"]), axis=1)
    df.to_csv("all_cws_modeshift_int_" + str(i) + ".csv")
    #
    #







    ########################################################################################################

    df_n = df.copy()
    # #combined (all inside)
    # df_n = df_n[["ORRA", "TRRA", "nos", "wt", "lost_ton", "rncg1", "OFIPS1", "TFIPS1", "OFIPS", "TFIPS"]]
    # df_1 = df_n.copy()
    #
    # df_1 = df_1[((df_1.OFIPS !=" ") & (df_1.TFIPS !=" ") & (df_1.OFIPS !="") & (df_1.TFIPS !=""))]
    # #df_1 = df_1[((df_1.OFIPS1 !=" ") & (df_1.TFIPS1 !=" ") & (df_1.OFIPS1 !="") & (df_1.TFIPS1 !=""))]
    #
    # df_1 = df_1[["ORRA", "TRRA", "nos", "wt", 'lost_ton', "rncg1", "OFIPS", "TFIPS"]]
    # df_1.columns = ["ORRA", "TRRA", "XCAR", "XTON", "lost_ton", "RNCG", "OFIP", "TFIP"]
    #
    # df_1[["ORRA", "TRRA", "XCAR", "XTON", "RNCG", "OFIP", "TFIP"]].to_csv("./output/output/base_in_" + str(i) + ".csv")
    # #
    # #
    # #df1['XTON'] = df1['XTON'] - df1['lost_ton']
    # df_1['XTON'] = np.where(df_1['RNCG'] > 12, df_1['XTON']- df_1['lost_ton'], df_1['XTON']) #mode shift only if greater than 12
    # df_1 = df_1[["ORRA", "TRRA", "XCAR", "XTON", "RNCG", "OFIP", "TFIP"]]
    # df_1 = df_1[["ORRA", "TRRA", "XCAR", "XTON", "RNCG", "OFIP", "TFIP"]]
    # #
    # df_1.to_csv("./output/output/s1" + str(i) + "_in.csv")

    #
    #
    # al
    df_1 = df_n.copy()
    #
    # unusuable records


    df_1[['OFIPS1', 'TFIPS1']] = df_1[['OFIPS1', 'TFIPS1']].replace({'': np.nan, 0: np.nan, " ": np.nan})
    df_1[df_1['OFIPS1'].isnull() | df_1['TFIPS1'].isnull()].to_csv("discarded_records.csv")
    df_1 = df_1.dropna(subset=['OFIPS1', 'TFIPS1'])

    df_1 = df_1[((df_1.OFIPS1 != " ") & (df_1.TFIPS1 != " ") & (df_1.OFIPS1 != "") & (df_1.TFIPS1 != ""))]
    #
    df_1 = df_1[["ORRA", "TRRA", "nos", "wt", 'lost_ton', "rncg1", "OFIPS1", "TFIPS1"]]
    df_1.columns = ["ORRA", "TRRA", "XCAR", "XTON", "lost_ton", "RNCG", "OFIP", "TFIP"]

    df_1[["ORRA", "TRRA", "XCAR", "XTON", "RNCG", "OFIP", "TFIP"]].to_csv("./output/output/base_" + str(i) + "_all.csv")
    #

    #
    # df1['XTON'] = df1['XTON'] - df1['lost_ton']
    df_1['XTON'] = np.where(df_1['RNCG'] > 12, df_1['XTON'] - df_1['lost_ton'],
                            df_1['XTON'])  # mode shift only if greater than 12
    df_1 = df_1[["ORRA", "TRRA", "XCAR", "XTON", "RNCG", "OFIP", "TFIP"]]
    df_1 = df_1[["ORRA", "TRRA", "XCAR", "XTON", "RNCG", "OFIP", "TFIP"]]
    #
    df_1.to_csv("./output/output/s1" + str(i) + "_all.csv")
    #


    # #only
    # df_1 = df_n.copy()
    # #
    # df_1 = df_1[~((df_1.OFIPS !=" ") & (df_1.TFIPS !=" ") & (df_1.OFIPS !="") & (df_1.TFIPS !=""))]
    # df_1 = df_1[((df_1.OFIPS1 !=" ") & (df_1.TFIPS1 !=" ") & (df_1.OFIPS1 !="") & (df_1.TFIPS1 !=""))]
    #
    #
    # df_1 = df_1[["ORRA", "TRRA", "nos", "wt", 'lost_ton', "rncg1", "OFIPS1", "TFIPS1"]]
    # df_1.columns = ["ORRA", "TRRA", "XCAR", "XTON", "lost_ton", "RNCG", "OFIP", "TFIP"]
    # #
    # df_1[["ORRA", "TRRA", "XCAR", "XTON", "RNCG", "OFIP", "TFIP"]].to_csv("./output/output/base_" + str(i) + "_only.csv")
    # #
    # #
    # #df1['XTON'] = df1['XTON'] - df1['lost_ton']
    # df_1['XTON'] = np.where(df_1['RNCG'] > 12, df_1['XTON']- df_1['lost_ton'], df_1['XTON']) #mode shift only if greater than 12
    # df_1 = df_1[["ORRA", "TRRA", "XCAR", "XTON", "RNCG", "OFIP", "TFIP"]]
    # df_1 = df_1[["ORRA", "TRRA", "XCAR", "XTON", "RNCG", "OFIP", "TFIP"]]
    # #
    # df_1.to_csv("./output/output/s1" + str(i) + "_only.csv")
