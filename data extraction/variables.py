import pandas as pd
#
class1 = [103, 105, 400, 555, 712, 777, 802, 978]
distance_bins = {800: 5, 1200: 6, 200: 2, 400: 3, 50: 1, 600: 4}
use_rate_bins = {100: 1, 1000: 2, 2000: 3, 8000: 4, 25000: 5, 50000: 6, 100000: 7}
unique_distances = {1: 1}
#
start_coord = "o_coord"
end_coord = "t_coord"
#
# final table columns
no_of_cars = "nos"
wt_per_car = "wtpcr"
commodity = "cmdty"
online_dist = "dist"
#
all_dist = "dist1"
start_rr = "rr1"
current_rr = "rr"
forwarded_rr = "rr2"
origin = 'origin'
destination = 'destination'
transfer_1 = "o1"
transfer_2 = "d1"
total_wt = 'wt'
inout = 'inout'
commodity_new = 'commo_new'
use_rate = "use_rate"
#
shortline_dist = "_d_"
google_maps_dist = "distance"
unique_ods = "od"
#
od_dist_time_loc = "./intermediate/od_dist_time_dict.npy"
name_to_coord_loc = "./intermediate/name_to_coord.npy"
zip_to_coord_loc = './intermediate/zip_to_coord.npy'
#
summary1_csv = "./intermediate/summary1.csv"
summary2_csv = "./intermediate/summary2.csv"
summary3_csv = "./intermediate/summary3.csv"
#
conv_df_loc = "../../shortlines_project/input/conversion.csv"
SCTG_xlsx_loc = "../../shortlines_project/input/SCTG.xlsx"
SP_49 = "../../shortlines_project/input/49.xlsx"
#
# # constants
#
truck_speed = [45, 45, 45, 45]  # mph
rail_speed = 20  # mph
base = 0
compare = [1, 2, 3]
min_cost_pcar = 325
#
base_indexes = [8, 4, 0]
s1_indexes = [9, 5, 1]
s2_indexes = [10, 6, 2]
s3_indexes = [11, 7, 3]
#
type_conversion_dict = {"Dry van": 0, "Hopper": 1, "Tanker": 2, "Dry Van": 0, "Tanker ": 2}
#
rail_rate_df = pd.read_csv("./intermediate/RATES.csv").loc[:, 'SCTG':'RTM']
truck_rate_df = pd.ExcelFile("../../shortlines_project/input/Rate Table per ton.xlsx").parse("Sheet1")
truck_rate_df.drop(['Truck Configuration'], inplace=True, axis=1)
#
commodty_distr_df = pd.ExcelFile("../../shortlines_project/input/Trailer type.xlsx").parse("Sheet1")
commodty_distr_df.drop(['Description'], inplace=True, axis=1)
#
# # truck_rate_df = truck_rate_df.transpose().reset_index()
#
# # select the columns from start to end
model1_df = pd.ExcelFile('../../shortlines_project/input/Modeparms(compare).xlsx').parse("Shpmt Freight Rate Models").loc[0:37, 'SCTG':'Group']
model2_df = pd.ExcelFile('../../shortlines_project/input/Modeparms(compare).xlsx').parse("22-Mkt Share Frt-Trans time").loc[0:3,
            'SCTG':'Group']
#
cmdty_list1 = ['"{:02}"'.format(int(x)) for x in list(model1_df['SCTG'].unique()) if str(x) != 'nan']
cmdty_list2 = ['"{:02}"'.format(int(x)) for x in list(model2_df['SCTG'].unique()) if str(x) != 'nan']
