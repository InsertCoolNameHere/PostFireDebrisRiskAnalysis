<h1><b><center>CALCULATION OF POST-FIRE DEBIS FLOW RISK OVER CONUS</center></b>
<hr style="border:2px solid gray">

<h2><u>DATA SOURCES</u></h2>

### [Watershed (NHD Plus)](https://apps.nationalmap.gov/downloader/#/)
Hydrography->NHDPlus High Resolution (NHDPlus HR)

### [Elevation](https://apps.nationalmap.gov/downloader/#/)
Digital Evevation map (spatial resolution of 30m)

### [Design Storm](https://hdsc.nws.noaa.gov/hdsc/pfds/pfds_gis.html)
Interval - 5yrs, Duration- 15mins; Missing a segment of North-Western USA

### [Vegetation](https://landfire.gov/version_download.php#)
We use EVT-140 CONUS (2014) data.

### [Soil](https://water.usgs.gov/GIS/metadata/usgswrd/XML/ussoils.xml#stdorder)
STATSGO Database.

<hr style="border:0.5px solid gray">

## <u>SHAPEFILE SIMPLIFICATION</u>

NHD-shapefiles were too large in size and number to support fast visualization. We simplified these shapes to enable fast 
fetching. The *shape_simplification_ogr* directory contains scripts for simplification of shapefiles. 

1) Run *simplification_nhd_script.sh* to simplify the catchment shapes.
2) Run *update_grid_script.sh* to modify the GridCode inside the generated jsons to make them unique.

For simplification of the STATSGO shapes, just run *simplification_statsgo_script.sh*

<sub><sub>NOTE TO SELF: Run simplification on lattice-77 and copy and ingest from lattice-101.</sub></sub>

## <u>DIGITAL ELEVATION MAP ZONAL STATISTICS</u>
Run the following from the directory containing DEM TIFFs:

```ls -n | %{py  PostFireDebrisRiskAnalysis\arcpy_processing\dem_processing\dem_huc_zstats_w_intrc_chk.py $_}```

## <u>DNBR ZONAL STATISTICS</u>
Differential Normalized Burn Ratio. 

1) Import the file *EVT-140_CONUS_MAIN\US_140EVT_20180618\Grid\us_140evt* into ArcMap. 
2) Open Attribute Table and add a field DNBR. RClick and select *Field Calculator*. 
3) Use the python code *\vegetation\pre_logic.py* as: ```DNBR = get_lambda(!Value_1!)```
4) Extract the DNBR field into a single-band TIFF file using *delete raster attribute table* function.
   
Run the following to perform Zonal Statistics over NHD catchments:

```
cd C:\Users\sapmitra\Documents\PostFireDebris\data\CatchmentBoundaries\temp_shapefiles
ls -n | %{py PostFireDebrisRiskAnalysis\arcpy_processing\vegetation_processing\dnbr_zonal_stats_single.py $_}
```

## <u>STATS SOIL ZONAL STATISTICS</u>
Run the following from the directory containing DEM TIFFs:

```
cd C:\Users\sapmitra\Documents\PostFireDebris\data\SOILS
ls -n | findstr "shp"| %{py C:\Users\sapmitra\PycharmProjects\FireWatcher\data_proc\soils\soils_all_hucs_zonal_stats_single.py $_}
```


## <u>DESIGN STORM</u>

Run the following from the directory containing Design Storm .asc files:

```
cd C:\Users\sapmitra\Documents\PostFireDebris\data\DesignStorm
ls -n | %{py PostFireDebrisRiskAnalysis\arcpy_processing\design_storm_processing\dstorm_huc_zonal_intrc_chk_single.py $_}
```

## <u>COMBINE BOUNDARIES</u>

Use files *PostFireDebrisRiskAnalysis\combine_boundaries\combine\*.py* to combine the various X1, X2, X3 and 
Design Storms for overlapping/duplicate catchment boundaries.

## <u>TH<sub>i15</sub></u>

Run *combine_boundaries/compute_thi15.py* on lattice machines to compute TH<sub>i15</sub>. DNBR (X2) has to be scaled by dividing by 1000.

## <u>POST-FIRE RISK</u>

Run *PostFireDebrisRiskAnalysis\thi15\compare_thi15_DS.py*



# <b><center>INGESTION INTO MONGODB</center></b>
<hr style="border:2px solid gray">


## <u>COMMANDS USED</u>

```
db.createCollection("nhd_shapes")
db.nhd_shapes.createIndex({geometry : "2dsphere"})
db.X1_Elevation.createIndex({"GridCode": 1},{unique: true});
```
## <u>DATA INGESTION</u>

The *PostFireDebrisRiskAnalysis\shape_simplification_ogr\update_grid_script.sh* script excludes/includes any shape-files that
were missed in the previous run due to incompatibility with mongodb and also updates the GridCode and copies it to the upper level
of the json file. 

Following this, data Ingestion is done using the script *PostFireDebrisRiskAnalysis\ingestion_with_check\insert_script_nhd.sh* 
that logs the NHD shapes that were incompatible into the console. 


Computed Attributes relating to each NHD catchment is appended to the corresponding document in the *nhd_shapes* collection using the merge command as below:

```
mongoimport --port 27018 --db sustaindb --collection nhd_shapes --mode merge --upsertFields GridCode --headerline --type csv --file thi15.csv
```

Move the DStorm, THI15, RISK parameters into the *properties* attribute for visualization on Sustain:

```angular2html
db.nhd_test.find().forEach(doc =>
  {
    let id = doc._id;
    let dstorm = doc.DStorm;
    let thi15 = doc.THI15;
    let risk = doc.RISK;
    if (dstorm) {
        db.nhd_test.update({"_id": id}, {$set: {"properties.DStorm": dstorm}});
    }
    if (thi15) {
        db.nhd_test.update({"_id": id}, {$set: {"properties.THI15": thi15}});
    }
    if (risk) {
        db.nhd_test.update({"_id": id}, {$set: {"properties.RISK": risk}});
    }
  }
);
```

Update script to unset *properties.DStorm* for test:

```

db.nhd_test.update({}, {$unset: {'properties.DStorm':1}}, {multi: true});

mongoimport --port 27018 --db sustaindb --collection nhd_test --mode merge --upsertFields GridCode --headerline --type csv --file combined_DS_test.csv 





db.nhd_shapes.updateMany(
{},
[
  {
    $unset: ["properties.DStorm", "properties.THI15", "properties.RISK"] 
  }
])

db.nhd_shapes.updateMany(
{},
[
  {
    $set: {
      "properties.RISK": -1
    }
  }
]);


db.nhd_shapes.updateMany(
{},
[
  {
    $set: {
      "properties.DStorm": "$DStorm",
      "properties.THI15": "$THI15",
      "properties.RISK": "$RISK"
    }
  }
]);





```
