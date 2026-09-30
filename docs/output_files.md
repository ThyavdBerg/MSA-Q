---
layout: default
title: Output files
---

# The output files
MSA-Q creates a number of output files. The number and types created will vary based on information given in the [input tabs](main_dialogue_window.html#tabs) and the choice given in the run dialog window, which pops up when "OK" is pressed in the [main dialog window](main_dialogue_window.html).

![run dialog](assets/images/run_dialog.png)

## pointsampled_map.sqlite and pointsampled_map.csv
These files will be created when choosing "create map with point sampled environmental variables" in the run dialog.

pointsampled_map.csv will only be created when "make .csv map copies?" is checked in the [model paramters input tab](model_parameters_input_tab.html).

Both files contain the same information, but in different file formats. Pointsampled_map.sqlite is a SQLite database file, while pointsampled_map.csv is a comma separated text file/spreadsheet. They each contain a single table (named "Empty_basemap" in de sqlite database), which corresponds to a MSA-Q output map to which no vegetation communities have been assigned, but all of the environmental variables from the input maps have been point-sampled. It has six+ columns, which are:

* **msa_id** unique ID for the vector point. Can be used as a primary key.
* **geom_x** the X coordinate of the point in your chosed coordinate reference system.
* **geom_y** the Y coordinate of the point in your chosed coordinate reference system.
* **veg_com** Vegetation communities assigned to the vector points. In this version of the file, these are all set to "Empty"
* **chance_to_happen** This column is used within MSA-Q to determine which point is assigned a certain vegetation community. In this version of the file, all values are set to 0. 
* **map layer (environmental variable) columns** All following columns should be named after the features and bands from map layers you have chosen as input in [the spatial and environmental input tab](spatial_and_environmental_input.html#available-fieldsbands). The values of the points corresponds to the value said input map has at the coordinates of the vector point.

## output_basemap.sqlite and basemap.csv
These files will be created when choosing "create basemap with only base rules from the rule tree" in the run dialog.

Basemap_map.csv will only be created when "make .csv map copies?" is checked in the [model paramters input tab](model_parameters_input_tab.html).

The created files are the same as for the [point sampled map option](#pointsampled_mapsqlite-and-pointsampled_mapcsv), except the veg_com column has been filled according to the rules that belong to the [base group](rule_tree_input_tab.html#designate-as-base-group).

## Map .csv files
These files will only be created when "make .csv map copies?" is checked in the [model paramters input tab](model_parameters_input_tab.html), and when "Run MSA thought experiment (without fit)" or "Run MSA reconstruction (with fit)" have been checked.

For each map created based on the number of iterations and number of scenarios in the rule tree, a .csv map will be created, with the naming convention [scenario]_[iteration] (for example: 1000_1 or 110001101_10). These will be the same as [pointsampled_map.csv](#pointsampled_mapsqlite-and-pointsampled_mapcsv), except the veg_com column has been filled with vegetation communities according to the rules given in the entire [rule tree](rule_tree_input_tab.html).

## Simulated_likelihood_and_landscape.csv
This file is created when either "Run MSA thought experiment (without fit)" or "Run MSA reconstruction (with fit)" has been checked. It contains the fit scores (or: likelihood scores) as well as the landcover percentages for each vegetation community over the entire modelled area. 

The file is a comma separated delimited text file/spreadsheet. It has  7+ columns, which are: 

* **Map_id**: The name of the generated map, which corresponds with the previously mentioned .csv files. 
* **Iteration**: The iteration for which the map was made, which will be the same as the number after the underscore in map_id.
* **Likelihood_met**: A boolean indicating whether both the cumulative and the site-specific likelihood thresholds were met. Values can be yes, no or null. In the case of a thought experiment, it will be null as no fit was calculated.
* **Like_thres_sites**: A copy of [desired fit per site].
* **Like_thres_cumul**: A copy of [desired fit combined].
* **Likelihood_cumul**: Contains the value calculated for fit compared to the actual pollen counts cumulative for all sites. In the case of a thought experiment, this column will be empty.
* **Likelihood columns**: Columns named with a naming convention of likelihood_[site] (e.g. likelihood_samplingpointnorth) that contains the value calculated for fit compared to the actual pollen counts for the specific site. In the case of an MSA "thought experiment", these columns will be empty.
* **Percentage columns**: Columns named with a naming convention of percent_vegetation_[community] (e.g. percent_woodland). This will contain the percentage of coverage per vegetation community for the map in question. This will be a value between 0 and 100. Note that this value can be helpful, but does not tell the entire story, and the spatial distribution of the vegetation communities should be examined as well.

## Simulated_pollen_output.csv
This file is created when either "Run MSA thought experiment (without fit)" or "Run MSA reconstruction (with fit)" has been checked. It contains the simulated pollen percentages for each combination of scenario, iteration and sampling site.

The file is a comma separated delimited text file/spreadsheet. It has  3+ columns, which are: 

* **Map_id**: Same as for [simulated_likelihood_and_landscape.csv](#simulated_likelihood_and_landscapecsv)
* **Site_name**: Name of the site for which the simulated pollen percentages were calculated.
* **Simulated percenage columns**: Columns names with a naming convention of sim_[taxon]_percent (e.g. sim_birch_percent). These contain the simulated pollen percentages for the sampling site, per scenario, per iteration. 

## MSA_output.sqlite
This file is created when either "Run MSA thought experiment (without fit)" or "Run MSA reconstruction (with fit)" has been checked. It is a SQLite database file that contains multiple tables.

### Basemap
This is the same as in [basemap.sqlite](#output_basemapsqlite-and-basemapcsv).

### Dist_dir
This table contains the distance and cardinal direction for every point on the vector grid, to every site.

### Maps
The same as [simulated_likelihood_and_landscape](#simulated_likelihood_and_landscapecsv)

### simulated_pollen
The same as [simulated pollen output](#simulated_pollen_outputcsv)

### PollenLookup
This is the lookup table for distance weighted plant abundance that is created based on the chosen dispersal and deposition model.

### Pseudo_points
This contains information on the points that are created around the sampling sites, in order to avoid overlap between the sampling site and a vector point. See [opening the black box](opening_the_black_box.html#sampling-site-snapping).

### Sampling_sites
This contains a copy of the information the user has given about the sampling points, and which vector point on the map grid the sampling point has snapped to. See [opening the black box](opening_the_black_box.html#sampling-site-snapping).

### Taxa
This is a copy of the information the user has given about the taxa.

### Veg_com
This is a copy of the information the user has given about the vegetation communities, presented in a way that makes it useable as a lookup table.

### Vegcom_list
This contains a list of the vegetation community names.

### Tables for pollen loading
Tables with a naming convention of [Site_name][map_id] (e.g. LakeOntario10000_1). These contain the pollen loading calculated for each taxon, for each vector point and [pseudo point](opening_the_black_box.html#sampling-site-snapping). Note that the pollen loading values are not comparable between projects.

### Tables for maps
Tables with the naming convention of [scenario]_[iteration] (also known as the map_id) are the same as the [map csv files](#map-csv-files).

### Tables for "real" pollen percentages
Tables with the same name as the sampling sites contain a copy of the information the user has given about the pollen percentages for the sampling sites. These tables will only be present when "Run MSA reconstruction (with fit)" has been chosen.

### Further optional tables
Depending on which pollen dispersal and deposition model was used, additional tables may appear with data that facilitates these calculations. An example is a "windrose" table, if the model was run with [windrose weighting](model_parameters_input_tab.html) enabled.

## MSA_QGIS.log
This is a text file that contains the log of what has been happening in the code. If the run went wrong, it will in most cases also contain the [error](warnings_and_errors.html). This file mostly exists to troubleshoot when MSA-Q does not behave as expected. The file can be opened and read in basic text editors.

## temp_ files
Files with the prefix temp_ may remain in the output folder when MSA-Q has encountered an error, or when it was (for whatever reason) not possible to delete these during runtime (for example because the file was opened elsewhere). These files may help diagnose an error, but are otherwise not part of the model output and are not necessary to keep.