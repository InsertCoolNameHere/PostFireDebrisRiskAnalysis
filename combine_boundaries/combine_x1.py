# HANDLES AND MERGES DUPLICATE GRID CODES IN GENERATED ZONAL STATISTICS
import pandas as pd
import os
import csv

X1_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\newXs\\X1_Zonal"

combined_x1_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\newXs\\X1_Zonal"

x1_dict = {}
x2_dict = {}
x3_dict = {}
# READ ALL X1
print("X1....")

ind=0
for f in os.listdir(X1_path):
    file_n = str(f)
    if not file_n.endswith(".csv"):
        print("IGNORING...", file_n)
        continue
    cdf_csv_path = os.path.join(X1_path, f)
    cdf_df = pd.read_csv(cdf_csv_path, index_col=False, header=0)

    for i in range(len(cdf_df)):
        grid_key = cdf_df.iloc[i,0]
        x1 = float(cdf_df.iloc[i,1])
        count = float(cdf_df.iloc[i,2])

        if grid_key in x1_dict:
            # print("DUPLICATE>>>>>>>")
            d = x1_dict[grid_key]
            curr_x1 = d["x1"]
            curr_cnt = d["count"]

            new_count = count + curr_cnt
            new_x1 = max(curr_x1, x1)
            #print(new_count, count, curr_cnt)
            x1_dict[grid_key] = {"x1": new_x1, "count": new_count}
        else:
            x1_dict[grid_key] = {"x1":x1, "count":count}
    ind+=1
    print("READ ",ind)



print("...........................COMBINING.................................")



csv_columns = ["GridCode","X1_elevation","Count"]
csv_file = os.path.join(combined_x1_path, "combined_x1.csv")
try:
    with open(csv_file, 'wb') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for key in x1_dict:
            d = x1_dict[key]
            data = {"GridCode": key, "X1_elevation": d["x1"], "Count": d["count"]}
            writer.writerow(data)
except IOError:
    print("I/O error")
