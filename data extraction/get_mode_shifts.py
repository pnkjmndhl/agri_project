import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from variables import *


def get_utilities(cost, comm, _dist_, _gdist_):
    if comm in cmdty_list1:
        b0 = float(model1_df[model1_df.SCTG == int(comm.replace('"', ""))]['b0'])
        br = float(model1_df[model1_df.SCTG == int(comm.replace('"', ""))]['br'])
        gen_b0 = model1_df.loc[0:0, :]['b0'][0]
        gen_br = model1_df.loc[0:0, :]['br'][0]
        Ur = cost[0] * (gen_br + br)
        Ut = [(gen_b0 + b0) + x * (br + gen_br) for x in cost[1:]]
    elif comm in cmdty_list2:
        b0 = float(model2_df[model2_df.SCTG == int(comm.replace('"', ""))]['b0'])
        bC = float(model2_df[model2_df.SCTG == int(comm.replace('"', ""))]['bC'])
        bT = float(model2_df[model2_df.SCTG == int(comm.replace('"', ""))]['bT'])
        Ur = bC * cost[0] + bT * float(_dist_) / rail_speed  # distance in miles divided by speed in mph
        _truck_speed_ = [y for (x, y) in enumerate(truck_speed) if x in [base, _compare_]]
        cost_transit_time = zip(cost[1:], [float(_gdist_) / x for x in _truck_speed_])
        Ut = [b0 + bC * x + bT * y for x, y in cost_transit_time]  # distance in miles divided by speed in mph
    else:
        return 1, [1]*(len(cost)-1)
    return Ur, Ut


def get_rail_rate(_dist_, _comm_):
    # interpolate
    rl_rate_p_tm1 = rail_rate_df[(rail_rate_df['SCTG'].astype(str) == _comm_)][['DGROUP', 'RTM']]
    if _dist_ < 50:
        _dist = 50
    elif _dist_ > 1200:
        _dist_ = 1200
    if _dist_ in rl_rate_p_tm1.DGROUP.tolist():
        rl_rate_p_tm = float(rl_rate_p_tm1[rl_rate_p_tm1.DGROUP == _dist_]["RTM"])
    elif len(rl_rate_p_tm1) >1:
        # interpolate (also some actual DGROUP donot have any values for RTM
        rl_rate_p_tm1 = rl_rate_p_tm1.append({'DGROUP': _dist_, 'RTM': np.nan}, ignore_index=True)
        rl_rate_p_tm1 = rl_rate_p_tm1.sort_values(by='DGROUP').reset_index()[['DGROUP', 'RTM']]
        rl_rate_p_tm1 = rl_rate_p_tm1.interpolate(method='polynomial', axis=0, order=1).ffill().bfill() #linear interpolation
        rl_rate_p_tm = float(rl_rate_p_tm1[rl_rate_p_tm1['DGROUP'] == _dist_]['RTM'])
    else: #if only one rate present for that commodity, return that rate
        return float(rl_rate_p_tm1["RTM"])
    return rl_rate_p_tm


def get_truck_rates(_dist_, _compare_):
    colnames = list(truck_rate_df.columns)
    colnames.remove("#")
    if _dist_ > max(colnames):
        _dist_ = max(colnames)
    #
    if _dist_ not in colnames:
        colnames.append(_dist_)
        all_sorted = sorted(colnames)
        dist_index = all_sorted.index(_dist_)
        _dists_ = [all_sorted[dist_index - 1]] + [all_sorted[dist_index + 1]]
        tr_rate = truck_rate_df[_dists_].reset_index().transpose().to_dict()
        tr_rate = {y['index']: [y[_dists_[0]], y[_dists_[1]]] for x, y in tr_rate.iteritems()}
        tr_rate = {x: float(_dist_ - _dists_[0]) / (_dists_[1] - _dists_[0]) * (y[1] - y[0]) + y[0] for x, y in
                   tr_rate.iteritems()}
    else:
        tr_rate = truck_rate_df[_dist_].reset_index().transpose().to_dict()
        tr_rate = {y['index']: y[_dist_] for x, y in tr_rate.iteritems()}
    #
    if _compare_ == 1:
        indexes = s1_indexes
    elif _compare_ == 2:
        indexes = s2_indexes
    else:
        indexes = s3_indexes
    indexes_all = base_indexes + indexes
    truck_rate_pton_const = [tr_rate[x] for x in indexes_all]
    #
    return truck_rate_pton_const


#commodty, dist, rr, nos, ann_tonnage, gdist = '"02"', 174.375, 62, 3, 330, 3524
def get_share(commodty, dist, ann_tonnage, gdist):
    #print ("commodty: {0} rail_dist: {1} wt: {2} gdist: {3}".format(commodty, dist,ann_tonnage, gdist))
    if commodty == '""':
        return 0,0,0,0,0,0,0,0,0,0,0
    #print commodty
    global _compare_
    rl_rate_p_tm = get_rail_rate(dist, commodty)
    truck_rate_pton_const_all = get_truck_rates(gdist, _compare_)
    ttype_int = int((commodty_distr_df[commodty_distr_df.SCTG == int(commodty[1:-1])]["Trailer type"]).map(type_conversion_dict))
    truck_rate_pton_const = [truck_rate_pton_const_all[ttype_int]] + [truck_rate_pton_const_all[ttype_int + 3]]
    #
    cost = [rl_rate_p_tm * ann_tonnage * dist, truck_rate_pton_const[0] * ann_tonnage,
            truck_rate_pton_const[1] * ann_tonnage]
    # calculation
    # if cost[0] <= min_cost_pcar * nos:
    #     cost[0] = min_cost_pcar * nos
    Ur, Ut = get_utilities(cost, commodty, dist, gdist)
    # print ("{0}.{1}".format(Ur, Ut))
    pr = [1 - 1.0 / (1 + np.exp(Ur - x)) for x in Ut]
    return cost[0], cost[1], cost[2], Ur, Ut[0], Ut[1], pr[0], pr[1], rl_rate_p_tm, truck_rate_pton_const[0], \
           truck_rate_pton_const[1]




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



def main():
    for compare__ in compare:
        global _compare_
        _compare_ = compare__
        # drop any tonnages less than 75 tons/carload
        data_df = pd.read_csv("./intermediate/base.csv")
        data_df['costr'], data_df['cost0'], data_df['cost1'], data_df['Ur'], data_df['Ut0'], data_df['Ut1'], data_df[
            'pr0'], \
        data_df['pr1'], data_df['rl_rate_ptm'], data_df['truck_rate1'], data_df['truck_rate2'] = zip(
            *data_df.apply(lambda x: get_share(x[commodity], x[rail_dist], x[total_wt], x[google_maps_dist]), axis=1))
        # data_df['tr_addi']= data_df['pt1']-data_df['pt0']
        data_df['percent_lost'] = (1 - data_df['pr1'] / data_df['pr0'])
        data_df['percent_lost'].fillna(0, inplace=True)
        data_df['lost_ton'] = data_df[total_wt] * data_df['percent_lost']
        data_df['lost_rev'] = data_df['rl_rate_ptm'] * data_df['lost_ton'] * data_df[google_maps_dist]
        data_df['pcent_div'] = data_df['lost_ton'] / data_df[total_wt]
        data_df.to_csv("./output/mode_split_{0}_{1}_{2}.csv".format("pred1", base, _compare_))


if __name__ == '__main__':
    _compare_ = -99
    main()
