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

from PyQt5.QtCore import QRect, Qt
from PyQt5.QtWidgets import QTableWidgetItem, QWidget, QLineEdit, QLabel, QVBoxLayout, QComboBox, QGridLayout, \
    QDoubleSpinBox, QFrame, QRadioButton, QHBoxLayout, QPushButton, QSpacerItem, QScrollArea, QCheckBox, QMessageBox
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.utils import iface
from qgis.core import *


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'MSA_QGIS_dialog_base.ui'))
FORM_CLASS_TAXA, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'MSA_QGIS_dialog_popup_taxa.ui'))
FORM_CLASS_VEGCOM, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'MSA_QGIS_dialog_popup_vegcom.ui'))
FORM_CLASS_RULES, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'MSA_QGIS_dialog_popup_add_rule.ui'))

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
        self.rule_number = 0

        # class lists & dictionaries
        self.list_cb_rule_veg_com = []
        self.list_cb_env_var = []
        self.list_cb_rule_type = []
        self.nest_dict_rules = {}    # {'rule number': [rule_number(int), vegcom(str), chance(float), n of prev vegcoms(int),
                                # n of env vars(int), # all(bool),
                                # prevvegcom (QTableItem), AND(bool), OR(bool), nextprevvegcom...etc,
                                # envvar (QtableItem), AND(bool), OR(bool), next envvar...etc}

        # UI setup
        self.qgsFileWidget_importHandbag.setFilter('*.hum')
            #create the whole mess that allows scrolling in the rules tab- widgets within widgets within widgets
        self.frameWidget_rules = QFrame(self.scrollArea_rules)
        self.frameWidget_rules.setLayout(self.vLayout_scrollArea)
        self.scrollArea_rules.setWidget(self.frameWidget_rules)

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
        self.pushButton_addRule.clicked.connect(self.addNewRule)



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
        """
        Loads a HUMPOL handbag (.hum) file into the software. This fills in the data (if specified in the file) for:
        Taxa
        Communities
        Sample points
        Windroses
        Metadata
        Notes
        Compatible with the HUMPOL suite (Bunting & Middleton 2005) and LandPolFlow (Bunting & Middleton 2009)
        """
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

    def addNewRule(self):
        """ Allows the dynamic adding of new rules under the rules tab in the main dialog UI."""

        self.add_rule_popup = MsaQgisAddRulePopup(self.rule_number, self.nest_dict_rules, self.tableWidget_vegCom,
                                                  self.tableWidget_selected, self.tableWidget_selRaster)
        self.add_rule_popup.show()

        if self.add_rule_popup.exec_():
            self.rule_number += 1
            # fill the dictionary

            # add the rule to the rule list

