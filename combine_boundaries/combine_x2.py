# HANDLES AND MERGES DUPLICATE GRID CODES IN GENERATED ZONAL STATISTICS
import pandas as pd
import os
import csv

X2_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\X2_Zonal_resampled"

combined_x2_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\X2_Zonal_resampled"

x2_dict = {}
# READ ALL X1
print("X2....")

ind=0
for f in os.listdir(X2_path):
    cdf_csv_path = os.path.join(X2_path, f)
    cdf_df = pd.read_csv(cdf_csv_path, index_col=False, header=0)

    for i in range(len(cdf_df)):
        grid_key = cdf_df.iloc[i,0]
        x1 = float(cdf_df.iloc[i,1])
        count = float(cdf_df.iloc[i,2])

        if grid_key in x2_dict:
            # print("DUPLICATE>>>>>>>")
            d = x2_dict[grid_key]
            curr_x1 = d["x1"]
            curr_cnt = d["count"]

            new_count = count + curr_cnt
            new_x1 = (curr_x1 * curr_cnt + x1 * count) / (float)(count + curr_cnt)
            #print(new_count, count, curr_cnt)
            x2_dict[grid_key] = {"x1": new_x1, "count": new_count}
        else:
            x2_dict[grid_key] = {"x1":x1, "count":count}

        if i % 10000 == 0:
            print(i)

    ind+=1
    print("READ ",ind)



print("...........................COMBINING.................................")



csv_columns = ["GridCode","X2_dnbr","Count"]
csv_file = os.path.join(combined_x2_path, "combined_x2.csv")
try:
    with open(csv_file, 'wb') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for key in x2_dict:
            d = x2_dict[key]
            data = {"GridCode": key, "X2_dnbr": d["x1"], "Count": d["count"]}
            writer.writerow(data)
except IOError:
    print("I/O error")
