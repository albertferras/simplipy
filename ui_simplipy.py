# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_simplipy.ui'
#
# Created: Mon Jan  4 16:31:41 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_simplipy(object):
    def setupUi(self, simplipy):
        simplipy.setObjectName(_fromUtf8("simplipy"))
        simplipy.setEnabled(True)
        simplipy.resize(680, 700)
        simplipy.setMinimumSize(QtCore.QSize(680, 700))
        simplipy.setMaximumSize(QtCore.QSize(680, 700))
        self.verticalLayout_4 = QtGui.QVBoxLayout(simplipy)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.group_Source = QtGui.QWidget(simplipy)
        self.group_Source.setEnabled(True)
        self.group_Source.setObjectName(_fromUtf8("group_Source"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.group_Source)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setMargin(0)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.groupInput = QtGui.QGroupBox(self.group_Source)
        self.groupInput.setEnabled(True)
        self.groupInput.setObjectName(_fromUtf8("groupInput"))
        self.verticalLayout_7 = QtGui.QVBoxLayout(self.groupInput)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.horizontalLayout_9 = QtGui.QHBoxLayout()
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        self.label_4 = QtGui.QLabel(self.groupInput)
        self.label_4.setMinimumSize(QtCore.QSize(50, 0))
        self.label_4.setMaximumSize(QtCore.QSize(50, 16777215))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_9.addWidget(self.label_4)
        self.inputlayerComboBox = QtGui.QComboBox(self.groupInput)
        self.inputlayerComboBox.setObjectName(_fromUtf8("inputlayerComboBox"))
        self.horizontalLayout_9.addWidget(self.inputlayerComboBox)
        self.verticalLayout_7.addLayout(self.horizontalLayout_9)
        self.groupBox = QtGui.QGroupBox(self.groupInput)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setContentsMargins(8, 4, 0, 0)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.features_all_radio = QtGui.QRadioButton(self.groupBox)
        self.features_all_radio.setIconSize(QtCore.QSize(16, 16))
        self.features_all_radio.setChecked(True)
        self.features_all_radio.setObjectName(_fromUtf8("features_all_radio"))
        self.verticalLayout_5.addWidget(self.features_all_radio)
        self.features_selected_radio = QtGui.QRadioButton(self.groupBox)
        self.features_selected_radio.setIconSize(QtCore.QSize(16, 16))
        self.features_selected_radio.setObjectName(_fromUtf8("features_selected_radio"))
        self.verticalLayout_5.addWidget(self.features_selected_radio)
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_2.setMargin(0)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_8.addWidget(self.label_2)
        self.label_total_features = QtGui.QLabel(self.groupBox)
        self.label_total_features.setMargin(0)
        self.label_total_features.setIndent(8)
        self.label_total_features.setObjectName(_fromUtf8("label_total_features"))
        self.horizontalLayout_8.addWidget(self.label_total_features)
        self.verticalLayout_5.addLayout(self.horizontalLayout_8)
        self.verticalLayout_7.addWidget(self.groupBox)
        self.horizontalLayout_5.addWidget(self.groupInput)
        self.line_3 = QtGui.QFrame(self.group_Source)
        self.line_3.setFrameShape(QtGui.QFrame.VLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName(_fromUtf8("line_3"))
        self.horizontalLayout_5.addWidget(self.line_3)
        self.groupOutput = QtGui.QGroupBox(self.group_Source)
        self.groupOutput.setObjectName(_fromUtf8("groupOutput"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.groupOutput)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.radio_output_newlayer = QtGui.QRadioButton(self.groupOutput)
        self.radio_output_newlayer.setEnabled(True)
        self.radio_output_newlayer.setChecked(True)
        self.radio_output_newlayer.setObjectName(_fromUtf8("radio_output_newlayer"))
        self.verticalLayout_6.addWidget(self.radio_output_newlayer)
        self.radio_output_newlayerhidden = QtGui.QRadioButton(self.groupOutput)
        self.radio_output_newlayerhidden.setObjectName(_fromUtf8("radio_output_newlayerhidden"))
        self.verticalLayout_6.addWidget(self.radio_output_newlayerhidden)
        spacerItem = QtGui.QSpacerItem(20, 70, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.verticalLayout_6.addItem(spacerItem)
        self.horizontalLayout_5.addWidget(self.groupOutput)
        self.verticalLayout_4.addWidget(self.group_Source)
        self.line_4 = QtGui.QFrame(simplipy)
        self.line_4.setFrameShape(QtGui.QFrame.HLine)
        self.line_4.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_4.setObjectName(_fromUtf8("line_4"))
        self.verticalLayout_4.addWidget(self.line_4)
        self.group_Config = QtGui.QHBoxLayout()
        self.group_Config.setObjectName(_fromUtf8("group_Config"))
        self.group_Algorithm = QtGui.QGroupBox(simplipy)
        self.group_Algorithm.setObjectName(_fromUtf8("group_Algorithm"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.group_Algorithm)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setContentsMargins(0, 4, 0, 0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.radio_alg_douglas = QtGui.QRadioButton(self.group_Algorithm)
        self.radio_alg_douglas.setChecked(True)
        self.radio_alg_douglas.setObjectName(_fromUtf8("radio_alg_douglas"))
        self.verticalLayout_3.addWidget(self.radio_alg_douglas)
        self.radio_alg_visvalingam = QtGui.QRadioButton(self.group_Algorithm)
        self.radio_alg_visvalingam.setChecked(False)
        self.radio_alg_visvalingam.setObjectName(_fromUtf8("radio_alg_visvalingam"))
        self.verticalLayout_3.addWidget(self.radio_alg_visvalingam)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.group_Config.addWidget(self.group_Algorithm)
        self.line = QtGui.QFrame(simplipy)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.group_Config.addWidget(self.line)
        self.group_Options = QtGui.QGroupBox(simplipy)
        self.group_Options.setObjectName(_fromUtf8("group_Options"))
        self.verticalLayout_9 = QtGui.QVBoxLayout(self.group_Options)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setContentsMargins(0, 4, 0, 0)
        self.verticalLayout_9.setObjectName(_fromUtf8("verticalLayout_9"))
        self.alg_parameter_group_douglas = QtGui.QFrame(self.group_Options)
        self.alg_parameter_group_douglas.setObjectName(_fromUtf8("alg_parameter_group_douglas"))
        self.verticalLayout_8 = QtGui.QVBoxLayout(self.alg_parameter_group_douglas)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setMargin(0)
        self.verticalLayout_8.setObjectName(_fromUtf8("verticalLayout_8"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label = QtGui.QLabel(self.alg_parameter_group_douglas)
        self.label.setMinimumSize(QtCore.QSize(80, 0))
        self.label.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_2.addWidget(self.label)
        self.option_epsilon = QtGui.QDoubleSpinBox(self.alg_parameter_group_douglas)
        self.option_epsilon.setMaximumSize(QtCore.QSize(100, 16777215))
        self.option_epsilon.setSpecialValueText(_fromUtf8(""))
        self.option_epsilon.setPrefix(_fromUtf8(""))
        self.option_epsilon.setSuffix(_fromUtf8(""))
        self.option_epsilon.setDecimals(5)
        self.option_epsilon.setMinimum(0.0)
        self.option_epsilon.setMaximum(999999999.0)
        self.option_epsilon.setSingleStep(0.001)
        self.option_epsilon.setProperty("value", 0.01)
        self.option_epsilon.setObjectName(_fromUtf8("option_epsilon"))
        self.horizontalLayout_2.addWidget(self.option_epsilon)
        self.verticalLayout_8.addLayout(self.horizontalLayout_2)
        self.label_dougle_partition_by = QtGui.QLabel(self.alg_parameter_group_douglas)
        self.label_dougle_partition_by.setObjectName(_fromUtf8("label_dougle_partition_by"))
        self.verticalLayout_8.addWidget(self.label_dougle_partition_by)
        self.option_douglas_firstandlast = QtGui.QRadioButton(self.alg_parameter_group_douglas)
        self.option_douglas_firstandlast.setChecked(True)
        self.option_douglas_firstandlast.setObjectName(_fromUtf8("option_douglas_firstandlast"))
        self.verticalLayout_8.addWidget(self.option_douglas_firstandlast)
        self.option_douglas_firstandfurthest = QtGui.QRadioButton(self.alg_parameter_group_douglas)
        self.option_douglas_firstandfurthest.setObjectName(_fromUtf8("option_douglas_firstandfurthest"))
        self.verticalLayout_8.addWidget(self.option_douglas_firstandfurthest)
        self.option_douglas_diameterpoints = QtGui.QRadioButton(self.alg_parameter_group_douglas)
        self.option_douglas_diameterpoints.setChecked(False)
        self.option_douglas_diameterpoints.setObjectName(_fromUtf8("option_douglas_diameterpoints"))
        self.verticalLayout_8.addWidget(self.option_douglas_diameterpoints)
        self.verticalLayout_9.addWidget(self.alg_parameter_group_douglas)
        self.alg_parameter_group_visvalingam = QtGui.QFrame(self.group_Options)
        self.alg_parameter_group_visvalingam.setObjectName(_fromUtf8("alg_parameter_group_visvalingam"))
        self.verticalLayout = QtGui.QVBoxLayout(self.alg_parameter_group_visvalingam)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.label_5 = QtGui.QLabel(self.alg_parameter_group_visvalingam)
        self.label_5.setMinimumSize(QtCore.QSize(80, 0))
        self.label_5.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout_6.addWidget(self.label_5)
        self.option_minarea = QtGui.QDoubleSpinBox(self.alg_parameter_group_visvalingam)
        self.option_minarea.setMaximumSize(QtCore.QSize(100, 16777215))
        self.option_minarea.setDecimals(5)
        self.option_minarea.setMaximum(999999999.0)
        self.option_minarea.setSingleStep(0.01)
        self.option_minarea.setProperty("value", 0.05)
        self.option_minarea.setObjectName(_fromUtf8("option_minarea"))
        self.horizontalLayout_6.addWidget(self.option_minarea)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.verticalLayout_9.addWidget(self.alg_parameter_group_visvalingam)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_9.addItem(spacerItem2)
        self.group_Config.addWidget(self.group_Options)
        self.line_2 = QtGui.QFrame(simplipy)
        self.line_2.setFrameShape(QtGui.QFrame.VLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.group_Config.addWidget(self.line_2)
        self.group_Constraints = QtGui.QGroupBox(simplipy)
        self.group_Constraints.setObjectName(_fromUtf8("group_Constraints"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.group_Constraints)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.cnstr_expandcontract = QtGui.QCheckBox(self.group_Constraints)
        self.cnstr_expandcontract.setEnabled(True)
        self.cnstr_expandcontract.setObjectName(_fromUtf8("cnstr_expandcontract"))
        self.horizontalLayout_3.addWidget(self.cnstr_expandcontract)
        self.select_cnstr_expandcontract = QtGui.QComboBox(self.group_Constraints)
        self.select_cnstr_expandcontract.setEditable(False)
        self.select_cnstr_expandcontract.setObjectName(_fromUtf8("select_cnstr_expandcontract"))
        self.select_cnstr_expandcontract.addItem(_fromUtf8(""))
        self.select_cnstr_expandcontract.addItem(_fromUtf8(""))
        self.horizontalLayout_3.addWidget(self.select_cnstr_expandcontract)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.cnstr_repairintersections = QtGui.QCheckBox(self.group_Constraints)
        self.cnstr_repairintersections.setObjectName(_fromUtf8("cnstr_repairintersections"))
        self.verticalLayout_2.addWidget(self.cnstr_repairintersections)
        self.cnstr_preventshaperemoval = QtGui.QCheckBox(self.group_Constraints)
        self.cnstr_preventshaperemoval.setObjectName(_fromUtf8("cnstr_preventshaperemoval"))
        self.verticalLayout_2.addWidget(self.cnstr_preventshaperemoval)
        self.horizontalLayout_min_points_polygon = QtGui.QHBoxLayout()
        self.horizontalLayout_min_points_polygon.setObjectName(_fromUtf8("horizontalLayout_min_points_polygon"))
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_min_points_polygon.addItem(spacerItem3)
        self.label_min_points_polygon = QtGui.QLabel(self.group_Constraints)
        self.label_min_points_polygon.setObjectName(_fromUtf8("label_min_points_polygon"))
        self.horizontalLayout_min_points_polygon.addWidget(self.label_min_points_polygon)
        self.spinBox_min_points_polygon = QtGui.QSpinBox(self.group_Constraints)
        self.spinBox_min_points_polygon.setMinimum(3)
        self.spinBox_min_points_polygon.setObjectName(_fromUtf8("spinBox_min_points_polygon"))
        self.horizontalLayout_min_points_polygon.addWidget(self.spinBox_min_points_polygon)
        self.verticalLayout_2.addLayout(self.horizontalLayout_min_points_polygon)
        self.horizontalLayout_min_points_line = QtGui.QHBoxLayout()
        self.horizontalLayout_min_points_line.setObjectName(_fromUtf8("horizontalLayout_min_points_line"))
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_min_points_line.addItem(spacerItem4)
        self.label_min_points_line = QtGui.QLabel(self.group_Constraints)
        self.label_min_points_line.setObjectName(_fromUtf8("label_min_points_line"))
        self.horizontalLayout_min_points_line.addWidget(self.label_min_points_line)
        self.spinBox_min_points_line = QtGui.QSpinBox(self.group_Constraints)
        self.spinBox_min_points_line.setMinimum(2)
        self.spinBox_min_points_line.setObjectName(_fromUtf8("spinBox_min_points_line"))
        self.horizontalLayout_min_points_line.addWidget(self.spinBox_min_points_line)
        self.verticalLayout_2.addLayout(self.horizontalLayout_min_points_line)
        self.cnstr_usetopology = QtGui.QCheckBox(self.group_Constraints)
        self.cnstr_usetopology.setObjectName(_fromUtf8("cnstr_usetopology"))
        self.verticalLayout_2.addWidget(self.cnstr_usetopology)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem5 = QtGui.QSpacerItem(25, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem5)
        self.label_snap_precision = QtGui.QLabel(self.group_Constraints)
        self.label_snap_precision.setObjectName(_fromUtf8("label_snap_precision"))
        self.horizontalLayout.addWidget(self.label_snap_precision)
        self.doubleSpinBox_snap_precision = QtGui.QDoubleSpinBox(self.group_Constraints)
        self.doubleSpinBox_snap_precision.setMaximumSize(QtCore.QSize(100, 16777215))
        self.doubleSpinBox_snap_precision.setDecimals(5)
        self.doubleSpinBox_snap_precision.setMaximum(9999999.99)
        self.doubleSpinBox_snap_precision.setSingleStep(0.0001)
        self.doubleSpinBox_snap_precision.setProperty("value", 0.0001)
        self.doubleSpinBox_snap_precision.setObjectName(_fromUtf8("doubleSpinBox_snap_precision"))
        self.horizontalLayout.addWidget(self.doubleSpinBox_snap_precision)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_10 = QtGui.QHBoxLayout()
        self.horizontalLayout_10.setObjectName(_fromUtf8("horizontalLayout_10"))
        spacerItem6 = QtGui.QSpacerItem(25, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem6)
        self.cnstr_sharededges = QtGui.QCheckBox(self.group_Constraints)
        self.cnstr_sharededges.setChecked(True)
        self.cnstr_sharededges.setObjectName(_fromUtf8("cnstr_sharededges"))
        self.horizontalLayout_10.addWidget(self.cnstr_sharededges)
        self.verticalLayout_2.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_11 = QtGui.QHBoxLayout()
        self.horizontalLayout_11.setObjectName(_fromUtf8("horizontalLayout_11"))
        spacerItem7 = QtGui.QSpacerItem(25, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem7)
        self.cnstr_nonsharededges = QtGui.QCheckBox(self.group_Constraints)
        self.cnstr_nonsharededges.setChecked(True)
        self.cnstr_nonsharededges.setObjectName(_fromUtf8("cnstr_nonsharededges"))
        self.horizontalLayout_11.addWidget(self.cnstr_nonsharededges)
        self.verticalLayout_2.addLayout(self.horizontalLayout_11)
        spacerItem8 = QtGui.QSpacerItem(20, 3, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem8)
        self.group_Config.addWidget(self.group_Constraints)
        self.verticalLayout_4.addLayout(self.group_Config)
        self.simplipy_log = QtGui.QTextEdit(simplipy)
        self.simplipy_log.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.simplipy_log.setFont(font)
        self.simplipy_log.setFocusPolicy(QtCore.Qt.NoFocus)
        self.simplipy_log.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.simplipy_log.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.simplipy_log.setReadOnly(True)
        self.simplipy_log.setObjectName(_fromUtf8("simplipy_log"))
        self.verticalLayout_4.addWidget(self.simplipy_log)
        self.progressBar = QtGui.QProgressBar(simplipy)
        self.progressBar.setEnabled(True)
        self.progressBar.setMaximum(100)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(True)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.verticalLayout_4.addWidget(self.progressBar)
        self.start_button = QtGui.QPushButton(simplipy)
        self.start_button.setObjectName(_fromUtf8("start_button"))
        self.verticalLayout_4.addWidget(self.start_button)

        self.retranslateUi(simplipy)
        QtCore.QMetaObject.connectSlotsByName(simplipy)

    def retranslateUi(self, simplipy):
        simplipy.setWindowTitle(_translate("simplipy", "simplipy", None))
        self.groupInput.setTitle(_translate("simplipy", "Input", None))
        self.label_4.setText(_translate("simplipy", "Layer:", None))
        self.groupBox.setTitle(_translate("simplipy", "Features:", None))
        self.features_all_radio.setText(_translate("simplipy", "All", None))
        self.features_selected_radio.setText(_translate("simplipy", "Selected features", None))
        self.label_2.setText(_translate("simplipy", "Total features:", None))
        self.label_total_features.setText(_translate("simplipy", "0", None))
        self.groupOutput.setTitle(_translate("simplipy", "Output", None))
        self.radio_output_newlayer.setText(_translate("simplipy", "Add result to canvas (visible layer)", None))
        self.radio_output_newlayerhidden.setText(_translate("simplipy", "Add result to canvas (hidden layer)", None))
        self.group_Algorithm.setTitle(_translate("simplipy", "Algorithms", None))
        self.radio_alg_douglas.setText(_translate("simplipy", "Douglas-Peucker", None))
        self.radio_alg_visvalingam.setText(_translate("simplipy", "Visvalingam", None))
        self.group_Options.setTitle(_translate("simplipy", "Parameters", None))
        self.label.setText(_translate("simplipy", "Tolerance:", None))
        self.label_dougle_partition_by.setText(_translate("simplipy", "Partition by (ring to chain):", None))
        self.option_douglas_firstandlast.setText(_translate("simplipy", "First and last", None))
        self.option_douglas_firstandfurthest.setToolTip(_translate("simplipy", "<html><head/><body><p>The first point is the first point in the polygon. The end point is the point with maximum distance to the first point.</p></body></html>", None))
        self.option_douglas_firstandfurthest.setText(_translate("simplipy", "First and furthest", None))
        self.option_douglas_diameterpoints.setToolTip(_translate("simplipy", "<html><head/><body><p>The <a href=\"http://cgm.cs.mcgill.ca/~orm/diam.html\"><span style=\" text-decoration: underline; color:#0000ff;\">diameter of a polygon</span></a> is defined as the maximum distance between any two points of the polygon. These two points are the starting points.</p></body></html>", None))
        self.option_douglas_diameterpoints.setText(_translate("simplipy", "Diameter points", None))
        self.label_5.setText(_translate("simplipy", "Min Area:", None))
        self.group_Constraints.setTitle(_translate("simplipy", "Constraints", None))
        self.cnstr_expandcontract.setToolTip(_translate("simplipy", "<html><head/><body><p>Expand: The original geometry is a sub-region of the simplified geometry.</p><p>Contract: The simplified geometry is a sub-region of the original geometry.</p><p><br/></p><p>Works by rolling back removed points which created an expansion or contraction of the original geometry.</p></body></html>", None))
        self.cnstr_expandcontract.setText(_translate("simplipy", "Expand/Contract", None))
        self.select_cnstr_expandcontract.setItemText(0, _translate("simplipy", "Contract", None))
        self.select_cnstr_expandcontract.setItemText(1, _translate("simplipy", "Expand", None))
        self.cnstr_repairintersections.setToolTip(_translate("simplipy", "<html><head/><body><p>Fixes the self-intersections and intersections with other polygons that are created after polygons simplification.</p><p>Works by restoring some of the points removed in the simplification of the geometry.</p></body></html>", None))
        self.cnstr_repairintersections.setText(_translate("simplipy", "Repair intersections", None))
        self.cnstr_preventshaperemoval.setToolTip(_translate("simplipy", "<html><head/><body><p>Prevents small polygons from disappearing after simplifications. This can happen when the simplification tolerance is very high compared with the size of the shape. For example, in a world map: Prevent small islands to be deleted.</p><p>The number of points from every shape prevented to be removed will be the result of executing the Visvalingam algorithm until there are 3 points left.</p></body></html>", None))
        self.cnstr_preventshaperemoval.setText(_translate("simplipy", "Prevent shape removal", None))
        self.label_min_points_polygon.setText(_translate("simplipy", "Min points (polygon)", None))
        self.label_min_points_line.setText(_translate("simplipy", "Min points (line)", None))
        self.cnstr_usetopology.setToolTip(_translate("simplipy", "<html><head/><body><p>Recommended for maps.</p><p>Avoids the creation of gaps and overlapping areas between two shapes that share edges, such as the frontier of two countries.</p></body></html>", None))
        self.cnstr_usetopology.setText(_translate("simplipy", "Use topology", None))
        self.label_snap_precision.setToolTip(_translate("simplipy", "<html><head/><body><p><br/></p><p>Fixes topology errors by snapping together points that are almost identical. The \'junction precision\' let\'s you adjust the threshold to detect identical points.</p><p><br/></p><p>Increase this value when the resulting simplification doesn\'t simplify many of the edges between two polygons. This will happen if the original geometry has gaps between geometries. If something overlaps in the original geometry, this option will not help you fix it.</p></body></html>", None))
        self.label_snap_precision.setText(_translate("simplipy", "Snap precision:", None))
        self.cnstr_sharededges.setText(_translate("simplipy", "Simplify shared edges", None))
        self.cnstr_nonsharededges.setText(_translate("simplipy", "Simplify non-shared edges", None))
        self.simplipy_log.setHtml(_translate("simplipy", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Cantarell\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.start_button.setText(_translate("simplipy", "Start", None))

