# FOR EACH NHD FILE, CREATES A SHAPEFILE WITH CATCHMENT OBJECTID-> POLYGON MAP
import arcpy
import os
import sys

geojson_shapefiles_base_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\CatchmentBoundaries\\temp_shapefiles_json"
# THIS IS WHERE THE .SHP SIMPLIFIED POLYGONS GET DUMPED
temp_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\CatchmentBoundaries\\temp_shapefiles_delete_later"
base_path = "C:\\Users\\sapmitra\\Documents\\PostFireDebris\\data\\NHD_Data\\"
files = os.listdir(base_path)

huc4 = str(sys.argv[1])

i=0
tot = len(files)
for file in files:
    if file.endswith('gdb'):
        full_path_to_layer = base_path + file + '\NHDPlus\NHDPlusCatchment'
        print(full_path_to_layer, i, tot)

        tokens = file.split('_')
        huc4 = tokens[2]

        temp_file_name = "temp_table"+ str(huc4) + ".shp"
        temp_out_path = os.path.join(temp_path, temp_file_name)
        arcpy.SimplifyPolygon_cartography(full_path_to_layer, temp_out_path, 'POINT_REMOVE',
            '0.01 DecimalDegrees', '0 Unknown', 'RESOLVE_ERRORS', 'KEEP_COLLAPSED_POINTS', '#')

        print("SHAPE SIMPLIFICATION COMPLETE....SAVED IN TEMP PATH")

        # CONVERTS FEATURE CLASS TO A JSON
        geojson_shapefiles_path = geojson_shapefiles_base_path + '\\' + str(huc4) + '.json'
        '''if not osp.isdir(temp_shapefiles_path):
            os.makedirs(temp_shapefiles_path)'''
        arcpy.FeaturesToJSON_conversion(temp_out_path, geojson_shapefiles_path, 'NOT_FORMATTED', 'NO_Z_VALUES', 'NO_M_VALUES', 'GEOJSON')

        #arcpy.FeatureClassToShapefile_conversion(full_path_to_layer,temp_shapefiles_path)
        i+=1
        print("==============================================")

        '''file = ogr.Open(temp_shapefiles_path + "\\NHDPlusCatchment.shp")
        shape = file.GetLayer(0)
        # first feature of the shapefile
        feature = shape.GetFeature(0)
        first = feature.ExportToJson()
        print first  # (GeoJSON format)'''
