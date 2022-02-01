# MSA-QGIS
A QGIS plugin that allows the use of the Multiple Scenario Approach in QGIS.

It takes raster or vector polygon maps that have been loaded into QGIS, data on vegetation and pollen, a set of deterministic and probebalistic rules and a pollen dispersal model to iteratively generate hypothetical vegetation maps and test them against actual pollen counts to find possible vegetation reconstructions.

![Visual Abstract](https://i.imgur.com/DHYgHQ2.png)

## Read more about the MSA
### Papers
- [Bunting & Middleton, 2005. Modelling pollen dispersal and deposition using HUMPOL software including simulating windroses and irregular lakes](https://doi.org/10.1016/j.revpalbo.2004.12.009)
- [Bunting & Middleton, 2009. Equifinality and uncertainty in the interpretation of pollen data The MSA to reconstruction of past vegetation mosaics](https://doi.org/10.1177/0959683609105304)

### Websites

### Contributors

## Requirements
- QGIS 3.x
- Optional: [Python spatialite package](https://pypi.org/project/spatialite/)

## Naming conventions
When participating in this open source project, please keep to the following naming conventions of variables, functions & classes

- Always be descriptive
- English (unless the word is very universally known)
- Only abbreviate when the meaning is clear.

### Variables

- All lower case, underscores between words
- Nouns
- No single letters, including in for loops, unless the single letter has clear meaning
- Change the name of a variable when the data it contains changes significantly

Bad examples: var1, this_shitty_value, bob, asdhfkrkg, XVALUE

Good examples: vector_point_base, rows_column1, layer

Exception: when the variable contains a qt widget, use: widgetType_functionFunction

Examples: comboBox_species, pushButton_removeTaxa

### Functions

- Lower case for first word, then CamelCase, no underscores.
- Verbs + nouns

### Classes

- All CamelCase, no underscores
- If it creates a qt dialog or widget from a .ui file, start name with MsaQgis
