#!/bin/bash

while IFS= read -r line; do
    echo "$line" ;
    ogr2ogr -f "GeoJSON" -t_srs crs:84 /s/lattice-77/a/nobackup/galileo/sapmitra/processing/statsgo_soil/SOILS_temp/$line.json /s/lattice-77/a/nobackup/galileo/sapmitra/processing/statsgo_soil/SOILS/$line.shp
    echo "CONVERTED TO JSON...."
    mapshaper-xl /s/lattice-77/a/nobackup/galileo/sapmitra/processing/statsgo_soil/SOILS_temp/$line.json -simplify 5% -clean -o /s/lattice-77/a/nobackup/galileo/sapmitra/processing/statsgo_soil/SOILS_Simplified/$line.json
    echo "SIMPLIFIED JSON SHAPE...."
    echo "======================================="
done < "$1"