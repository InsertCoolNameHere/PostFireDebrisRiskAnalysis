# HANDLES AND MERGES DUPLICATE GRID CODES IN GENERATED ZONAL STATISTICS
import pandas as pd
import os
import csv

DS_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\DStorm"

combined_x2_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\DStorm"

ds_dict = {}
# READ ALL X1
print("X2....")

ind=0
for f in os.listdir(DS_path):
    cdf_csv_path = os.path.join(DS_path, f)
    cdf_df = pd.read_csv(cdf_csv_path, index_col=False, header=0)

    for i in range(len(cdf_df)):
        grid_key = cdf_df.iloc[i,0]
        x1 = float(cdf_df.iloc[i,1])
        count = float(cdf_df.iloc[i,2])

        if grid_key in ds_dict:
            # print("DUPLICATE>>>>>>>")
            d = ds_dict[grid_key]
            curr_x1 = d["DStorm"]
            curr_cnt = d["count"]

            new_count = count + curr_cnt
            new_x1 = (curr_x1 * curr_cnt + x1 * count) / (float)(count + curr_cnt)
            #print(new_count, count, curr_cnt)
            ds_dict[grid_key] = {"DStorm": new_x1, "count": new_count}
        else:
            ds_dict[grid_key] = {"DStorm":x1, "count":count}

        if i % 10000 == 0:
            print(i)

    ind+=1
    print("READ ",ind)



print("...........................COMBINING.................................")



csv_columns = ["GridCode","DStorm","Count"]
csv_file = os.path.join(combined_x2_path, "combined_DS.csv")
try:
    with open(csv_file, 'wb') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for key in ds_dict:
            d = ds_dict[key]
            data = {"GridCode": key, "DStorm": d["DStorm"], "Count": d["count"]}
            writer.writerow(data)
except IOError:
    print("I/O error")
