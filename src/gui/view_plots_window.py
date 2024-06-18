# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/gui/view_plots_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PlotViewer(object):
    def setupUi(self, PlotViewer):
        PlotViewer.setObjectName("PlotViewer")
        PlotViewer.resize(571, 260)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PlotViewer.sizePolicy().hasHeightForWidth())
        PlotViewer.setSizePolicy(sizePolicy)
        PlotViewer.setMinimumSize(QtCore.QSize(571, 260))
        PlotViewer.setMaximumSize(QtCore.QSize(571, 260))
        self.centralwidget = QtWidgets.QWidget(PlotViewer)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 551, 250))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QtCore.QSize(551, 250))
        self.groupBox.setMaximumSize(QtCore.QSize(551, 250))
        self.groupBox.setObjectName("groupBox")
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.groupBox)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(10, 20, 531, 191))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.comboBox = QtWidgets.QComboBox(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)
        self.comboBox.setMaximumSize(QtCore.QSize(200, 30))
        self.comboBox.setObjectName("comboBox")
        self.horizontalLayout_7.addWidget(self.comboBox)
        self.btnOpen = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnOpen.sizePolicy().hasHeightForWidth())
        self.btnOpen.setSizePolicy(sizePolicy)
        self.btnOpen.setMinimumSize(QtCore.QSize(100, 30))
        self.btnOpen.setMaximumSize(QtCore.QSize(100, 30))
        self.btnOpen.setObjectName("btnOpen")
        self.horizontalLayout_7.addWidget(self.btnOpen)
        self.btnRefreshPlotList = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnRefreshPlotList.sizePolicy().hasHeightForWidth())
        self.btnRefreshPlotList.setSizePolicy(sizePolicy)
        self.btnRefreshPlotList.setMinimumSize(QtCore.QSize(100, 30))
        self.btnRefreshPlotList.setMaximumSize(QtCore.QSize(100, 30))
        self.btnRefreshPlotList.setObjectName("btnRefreshPlotList")
        self.horizontalLayout_7.addWidget(self.btnRefreshPlotList)
        self.btnShow = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnShow.sizePolicy().hasHeightForWidth())
        self.btnShow.setSizePolicy(sizePolicy)
        self.btnShow.setMinimumSize(QtCore.QSize(100, 30))
        self.btnShow.setMaximumSize(QtCore.QSize(100, 30))
        self.btnShow.setObjectName("btnShow")
        self.horizontalLayout_7.addWidget(self.btnShow)
        self.btnDelete = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnDelete.sizePolicy().hasHeightForWidth())
        self.btnDelete.setSizePolicy(sizePolicy)
        self.btnDelete.setMinimumSize(QtCore.QSize(100, 30))
        self.btnDelete.setMaximumSize(QtCore.QSize(100, 30))
        self.btnDelete.setObjectName("btnDelete")
        self.horizontalLayout_7.addWidget(self.btnDelete)
        self.verticalLayout_2.addLayout(self.horizontalLayout_7)
        self.LblCharacteristics = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LblCharacteristics.sizePolicy().hasHeightForWidth())
        self.LblCharacteristics.setSizePolicy(sizePolicy)
        self.LblCharacteristics.setMinimumSize(QtCore.QSize(150, 20))
        self.LblCharacteristics.setMaximumSize(QtCore.QSize(150, 20))
        self.LblCharacteristics.setObjectName("LblCharacteristics")
        self.verticalLayout_2.addWidget(self.LblCharacteristics)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.comboBoxOptions = QtWidgets.QComboBox(self.verticalLayoutWidget_2)
        self.comboBoxOptions.setMinimumSize(QtCore.QSize(150, 30))
        self.comboBoxOptions.setMaximumSize(QtCore.QSize(200, 30))
        self.comboBoxOptions.setObjectName("comboBoxOptions")
        self.horizontalLayout.addWidget(self.comboBoxOptions)
        self.comboBoxFilter = QtWidgets.QComboBox(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.comboBoxFilter.sizePolicy().hasHeightForWidth())
        self.comboBoxFilter.setSizePolicy(sizePolicy)
        self.comboBoxFilter.setMinimumSize(QtCore.QSize(150, 30))
        self.comboBoxFilter.setMaximumSize(QtCore.QSize(200, 30))
        self.comboBoxFilter.setObjectName("comboBoxFilter")
        self.horizontalLayout.addWidget(self.comboBoxFilter)
        self.txtBoxFilter = QtWidgets.QLineEdit(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtBoxFilter.sizePolicy().hasHeightForWidth())
        self.txtBoxFilter.setSizePolicy(sizePolicy)
        self.txtBoxFilter.setMinimumSize(QtCore.QSize(100, 20))
        self.txtBoxFilter.setMaximumSize(QtCore.QSize(100, 20))
        self.txtBoxFilter.setObjectName("txtBoxFilter")
        self.horizontalLayout.addWidget(self.txtBoxFilter)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.LblRangeFilter = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.LblRangeFilter.setMinimumSize(QtCore.QSize(150, 20))
        self.LblRangeFilter.setMaximumSize(QtCore.QSize(150, 20))
        self.LblRangeFilter.setObjectName("LblRangeFilter")
        self.verticalLayout_2.addWidget(self.LblRangeFilter)
        self.filterLayout = QtWidgets.QHBoxLayout()
        self.filterLayout.setObjectName("filterLayout")
        self.LblStart = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LblStart.sizePolicy().hasHeightForWidth())
        self.LblStart.setSizePolicy(sizePolicy)
        self.LblStart.setMinimumSize(QtCore.QSize(40, 30))
        self.LblStart.setMaximumSize(QtCore.QSize(40, 30))
        self.LblStart.setObjectName("LblStart")
        self.filterLayout.addWidget(self.LblStart)
        self.txtBoxStart = QtWidgets.QLineEdit(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtBoxStart.sizePolicy().hasHeightForWidth())
        self.txtBoxStart.setSizePolicy(sizePolicy)
        self.txtBoxStart.setMinimumSize(QtCore.QSize(100, 20))
        self.txtBoxStart.setMaximumSize(QtCore.QSize(100, 20))
        self.txtBoxStart.setObjectName("txtBoxStart")
        self.filterLayout.addWidget(self.txtBoxStart)
        self.LblStop = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LblStop.sizePolicy().hasHeightForWidth())
        self.LblStop.setSizePolicy(sizePolicy)
        self.LblStop.setMinimumSize(QtCore.QSize(40, 30))
        self.LblStop.setMaximumSize(QtCore.QSize(40, 30))
        self.LblStop.setObjectName("LblStop")
        self.filterLayout.addWidget(self.LblStop)
        self.txtBoxEnd = QtWidgets.QLineEdit(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtBoxEnd.sizePolicy().hasHeightForWidth())
        self.txtBoxEnd.setSizePolicy(sizePolicy)
        self.txtBoxEnd.setMinimumSize(QtCore.QSize(100, 20))
        self.txtBoxEnd.setMaximumSize(QtCore.QSize(100, 20))
        self.txtBoxEnd.setObjectName("txtBoxEnd")
        self.filterLayout.addWidget(self.txtBoxEnd)
        self.LblFormat = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LblFormat.sizePolicy().hasHeightForWidth())
        self.LblFormat.setSizePolicy(sizePolicy)
        self.LblFormat.setMinimumSize(QtCore.QSize(200, 30))
        self.LblFormat.setMaximumSize(QtCore.QSize(200, 30))
        self.LblFormat.setObjectName("LblFormat")
        self.filterLayout.addWidget(self.LblFormat)
        self.verticalLayout_2.addLayout(self.filterLayout)
        PlotViewer.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(PlotViewer)
        self.statusbar.setObjectName("statusbar")
        PlotViewer.setStatusBar(self.statusbar)

        self.retranslateUi(PlotViewer)
        QtCore.QMetaObject.connectSlotsByName(PlotViewer)

    def retranslateUi(self, PlotViewer):
        _translate = QtCore.QCoreApplication.translate
        PlotViewer.setWindowTitle(_translate("PlotViewer", "Plot viewer"))
        self.groupBox.setTitle(_translate("PlotViewer", "View"))
        self.btnOpen.setText(_translate("PlotViewer", "Open DB"))
        self.btnRefreshPlotList.setText(_translate("PlotViewer", "Refresh List"))
        self.btnShow.setText(_translate("PlotViewer", "Show"))
        self.btnDelete.setText(_translate("PlotViewer", "Delete"))
        self.LblCharacteristics.setText(_translate("PlotViewer", "Filter:"))
        self.LblRangeFilter.setText(_translate("PlotViewer", "Range filter:"))
        self.LblStart.setText(_translate("PlotViewer", "Start:"))
        self.LblStop.setText(_translate("PlotViewer", "Stop:"))
        self.LblFormat.setText(_translate("PlotViewer", "NB* yyyy-mm-dd format for date"))