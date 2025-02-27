The current release (0.1.0) has been tested in comparison to HUMPOL_0 and in a single case study; It is suitable for use, but bugs and unexpected behaviours may exist and several planned features are not yet implemented. Issue reports, contributions and suggestions are very welcome.
# MSA in QGIS (MSA-Q)
This is a plugin that adds the Multiple Scenario Approach to landcover reconstruction using pollen to QGIS.

It takes raster or vector polygon maps that have been loaded into QGIS, data on vegetation and pollen, a set of 
deterministic and probabilistic rules and a pollen dispersal model to iteratively generate hypothetical vegetation maps, 
from which it models simulated pollen percentage assemblages using a distance weighting formula. These simulated pollen
assemblages can then be compared to real pollen assemblages in order to identify plausible maps. 

In the case of a full Multiple Scenario Approach reconstruction, the method leans heavily on a large number of iterations
so that the probabilistic rules can introduce variation that the author may not have envisioned. 

In the case of thought experiments, a more limited number of hypothetical vegetation maps are generated, relying more 
(but not necessarily solely) on the deterministic rules to build maps according to the author's hypothesis. In this case
an existing pollen assemblage is not always necessary.

![Visual Abstract](https://i.imgur.com/DHYgHQ2.png)

## How to use
MSA-Q is, as the name currently suggests, a plugin for QGIS. QGIS is an open source
and freely available GIS (geographical information system) that can be downloaded from their website (qgis.org). The plugin
provides a GUI for setting up and running an MSA reconstruction or thought experiment. In a nutshell, to run it you will need:
- GIS map layers (raster or polygon) to use as input for your environmental variables
- A list of pollen types and their associated parameters for applying a Pollen Dispersal and Deposition model (currently only the Prentice Mire model is implemented)
- A set of rules, based on the environmental variables, to place the taxa or vegetation communities onto the map
- (optionally) A set of vegetation communities that determines how the plant taxa are organized
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
- Van den Berg, 2025 (in prep). Refining Reconstruction: Discovering the capabilities and limitations of pollen analysis using the Multiple Scenario Approach

### Websites

### Contributors
- Thya W.B. van den Berg, University of Hull
- M. Jane Bunting, Univeristy of Hull

## Requirements
- QGIS 3.22 or more recent versions of QGIS 3.xx
