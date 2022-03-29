''' RUNS ONCE FOR EACH STATSGO REGION FILE, WHOSE NAME IS INPUT AS ARGS
ls into the STATSGO SOIL data folder and run:
ls -n | %{py  <PATH>\soils_huc_zonal_stats_single.py $_}
# THIS RUNS AGAINST ALL HUC FILES AND CHECKS FOR INTERSECTION
'''

import arcpy
import os
import pickle
import csv
import sys

soils_base_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\SOILS"
soils_reprojected_temp_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\SOILS_temp_data\\reproj"
soil_to_huc_map_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\soil_to_huc_map"
nhd_base_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\NHD_Data"
processed_data_out_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\X3_Zonal"
soil_output_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\SOILS_temp_data\\rast"

arcpy.CheckOutExtension("Spatial")

soil_file_name = str(sys.argv[1])
soil_file_abs_path = os.path.join(soils_base_path, soil_file_name)

if not soil_file_name.endswith(".shp"):
    print("IRRELEVANT:",soil_file_name)
    exit(1)
else:
    print("WORKING ON:",soil_file_name)

from arcpy.sa import *

# REPROJECTING SOILS SHP FILE TO WGS84
soil_reprojected_file = os.path.join(soils_reprojected_temp_path, "rp"+soil_file_name)
soil_output_file = os.path.join(soil_output_path, "rs"+soil_file_name.replace(".shp",""))

arcpy.Project_management(soil_file_abs_path, soil_reprojected_file,
                         "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
                         "'NAD_1927_To_NAD_1983_NADCON + WGS_1984_(ITRF00)_To_NAD_1983'",
                         "PROJCS['NAD_1927_Albers',GEOGCS['GCS_North_American_1927',DATUM['D_North_American_1927',SPHEROID['Clarke_1866',6378206.4,294.9786982]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Albers'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-96.0],PARAMETER['Standard_Parallel_1',29.5],PARAMETER['Standard_Parallel_2',45.5],PARAMETER['Latitude_Of_Origin',23.0],UNIT['Meter',1.0]]",
                         'NO_PRESERVE_SHAPE', '#', 'NO_VERTICAL')

print("Reproj Done.......")

# CONVERTING TO A RASTER OF PIXELS
arcpy.PolygonToRaster_conversion(soil_reprojected_file, 'KFFACT', soil_output_file, 'CELL_CENTER', 'NONE')

print("Rasterization Done.......")

# THE COLUMNS OF THE FINAL ZONALISED CSV
csv_columns = ["GridCode", "X3_soil", "Count"]

# READING DE->HUC MAP FROM DISK
with open(soil_to_huc_map_path, 'rb') as handle1:
    soil_to_huc_map = pickle.load(handle1)
# FORMAT: SOIL FILE NAME-> [HUC4 array]  eg. 'ussoils_01.shp': [u'0309']

print(soil_file_name, "SOIL-HUC MAP LOADED, SIZE: ", len(soil_to_huc_map))

# THE OUTPUT CSV FILE
save_csv_name = soil_file_name.replace(".","_")
related_hucs = soil_to_huc_map[soil_file_name]

if len(related_hucs) == 0:
    print("NO INTERSECTING CATCHMENT, IGNORE ",soil_file_name)
    print("IGNORING####################################\n")
    exit(1)

grid_to_val_map = {}

i=0
for huc4 in related_hucs:
    print("****************************************")
    outTable = os.path.join("IN_MEMORY", "temp_table" + str(i))
    i+=1
    nhd_filename = "NHDPLUS_H_" + str(huc4) + "_HU4_GDB.gdb\NHDPlus\NHDPlusCatchment"
    input_nhd_gdb = os.path.join(nhd_base_path, nhd_filename)

    # CALCULATING ZONAL STATS ANS SAVING THEM IN A TABLE
    ZonalStatisticsAsTable(input_nhd_gdb, 'GridCode', soil_output_file, outTable, ignore_nodata="DATA", statistics_type="MEAN")

    lst_flds = ['GridCode', 'MEAN', 'COUNT']

    with arcpy.da.SearchCursor(outTable, lst_flds) as curs:
        for row in curs:
            # print(len(row))
            grid_num = str(row[0])
            val = float(row[1])
            cnt = int(row[2])

            if grid_num in grid_to_val_map:
                # print("DUPLICATE>>>>>>>")
                d = grid_to_val_map[grid_num]
                curr_val = d["val"]
                curr_cnt = d["count"]

                new_cnt = cnt + curr_cnt
                new_val = (curr_val * curr_cnt + val * cnt) / (float)(cnt + curr_cnt)
                grid_to_val_map[grid_num] = {"val": new_val, "count": new_cnt}

                # print(grid_num, "OLD", d, "NEW", grid_to_val_map[grid_num])
            else:
                grid_to_val_map[grid_num] = {"val": val, "count": cnt}

print("WRITING CSV....")
# THE OUTPUT CSV FILE
csv_file = os.path.join(processed_data_out_path, str(save_csv_name) + ".csv")
try:
    with open(csv_file, 'wb') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for key in grid_to_val_map:
            d = grid_to_val_map[key]
            data = {"GridCode": key, "X3_soil": d["val"], "Count": d["count"]}
            writer.writerow(data)
except IOError:
    print("I/O error")

print("FINISHED>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")