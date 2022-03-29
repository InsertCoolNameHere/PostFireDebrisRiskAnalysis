#!/bin/bash

while IFS= read -r line; do
    echo "$line" ;
    python3 update_grid_code_ExcludeInclude.py $line
    echo "======================================="
done < "$1"
