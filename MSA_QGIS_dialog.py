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

from PyQt5.QtWidgets import QTableWidgetItem
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.utils import iface
from qgis.core import QgsWkbTypes

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'MSA_QGIS_dialog_base.ui'))


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
        self.extent = None
        self.mExtentGroupBox.setMapCanvas(iface.mapCanvas())
        #self.mExtentGroupBox.setOutputExtentFromDrawOnCanvas() #for some reason causes really weird behaviour.
        # Q asked on GIS stackexchange
        self.mExtentGroupBox.extentChanged.connect(self.setExtent)
        self.getFieldsandBands(self.tableWidget)
        self.tableWidget.itemSelectionChanged.connect(self.updateSelectedRows)


    def setExtent(self):
        """Attaches the extent given by the user to a variable, and updates the 'current extent'
        so that the input can be used in further analysis"""
        self.extent = self.mExtentGroupBox.outputExtent()
        self.mExtentGroupBox.setCurrentExtent(self.extent, self.mExtentGroupBox.outputCrs())

    def getFieldsandBands(self, listTable):
        """Fills a table widget with all fields from vector polygon layers and all bands from raster layers currently
        loaded into the QGIS interface"""
        listTable.clear()
        rowCount = 0
        columnCount = 0
        listTable.setRowCount(rowCount + 1)
        for lyrnr in range(iface.mapCanvas().layerCount()):
            layer = iface.mapCanvas().layer(lyrnr)
            if (layer.type() == layer.VectorLayer) and (layer.geometryType() == QgsWkbTypes.PolygonGeometry):
                provider = layer.dataProvider()
                for field in provider.fields():
                    listTable.setItem(rowCount, columnCount,QTableWidgetItem(layer.name()))
                    columnCount +=1
                    listTable.setItem(rowCount,columnCount, QTableWidgetItem(field.name()))
                    rowCount += 1
                    listTable.setRowCount(rowCount+1)
                    columnCount -=1
            elif layer.type() == layer.RasterLayer:
                continue #fill with bands when vector is functional
            else:
                continue
            listTable.setHorizontalHeaderLabels(['layers', 'fields'])

    def updateSelectedRows(self):
        """ Updates a table widget with the rows selected in another table widget"""
        selectionTable = self.tableWidget_selected
        listTable = self.tableWidget
        selectionTable.setRowCount(len(listTable.selectionModel().selectedRows()))
        rowCount = listTable.rowCount()
        rowCountSel = 0

        for row in range(rowCount):
            if listTable.item(row, 0).isSelected():
                print('row= ', row, 'selection', rowCountSel)
                selectionTable.setItem(rowCountSel,
                                       0,
                                       QTableWidgetItem(listTable.item(row, 0)))
                selectionTable.setItem(rowCountSel,
                                       1,
                                       QTableWidgetItem(listTable.item(row, 1)))
            else:
                continue
            rowCountSel += 1

            # sampItems = {}
            # polyItems = {}
            # rastItems = {}
            #
            # mapCanvas=iface.mapCanvas()
            #
            #
            # for lyrnr in range(mapCanvas.layerCount()):
            #     layer=mapCanvas.layer(lyrnr)
            #     if (layer.type() == layer.VectorLayer) and (layer.geometryType() == QgsWkbTypes.PointGeometry): #this one is technically not necessary as well be using vectorpoint_base
            #         print('points layer', layer.name())
            #         provider = layer.dataProvider()
            #         fields = provider.fields()
            #         theItem = [layer]
            #         for j in fields:
            #             theItem += [[str(j.name()), str(j.name()), False]]
            #         sampItems[str(layer.name())] = theItem
            #         self.inSample.addItem(layer.name())
            #     elif (layer.type() == layer.VectorLayer) and (layer.geometryType() == QgsWkbTypes.PolygonGeometry):
            #         print('polygon layer', layer.name())
            #         provider = layer.dataProvider()
            #         fields = provider.fields()
            #         theItem = [layer]
            #         for j in fields:
            #             theItem += [[str(j.name()), str(j.name()), False]]
            #         polyItems[str(layer.name())] = theItem
            #     elif layer.type() == layer.RasterLayer:
            #         print('raster layer', layer.name())
            #         theItem = [layer]
            #         for j in range(layer.bandCount()):
            #             if layer.bandCount() == 1:
            #                 name1 = layer.bandName(j + 1)
            #                 name2 = layer.name()[:10]
            #             else:
            #                 name1 = layer.bandName(j + 1)
            #                 name2 = layer.name()[:8] + "_" + str(j + 1)
            #             theItem += [[name1, name2, False]]
            #         rastItems[str(layer.name())] = theItem