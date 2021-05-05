# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MsaQgisDialog
                                 A QGIS plugin
 This plugin allows the use of the Multi Scenario Approach in QGIS
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-01-14
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Thya van den Berg
        email                : w.b.van-den-berg-2020@hull.ac.uk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import re

from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QTableWidgetItem, QWidget, QLineEdit, QLabel, QVBoxLayout, QComboBox, QGridLayout, \
    QDoubleSpinBox, QFrame
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.utils import iface
from qgis.core import QgsWkbTypes


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'MSA_QGIS_dialog_base.ui'))
FORM_CLASS_TAXA, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'MSA_QGIS_dialog_popup_taxa.ui'))
FORM_CLASS_VEGCOM, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'MSA_QGIS_dialog_popup_vegcom.ui'))


### Main dialog window
class MsaQgisDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(MsaQgisDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # class variables
        self.vegcom_row_count = 0
        self.vegcom_column_count = 1
        self.extent = None

        # UI setup
        self.qgsFileWidget_importHandbag.setFilter('*.hum')

        # events
        self.mExtentGroupBox.setMapCanvas(iface.mapCanvas())
        #self.mExtentGroupBox.setOutputExtentFromDrawOnCanvas() #for some reason causes really weird behaviour.
        # Q asked on GIS stackexchange
        self.mExtentGroupBox.extentChanged.connect(self.setExtent)
        self.getFieldsandBands(self.tableWidget_vector, self.tableWidget_raster)
        self.tableWidget_vector.itemSelectionChanged.connect(lambda: self.updateSelectedRows(self.tableWidget_selected,
                                                                                      self.tableWidget_vector))
        self.tableWidget_raster.itemSelectionChanged.connect(lambda: self.updateSelectedRows(self.tableWidget_selRaster,
                                                                                             self.tableWidget_raster))
        self.pushButton_newTaxa.clicked.connect(self.addNewTaxon)
        self.pushButton_newVegCom.clicked.connect(self.addNewVegCom)
        self.pushButton_removeTaxa.clicked.connect(self.removeTaxaEntry)
        self.pushButton_removeVegCom.clicked.connect(self.removeVegComEntry)
        self.pushButton_importHandbag.clicked.connect(self.loadHandbagFile)


    def setExtent(self):
        """Attaches the extent given by the user to a variable, and updates the 'current extent'
        so that the input can be used in further analysis"""
        self.extent = self.mExtentGroupBox.outputExtent()
        self.mExtentGroupBox.setCurrentExtent(self.extent, self.mExtentGroupBox.outputCrs())

    def getFieldsandBands(self, tableWidget_vector, tableWidget_raster):
        """Fills a table widget with all fields from vector polygon layers and all bands from raster layers currently
        loaded into the QGIS interface"""
        tableWidget_vector.clear()
        row_count = 0
        column_count = 0
        tableWidget_vector.setRowCount(row_count + 1)

        tableWidget_raster.clear()
        ras_row_count = 0
        ras_column_count = 0
        tableWidget_raster.setRowCount(ras_row_count + 1)

        for lyr_nr in range(iface.mapCanvas().layerCount()):
            layer = iface.mapCanvas().layer(lyr_nr)
            if (layer.type() == layer.VectorLayer) and (layer.geometryType() == QgsWkbTypes.PolygonGeometry):
                data_provider = layer.dataProvider()
                for field in data_provider.fields():
                    tableWidget_vector.setItem(row_count, column_count, QTableWidgetItem(layer.name()))
                    column_count +=1
                    tableWidget_vector.setItem(row_count, column_count, QTableWidgetItem(field.name()))
                    row_count += 1
                    tableWidget_vector.setRowCount(row_count + 1)
                    column_count -= 1
            elif layer.type() == layer.RasterLayer:
                for band in range(layer.bandCount()):
                    tableWidget_raster.setItem(ras_row_count, ras_column_count, QTableWidgetItem(layer.name()))
                    ras_column_count += 1
                    tableWidget_raster.setItem(ras_row_count, ras_column_count, QTableWidgetItem(layer.bandName(band + 1)))
                    ras_row_count += 1
                    tableWidget_raster.setRowCount(ras_row_count + 1)
                    ras_column_count -= 1
            else:
                continue

            tableWidget_vector.setHorizontalHeaderLabels(['Layers', 'Fields'])
            tableWidget_raster.setHorizontalHeaderLabels(['Layers', 'Bands'])
        tableWidget_vector.setRowCount(row_count)
        tableWidget_raster.setRowCount(ras_row_count)

    def updateSelectedRows(self, tableWidget_selection, tableWidget_list):
        """ Updates a table widget with the rows selected in another table widget"""
        # selectionTable = self.tableWidget_selected
        # listTable = self.tableWidget_vector
        tableWidget_selection.setRowCount(len(tableWidget_list.selectionModel().selectedRows()))
        row_count_sel = 0

        for row in range(tableWidget_list.rowCount()):
            if tableWidget_list.item(row, 0).isSelected():
                tableWidget_selection.setItem(row_count_sel,
                                              0,
                                              QTableWidgetItem(tableWidget_list.item(row, 0)))
                tableWidget_selection.setItem(row_count_sel,
                                              1,
                                              QTableWidgetItem(tableWidget_list.item(row, 1)))
            else:
                continue
            row_count_sel += 1

    def addNewTaxon(self):
        """ Adds a new pollen taxon to the list of taxa by opening a pop-up in which the taxon short and full name,
        fall speed and relative pollen productivity can be given"""
        self.taxonPopup = MsaQgisAddTaxonPopup()
        self.taxonPopup.show()
        result = self.taxonPopup.exec_()
        # runs when apply is clicked on the add new taxon popup
        if result:
            # Get filled in values
            taxon_short_name = self.taxonPopup.lineEdit_taxonShortName.text()
            taxon_full_name = self.taxonPopup.lineEdit_taxonFullName.text()
            taxon_fall_speed = self.taxonPopup.doubleSpinBox_taxonFallSpeed.value()
            taxon_rpp = self.taxonPopup.doubleSpinBox_taxonRPP.value()
            # Check if entry is valid and add to table
            if taxon_short_name and taxon_full_name and taxon_fall_speed and taxon_rpp:
                row_count = self.tableWidget_taxa.rowCount()
                self.tableWidget_taxa.setRowCount(row_count+1)
                self.tableWidget_taxa.setItem(row_count, 0, QTableWidgetItem(taxon_short_name))
                self.tableWidget_taxa.setItem(row_count, 1, QTableWidgetItem(taxon_full_name))
                self.tableWidget_taxa.setItem(row_count, 2, QTableWidgetItem(str(taxon_fall_speed)))
                self.tableWidget_taxa.setItem(row_count, 3, QTableWidgetItem(str(taxon_rpp)))
            else:
                iface.messageBar().pushMessage('Missing value in add new taxon, '
                                                    'please try again', level=1)

    def addNewVegCom(self):
        """ Adds a new vegetation community to the list of communities by opening a pop-up in which a list of species
         and their percentages, as well as a new community name can be given"""
        #pass list of taxa to the popup and open it
        tableWidget_taxa = self.tableWidget_taxa
        item_list = [tableWidget_taxa.item(row,0).text() for row in range(tableWidget_taxa.rowCount())]
        self.veg_com_popup = MsaQgisAddVegComPopup(item_list)
        tableWidget_vegCom = self.tableWidget_vegCom

        #add entries to table
        result = self.veg_com_popup.exec_()
        if result:
            self.vegcom_row_count += 1
            tableWidget_vegCom.setRowCount(self.vegcom_row_count)
            tableWidget_vegCom.setItem(self.vegcom_row_count - 1, 0, QTableWidgetItem(
                self.veg_com_popup.lineEdit_vegComName.text()))

            #Check if a taxon already had a column, add new column only for a new taxon
            #Create list of taxa that already have a column
            header_list = [tableWidget_vegCom.horizontalHeaderItem(column).text() for column in range(1, tableWidget_vegCom.columnCount())]
            for taxon in range(len(self.veg_com_popup.vegcom_taxon_combo_list)):
                if self.veg_com_popup.vegcom_taxon_combo_list[taxon].currentText() in header_list:
                    # get column number of named column
                    for column in range(tableWidget_vegCom.columnCount()):
                        header_text = tableWidget_vegCom.horizontalHeaderItem(column).text()
                        if header_text == self.veg_com_popup.vegcom_taxon_combo_list[taxon].currentText():
                            tableWidget_vegCom.setItem(self.vegcom_row_count - 1, column, QTableWidgetItem(
                                str(self.veg_com_popup.vegcom_taxon_double_list[taxon].value())))
                    # add value at right location to that column
                    pass
                elif self.veg_com_popup.vegcom_taxon_combo_list[taxon] not in header_list:
                    self.vegcom_column_count += 1
                    self.tableWidget_vegCom.setColumnCount(self.vegcom_column_count)
                    # set header of new column
                    tableWidget_vegCom.setHorizontalHeaderItem(self.vegcom_column_count - 1, QTableWidgetItem(
                                self.veg_com_popup.vegcom_taxon_combo_list[taxon].currentText()))
                    # add value to new column
                    tableWidget_vegCom.setItem(self.vegcom_row_count - 1, self.vegcom_column_count - 1, QTableWidgetItem(
                        str(self.veg_com_popup.vegcom_taxon_double_list[taxon].value())))
                else:
                    print('error in creating veg com columns')

    def removeTaxaEntry(self):
        """ Removes selected entries from a table with a pop-up warning"""
        # popup
        pass #TODO create pop-up warning


        #get selection
        tableWidget_taxa = self.tableWidget_taxa
        for row in tableWidget_taxa.selectionModel().selectedRows():
            tableWidget_taxa.removeRow(row.row())

    def removeVegComEntry(self):
        """ Removes selected entries from a table with a pop-up warning"""
        #Popup
        pass #TODO create pop-up warning


        #remove row
        tableWidget_vegCom = self.tableWidget_vegCom
        columns_to_remove = []

        if tableWidget_vegCom.selectionModel().selectedRows():
            for row in tableWidget_vegCom.selectionModel().selectedRows():
                tableWidget_vegCom.removeRow(row.row())
                self.vegcom_row_count -= 1
        #remove columns that no longer contain data after the row was removed
        for column in range(1,tableWidget_vegCom.columnCount()):
            item_list = []
            for row in range(tableWidget_vegCom.rowCount()):
                if tableWidget_vegCom.item(row,column):
                    item_list.append(tableWidget_vegCom.item(row,column))
            if not item_list:
                columns_to_remove.append(column)
            else:
                continue
        for list_item in columns_to_remove:
            tableWidget_vegCom.removeColumn(list_item)
            self.vegcom_column_count -= 1
            tableWidget_vegCom.setColumnCount(self.vegcom_column_count)

    def loadHandbagFile(self):
        #TODO sample points, windrose data, metadata, notes
        file_name = self.qgsFileWidget_importHandbag.filePath()
        tableWidget_vegCom = self.tableWidget_vegCom
        if not os.path.isfile(file_name):
            print('file does not exist')
        else:
            with open(file_name) as file:
                for line in file:
                    if line[0] == '1':
                        if int(line[:4]) >= 1100:
                            line = line[5:]
                            line_list = list(re.split('\t|\n', line))
                            row_count = self.tableWidget_taxa.rowCount()
                            self.tableWidget_taxa.setRowCount(row_count + 1)
                            self.tableWidget_taxa.setItem(row_count, 0, QTableWidgetItem(line_list[0]))
                            self.tableWidget_taxa.setItem(row_count, 1, QTableWidgetItem(line_list[1]))
                            self.tableWidget_taxa.setItem(row_count, 2, QTableWidgetItem(str(line_list[2])))
                            self.tableWidget_taxa.setItem(row_count, 3, QTableWidgetItem(str(line_list[3])))
                    elif line[0] == '2': #communities
                        # skip community names (TODO but what to do if a handbag file has multiple community files?)
                        if 2200 <= int(line[:4]) < 2300:
                            line = line[7:]
                            line = line.replace('\n','')
                            self.vegcom_row_count += 1
                            tableWidget_vegCom.setRowCount(self.vegcom_row_count)
                            tableWidget_vegCom.setItem(self.vegcom_row_count - 1, 0, QTableWidgetItem(
                                line))
                        elif int(line[:4]) >= 2300:
                            line = line[5:]
                            line_list = list(re.split('\t|\n', line))
                            # Only create a new column if the header does not yet exist note: this is a duplicate from addNewVegCom
                            header_list = [tableWidget_vegCom.horizontalHeaderItem(column).text() for column in
                                           range(1, tableWidget_vegCom.columnCount())]


                            if line_list[0] in header_list:
                                # get column number of named column
                                for column in range(tableWidget_vegCom.columnCount()):
                                    header_text = tableWidget_vegCom.horizontalHeaderItem(column).text()
                                    if header_text == line_list[0]:
                                        tableWidget_vegCom.setItem(self.vegcom_row_count - 1, column,
                                                                   QTableWidgetItem(line_list[1]))
                                # add value at right location to that column
                                pass
                            elif line_list[0] not in header_list:
                                self.vegcom_column_count += 1
                                self.tableWidget_vegCom.setColumnCount(self.vegcom_column_count)
                                # set header of new column
                                tableWidget_vegCom.setHorizontalHeaderItem(self.vegcom_column_count - 1,
                                                                           QTableWidgetItem(line_list[0]))
                                # add value to new column
                                tableWidget_vegCom.setItem(self.vegcom_row_count - 1, self.vegcom_column_count - 1,
                                                           QTableWidgetItem(
                                                               str(line_list[1])))
                            else:
                                print('error in creating veg com columns')

                        pass
                    elif line[0] == '3': #sample points
                        pass

                file.close()


class MsaQgisAddTaxonPopup (QtWidgets.QDialog, FORM_CLASS_TAXA):
    def __init__(self, parent=None):
        """Popup Constructor."""
        super(MsaQgisAddTaxonPopup, self).__init__(parent)
        self.setupUi(self)


class MsaQgisAddVegComPopup (QtWidgets.QDialog, FORM_CLASS_VEGCOM):
    def __init__(self, taxonlist, parent=None):
        """Popup Constructor."""
        super(MsaQgisAddVegComPopup, self).__init__(parent)
        self.setupUi(self)
        #events
        self.pushButton_vegComAddSpecies.clicked.connect(self.addVegComTaxonRow)

        #class variables
        self.previous = 0
        self.taxon_list = taxonlist
        self.vegcom_taxon_double_list = []
        self.vegcom_taxon_combo_list = []


        #add gridlayout to scrollarea
        self.frameWidget_scroll = QFrame(self.scrollArea)
        self.frameWidget_scroll.setLayout(self.gridLayout)
        self.scrollArea.setWidget(self.frameWidget_scroll)

        #set locations of original widgets in grid (because Qt designer won't bloody work with me)

        self.gridLayout.addWidget(self.label_Title, 0, 0, 1, 4)
        self.gridLayout.addWidget(self.label_Name, 1, 0)
        self.gridLayout.addWidget(self.lineEdit_vegComName, 1, 1, 1, 4)
        self.gridLayout.setRowStretch(2, 100) #stretch middle row to maximum possible size
        self.gridLayout.addWidget(self.pushButton_vegComAddSpecies, 3, 0, 1, 4)
        self.gridLayout.addWidget(self.buttonBox_2, 4, 1, 1, 3)
        self.gridLayout.addWidget(self.buttonBox_2, 5, 0, 1, 4)

    def addVegComTaxonRow(self):
        """ Adds a new comboBox and doubleSpinBox to be able to add a new taxon to a vegetation community"""
        label = QLabel('Taxon ' + str(int((self.previous * 0.5)+1)), self)
        self.comboBox = QComboBox()
        self.doubleSpin = QDoubleSpinBox()
        # insert the new widgets
        self.gridLayout.addWidget(label, self.previous+2, 0, 1, 4)
        self.gridLayout.addWidget(self.comboBox, self.previous+3, 0, 1, 3)
        self.gridLayout.addWidget(self.doubleSpin, self.previous+3, 3, 1, 2)
        self.gridLayout.setRowStretch(self.previous + 2, 0)  # reset stretch of previously stretched row
        self.gridLayout.setRowStretch(self.previous + 4, 100)  # set new middle row to maximum stretch
        # move the widgets below to new location
        self.gridLayout.addWidget(self.pushButton_vegComAddSpecies, self.previous + 5, 0, 1, 4)
        self.gridLayout.addWidget(self.buttonBox_2, self.previous + 6, 0, 1, 4)
        self.previous += 2
        # Fill the comboBox
        self.comboBox.addItems(self.taxon_list)
        # Create list of items to pass to the main dialog
        self.vegcom_taxon_combo_list.append(self.comboBox)
        self.vegcom_taxon_double_list.append(self.doubleSpin)