class MsaQgisAddRulePopup (QtWidgets.QDialog, FORM_CLASS_RULES):
    def __init__(self, rule_number, nest_dict_rules, tableWidget_vegCom, tableWidget_selected, tableWidget_selRaster, parent = None):
        """Popup Constructor"""
        super(MsaQgisAddRulePopup, self).__init__(parent)
        self.setupUi(self)

        # Class variables
        self.rule_number = rule_number
        self.tableWidget_vegCom = tableWidget_vegCom
        self.tableWidget_selected = tableWidget_selected
        self.tableWidget_selRaster = tableWidget_selRaster
        self.index_latest_layout_vegcom = 1
        self.index_latest_layout_envvar = 3

        # Dictionaries & lists
        self.list_prevVegCom = []
        self.list_envVar = []
        self.nest_dict_rules = nest_dict_rules
        #self.dict_prev_veg_com = {self.comboBox_envVar:[self.doubleSpin_rangeMin, self.doubleSpin_rangeMax, self.comboBox_category]}

        self.dict_rules = {}
        # TODO Create dictionary of rule
            # {'rule number': [rule_number(int), vegcom(str), chance(float), n of prev vegcoms(int),
            # n of env vars(int), # all(bool),
            # prevvegcom (QTableItem), AND(bool), OR(bool), nextprevvegcom...etc,
            # envvar (QtableItem), rangemin (float or NULL), rangemax (~), category (str or NULL), AND(bool), OR(bool), next envvar...etc}

        # self.dict_rules['Rule '+rule_number] =

        # create scrollArea
        self.frameWidget_scroll = QFrame(self.scrollArea)
        self.frameWidget_scroll.setLayout(self.vLayout_total)
        self.scrollArea.setWidget(self.frameWidget_scroll)

        # Set (in)visible
        self.label_rangeMinMax.hide()
        self.doubleSpin_rangeMin.hide()
        self.doubleSpin_rangeMax.hide()
        self.label_category.hide()
        self.comboBox_category.hide()
        self.label_nOfPoints.hide()
        self.spinBox_nOfPoints.hide()
        self.comboBox_condTypePrevVeg.hide()
        self.label_condTypePrevVeg.hide()
        self.comboBox_condTypeEnvVar.hide()
        self.label_condTypeEnvVar.hide()

        # Events
        self.pushButton_condVegCom.clicked.connect(self.addConditionalPrevVegCom)
        self.pushButton_condEnvVar.clicked.connect(self.addConditionalEnvVar)
        self.comboBox_envVar.currentTextChanged.connect(lambda: self.addRangeOrCatToEnvVar(self.comboBox_envVar,
                                                                                   self.label_rangeMinMax,
                                                                                   self.doubleSpin_rangeMin,
                                                                                   self.doubleSpin_rangeMax,
                                                                                   self.label_selectEnvVar,
                                                                                   self.label_category,
                                                                                   self.comboBox_category))
        self.comboBox_rule.currentTextChanged.connect(self.addNofPointsToRule)

        # Fill comboBoxes
        for row in range(self.tableWidget_vegCom.rowCount()):
            self.comboBox_ruleVegCom.addItem(self.tableWidget_vegCom.item(row, 0).text())
            self.comboBox_prevVegCom.addItem(self.tableWidget_vegCom.item(row, 0).text())
        for row in range(self.tableWidget_selected.rowCount()):
            self.comboBox_envVar.addItem(self.tableWidget_selected.item(row, 0).text()+' - '+self.tableWidget_selected.item(row,1).text())
        for row in range(self.tableWidget_selRaster.rowCount()):
            self.comboBox_envVar.addItem(self.tableWidget_selRaster.item(row, 0).text()+' - '+self.tableWidget_selRaster.item(row,1).text())
        #set min & max size for comboBox envVar
        self.label_writtenRule.setText('Rule '+str(rule_number))


    def addRangeOrCatToEnvVar(self, env_var, label_range, rangeMin, rangeMax,label_noChoice, label_category, category): #TODO change to accomodate dynamic buttons
        """ An option to fill in range for the environmental variable appears if the variable is numerical"""
        #get layer associated with current item
        category.clear()
        rangeMin.clear()
        rangeMax.clear()
        if env_var.currentText() == 'Empty':
            label_range.hide()
            rangeMin.hide()
            rangeMax.hide()
            label_noChoice.show()
            label_category.hide()
            category.hide()
        else:
            layer_name = list(re.split(' - ', env_var.currentText()))[0]
            field_or_band = list(re.split(' - |:', env_var.currentText()))[1]
            layer = QgsProject.instance().mapLayersByName(layer_name)[0]
            data_provider = layer.dataProvider()
            if (layer.type() == layer.VectorLayer):
                field_index = data_provider.fieldNameIndex(field_or_band)
                field = data_provider.fields().at(field_index)
                if field.type() == 10 or field.type() == 1: # 10 is str, 1 is bool TODO check if these and int & double are the only options
                    label_range.hide()
                    rangeMin.hide()
                    rangeMax.hide()
                    label_noChoice.hide()
                    label_category.show()
                    category.show()
                    #get categories from fields
                    feat_field = 0
                    for feat in data_provider.getFeatures():
                        if feat_field == 0:
                            feat_field = feat.attribute(field.name())
                            category.addItem(str(feat_field))
                        elif feat_field == feat.attribute(field.name()):
                            pass
                        else:
                            feat_field = feat.attribute(field.name())
                            category.addItem(str(feat_field))

                else:
                    label_range.show()
                    rangeMin.show()
                    rangeMax.show()
                    label_noChoice.hide()
                    label_category.hide()
                    category.hide()
                    #get range from fields
                    rangeMin.setMinimum(data_provider.minimumValue(field_index))
                    rangeMin.setMaximum(data_provider.maximumValue(field_index))
                    rangeMax.setMinimum(data_provider.minimumValue(field_index))
                    rangeMax.setMaximum(data_provider.maximumValue(field_index))
                pass
            elif layer.type() == layer.RasterLayer:
                band_nr = int(list(re.split(' ',field_or_band))[1]) #TODO check if the format 'band [number]:' is consistent for all raster layers!
                if data_provider.dataType(band_nr) != 0: # Checks if band contains numerical data
                    label_range.show()
                    rangeMin.show()
                    rangeMax.show()
                    label_noChoice.hide()
                    label_category.hide()
                    category.hide()
                    #get range from bands
                    stats = data_provider.bandStatistics(band_nr, QgsRasterBandStats.All)
                    minimum_value = stats.minimumValue
                    maximum_value = stats.maximumValue
                    rangeMin.setMinimum(minimum_value)
                    rangeMin.setMaximum(maximum_value)
                    rangeMax.setMinimum(minimum_value)
                    rangeMax.setMaximum(maximum_value)
                else: #NOTE honestly, currently not necessary, unless there is a way to find out if a raster layer is actually categorical...
                    label_range.hide()
                    rangeMin.hide()
                    rangeMax.hide()
                    label_noChoice.hide()
                    label_category.show()
                    category.show()
                    #get categories from band TODO don't think there is currently a way to do this
        pass


    def addNofPointsToRule(self):
        """ Makes a spin box appear when adjacent or encroach is selected under choose rule type"""
        if self.comboBox_rule.currentText() == 'Encroach' or self.comboBox_rule.currentText() == 'Adjacent':
            self.label_nOfPoints.show()
            self.spinBox_nOfPoints.show()
        else:
            self.label_nOfPoints.hide()
            self.spinBox_nOfPoints.hide()
        pass

    def addConditionalPrevVegCom(self, prev_layout):
        """ A comboBox appears from which the user can choose whether they want to apply OR or AND rules, and an
        extra row where an additional previous vegetation community can be chosen appears """
        # combobox and/or
        self.comboBox_condTypePrevVeg.show()
        self.label_condTypePrevVeg.show()
        self.radioButton_all.hide()
        # create new widgets
        comboBox_prevVegCom = QComboBox()
        label_prevVegCom = QLabel()
        pushButton_rmPrevVegCom = QPushButton('Remove conditional')

        #fill combobox
        comboBox_prevVegCom.addItem('Empty')
        for row in range(self.tableWidget_vegCom.rowCount()):
            comboBox_prevVegCom.addItem(self.tableWidget_vegCom.item(row, 0).text())
        #create layouts
        vLayout_prevVegCom = QVBoxLayout()
        vLayout_removeButton = QVBoxLayout()
        hLayout_prevVegCom = QHBoxLayout()
        widget_total = QWidget()
        #fill layouts
        vLayout_prevVegCom.addWidget(label_prevVegCom)
        vLayout_prevVegCom.addWidget(comboBox_prevVegCom)
        vLayout_removeButton.addWidget(pushButton_rmPrevVegCom)
        vLayout_removeButton.insertStretch(0)
        hLayout_prevVegCom.addLayout(vLayout_prevVegCom)
        hLayout_prevVegCom.addLayout(vLayout_removeButton)
        widget_total.setLayout(hLayout_prevVegCom)

        self.vLayout_total.insertWidget(self.index_latest_layout_vegcom + 1, widget_total)
        #event for subsequent remove
        pushButton_rmPrevVegCom.clicked.connect(lambda *args, widget = widget_total:
                                                self.removeConditionalPrevVegCom(widget_total))

        self.index_latest_layout_vegcom +=1

        pass

    def removeConditionalPrevVegCom(self, widget_to_remove):
        """ Removes selected conditionals that were added to the list of previous vegcoms. If all but the
        start prev veg com are gone, the all radioButton reappears and choose condition comboBox type disappears"""
        widget_to_remove.deleteLater()
        self.index_latest_layout_vegcom -=1

        if self.index_latest_layout_vegcom == 1:
            self.comboBox_condTypePrevVeg.hide()
            self.label_condTypePrevVeg.hide()
            self.radioButton_all.show()

    def addConditionalEnvVar(self):
        """ A comboBox appears from which the user can choose whether the want to apply OR or AND rules, and an
        extra row where an additional environmental variable can be chosen appears"""
        self.comboBox_condTypeEnvVar.show()
        self.label_condTypeEnvVar.show()

        # create new widgets
        label_envVar = QLabel()
        comboBox_envVar = QComboBox()
        label_range = QLabel('Range')
        doubleSpin_rangeMin = QDoubleSpinBox()
        doubleSpin_rangeMax = QDoubleSpinBox()
        label_noChoice = QLabel('[No environmental variable selected]')
        label_chooseCategory = QLabel('Category')
        comboBox_category = QComboBox()
        pushButton_rmPrevVegCom = QPushButton('Remove conditional')

        # fill combobox

        # create layouts
        vLayout_envVar = QVBoxLayout()
        vLayout_rangeOrCat = QVBoxLayout()
        hLayout_range = QHBoxLayout()
        vLayout_removeButton = QVBoxLayout()
        hLayout_envVar = QHBoxLayout()
        widget_total = QWidget()

        # fill layouts
        vLayout_envVar.addWidget(label_envVar)
        vLayout_envVar.addWidget(comboBox_envVar)
        vLayout_rangeOrCat.addWidget(label_range)
        hLayout_range.addWidget(doubleSpin_rangeMin)
        hLayout_range.addWidget(doubleSpin_rangeMax)
        vLayout_rangeOrCat.addLayout(hLayout_range)
        vLayout_rangeOrCat.addWidget(label_noChoice)
        vLayout_rangeOrCat.addWidget(label_chooseCategory)
        vLayout_rangeOrCat.addWidget(comboBox_category)
        vLayout_removeButton.addWidget(pushButton_rmPrevVegCom)
        vLayout_removeButton.insertStretch(0)
        hLayout_envVar.addLayout(vLayout_envVar)
        hLayout_envVar.addLayout(vLayout_rangeOrCat)
        hLayout_envVar.addLayout(vLayout_removeButton)
        widget_total.setLayout(hLayout_envVar)
        self.vLayout_total.insertWidget(self.index_latest_layout_envvar+self.index_latest_layout_vegcom, widget_total)

        # hide
        label_range.hide()
        doubleSpin_rangeMin.hide()
        doubleSpin_rangeMax.hide()
        label_chooseCategory.hide()
        comboBox_category.hide()

        # create signals (to hide/show range/category and to remove later
        comboBox_envVar.currentTextChanged.connect(lambda *args, env_var = comboBox_envVar, label_range = label_range, rangeMin =doubleSpin_rangeMin,
                                                          rangeMax = doubleSpin_rangeMax, label_noChoice = label_noChoice,
                                                          label_category = label_chooseCategory,category = comboBox_category:
                                                   self.addRangeOrCatToEnvVar(env_var, label_range, rangeMin, rangeMax,
                                                                              label_noChoice, label_category, category))
        pushButton_rmPrevVegCom.clicked.connect(lambda *args, widget = widget_total:
                                                self.removeConditionalEnvVar(widget))

        self.index_latest_layout_envvar += 1
        pass

    def removeConditionalEnvVar(self, widget):
        widget.deleteLater()
        self.index_latest_layout_envvar -=1

        if self.index_latest_layout_envvar ==1:
            #show and hide where appropriate
            pass


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



