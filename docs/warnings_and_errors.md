---
layout: default
title: warnings and errors
---

THIS PAGE IS A WORK IN PROGRESS

# Warnings and errors

Warnings and errors may occur both when setting up the MSA-Q run using the graphical interface, and during runtime. Warnings are less serious than errors, and either indicate that something may have gone wrong, but not necessarily, or that whatever just went wrong didn't break anything and the action can be re-attempted. Errors are more serious, and generally mean that MSA-Q cannot continue and needs to be reloaded and/or that an MSA run has been aborted. Usually, this means there is an issue with the input, but it may also be serious bug in the code that needs to be addressed. 

## Warnings and errors during input

These are errors and warnings that occur while interacting with the MSA-Q interface. They will show up as a yellow (warning) or red (error) banner in the QGIS interface, in which a description is given of what went wrong. Errors and warnings about the interface are not preserved in MSA_QGIS.log or otherwise written to a file, but can be viewed in the [QGIS Log Messages panel](https://docs.qgis.org/3.44/en/docs/user_manual/introduction/general_tools.html#log-messages-panel). 

![error bar example](assets/images/error_bar_example.png)

*The warning that occurs when attempting to add a rule block to the rule tree, when there are not yet any rules in the rule list.*

## Runtime errors
These are errors that happen after "ok" has been clicked and the MSA-Q model is running. Encountering an error during runtime will end the run, and the "succes dialog" will open, showing that no final output has been created (al values set to 0), or the "error dialog" will open, showing what error occurred. Either way, the error is written to MSA_QGIS.log, and can also be read in the [QGIS Log Messages panel](https://docs.qgis.org/3.44/en/docs/user_manual/introduction/general_tools.html#log-messages-panel). The error message will generally include what type of error occurred, and a short text with a little more detail. If you do not understand the error message or suspect that there is something wrong with the code rather than the input, feel free to [open an issue on GitHub](https://github.com/ThyavdBerg/MSA-Q/issues), or [contact the authors](contact.html).

