---
layout: default
title: Before opening the plugin
---

# Before opening the plugin

## Setting up the coordinate reference system
The coordinate reference system (CRS) should be set to the **projected** coordinate reference system that is most 
accurate for the area of interest. MSA_QGIS will not produce accurate results when using geographical coordinate 
reference systems, as the maths being done in the background will not work with degrees. For more information see 
the [QGIS documentation on coordinate reference systems](https://docs.qgis.org/3.44/en/docs/gentle_gis_introduction/coordinate_reference_systems.html)

## Importing maps
Any maps you would like to use as input for the creation of the simulated vegetation maps need to be imported prior 
to opening the plugin. Raster and vector polygon maps of any file type can be used. For detailed instructions, see 
the [QGIS documentation on opening data](https://docs.qgis.org/3.44/en/docs/user_manual/managing_data_source/opening_data.html).

### Choosing maps to import
* Always be mindful of the final resolution of your model, and whether the resolution of your raster layer or scale 
  of your vector polygon layer matches.
* If you would like to incorporate information from line or point vector layers, these need to be turned into 
  polygon maps first with a buffer. Be mindful of the final resolution of your model.
* MSA-Q currently does not have the capability to place vegetation communities at given coordinates. If you do want to 
place vegetation communities at given coordinates, you need to create a new map layer and draw (or generate) the 
area that you would like to fill prior to running the plugin and then create a rule to fill that polygon at a later 
stage.


