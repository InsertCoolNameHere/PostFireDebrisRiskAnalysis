import csv

# CONVERTS THE WEIBULL PARAMETERS CSV FILE INTO A DICTIONARY TO BE USED INSIDE ARCGIS

import pandas as pd
cdf_csv_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\Vegetation\\CDFParameters.csv"

cdf_df = pd.read_csv(cdf_csv_path, index_col=False, header=0)

cdf_dict = {}

print(cdf_df.columns)

for i in range(len(cdf_df)):
    class_id = int(cdf_df.iloc[i,0])
    lamb = float(cdf_df.iloc[i,2])
    kap = float(cdf_df.iloc[i,3])
    cdf_dict[class_id] = {"lamb":lamb, "kap":kap}

print(cdf_dict)

