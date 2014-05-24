# -*- coding: utf-8 -*-
"""
/***************************************************************************
 simplipyDialog
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
"""

from PyQt4 import QtCore, QtGui
from ui_simplipy import Ui_simplipy
# create the dialog for zoom to point


class simplipyDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_simplipy()
        self.ui.setupUi(self)
