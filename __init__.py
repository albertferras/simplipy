# -*- coding: utf-8 -*-
"""
/***************************************************************************
 simplipy
                                 A QGIS plugin
 Simplification tools with many options
                             -------------------
        begin                : 2013-12-22
        copyright            : (C) 2013 by Albert Ferràs
        email                : albert.ferras@gmail.com
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

def classFactory(iface):
    # load simplipy class from file simplipy
    from simplipy import simplipy
    return simplipy(iface)
