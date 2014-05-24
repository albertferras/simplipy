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
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import QDomDocument
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from simplipydialog import simplipyDialog
from afcsimplifier.simplifier import ChainDB
from afcsimplifier.douglaspeucker import douglaspeucker
from afcsimplifier.visvalingam import visvalingam
import StringIO
import binascii
import os.path
import traceback
import sys

starting_points_qobj = { # TODO PARSE AND USE IN CHAINDB
    ChainDB.STARTING_POINT_FIRSTANDLAST: 'option_douglas_firstandlast',
    ChainDB.STARTING_POINT_FIRSTANDFURTHEST: 'option_douglas_firstandfurthest',
    ChainDB.STARTING_POINT_DIAMETERPOINTS: 'option_douglas_diameterpoints',
}

simplify_algorithms = {
    "douglas": {
        'function': douglaspeucker,
        'parameters': {
            'epsilon': {'QObject': 'option_epsilon',
                        'format': float,
                        'format_description': "Epsilon must be a number greater than 0.0",
                        'validate': lambda e: 0.0 < e,
                        },
        }
    },
    "visvalingam": {
        "function": visvalingam,
        'parameters': {
            'minArea': {'QObject': 'option_minarea',
                        'format': float,
                        'format_description': "MinArea must be a number greater than 0.0",
                        'validate': lambda area: 0.0 < area,
                     }
        }
    },
}

