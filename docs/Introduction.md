# Introduction

MSA-Q is a plugin for QGIS3 that allows the use of the Multiple Scenario Approach using the QGIS interface

The Multiple Scenario Approach is a framework for simulating plausible vegetation maps from pollen percentage data. 
The approach works by taking maps of the environment, such as waterways, height and/or geology, and applying 
probabilistic and deterministic rules to assign certain vegetation types. This assignment is done in an iterative 
way, which means many different vegetation maps are created. From these maps, pollen percentage data is then 
generated for chosen sites using a Pollen Dispersal and Deposition (PDD) model. The generated pollen percentages can 
then be compared to actual pollen percentages, in order to determine which of the simulated vegetation maps are plausible, or can be examined on their own for thought experiments.

The MSA_QGIS plugin was made with the FAIR (Findable, Accessible, Interoperable, Reusable) principles of open 
science in mind. Input and output files are in file formats that are intended to be as accessible, timeless and 
readable as possible, so that they may easily be shared and understood. The software and plugin are free and openly 
available, and the code can be examined and contributed to by everyone (with some moderation, of course). The interface is meant to be user- and beginner friendly, but also flexible. If you use this plugin, please keep the spirit of open science in mind and share your science and data freely if you can.

