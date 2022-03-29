#!/bin/bash
while IFS= read -r line; do
    #CD TO THE DIRECTORY OF THE PYTHON FILE
    cd /s/lattice-101/a/nobackup/galileo/sustain/FireWatcher/fix_shapely;
    #RUN THE PYTHON FILE OVER ALL THE FILES IN THE GIVEN DIRECTORY
    python3 soils_insert.py "/s/lattice-101/a/nobackup/galileo/sustain/arcgis/statsgo_soil/SOILS_Simplified/" $line
done < "$1"
