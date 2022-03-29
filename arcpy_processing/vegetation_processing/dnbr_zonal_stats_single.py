# A SINGLE CONUS DNBR TIF FILE IS THE INPUT THAT IS CHECKED AGAINST ALL RELEVANT HUC REGION
import os
import csv
import sys

nhd_base_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\NHD_Data"
processed_data_out_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\X2_Zonal_resampled"

huc_code = str(sys.argv[1])
# THE OUTPUT CSV FILE
related_hucs = ['1002','1003','1004','1005','1006','1007','1008','1009','1010','1011','1012','1013','1014','1015','1016','1018','1019','1025','1102','1103','1104','1108','1109','1110','1112','1301','1302','1303','1305','1306','1307','1308','1309','1401','1402','1403','1404','1405','1406','1407','1408','1501','1502','1503','1504','1505','1506','1507','1508','1601','1602','1603','1604','1605','1606','1701','1702','1703','1704','1705','1706','1707','1708','1709','1710','1711','1712','1801','1802','1803','1804','1805','1806','1807','1808','1809','1810']

if huc_code not in related_hucs:
    print("IGNORE HUC", huc_code)
    exit(1)
else:
    print("USING HUC", huc_code)


import arcpy
arcpy.CheckOutExtension("Spatial")
arcpy.env.cellSize = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\DEM_Data\\USGS_1_n40w077.tif"
dnbr_file_abs_path = "C:\Users\sapmitra\Documents\ArcGIS\my_sandbox\\dnbr.tif"

from arcpy.sa import *

# THE COLUMNS OF THE FINAL ZONALISED CSV
csv_columns = ["GridCode", "X2_dnbr", "Count"]

save_csv_name = huc_code

grid_to_val_map = {}

i=0

#print("****************************************", i, tot_hucs)
outTable = os.path.join("IN_MEMORY", "temp_table")
nhd_filename = "NHDPLUS_H_" + str(huc_code) + "_HU4_GDB.gdb\NHDPlus\NHDPlusCatchment"
input_nhd_gdb = os.path.join(nhd_base_path, nhd_filename)

# CALCULATING ZONAL STATS ANS SAVING THEM IN A TABLE
ZonalStatisticsAsTable(input_nhd_gdb, 'GridCode', dnbr_file_abs_path, outTable, ignore_nodata="DATA", statistics_type="MEAN")

# FIELDS FROM THE GENERATED ZONAL OUTPUT THAT WE WILL READ
lst_flds = ['GridCode', 'MEAN', 'COUNT']

with arcpy.da.SearchCursor(outTable, lst_flds) as curs:
    for row in curs:
        # print(len(row))
        grid_num = str(row[0])
        val = float(row[1])
        cnt = int(row[2])
        grid_key = str(grid_num) +'A'+ str(huc_code)

        if cnt >0:
            if grid_key in grid_to_val_map:
                # print("DUPLICATE>>>>>>>")
                d = grid_to_val_map[grid_key]
                curr_val = d["val"]
                curr_cnt = d["count"]

                new_cnt = cnt + curr_cnt
                new_val = (curr_val * curr_cnt + val * cnt) / (float)(cnt + curr_cnt)
                grid_to_val_map[grid_key] = {"val": new_val, "count": new_cnt}

                # print(grid_num, "OLD", d, "NEW", grid_to_val_map[grid_num])
            else:
                grid_to_val_map[grid_key] = {"val": val, "count": cnt}

print("WRITING CSV....", len(grid_to_val_map))
# THE OUTPUT CSV FILE
csv_file = os.path.join(processed_data_out_path, str(save_csv_name) + ".csv")
try:
    with open(csv_file, 'wb') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for key in grid_to_val_map:
            d = grid_to_val_map[key]
            data = {"GridCode": key, "X2_dnbr": d["val"], "Count": d["count"]}
            writer.writerow(data)
except IOError:
    print("I/O error")

print("FINISHED>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")