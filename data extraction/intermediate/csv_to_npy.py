import numpy as np
import pandas as pd

df = pd.read_csv("zip_to_coordinates_all.csv")

df_dict = df.transpose().to_dict()
df_dict = {(y['zip'],y['country']): y['coord'] for x,y in df_dict.iteritems()}

np.save('zip_to_coord.npy', np.array(dict(df_dict)))



df = pd.read_csv("splc_to_coordinates_all.csv")

df_dict = df.transpose().to_dict()
df_dict = {(y['SPLC'],y['RR']): y['coord'] for x,y in df_dict.iteritems()}

np.save('splc_to_coord.npy', np.array(dict(df_dict)))