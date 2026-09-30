---
layout: default
title: Save files
---

# Save files

There are three save files associated with MSA-Q. They are saved together in a folder and should ideally be kept together, but can be saved and loaded individually if so desired. In addition, an image of the rule tree can be saved. The names of the save files should not be changed, instead, name the folder that the save files are stored in so that you can identify your project.

The save files should be provided with any publication for reproducibility purposes, along with the other [input files](input_files.html). 

![MSA-Q save dialog](assets/images/save_dialog.png)

## Input state and environmental data (inputstate.csv)
This file contains all input except for the rules and rule tree. The format is a delimited text (comma separated value) format that can be read (and edited) in your chosen text or spreadsheet editor without having to load the file into the plugin.

This save file can be edited manually. So long as the structure and data types are correct, MSA-Q will load the file correctly. 

## Rule list (ruledict.pkl)
This file contains a list of the rules in the form of a python dictionary. The format is a pickled python dictionary (.pkl). Note that the rules are dependent on the input from the [input state](#input-state-and-environmental-data-inputstatecsv) file. 

Since this file is not as easy to read without access to QGIS and the MSA-Q plugin, the text of the rules is also included in the [inputstate file](#input-state-and-environmental-data-inputstatecsv), however that file is **not** used to load the rules.

## Rule tree (ruletree.pkl)
This file contains the rule tree. Note that it is dependent on the correct matching information in the [rule list](#rule-list-ruledictpkl) and it is strongly recommended not to separate these files.

Since this file is not as easy to read without access to QGIS and the MSA-Q plugin, an [image of the rule tree](#image-of-rule-tree-ruletreeimagetiff) can also be saved.

## Image of rule tree (ruletreeimage.tiff)
This is not a save file, but an image of the rule tree. Since the rule tree save file is not as easy to read and edit as the input state file, this image is provided in case the project needs to be reproduced in a non-compatible version of MSA-Q in the future, or the rule tree needs to be reviewed without access to QGIS and the MSA-Q plugin.

## QGIS project
Next to the MSA-Q plugin, you will have a QGIS project open. Important for the MSA-Q run in this QGIS project is the Coordinate reference system you have set, and the loaded input map layers. Other information can be added to the QGIS project (for example visualizations, additional maps, map layouts, etc.) but will be ignored by MSA-Q. It is important to save this QGIS project in addition to your MSA-Q save files, which needs to be done in the main QGIS interface, [see the QGIS documentation](https://docs.qgis.org/3.44/en/docs/user_manual/introduction/project_files.html) for more information. 

Note that QGIS does not automatically also save editing in map layers when the project is saved, these [also need to be saved](https://docs.qgis.org/3.44/en/docs/user_manual/working_with_vector/editing_geometry_attributes.html#saving-edited-layers).