import math

import pandas as pd
import os
import csv

DS_path = "/s/lattice-101/a/nobackup/galileo/sustain/arcgis/resampled_attributes/DStorm/combined_DS.csv"
thi15_path = "/s/lattice-101/a/nobackup/galileo/sustain/arcgis/resampled_attributes/THI15/thi15.csv"
risk_path = "/s/lattice-101/a/nobackup/galileo/sustain/arcgis/resampled_attributes/risk"


numer = math.log10(9) + 3.63
ds_dict = {}
th_dict = {}
# READ ALL X1
print("DStorm....")

ind=0

cdf_df = pd.read_csv(DS_path, index_col=False, header=0)

for i in range(len(cdf_df)):
    grid_key = cdf_df.iloc[i,0]
    x1 = float(cdf_df.iloc[i,1])
    count = float(cdf_df.iloc[i,2])

    ds_dict[grid_key] = {"DStorm": x1, "count": count}

    if i%100000 == 0:
        print(i)
print("THI15....")
# READ ALL X2

cdf_df = pd.read_csv(thi15_path, index_col=False, header=0)

for i in range(len(cdf_df)):
    grid_key = cdf_df.iloc[i,0]
    x2 = float(cdf_df.iloc[i,1])

    th_dict[grid_key] = {"THI15": x2}
    if i%100000 == 0:
        print(i)

print("...........................COMBINING.................................")
risk_dict = {}
for gg in ds_dict:
    if gg in th_dict:
        x1 = ds_dict[gg]["DStorm"]
        x2 = th_dict[gg]["THI15"]

        tval = 0

        if x1<=x2:
            tval = 1
        risk_dict[gg] = {"RISK": tval}

csv_columns = ["GridCode", "RISK"]
csv_file = os.path.join(risk_path, "risk.csv")
try:
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for key in risk_dict:
            d = risk_dict[key]
            data = {"GridCode": key, "RISK": d["RISK"]}
            writer.writerow(data)
except IOError:
    print("I/O error")

