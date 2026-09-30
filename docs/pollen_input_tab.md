---
layout: default
title: Pollen input tab
---

# Pollen input tab

![pollen input tab](assets/images/pollen_input_tab.png)

## Sample sites
Click "add sampling site" to open a pop-up where a sampling location can be added. Currently four pieces of information are asked for:
* Site name: This should be a concise but unique and descriptive way to identify your site. It should correspond to the name of the site in the csv file with your pollen percentages.
* X and Y coordinate: These should be the coordinates of your site in the form of a point that corresponds in coordinate reference system to the rest of your project. The coordinates should fall within and not be too close to the edge of your [Area of Interest](spatial_and_environmental_input.html#area-of-interest). Make sure to check the X and Y coordinates are not switched around.
* Lake or Point: This point can be ignored in the current build of MSA-Q, as a lake version of the model is not yet implemented. 

![add sampling site](assets/images/add_sampling_site_popup.png)

## Pollen percentage file paths
Once a sampling site has been added, you can click "Import pollen Percentage File" to import your pollen percentages. A pop-up will open where you can select your site from a dropdown based on the sites given in [sample sites](#sample-sites) and then link to the file with the explorer. The only currently accepted format is a csv spreadsheet that follows the Tilia format. This action needs to be repeated for each site, even if the information is in the same spreadsheet. See [input files](input_files.html#pollen-percentages) for the correct configuration of the pollen percentage file.

![add pollen percentages pop-up](assets/images/add_pollen_percentages_popup.png)

The file path is absolute, not relative, and so if the file is shared with someone on another computer, it will need to be reconfigured. When loading an existing MSA-Q save file, if the pollen percentage file is not found the given path, the user is prompted to enter new paths.

## Excerpt pollen percentages
When a pollen percentages file has been added, this section can be used to check if the file was added correctly. Only the first 10 rows of the pollen percentages file are shown. A new tab is created for each sampling site.