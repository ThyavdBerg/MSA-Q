# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MsaQgis

                                 A QGIS plugin
 This plugin allows the use of the Multi Scenario Approach in QGIS
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-01-14
        copyright            : (C) 2021 by Thya van den Berg
        email                : w.b.van-den-berg-2020@hull.ac.uk
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load MsaQgis class from file MsaQgis.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .MSA_QGIS import MsaQgis
    return MsaQgis(iface)
