#!/bin/bash
while IFS= read -r line; do
    #CD TO THE DIRECTORY OF THE PYTHON FILE
    cd /s/lattice-101/a/nobackup/galileo/sustain/FireWatcher/fix_shapely;
    #RUN THE PYTHON FILE OVER ALL THE FILES IN THE GIVEN DIRECTORY
    python3 fix_nhd_shapes.py "/s/lattice-101/a/nobackup/galileo/sustain/arcgis/resampled_attributes/NHD_Simplified_Upd_gridCode/" $line
done < "$1"
