THIS PLUGIN IS CURRENTLY STILL IN DEVELOPMENT. IT IS NOT RECOMMENDED TO USE IT FOR RESEARCH.

# MSA in QGIS
A QGIS plugin that allows the use of the Multiple Scenario Approach and thought experiments in QGIS.

It takes raster or vector polygon maps that have been loaded into QGIS, data on vegetation and pollen, a set of 
deterministic and probabilistic rules and a pollen dispersal model to iteratively generate hypothetical vegetation maps, 
from which it models simulated pollen percentage assemblages using a distance weighting formula. These simulated pollen
assemblages can then be compared to real pollen assemblages in order to identify plausible maps. 

In the case of a full Multiple Scenario Approach reconstruction, the method leans heavily on a large number of iterations
so that the probabilistic rules can introduce variation that the author may not have envisioned. The 

In the case of thought experiments, a more limited number of hypothetical vegetation maps are generated, relying more 
(but not necessarily solely) on the deterministic rules to build maps according to the author's hypothesis. In this case
an existing pollen assemblage is not always necessary.

![Visual Abstract](https://i.imgur.com/DHYgHQ2.png)

## How to use
MSA in QGIS (better name pending, suggestions welcome...) is, as the name currently suggests, a plugin for QGIS. QGIS is an open source
and freely available GIS (geographical information system) that can be downloaded from their website (qgis.org). The plugin
provides a GUI for setting up and running an MSA reconstruction or thought experiment. In a nutshell, to run it you will need:
- GIS maps (raster or polygon) to use as input for your environmental variables
- A list of pollen types and their associated parameters for running a distance weighting model (such as relative pollen productivity and fall speed)
- A set of rules, based on the environmental variables, to place the taxa or vegetation communities onto the map
- (optionally) a set of vegetation communities that determines how the plant taxa are organized
- (optionally) Actual pollen percentages and the coordinates where they were gathered

### Getting started
Download this entire branch of the repository as a zip file. DO NOT UNZIP IT. Under plug-ins --> manage and install 
plugins in QGIS the plugin can then be installed from ZIP. 

### Manual
A more extensive manual is available in the "relevant info" folder.

## Read more about the MSA
### Papers
- [Bunting & Middleton, 2005. Modelling pollen dispersal and deposition using HUMPOL software including simulating windroses and irregular lakes](https://doi.org/10.1016/j.revpalbo.2004.12.009)
- [Bunting & Middleton, 2009. Equifinality and uncertainty in the interpretation of pollen data The MSA to reconstruction of past vegetation mosaics](https://doi.org/10.1177/0959683609105304)

### Websites

### Contributors
- Thya W.B. van den Berg, University of Hull

## Requirements
- QGIS 3.22
