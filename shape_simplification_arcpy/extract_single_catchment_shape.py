# FOR EACH NHD FILE, CREATES A SHAPEFILE WITH CATCHMENT OBJECTID-> POLYGON MAP IN IT. THIS WILL BE STORED IN MONGODB
import arcpy
import os
import sys

# THIS IS THE PATH TO THE OUTPUT FILES
geojson_shapefiles_base_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\CatchmentBoundaries\\fixed\\temp_shapefiles_json"
# THIS IS WHERE THE .SHP SIMPLIFIED POLYGONS GET DUMPED
temp_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\CatchmentBoundaries\\temp_shapefiles_delete_later"
base_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\NHD_Data\\"
files = os.listdir(base_path)

hucs_left = ['0102','0103','0104','0105','0106','0107','0108','0109','0110','0202','0203','0206','0207','0302','0303','0306','0308','0309','0310','0311','0312','0313','0314','0317','0318','0401','0402','0403','0404','0405','0406','0407','0408','0409','0410','0411','0412','0413','0414','0415','0416','0417','0418','0418i','0419','0419i','0420','0421','0422','0423','0424','0424i','0425','0426','0426i','0427','0428','0428i','0429','0430','0431','0432','0433','0501','0502','0503','0504','0505','0506','0507','0508','0509','0510','0511','0513','0602','0603','0604','0701','0702','0703','0704','0705','0706','0707','0708','0709','0710','0711','0712','0713','0714','0801','0802','0803','0805','0806','0807','0808','0809','0901','0903','0904','1002','1006','1007','1010','1011','1015','1016','1017','1020','1021','1022','1023','1024','1025','1026','1027','1028','1030','1103','1104','1105','1106','1108','1109','1110','1111','1112','1201','1202','1204','1205','1206','1208','1301','1303','1305','1306','1307','1308','1309','1401','1402','1403','1405','1406','1407','1503','1504','1506','1507','1601','1603','1605','1703','1708','1712','1803','1805','1806','1807','1808','1810']

for f in os.listdir(temp_path):
    os.remove(os.path.join(temp_path, f))

#huc4 = str(sys.argv[1])
huc4 = '0104'

if huc4 in hucs_left:
    print("ALREADY DONE, SKIPPING ",huc4)
    exit(1)


file = "NHDPLUS_H_" + str(huc4) + "_HU4_GDB.gdb"


full_path_to_layer = base_path + file + '\NHDPlus\NHDPlusCatchment'
print(full_path_to_layer)

tokens = file.split('_')
huc4 = tokens[2]

temp_file_name = "temp_table"+ str(huc4) + ".shp"
temp_out_path = os.path.join(temp_path, temp_file_name)
arcpy.SimplifyPolygon_cartography(full_path_to_layer, temp_out_path, 'POINT_REMOVE',
    '0.01 DecimalDegrees', '0 Unknown', 'RESOLVE_ERRORS', 'KEEP_COLLAPSED_POINTS', '#')

print("SHAPE SIMPLIFICATION COMPLETE....SAVED IN TEMP PATH")

arcpy.RepairGeometry_management(temp_out_path)
print("FIXING COMPLETE...")

# CONVERTS FEATURE CLASS TO A JSON
geojson_shapefiles_path = geojson_shapefiles_base_path + '\\' + str(huc4) + '.json'

arcpy.FeaturesToJSON_conversion(temp_out_path, geojson_shapefiles_path, 'NOT_FORMATTED', 'NO_Z_VALUES', 'NO_M_VALUES', 'GEOJSON')

print("==============================================")