class ExceptNoTraceback(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        Exception.__init__(self, message)

def exception_format(e):
    msg = str(e)
    msg += "\n-----------\n"
    try:
        f = StringIO.StringIO()
        traceback.print_exc(file=f)
        sh = f.getvalue()
        sh = str(sh)
        print sh
    except Exception:
        traceback.print_exc()
        sh = "traceback didnt work"
    msg += sh
    return msg


def exception_format2(e):
    """Convert an exception object into a string,
    complete with stack trace info, suitable for display.
    """
    info = "".join(traceback.format_tb(sys.exc_info()[2]))
    return str(e) + "\n\n" + info

def debug(x):
    QgsMessageLog.logMessage(str(x), "SimpliPy")


geometryTypeMap = {0: "Point", 1: "LineString", 2: "Polygon"}

OUTPUT_NEWLAYER = 1
OUTPUT_ATTRIBUTE = 2


class simplipy:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.layerNum = 0
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'simplipy_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = simplipyDialog()
        self.qgisSettings = QSettings()
        self.layerRegistry = QgsMapLayerRegistry.instance()
        self.input_layer_list = []

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/simplipy/icon.png"),
            u"Advanced geometry simplification", self.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect(self.run)
        self.iface.mapCanvas().selectionChanged.connect(self.refresh_feature_count)

        QObject.connect(self.dlg.ui.inputlayerComboBox, SIGNAL("currentIndexChanged(QString)"), self.inputlayer_changed)
        QObject.connect(self.dlg.ui.features_selected_radio, SIGNAL("currentIndexChanged(QString)"), self.refresh_feature_count)
        QObject.connect(self.dlg.ui.features_all_radio, SIGNAL("toggled(bool)"), self.refresh_feature_count)
        QObject.connect(self.dlg.ui.output_field_attribute, SIGNAL("currentIndexChanged(QString)"), self.select_output_field_radio)

        QObject.connect(self.dlg.ui.cnstr_expandcontract, SIGNAL("toggled(bool)"), self.refresh_constraint_options_gui)
        QObject.connect(self.dlg.ui.cnstr_repairintersections, SIGNAL("toggled(bool)"), self.refresh_constraint_options_gui)
        QObject.connect(self.dlg.ui.cnstr_preventshaperemoval, SIGNAL("toggled(bool)"), self.refresh_constraint_options_gui)
        QObject.connect(self.dlg.ui.cnstr_usetopology, SIGNAL("toggled(bool)"), self.refresh_constraint_options_gui)


        QObject.connect(self.dlg.ui.start_button, SIGNAL("clicked()"), self.start_simplify)

        # Algorithm and parameters qobjects find
        for alg_id, alg in simplify_algorithms.items():
            alg['qobj'] = {
                'radio': getattr(self.dlg.ui, "radio_alg_"+alg_id),
                'parameter_group': getattr(self.dlg.ui, "alg_parameter_group_"+alg_id),
            }
            for param_id, parameter in alg['parameters'].iteritems():
                parameter['qobj'] = getattr(self.dlg.ui, parameter['QObject'])


        for alg_id, alg in simplify_algorithms.items():
            QObject.connect(alg['qobj']['radio'], SIGNAL("toggled(bool)"), lambda: self.show_alg_parameters(self.get_algorithm_selected()))


        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&SimpliPy", self.action)


        self.refresh_constraint_options_gui()
        self.refresh_input_layer_list()

    def refresh_constraint_options_gui(self):
        # sets to enabled/disabled the constraint options /depending on what constraints are selected)
        self.dlg.ui.select_cnstr_expandcontract.setDisabled(not self.dlg.ui.cnstr_expandcontract.isChecked())
        self.dlg.ui.label_precision_repair.setDisabled(not self.dlg.ui.cnstr_repairintersections.isChecked())
        self.dlg.ui.doubleSpinBox_precision_repair.setDisabled(not self.dlg.ui.cnstr_repairintersections.isChecked())

        self.dlg.ui.label_min_points.setDisabled(not self.dlg.ui.cnstr_preventshaperemoval.isChecked())
        self.dlg.ui.spinBox_min_points.setDisabled(not self.dlg.ui.cnstr_preventshaperemoval.isChecked())
        self.dlg.ui.label_snap_precision.setDisabled(not self.dlg.ui.cnstr_usetopology.isChecked())
        self.dlg.ui.doubleSpinBox_snap_precision.setDisabled(not self.dlg.ui.cnstr_usetopology.isChecked())
        self.dlg.ui.cnstr_sharededges.setDisabled(not self.dlg.ui.cnstr_usetopology.isChecked())
        self.dlg.ui.cnstr_nonsharededges.setDisabled(not self.dlg.ui.cnstr_usetopology.isChecked())

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&SimpliPy", self.action)
        self.iface.removeToolBarIcon(self.action)

    def show_alg_parameters(self, alg_id):
        for alg2_id, alg2 in simplify_algorithms.items():
            alg2['qobj']['parameter_group'].setVisible(alg2_id == alg_id)

    def get_input_layer(self):
        idx = self.dlg.ui.inputlayerComboBox.currentIndex()
        if idx is None or idx < 0 or idx >= len(self.input_layer_list):
            return None
        return self.input_layer_list[idx]

    def get_geometry_fields(self, layer):
        L = []
        for field in layer.dataProvider().fields():
            if field.typeName() == "geometry":
                L.append(field)
        return L

    def select_output_field_radio(self):
        self.dlg.ui.radio_output_attribute.setChecked(True)

    def refresh_input_layer_list(self):
        active_layer = self.iface.activeLayer()
        inputlayer = self.dlg.ui.inputlayerComboBox
        inputlayer.clear()
        layers = self.layerRegistry.mapLayers().values()

        self.input_layer_list = []
        sel = None
        for (i, layer) in enumerate(layers):
            self.input_layer_list.append(layer)
            inputlayer.addItem(layer.name())
            if active_layer and layer.name() == active_layer.name():
                sel = i

        if sel is not None:
            inputlayer.setCurrentIndex(sel)
            if active_layer:
                if active_layer.selectedFeatureCount() > 0:
                    self.dlg.ui.features_selected_radio.setChecked(True)
                else:
                    self.dlg.ui.features_all_radio.setChecked(True)


    def get_total_features(self, layer):
        try:
            if layer is None:
                num_features = 0
            else:
                if self.dlg.ui.features_all_radio.isChecked():
                    num_features = layer.featureCount()
                elif self.dlg.ui.features_selected_radio.isChecked():
                    num_features = layer.selectedFeatureCount()
                else:
                    num_features = 0
            return num_features
        except:
            return 0

    def get_features(self, layer):
        if layer is None:
            features = []
        else:
            if self.dlg.ui.features_all_radio.isChecked():
                features = layer.getFeatures()
            elif self.dlg.ui.features_selected_radio.isChecked():
                features = layer.selectedFeatures()
            else:
                features = []
        return features


    def refresh_feature_count(self):
        layer = self.get_input_layer()
        if layer is None:
            num_features = 0
        else:
            num_features = self.get_total_features(layer)
        self.dlg.ui.label_total_features.setText(str(num_features))

    def inputlayer_changed(self):
        self.refresh_feature_count()
        self.refresh_output_field_list()

    def refresh_output_field_list(self):
        outputfield = self.dlg.ui.output_field_attribute
        outputfield.clear()
        selected_layer = self.get_input_layer()

        if selected_layer is not None:
            for field in self.get_geometry_fields(selected_layer):
                outputfield.addItem(field.name())

        if outputfield.currentIndex() == -1:
            outputfield.setDisabled(True)
            self.dlg.ui.radio_output_attribute.setDisabled(True)
            outputfield.addItem("geometry field not found")
        else:
            outputfield.setDisabled(False)
            self.dlg.ui.radio_output_attribute.setDisabled(False)
        self.dlg.ui.radio_output_newlayer.setChecked(True)

    def log_clear(self):
        self.dlg.ui.simplipy_log.clear()

    def log(self, msg):
        if not isinstance(msg, basestring):
            msg = str(msg)
        self.dlg.ui.simplipy_log.append(msg)
        self.dlg.ui.simplipy_log.ensureCursorVisible()
        print msg


    def get_output_mode(self):
        if self.dlg.ui.radio_output_newlayer.isChecked():
            return OUTPUT_NEWLAYER
        if self.dlg.ui.radio_output_attribute.isChecked():
            return OUTPUT_ATTRIBUTE
        raise Exception("Cant find output mode")

    def get_output_field_idx(self):
        layer = self.get_input_layer()
        for (i, field) in enumerate(layer.dataProvider().fields()):
            if field.typeName() == "geometry" and field.name() == self.dlg.ui.output_field_attribute.currentText():
                return i
        raise Exception("Cant find output field idx!?")


    def get_algorithm_selected(self):
        for alg_id, alg in simplify_algorithms.items():
            qobj_radio = getattr(self.dlg.ui, 'radio_alg_'+alg_id)
            if qobj_radio is None:
                raise ExceptNoTraceback("Can't find radio button for algorithm "+alg_id)
            if qobj_radio.isChecked():
                return alg_id
        raise ExceptNoTraceback("No algorithm selected")


    def get_constraints(self):
        constraints = {}

        constraints['expandcontract'] = None
        if self.dlg.ui.cnstr_expandcontract.isChecked():
            constraints['expandcontract'] = self.dlg.ui.select_cnstr_expandcontract.currentText()

        constraints['simplify_shared_edges'] = self.dlg.ui.cnstr_sharededges.isChecked()
        constraints['simplify_non_shared_edges'] = self.dlg.ui.cnstr_nonsharededges.isChecked()
        constraints['repair_intersections'] = self.dlg.ui.cnstr_repairintersections.isChecked()
        constraints['repair_intersections_precision'] = float(self.dlg.ui.doubleSpinBox_precision_repair.text())
        constraints['prevent_shape_removal'] = self.dlg.ui.cnstr_preventshaperemoval.isChecked()
        constraints['prevent_shape_removal_min_points'] = int(self.dlg.ui.spinBox_min_points.text())

        constraints['use_topology'] = self.dlg.ui.cnstr_usetopology.isChecked()
        constraints['use_topology_snap_precision'] = float(self.dlg.ui.doubleSpinBox_snap_precision.text())

        return constraints


    def get_algorithm_parameters(self, alg_id):
        params = {}
        for parameter_name, parameter in simplify_algorithms[alg_id]['parameters'].items():
            #self.log(str(type(parameter['qobj'])))
            qobj = parameter['qobj']
            if isinstance(qobj, (QLineEdit, QDoubleSpinBox, QSpinBox)):
                value = qobj.text()
            elif isinstance(qobj, QRadioButton):
                value = qobj.isChecked()
            else:
                raise ExceptNoTraceback("Get parameter of %s not defined" % str(type(qobj)))

            valid_parameter = True
            try:
                value = parameter['format'](value)
                if not parameter['validate'](value):
                    valid_parameter = False
            except:
                valid_parameter = False
            if not valid_parameter:
                raise ExceptNoTraceback(parameter['format_description'])
            params[parameter_name] = value
        return params


    def createLayer(self, geometry_type, crs=None, attributes=None, gid_column_name="gid"):
        # 1 - these 4 lines are here to avoid the popup asking the CRS of the new created layer
        projectionSettingKey = "Projections/defaultBehaviour"
        oldProjectionSetting = self.qgisSettings.value(projectionSettingKey)
        self.qgisSettings.setValue(projectionSettingKey, "useGlobal")
        self.qgisSettings.sync()

        # create layer
        layer = QgsVectorLayer(geometry_type, "SimpliPy %d" % self.layerNum, "memory")
        self.layerNum += 1

        layer.setCrs(crs)

        pr = layer.dataProvider()
        pr.addAttributes([QgsField(gid_column_name, QVariant.String)])

        self.qgisSettings.setValue(projectionSettingKey, oldProjectionSetting)
        return layer

    sthread = None
    def start_simplify(self):
        if self.sthread is not None:
            # if thread running, stop it (or try to stop it)
            self.sthread.stop()
            return

        try:
            # get input layer
            self.log_clear()
            output_mode = self.get_output_mode()

            alg_id = self.get_algorithm_selected()
            params = self.get_algorithm_parameters(alg_id)
            constraints = self.get_constraints()
            self.log("Algorithm: %s" % alg_id)
            self.log(str(params))
            self.log(str(constraints))

            layer = self.get_input_layer()
            if layer is None:
                self.log("Error: No layer selected")
                return

            self.dlg.ui.start_button.setDisabled(True)
            self.dlg.ui.start_button.setText("Starting...")
            self.dlg.repaint()
            self.log("-"*80)
            self.log("Start simplify")

            # create instance of simplifier module
            simplifier = simplify_algorithms[alg_id]['function']

            # which features do we need to process
            geometry_type = geometryTypeMap[layer.geometryType()]

            gid_column = get_gid_column_name(layer)
            if output_mode == OUTPUT_NEWLAYER:
                new_layer = self.createLayer(geometry_type, layer.crs(), gid_column_name=gid_column)
                new_layer.startEditing()
            elif output_mode == OUTPUT_ATTRIBUTE:
                self.log("START EDIT")
                layer.startEditing()

            feature_map = {}
            for feature in self.get_features(layer):
                gid = feature.id()
                feature_map[gid] = feature

            num_features = len(feature_map)
            features = feature_map.values()

            def setprogress(x):
                self.dlg.ui.progressBar.setValue(x)
            def save_feature(simp_feature):
                if output_mode == OUTPUT_NEWLAYER:
                    new_layer.dataProvider().addFeatures([simp_feature])
                if output_mode == OUTPUT_ATTRIBUTE:
                    idx = self.get_output_field_idx()
                    gid = simp_feature.attributes()[0]
                    feature = feature_map[gid] # feature from original source(layer)
                    self.log("save on attribute= %s:%s" % (idx, gid))
                    feature.setAttribute(idx, simp_feature.geometry())

            def jobfinished(value):
                self.log("Thread job finished!")
                self.sthread.stop()
                self.dlg.ui.start_button.setText("Start")
                self.set_ui_enabled(True)

                if output_mode == OUTPUT_NEWLAYER:
                    new_layer.commitChanges()
                    # add layer to layer registry
                    uri = os.path.join(os.path.dirname(__file__), "qgis_style_test.qml")
                    if os.path.exists(uri):
                        new_layer.loadNamedStyle(uri)
                    self.layerRegistry.addMapLayer(new_layer)
                    self.iface.legendInterface().setLayerVisible(new_layer, True)
                elif output_mode == OUTPUT_ATTRIBUTE:
                    self.log("COMMIT")
                    layer.commitChanges()

                self.iface.mapCanvas().refresh()
                if output_mode == OUTPUT_NEWLAYER:
                    new_layer.loadNamedStyle(uri)
                self.sthread = None
            def error(e):
                self.log("Error simplifying:")
                self.log(e)

            self.set_ui_enabled(False)
            self.dlg.ui.start_button.setText("Stop")
            self.sthread = SimplifyThread(self.iface.mainWindow(), layer, simplifier, params, constraints, features, num_features, logger=self.log)
            QObject.connect(self.sthread, SIGNAL("jobFinished( PyQt_PyObject )"), jobfinished)
            QObject.connect(self.sthread, SIGNAL("progress( PyQt_PyObject )"), setprogress)
            QObject.connect(self.sthread, SIGNAL("featureResult( PyQt_PyObject )"), save_feature)
            QObject.connect(self.sthread, SIGNAL("error( PyQt_PyObject )"), error)

            self.sthread.start()
        except ExceptNoTraceback, e:
            self.log("ERROR: %s" % e)
            self.log(exception_format(e))
        except Exception, e:
            self.log("Error simplifying:")
            self.log(exception_format(e))

    def set_ui_enabled(self, enabled=True):
        self.dlg.ui.start_button.setDisabled(not enabled)
        self.dlg.ui.groupInput.setDisabled(not enabled)
        self.dlg.ui.groupOutput.setDisabled(not enabled)
        self.dlg.ui.group_Algorithm.setDisabled(not enabled)
        self.dlg.ui.group_Constraints.setDisabled(not enabled)
        self.dlg.ui.group_Options.setDisabled(not enabled)


    # run method that performs all the real work
    def run(self):
        # show the dialog
        self.dlg.show()

        self.dlg.ui.simplipy_log.clear()
        self.log("Simplipy Log:")

        self.refresh_input_layer_list()
        self.refresh_output_field_list()
        self.show_alg_parameters(self.get_algorithm_selected())

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code)
            pass


