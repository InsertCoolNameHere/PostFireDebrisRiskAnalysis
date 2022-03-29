''' RUNS ONCE FOR EACH DESIGN STORM REGION FILE, WHOSE NAME IS INPUT AS ARGS
ls into the DESIGN STORM data folder and run:
ls -n | %{py  <PATH>\dstorm_huc_zonal_intrc_chk_single.py $_}
# THIS RUNS AGAINST ALL HUC FILES AND CHECKS FOR INTERSECTION
'''

from locale import currency

import os
import pickle
import csv
import sys
from os.path import exists

dstorm_ip_base_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\DesignStorm\\relevant"
nhd_base_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\NHD_Data"
processed_data_out_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\DStorm"

# MAKING SURE THAT THI15 and DESIGN STORM AVERAGES ARE IN THE SAME UNIT
conversion_factor = 0.1016

csv_columns = ["GridCode", "DStorm", "Count"]

ds_filename = str(sys.argv[1])
#ds_filename = "sw5yr15ma.asc"

if ds_filename.endswith('.asc'):
    print("INPUT FILE: ", ds_filename)
    x=1
else:
    print("IGNORE", ds_filename)
    exit(1)

save_csv_name = ds_filename.replace(".", "_")

valid_hucs = ['1002','1003','1004','1005','1006','1007','1008','1009','1010','1011','1012','1013','1014','1015','1016','1018','1019','1025','1102','1103','1104','1108','1109','1110','1112','1301','1302','1303','1305','1306','1307','1308','1309','1401','1402','1403','1404','1405','1406','1407','1408','1501','1502','1503','1504','1505','1506','1507','1508','1601','1602','1603','1604','1605','1606','1703','1704','1705','1707','1708','1709','1712','1801','1802','1803','1804','1805','1806','1807','1808','1809','1810']
#valid_hucs = ['1805']
related_hucs = valid_hucs

csv_out_file = os.path.join(processed_data_out_path, str(save_csv_name) + ".csv")
path_exists = exists(csv_out_file)

import arcgisscripting
import arcpy
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
#arcpy.CheckOutExtension("3D")
arcpy.env.cellSize = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\DEM_Data\\USGS_1_n40w077.tif"

i=0

# DEM TIF
input_asc = os.path.join(dstorm_ip_base_path, ds_filename)
grid_to_val_map = {}
for huc4 in related_hucs:
    # ONE OF THE CATCHMENTS IT CLASHES WITH
    nhd_filename = "NHDPLUS_H_" + str(huc4) + "_HU4_GDB.gdb\NHDPlus\NHDPlusCatchment"
    input_nhd_gdb = os.path.join(nhd_base_path, nhd_filename)

    #outShp = os.path.join("IN_MEMORY", "output_shp")
    #outInt = os.path.join("IN_MEMORY", "output_int")

    '''arcpy.Intersect_analysis(
        r'C:\Users\sapmitra\Documents\ArcGIS\my_sandbox\nhd\inputs\NHDPLUS_H_1804_HU4_GDB.gdb\NHDPlus\NHDPlusCatchment #;C:\Users\sapmitra\Documents\PostFireDebris\data\DEM_full_Data\USGS_1_n31w101.tif #',
        outInt, 'ALL', '#', 'INPUT')'''

    #arcpy.RasterDomain_3d(input_asc, outShp, "POLYGON")
    #print("HERE")
    #arcpy.Intersect_analysis([outShp, input_nhd_gdb], outInt, 'ALL', '#', 'INPUT')
    #result = arcpy.GetCount_management(outInt)
    #count = int(result.getOutput(0))
    #arcpy.Delete_management(outShp)
    #arcpy.Delete_management(outInt)
    '''if count > 0:
        print(huc4, " IS WORTH PROCESSING...")
    else:
        #print("NO INTERSECTION FOR ", huc4)
        continue'''

    print("****************************************")

    outTable = os.path.join("IN_MEMORY", "temp_table"+str(i))
    i+=1

    try:
        ZonalStatisticsAsTable(input_nhd_gdb, 'GridCode', input_asc, outTable, ignore_nodata="DATA", statistics_type="MEAN")
    except arcgisscripting.ExecuteError:
        print("BOUNDS MISMATCH FOR ",huc4, i, len(related_hucs))
        continue

    lst_flds = ['GridCode', 'MEAN', 'COUNT']

    with arcpy.da.SearchCursor(outTable, lst_flds) as curs:
        for row in curs:
            #print(len(row))
            grid_num = str(row[0])
            val = float(row[1])
            cnt = int(row[2])
            grid_key = str(grid_num) + 'A' + str(huc4)

            if grid_key in grid_to_val_map:
                #print("DUPLICATE>>>>>>>")
                d = grid_to_val_map[grid_key]
                curr_val = d["val"]
                curr_cnt = d["count"]

                new_cnt = cnt+curr_cnt
                new_val = (curr_val*curr_cnt + val*cnt) / (float)(cnt+curr_cnt)
                grid_to_val_map[grid_key] = {"val": new_val, "count": new_cnt}
                #print(grid_num, "OLD", d, "NEW", grid_to_val_map[grid_num])
            else:
                grid_to_val_map[grid_key] = {"val":val, "count":cnt}
    arcpy.Delete_management(outTable)
    print("ENTRIES GENERATED:",len(grid_to_val_map), huc4, i)

csv_out_file = os.path.join(processed_data_out_path, str(save_csv_name) + ".csv")
#print(csv_out_file)
import traceback
try:
    with open(csv_out_file, 'wb') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for key in grid_to_val_map:
            d = grid_to_val_map[key]
            dval_scaled = float(d["val"])*conversion_factor
            data = {"GridCode": key, "DStorm": dval_scaled, "Count": d["count"]}
            writer.writerow(data)
except IOError:
    traceback.print_exc()
    print("I/O error")

print("FINISHED>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")