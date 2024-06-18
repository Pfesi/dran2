# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/gui/edit_driftscan_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DriftscanWindow(object):
    def setupUi(self, DriftscanWindow):
        DriftscanWindow.setObjectName("DriftscanWindow")
        DriftscanWindow.resize(1280, 755)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DriftscanWindow.sizePolicy().hasHeightForWidth())
        DriftscanWindow.setSizePolicy(sizePolicy)
        DriftscanWindow.setMaximumSize(QtCore.QSize(1280, 757))
        DriftscanWindow.setAutoFillBackground(False)
        self.centralwidget = QtWidgets.QWidget(DriftscanWindow)
        self.centralwidget.setAutoFillBackground(False)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 40, 611, 331))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.LblFilename = QtWidgets.QLabel(self.gridLayoutWidget)
        self.LblFilename.setObjectName("LblFilename")
        self.horizontalLayout_4.addWidget(self.LblFilename)
        self.EdtFilename = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.EdtFilename.setEnabled(False)
        self.EdtFilename.setObjectName("EdtFilename")
        self.horizontalLayout_4.addWidget(self.EdtFilename)
        self.gridLayout.addLayout(self.horizontalLayout_4, 0, 1, 1, 1)
        self.tabWidget = QtWidgets.QTabWidget(self.gridLayoutWidget)
        self.tabWidget.setMaximumSize(QtCore.QSize(16777215, 300))
        font = QtGui.QFont()
        font.setBold(False)
        font.setUnderline(True)
        self.tabWidget.setFont(font)
        self.tabWidget.setAutoFillBackground(False)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.layoutWidget = QtWidgets.QWidget(self.tab)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 581, 251))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.LblCurDate = QtWidgets.QLabel(self.layoutWidget)
        self.LblCurDate.setObjectName("LblCurDate")
        self.verticalLayout.addWidget(self.LblCurDate)
        self.EdtCurDate = QtWidgets.QLineEdit(self.layoutWidget)
        self.EdtCurDate.setEnabled(False)
        self.EdtCurDate.setObjectName("EdtCurDate")
        self.verticalLayout.addWidget(self.EdtCurDate)
        self.LblObsDate = QtWidgets.QLabel(self.layoutWidget)
        self.LblObsDate.setObjectName("LblObsDate")
        self.verticalLayout.addWidget(self.LblObsDate)
        self.EdtObsDate = QtWidgets.QLineEdit(self.layoutWidget)
        self.EdtObsDate.setEnabled(False)
        self.EdtObsDate.setObjectName("EdtObsDate")
        self.verticalLayout.addWidget(self.EdtObsDate)
        self.LblObsTime_2 = QtWidgets.QLabel(self.layoutWidget)
        self.LblObsTime_2.setObjectName("LblObsTime_2")
        self.verticalLayout.addWidget(self.LblObsTime_2)
        self.EdtObsTime = QtWidgets.QLineEdit(self.layoutWidget)
        self.EdtObsTime.setEnabled(False)
        self.EdtObsTime.setObjectName("EdtObsTime")
        self.verticalLayout.addWidget(self.EdtObsTime)
        self.LblObsTime_4 = QtWidgets.QLabel(self.layoutWidget)
        self.LblObsTime_4.setObjectName("LblObsTime_4")
        self.verticalLayout.addWidget(self.LblObsTime_4)
        self.EdtHa = QtWidgets.QLineEdit(self.layoutWidget)
        self.EdtHa.setEnabled(False)
        self.EdtHa.setObjectName("EdtHa")
        self.verticalLayout.addWidget(self.EdtHa)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.verticalLayout_10 = QtWidgets.QVBoxLayout()
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.LblObjectType = QtWidgets.QLabel(self.layoutWidget)
        self.LblObjectType.setObjectName("LblObjectType")
        self.verticalLayout_10.addWidget(self.LblObjectType)
        self.EdtObjectType = QtWidgets.QLineEdit(self.layoutWidget)
        self.EdtObjectType.setEnabled(False)
        self.EdtObjectType.setObjectName("EdtObjectType")
        self.verticalLayout_10.addWidget(self.EdtObjectType)
        self.LblObjectName = QtWidgets.QLabel(self.layoutWidget)
        self.LblObjectName.setObjectName("LblObjectName")
        self.verticalLayout_10.addWidget(self.LblObjectName)
        self.EdtObjectName = QtWidgets.QLineEdit(self.layoutWidget)
        self.EdtObjectName.setEnabled(False)
        self.EdtObjectName.setObjectName("EdtObjectName")
        self.verticalLayout_10.addWidget(self.EdtObjectName)
        self.LblMjd = QtWidgets.QLabel(self.layoutWidget)
        self.LblMjd.setObjectName("LblMjd")
        self.verticalLayout_10.addWidget(self.LblMjd)
        self.EdtMjd = QtWidgets.QLineEdit(self.layoutWidget)
        self.EdtMjd.setEnabled(False)
        self.EdtMjd.setObjectName("EdtMjd")
        self.verticalLayout_10.addWidget(self.EdtMjd)
        self.LblObsTime_3 = QtWidgets.QLabel(self.layoutWidget)
        self.LblObsTime_3.setObjectName("LblObsTime_3")
        self.verticalLayout_10.addWidget(self.LblObsTime_3)
        self.EdtZa = QtWidgets.QLineEdit(self.layoutWidget)
        self.EdtZa.setEnabled(False)
        self.EdtZa.setObjectName("EdtZa")
        self.verticalLayout_10.addWidget(self.EdtZa)
        self.horizontalLayout_2.addLayout(self.verticalLayout_10)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.LblFreq = QtWidgets.QLabel(self.layoutWidget)
        self.LblFreq.setObjectName("LblFreq")
        self.verticalLayout_3.addWidget(self.LblFreq)
        self.EdtFreq = QtWidgets.QLineEdit(self.layoutWidget)
        self.EdtFreq.setEnabled(False)
        self.EdtFreq.setObjectName("EdtFreq")
        self.verticalLayout_3.addWidget(self.EdtFreq)
        self.LblTsysLCP = QtWidgets.QLabel(self.layoutWidget)
        self.LblTsysLCP.setObjectName("LblTsysLCP")
        self.verticalLayout_3.addWidget(self.LblTsysLCP)
        self.EdtTsysL = QtWidgets.QLineEdit(self.layoutWidget)
        self.EdtTsysL.setEnabled(False)
        self.EdtTsysL.setObjectName("EdtTsysL")
        self.verticalLayout_3.addWidget(self.EdtTsysL)
        self.LblTsysRCP = QtWidgets.QLabel(self.layoutWidget)
        self.LblTsysRCP.setObjectName("LblTsysRCP")
        self.verticalLayout_3.addWidget(self.LblTsysRCP)
        self.EdtTsysR = QtWidgets.QLineEdit(self.layoutWidget)
        self.EdtTsysR.setEnabled(False)
        self.EdtTsysR.setObjectName("EdtTsysR")
        self.verticalLayout_3.addWidget(self.EdtTsysR)
        self.LblObsTime_5 = QtWidgets.QLabel(self.layoutWidget)
        self.LblObsTime_5.setObjectName("LblObsTime_5")
        self.verticalLayout_3.addWidget(self.LblObsTime_5)
        self.EdtHpbw = QtWidgets.QLineEdit(self.layoutWidget)
        self.EdtHpbw.setEnabled(False)
        self.EdtHpbw.setObjectName("EdtHpbw")
        self.verticalLayout_3.addWidget(self.EdtHpbw)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.LblTemp = QtWidgets.QLabel(self.layoutWidget)
        self.LblTemp.setObjectName("LblTemp")
        self.verticalLayout_2.addWidget(self.LblTemp)
        self.EdtTemp = QtWidgets.QLineEdit(self.layoutWidget)
        self.EdtTemp.setEnabled(False)
        self.EdtTemp.setObjectName("EdtTemp")
        self.verticalLayout_2.addWidget(self.EdtTemp)
        self.LblPres = QtWidgets.QLabel(self.layoutWidget)
        self.LblPres.setObjectName("LblPres")
        self.verticalLayout_2.addWidget(self.LblPres)
        self.EdtPres = QtWidgets.QLineEdit(self.layoutWidget)
        self.EdtPres.setEnabled(False)
        self.EdtPres.setObjectName("EdtPres")
        self.verticalLayout_2.addWidget(self.EdtPres)
        self.LblHum = QtWidgets.QLabel(self.layoutWidget)
        self.LblHum.setObjectName("LblHum")
        self.verticalLayout_2.addWidget(self.LblHum)
        self.EdtHum = QtWidgets.QLineEdit(self.layoutWidget)
        self.EdtHum.setEnabled(False)
        self.EdtHum.setObjectName("EdtHum")
        self.verticalLayout_2.addWidget(self.EdtHum)
        self.LblObsTime_6 = QtWidgets.QLabel(self.layoutWidget)
        self.LblObsTime_6.setObjectName("LblObsTime_6")
        self.verticalLayout_2.addWidget(self.LblObsTime_6)
        self.EdtFnbw = QtWidgets.QLineEdit(self.layoutWidget)
        self.EdtFnbw.setEnabled(False)
        self.EdtFnbw.setObjectName("EdtFnbw")
        self.verticalLayout_2.addWidget(self.EdtFnbw)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.tabWidget.addTab(self.tab, "")
        self.fit_window_tab = QtWidgets.QWidget()
        self.fit_window_tab.setObjectName("fit_window_tab")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.fit_window_tab)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 601, 261))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.fit_window_layout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.fit_window_layout.setContentsMargins(0, 0, 0, 0)
        self.fit_window_layout.setObjectName("fit_window_layout")
        self.plot_groupbox = QtWidgets.QGroupBox(self.horizontalLayoutWidget)
        self.plot_groupbox.setObjectName("plot_groupbox")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.plot_groupbox)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 23, 175, 231))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.plot_layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.plot_layout.setContentsMargins(0, 0, 0, 0)
        self.plot_layout.setObjectName("plot_layout")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("label")
        self.horizontalLayout_8.addWidget(self.label)
        self.ComboBoxFitType = QtWidgets.QComboBox(self.verticalLayoutWidget)
        self.ComboBoxFitType.setEnabled(False)
        self.ComboBoxFitType.setObjectName("ComboBoxFitType")
        self.ComboBoxFitType.addItem("")
        self.ComboBoxFitType.addItem("")
        self.horizontalLayout_8.addWidget(self.ComboBoxFitType)
        self.plot_layout.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_9.addWidget(self.label_2)
        self.ComboBoxFitLoc = QtWidgets.QComboBox(self.verticalLayoutWidget)
        self.ComboBoxFitLoc.setEnabled(False)
        self.ComboBoxFitLoc.setObjectName("ComboBoxFitLoc")
        self.ComboBoxFitLoc.addItem("")
        self.ComboBoxFitLoc.addItem("")
        self.horizontalLayout_9.addWidget(self.ComboBoxFitLoc)
        self.plot_layout.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_10.addWidget(self.label_3)
        self.ComboBoxFitOrder = QtWidgets.QComboBox(self.verticalLayoutWidget)
        self.ComboBoxFitOrder.setEnabled(False)
        self.ComboBoxFitOrder.setObjectName("ComboBoxFitOrder")
        self.ComboBoxFitOrder.addItem("")
        self.ComboBoxFitOrder.addItem("")
        self.ComboBoxFitOrder.addItem("")
        self.ComboBoxFitOrder.addItem("")
        self.ComboBoxFitOrder.addItem("")
        self.ComboBoxFitOrder.addItem("")
        self.ComboBoxFitOrder.addItem("")
        self.ComboBoxFitOrder.addItem("")
        self.ComboBoxFitOrder.addItem("")
        self.ComboBoxFitOrder.addItem("")
        self.horizontalLayout_10.addWidget(self.ComboBoxFitOrder)
        self.plot_layout.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.label_4 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_11.addWidget(self.label_4)
        self.ComboBoxFilterType = QtWidgets.QComboBox(self.verticalLayoutWidget)
        self.ComboBoxFilterType.setEnabled(False)
        self.ComboBoxFilterType.setObjectName("ComboBoxFilterType")
        self.ComboBoxFilterType.addItem("")
        self.ComboBoxFilterType.addItem("")
        self.horizontalLayout_11.addWidget(self.ComboBoxFilterType)
        self.plot_layout.addLayout(self.horizontalLayout_11)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.LblFilteringWindow = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.LblFilteringWindow.setObjectName("LblFilteringWindow")
        self.horizontalLayout_12.addWidget(self.LblFilteringWindow)
        self.EdtFilteringWindow = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.EdtFilteringWindow.setEnabled(False)
        self.EdtFilteringWindow.setObjectName("EdtFilteringWindow")
        self.horizontalLayout_12.addWidget(self.EdtFilteringWindow)
        self.plot_layout.addLayout(self.horizontalLayout_12)
        self.fit_window_layout.addWidget(self.plot_groupbox)
        self.single_beam_groupbox = QtWidgets.QGroupBox(self.horizontalLayoutWidget)
        self.single_beam_groupbox.setObjectName("single_beam_groupbox")
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.single_beam_groupbox)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(10, 20, 171, 241))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.single_beam_layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.single_beam_layout.setContentsMargins(0, 0, 0, 0)
        self.single_beam_layout.setObjectName("single_beam_layout")
        self.BtnFilterData = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.BtnFilterData.setEnabled(False)
        self.BtnFilterData.setObjectName("BtnFilterData")
        self.single_beam_layout.addWidget(self.BtnFilterData)
        self.BtnFitData = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.BtnFitData.setEnabled(False)
        self.BtnFitData.setObjectName("BtnFitData")
        self.single_beam_layout.addWidget(self.BtnFitData)
        self.BtnClearSelection = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.BtnClearSelection.setEnabled(False)
        self.BtnClearSelection.setObjectName("BtnClearSelection")
        self.single_beam_layout.addWidget(self.BtnClearSelection)
        self.BtnSave = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.BtnSave.setEnabled(False)
        self.BtnSave.setObjectName("BtnSave")
        self.single_beam_layout.addWidget(self.BtnSave)
        self.BtnCalc = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.BtnCalc.setEnabled(False)
        self.BtnCalc.setObjectName("BtnCalc")
        self.single_beam_layout.addWidget(self.BtnCalc)
        self.BrcpPSSlayout_3 = QtWidgets.QHBoxLayout()
        self.BrcpPSSlayout_3.setObjectName("BrcpPSSlayout_3")
        self.EdtAddPSS = QtWidgets.QLineEdit(self.verticalLayoutWidget_2)
        self.EdtAddPSS.setEnabled(False)
        self.EdtAddPSS.setObjectName("EdtAddPSS")
        self.BrcpPSSlayout_3.addWidget(self.EdtAddPSS)
        self.DropSetPSS = QtWidgets.QComboBox(self.verticalLayoutWidget_2)
        self.DropSetPSS.setEnabled(False)
        self.DropSetPSS.setObjectName("DropSetPSS")
        self.DropSetPSS.addItem("")
        self.BrcpPSSlayout_3.addWidget(self.DropSetPSS)
        self.single_beam_layout.addLayout(self.BrcpPSSlayout_3)
        self.BrcpPSSlayout_4 = QtWidgets.QHBoxLayout()
        self.BrcpPSSlayout_4.setObjectName("BrcpPSSlayout_4")
        self.BtnGetPSS_2 = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.BtnGetPSS_2.setObjectName("BtnGetPSS_2")
        self.BrcpPSSlayout_4.addWidget(self.BtnGetPSS_2)
        self.BtnPSSreset_2 = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.BtnPSSreset_2.setObjectName("BtnPSSreset_2")
        self.BrcpPSSlayout_4.addWidget(self.BtnPSSreset_2)
        self.single_beam_layout.addLayout(self.BrcpPSSlayout_4)
        self.fit_window_layout.addWidget(self.single_beam_groupbox)
        self.pss_values_groupbox = QtWidgets.QGroupBox(self.horizontalLayoutWidget)
        self.pss_values_groupbox.setObjectName("pss_values_groupbox")
        self.verticalLayoutWidget_3 = QtWidgets.QWidget(self.pss_values_groupbox)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(10, 20, 171, 241))
        self.verticalLayoutWidget_3.setObjectName("verticalLayoutWidget_3")
        self.FitButtonsLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_3)
        self.FitButtonsLayout_2.setContentsMargins(0, 0, 0, 0)
        self.FitButtonsLayout_2.setObjectName("FitButtonsLayout_2")
        self.BtnPopulatePSS = QtWidgets.QPushButton(self.verticalLayoutWidget_3)
        self.BtnPopulatePSS.setEnabled(False)
        self.BtnPopulatePSS.setObjectName("BtnPopulatePSS")
        self.FitButtonsLayout_2.addWidget(self.BtnPopulatePSS)
        self.AlcpPSSlayout = QtWidgets.QHBoxLayout()
        self.AlcpPSSlayout.setObjectName("AlcpPSSlayout")
        self.LblPSSlcpA = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.LblPSSlcpA.setObjectName("LblPSSlcpA")
        self.AlcpPSSlayout.addWidget(self.LblPSSlcpA)
        self.EdtPSSlcpA = QtWidgets.QLineEdit(self.verticalLayoutWidget_3)
        self.EdtPSSlcpA.setEnabled(False)
        self.EdtPSSlcpA.setObjectName("EdtPSSlcpA")
        self.AlcpPSSlayout.addWidget(self.EdtPSSlcpA)
        self.FitButtonsLayout_2.addLayout(self.AlcpPSSlayout)
        self.BlcpPSSlayout = QtWidgets.QHBoxLayout()
        self.BlcpPSSlayout.setObjectName("BlcpPSSlayout")
        self.LblPSSlcpB = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.LblPSSlcpB.setObjectName("LblPSSlcpB")
        self.BlcpPSSlayout.addWidget(self.LblPSSlcpB)
        self.EdtPSSlcpB = QtWidgets.QLineEdit(self.verticalLayoutWidget_3)
        self.EdtPSSlcpB.setEnabled(False)
        self.EdtPSSlcpB.setObjectName("EdtPSSlcpB")
        self.BlcpPSSlayout.addWidget(self.EdtPSSlcpB)
        self.FitButtonsLayout_2.addLayout(self.BlcpPSSlayout)
        self.ArcpPSSlayout = QtWidgets.QHBoxLayout()
        self.ArcpPSSlayout.setObjectName("ArcpPSSlayout")
        self.LblPSSrcpA = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.LblPSSrcpA.setObjectName("LblPSSrcpA")
        self.ArcpPSSlayout.addWidget(self.LblPSSrcpA)
        self.EdtPSSrcpA = QtWidgets.QLineEdit(self.verticalLayoutWidget_3)
        self.EdtPSSrcpA.setEnabled(False)
        self.EdtPSSrcpA.setObjectName("EdtPSSrcpA")
        self.ArcpPSSlayout.addWidget(self.EdtPSSrcpA)
        self.FitButtonsLayout_2.addLayout(self.ArcpPSSlayout)
        self.BrcpPSSlayout = QtWidgets.QHBoxLayout()
        self.BrcpPSSlayout.setObjectName("BrcpPSSlayout")
        self.LblPSSrcpB = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.LblPSSrcpB.setObjectName("LblPSSrcpB")
        self.BrcpPSSlayout.addWidget(self.LblPSSrcpB)
        self.EdtPSSrcpB = QtWidgets.QLineEdit(self.verticalLayoutWidget_3)
        self.EdtPSSrcpB.setEnabled(False)
        self.EdtPSSrcpB.setObjectName("EdtPSSrcpB")
        self.BrcpPSSlayout.addWidget(self.EdtPSSrcpB)
        self.FitButtonsLayout_2.addLayout(self.BrcpPSSlayout)
        self.BtnSavePSS = QtWidgets.QPushButton(self.verticalLayoutWidget_3)
        self.BtnSavePSS.setEnabled(False)
        self.BtnSavePSS.setObjectName("BtnSavePSS")
        self.FitButtonsLayout_2.addWidget(self.BtnSavePSS)
        self.BtnResetPSS = QtWidgets.QPushButton(self.verticalLayoutWidget_3)
        self.BtnResetPSS.setEnabled(False)
        self.BtnResetPSS.setObjectName("BtnResetPSS")
        self.FitButtonsLayout_2.addWidget(self.BtnResetPSS)
        self.fit_window_layout.addWidget(self.pss_values_groupbox)
        self.tabWidget.addTab(self.fit_window_tab, "")
        self.gridLayout.addWidget(self.tabWidget, 1, 1, 1, 1)
        self.layoutWidget1 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget1.setGeometry(QtCore.QRect(10, 410, 141, 311))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.imaging_verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.imaging_verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.imaging_verticalLayout.setObjectName("imaging_verticalLayout")
        self.BtnOpenFile = QtWidgets.QPushButton(self.layoutWidget1)
        self.BtnOpenFile.setObjectName("BtnOpenFile")
        self.imaging_verticalLayout.addWidget(self.BtnOpenFile)
        self.BtnResetStatus = QtWidgets.QPushButton(self.layoutWidget1)
        self.BtnResetStatus.setObjectName("BtnResetStatus")
        self.imaging_verticalLayout.addWidget(self.BtnResetStatus)
        self.BtnViewStatus = QtWidgets.QPushButton(self.layoutWidget1)
        self.BtnViewStatus.setObjectName("BtnViewStatus")
        self.imaging_verticalLayout.addWidget(self.BtnViewStatus)
        self.BtnViewFit = QtWidgets.QPushButton(self.layoutWidget1)
        self.BtnViewFit.setEnabled(False)
        self.BtnViewFit.setObjectName("BtnViewFit")
        self.imaging_verticalLayout.addWidget(self.BtnViewFit)
        self.BtnResetPlot = QtWidgets.QPushButton(self.layoutWidget1)
        self.BtnResetPlot.setEnabled(False)
        self.BtnResetPlot.setObjectName("BtnResetPlot")
        self.imaging_verticalLayout.addWidget(self.BtnResetPlot)
        self.BtnSaveToDb = QtWidgets.QPushButton(self.layoutWidget1)
        self.BtnSaveToDb.setEnabled(False)
        self.BtnSaveToDb.setObjectName("BtnSaveToDb")
        self.imaging_verticalLayout.addWidget(self.BtnSaveToDb)
        self.checkBox = QtWidgets.QCheckBox(self.layoutWidget1)
        self.checkBox.setEnabled(False)
        self.checkBox.setObjectName("checkBox")
        self.imaging_verticalLayout.addWidget(self.checkBox)
        self.layoutWidget2 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget2.setGeometry(QtCore.QRect(150, 412, 471, 311))
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.otherPlotsLayout = QtWidgets.QGridLayout(self.layoutWidget2)
        self.otherPlotsLayout.setContentsMargins(0, 0, 0, 0)
        self.otherPlotsLayout.setObjectName("otherPlotsLayout")
        self.layoutWidget3 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget3.setGeometry(QtCore.QRect(630, 50, 641, 671))
        self.layoutWidget3.setObjectName("layoutWidget3")
        self.PlotLayout = QtWidgets.QGridLayout(self.layoutWidget3)
        self.PlotLayout.setContentsMargins(0, 0, 0, 0)
        self.PlotLayout.setObjectName("PlotLayout")
        self.layoutWidget4 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget4.setGeometry(QtCore.QRect(10, 370, 611, 38))
        self.layoutWidget4.setObjectName("layoutWidget4")
        self.FitBaseLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget4)
        self.FitBaseLayout_2.setContentsMargins(0, 0, 0, 0)
        self.FitBaseLayout_2.setObjectName("FitBaseLayout_2")
        self.LblPlottype = QtWidgets.QLabel(self.layoutWidget4)
        self.LblPlottype.setObjectName("LblPlottype")
        self.FitBaseLayout_2.addWidget(self.LblPlottype)
        self.ComboBoxPlotType = QtWidgets.QComboBox(self.layoutWidget4)
        self.ComboBoxPlotType.setEnabled(False)
        self.ComboBoxPlotType.setObjectName("ComboBoxPlotType")
        self.ComboBoxPlotType.addItem("")
        self.ComboBoxPlotType.setItemText(0, "")
        self.FitBaseLayout_2.addWidget(self.ComboBoxPlotType)
        self.BtnChoosePlot = QtWidgets.QPushButton(self.layoutWidget4)
        self.BtnChoosePlot.setEnabled(False)
        self.BtnChoosePlot.setObjectName("BtnChoosePlot")
        self.FitBaseLayout_2.addWidget(self.BtnChoosePlot)
        self.gridLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(10, 0, 1261, 41))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.nav_grid_layout = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.nav_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.nav_grid_layout.setObjectName("nav_grid_layout")
        DriftscanWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(DriftscanWindow)
        self.statusbar.setObjectName("statusbar")
        DriftscanWindow.setStatusBar(self.statusbar)
        self.actionOpen_file = QtWidgets.QAction(DriftscanWindow)
        self.actionOpen_file.setObjectName("actionOpen_file")
        self.actionClose_program = QtWidgets.QAction(DriftscanWindow)
        self.actionClose_program.setObjectName("actionClose_program")
        self.actionExit = QtWidgets.QAction(DriftscanWindow)
        self.actionExit.setObjectName("actionExit")

        self.retranslateUi(DriftscanWindow)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(DriftscanWindow)

    def retranslateUi(self, DriftscanWindow):
        _translate = QtCore.QCoreApplication.translate
        DriftscanWindow.setWindowTitle(_translate("DriftscanWindow", "DRAN - View/Edit Driftscan"))
        self.LblFilename.setText(_translate("DriftscanWindow", "File:"))
        self.LblCurDate.setText(_translate("DriftscanWindow", "Current date:"))
        self.LblObsDate.setText(_translate("DriftscanWindow", "Obs Date:"))
        self.LblObsTime_2.setText(_translate("DriftscanWindow", "Obs time:"))
        self.LblObsTime_4.setText(_translate("DriftscanWindow", "HA:"))
        self.LblObjectType.setText(_translate("DriftscanWindow", "Object type:"))
        self.LblObjectName.setText(_translate("DriftscanWindow", "Object name:"))
        self.LblMjd.setText(_translate("DriftscanWindow", "MJD:"))
        self.LblObsTime_3.setText(_translate("DriftscanWindow", "ZA:"))
        self.LblFreq.setText(_translate("DriftscanWindow", "Frequency:"))
        self.LblTsysLCP.setText(_translate("DriftscanWindow", "Tsys LCP:"))
        self.LblTsysRCP.setText(_translate("DriftscanWindow", "Tsys RCP"))
        self.LblObsTime_5.setText(_translate("DriftscanWindow", "HPBW:"))
        self.LblTemp.setText(_translate("DriftscanWindow", "Amb Temp:"))
        self.LblPres.setText(_translate("DriftscanWindow", "Pressure:"))
        self.LblHum.setText(_translate("DriftscanWindow", "Humidity:"))
        self.LblObsTime_6.setText(_translate("DriftscanWindow", "FNBW"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("DriftscanWindow", "Scan properties"))
        self.plot_groupbox.setTitle(_translate("DriftscanWindow", "Fitting criteria:"))
        self.label.setText(_translate("DriftscanWindow", "Fit type:"))
        self.ComboBoxFitType.setItemText(0, _translate("DriftscanWindow", "Polynomial"))
        self.ComboBoxFitType.setItemText(1, _translate("DriftscanWindow", "Gaussian"))
        self.label_2.setText(_translate("DriftscanWindow", "Fit Location:"))
        self.ComboBoxFitLoc.setItemText(0, _translate("DriftscanWindow", "Base"))
        self.ComboBoxFitLoc.setItemText(1, _translate("DriftscanWindow", "Peak"))
        self.label_3.setText(_translate("DriftscanWindow", "Fit Order:"))
        self.ComboBoxFitOrder.setItemText(0, _translate("DriftscanWindow", "1"))
        self.ComboBoxFitOrder.setItemText(1, _translate("DriftscanWindow", "2"))
        self.ComboBoxFitOrder.setItemText(2, _translate("DriftscanWindow", "3"))
        self.ComboBoxFitOrder.setItemText(3, _translate("DriftscanWindow", "4"))
        self.ComboBoxFitOrder.setItemText(4, _translate("DriftscanWindow", "5"))
        self.ComboBoxFitOrder.setItemText(5, _translate("DriftscanWindow", "6"))
        self.ComboBoxFitOrder.setItemText(6, _translate("DriftscanWindow", "7"))
        self.ComboBoxFitOrder.setItemText(7, _translate("DriftscanWindow", "8"))
        self.ComboBoxFitOrder.setItemText(8, _translate("DriftscanWindow", "9"))
        self.ComboBoxFitOrder.setItemText(9, _translate("DriftscanWindow", "10"))
        self.label_4.setText(_translate("DriftscanWindow", "Filter:"))
        self.ComboBoxFilterType.setItemText(0, _translate("DriftscanWindow", "Rms cuts"))
        self.ComboBoxFilterType.setItemText(1, _translate("DriftscanWindow", "Smoothing"))
        self.LblFilteringWindow.setText(_translate("DriftscanWindow", "Window: "))
        self.single_beam_groupbox.setTitle(_translate("DriftscanWindow", "Data fitting:"))
        self.BtnFilterData.setText(_translate("DriftscanWindow", "Filter data"))
        self.BtnFitData.setText(_translate("DriftscanWindow", "Fit data"))
        self.BtnClearSelection.setText(_translate("DriftscanWindow", "Clear selection"))
        self.BtnSave.setText(_translate("DriftscanWindow", "Save"))
        self.BtnCalc.setText(_translate("DriftscanWindow", "Calculate"))
        self.DropSetPSS.setItemText(0, _translate("DriftscanWindow", "Set PSS"))
        self.BtnGetPSS_2.setText(_translate("DriftscanWindow", "Get PSS"))
        self.BtnPSSreset_2.setText(_translate("DriftscanWindow", "Reset PSS"))
        self.pss_values_groupbox.setTitle(_translate("DriftscanWindow", "Estimate flux:"))
        self.BtnPopulatePSS.setText(_translate("DriftscanWindow", "Populate PSS from file"))
        self.LblPSSlcpA.setText(_translate("DriftscanWindow", "A LCP PSS:"))
        self.LblPSSlcpB.setText(_translate("DriftscanWindow", "B LCP PSS:"))
        self.LblPSSrcpA.setText(_translate("DriftscanWindow", "A RCP PSS:"))
        self.LblPSSrcpB.setText(_translate("DriftscanWindow", "B RCP PSS:"))
        self.BtnSavePSS.setText(_translate("DriftscanWindow", "Save PSS/Flux"))
        self.BtnResetPSS.setText(_translate("DriftscanWindow", "Reset PSS/Flux"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.fit_window_tab), _translate("DriftscanWindow", "Fit window"))
        self.BtnOpenFile.setText(_translate("DriftscanWindow", "Open File"))
        self.BtnResetStatus.setText(_translate("DriftscanWindow", "Reset status"))
        self.BtnViewStatus.setText(_translate("DriftscanWindow", "View status"))
        self.BtnViewFit.setText(_translate("DriftscanWindow", "View fit"))
        self.BtnResetPlot.setText(_translate("DriftscanWindow", "Reset plot"))
        self.BtnSaveToDb.setText(_translate("DriftscanWindow", "Save to DB"))
        self.checkBox.setText(_translate("DriftscanWindow", "Cross hair"))
        self.LblPlottype.setText(_translate("DriftscanWindow", "Current plot selection:"))
        self.BtnChoosePlot.setText(_translate("DriftscanWindow", "Choose plot"))
        self.actionOpen_file.setText(_translate("DriftscanWindow", "Open file"))
        self.actionClose_program.setText(_translate("DriftscanWindow", "Close program"))
        self.actionExit.setText(_translate("DriftscanWindow", "Exit"))