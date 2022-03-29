''' RUNS ONCE FOR EACH DEM TIF FILE, WHOSE NAME IS INPUT AS ARGS.
ls into the DEM data folder and run:
ls -n | %{py  <PATH>\dem_huc_zstats_w_intrc_chk.py $_}
THIS RUNS AGAINST ALL HUC FILES AND CHECKS FOR INTERSECTION, REJECTING THE IRRELEVANT ONES
'''

from locale import currency

import os
import pickle
import csv
import sys
from os.path import exists

dem_to_huc_map_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\dem_to_huc_map"
dem_tif_base_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\DEM_full_Data"
nhd_base_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\NHD_Data"
processed_data_out_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\newXs\\X1_Zonal"

csv_columns = ["GridCode", "X1_elevation", "Count"]

tif_filename = str(sys.argv[1])

tokens = tif_filename.split("_")
if len(tokens) != 3:
    print("IRRELEVANT",tif_filename)
    exit(1)

coor = tokens[2]
coor = coor.replace(".tif","").replace("n","")
tokens2 = coor.split("w")
if len(tokens2) != 2:
    print("IRRELEVANT2")
    exit(1)
lat = int(tokens2[0])
lon = int(tokens2[1])

# ONLY WORKING WITH DEM DATA FROM THE WESTERN USA
if lat > 42 or lat < 31:
    print("IRRELEVANT LAT...NOT PROCESSING",tif_filename)
    exit(1)
if lon > 124 or lon < 101:
    print("IRRELEVANT LON...NOT PROCESSING",tif_filename)
    exit(1)

if tif_filename.endswith('.tif') and tif_filename.startswith('USGS'):
    x=1
else:
    print("IGNORE", tif_filename)
    exit(1)

print(">>>>>WORTH PROCESSING<<<<<<", tif_filename)

save_csv_name = tif_filename.replace(".","_")

valid_hucs = ['1002','1003','1004','1005','1006','1007','1008','1009','1010','1011','1012','1013','1014','1015','1016','1018','1019','1025','1102','1103','1104','1108','1109','1110','1112','1301','1302','1303','1305','1306','1307','1308','1309','1401','1402','1403','1404','1405','1406','1407','1408','1501','1502','1503','1504','1505','1506','1507','1508','1601','1602','1603','1604','1605','1606','1701','1702','1703','1704','1705','1706','1707','1708','1709','1710','1711','1712','1801','1802','1803','1804','1805','1806','1807','1808','1809','1810']
#valid_hucs = ['1306','1307']
related_hucs = valid_hucs

csv_out_file = os.path.join(processed_data_out_path, str(save_csv_name) + ".csv")
path_exists = exists(csv_out_file)

if path_exists:
    print("DUPLICATE####################################\n")
    exit(1)

import arcgisscripting
import arcpy
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
arcpy.CheckOutExtension("3D")

i=0

# DEM TIF
input_tif = os.path.join(dem_tif_base_path, tif_filename)
grid_to_val_map = {}
for huc4 in related_hucs:
    # ONE OF THE CATCHMENTS IT CLASHES WITH
    nhd_filename = "NHDPLUS_H_" + str(huc4) + "_HU4_GDB.gdb\NHDPlus\NHDPlusCatchment"
    input_nhd_gdb = os.path.join(nhd_base_path, nhd_filename)

    outShp = os.path.join("IN_MEMORY", "output_shp")
    outInt = os.path.join("IN_MEMORY", "output_int")

    '''arcpy.Intersect_analysis(
        r'C:\Users\sapmitra\Documents\ArcGIS\my_sandbox\nhd\inputs\NHDPLUS_H_1804_HU4_GDB.gdb\NHDPlus\NHDPlusCatchment #;C:\Users\sapmitra\Documents\PostFireDebris\data\DEM_full_Data\USGS_1_n31w101.tif #',
        outInt, 'ALL', '#', 'INPUT')'''

    arcpy.RasterDomain_3d(input_tif, outShp, "POLYGON")

    arcpy.Intersect_analysis([outShp, input_nhd_gdb], outInt, 'ALL', '#', 'INPUT')
    #arcpy.Intersect_analysis(input_nhd_gdb+" #;"+input_tif +" #", "in_memory/output_cnt", 'ALL', '#', 'INPUT')
    result = arcpy.GetCount_management(outInt)
    count = int(result.getOutput(0))
    arcpy.Delete_management(outShp)
    arcpy.Delete_management(outInt)
    if count > 0:
        print(huc4, " IS WORTH PROCESSING...")
    else:
        #print("NO INTERSECTION FOR ", huc4)
        continue

    print("****************************************")
    outTable = os.path.join("IN_MEMORY", "temp_table"+str(i))
    i+=1

    #input_tif = r'C:\Users\sapmitra\Documents\PostFireDebris\data\DEM_Data\USGS_1_n50w125.tif'

    #input_nhd_gdb = r'C:\Users\sapmitra\Documents\PostFireDebris\data\NHD_Data\NHDPLUS_H_1711_HU4_GDB.gdb'

    # THIS TAKES AN INPUT TIF FROM THE DEM AND GENERATES A MAP or >=23 DEGREES
    outSlope = Slope(input_tif, 'DEGREE', '1')
    outraster = arcpy.sa.GreaterThan(outSlope,23)
    print("GREATER THAN COMPUTATION OVER...SAVING OUTPUT IN MEMORY")

    try:
        ZonalStatisticsAsTable(input_nhd_gdb, 'GridCode', outraster, outTable, ignore_nodata="DATA", statistics_type="MEAN")
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

    print("ENTRIES GENERATED:",len(grid_to_val_map))

csv_out_file = os.path.join(processed_data_out_path, str(save_csv_name) + ".csv")
#print(csv_out_file)
import traceback
try:
    with open(csv_out_file, 'wb') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for key in grid_to_val_map:
            d = grid_to_val_map[key]
            data = {"GridCode": key, "X1_elevation": d["val"], "Count": d["count"]}
            writer.writerow(data)
except IOError:
    traceback.print_exc()
    print("I/O error")

print("FINISHED>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")