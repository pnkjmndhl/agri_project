import pandas as pd
import numpy as np
import arcpy


arcpy.env.overwriteOutput = True  # overwrite files if its already present

states_shp = "../shp/tl_2017_us_states.shp"
temp = "in_memory/T1"
temp1 = "../shp/agri.shp"
temp2 = "../shp/fert.shp"


def get_coordinates_of_centroid(area_shp):
    dumm_dict = {}
    arcpy.FeatureToPoint_management(area_shp, temp,"CENTROID")
    with arcpy.da.UpdateCursor(temp, ["STATE_FP", "SHAPE@XY"]) as cursor:
        for row in cursor:
            dumm_dict[row[0]] = (row[1][0], row[1][1])
    dumm_dict[52] = (np.nan, np.nan) #removing american samoa
    return dumm_dict
    


data_df = pd.read_csv("./output/WB2018_900_Unmasked.csv")
fips_to_coord_dict = get_coordinates_of_centroid(states_shp)


data_df['ostate'] = data_df['ofip'].astype(int)/1000
data_df['ostate'] = data_df['ostate'].round(0)
data_df['dstate'] = data_df['tfip'].astype(int)/1000
data_df['dstate'] = data_df['dstate'].round(0)
data_df['uton'] = data_df['uton'].astype(int)

data_summary1 = data_df[(data_df.SCTG_CODE == '"02"') | (data_df.SCTG_CODE == '"03"') ]
data_summary2 = data_df[~((data_df.SCTG_CODE == '"02"') | (data_df.SCTG_CODE == '"03"')) ]





data_summary = pd.pivot_table(data_summary1, values='uton', index=['ostate', 'dstate'], aggfunc=np.sum).reset_index()
data_summary = data_summary[(data_summary.ostate !=0) & (data_summary.dstate !=0)]
data_summary['start_X'] = data_summary['ostate'].map(lambda x: fips_to_coord_dict[x][0])
data_summary['start_Y'] = data_summary['ostate'].map(lambda x: fips_to_coord_dict[x][1])
data_summary['end_X'] = data_summary['dstate'].map(lambda x: fips_to_coord_dict[x][0])
data_summary['end_Y'] = data_summary['dstate'].map(lambda x: fips_to_coord_dict[x][1])
data_summary.to_csv("./intermediate/agri_XY.csv")
arcpy.XYToLine_management ("./intermediate/agri_XY.csv", temp1, "start_X", "start_Y", "end_X", "end_Y", "", "uton", arcpy.SpatialReference(4326))



data_summary = pd.pivot_table(data_summary2, values='uton', index=['ostate', 'dstate'], aggfunc=np.sum).reset_index()
data_summary = data_summary[(data_summary.ostate !=0) & (data_summary.dstate !=0)]
data_summary['start_X'] = data_summary['ostate'].map(lambda x: fips_to_coord_dict[x][0])
data_summary['start_Y'] = data_summary['ostate'].map(lambda x: fips_to_coord_dict[x][1])
data_summary['end_X'] = data_summary['dstate'].map(lambda x: fips_to_coord_dict[x][0])
data_summary['end_Y'] = data_summary['dstate'].map(lambda x: fips_to_coord_dict[x][1])
data_summary.to_csv("./intermediate/fert_XY.csv")
arcpy.XYToLine_management ("./intermediate/fert_XY.csv", temp2, "start_X", "start_Y", "end_X", "end_Y", "", "uton", arcpy.SpatialReference(4326))


