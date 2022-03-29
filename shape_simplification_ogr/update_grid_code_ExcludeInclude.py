import json
import sys
import os

# This excludes the problematic gridcodes for later refinement and just dumps the normal ones into the jsons
# This also takes the "GridCode" attribute to the top level

#THIS IS A FILE CONTAINING NAMES OF ALL GRID CODES THAT FAILED INGESTION THAT NEED TO BE AVOIDED
# OR INCLUDED, DEPENDING ON WHAT WE ARE DOING
problematic_grid_codes = "missed_grid_codes_list"
json_files_base_path = "NHD_Simplified"
json_output_base_path = "NHD_Simplified_Upd_gridCode"
json_file_name = str(sys.argv[1])
#json_file_name = "1002.json"

with open(problematic_grid_codes) as file:
    prob_gcs = []
    for readline in file:
        line_strip = readline.strip()
        prob_gcs.append(line_strip)

print(len(prob_gcs))

huc4 = json_file_name.replace(".json","")
print(huc4)

json_file_abs_path = os.path.join(json_files_base_path, json_file_name)
json_output_file_abs_path = os.path.join(json_output_base_path, json_file_name)

with open(json_file_abs_path, 'r+') as f:
    data = json.load(f)
    features_array = data["features"]

    features_array_new = []
    data_new = {}
    data_new["features"] = features_array_new

    for ft in features_array:
        prop = ft["properties"]
        gridCode = prop["GridCode"]

        gc_upd = str(gridCode) + "A" + str(huc4)
        prop["GridCode"] = gc_upd
        ft["GridCode"] = gc_upd

        if gc_upd in prob_gcs:
            print("IGNORED PROBLEMATIC", gc_upd)
        else:
            features_array_new.append(ft)
    with open(json_output_file_abs_path, 'w') as f1:
        json.dump(data_new, f1)
