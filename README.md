# MSA-QGIS
A plugin that allows the use of the Multiple Scenario Approach in QGIS.

![visual_abstract](https://raw.githubusercontent.com/ThyavdBerg/MSA-QGIS/fdf76fc4f7c7b3e67c0e73bb8cfd56e50770dd14/Relevant%20Info/MSA%20figure.svg?token=ASNU5XQMJU6W6NO4D4745MDB6AYT4)

## Read more about the MSA
### Papers
[Bunting & Middleton, 2009](/Relevant Info/MSA_figure.svg)

### Websites

### Contributors


## Naming conventions
When participating in this open source project, please keep to the following naming conventions of variables, functions & classes

- Always be descriptive
- English (unless the word is very universally known)
- Only abbreviate when the meaning is clear.

### Variables

- All lower case, underscores between words
- Nouns
- No single letters, including in for loops, unless the single letter has meaning
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
- If it creates a qt dialog, start name with MsaQgis
