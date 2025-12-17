### MSA_QGIS.py
The main file containing the majority of the code that runs the actual model. 
Both the necessary setup to connect to QGIS, and what the model does after you press "run" are in this file.

### MSA_QGIS_Main_ms_subprocess.py
This file continues on from MSA_QGIS.py, and contains the parts that are multiprocessed. This is, in essence, where the 
rules are processed, maps are created, and pollen are simulated, when running a partial or full MSA.

### MSA_QGIS_custom_sql_methods.py
Contains functions that sqlite does not have, that needed to be added manually. They are used in MSA_QGIS.py

### MSA_QGIS_dialog.py
Contain the python code for how the UI functions. This adds functionality to the base UI, which were made in Qt5 and are found in the various .ui files.

### MSA_QGIS_custom_widget_frame_rule_tree.py
Contains a custom QTwidget. It is an adjusted QTFrame that contains the rule tree. It is used in MSA_QGIS_dialog.py.

### MSA_QGIS_custom_widget_rule_tree.py
Contains custom QTwidgets for the rule tree. It is used in MSA_QGIS_dialog.py.

### MSA_QGIS_distance_weighting_sql_methods.py
Contains functions for distance weighting. Essentially, this is where the spatial pollen models live.

### MSA_QGIS_... .ui
Various QT5 UI files that contain dialog boxes and popups.

### metadata.txt
File that is used to display metadata of the plugin within QGIS.

### All other files
All of the other files are files that are related to compiling the code, and making the plugin work. They are explained in the documentation of the QGIS plugin builder (by G. Sherman) which can be found here: [plugin builder](https://g-sherman.github.io/Qgis-Plugin-Builder/)