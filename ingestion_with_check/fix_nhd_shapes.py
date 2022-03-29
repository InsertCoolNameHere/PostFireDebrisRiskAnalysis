import os
import sys

base_path = str(sys.argv[1])
#huc_file_name = "1808.json"
huc_file_name = str(sys.argv[2])
file_path = base_path+huc_file_name
op_path = base_path+"op_"+huc_file_name
jq_op_path = base_path+"ins/op_"+huc_file_name
log_file_path = base_path+"log_missed.txt"

jq_command = "jq -c '.features' " + op_path + " > " + jq_op_path
command1 = "/s/parsons/b/others/sustain/db-tools/mongodb-database-tools-rhel80-x86_64-100.3.0/bin/mongoimport --port 27018 --db sustaindb --collection nhd_shapes --file "+ jq_op_path +" --jsonArray > "+ log_file_path+" 2>&1"
command2 = "/s/parsons/b/others/sustain/db-tools/mongodb-database-tools-rhel80-x86_64-100.3.0/bin/mongoimport --port 27018 --db sustaindb --collection nhd_shapes --mode upsert --upsertFields=GridCode --file "+ jq_op_path +" --jsonArray > "+ log_file_path+" 2>&1"

if os.path.exists(op_path):
    os.remove(op_path)
if os.path.exists(log_file_path):
    os.remove(log_file_path)
if os.path.exists(jq_op_path):
    os.remove(jq_op_path)


missed_stuff = []

print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>INGESTING:",huc_file_name)
import json
import shapely
from shapely.geometry import shape
with open(file_path) as geojson_file:
     data = json.load(geojson_file)

while True:
    begin_populating = True
    command_exec = command1
    if len(missed_stuff) > 0:
        begin_populating = False
        command_exec = command2

    features_array_new = []
    data_new = {}
    data_new["features"] = features_array_new

    for feat in data['features']:
        prop = feat["properties"]
        gridCode = prop["GridCode"]

        if gridCode in missed_stuff:
            print("BEGIN POPULATING")
            begin_populating = True
            continue

        #result = shape(feat['geometry']).buffer(1e-12, resolution=0)#.simplify(0)
        #geojson = shapely.geometry.mapping(result)
        #feat['geometry'] = geojson
        feat["GridCode"] = gridCode
        if begin_populating:
            features_array_new.append(feat)

    print("ABOUT TO INSERT", len(features_array_new)," ENTRIES")
    if len(features_array_new) == 0:
        print("ALL DATA INSERTED....")
        break

    # LOOK INTO THE LOG FILE TO SEE IF ANYTHING WAS MISSED
    with open(op_path, 'w') as f1:
        json.dump(data_new, f1)

    # RUN MONGO IMPORT SHELL COMMAND
    os.system(jq_command)

    print(command_exec)
    os.system(command_exec)

    # PARSE LOG FILE TO FIND MISSED SHAPES
    missed_stuff = []
    if os.path.exists(log_file_path):
        with open(log_file_path) as file:
            lines = []
            for line in file:
                ll = line.rstrip()
                if "GridCode" in ll:
                    tokens = ll.split("GridCode: ")

                    for i in range(1,len(tokens)):
                        tokens1 = tokens[i]
                        gcd = tokens1.split(",")[0]

                        if "}" in gcd:
                            gcd = gcd.split("}")[0]

                        gcd = gcd.strip()
                        gcd = gcd.replace("\"","")

                        missed_stuff.append(gcd)
    myset = set(missed_stuff)
    missed_stuff = list(myset)
    print("MISSED THESE GRIDCODES:", missed_stuff)
    if len(missed_stuff) == 0:
        break

os.remove(op_path)
os.remove(log_file_path)
print("REMOVED TEMP AND LOG FILE:",op_path, log_file_path)
print(".................................................")
