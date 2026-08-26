---
layout: default
title: Installation
---

# Installation

### Install QGIS

As MSA-Q is a plugin for QGIS, installing QGIS is required. QGIS is a free and open source GIS (Geographical 
Information System) that is updated regularly.
QGIS can be downloaded from their [website](https://qgis.org). The manner in which it is installed (through OSGEO4W or 
regular/quick install) does not matter for running MSA-Q. [^1] 

#### versions
MSA-Q was produced and tested using QGIS LTR versions 3.22 and 3.34. Any version of QGIS 3 after 3.22 should run 
MSA-Q without problems. MSA-Q has NOT yet been tested for QGIS4.

### Install MSA-Q in QGIS
Currently there is only one way to install the MSA-Q plugin in QGIS.

#### A zipped file from the respository
A zip-folder containing MSA-Q can be downloaded in two ways:
* From the [releases](https://github.com/ThyavdBerg/MSA-Q/releases) on Github. This ensures you have a specific 
  version of the plugin, but it may not be the most recent version with the most recent bugfixes. The goal is to 
  have all versions that were actually used in research represented here, in order to serve reproducibility. Release 
  names correspond broadly to the project or publication it was used in.
* Directly from the [main branch](https://github.com/ThyavdBerg/MSA-Q) on GitHub. Ensure you are on the main branch 
  by checking which branch you have selected, and then click on 
  the "<> code" dropdown and select "download ZIP". This ensures you have to most recent, tested version.

Save the ZIP folder to a place where you know you can find it again, such as with your research project 
files or a dedicated QGIS plugin folder. 
The ZIP folder should have the name MSA-Q-main.zip if it was downloaded from the main branch, or MSA-Q-[version].zip if 
it was downloaded from the releases page (provided that you have not renamed it upon downloading). To install the 
plugin in QGIS, follow these steps:    

1. Open QGIS
2. Go to "plugins" in the menu toolbar.
3. Open "manage and install plugins"
4. Click "install from ZIP"
5. Click the ellipsis and find the zip folder containing MSA-Q in your file explorer.
6. Click install plugin

You may receive a warning on installing external plugins.  [^2]

A new, small icon should have appeared in the toolbar. If it has not, make sure the plugin toolbar is turned on by 
going to "view" -> "toolbars" -> check "plugin toolbar". A new option "MSA-Q" should also have appeared in the 
"plugin" downdown menu.

### Footnotes


[^1]: For development it is recommended to install QGIS through OSGEO4W.

[^2]: For more information on installing QGIS plugins, check the [QGIS documentation](<https://docs.qgis.org/3.44/en/docs/user_manual/plugins/plugins.html>).