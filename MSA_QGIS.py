# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MsaQgis
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QVariant
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import *
from qgis.utils import iface

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .MSA_QGIS_dialog import MsaQgisDialog
import os.path
import sys

# Import processing tools from Qgis (make sure python interpreter contains path C:\OSGeo4W64\apps\qgis\python\plugins)
from os.path import expanduser
home = expanduser("~")
sys.path.append(home + '\OSGeo4W64\apps\qgis\python\plugins')
import processing
from processing.core.Processing import Processing
Processing.initialize()


class MsaQgis:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'MsaQgis_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&MSA QGIS')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('MsaQgis', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/MSA_QGIS/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Multi Scenario Approach'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&MSA QGIS'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = MsaQgisDialog()


        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:

### Create the base point layer with resolution and extent given by user
            # with help from https://howtoinqgis.wordpress.com/2016/10/30/how-to-generate-regularly-spaced-points-in-qgis-using-python/
            layer = iface.activeLayer() #active layer currently has to be in a projection that uses meters, like pseudomercator
            spacing = self.dlg.spinBox_resolution.value() #Takes input from user in "resolution" to set spacing
            inset = spacing * 0.5 #set inset

            #get Coordinate Reference System and extent (for method 1)
            crs = layer.crs()
            # ext = layer.extent()

            #Create new vector point layer
            vectorpoint_base = QgsVectorLayer('Point', 'Name', 'memory', crs=crs,)
            data_provider = vectorpoint_base.dataProvider()

            #Set extent of the new layer
            if self.dlg.extent is None:
                self.iface.messageBar().pushMessage('Extent not chosen!', level=1)
            else:
                self.iface.messageBar().pushMessage('Extent set!', level=0)
                xmin = self.dlg.extent.xMinimum() + inset
                xmax = self.dlg.extent.xMaximum()
                ymin = self.dlg.extent.yMinimum()
                ymax = self.dlg.extent.yMaximum() - inset
            # If I get the QgsExtentComboBox working, code below will be removed
            # if self.dlg.comboBox_area_of_interest.currentText() == "Use active layer":
            #     # Method 1 uses active layer
            #      xmin = ext.xMinimum() + inset
            #      xmax = ext.xMaximum()
            #      ymin = ext.yMinimum()
            #      ymax = ext.yMaximum() - inset
            # else:
            #     #Method 2 uses user input
            #     xmin = self.dlg.spinBox_west.value() + inset
            #     xmax = self.dlg.spinBox_east.value()
            #     ymin = self.dlg.spinBox_south.value()
            #     ymax = self.dlg.spinBox_north.value() - inset


            #Create the coordinates of the points in the grid
                points = []
                y = ymax
                while y >= ymin:
                    x = xmin
                    while x <= xmax:
                        geom = QgsGeometry.fromPointXY(QgsPointXY(x,y))
                        feat = QgsFeature()
                        feat.setGeometry(geom)
                        points.append(feat)
                        x += spacing
                    y = y-spacing
                data_provider.addFeatures(points)
                vectorpoint_base.updateExtents()


### Add fields with x and y geometry
            data_provider.addAttributes([QgsField('geom_X', QVariant.Double, 'double', 20,5),
                                         QgsField('geom_Y', QVariant.Double, 'double', 20,5),
                                         QgsField('MSA-ID', QVariant.Int)])
            vectorpoint_base.updateFields()
            vectorpoint_base.startEditing()
            for feat in vectorpoint_base.getFeatures():
                geom= feat.geometry()
                feat['geom_X'] = geom.asPoint().x()
                feat['geom_Y'] = geom.asPoint().y()
                feat['MSA-ID'] = feat.id()
                vectorpoint_base.updateFeature(feat)
            vectorpoint_base.commitChanges()


### Use processing tools to fill vectorpoint_base with fields/bands from selected in UI
# Point sample the vector layers using join attributes by location processing algorithm
# (id: qgis:joinattributebylocation)
            vectorpoint_polygon = vectorpoint_base
            selection_table = self.dlg.tableWidget_selected
            for rows_column1 in range(selection_table.rowCount()):
                print('forloop 1')
                layer_name = selection_table.item(rows_column1, 0).text()
                previous_row = selection_table.item(rows_column1-1, 0)
                fields = []

                #find the next layer name in the list, if it exists
                for rows_column3 in range((selection_table.rowCount())+1):
                    print('forloop 2')
                    next_name = selection_table.item(rows_column3, 0)
                    if rows_column3 <= rows_column1: #ignore layers under current row
                        pass
                    elif next_name == None: #There is no next layer in the list
                        next_row = selection_table.item(rows_column3, 0)
                        break
                    elif layer_name == next_name.text(): #Next row in the list is for the same layer, ignore
                        pass
                    elif layer_name != next_name.text(): #There is a next layer in the list
                        next_row = selection_table.item(rows_column3, 0)
                        break
                    else:
                        print('something went wrong in finding the next layer name')
                        break

                # Check if a new layer name in the table was reached and that that is NOT the last layer in the list
                # Skip if that layer was already processed due to being in previous row
                if (previous_row == None or previous_row.text() != layer_name)\
                        and next_row != None:
                    layer = QgsProject.instance().mapLayersByName(layer_name)[0]
                    for rows_column2 in range(selection_table.rowCount()):
                        print('forloop 3')
                        if selection_table.item(rows_column2, 0).text() == layer_name:
                            field = selection_table.item(rows_column2, 1).text()
                            fields.append(field)
                    processing_saved=processing.run('qgis:joinattributesbylocation',
                                    {'INPUT': vectorpoint_polygon,
                                     'JOIN': layer,
                                     'METHOD': 0,
                                     'PREDICATE': 0,
                                     'JOIN_FIELDS': fields,
                                     'OUTPUT': 'memory:'})
                    vectorpoint_polygon = processing_saved['OUTPUT']

                # Make sure that the last layer in the list has been reached
                elif next_row == None:
                    # Then print the last added layer to an actual output file
                    layer = QgsProject.instance().mapLayersByName(layer_name)[0]
                    for rows_column2 in range(selection_table.rowCount()):
                        print('forloop 4')
                        if selection_table.item(rows_column2, 0).text() == layer_name:
                            field = selection_table.item(rows_column2, 1).text()
                            fields.append(field)
                    outputfile = self.dlg.mQgsFileWidget.filePath()+'vector.shp'
                    processing.run('qgis:joinattributesbylocation',
                                    {'INPUT': vectorpoint_polygon,
                                     'JOIN': layer,
                                     'METHOD': 0,
                                     'PREDICATE': 0,
                                     'JOIN_FIELDS': fields,
                                     'OUTPUT': outputfile})
                    break

                elif previous_row.text() == layer_name:
                    pass
                else:
                    print(layer_name)
                    print('something went wrong around the processing algorithm')
                    break

# Point sample the raster layers using sample raster values processing algorithm
# (id: qgis:rastersampling)
            vectorpoint_raster = vectorpoint_base
            selection_table = self.dlg.tableWidget_Sel_Raster
            for rows_column1 in range(selection_table.rowCount()):
                layer_name = selection_table.item(rows_column1, 0).text()
                previous_row = selection_table.item(rows_column1-1, 0)
                fields = []

                #find the next layer name in the list, if it exists
                for rows_column3 in range((selection_table.rowCount())+1):
                    next_name = selection_table.item(rows_column3, 0)
                    if rows_column3 <= rows_column1: #ignore layers under current row
                        pass
                    elif next_name == None: #There is no next layer in the list
                        next_row = selection_table.item(rows_column3, 0)
                        break
                    elif layer_name == next_name.text(): #Next row in the list is for the same layer, ignore
                        pass
                    elif layer_name != next_name.text(): #There is a next layer in the list
                        next_row = selection_table.item(rows_column3, 0)
                        break
                    else:
                        print('something went wrong in finding the next layer name - raster')
                        break

                # Check if a new layer name in the table was reached and that that is NOT the last layer in the list
                # Skip if that layer was already processed due to being in previous row
                if (previous_row == None or previous_row.text() != layer_name)\
                        and next_row != None:
                    layer = QgsProject.instance().mapLayersByName(layer_name)[0]
                    for rows_column2 in range(selection_table.rowCount()):
                        if selection_table.item(rows_column2, 0).text() == layer_name:
                            field = selection_table.item(rows_column2, 1).text()
                            fields.append(field)
                    processing_saved=processing.run('qgis:rastersampling',
                                    {'INPUT': vectorpoint_raster,
                                     'RASTERCOPY': layer,
                                     'COLUMN_PREFIX': layer_name[:5],
                                     'OUTPUT': 'TEMPORARY_OUTPUT:'})
                    vectorpoint_raster = processing_saved['OUTPUT']

                # Make sure that the last layer in the list has been reached
                elif next_row == None:
                    # Then print the last added layer to an actual output file
                    layer = QgsProject.instance().mapLayersByName(layer_name)[0]
                    for rows_column2 in range(selection_table.rowCount()):
                        if selection_table.item(rows_column2, 0).text() == layer_name:
                            field = selection_table.item(rows_column2, 1).text()
                            fields.append(field)
                    outputfile_ras = self.dlg.mQgsFileWidget.filePath()+'raster.shp'
                    processing.run('qgis:rastersampling',
                                    {'INPUT': vectorpoint_raster,
                                     'RASTERCOPY': layer,
                                     'COLUMN_PREFIX': layer_name[:5],
                                     'OUTPUT': outputfile_ras})
                    break

                elif previous_row.text() == layer_name:
                    pass
                else:
                    print(layer_name)
                    print('something went wrong around the processing algorithm')
                    break

# Create layers for output files (may replace with direct reference to files instead)
            vectorpoint_filled_vec = QgsVectorLayer(outputfile, 'final', 'ogr')
            vectorpoint_filled_ras = QgsVectorLayer(outputfile_ras, 'final_ras', 'ogr')

# Join tables - add if statement to skip for no vector layers or no raster layers
            join_info = QgsVectorLayerJoinInfo()
            join_info.setJoinLayer(vectorpoint_filled_vec)
            join_info.setJoinFieldName('MSA-ID')
            join_info.setTargetFieldName('MSA-ID')
            join_info.setUsingMemoryCache(True)
            join_info.setJoinFieldNamesBlockList(['geom_X', 'geom_Y'])
            vectorpoint_filled_ras.addJoin(join_info)
# add to map canvas
            QgsProject.instance().addMapLayer(vectorpoint_filled_ras)

            #...
            pass

