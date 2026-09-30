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

## Unforeseen errors
If an error is not caught within the code of MSA-Q, QGIS will catch it instead. The interface will close or the run will end, and a popup will be opened by QGIS, in which the error type, description, and traceback will be shown. Note that the MSA-Q plugin did not close gracefully and will need to be reloaded. In addition, any files generated as output in a MSA-Q run will likely not be of use.

If an error like this occurs, this always means that there is an issue with the MSA-Q code. Please report the issue on [open an issue on GitHub](https://github.com/ThyavdBerg/MSA-Q/issues), or [contact the authors](contact.html).

## Crashes
This is what happens when QGIS (or your computer!) fully stops responding or shuts down. If this happens before running the plugin, it is most likely a problem with QGIS itself, and should be reported to QGIS rather than the authors of the MSA-Q plugin. If this happens while running the plugin, check the MSA-QGIS.log file for errors. If there is nothing there, it is likely an issue with QGIS. In case of a crash, the most reliable solution is to simple restart QGIS or your computer, and try again. 

Note that the QGIS interface will be blocked while the MSA-Q plugin is running. It will not respond, and may display "not responding" in Windows. This does not mean that QGIS or the plugin has crashed! It simply means that the interface is blocked and you need to wait for it to finish running the model. 

## List of foreseen errors

WORK IN PROGRESS