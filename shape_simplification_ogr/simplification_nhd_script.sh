#!/bin/bash

while IFS= read -r line; do
    echo "$line" ;
    ogr2ogr -f "GeoJSON" /s/lattice-77/a/nobackup/galileo/sapmitra/processing/NHD_temp/$line.json /s/lattice-77/a/nobackup/galileo/sapmitra/NHD_Data/NHDPLUS_H_$line\_HU4_GDB.gdb "NHDPlusCatchment"
    echo "CONVERTED TO JSON...."
    mapshaper-xl NHD_temp/$line.json -simplify 5% -clean -o NHD_Simplified/$line.json
    echo "SIMPLIFIED JSON SHAPE...."
    echo "======================================="
done < "$1"