def get_gid_column_name(layer):
    return layer.attributeDisplayName(0)

from PyQt4.QtCore import *
from PyQt4.QtGui import *
class WorkerThread( QThread ):
    def __init__( self, parentThread):
        self.parent = parentThread
        QThread.__init__( self, parentThread )
    def run( self ):
        self.running = True
        success = self.doWork()
        self.emit( SIGNAL( "jobFinished( PyQt_PyObject )" ), success )
    def stop( self ):
        self.running = False
        pass
    def doWork( self ):
        return True
    def cleanUp( self):
        pass

import time
class SimplifyThread(WorkerThread):
    def __init__(self, parentThread, source_layer, simplifier, params, constraints, features, num_features, logger=None):
        WorkerThread.__init__(self, parentThread)
        self.simplifier = simplifier
        self.params = params
        self.constraints = constraints
        self.features = features
        self.num_features = num_features
        self.logger = logger
        self.source_layer = source_layer

    def stop( self ):
        WorkerThread.stop(self)

    def simplifyFeature(self, feature):
        #Simplify feature
        wkb = feature.geometry().asWkb()
        wkb_simplified = self.simplifier.simplify(wkb)

        # save simplified wkb
        f = QgsFeature()
        geom = QgsGeometry()
        geom.fromWkb(wkb_simplified)
        f.setGeometry(geom)
        f.setAttributes(["haha", "hehe"])
        return f

    def progress_iter(self, items, total=None):
        self.emit(SIGNAL("progress( PyQt_PyObject )"), 0)
        if total is None:
            total = len(items)
        i = 0
        last_p = 0
        tlast = time.time()
        for item in items:
            if self.running is False:
                raise Exception("Cancel requested")
            yield item
            p_int = int((i*100.0) / total)
            i += 1

            tnow = time.time()
            if last_p != p_int and (tnow - tlast) > 0.2:
                tlast = tnow
                self.emit(SIGNAL("progress( PyQt_PyObject )"), p_int)
                last_p = p_int
        self.emit(SIGNAL("progress( PyQt_PyObject )"), 100.0)



    def doWork(self):
        try:
            i = 0
            last_p = 0
            self.emit(SIGNAL("progress( PyQt_PyObject )"), 0)
            
            def push_progress(msg):
                self.logger("Progress = %s" % str(msg))

            # Fill chain db
            self.logger("fill chain db")
            features = {}
            cdb = ChainDB()
            for feature in self.progress_iter(self.features, total=self.num_features):
                key = feature.id()
                features[key] = feature
                geom = feature.geometry()
                geom_wkb = geom.asWkb()
                cdb.add_geometry(key, geom_wkb)

            # Simplify features
            self.logger("simplify features")
            cdb.set_constraints(**self.constraints)
            cdb.simplify_keys(self.progress_iter(features.keys()), self.simplifier, push_progress=push_progress, **self.params)

            # Return geometries as wkb
            self.logger("return wkbs")
            for key in self.progress_iter(features.keys()):
                # get wkb
                wkb = cdb.to_wkb(key)

                # create feature
                f = QgsFeature()
                geom = QgsGeometry()
                geom.fromWkb(wkb)
                f.setGeometry(geom)
                f.setAttributes([key])

                # return feature
                self.emit(SIGNAL("featureResult( PyQt_PyObject )"), f)

        except Exception, e:
            self.emit(SIGNAL("error( PyQt_PyObject )"), exception_format(e))
        return True