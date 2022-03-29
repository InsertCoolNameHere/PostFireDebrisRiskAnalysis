import math

import pandas as pd
import os
import csv

X1_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\newXs\\X1_Zonal\\combined_x1.csv"
X2_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\X2_Zonal_resampled"
X3_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\X3_Zonal_resampled"

thi15_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\THI15"


numer = math.log10(9) + 3.63
x1_dict = {}
x2_dict = {}
x3_dict = {}
# READ ALL X1
print("X1....")

ind=0
for f in os.listdir(X1_path):
    cdf_csv_path = os.path.join(X1_path, f)
    cdf_df = pd.read_csv(cdf_csv_path, index_col=False, header=0)

    for i in range(len(cdf_df)):
        grid_key = cdf_df.iloc[i,0]
        x1 = float(cdf_df.iloc[i,1])
        count = float(cdf_df.iloc[i,2])

        x1_dict[grid_key] = {"x1": x1, "count": count}

    ind+=1
    print("READ ",ind)

print("X2....")
# READ ALL X2
ind=0
for f in os.listdir(X2_path):
    cdf_csv_path = os.path.join(X2_path, f)
    cdf_df = pd.read_csv(cdf_csv_path, index_col=False, header=0)

    for i in range(len(cdf_df)):
        grid_key = cdf_df.iloc[i,0]
        x2 = float(cdf_df.iloc[i,1])
        count = float(cdf_df.iloc[i,2])

        x2_dict[grid_key] = {"x2": x2, "count": count}
    ind += 1
    print("READ ", ind)

# READ ALL X3
ind=0
print("X3....")
for f in os.listdir(X3_path):
    cdf_csv_path = os.path.join(X3_path, f)
    cdf_df = pd.read_csv(cdf_csv_path, index_col=False, header=0)

    for i in range(len(cdf_df)):
        grid_key = cdf_df.iloc[i,0]
        x3 = float(cdf_df.iloc[i,1])
        count = float(cdf_df.iloc[i,2])

        x3_dict[grid_key] = {"x3": x3, "count": count}
    ind += 1
    print("READ ", ind)


print("...........................COMBINING.................................")
thi15_dict = {}
for gg in x3_dict:
    if gg in x1_dict and gg in x2_dict:
        x1 = x1_dict[gg]["x1"]
        x2 = x2_dict[gg]["x2"]/1000
        x3 = x3_dict[gg]["x3"]
        deno = (0.41*x1) + (0.67*x2) + (0.7*x3)
        tval = numer/ deno
        thi15_dict[gg] = {"thi15": tval}



csv_columns = ["GridCode", "THI15"]
csv_file = os.path.join(thi15_path, "thi15.csv")
try:
    with open(csv_file, 'wb') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for key in thi15_dict:
            d = thi15_dict[key]
            data = {"GridCode": key, "THI15": d["thi15"]}
            writer.writerow(data)
except IOError:
    print("I/O error")

