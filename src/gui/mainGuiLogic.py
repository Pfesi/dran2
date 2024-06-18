# ============================================================================#
# File: main_gui_logic.py                                                     #
# Author: Pfesesani V. van Zyl                                                #
# ============================================================================#

# Standard library imports
# --------------------------------------------------------------------------- #
from ast import Pass
from datetime import datetime
from PyQt5 import QtWidgets # from PyQt6 import QtWidgets
import numpy as np
import sys
import os
import matplotlib.pyplot as pl
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
import pandas as pd
import webbrowser
from astropy.time import Time
import glob

# Local imports
# --------------------------------------------------------------------------- #
sys.path.append("src/")
from common.msgConfiguration import msg_wrapper
from common.sqlite_db import SQLiteDB
# from common.fits_file_reader import FitsFileReader
from common.observation import Observation
# from common.driftScans import DriftScans
import common.fitting as fit
from gui.main_window import Ui_MainWindow
from gui.edit_driftscan_window1 import Ui_DriftscanWindow
from gui.edit_timeseries_window import Ui_TimeSeriesWindow
from gui.view_plots_window import Ui_PlotViewer
from common.file_handler import FileHandler
import common.calibrate as cp
from gui.canvasManager import CanvasManager
from gui.secondaryCanvasManager import SecondaryCanvasManager
from gui.timeseries_canvas import TimeCanvas
# from common.fitting import f as fx
import common.fitting as fit
import common.miscellaneousFunctions as misc
# =========================================================================== #

class Main(QtWidgets.QMainWindow, Ui_MainWindow):
    """ The main class that handles all gui operations."""

    def __init__(self, log):

        super(Main, self).__init__()
        self.log = log 
        self.filePath="" 

        msg_wrapper("debug", self.log.debug,"GUI initiated")

        # Setup the user interface
        self.setupUi(self)
        self.statusbar.showMessage("Ready.")

        # initiate file handling
        self.file=FileHandler(self.log)

        # setup holder for deleted values
        self.deleted=[]
        if self.filePath=="":

            # set button properties
            btnCol='white'
            btnTextCol='black'

            # Connect buttons to window
            self.btn_edit_driftscan.clicked.connect(self.open_drift_window)
            self.btn_edit_timeseries.clicked.connect(self.open_timeseries_window)
            self.btn_view_plots.clicked.connect(self.open_plots_window)
            # self.btn_edit_driftscan.setStyleSheet(f'QPushButton {{background-color: {btnCol}; color: {btnTextCol};}}')
            # self.btn_edit_timeseries.setStyleSheet(f'QPushButton {{background-color: {btnCol}; color: {btnTextCol};}}')
            # self.btn_view_plots.setStyleSheet(f'QPushButton {{background-color: {btnCol}; color: {btnTextCol};}}')

        else:
            self.open_drift_window()
            # self.open_file()

    # === Windows setup   ===
    def open_drift_window(self):
        """ Connect the edit drift scan window to the main window. """

        msg_wrapper("debug", self.log.debug, "Initiating drift scan editing window")

        # Initiate Canvas
        self.Canvas = CanvasManager(log=self.log)
        self.ntb = NavigationToolbar(self.Canvas, self)
        self.drift_window = QtWidgets.QMainWindow()
        self.drift_ui = Ui_DriftscanWindow()
        self.drift_ui.setupUi(self.drift_window)

        # initiate Secondary canvas
        self.secondaryCanvas = SecondaryCanvasManager(log=self.log)

        # Layouts
        plotLayout = self.drift_ui.PlotLayout
        otherPlotLayout = self.drift_ui.otherPlotsLayout

        # Add Canvas/es to the gui
        plotLayout.addWidget(self.ntb)
        plotLayout.addWidget(self.Canvas)
        otherPlotLayout.addWidget(self.secondaryCanvas)

        # Connect buttons to actions performed by user
        self.connect_buttons()

        # Print welcome message
        self.write("DRAN GUI loaded successfully.",'info')
        self.write("Open a file to get started.",'info')

        # Set status, indicates whether fit/plot has been modified/not
        self.status = [0, 0, 0, 0, 0, 0]
        self.drift_window.show()

    def open_timeseries_window(self):
        """ Connect the edit timeseries window. """

        msg_wrapper("debug", self.log.debug, "Initiating timeseries editing window")

        # Initiate Canvas
        self.Canvas = TimeCanvas(log=self.log)
        self.ntb = NavigationToolbar(self.Canvas,self) # add nav toolbar
        self.time_window = QtWidgets.QMainWindow()
        self.time_ui = Ui_TimeSeriesWindow()
        self.time_ui.setupUi(self.time_window)

        # Layouts
        plotLayout = self.time_ui.PlotLayout

        # Add canvas to the gui
        plotLayout.addWidget(self.ntb)
        plotLayout.addWidget(self.Canvas)
        
        # connect buttons to actions performed by users
        self.time_ui.BtnResetPoint.setVisible(False)
        self.time_ui.BtnFit.setVisible(True)
        self.time_ui.BtnQuit.setText("Update db")
        self.time_ui.EdtSplKnots.setVisible(False)
        self.time_ui.LblSplKnots.setVisible(False)
        self.time_ui.BtnUpdateDB.setVisible(False)
        self.time_ui.BtnOpenDB.clicked.connect(self.open_db)
        self.time_ui.comboBoxColsYerr.setVisible(True)
        self.time_ui.Lblxlim.setVisible(False)
        self.time_ui.Lblylim.setVisible(False)
        self.time_ui.EdtxlimMin.setVisible(False)
        self.time_ui.EdtxlimMax.setVisible(False)
        self.time_ui.EdtylimMax.setVisible(False)
        self.time_ui.EdtylimMin.setVisible(False)
        self.time_ui.BtnFilter.setEnabled(False)
        self.time_ui.BtnRefreshDB.setVisible(True)
        self.time_ui.BtnSaveDB.setVisible(False)
        self.time_ui.EdtFilter.setEnabled(False)

        self.time_ui.EdtEndDate.setVisible(False)
        self.time_ui.EdtStartDate.setVisible(False)
        self.time_ui.LblEndDate.setVisible(False)
        self.time_ui.LblStartDate.setVisible(False)

        # Setup index change options for combo boxes
        self.time_ui.comboBoxTables.currentIndexChanged.connect(self.on_table_name_changed)
        self.time_ui.comboBoxFitTypes.currentIndexChanged.connect(self.on_fit_changed)

        # connect buttons
        self.time_ui.BtnRefreshDB.clicked.connect(self.refresh_list) #TODO: make this operational
        self.time_window.show()

    def open_plots_window(self):
        """ Connect the plots window to the main window. """

        msg_wrapper("debug", self.log.debug, "Initiating plot viewer window")

        # Initiate viewer
        self.plot_window = QtWidgets.QMainWindow()
        self.plot_ui = Ui_PlotViewer()
        self.plot_ui.setupUi(self.plot_window)

        # fix all else
        self.plot_ui.btnDelete.setEnabled(False)
        self.plot_ui.btnRefreshPlotList.setEnabled(False)
        self.plot_ui.btnShow.setEnabled(False)
        self.plot_ui.comboBox.setEnabled(False)
        self.plot_ui.comboBoxFilter.setEnabled(False)
        self.plot_ui.comboBoxOptions.setEnabled(False)
        self.plot_ui.txtBoxEnd.setEnabled(False)
        self.plot_ui.txtBoxStart.setEnabled(False)

        # Enable open db only
        self.plot_ui.btnOpen.clicked.connect(self.open_db_path)

        # Setup index change options for combo boxes
        self.plot_ui.comboBox.currentIndexChanged.connect(self.on_combo_changed)
        self.plot_ui.comboBoxFilter.currentIndexChanged.connect(self.on_filter_changed)
        
        # # Connect buttons to actions performed by user
        self.plot_ui.btnRefreshPlotList.clicked.connect(self.add_items_to_combobox)
        
        self.plot_ui.btnShow.clicked.connect(self.show_plot_browser)
        self.plot_ui.btnDelete.clicked.connect(self.delete_obs)

        self.plot_window.show()

    # checked start --------
    # ---------------------------
    def write(self,msg,logType=""):
        """ Write to screen and gui """

        if logType=="info":
            msg_wrapper("info", self.log.info, msg)
        else:
            msg_wrapper("debug", self.log.debug, msg)

    def open_file_name_dialog(self, ext):
        """ Open file. Had to use this 
        to avoid segmentation fault: 11 error
        """

        msg_wrapper("debug", self.log.debug, "Open file name dialog")

        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open File", "", "Fits Files ("+ext+");;Fits Files ("+ext+")")

        if fileName:
            return fileName
        else:
            return
        
    def set_fit_parmeters(self,bf=0,pf=0,ps=0):
        """
        Initialize fit status parameters. These are parameters that tell us
        wether a certain part of the scan has been fit or not. The status of 
        the fit can be either 0 (data not fit yet) or 1 (data fitting has 
        been done) for the current scan. A smoothing parameter is also included
        to let us know if smoothing has been done on the original data.

        By default, all the parameters are set to zero.
        """

        msg_wrapper("debug", self.log.debug, "Setting fit status")

        self.base_is_fit = bf        # Baseline has not been corrected
        self.peak_is_fit = pf        # Peak fit has not been done
        self.plot_is_smoothed = ps   # rmscut/smoothing has not been done

    def reset_plot(self):
        """ Reset figure to default settings. """

        self.write("Reset figure to default settings",'info')
        
        # Get the plot index, set fitting done to zero and rest any previous fits
        plotIndex = self.get_plot_index()
        self.fit_done = 0
        self.reset_previous_fits()

        # Reset x and y to factory settings of current plot
        self.reset_xy(plotIndex)

        print('here')
        # Reset the plot
        title = self.set_title()
        self.Canvas.plot_figure(self.x, self.y, title, "Raw data")
        self.Canvas.plot_residual()

        # Reset fit and flag parameters
        self.set_fit_parmeters()
        self.set_flags()
        self.reset_peak(plotIndex)

    def get_plot_index(self):
        """ Get the current plot index. Deliberately set to ind+1 to account for offset."""

        msg_wrapper("debug", self.log.debug,
                    f'Getting plot index {self.drift_ui.ComboBoxPlotType.currentIndex()}\n')
        return int(self.drift_ui.ComboBoxPlotType.currentIndex())+1
    
    def reset_previous_fits(self):
        """ Reset previous fits. """

        msg_wrapper("debug", self.log.debug, "Reset previous fits")
        
        if "D" in self.data["FRONTEND"]:
            self.reset_dual_plot_fit_a()
            self.reset_dual_plot_fit_b()

        if "S" in self.data["FRONTEND"]:
            self.reset_plot_fit()

    def reset_dual_plot_fit_a(self):
        """ Reset all previously fit parameters of the A beam to zreo. """

        self.peakFitA = np.nan
        self.peakRmsA = np.nan
        self.s2nA = np.nan
        self.rmsbA = np.nan
        self.rmsaA = np.nan
        self.base_slopeA = np.nan
        self.base_rmsA = np.nan
        self.peakLocA=np.nan
        
    def reset_dual_plot_fit_b(self):
        """ Reset all previously fit parameters of the B beam to zero. """

        self.peakFitB = np.nan
        self.peakRmsB = np.nan
        self.s2nB = np.nan
        self.rmsbB = np.nan
        self.rmsaB = np.nan
        self.base_slopeB = np.nan
        self.base_rmsB = np.nan
        self.peakLocB=np.nan

    def reset_plot_fit(self):
        """ Reset all previously fit parameters to zero. """

        self.peakFit = np.nan
        self.peakRms = np.nan
        self.s2n = np.nan
        self.baseSlope = np.nan
        self.base_rms = np.nan
        self.peakLoc = np.nan

    def reset_xy(self, ind):
        """ Set X and Y values to current plot. """
        # TODO: check this does what it says it does
        msg_wrapper("debug", self.log.debug, "Setting X and Y")

        # for single beam
        try:
            self.x = self.scans[self.scanKeys[0]]
        except Exception as e:
            print(e)
            self.x = np.zeros_like(1000)

        # for dual beam - check this again
        # try:
        #     ind=ind+2
        #     for i in range(2, len(self.lenScans)):
        #         if ind == i:
        #             self.y = self.scans[self.scanKeys[ind]]
        # except Exception:
        #     self.y = np.zeros_like(1000)

    def set_title(self):
        """ Set the plot title. """

        plotTitle = "Plot of " + \
            self.data['OBJECT']+" @ " + \
            str(self.data['CENTFREQ'])+" MHz"
        return plotTitle
    
    def set_flags(self, flag=100):
        """ Set base flags.
            FLAGS = 100  # Source was manually edited/reduced by user
            This becomes the default for all flags if you save to DB
            while using the GUI.
        """

        msg_wrapper("debug", self.log.debug, "set flags")

        plotIndex = self.get_plot_index()
        beam = self.data['FRONTEND']

        if beam == "13.0S":
            if (self.scanKeys[plotIndex]) == "OLTA":
                self.data['OLFLAG'] = flag

            if (self.scanKeys[plotIndex]) == "ORTA":
                self.data['ORFLAG'] = flag

        else:

            if (self.scanKeys[plotIndex]) == "SLTA":
                try:
                    self.data["SLFLAG"] = flag
                except:
                    pass

            elif (self.scanKeys[plotIndex]) == "NLTA":
                try:
                    self.data["NLFLAG"] = flag
                except:
                    pass

            elif (self.scanKeys[plotIndex]) == "OLTA":
                try:
                    self.data["OLFLAG"] = flag
                except:
                    pass

            elif (self.scanKeys[plotIndex]) == "SRTA":
                try:
                    self.data["SRFLAG"] = flag
                except:
                    pass

            elif (self.scanKeys[plotIndex]) == "NRTA":
                try:
                    self.data["NRFLAG"] = flag
                except:
                    pass

            elif (self.scanKeys[plotIndex]) == "ORTA":
                try:
                    self.data["ORFLAG"] = flag
                except:
                    pass

    def reset_peak(self,plotIndex):
        """ Reset previous peak fits. """ 

        msg_wrapper("debug", self.log.debug, 'reset peak fit')

        if self.data['FRONTEND'] == "13.0S":
            if plotIndex == 0:
                msg_wrapper("debug", self.log.debug, "Data for LCP")
                self.reset_dict("OLTA", "")
            else:
                msg_wrapper("debug", self.log.debug, "Data for RCP")
                self.reset_dict("ORTA", "")

        elif self.data["FRONTEND"] == "02.5S" or self.data["FRONTEND"] == "01.3S" or self.data["FRONTEND"] == "04.5S":
            msg_wrapper("debug", self.log.debug, "Fit stats for " +
                        self.scanKeys[plotIndex]+" data")

            if plotIndex == 0:
                self.reset_dict("SLTA", "NLTA")

            elif plotIndex == 1:
                self.reset_dict("NLTA", "OLTA")

            elif plotIndex == 2:
                self.reset_dict("OLTA", "SRTA")

            elif plotIndex == 3:
                self.reset_dict("SRTA", "NRTA")

            elif plotIndex == 4:
                self.reset_dict("NRTA", "ORTA")

            elif plotIndex == 5:
                self.reset_dict("ORTA", "")

        elif "D" in self.data["FRONTEND"]:
            msg_wrapper("debug", self.log.debug, "Fit stats for " +
                        self.scanKeys[plotIndex]+" data")

            if plotIndex == 0:
                self.reset_dict("ASLTA", "ANLTA")

            elif plotIndex == 1:
                self.reset_dict("ANLTA", "AOLTA")

            elif plotIndex == 2:
                self.reset_dict("AOLTA", "ASRTA")

            elif plotIndex == 3:
                self.reset_dict("ASRTA", "ANRTA")

            elif plotIndex == 4:
                self.reset_dict("ANRTA", "AORTA")

            elif plotIndex == 5:
                self.reset_dict("AORTA", "")

    def reset_dict(self, filter_key1, filter_key2=""):
        """ Reset the data dictionary containing the 
            driftscan keys
        """

        ld = list((self.data).items())
        keys = list((self.data).keys())
        print(ld)
        print(keys)
        print(filter_key1)
        sys.exit()
        # values = list((self.data).values())
        idx_of_key1 = int(keys.index(filter_key1))

        try:
            idx_of_key2 = int(keys.index(filter_key2))

        except:
            idx_of_key2 = len(ld)

        if self.data["FRONTEND"] == "02.5S" or self.data["FRONTEND"] == "01.3S" or "D" in self.data["FRONTEND"]:

            if filter_key1 == "SLTA":
                for i in range(len(ld)):
                    if i >= idx_of_key1 and i < idx_of_key2:
                        if "FLAG" in keys[i]:
                            self.data[keys[i]] = 100
                        else:
                            self.data[keys[i]] = 0
                    else:
                        pass

            elif filter_key1 == "NLTA":
                for i in range(len(ld)):
                    if i >= idx_of_key1 and i < idx_of_key2:
                        if "FLAG" in keys[i]:
                            self.data[keys[i]] = 100
                        else:
                            self.data[keys[i]] = 0
                    else:
                        pass

            elif filter_key1 == "OLTA":
                for i in range(len(ld)):
                    if i >= idx_of_key1 and i < idx_of_key2:
                        if "FLAG" in keys[i]:
                            self.data[keys[i]] = 100
                        else:
                            self.data[keys[i]] = 0
                    else:
                        pass

            elif filter_key1 == "SRTA":
                for i in range(len(ld)):
                    if i >= idx_of_key1 and i < idx_of_key2:
                        if "FLAG" in keys[i]:
                            self.data[keys[i]] = 100
                        else:
                            self.data[keys[i]] = 0
                    else:
                        pass

            elif filter_key1 == "NRTA":
                for i in range(len(ld)):
                    if i >= idx_of_key1 and i < idx_of_key2:
                        if "FLAG" in keys[i]:
                            self.data[keys[i]] = 100
                        else:
                            self.data[keys[i]] = 0
                    else:
                        pass

            elif filter_key1 == "ORTA":
                for i in range(len(ld)):
                    if i >= idx_of_key1:
                        if "FLAG" in keys[i]:
                            self.data[keys[i]] = 100
                        else:
                            self.data[keys[i]] = 0
                    else:
                        pass

        else:
            for i in range(len(ld)):
                if i >= idx_of_key1:
                    if "FLAG" in keys[i]:
                        self.data[keys[i]] = 100
                    else:
                        self.data[keys[i]] = 0

    # ===  Combobox change setup ===
    def on_fit_combobox_changed(self):
        """ Handle events related to the combobox option change. """

        msg_wrapper("debug", self.log.debug, "Fitting ComboBox option changed")

        # Check the selected fit type
        self.write("Now fitting: " +
                self.drift_ui.ComboBoxFitLoc.currentText(),'info')

        # Set the fit type
        if self.drift_ui.ComboBoxFitLoc.currentText() == "Base":
            self.drift_ui.ComboBoxFitOrder.setCurrentIndex(0)

        elif self.drift_ui.ComboBoxFitLoc.currentText() == "Peak":
            self.drift_ui.ComboBoxFitOrder.setCurrentIndex(1)

    def on_filter_type_combobox_changed(self):
        """
        Handle events related to the filter type combobox option change.
        """

        msg_wrapper("debug", self.log.debug, "Combo Box Filter Type Changed")

        if self.drift_ui.ComboBoxFilterType.currentText() == "Please select:":
            self.write("Smoothing the data ",'info')

            # Enable filtering window
            self.drift_ui.EdtFilteringWindow.setEnabled(False)
            self.drift_ui.BtnFilterData.setEnabled(False)

        elif self.drift_ui.ComboBoxFilterType.currentText() == "rms cuts":
            self.write("Performing Rms cuts",'info')

            # Enable filtering window
            self.drift_ui.EdtFilteringWindow.setEnabled(False)
            self.drift_ui.BtnFilterData.setEnabled(True)

        else:
            self.drift_ui.EdtFilteringWindow.setEnabled(True)
            self.drift_ui.BtnFilterData.setEnabled(True)

    def on_fit_type_combobox_changed(self):
        """ Handle events related to the combobox option change. """

        msg_wrapper("debug", self.log.debug,
                    "Fitting ComboBox option changed ")

        fit_type = self.get_fit_type()

        # Check the selected fit type
        self.write(" Now fitting: " + fit_type,'info')

        # Set the fit type
        if fit_type == "Polynomial":

            # Enable peak fitting buttons
            self.drift_ui.ComboBoxFitOrder.setEnabled(True)
            self.drift_ui.ComboBoxFitLoc.setEnabled(True)

    def on_checkbox_changed(self):
        """ Update the cursor depending on checkbox status (on/off)"""

        # Check state of checkbox
        if self.drift_ui.checkBox.isChecked() == True:
            self.write("Checked",'info')
            self.Canvas.cursorState = "on"
        else:
            self.write("Not checked",'info')
            self.Canvas.cursorState = "off"

    # === Enabling, disabling and populating widgets ===

    def enable_widgets(self):
        """ Enable the widgets. """

        msg_wrapper("debug", self.log.debug,"Enabling widgets")

        self.drift_ui.ComboBoxPlotType.setEnabled(True)
        self.drift_ui.ComboBoxFitLoc.setEnabled(True)
        self.drift_ui.ComboBoxFitOrder.setEnabled(True)
        self.drift_ui.ComboBoxFitType.setEnabled(True)
        self.drift_ui.ComboBoxFilterType.setEnabled(True)
        self.drift_ui.EdtFilteringWindow.setEnabled(True)

        # Enable buttons
        self.drift_ui.BtnChoosePlot.setEnabled(True)
        self.drift_ui.BtnViewFit.setEnabled(True)
        self.drift_ui.BtnFitData.setEnabled(True)
        self.drift_ui.BtnClearSelection.setEnabled(True)
        self.drift_ui.BtnResetPlot.setEnabled(True)
        self.drift_ui.BtnSave.setEnabled(True)
        #self.drift_ui.BtnResetFit.setEnabled(True)
        self.drift_ui.BtnSaveToDb.setEnabled(True)
        self.drift_ui.BtnFilterData.setEnabled(True)
        self.drift_ui.BtnCalc.setEnabled(True)

        # enable target buttons
        self.drift_ui.BtnPopulatePSS.setEnabled(True)
        self.drift_ui.BtnSavePSS.setVisible(False)
        self.drift_ui.BtnResetPSS.setVisible(False)

        # Enable checkboxes
        self.drift_ui.checkBox.setEnabled(True)
        self.cursor_state = "off"

    def populate_widgets(self):
        """ Populate the gui widgets. """

        msg_wrapper("debug", self.log.debug,"Populate widgets")

        self.drift_ui.EdtFilename.setText(self.data["FILENAME"])
        self.drift_ui.EdtCurDate.setText(self.data["CURDATETIME"])
        self.drift_ui.EdtObsDate.setText(self.data["OBSDATE"])
        self.drift_ui.EdtObsTime.setText(self.data["OBSTIME"])

        self.drift_ui.EdtObjectType.setText(self.data["OBSERVER"])
        self.drift_ui.EdtObjectName.setText(self.data["OBJECT"])
        self.drift_ui.EdtMjd.setText(str(f'{self.data["MJD"]:.1f}'))

        self.drift_ui.EdtFreq.setText(str(self.data["CENTFREQ"]))
        self.drift_ui.EdtTsysL.setText(str(f'{self.data["TSYS1"]:.1f}'))
        self.drift_ui.EdtTsysR.setText(str(f'{self.data["TSYS2"]:.1f}'))

        self.drift_ui.EdtTemp.setText(str(f'{self.data["TAMBIENT"]:.1f}'))
        self.drift_ui.EdtPres.setText(str(f'{self.data["PRESSURE"]:.1f}'))
        self.drift_ui.EdtHum.setText(str(f'{self.data["HUMIDITY"]:.1f}'))

        self.drift_ui.EdtFnbw.setText(str(f'{self.data["FNBW"]:.2f}'))
        self.drift_ui.EdtHa.setText(str(f'{self.data["HA"]:.1f}'))
        self.drift_ui.EdtZa.setText(str(f'{self.data["ZA"]:.1f}'))
        self.drift_ui.EdtHpbw.setText(str(f'{self.data["HPBW"]:.2f}'))

    def setup_flags(self):
        """ Setup flag parameters, default =100. These
        flags tell us whether a scan has been fit manually
        or not. see set_flags()
        """
        

        msg_wrapper("debug", self.log.debug,"Setting flags")

        if ("13.0S" in self.data["FRONTEND"]):
            self.data["OLFLAG"] = 100
            self.data["ORFLAG"] = 100

        else:
            self.data["SLFLAG"] = 100
            self.data["NLFLAG"] = 100
            self.data["OLFLAG"] = 100
            self.data["SRFLAG"] = 100
            self.data["NRFLAG"] = 100
            self.data["ORFLAG"] = 100
    
    def open_file(self):
        """ Open file for processing. """

        self.write("Opening file",'info')

        # hide pss's
        self.drift_ui.pss_values_groupbox.setVisible(False)

        # Initialize fit parameters
        self.set_fit_parmeters()
        
        # self.filePath = self.open_file_name_dialog("*.fits")
        self.filePath= '/Users/pfesesanivanzyl/data/Calibrators/HydraA/2280/2021d365_00h28m13s_Cont_mike_HYDRA_A.fits'

        if self.filePath == None:
            self.write("You need to select a file to open",'info')
            self.write("Please select a file",'info')
            pass
        else:
            try:
                self.reset_plot()
                self.reset_peak()
            except:
                pass

            self.drift_ui.pss_values_groupbox.setVisible(False)

            # Get data from file
            self.obs=Observation(FILEPATH=self.filePath, theoFit='',autoFit='',log=self.log)
            self.obs.get_data_only()

            self.data, self.scans = {},{}
            self.scanKeys, self.dataKeys = [], []

            for k,v in self.obs.__dict__.items():
                # print(k,v)
                if 'theo' in k or 'auto' in k or 'INFOHEADER' in k or 'log' in k or 'HDULIST' in k or 'CARDS' in k or 'plotDir' in k or 'RAW' in k or 'J2000' in k:
                    pass
                elif 'TA_' in k or 'OFFSET' in k:
                    # if 'OFFSET' in k:
                    #     self.scans['OFFSET']=v
                    # else:
                        print('--- ',k,v)
                        if k=='ON_TA_LCP' or k=='ON_TA_RCP':
                            if 'L' in k:
                                key='OLTA'
                            else:
                                key='ORTA'
                            self.scans[key]=v['value']
                            self.scanKeys.append(key)
                            self.data[key]=v['value']

                        elif k=='HPN_TA_LCP' or k=='HPN_TA_RCP':
                            if 'L' in k:
                                key='NLTA'
                            else:
                                key='NRTA'
                            self.scans[key]=v['value']
                            self.scanKeys.append(key)
                            self.data[key]=v['value']

                        elif k=='HPS_TA_LCP' or k=='HPS_TA_RCP':
                            if 'L' in k:
                                key='SLTA'
                            else:
                                key='SRTA'
                            self.scans[key]=v['value']
                            self.scanKeys.append(key)
                            self.data[key]=v['value']

                        else:
                            self.scans[k]=v['value']
                            self.scanKeys.append(k)
                            # self.data[k]=v['value']
                else:
                    # print(k,v)
                    try:
                        self.data[k] = v['value']
                    except:
                        self.data[k] = v
                    self.dataKeys.append(k)
   
            print('\n')
            print('Data keys: ',self.data.keys(), '\n')
            print('Scan keys: ',self.scans.keys(),'\n')
            # sys.exit()
            # print(self.data['FILEPATH'],'\n')
            # self.lenData= len(self.data)
            self.lenScans= len(self.scans)

            # sys.exit()
            # # self.data = fileReader.data
            # # self.scans = fileReader.scans

            self.Canvas.delete_canvas()

            # set the figure layout
            if "D" in self.data["FRONTEND"]:
                self.Canvas.init_dual_fig_canvas()
                self.Canvas.clear_dual_canvas()
                self.secondaryCanvas.init_canvas()
                self.secondaryCanvas.clear_canvas()
            else:
                self.Canvas.init_fig_canvas()
                self.Canvas.clear_canvas()
                self.secondaryCanvas.init_canvas()
                self.secondaryCanvas.clear_canvas()

            # # Setup pss and flux calculation buttons
            # if (self.data["OBJECTTYPE"] == "CAL"):
            #     self.drift_ui.BtnCalc.setText("Calc PSS")
            #     self.drift_ui.BtnCalc.clicked.connect(self.calc_pss_)
                
            #     # remove pss estimation buttons and boxes
            #     self.drift_ui.pss_values_groupbox.setVisible(False)
            #     #self.disable_target_widgdets()

            # elif self.data["OBJECTTYPE"] == "TAR":
            #     #self.drift_ui.BtnCalc.
            #     self.drift_ui.BtnCalc.setText("Calc Flux")
            #     self.drift_ui.BtnCalc.clicked.connect(self.calc)
            #     self.drift_ui.pss_values_groupbox.setVisible(False)
            #     #self.enable_target_buttons()
 
            self.write("Opened file: "+self.filePath,'info')
            print("\n")
            # sys.exit()
            # Setup environment variables
            # self.set_beam_names()

            self.populate_widgets()
            self.enable_widgets()

            # sys.exit()

            if self.lenScans == 3:
                # for single beam scans
                ind=0
                self.x = self.scans[self.scanKeys[ind]]
                self.y = self.scans[self.scanKeys[ind+1]]
                y1 = self.scans[self.scanKeys[ind+2]]
                self.secondaryCanvas.plot_figure(self.x, self.y, y1, label1=self.scanKeys[ind+1],label2=self.scanKeys[ind+2])
    
            else:
                # for dual beam scans
                ind=0
                self.x = self.scans[self.scanKeys[ind]]
                self.y = self.scans[self.scanKeys[ind+1]]
                y1 = self.scans[self.scanKeys[ind+2]]
                self.secondaryCanvas.plot_figure(self.x, self.y, y1, label1=self.scanKeys[ind+1],label2=self.scanKeys[ind+2])
            
            # Add items to combo boxes
            self.drift_ui.ComboBoxPlotType.clear()
            self.drift_ui.ComboBoxPlotType.clear()
            self.drift_ui.ComboBoxPlotType.addItems(self.scanKeys[1:])

            # sys.exit()
            # allProperties = list(self.data.keys())#[3:]
            #self.drift_ui.ComboBoxScanProperty.setEnabled(True)
            #self.drift_ui.ComboBoxScanProperty.clear()
            #self.drift_ui.ComboBoxScanProperty.addItems(allProperties)
            #self.drift_ui.newPropertyValue.setEnabled(True)
            #self.drift_ui.BtnModify.setEnabled(True)

            self.fit_types = ["Polynomial"]#, "Gaussian"]
            self.drift_ui.ComboBoxFitType.clear()
            self.drift_ui.ComboBoxFitType.clear()
            self.drift_ui.ComboBoxFitType.addItems(self.fit_types)

            self.smoothing_types = ["please select:", "rms cuts", "flat",
                              "hanning", "bartlett", "blackman"]
            self.drift_ui.ComboBoxFilterType.clear()
            self.drift_ui.ComboBoxFilterType.clear()
            self.drift_ui.ComboBoxFilterType.addItems(self.smoothing_types)

            # Setup index change options for combo boxes
            self.drift_ui.ComboBoxFitLoc.currentIndexChanged.connect(
                self.on_fit_combobox_changed)
            self.drift_ui.ComboBoxFilterType.currentIndexChanged.connect(
                self.on_filter_type_combobox_changed)
            self.drift_ui.ComboBoxFitType.currentIndexChanged.connect(
                self.on_fit_type_combobox_changed)
            self.drift_ui.checkBox.stateChanged.connect(
                self.on_checkbox_changed)

            # SET FLAGS
            self.setup_flags()

            # set x,y, plot first image
            # print(ind,self.scanKeys[ind+1])
            # print(len(self.x),len(self.y))
            # sys.exit()
            # self.reset_xy(0)
            # print(len(self.x),len(self.y))
            # sys.exit()
            self.Canvas.plot_figure(self.x, self.y, label=self.scanKeys[ind+1])
            if "D" in self.data["FRONTEND"]:
                self.Canvas.label_dual_res()
            else:
                self.Canvas.label_res()

        self.write("Starting data reduction",'info')

    def update_smoothing_params(self):
        """ Update that plot has been smoothed"""
        #TODO: check this function points to the correct index
        plotIndex = self.get_plot_index()

        if "13.0S" == self.data["FRONTEND"]:

            if plotIndex == 1:
                self.data["OLRMSB"] = self.rmsb
                self.data["OLRMSA"] = self.rmsa

            elif plotIndex == 2:
                self.data["ORRMSB"] = self.rmsb
                self.data["ORRMSA"] = self.rmsa

        elif "01.3S" == self.data["FRONTEND"] or "02.5S" == self.data["FRONTEND"] or "04.5S" == self.data["FRONTEND"]:

            if plotIndex == 1:
                self.data["SLRMSB"] = self.rmsb
                self.data["SLRMSA"] = self.rmsa
            elif plotIndex == 2:
                self.data["NLRMSB"] = self.rmsb
                self.data["NLRMSA"] = self.rmsa
            elif plotIndex == 3:
                self.data["OLRMSB"] = self.rmsb
                self.data["OLRMSA"] = self.rmsa
            elif plotIndex == 4:
                self.data["SRRMSB"] = self.rmsb
                self.data["SRRMSA"] = self.rmsa
            elif plotIndex == 5:
                self.data["NRRMSB"] = self.rmsb
                self.data["NRRMSA"] = self.rmsa
            elif plotIndex == 6:
                self.data["ORRMSB"] = self.rmsb
                self.data["ORRMSA"] = self.rmsa
            else:
                pass
        else:
            pass
    
    def filter_data(self):
        
        """ Filter/smooth the data """

        if self.drift_ui.ComboBoxFilterType.currentText() == "rms cuts":

            # perform rms cuts on the data, remove points with calues > 3*rms

            self.write("Performing rms cuts",'info')
            # ================================================
            # Clean the data using rms cuts
            # ================================================

            scanLen = len(self.x)
            if self.data["CENTFREQ"] <= 3000:
                noTotScans = 2
            else:
                noTotScans = 6

            # spline the data
            spl = fit.spline(self.x, self.y)

            scanRes, self.rmsb, self.rmsa, self.x, self.y, self.res, finMaxSpl, finspl, pointsDeleted = fit.clean_data(
                spl, self.x, self.y, scanLen,self.log)

            self.write(f'RMS before: after -> {self.rmsb}: {self.rmsa}','info')

            self.Canvas.clear_canvas()  # Update figures
            self.update_plot(self.x, self.y, "After rms cuts",
                             self.res, "smoothed data", "smoothed residual")    # Update plot

            #update rms before and after
            self.update_smoothing_params()
            self.plot_is_smoothed = 1

        else:
            msg_wrapper("debug", self.log.debug, "Smoothing window")

            smooth_type = self.drift_ui.ComboBoxFilterType.currentText()

            if smooth_type == "":

                self.write("Please select a filter.")
                self.plot_is_smoothed = 0

            else:
                # TODO: Select a better smoothing algorithm

                # Get value from smoothing window
                window = self.drift_ui.EdtFilteringWindow.text()

                try:
                    window = int(window)
                except Exception as e:
                    self.write("You need to enter a window width")

                if type(window).__name__ == "int":

                    smoothed = fit.filter_scans(self.y, window, smooth_type)

                    self.x = np.arange(0, len(smoothed), 1)
                    self.y = smoothed
                    self.Canvas.clear_canvas()            
                    self.update_plot(self.x, self.y, "After " +
                                    smooth_type+" smoothing", [])

                    self.plot_is_smoothed = 1

    # def sbKeys(self):
    #     sbKeys = ['FILENAME','FILEPATH','HDULENGTH','CURDATETIME','OBSDATE',
    #               'OBSTIME','OBSDATETIME','OBJECT','LONGITUD','LAATITUDE',
    #               'COORDSYS','EQUINOX','RADECSYS','OBSERVER','OBSLOCAL',
    #               'PROJNAME','PROPOSAL','TELESCOP','UPGRADE','FOCUS','TILT',
    #               'TAMBIENT','PRESSURE','HUMIDITY','WINDSPD','SCANDIR',
    #               'POINTING','FEEDTYPE','BMOFFHA']
        
    def view_fit(self):
        """ View current fit info"""

        self.write("Viewing fit information...",'info')

        plotIndex = self.get_plot_index()
        print('*** ',plotIndex)

        print(self.data.keys())
        sys.exit()
        if self.data['FRONTEND'] == "13.0S":
            if plotIndex == 0:
                msg_wrapper("debug", self.log.debug, "Data for LCP")
                self.iter_dict("OLTA", "ORTA")
            else:
                msg_wrapper("debug", self.log.debug, "Data for RCP")
                self.iter_dict("ORTA", "")

        elif self.data["FRONTEND"] == "02.5S" or self.data["FRONTEND"] == "01.3S":
            plotIndex = self.get_plot_index()
            if plotIndex == 0:
                self.write("Fit stats for "+self.scanKeys[plotIndex]+" data",'info')
                self.iter_dict("SLTA", "NLTA")
            elif plotIndex == 1:
                self.write("Fit stats for "+self.scanKeys[plotIndex]+" data", 'info')
                self.iter_dict("NLTA", "OLTA")
            elif plotIndex == 2:
                self.write("Fit stats for "+self.scanKeys[plotIndex]+" data",'info')
                self.iter_dict("OLTA", "SRTA")
            elif plotIndex == 3:
                self.write("Fit stats for "+self.scanKeys[plotIndex]+" data",'info')
                self.iter_dict("SRTA", "NRTA")
            elif plotIndex == 4:
                self.write("Fit stats for "+self.scanKeys[plotIndex]+" data",'info')
                self.iter_dict("NRTA", "ORTA")
            elif plotIndex == 5:
                self.write("Fit stats for "+self.scanKeys[plotIndex]+" data",'info')
                self.iter_dict("ORTA", "")
        
        elif "D" in self.data["FRONTEND"]:
            #TODO: what about "B" scans?

            plotIndex = self.get_plot_index()

            if plotIndex == 0:
                self.write("Fit stats for "+self.scanKeys[plotIndex]+" data",'info')
                self.iter_dict("ASLTA", "ANLTA")
            elif plotIndex == 1:
                self.write("Fit stats for "+self.scanKeys[plotIndex]+" data",'info')
                self.iter_dict("ANLTA", "AOLTA")
            elif plotIndex == 2:
                self.write("Fit stats for "+self.scanKeys[plotIndex]+" data",'info')
                self.iter_dict("AOLTA", "ASRTA")
            elif plotIndex == 3:
                self.write("Fit stats for "+self.scanKeys[plotIndex]+" data",'info')
                self.iter_dict("ASRTA", "ANRTA")
            elif plotIndex == 4:
                self.write("Fit stats for "+self.scanKeys[plotIndex]+" data",'info')
                self.iter_dict("ANRTA", "AORTA")
            elif plotIndex == 5:
                self.write("Fit stats for "+self.scanKeys[plotIndex]+" data",'info')
                self.iter_dict("AORTA", "")
            

    # def iter_dict(self, filter_key1, filter_key2=""):
    #     """
    #     Dictionary iterator to extract current fit information
    #     """

    #     ld = list((self.data).items())
    #     keys = list((self.data).keys())
    #     values = list((self.data).values())

    #     idx_of_key1 = int(keys.index(filter_key1))
    #     try:
    #         idx_of_key2 = int(keys.index(filter_key2))
    #     except:
    #         idx_of_key2 = len(ld)

    #     self.write("Fit stats: \n"+"-"*30,'info')

    #     if self.data["FRONTEND"] == "02.5S" or self.data["FRONTEND"] == "01.3S" or self.data["FRONTEND"] == "04.5S":

    #         if filter_key1 == "SLTA":
    #             for i in range(len(ld)):
    #                 if i >= idx_of_key1 and i < idx_of_key2:
    #                     self.write(str(keys[i]) + ": " + str(values[i]),'info')
    #                 else:
    #                     pass
    #         elif filter_key1 == "NLTA":
    #             for i in range(len(ld)):
    #                 if i >= idx_of_key1 and i < idx_of_key2:
    #                     self.write(str(keys[i]) + ": " + str(values[i]),'info')
    #                 else:
    #                     pass
    #         elif filter_key1 == "OLTA":
    #             for i in range(len(ld)):
    #                 if i >= idx_of_key1 and i < idx_of_key2:
    #                     self.write(str(keys[i]) + ": " + str(values[i]),'info')
    #                 else:
    #                     pass
    #         elif filter_key1 == "SRTA":
    #             for i in range(len(ld)):
    #                 if i >= idx_of_key1 and i < idx_of_key2:
    #                     self.write(str(keys[i]) + ": " + str(values[i]),'info')
    #                 else:
    #                     pass
    #         elif filter_key1 == "NRTA":
    #             for i in range(len(ld)):
    #                 if i >= idx_of_key1 and i < idx_of_key2:
    #                     self.write(str(keys[i]) + ": " + str(values[i]),'info')
    #                 else:
    #                     pass
    #         elif filter_key1 == "ORTA":
    #             for i in range(len(ld)):
    #                 if i >= idx_of_key1:
    #                     self.write(str(keys[i]) + ": " + str(values[i]),'info')
    #                 else:
    #                     pass

    #     elif self.data["FRONTEND"] == "13.0S":
    #         if filter_key1 == "OLTA":
    #             for i in range(len(ld)):
    #                 if i >= idx_of_key1 and i < idx_of_key2 and idx_of_key2 != "":
    #                     self.write(str(keys[i]) + ": " + str(values[i]),'info')
    #         else:
    #             for i in range(len(ld)):
    #                 if i >= idx_of_key1:
    #                     self.write(str(keys[i]) + ": " + str(values[i]),'info')
            

    #     elif "D" in self.data["FRONTEND"]:

    #         if filter_key1 == "ASLTA":
    #             for i in range(len(ld)):
    #                 if i >= idx_of_key1 and i < idx_of_key2:
    #                     self.write(str(keys[i]) + ": " + str(values[i]),'info')
    #                 else:
    #                     pass
    #         elif filter_key1 == "ANLTA":
    #             for i in range(len(ld)):
    #                 if i >= idx_of_key1 and i < idx_of_key2:
    #                     self.write(str(keys[i]) + ": " + str(values[i]),'info')
    #                 else:
    #                     pass
    #         elif filter_key1 == "AOLTA":
    #             for i in range(len(ld)):
    #                 if i >= idx_of_key1 and i < idx_of_key2:
    #                     self.write(str(keys[i]) + ": " + str(values[i]),'info')
    #                 else:
    #                     pass
    #         elif filter_key1 == "ASRTA":
    #             for i in range(len(ld)):
    #                 if i >= idx_of_key1 and i < idx_of_key2:
    #                     self.write(str(keys[i]) + ": " + str(values[i]),'info')
    #                 else:
    #                     pass
    #         elif filter_key1 == "ANRTA":
    #             for i in range(len(ld)):
    #                 if i >= idx_of_key1 and i < idx_of_key2:
    #                     self.write(str(keys[i]) + ": " + str(values[i]),'info')
    #                 else:
    #                     pass
    #         elif filter_key1 == "AORTA":
    #             for i in range(len(ld)):
    #                 if i >= idx_of_key1:
    #                     self.write(str(keys[i]) + ": " + str(values[i]),'info')
    #                 else:
    #                     pass


    # OPERATIONS FOR TIMESERIES
    def open_db(self):
        """ Open the database. """

        # get db file
        self.dbFile = '/Users/pfesesanivanzyl/dran/HART26DATA.db' #'/Users/pfesesanivanzyl/software/working/HartSoftware/dran/CALDB.db' #self.open_file_name_dialog("*.db")
        # get db file
        # self.dbFile = self.open_file_name_dialog("*.db")
        if self.dbFile == None:
            print("No file selected")
        else:
            self.time_ui.EdtDB.setText(self.dbFile)
            self.time_ui.EdtDB.setEnabled(True)
            
            # open the database and get tables
            msg_wrapper("debug", self.log.debug,f'\nOpening database: {self.dbFile}')
            self.db = SQLiteDB(dbPath=self.dbFile, log=self.log)
            self.db.create_db()
            
            # populate columns
            self.dbName=self.dbFile.split('/')[-1]
            self.tables=self.db.get_table_names(self.dbName)
            # self.time_ui.comboBoxTables.
            # print(self.tables)
            # sys.exit()
            # self.db.close_db()
            # self.populate_cols()

            #self.time_ui.comboBoxColsX.setEnabled(True)
            #self.time_ui.comboBoxColsY.setEnabled(True)
            self.enable_time_buttons()
            self.connect_time_buttons()
            self.populate_cols()
            self.db.close_db()
            # print('Closing database: ',self.dbFile)    

    def on_table_name_changed(self):
        """ update combobox when table name changes. """
        self.populate_cols()
    
    def populate_cols(self):
        """ Populate x and y columns with data from tables. """
        # TODO: Double check this makes sense
        # open the database and get tables
        # print(self.dbFile)
        
        self.db = SQLiteDB(dbPath=self.dbFile, log=self.log)
        self.db.create_db()
        self.db.close_db()
        # get column names from currently selected table
        self.table = self.time_ui.comboBoxTables.currentText()
        # print('Reading table: ', self.table)
        # sys.exit()
        # self.db.close_db()

        print('table before issue: ', self.table)
        # print(self.tables)
        
        if not self.table:
            print("Issue: ")
            # force the combobox to accept items
            #self.time_ui.comboBoxTables.addItems(self.tables)
            #self.time_ui.comboBoxTables.addItems(self.tables)
            # self.time_ui.comboBoxTables.clear()
            self.time_ui.comboBoxTables.clear()
            self.time_ui.comboBoxTables.addItems(self.tables)
            # print(self.tables)
            # sys.exit()

            # lt = len(self.tables)
            # lc = self.time_ui.comboBoxTables.count()
            # x = [self.time_ui.comboBoxTables.itemText(i) for i in range(self.time_ui.comboBoxTables.count())]
            self.table = self.time_ui.comboBoxTables.currentText()
            
            # print('lt, lc, x: ',lt,lc,x)
            # print('curtxt now: ',self.time_ui.comboBoxTables.currentText())
            # print(self.table)
            # print(self.tables)
            # sys.exit()
        # print('Outs')
        # sys.exit()
            
        # print(self.table)
        self.db = SQLiteDB(dbPath=self.dbFile, log=self.log)
        self.db.create_db()
        self.colInd, self.colName, self.colType = self.db.get_all_table_coloumns(self.table)
        # self.db.close_db()
        # print('table: ', self.table)
        # print('cols: ',self.colName,'\n')
        
        # self.db = SQLiteDB(databaseName=self.dbFile, log=self.log)
        # self.db.create_db()
        # select only numerical cols with a few exceptions
        colDict={}
        self.colNames=[]
        for i in range(len(self.colInd)):
            colDict[self.colInd[i]] = self.colName[i]
            self.colNames.append(self.colName[i])

        # get rows
        self.rows = self.db.get_rows_of_cols(self.table, self.colNames)
        # self.db.close_db()

        print('creating dataframe from table rows')
        self.df = pd.DataFrame(list(self.rows), columns=self.colNames)
        self.df = self.df.sort_values('FILENAME')
        self.orig_df=self.df # copy of df
        self.df["OBSDATE"]=pd.to_datetime(self.df["OBSDATE"],format="%Y-%m-%d")

        # self.time_ui.comboBoxColsX.clear()
        # self.time_ui.comboBoxColsY.clear()
        # self.time_ui.comboBoxColsYerr.clear()

        # print(self.colNames)
        # sys.exit()
        plotCols=[]
        for name in self.colNames:
            #'id', 'FILENAME', 'FILEPATH', 'HDULENGTH', 'CURDATETIME', 'OBSDATE', 'OBSTIME', 
            # 'OBSDATETIME', 'OBJECT', 'LONGITUD', 'LATITUDE', 'COORDSYS', 'EQUINOX', 'RADECSYS', 
            # 'OBSERVER', 'OBSLOCAL', 'PROJNAME', 'PROPOSAL', 'TELESCOP', 'UPGRADE', 'FOCUS', 'TILT', 
            # 'TAMBIENT', 'PRESSURE', 'HUMIDITY', 'WINDSPD', 'SCANDIR', 'POINTING', 'FEEDTYPE', 
            # 'BMOFFHA', 'BMOFFDEC', 'HPBW', 'FNBW', 'SNBW', 'DICHROIC', 'PHASECAL', 'NOMTSYS', 'FRONTEND', 
            # 'CENTFREQ', 'BANDWDTH', 'INSTRUME', 'INSTFLAG', 'SCANDIST', 'SCANTIME', 'TCAL1', 'TCAL2', 
            # 'HZPERK1', 'HZKERR1', 'HZPERK2', 'HZKERR2', 'TSYS1', 'TSYSERR1', 'TSYS2', 'TSYSERR2', 
            # 'BEAMTYPE', 'LOGFREQ', 'ELEVATION', 'ZA', 'MJD', 'HA', 'PWV', 'SVP', 'AVP', 'DPT', 'WVD', 
            # 'ATMOSABS', 'OBSNAME', 'OLTA', 'OLTAERR', 'OLBRMS', 'OLSLOPE', 'OLMIDOFFSET', 'OLFLAG', 
            # 'OLPEAKLOC', 'OLBASELEFT', 'OLBASERIGHT', 'OLS2N', 'ORTA', 'ORTAERR', 'ORBRMS', 'ORSLOPE', 
            # 'ORMIDOFFSET', 'ORFLAG', 'ORPEAKLOC', 'ORBASELEFT', 'ORBASERIGHT', 'ORS2N', 'SRC'

            if 'id' in name  or 'LOGFREQ' in name or 'CURDATETIME' in name or \
                'FILE' in name or 'OBSD' in name \
                    or 'MJD' in name or 'OBS' in name or 'OBJ' in name or 'id' == name \
                        or 'RAD' in name or 'TYPE' in name or 'PRO' in name or 'TELE' in\
                              name or 'UPGR' in name  or 'INST' in name or \
                                'SCANDIR' in name or 'SRC' in name or 'COORDSYS' in name or 'LONGITUD' in name \
                                    or 'LATITUDE' in name  or 'POINTING' in name \
                                       or 'DICHROIC' in name \
                                            or 'PHASECAL' in name or 'HPBW' in name or 'FNBW' in name or 'SNBW' in name\
                                                or 'FRONTEND' in name or 'BASE' in name: 
                                                    # 'HZK' in name or 'HZP' in name:
                #or 'ERR' in name or 'LD' in name or 'RD' in name or 'HDU' in name or 'EQUINOX' in name or 'SOURCE' in name or 
                #or 'HA' in name  or 'BMOFFHA' in name or 'BMOFFDEC' in name or 'NOMTSYS' in name or 'BANDWDTH' in name 
                # or 'ELEVATION' in name
                pass
            else:
                plotCols.append(name)

        errcols=[]
        for name in self.colNames:
            if   'ERR' in name : #'LD' in name or 'RD' in name or or 'DS' in name or 'DN' in name or 'DO' in name or 'DF' in name or 'DC' in name
                errcols.append(name)
            else:
                pass

        yerr=['None']
        self.time_ui.comboBoxColsX.clear()
        self.time_ui.comboBoxColsX.clear()
        self.time_ui.comboBoxColsX.addItems(['OBSDATE','MJD','HA','ELEVATION'])
        self.time_ui.comboBoxColsY.clear()
        self.time_ui.comboBoxColsY.clear()
        self.time_ui.comboBoxColsY.addItems(plotCols)
       
        self.yErr=list(yerr)+list(errcols)
        self.time_ui.comboBoxColsYerr.clear()
        self.time_ui.comboBoxColsYerr.clear()
        self.time_ui.comboBoxColsYerr.addItems(self.yErr)
        self.db.close_db()

    def on_fit_changed(self):
        """  Toggle labels and edit boxes on or off when fit type is changed."""

        if self.time_ui.comboBoxFitTypes.currentText()=="Spline":
            self.time_ui.LblSplKnots.setVisible(True)
            self.time_ui.EdtSplKnots.setVisible(True)
            self.time_ui.EdtEndDate.setVisible(False)
            self.time_ui.EdtStartDate.setVisible(False)
            self.time_ui.LblEndDate.setVisible(False)
            self.time_ui.LblStartDate.setVisible(False)
        else:
            self.time_ui.LblSplKnots.setVisible(False)
            self.time_ui.EdtSplKnots.setVisible(False)
            self.time_ui.EdtEndDate.setVisible(True)
            self.time_ui.EdtEndDate.setEnabled(True)
            self.time_ui.EdtStartDate.setVisible(True)
            self.time_ui.EdtStartDate.setEnabled(True)
            self.time_ui.LblEndDate.setVisible(True)
            self.time_ui.LblStartDate.setVisible(True)

    def refresh_list(self):
        """Refresh list if database updated"""
        #TODO: enable this function
        pass

    def enable_time_buttons(self):
        """ Enable time buttons. """
        self.time_ui.comboBoxTables.setEnabled(True)
        self.time_ui.comboBoxColsX.setEnabled(True)
        self.time_ui.comboBoxColsY.setEnabled(True)
        self.time_ui.comboBoxColsYerr.setEnabled(True)
        self.time_ui.EdtSplKnots.setEnabled(True)
        self.time_ui.BtnPlot.setEnabled(True)
        self.time_ui.comboBoxFilters.setEnabled(True)
        self.time_ui.EdtFilter.setEnabled(True)
        self.time_ui.BtnFilter.setEnabled(True)
        self.time_ui.comboBoxFitTypes.setEnabled(True)
        self.time_ui.comboBoxOrder.setEnabled(True)
        self.time_ui.BtnFit.setEnabled(True)
        # self.time_ui.BtnSavePlot.setEnabled(True)
        self.time_ui.BtnDelPoint.setEnabled(True)
        self.time_ui.BtnDelBoth.setEnabled(True)
        self.time_ui.BtnResetPoint.setEnabled(True)
        self.time_ui.BtnReset.setEnabled(True)
        self.time_ui.BtnRefreshDB.setEnabled(True)
        self.time_ui.BtnUpdateDB.setEnabled(True)
        self.time_ui.BtnSaveDB.setEnabled(True)
        self.time_ui.BtnQuit.setEnabled(True)

    def connect_time_buttons(self):
        """ connect button key press to widgets. """

        msg_wrapper("debug", self.log.debug,"Connecting buttons to main canvas")

        self.time_ui.BtnPlot.clicked.connect(self.plot_cols)
        self.time_ui.BtnFilter.clicked.connect(self.filter_timeseries_data)
        self.time_ui.BtnFit.clicked.connect(self.fit_timeseries)
        self.time_ui.BtnDelPoint.clicked.connect(self.update_point)#point)
        self.time_ui.BtnDelBoth.clicked.connect(self.update_db_all)#point)
        # self.time_ui.BtnResetPoints.clicked.connect()
        # self.time_ui.BtnSavePlot.clicked.connect()
        # self.time_ui.BtnQuit.clicked.connect()
        self.time_ui.BtnQuit.clicked.connect(self.update_db)
        self.time_ui.BtnReset.clicked.connect(self.reset_timeseries)
        #self.time_ui.BtnOpenDB.clicked.connect(self.open_db)
        self.time_ui.BtnRefreshDB.clicked.connect(self.refresh_db)
        # self.time_ui.BtnUpdateDB.clicked.connect()
        self.time_ui.BtnSaveDB.clicked.connect(self.save_time_db)
        #self.time_ui.BtnFit.clicked.connect(self.fit_timeseries)

    def plot_cols(self,col=""):
        """ Plot database columns. """

        self.db = SQLiteDB(dbPath=self.dbFile, log=self.log)
        self.db.create_db()

        # get column names from currently selected table
        self.table = self.time_ui.comboBoxTables.currentText()
        # print('Table: ', self.table)
        # sys.exit()
        if not self.table:
            print("Issue: ")
            self.time_ui.comboBoxTables.clear()
            self.time_ui.comboBoxTables.clear()
            print('Tables 1: ', self.tables)
            self.time_ui.comboBoxTables.addItems(self.tables)

            lt = len(self.tables)
            lc = self.time_ui.comboBoxTables.count()
            x = [self.time_ui.comboBoxTables.itemText(i) for i in range(self.time_ui.comboBoxTables.count())]
            
        self.colInd, self.colName, self.colType = self.db.get_all_table_coloumns(self.table)

        # select only numerical cols with a few exceptions
        colDict={}
        self.colNames=[]
        for i in range(len(self.colInd)):
            colDict[self.colInd[i]] = self.colName[i]
            self.colNames.append(self.colName[i])

        # get rows
        self.rows = self.db.get_rows_of_cols(self.table, self.colNames)

        # sys.exit()
        self.df = pd.DataFrame(list(self.rows), columns=self.colNames)
        self.df=self.df.sort_values('FILENAME')
        self.df["OBSDATE"]=pd.to_datetime(self.df["OBSDATE"],format="%Y-%m-%d")

        # get col names
        xCol = self.time_ui.comboBoxColsX.currentText()
        yCol = self.time_ui.comboBoxColsY.currentText()
        yErr = self.time_ui.comboBoxColsYerr.currentText()

        # print('yCol: ', yErr)

        if xCol == yCol:
            print("\nYou cannot plot the same column on X and Y\n")
        else:
            # yErr = self.time_ui.comboBoxColsYerr.currentText()

            # get col data
            # self.db.set_table_name(self.table)
            print(f"Plotting {xCol} vs {yCol} in table {self.table}")

            if yErr=="None":
                yerr=np.zeros(len(self.df))
            else:

                # print(self.df[yErr])
                self.df[yErr][self.df[yErr] < 0] = np.nan
                # print(self.df[yErr])
                # sys.exit()
                yerr=self.df[yErr]
                # condition : When True, yield x, otherwise yield y.
                yerr=np.where(yerr<0, np.nan, yerr)

            # print(self.df['OBSDATE'])
            t=self.df[self.df[xCol].isnull()]
            # print(t)
            # print(t[['id','FILENAME','OBSDATE']])

            # Fix the issue with OBSDATE NOT working properly
            for i in range(len(t)):
                fn=t['FILENAME'].iloc[i]
                # print(i,fn)
                date=fn[:8].split('d')
                year=date[0]
                day=date[1]
                # print(date)

                # converting to date
                res = datetime.strptime(year + "-" + day, "%Y-%j").strftime("%Y-%m-%d")
                # print(res)

                # id=int(t['id'].iloc[i])
                # print(id)
                t.at[t.index[i],'OBSDATE'] = res
                self.df.at[self.df.index[i],'OBSDATE'] = res
            # print(t[['id','FILENAME','OBSDATE']])

            #TODO: clean this up
            self.df[xCol].fillna(value=0, inplace=True)
            self.df[xCol].fillna(value=pd.NaT, inplace=True)

            self.df[yCol].fillna(value=np.nan, inplace=True)
           
            
            self.Canvas.plot_fig(self.df[xCol],self.df[yCol],xCol,yCol,data=self.df,yerr=yerr) #,data=self.)
            # sys.exit()
            
            #  <class 'pandas._libs.tslibs.nattype.NaTType'>
        self.db.close_db()

    def filter_timeseries_data(self):
        """ Filter the data"""

        #TODO: fix this - implement rms and binning cuts
        # get current text  from combobox and bins
        filterText = self.time_ui.comboBoxFilters.currentText()
        filterCut = self.time_ui.EdtFilter.text()

        if filterText=="Type":
            print(f'please select a filter type\n')
        else:

            if filterText == ">" or filterText == ">=" or filterText == "<" or filterText == "<=":
            
                try:
                    cut=float(filterCut)
                except:
                    print(f'{filterCut} is an invalid entry for filter {filterText}')
                    cut=""
                
                if cut=="":
                    pass
                else:
                    print(f'filter everything {filterText} {filterCut}')

                    # get x and y
                    if len(self.Canvas.x) == 0:
                        print(self.Canvas.x,self.Canvas.y)
                        print('\nYou need to plot the data first\n')
                    else:
                        x=np.array(self.Canvas.x)
                        y=np.array(self.Canvas.y).astype(float)
                        xCol=self.Canvas.xlab
                        yCol=self.Canvas.ylab

                        # print(self.df[['id','FILENAME','MJD']])

                        # print(f'cut: {cut}')
                        if filterText == ">":
                            cuts=np.where(y>float(cut))[0]
                        elif filterText == ">=":
                            cuts=np.where(y>=float(cut))[0]
                        elif filterText == "<":
                            cuts=np.where(y<float(cut))[0]
                        elif filterText == "<=":
                            cuts=np.where(y<=float(cut))[0]
                        else:
                            print('Invalid cut detected')
                            sys.exit()

                        if len(cuts)>0:
                            print(f'Dropping rows at index {cuts}')
                            #df_cuts=self.df[self.df[xCol]>]
                            self.df=self.df.drop(self.df.index[cuts])
                            #print(self.df)
                            self.deleted.append(cuts)
                            print(f'deleted: {self.deleted}')

                            # re-plot
                            print(self.df['SRC'])
                            print(self.df['FILENAME'][:8])
                            # sys.exit()
                            self.Canvas.plot_fig(self.df[xCol], self.df[yCol], xCol, yCol, data=self.df,title=f"Plot of {self.df['SRC'].iloc[-1]} - {xCol} vs {yCol}") #{self.df['FILENAME'][:8]}")

                        else:
                            print(f"No values found for condition {filterText} {filterCut} ")

            elif filterText == "rms cuts":
                print('RMS cuts not implemented yet.')

            #     print("Performing rms cuts")
            #     # ================================================
            #     # Clean the data using rms cuts
            #     # ================================================

            #     # get df
            #     xCol=self.Canvas.xlab
            #     yCol=self.Canvas.ylab

            #     # need to run this once else it destroys data
            #     self.df[yCol]=self.df[yCol].replace('nan',0)
            #     self.df[yCol].fillna(0,inplace=True)

            #     x=list(self.df[xCol])#np.array(self.Canvas.x)
            #     y=list(self.df[yCol])#np.array(self.Canvas.y).astype(float)
                
            #     scanLen = len(x)
            #     if self.df["CENTFREQ"][int(len(self.df)/2)] <= 3000:
            #         noTotScans = 2
            #     else:
            #         noTotScans = 6

            #     # spline the data
            #     spl = fit.spline(x, y)

            #     pl.plot(x,y)
            #     pl.plot(x,spl)
            #     pl.show()
            #     sys.exit()

            #     if len(spl)==0:
            #         pass
            #     else:
            #         # print('spl: ',spl)
            #         # print('y: ',y)
            #         #sys.exit()
            #         print(self.df['FILENAME'])

            #         scanResBefore, scanRmsBefore = fit.calc_residual(spl, y)
            #         finX, finY, scanRmsAfter, scanResAfter, finMaxSpl, finspl, pt, names = fit.clean_data_iterative_fitting(x, y, scanLen, scanResBefore, scanRmsBefore, self.log, x2=list(self.df["FILENAME"]))

            #         self.write(f'RMS before: after -> {scanRmsBefore:.3f}: {scanRmsAfter:.3f}','info')

            #         self.Canvas.clear_figure()  # Update figures

            #         #self.df[xCol]=""
            #         self.df[yCol]=np.nan

            #         #for j in range(len(list(self.df["FILENAME"]))):
            #         err=self.time_ui.comboBoxColsYerr.currentText()
            #         for i in range(len(names)):
            #             self.df.loc[self.df['FILENAME']==names[i] ,yCol]=finY[i]
            #             #self.df.loc[self.df['FILENAME']==names[i] ,err]=finY[i]
                    
            #         # #self.update_plot(self.x, self.y, "After rms cuts",
            #         # #                self.res, "smoothed data", "smoothed residual")    # Update plot
            #         # if self.time_ui.errorCheckBox.isChecked() == True:
    
            #         #     self.Canvas.plot_fig_errs(self.df[xCol], self.df[yCol], xCol, yCol, data=self.df,errs=self.df[err])
            #         # else:
            #         #     self.Canvas.plot_fig(self.df[xCol], self.df[yCol], xCol, yCol, data=self.df)
                                        

            #         # smallestRmsFound=True
            #         # self.df.fillna(0,inplace=True)
            #         # self.df=self.df.replace('nan',0)
            #         # for col in list(self.df.columns):
            #         #     if "FILENAME" in col or "OBSDATE":# in col or ""
            #         #         pass
            #         #     else:
            #         #         self.df[col] = pd.to_numeric(self.df[col],downcast=float)

                    
            #         # out_df=self.remove_rfi(self.df,xCol,yCol)

            #         # #print(out_df.columns)
                    
            #         # #if (len(out_df) == len(self.df)):
            #         # #    print("Failed to remove RFI, probably data length too short")
            #         # #else:
            #         #     # merge to original
            #         # self.df= pd.merge(self.df, out_df, how='left', on=['MJD'])
            #         #     #self.rename_col(self.df,"_x")
            #         # self.rename_col(self.df,"_y")

            #         # # re-plot
            #         # self.Canvas.clear_figure()
            #         # self.Canvas.plot_fig(self.df[xCol], self.df[yCol], xCol, yCol, data=self.df)
                                    

            #             # rms3_ = 
            #             # scanLen = len(self.Canvas.x)
            #             # if self.data["CENTFREQ"] <= 3000:
            #             #     noTotScans = 2
            #             # else:
            #             #     noTotScans = 6

            #             # # spline the data
            #             # spl = fit.spline(self.Canvas.x, self.Canvas.y)

            #             # scanRes, self.Canvas.x, self.Canvas.y, res, finspl, rmsb, rmsa = fit.cleanRmsCuts2(
            #             #     spl, self.Canvas.x, self.Canvas.y, scanLen, self.log)

            #             # self.write(f'RMS before: after -> {rmsb}: {rmsa,}','info')

            #             # self.Canvas.clear_figure()  # Update figures

            #             # # re-plot
            #             # xCol=self.Canvas.xlab
            #             # yCol=self.Canvas.ylab
            #             #self.Canvas.plot_fig(self.df[xCol] ,self.df[yCol], xCol, yCol, data=self.df)
    
            elif filterText == "binning":
               
               print("Binning not implemented yet\n")

    def fit_timeseries(self):

        # get fit type and fit order
        fitType = self.time_ui.comboBoxFitTypes.currentText()
        fitOrder = self.time_ui.comboBoxOrder.currentText()

        print(f"Fitting: {fitType}, order: {fitOrder}")

        if fitOrder != "Order" and fitType!="Type":

            xCol=self.Canvas.xlab
            yCol=self.Canvas.ylab

            print("col: ",xCol)
            if xCol !="MJD":
                print('Require x-axis as MJD')
            else:
                x=np.array(self.Canvas.x).astype(float)
                y=np.array(self.Canvas.y).astype(float)
                
                if fitType == "Polynomial":
                    try:
                        tstart=int(self.time_ui.EdtStartDate.text())
                    except:
                        tstart="nodate"
                    try:
                        tend=int(self.time_ui.EdtEndDate.text())
                    except:
                        tend="nodate"

                    if tstart == "nodate" and tend=="nodate":
                        print(f'\nstart; {x[0]},  end: {x[-1]}')
                        xm,model,res,rma,coeffs=fit.calc_residual_and_rms_fit(x,y,int(fitOrder))
                        ind=(np.where(model==max(model))[0])[0]
                        # print(ind)
                        # sys.exit()
                        print("\n","*"*20)
                        print(f'tstart: {x[0]}, tend: {x[-1]}')
                        print(f'ymin:{min(y):.3f}, ymax: {max(y):.3f}')
                        print('> model')
                        print(f'ymin:{min(model):.3f}, ymax: {max(model):.3f}, x @ ymax: {xm[ind]}')
                        print(f'rms of fit: {rma:.3f}')
                        print('coeffs: ',coeffs)
                        print("*"*20,"\n")

                        self.Canvas.plot_dual_fig(x,y,xm,model,'data','model','Plot of data vs polynomial model')

                    elif tstart == "nodate" and tend!="nodate":
                        print(f'start; {x[0]},  end: {tend}')
                        
                        if tend < x[0]:
                            print(f"End date ({tend}) needs to be bigger than start date ({x[0]})")
                        else:
                            v=np.where(x <= tend)[0]
                            x1=x[v]
                            y1=y[v]
                            xm,model,res,rma,coeffs=fit.calc_residual_and_rms_fit(x1,y1,int(fitOrder))
                            ind=(np.where(model==max(model))[0])[0]
                            print("\n","*"*20)
                            print(f'tstart: {x[0]}, tend: {tend}')
                            print(f'ymin:{min(y):.3f}, ymax: {max(y):.3f}')
                            print('> model')
                            print(f'ymin:{min(model):.3f}, ymax: {max(model):.3f}, x @ ymax: {xm[ind]}')
                            print(f'rms of fit: {rma:.3f}')
                            print('coeffs: ',coeffs)
                            print("*"*20,"\n")

                            self.Canvas.plot_dual_fig(x,y,xm,model,'data','model','Plot of data vs polynomial model')

                    elif tstart != "nodate" and tend=="nodate":
                        print(f'start; {tstart},  end: {x[-1]}')

                        if tstart > x[-1]:
                            print(f"Start date ({tstart}) needs to be smaller than end date ({x[-1]})")
                        else:
                            v=np.where(x >= tstart)[0]
                            x1=x[v]
                            y1=y[v]
                            xm,model,res,rma,coeffs=fit.calc_residual_and_rms_fit(x1,y1,int(fitOrder))
                            ind=(np.where(model==max(model))[0])[0]

                            print("\n","*"*20)
                            print(f'tstart: {tstart}, tend: {x[-1]}')
                            print(f'ymin:{min(y):.3f}, ymax: {max(y):.3f}')
                            print('> model')
                            print(f'ymin:{min(model):.3f}, ymax: {max(model):.3f}, x @ ymax: {xm[ind]}')
                            print(f'rms of fit: {rma:.3f}')
                            print('coeffs: ',coeffs)
                            print("*"*20,"\n")
                            
                            self.Canvas.plot_dual_fig(x,y,xm,model,'data','model','Plot of data vs polynomial model')

                    elif tstart != "nodate" and tend!="nodate":
                        print(f'start; {tstart},  end: {tend}')

                        if tstart > tend:
                            print(f"Start date ({tstart}) needs to be smaller than end date ({tend})")
                        else:
                            v=np.where((x >= tstart)&(x <= tend))[0]
                            x1=x[v]
                            y1=y[v]
                            xm,model,res,rma,coeffs=fit.calc_residual_and_rms_fit(x1,y1,int(fitOrder))
                            ind=(np.where(model==max(model))[0])[0]

                            print("\n","*"*20)
                            print(f'tstart: {tstart}, tend: {tend}')
                            print(f'ymin:{min(y):.3f}, ymax: {max(y):.3f}')
                            print('> model')
                            print(f'ymin:{min(model):.3f}, ymax: {max(model):.3f}, x @ ymax: {xm[ind]}')
                            print(f'rms of fit: {rma:.3f}')
                            print('coeffs: ',coeffs)
                            print("*"*20,"\n")

                            #print('coeffs: ',coeffs)
                            self.Canvas.plot_dual_fig(x,y,xm,model,'data','model','Plot of data vs polynomial model')
                
                elif fitType == "Spline":
                    knots=int(self.time_ui.EdtSplKnots.text())

                    if knots<9:
                        knots=9
                    xm,model=fit.spline_fit(x, y, int(knots),int(fitOrder))
                    self.Canvas.plot_dual_fig(x,y,xm,model,'data','model','Plot of data vs spline model')
                    
        elif fitOrder == "Order" and fitType!="Type":
            print("\nNo fit order selected\n")
        elif fitOrder != "Order" and fitType=="Type":
            print("\nNo fit type selected\n")
        else:
            print("\nNo fit parameters selected\n")

    def update_point(self):
        #TODO: fix the format
        # update db on change

                    
                    # check last selected points
                    fit_points= self.Canvas.fit_points
                    click_index = self.Canvas.click_index

                    print('\n')
                    print("+"*30)
                    print(f"\nDeleting \n-point: {fit_points} \n-at index {click_index}")
                    #self.deleted[click_index].append([click_index, fit_points])

                    # print('\ndf length Before deleting: ',len(self.df))
                    
                    xCol = self.Canvas.xlab
                    yCol = self.Canvas.ylab

                    print('\n','-'*30)

                    t = Time(fit_points[0][0])
                    #date=t
                    doy = t.strftime('%j')
                    #mjd=t.mjd

                    xp=self.df[xCol]
                    yp=self.df[yCol]

                    date_str=f'{str(fit_points[0][0])[:4]}d{str(doy)}'
                    
                    i=int(click_index[0]) # point index to delete
                    # print('Deleting: ')

                    # find what i is in the db
                    id=self.df['id'].iloc[i]
                    
                    #print(f'i: {ii}, id: {id}')
                    # i=ii#d
                    mjd=self.df['MJD'].iloc[i]
                    FN=self.df['FILENAME'].iloc[i]

                    print('\n-mjd: ',mjd,'\n-file: ',FN) #date_str

                    print(f"\n-id: {self.df['id'].iloc[i]}, \n-index: {i}")
                    
                    print(f'\n> Setting {yCol}: {self.df.iloc[i][yCol]:.3f}, to np.nan')
                    #print(self.df.iloc[i][yCol])
                    
                    try:
                        self.df.at[i,yCol]=np.nan
                    except ValueError:
                        self.df.at[i,yCol]=0.0

                    print(f'\n+ New {yCol}: {self.df.iloc[i][yCol]}')
                    # change plot
                    tablename = self.time_ui.comboBoxTables.currentText()
                  
                    xcol=self.time_ui.comboBoxColsX.currentText()
                    ycol=self.time_ui.comboBoxColsY.currentText()

                    #self.dbFile
                    self.db = SQLiteDB(self.dbFile, log=self.log)
                    self.db.create_db()

                    try:
                        # srcType=self.df['OBJECTTYPE'].iloc[i]
                        self.write(f"Updating {self.dbFile} table: {tablename}",'debug') # , type: {srcType}
                        print('\n-BEAMTYPE: ',self.df['BEAMTYPE'][i]) #,'\n-srcType: ',srcType)
                    except:
                        pass

                    # update the database
                    cols=list(self.df.columns)
                    stmt=f"UPDATE '{tablename}' SET "

                    dct={}

                    dct['BEAMTYPE']=self.df['BEAMTYPE'].iloc[i]

                    try:
                        dct['ATMOS_ABSORPTION_CORR']=self.df['ATMOS_ABSORPTION_CORR'].iloc[i]
                        dct['SIZE_CORRECTION_FACTOR']=self.df['SIZE_CORRECTION_FACTOR'].iloc[i]
                    except:
                        pass
                    
                    bms=['A','B']

                    print("YCOL: ",ycol)
                    if ycol == "SLTA" or ycol=="ASLTA" or ycol=="BSLTA" or ycol=="SLTAERR" or ycol=="ASLTAERR" or ycol=="BSLTAERR" or ycol == "SRTA" or ycol=="ASRTA" or ycol=="BSRTA" or ycol == "SRTAERR" or ycol=="ASRTAERR" or ycol=="BSRTAERR":
                        
                        if ycol[0]=="A":
                            k=0
                        elif ycol[0]=="B":
                            k=1
                        else:
                            k=""
                        if ycol=="SLTA" or ycol=="ASLTA" or ycol=="BSLTA" or ycol=="SLTAERR" or ycol=="ASLTAERR" or ycol=="BSLTAERR":
                            pol="L"
                        elif ycol == "SRTA" or ycol=="ASRTA" or ycol=="BSRTA" or ycol == "SRTAERR" or ycol=="ASRTAERR" or ycol=="BSRTAERR":
                            pol="R"

                        print()

                        try:
                            hps=np.nan
                            err_hps=np.nan
                            hpn=self.df[f'N{pol}TA'].iloc[i]
                            err_hpn=self.df[f'N{pol}TAERR'].iloc[i]
                            on=self.df[f'O{pol}TA'].iloc[i]
                            err_on=self.df[f'O{pol}TAERR'].iloc[i]

                            # single-beam
                            # if "TAR" in self.df['OBJECTTYPE'].iloc[i]:
                            print(f"Using - 'N{pol}TA': {hpn}, 'N{pol}TAERR': {err_hpn}, 'O{pol}TA': {on}, 'O{pol}TAERR': {err_on} to recalculate ")
                            pc, corrTa, errCorrTa=cp.calc_pc(0, 0, 0, hpn, err_hpn, on, err_on, dct)
                            stmt=stmt+f"S{pol}TA='{hps}', S{pol}TAERR='{err_hps}', S{pol}S2N='{np.nan}', O{pol}PC='{pc}', CO{pol}TA='{corrTa}', CO{pol}TAERR='{errCorrTa}', "   
                               
                            # elif "CAL" in self.df['OBJECTTYPE'].iloc[i]:
                            #     print(f"Using - 'N{pol}TA': {hpn}, 'N{pol}TAERR': {err_hpn}, 'O{pol}TA': {on}, 'O{pol}TAERR': {err_on} to recalculate ")
                            #     pss, errPss, pc, corrTa, errCorrTa, appEff=cp.calc_pc_pss(0, 0, 0, hpn, err_hpn, on, err_on, self.df['FLUX'].iloc[i],dct)
                            #     stmt=stmt+f"S{pol}TA='{hps}', S{pol}TAERR='{err_hps}', S{pol}S2N='{np.nan}', O{pol}PSS='{pss}', O{pol}DPSS='{errPss}', O{pol}PC='{pc}', CO{pol}TA='{corrTa}', CO{pol}TAERR='{errCorrTa}', O{pol}APPEFF='{appEff}', "
                                 
                            #     if pss==0.0:
                            #         print(f'- setting O{pol}PSS=np.nan')
                            #         pss=np.nan
                            #     if errPss==0.0:
                            #         errPss=np.nan
                            #         print(f'- setting O{pol}DPSS=np.nan')
                            #     if appEff==0.0:
                            #         appEff=np.nan
                            #         print(f'- setting O{pol}APPEFF=np.nan')

                            if pc==0.0:
                                print(f'- setting O{pol}PC=np.nan')
                                pc=np.nan
                            if corrTa==0.0:
                                corrTa=np.nan
                                print(f'- setting CO{pol}TA=np.nan')
                            if errCorrTa==0.0:
                                errCorrTa=np.nan
                                print(f'- setting CO{pol}TAERR=np.nan')
                            
                        except:
                                hps=np.nan
                                err_hps=np.nan
                                hpn=self.df[f'{bms[k]}N{pol}TA'].iloc[i]
                                err_hpn=self.df[f'{bms[k]}N{pol}TAERR'].iloc[i]
                                on=self.df[f'{bms[k]}O{pol}TA'].iloc[i]
                                err_on=self.df[f'{bms[k]}O{pol}TAERR'].iloc[i]

                                # dual-beam
                                # if "TAR" in self.df['OBJECTTYPE'].iloc[i]:
                                print(f"Using - '{bms[k]}N{pol}TA': {hpn}, '{bms[k]}N{pol}TAERR': {err_hpn}, '{bms[k]}O{pol}TA': {on}, '{bms[k]}O{pol}TAERR': {err_on} to recalculate ")
                                pc, corrTa, errCorrTa=cp.calc_pc(0, 0, 0, hpn, err_hpn, on, err_on, dct)
                                stmt=stmt+f"{bms[k]}S{pol}TA='{np.nan}', {bms[k]}S{pol}TAERR='{np.nan}', {bms[k]}S{pol}S2N='{np.nan}', {bms[k]}O{pol}PC='{pc:.3f}', {bms[k]}CO{pol}TA='{corrTa:.3f}', {bms[k]}CO{pol}TAERR='{errCorrTa:.3f}', "
                                
                                # elif "CAL" in self.df['OBJECTTYPE'].iloc[i]:
                                #     print(f"Using - '{bms[k]}N{pol}TA': {hpn}, '{bms[k]}N{pol}TAERR': {err_hpn}, '{bms[k]}O{pol}TA': {on}, '{bms[k]}O{pol}TAERR': {err_on} to recalculate ")
                                #     pss, errPss, pc, corrTa, errCorrTa, appEff=cp.calc_pc_pss(0, 0, 0, hpn, err_hpn, on, err_on, self.df['FLUX'].iloc[i],dct)
                                #     stmt=stmt+f"{bms[k]}S{pol}TA='{np.nan}', {bms[k]}S{pol}TAERR='{np.nan}', {bms[k]}S{pol}S2N='{np.nan}', {bms[k]}O{pol}PSS='{pss}', {bms[k]}O{pol}DPSS='{errPss}', {bms[k]}O{pol}PC='{pc}', {bms[k]}CO{pol}TA='{corrTa}', {bms[k]}CO{pol}TAERR='{errCorrTa}', {bms[k]}O{pol}APPEFF='{appEff}', "
                                
                                #     if pss==0.0:
                                #         print(f'- setting O{pol}PSS=np.nan')
                                #         pss=np.nan
                                #     if errPss==0.0:
                                #         errPss=np.nan
                                #         print(f'- setting O{pol}DPSS=np.nan')
                                #     if appEff==0.0:
                                #         appEff=np.nan
                                #         print(f'- setting O{pol}APPEFF=np.nan')

                                if pc==0.0:
                                    pc=np.nan
                                    print(f'- setting {bms[k]}O{pol}PC=np.nan')
                                if corrTa==0.0:
                                    corrTa=np.nan
                                    print(f'- setting {bms[k]}CO{pol}TA=np.nan')
                                if errCorrTa==0.0:
                                    errCorrTa=np.nan
                                    print(f'- setting {bms[k]}CO{pol}TAERR=np.nan')
                        
                    elif ycol == "NLTA" or ycol=="ANLTA" or ycol=="BNLTA" or ycol == "NLTAERR" or ycol=="ANLTAERR" or ycol=="BNLTAERR" or ycol == "NRTA" or ycol=="ANRTA" or ycol=="BNRTA" or ycol == "NRTAERR" or ycol=="ANRTAERR" or ycol=="BNRTAERR":
                 
                            if ycol[0]=="A":
                                k=0
                            elif ycol[0]=="B":
                                k=1
                            else:
                                k=""
                            if ycol=="NLTA" or ycol=="ANLTA" or ycol=="BNLTA" or ycol == "NLTAERR" or ycol=="ANLTAERR" or ycol=="BNLTAERR":
                                pol="L"
                            elif ycol == "NRTA" or ycol=="ANRTA" or ycol=="BNRTA" or ycol == "NRTAERR" or ycol=="ANRTAERR" or ycol=="BNRTAERR":
                                pol="R"

                            print()

                            try:
                                hps=self.df[f'S{pol}TA'].iloc[i]
                                err_hps=self.df[f'S{pol}TAERR'].iloc[i]
                                hpn=np.nan
                                err_hpn=np.nan
                                on=self.df[f'O{pol}TA'].iloc[i]
                                err_on=self.df[f'O{pol}TAERR'].iloc[i]

                                # single-beam
                                # if "TAR" in self.df['OBJECTTYPE'].iloc[i]:
                                print(f"Using - 'S{pol}TA': {hps}, 'S{pol}TAERR': {err_hps}, 'O{pol}TA': {on}, 'O{pol}TAERR': {err_on} to recalculate ")
                                pc, corrTa, errCorrTa=cp.calc_pc(0, hps, err_hps, 0, 0, on, err_on, dct)
                                stmt=stmt+f"N{pol}TA='{hpn}', N{pol}TAERR='{err_hpn}', O{pol}PC='{pc}', CO{pol}TA='{corrTa}', CO{pol}TAERR='{errCorrTa}', "   

                                # elif "CAL" in self.df['OBJECTTYPE'].iloc[i]:
                                #     print(f"Using - 'S{pol}TA': {hps}, 'S{pol}TAERR': {err_hps}, 'O{pol}TA': {on}, 'O{pol}TAERR': {err_on} to recalculate ")
                                #     pss, errPss, pc, corrTa, errCorrTa, appEff=cp.calc_pc_pss(0, hps, err_hps, 0, 0, on, err_on, self.df['FLUX'].iloc[i],dct)
                                #     stmt=stmt+f"N{pol}TA='{hpn}', N{pol}TAERR='{err_hpn}', N{pol}S2N='{np.nan}', O{pol}PSS='{pss}', O{pol}DPSS='{errPss}', O{pol}PC='{pc}', CO{pol}TA='{corrTa}', CO{pol}TAERR='{errCorrTa}', O{pol}APPEFF='{appEff}', "
                                
                                #     if pss==0.0:
                                #         print(f'- setting O{pol}PSS=np.nan')
                                #         pss=np.nan
                                #     if errPss==0.0:
                                #         errPss=np.nan
                                #         print(f'- setting O{pol}DPSS=np.nan')
                                #     if appEff==0.0:
                                #         appEff=np.nan
                                #         print(f'- setting O{pol}APPEFF=np.nan')

                                if pc==0.0:
                                    pc=np.nan
                                    print(f'- setting O{pol}PC=np.nan')
                                if corrTa==0.0:
                                    corrTa=np.nan
                                    print(f'- setting CO{pol}TA=np.nan')
                                if errCorrTa==0.0:
                                    errCorrTa=np.nan
                                    print(f'- setting CO{pol}TAERR=np.nan')
                            
                            except:
                                hps=self.df[f'{bms[k]}S{pol}TA'].iloc[i]
                                err_hps=self.df[f'{bms[k]}S{pol}TAERR'].iloc[i]
                                hpn=np.nan
                                err_hpn=np.nan
                                on=self.df[f'{bms[k]}O{pol}TA'].iloc[i]
                                err_on=self.df[f'{bms[k]}O{pol}TAERR'].iloc[i]

                                # dual-beam
                                # if "TAR" in self.df['OBJECTTYPE'].iloc[i]:
                                print(f"Using - '{bms[k]}S{pol}TA': {hps}, '{bms[k]}S{pol}TAERR': {err_hps}, '{bms[k]}O{pol}TA': {on}, '{bms[k]}O{pol}TAERR': {err_on} to recalculate ")
                                pc, corrTa, errCorrTa=cp.calc_pc(0, hps, err_hps, 0, 0,  on, err_on, dct)  
                                stmt=stmt+f"{bms[k]}N{pol}TA='{np.nan}', {bms[k]}N{pol}TAERR='{np.nan}', {bms[k]}N{pol}S2N='{np.nan}', {bms[k]}O{pol}PC='{pc}', {bms[k]}CO{pol}TA='{corrTa}', {bms[k]}CO{pol}TAERR='{errCorrTa}', "
                                
                                # elif "CAL" in self.df['OBJECTTYPE'].iloc[i]:
                                #     print(f"Using - '{bms[k]}S{pol}TA': {hps}, '{bms[k]}S{pol}TAERR': {err_hps}, '{bms[k]}O{pol}TA': {on}, '{bms[k]}O{pol}TAERR': {err_on} to recalculate ")
                                #     pss, errPss, pc, corrTa, errCorrTa, appEff=cp.calc_pc_pss(0, hps, err_hps, 0, 0, on, err_on, self.df['FLUX'].iloc[i],dct)
                                #     stmt=stmt+f"{bms[k]}N{pol}TA='{np.nan}', {bms[k]}N{pol}TAERR='{np.nan}', {bms[k]}N{pol}S2N='{np.nan}', {bms[k]}O{pol}PSS='{pss}', {bms[k]}O{pol}DPSS='{errPss}', {bms[k]}O{pol}PC='{pc}', {bms[k]}CO{pol}TA='{corrTa}', {bms[k]}CO{pol}TAERR='{errCorrTa}', {bms[k]}O{pol}APPEFF='{appEff}', "
                                    
                                #     if pss==0.0:
                                #         print(f'- setting O{pol}PSS=np.nan')
                                #         pss=np.nan
                                #     if errPss==0.0:
                                #         errPss=np.nan
                                #         print(f'- setting O{pol}DPSS=np.nan')
                                #     if appEff==0.0:
                                #         appEff=np.nan
                                #         print(f'- setting O{pol}APPEFF=np.nan')

                                if pc==0.0:
                                    pc=np.nan
                                    print(f'- setting {bms[k]}O{pol}PC=np.nan')
                                if corrTa==0.0:
                                    corrTa=np.nan
                                    print(f'- setting {bms[k]}CO{pol}TA=np.nan')
                                if errCorrTa==0.0:
                                    errCorrTa=np.nan
                                    print(f'- setting {bms[k]}CO{pol}TAERR=np.nan')    
                        
                    elif ycol == "OLTA" or ycol == "COLTA" or ycol == "COLTAERR" or ycol == "ACOLTA" or ycol == "ACOLTAERR" or ycol == "BCOLTA" or ycol == "BCOLTAERR" or ycol == "OLTAERR" or ycol == "AOLTA" or ycol == "BOLTA" or ycol=="ORTA" or ycol=="ORTAERR" or ycol=="AORTA" or ycol=="BORTA" or ycol == "OLPSS"  or ycol=="AOLPSS"  or ycol == "BOLPSS"  or ycol == "ORPSS"  or ycol=="AORPSS"  or ycol == "BORPSS" or ycol == "OLDPSS" or ycol=="AOLDPSS" or ycol == "BOLDPSS" or ycol == "ORDPSS" or ycol=="AORDPSS" or ycol == "BORDPSS" or ycol == "CORTA" or ycol == "CORTAERR" or ycol == "ACORTA" or ycol == "ACORTAERR" or ycol == "BCORTA" or ycol == "BCORTAERR" : 
                        
                        if ycol[0]=="A":
                            k=0
                        elif ycol[0]=="B":
                            k=1
                        else:
                            k=""
                        if   ycol=="OLTA" or ycol=="OLTAERR" or ycol=="AOLTA" or ycol=="BOLTA" or ycol == "OLPSS"  or ycol=="AOLPSS"  or ycol == "BOLPSS" or ycol == "OLDPSS" or ycol=="AOLDPSS" or ycol == "BOLDPSS" or ycol == "COLTA" or ycol == "COLTAERR" or ycol == "ACOLTA" or ycol == "ACOLTAERR" or ycol == "BCOLTA" or ycol == "BCOLTAERR" :
                            pol="L"
                        elif ycol=="ORTA" or ycol=="ORTAERR" or ycol=="AORTA" or ycol=="BORTA" or ycol == "ORPSS"  or ycol=="AORPSS"  or ycol == "BORPSS" or ycol == "ORDPSS" or ycol=="AORDPSS" or ycol == "BORDPSS" or ycol == "CORTA" or ycol == "CORTAERR" or ycol == "ACORTA" or ycol == "ACORTAERR" or ycol == "BCORTA" or ycol == "BCORTAERR" :
                            pol="R"

                        print()

                        # try:

                        # single-beam
                        # if "TAR" in self.df['OBJECTTYPE'].iloc[i]:
                        frq=self.df['CENTFREQ'].iloc[i]
                        if k=="":
                                if int(frq)<=3000:
                                    stmt=stmt+f"O{pol}TA='{np.nan}', O{pol}TAERR='{np.nan}', O{pol}FLAG='{np.nan}', " 
                                else:
                                    stmt=stmt+f"O{pol}FLAG='{np.nan}', O{pol}TA='{np.nan}', O{pol}TAERR='{np.nan}', O{pol}PC='{np.nan}', CO{pol}TA='{np.nan}', CO{pol}TAERR='{np.nan}', S{pol}TA='{np.nan}', S{pol}TAERR='{np.nan}', N{pol}TA='{np.nan}', N{pol}TAERR='{np.nan}',  "
                        else:
                                stmt=stmt+f"{bms[k]}O{pol}FLAG='{np.nan}', {bms[k]}N{pol}TA='{np.nan}', {bms[k]}N{pol}TAERR='{np.nan}', {bms[k]}S{pol}TA='{np.nan}', {bms[k]}S{pol}TAERR='{np.nan}', {bms[k]}O{pol}TA='{np.nan}', {bms[k]}O{pol}TAERR='{np.nan}', {bms[k]}CO{pol}TA='{np.nan}', {bms[k]}CO{pol}TAERR='{np.nan} ',{bms[k]}S{pol}S2N='{np.nan}', {bms[k]}O{pol}PC='{np.nan}', "
                        # except:
                        # elif "CAL" in self.df['OBJECTTYPE'].iloc[i]:
                        #     frq=self.df['CENTFREQ'].iloc[i]
                        #     if k=="":
                        #         if int(frq)<=3000:
                        #             # pss, errPSS, appEff = cp.calc_pss(flux, Ta, errTa)
                        #             stmt=stmt+f"O{pol}TA='{np.nan}', O{pol}TAERR='{np.nan}', O{pol}PSS='{np.nan}', O{pol}DPSS='{np.nan}', O{pol}S2N='{np.nan}', " 
                        #         else:
                        #             stmt=stmt+f"N{pol}TA='{np.nan}', N{pol}TAERR='{np.nan}', S{pol}TA='{np.nan}', S{pol}TAERR='{np.nan}', O{pol}TA='{np.nan}', O{pol}TAERR='{np.nan}', O{pol}PC='{np.nan}', CO{pol}TA='{np.nan}', CO{pol}TAERR='{np.nan}', O{pol}PSS='{np.nan}', O{pol}DPSS='{np.nan}', O{pol}APPEFF='{np.nan}', "
                        #     else:
                        #         stmt=stmt+f"{bms[k]}N{pol}TA='{np.nan}', {bms[k]}N{pol}TAERR='{np.nan}', {bms[k]}S{pol}TA='{np.nan}', {bms[k]}S{pol}TAERR='{np.nan}', {bms[k]}O{pol}TA='{np.nan}', {bms[k]}O{pol}TAERR='{np.nan}', {bms[k]}CO{pol}TA='{np.nan}', {bms[k]}CO{pol}TAERR='{np.nan} ',{bms[k]}S{pol}S2N='{np.nan}', {bms[k]}O{pol}PC='{np.nan}', {bms[k]}O{pol}PSS='{np.nan}', {bms[k]}O{pol}DPSS='{np.nan}', {bms[k]}O{pol}APPEFF='{np.nan}', "
                    
                    else:
                    
                        # only delete that entry
                        # if O
                        stmt=stmt+f"{ycol}='{np.nan}', "

                    stmt=stmt[:-3]+f"'  WHERE FILENAME = '{FN}' ;"
                    print(stmt,'\n')   
                    # sys.exit()
                    self.db.c.execute(stmt)
                    self.db.commit_changes()
                    self.db.close_db()

                    self.Canvas.clear_figure()
                    self.plot_cols_df()
            
                    print("+-"*30)

    def update_db_all(self):
                    #TODO: Fix the format
                    # update db on change

                    # check last selected points
                    fit_points= self.Canvas.fit_points
                    click_index = self.Canvas.click_index

                    print('\n',"+"*30)
                    print(f"\nDeleting \n-point: {fit_points} \n-at index {click_index}")
                    #self.deleted[click_index].append([click_index, fit_points])

                    print('\ndf length Before deleting: ',len(self.df))

                    xCol = self.Canvas.xlab
                    yCol = self.Canvas.ylab

                    print('\n','-'*30)
                    i=int(click_index[0]) # point index to delete
                    # find what i is in the db
                    id=self.df['id'].iloc[i]
                    #print(f'i: {ii}, id: {id}')
                    # i=ii#d
                    FN=self.df['FILENAME'].iloc[i]

                    # if 'TAR' in self.df['OBJECTTYPE'].iloc[i]:

                    t = Time(fit_points[0][0])
                    print(t)
                        # sys.exit()
                        #date=t
                    doy = t.strftime('%j')
                        #mjd=t.mjd

                    xp=self.df[xCol]
                    yp=self.df[yCol]

                    date_str=f'{str(fit_points[0][0])[:4]}d{str(doy)}'
                        

                        # for i in range(len(self.df)):
                            # if date_str in self.df['FILENAME'].iloc[i]:
                                #print(date_str, self.df['FILENAME'].iloc[i])

                        #if self.df[yCol].iloc[i]==float(fit_points[0][1]):
                        

                    print('Deleting: ')

                        

                    print('\n-date: ',date_str,'\n-file: ',FN)

                    print(f"\n-id: {self.df['id'].iloc[i]}, \n-index: {i}")
                        # print('match: ', self.df['id'].iloc[i])#, self.df.iloc[i])
                        
                        #self.df.drop(id,inplace=True)
                        
                    print(f'\n> Setting {yCol}: {self.df.iloc[i][yCol]}, to np.nan')
                        #print(self.df.iloc[i][yCol])
                    try:
                            self.df.at[i,yCol]=np.nan
                    except ValueError:
                            self.df.at[i,yCol]=0.0
                            
                        #self.df=self.df[~(self.df['id']==id)]
                        #print(self.df.iloc[i][yCol])
                    print(f'\n+ New {yCol}: {self.df.iloc[i][yCol]}')
                        # change plot
                    tablename = self.time_ui.comboBoxTables.currentText()
                    
                    xcol=self.time_ui.comboBoxColsX.currentText()
                    ycol=self.time_ui.comboBoxColsY.currentText()

                        #self.dbFile
                    db = SQLiteDB(self.dbFile, log=self.log)
                    db.create_db()

                    try:
                            # srcType=self.df['OBJECTTYPE'].iloc[i]
                        self.write(f"Updating {self.dbFile} table: {tablename}",'debug') # , type: {srcType}
                        print('\n-BEAMTYPE: ',self.df['BEAMTYPE'][i]) #,'\n-srcType: ',srcType)
                    except:
                            pass

                        # update the database
                    cols=list(self.df.columns)
                    stmt=f"UPDATE '{tablename}' SET "

                        
                    for col in cols:
                        if 'id' in col  or 'LOGFREQ' in col or 'CURDATETIME' in col or \
                            'FILE' in col or 'OBSD' in col \
                                or 'MJD' in col or 'OBS' in col or 'OBJ' in col or 'id' == col \
                                    or 'RAD' in col or 'TYPE' in col or 'PRO' in col or 'TELE' in\
                                        col or 'UPGR' in col  or 'INST' in col or \
                                            'SCANDIR' in col or 'SRC' in col or 'COORDSYS' in col or 'LONGITUD' in col \
                                                or 'LATITUDE' in col  or 'POINTING' in col \
                                                or 'DICHROIC' in col \
                                                        or 'PHASECAL' in col or 'HPBW' in col or 'FNBW' in col or 'SNBW' in col\
                                                            or 'FRONTEND' in col or 'BASE' in col: 
                                pass
                        else:
                                stmt=stmt+f"{col}='{np.nan}', "
                    # 

                    stmt=stmt[:-3]+f"'  WHERE FILENAME = '{FN}' ;"
                    print(stmt)        
                 
                  

                    db.c.execute(stmt)
                    db.commit_changes()
                    db.close_db()
                    # print("updated CALDB")
                    print(tablename,xcol,ycol)

                    print('After deleting: ',len(self.df))
                    print(self.df.iloc[i][yCol])
                    self.Canvas.clear_figure()
                    self.plot_cols_df()
                 
    def update_db(self):
                    #TODO: check that this works
                    # update db on change

                    # check last selected points
                    fit_points= self.Canvas.fit_points
                    click_index = self.Canvas.click_index

                    print('\n',"+"*30)
                    print(f"\nDeleting \n-point: {fit_points} \n-at index {click_index}")

                    # print('\ndf length Before deleting: ',len(self.df))

                    xCol = self.Canvas.xlab
                    yCol = self.Canvas.ylab

                    print('\n','-'*30)
                    try:
                        t = Time(fit_points[0][0])
                    except:
                        print('An error occurred, please ensure you click on a point')
                        sys.exit()

                    doy = t.strftime('%j')

                    xp=self.df[xCol]
                    yp=self.df[yCol]

                    date_str=f'{str(fit_points[0][0])[:4]}d{str(doy)}'
                    
                    ii=int(click_index[0]) # point index to delete

                    print('Deleting: ')

                    try:
                        self.df=self.df.replace(None,np.nan)
                    except:
                        pass

                    try:
                        self.df=self.df.replace("nan",np.nan)
                    except:
                        pass

                    # find what i is in the db
                    id=self.df['id'].iloc[ii]

                    i=ii#d
                    FN=self.df['FILENAME'].iloc[i]

                    print('\n-date: ',date_str,'\n-file: ',FN)
                    print(f"\n-id: {self.df['id'].iloc[i]}, \n-index: {ii}")
                    print(f'\n> Setting {yCol}: {self.df.iloc[i][yCol]}, to np.nan')

                    self.df.at[i,yCol]=np.nan
                    print(f'\n+ New {yCol}: {self.df.iloc[i][yCol]}')

                    tablename = self.time_ui.comboBoxTables.currentText()
                  
                    xcol=self.time_ui.comboBoxColsX.currentText()
                    ycol=self.time_ui.comboBoxColsY.currentText()

                    db = self.db #SQLiteDB(databaseName="CALDB.db", log=self.log)
                    db.create_db()

                    srcType=self.df['OBJECTTYPE'].iloc[i]

                    if srcType == "CAL":
                        
                        self.write(f"Updating {self.dbFile} table: {tablename}, type: {srcType}",'info')
                        
                        print('\n-BEAMTYPE: ',self.df['BEAMTYPE'][i],'\n-srcType: ',srcType)

                        # update the database
                        if 'S' in  str(self.df['BEAMTYPE'].iloc[i]):

                            print(self.df['BEAMTYPE'].iloc[i])
                            
                            if "13.0S" == self.df['BEAMTYPE'].iloc[i]:
                                if "TSYS1" in ycol or "TSYS2" in ycol:
                                    if 'TSYS1' in ycol:
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLTA='{np.nan}',  OLTAERR='{np.nan}', OLFLAG=200, OLPSS='{pss}', OLDPSS={errpss},  OLAPPEFF={appeff}, WHERE FILENAME = '{FN}' ;"

                                    if 'TSYS2' in ycol:
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORTA='{np.nan}', ORTAERR='{np.nan}', ORFLAG=200, ORPSS='{pss}', ORDPSS={errpss}, ORAPPEFF={appeff}, WHERE FILENAME = '{FN}' ;"

                                elif "OLTA" in ycol :
                                    pss,errpss,appeff = np.nan,np.nan,np.nan
                                    stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}',OLTAERR='{np.nan}', OLFLAG=201, OLPSS='{pss}', OLDPSS='{errpss}', OLAPPEFF='{appeff}' WHERE FILENAME = '{FN}' ;"

                                elif "ORTA" in ycol :
                                    pss,errpss,appeff = np.nan,np.nan,np.nan
                                    stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}',ORTAERR='{np.nan}', ORFLAG=202, ORPSS='{pss}', ORDPSS='{errpss}', ORAPPEFF='{appeff}' WHERE FILENAME = '{FN}' ;"

                                elif "OLPSS" in ycol:
                                        print('\nprint updating OLPSS')
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLDPSS='{np.nan}', OLFLAG=201, OLAPPEFF='{np.nan}' WHERE FILENAME = '{FN}' ;"

                                elif "ORPSS" in ycol:
                                        print('\nprint updating ORPSS')
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORFLAG=202, ORDPSS='{np.nan}', ORAPPEFF='{np.nan}' WHERE FILENAME = '{FN}' ;"
                                       
                                print(stmt)
                                db.c.execute(stmt)
                                db.commit_changes()
                                db.close_db()
                                print(f"updated {self.dbFile}")
                                print(tablename,xcol,ycol)
                                print('\nDONE')
                                print("+"*30,"\n")

                            else:
                    
                                if "TSYS1" in ycol or "TSYS2" in ycol or 'LS2N' in ycol or 'RS2N' in ycol or 'PC' in ycol :# or "SLTA" in ycol:
                                    if 'TSYS1' in ycol :
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLTA='{np.nan}', SLTA='{np.nan}', \
                                            NLTA='{np.nan}', OLTAERR='{np.nan}', SLTAERR='{np.nan}', NLTAERR='{np.nan}', OLFLAG=200, \
                                                OLS2N='{np.nan}',OLPSS='{np.nan}', OLDPSS='{np.nan}', OLPC='{np.nan}', \
                                                    OLAPPEFF='{np.nan}', COLTA='{np.nan}', COLTAERR='{np.nan}'  WHERE FILENAME = '{FN}' ;"
                                        print("\n",stmt)
                                        db.c.execute(stmt)
                                        db.commit_changes()
                                        db.close_db()
                                        print(f"updated {self.dbFile}")
                                        print(tablename,xcol,ycol)

                                    if 'OLPC' in ycol :
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLTA='{np.nan}', SLTA='{np.nan}', \
                                            NLTA='{np.nan}', OLTAERR='{np.nan}', SLTAERR='{np.nan}', NLTAERR='{np.nan}', OLFLAG=200, \
                                                OLS2N='{np.nan}',OLPSS='{np.nan}', OLDPSS='{np.nan}', OLPC='{np.nan}', \
                                                    OLAPPEFF='{np.nan}', TSYS1='{np.nan}',COLTA='{np.nan}', COLTAERR='{np.nan}'  WHERE FILENAME = '{FN}' ;"
                                        print("\n",stmt)
                                        db.c.execute(stmt)
                                        db.commit_changes()
                                        db.close_db()
                                        print(f"updated {self.dbFile}")
                                        print(tablename,xcol,ycol)

                                    if 'ORPC' in ycol :
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLTA='{np.nan}', SLTA='{np.nan}', \
                                            NLTA='{np.nan}', OLTAERR='{np.nan}', SLTAERR='{np.nan}', NLTAERR='{np.nan}', OLFLAG=200, \
                                                OLS2N='{np.nan}',OLPSS='{np.nan}', OLDPSS='{np.nan}', OLPC='{np.nan}', \
                                                    OLAPPEFF='{np.nan}', TSYS2='{np.nan}',COLTA='{np.nan}', COLTAERR='{np.nan}'  WHERE FILENAME = '{FN}' ;"
                                        print("\n",stmt)
                                        db.c.execute(stmt)
                                        db.commit_changes()
                                        db.close_db()
                                        print(f"updated {self.dbFile}")
                                        print(tablename,xcol,ycol)

                                    if 'TSYS2' in ycol :
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORTA='{np.nan}', SRTA='{np.nan}', NRTA='{np.nan}', \
                                            ORTAERR='{np.nan}', SRTAERR='{np.nan}', NRTAERR='{np.nan}', ORFLAG=200, ORS2N='{np.nan}',ORPSS='{np.nan}', \
                                                ORDPSS='{np.nan}', ORPC='{np.nan}', ORAPPEFF='{np.nan}', CORTA='{np.nan}', CORTAERR={np.nan}  WHERE FILENAME = '{FN}' ;"
                                        print("\n",stmt)
                                        db.c.execute(stmt)
                                        db.commit_changes()
                                        db.close_db()
                                        print(f"updated {self.dbFile}")
                                        print(tablename,xcol,ycol)

                                    if 'SLS2N' in ycol:
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLS2N='{np.nan}',NLS2N='{np.nan}',OLTA='{np.nan}', SLTA='{np.nan}', NLTA='{np.nan}', OLTAERR='{np.nan}', SLTAERR='{np.nan}', NLTAERR='{np.nan}', OLFLAG=200, TSYS1='{np.nan}', OLPSS='{np.nan}', OLDPSS='{np.nan}', OLPC='{np.nan}', OLAPPEFF='{np.nan}', COLTA='{np.nan}', COLTAERR='{np.nan}'  WHERE FILENAME = '{FN}' ;"
                                        print("\n",stmt)
                                        db.c.execute(stmt)
                                        db.commit_changes()
                                        db.close_db()
                                        print(f"updated {self.dbFile}")
                                        print(tablename,xcol,ycol)

                                    if 'NLS2N' in ycol:
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLS2N='{np.nan}',SLS2N='{np.nan}',OLTA='{np.nan}', SLTA='{np.nan}', NLTA='{np.nan}', OLTAERR='{np.nan}', SLTAERR='{np.nan}', NLTAERR='{np.nan}', OLFLAG=200, TSYS1='{np.nan}', OLPSS='{np.nan}', OLDPSS='{np.nan}', OLPC='{np.nan}', OLAPPEFF='{np.nan}', COLTA='{np.nan}', COLTAERR='{np.nan}'  WHERE FILENAME = '{FN}' ;"
                                        print("\n",stmt)
                                        db.c.execute(stmt)
                                        db.commit_changes()
                                        db.close_db()
                                        print(f"updated {self.dbFile}")
                                        print(tablename,xcol,ycol)

                                    if 'OLS2N' in ycol:
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', SLS2N='{np.nan}',NLS2N='{np.nan}',OLTA='{np.nan}', SLTA='{np.nan}', NLTA='{np.nan}', OLTAERR='{np.nan}', SLTAERR='{np.nan}', NLTAERR='{np.nan}', OLFLAG=200, TSYS1='{np.nan}', OLPSS='{np.nan}', OLDPSS='{np.nan}', OLPC='{np.nan}', OLAPPEFF='{np.nan}', COLTA='{np.nan}', COLTAERR='{np.nan}'  WHERE FILENAME = '{FN}' ;"
                                        print("\n",stmt)
                                        db.c.execute(stmt)
                                        db.commit_changes()
                                        db.close_db()
                                        print(f"updated {self.dbFile}")
                                        print(tablename,xcol,ycol)

                                    if 'SRS2N' in ycol:
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORS2N='{np.nan}',NRS2N='{np.nan}',ORTA='{np.nan}', SRTA='{np.nan}', NRTA='{np.nan}', ORTAERR='{np.nan}', SRTAERR='{np.nan}', NRTAERR='{np.nan}', ORFLAG=200, TSYS2='{np.nan}', ORPSS='{np.nan}', ORDPSS='{np.nan}', ORPC='{np.nan}', ORAPPEFF='{np.nan}', CORTA='{np.nan}', CORTAERR={np.nan}  WHERE FILENAME = '{FN}' ;"
                                        print("\n",stmt)
                                       
                                        db.c.execute(stmt)
                                        db.commit_changes()
                                        db.close_db()
                                        print(f"updated {self.dbFile}")
                                        print(tablename,xcol,ycol)

                                    if 'NRS2N' in ycol:
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORS2N='{np.nan}',SRS2N='{np.nan}',ORTA='{np.nan}', SRTA='{np.nan}', NRTA='{np.nan}', ORTAERR='{np.nan}', SRTAERR='{np.nan}', NRTAERR='{np.nan}', ORFLAG=200, TSYS2='{np.nan}', ORPSS='{np.nan}', ORDPSS='{np.nan}', ORPC='{np.nan}', ORAPPEFF='{np.nan}', CORTA='{np.nan}', CORTAERR={np.nan}  WHERE FILENAME = '{FN}' ;"
                                        print("\n",stmt)
                                       
                                        db.c.execute(stmt)
                                        db.commit_changes()
                                        db.close_db()
                                        print(f"updated {self.dbFile}")
                                        print(tablename,xcol,ycol)

                                    if 'ORS2N' in ycol:
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', SRS2N='{np.nan}',NRS2N='{np.nan}',ORTA='{np.nan}', SRTA='{np.nan}', NRTA='{np.nan}', ORTAERR='{np.nan}', SRTAERR='{np.nan}', NRTAERR='{np.nan}', ORFLAG=200, TSYS2='{np.nan}', ORPSS='{np.nan}', ORDPSS='{np.nan}', ORPC='{np.nan}', ORAPPEFF='{np.nan}', CORTA='{np.nan}', CORTAERR={np.nan}  WHERE FILENAME = '{FN}' ;"
                                        print("\n",stmt)
                                       
                                        db.c.execute(stmt)
                                        db.commit_changes()
                                        db.close_db()
                                        print(f"updated {self.dbFile}")
                                        print(tablename,xcol,ycol)

                                elif "OLTA" in ycol or "NLTA" in ycol or "SLTA" in ycol:
                                        
                                        if 'NLTA' in ycol:
                                            if "13.0S" not in str(self.df['BEAMTYPE'].iloc[i]):
                                                onta=self.df['OLTA'].iloc[i]
                                                ontaerr=self.df['OLTAERR'].iloc[i]
                                                sta=self.df['SLTA'].iloc[i]
                                                staerr=self.df['SLTAERR'].iloc[i]

                                                if "01.3S" in str(self.df['BEAMTYPE'].iloc[i]):
                                              
                                                    print('\nupdating 22ghz olpss - nlta')
                                                    pss,errpss,pc,ota,otaerr,appeff = cp.calc_pc_pss(0,sta,staerr, 0.0,0.0,onta,ontaerr,self.df['TOTAL_PLANET_FLUX_D'].iloc[i],self.df)

                                                elif "02.5S" in str(self.df['BEAMTYPE'].iloc[i]):
                                                    print('\nupdating 12ghz olpss - nlta')
                                                    pss,errpss,pc,ota,otaerr,appeff = cp.calc_pc_pss(0,sta,staerr, 0.0,0.0,onta,ontaerr,self.df['FLUX'].iloc[i],self.df)
                                                    
                                                
                                                #print(str(self.df['BEAMTYPE'].iloc[i]),"0.25S","0.25S"==str(self.df['BEAMTYPE'].iloc[i]))
                                                stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', NLTAERR='{np.nan}', OLFLAG=200, OLPSS='{pss}', OLDPSS={errpss}, OLPC={pc}, OLAPPEFF={appeff}, COLTA={ota}, COLTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"
                                                print("\n",stmt)

                                        elif 'SLTA' in ycol:
                                            if "13.0S" not in str(self.df['BEAMTYPE'].iloc[i]):
                                                onta=self.df['OLTA'].iloc[i]
                                                ontaerr=self.df['OLTAERR'].iloc[i]
                                                nta=self.df['NLTA'].iloc[i]
                                                ntaerr=self.df['NLTAERR'].iloc[i]

                                                if "01.3S" in str(self.df['BEAMTYPE'].iloc[i]):
                                                    print('\nupdating 22ghz olpss - slta')
                                                    pss,errpss,pc,ota,otaerr,appeff = cp.calc_pc_pss(0,0.0,0.0,nta,ntaerr,onta,ontaerr,self.df['TOTAL_PLANET_FLUX_D'].iloc[i],self.df)

                                                elif "02.5S" in str(self.df['BEAMTYPE'].iloc[i]):
                                                    print('\nupdating 12ghz olpss - slta')
                                                    pss,errpss,pc,ota,otaerr,appeff = cp.calc_pc_pss(0,0.0,0.0,nta,ntaerr,onta,ontaerr,self.df['FLUX'].iloc[i],self.df)
                                                
                                                stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}',SLTAERR='{np.nan}', OLFLAG=200, OLPSS='{pss}', OLDPSS={errpss}, OLPC={pc}, OLAPPEFF={appeff},COLTA={ota},COLTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"
                                                print(stmt)

                                        else:
                                            print('print updating OLTA')
                                            try:
                                                stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLTAERR='{np.nan}', OLPC='{np.nan}', OLFLAG=200, OLPSS='{np.nan}', OLDPSS='{np.nan}', COLTA='{np.nan}', COLTAERR='{np.nan}',OLAPPEFF='{np.nan}' WHERE FILENAME = '{FN}' ;"
                                            except:
                                                stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}',OLTAERR='{np.nan}',OLFLAG=200, OLPSS='{np.nan}',OLDPSS='{np.nan}',OLAPPEFF='{np.nan}' WHERE FILENAME = '{FN}' ;"
                                            print(stmt)
                                
                                        db.c.execute(stmt)
                                        db.commit_changes()
                                        db.close_db()
                                        print(f"\nupdated {self.dbFile} ")
                                        print(tablename,xcol,ycol)
                                        print('\nDONE')
                                        print("+"*30,"\n")

                                elif "ORTA" in ycol or "NRTA" in ycol or "SRTA" in ycol:
                                    if 'NRTA' in ycol:
                                            if "13.0S" not in str(self.df['BEAMTYPE'].iloc[i]):
                                                onta=self.df['ORTA'].iloc[i]
                                                ontaerr=self.df['ORTAERR'].iloc[i]
                                                sta=self.df['SRTA'].iloc[i]
                                                staerr=self.df['SRTAERR'].iloc[i]

                                                if "01.3S" in str(self.df['BEAMTYPE'].iloc[i]):
                                                    print('updating 22ghz orpss - nrta')
                                                    pss,errpss,pc,ota,otaerr,appeff = cp.calc_pc_pss(0,sta,staerr, 0.0,0.0,onta,ontaerr,self.df['TOTAL_PLANET_FLUX_D'].iloc[i],self.df)

                                                elif "02.5S" in str(self.df['BEAMTYPE'].iloc[i]):
                                                    print('updating 12ghz orpss - nrta')
                                                    pss,errpss,pc,ota,otaerr,appeff = cp.calc_pc_pss(0,sta,staerr, 0.0,0.0,onta,ontaerr,self.df['FLUX'].iloc[i],self.df)
                                                
                                                stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORTAERR='{np.nan}',ORFLAG=200, ORPSS='{pss}', ORDPSS={errpss}, ORPC={pc}, ORAPPEFF={appeff},CORTA={ota},CORTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"
                                                print(stmt)
                                                db.c.execute(stmt)
                                                db.commit_changes()
                                                db.close_db()
                                                print("updated CALDB")
                                                print(tablename,xcol,ycol)
                                                print('DONE')

                                    elif 'SRTA' in ycol:
                                            if "13.0S" not in str(self.df['BEAMTYPE'].iloc[i]):
                                                onta=self.df['ORTA'].iloc[i]
                                                ontaerr=self.df['ORTAERR'].iloc[i]
                                                nta=self.df['NRTA'].iloc[i]
                                                ntaerr=self.df['NRTAERR'].iloc[i]

                                                if "01.3S" in str(self.df['BEAMTYPE'].iloc[i]):
                                                    print('updating 22ghz orpss - srta')
                                                    pss,errpss,pc,ota,otaerr,appeff = cp.calc_pc_pss(0,0.0,0.0,nta,ntaerr,onta,ontaerr,self.df['TOTAL_PLANET_FLUX_D'].iloc[i],self.df)

                                                elif "02.5S" in str(self.df['BEAMTYPE'].iloc[i]):
                                                    print('updating 12ghz orpss - srta')
                                                    pss,errpss,pc,ota,otaerr,appeff = cp.calc_pc_pss(0,0.0,0.0,nta,ntaerr,onta,ontaerr,self.df['FLUX'].iloc[i],self.df)
                                                
                                                stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', SRTAERR='{np.nan}', ORFLAG=200, ORPSS='{pss}', ORDPSS={errpss}, ORPC={pc}, ORAPPEFF={appeff},CORTA={ota},CORTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"
                                                print(stmt)
                                                db.c.execute(stmt)
                                                db.commit_changes()
                                                db.close_db()
                                                print("updated CALDB")
                                                print(tablename,xcol,ycol)
                                                print('DONE')

                                    else:
                                        print('\nprint updating ORTA')
                                        try:
                                            stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORTAERR='{np.nan}', ORFLAG=200, ORPC='{np.nan}', ORPSS='{np.nan}', ORDPSS='{np.nan}', CORTA='{np.nan}', CORTAERR='{np.nan}', ORAPPEFF={appeff} WHERE FILENAME = '{FN}' ;"
                                        except:
                                            stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORFLAG=200, ORPSS='{np.nan}', ORDPSS='{np.nan}' WHERE FILENAME = '{FN}' ;"

                                        print(stmt)
                                        db.c.execute(stmt)
                                        db.commit_changes()
                                        db.close_db()
                                        print("updated CALDB")
                                        print(tablename,xcol,ycol)

                                elif "OLPSS" in ycol:
                                        print('\nprint updating OLPSS')
                                        # try:
                                        #     stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLFLAG=200, COLTA='{np.nan}', COLTAERR='{np.nan}', OLAPPEFF='{np.nan}' WHERE FILENAME = '{FN}' ;"
                                        # except:
                                        #     stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLFLAG=200, OLTA='{np.nan}' WHERE FILENAME = '{FN}' ;"
                                        
                                        # try:
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLDPSS='{np.nan}', OLFLAG=201, OLAPPEFF='{np.nan}' WHERE FILENAME = '{FN}' ;"
                                        # except:
                                        #     stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}',OLTAERR='{np.nan}',OLFLAG=200, OLPSS='{np.nan}',OLDPSS='{np.nan}',OLAPPEFF='{np.nan}' WHERE FILENAME = '{FN}' ;"

                                        print(stmt)
                                        db.c.execute(stmt)
                                        db.commit_changes()
                                        db.close_db()
                                        print(f"updated {self.dbFile}")
                                        print(tablename,xcol,ycol)

                                elif "ORPSS" in ycol:
                                        print('\nprint updating ORPSS')
                                        # try:
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORFLAG=200, ORDPSS='{np.nan}', ORAPPEFF='{np.nan}' WHERE FILENAME = '{FN}' ;"
                                        # except:
                                        #     stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORFLAG=200, ORTA='{np.nan}'  WHERE FILENAME = '{FN}' ;"
                                        print(stmt)
                                        db.c.execute(stmt)
                                        db.commit_changes()
                                        db.close_db()
                                        print(f"updated {self.dbFile}")
                                        print(tablename,xcol,ycol)

                                else:
                                    print('No update')#MISSED: ',ycol)
                                    #sys.exit()

                        elif 'D' in str(self.df['BEAMTYPE'].iloc[0]):
                            print("D in beamtype")

                            if "TSYS1" in ycol or "TSYS2" in ycol:# or "SLTA" in ycol:
                                if 'TSYS1' in ycol:
                                    stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', AOLTA='{np.nan}', ASLTA='{np.nan}', ANLTA='{np.nan}', AOLTAERR='{np.nan}', ASLTAERR='{np.nan}', ANLTAERR='{np.nan}', AOLFLAG=200, AOLPSS='{pss}', AOLDPSS={errpss}, AOLPC={pc}, AOLAPPEFF={appeff}, ACOLTA={ota}, ACOLTAERR={otaerr} \
                                         BOLTA='{np.nan}', BSLTA='{np.nan}', BNLTA='{np.nan}', BOLTAERR='{np.nan}', BSLTAERR='{np.nan}', BNLTAERR='{np.nan}', BOLFLAG=200, BOLPSS='{pss}', BOLDPSS={errpss}, BOLPC={pc}, BOLAPPEFF={appeff}, BCOLTA={ota}, BCOLTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"
                                    print("\n",stmt)
                                if 'TSYS2' in ycol:
                                    stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', AORTA='{np.nan}', ASRTA='{np.nan}', ANRTA='{np.nan}', AORTAERR='{np.nan}', ASRTAERR='{np.nan}', ANRTAERR='{np.nan}', AORFLAG=200, AORPSS='{pss}', AORDPSS={errpss}, AORPC={pc}, AORAPPEFF={appeff}, ACORTA={ota}, ACORTAERR={otaerr}  \
                                         BORTA='{np.nan}', BSRTA='{np.nan}', BNRTA='{np.nan}', BORTAERR='{np.nan}', BSRTAERR='{np.nan}', BNRTAERR='{np.nan}', BORFLAG=200, BORPSS='{pss}', BORDPSS={errpss}, BORPC={pc}, BORAPPEFF={appeff}, BCORTA={ota}, BCORTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"
                                    
                                    print("\n",stmt)

                            elif "AOLTA" in ycol:
                                
                                    stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', AOLTAERR='{np.nan}', OLFLAG=200, AOLPSS='{np.nan}',AOLDPSS='{np.nan}'  WHERE FILENAME = '{FN}' ;"
                                    print(stmt)

                            elif "AORTA" in ycol:
                                    stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', AORTAERR='{np.nan}',ORFLAG=200, AORPSS='{np.nan}' ,AORDPSS='{np.nan}' WHERE FILENAME = '{FN}' ;"
                                    print(stmt)

                            elif "BOLTA" in ycol:
                                    stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', BOLTAERR='{np.nan}', OLFLAG=200, BOLPSS='{np.nan}' ,BOLDPSS='{np.nan}' WHERE FILENAME = '{FN}' ;"
                                    print(stmt)

                            elif "BORTA" in ycol:
                                    stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', BORTAERR='{np.nan}',ORFLAG=200, BORPSS='{np.nan}' ,BORDPSS='{np.nan}' WHERE FILENAME = '{FN}' ;"
                                    print(stmt)

                            elif "AOLPSS" in ycol:
                                    stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', AOLDPSS='{np.nan}', OLFLAG=200  WHERE FILENAME = '{FN}' ;"
                                    print(stmt)

                            elif "AORPSS" in ycol:
                                    stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORFLAG=200, AORDPSS='{np.nan}'  WHERE FILENAME = '{FN}' ;"
                                    print(stmt)

                            elif "BOLPSS" in ycol:
                                    stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLFLAG=200, BOLDPSS='{np.nan}'  WHERE FILENAME = '{FN}' ;"
                                    print(stmt)

                            elif "BORPSS" in ycol:
                                    stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORFLAG=200, BORDPSS='{np.nan}'  WHERE FILENAME = '{FN}' ;"
                                    print(stmt)

                            elif "ASLTA" in ycol or "BSLTA" in ycol:
                                    
                                    if "ASLTA" in ycol:
                                        onta=self.df['AOLTA'].iloc[i]
                                        ontaerr=self.df['AOLTAERR'].iloc[i]
                                        nta=self.df['ANLTA'].iloc[i]
                                        ntaerr=self.df['ANLTAERR'].iloc[i]

                                        print('updating dual aolpss - aSlta')
                                        pss,errpss,pc,ota,otaerr,appeff = cp.calc_pc_pss(0,0.0,0.0, nta,ntaerr,onta,ontaerr,self.df['FLUX'].iloc[i],self.df)
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLFLAG=200, AOLPSS='{pss}', AOLDPSS={errpss}, AOLPC={pc}, AOLAPPEFF={appeff},ACOLTA={ota},ACOLTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"

                                    elif "BSLTA" in ycol:
                                        onta=self.df['BOLTA'].iloc[i]
                                        ontaerr=self.df['BOLTAERR'].iloc[i]
                                        nta=self.df['BNLTA'].iloc[i]
                                        ntaerr=self.df['BNLTAERR'].iloc[i]

                                        print('updating dual aolpss - bSlta')
                                        pss,errpss,pc,ota,otaerr,appeff = cp.calc_pc_pss(0,0.0,0.0, nta,ntaerr,onta,ontaerr,self.df['FLUX'].iloc[i],self.df)
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLFLAG=200, BOLPSS='{pss}', BOLDPSS={errpss}, BOLPC={pc}, BOLAPPEFF={appeff},BCOLTA={ota},BCOLTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"

                                    print(stmt)

                            elif "ANLTA" in ycol or "BNLTA" in ycol:
                                    
                                    if "ANLTA" in ycol:
                                        onta=self.df['AOLTA'].iloc[i]
                                        ontaerr=self.df['AOLTAERR'].iloc[i]
                                        sta=self.df['ASLTA'].iloc[i]
                                        staerr=self.df['ASLTAERR'].iloc[i]

                                        print('updating dual aolpss - aSlta')
                                        pss,errpss,pc,ota,otaerr,appeff = cp.calc_pc_pss(0,sta,staerr, 0.0,0.0,onta,ontaerr,self.df['FLUX'].iloc[i],self.df)
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLFLAG=200, AOLPSS='{pss}', AOLDPSS={errpss}, AOLPC={pc}, AOLAPPEFF={appeff},ACOLTA={ota},ACOLTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"

                                    elif "BNLTA" in ycol:
                                        onta=self.df['BOLTA'].iloc[i]
                                        ontaerr=self.df['BOLTAERR'].iloc[i]
                                        sta=self.df['BSLTA'].iloc[i]
                                        staerr=self.df['BSLTAERR'].iloc[i]

                                        print('updating dual aolpss - bSlta')
                                        pss,errpss,pc,ota,otaerr,appeff = cp.calc_pc_pss(0,sta,staerr, 0.0,0.0,onta,ontaerr,self.df['FLUX'].iloc[i],self.df)
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLFLAG=200, BOLPSS='{pss}', BOLDPSS={errpss}, BOLPC={pc}, BOLAPPEFF={appeff},BCOLTA={ota},BCOLTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"

                                    print(stmt)

                            elif "AOLTA" in ycol or "BOLTA" in ycol:
                                    
                                    if "AOLTA" in ycol:

                                        print('updating dual aolpss - aSlta')
                                        pss,errpss,pc,ota,otaerr,appeff = np.nan,np.nan,np.nan,np.nan,np.nan,np.nan
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLFLAG=200, AOLPSS='{pss}', AOLDPSS={errpss}, AOLPC={pc}, AOLAPPEFF={appeff},ACOLTA={ota},ACOLTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"

                                    elif "BOLTA" in ycol:

                                        print('updating dual aolpss - bSlta')
                                        pss,errpss,pc,ota,otaerr,appeff =np.nan,np.nan,np.nan,np.nan,np.nan,np.nan
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLFLAG=200, BOLPSS='{pss}', BOLDPSS={errpss}, BOLPC={pc}, BOLAPPEFF={appeff},BCOLTA={ota},BCOLTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"

                                    print(stmt)

                            elif "ASRTA" in ycol or "BSRTA" in ycol:
                                    
                                    if "ASRTA" in ycol:
                                        onta=self.df['AORTA'].iloc[i]
                                        ontaerr=self.df['AORTAERR'].iloc[i]
                                        nta=self.df['ANRTA'].iloc[i]
                                        ntaerr=self.df['ANRTAERR'].iloc[i]

                                        print('updating dual aoRpss - aSRta')
                                        pss,errpss,pc,ota,otaerr,appeff = cp.calc_pc_pss(0,0.0,0.0, nta,ntaerr,onta,ontaerr,self.df['FLUX'].iloc[i],self.df)
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORFLAG=200, AORPSS={pss}, AORDPSS={errpss}, AORPC={pc}, AORAPPEFF={appeff},ACORTA={ota},ACORTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"

                                    elif "BSRTA" in ycol:
                                        onta=self.df['BORTA'].iloc[i]
                                        ontaerr=self.df['BORTAERR'].iloc[i]
                                        nta=self.df['BNRTA'].iloc[i]
                                        ntaerr=self.df['BNRTAERR'].iloc[i]

                                        print('updating dual aoRpss - bSRta')
                                        pss,errpss,pc,ota,otaerr,appeff = cp.calc_pc_pss(0,0.0,0.0, nta,ntaerr,onta,ontaerr,self.df['FLUX'].iloc[i],self.df)
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORFLAG=200, BORPSS={pss}, BORDPSS={errpss}, BORPC={pc}, BORAPPEFF={appeff},BCORTA={ota},BCORTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"

                                    print(stmt)

                            elif "ANRTA" in ycol or "BNRTA" in ycol:
                                    
                                    if "ANRTA" in ycol:
                                        onta=self.df['AORTA'].iloc[i]
                                        ontaerr=self.df['AORTAERR'].iloc[i]
                                        sta=self.df['ASRTA'].iloc[i]
                                        staerr=self.df['ASRTAERR'].iloc[i]

                                        print('updating dual aoRpss - aSRta')
                                        pss,errpss,pc,ota,otaerr,appeff = cp.calc_pc_pss(0,sta,staerr, 0.0,0.0,onta,ontaerr,self.df['FLUX'].iloc[i],self.df)
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORFLAG=200, AORPSS={pss}, AORDPSS={errpss}, AORPC={pc}, AORAPPEFF={appeff},ACORTA={ota},ACORTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"

                                    elif "BNRTA" in ycol:
                                        onta=self.df['BORTA'].iloc[i]
                                        ontaerr=self.df['BORTAERR'].iloc[i]
                                        sta=self.df['BSRTA'].iloc[i]
                                        staerr=self.df['BSRTAERR'].iloc[i]

                                        print('updating dual aoRpss - bSlta')
                                        pss,errpss,pc,ota,otaerr,appeff = cp.calc_pc_pss(0,sta,staerr, 0.0,0.0,onta,ontaerr,self.df['FLUX'].iloc[i],self.df)
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORFLAG=200, BORPSS={pss}, BORDPSS={errpss}, BORPC={pc}, BORAPPEFF={appeff},BCORTA={ota},BCORTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"

                                    print(stmt)

                            elif "AORTA" in ycol or "BORTA" in ycol:
                                    
                                    if "AORTA" in ycol:

                                        print('updating dual aoRpss - aSRta')
                                        pss,errpss,pc,ota,otaerr,appeff = np.nan,np.nan,np.nan,np.nan,np.nan,np.nan
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORFLAG=200, AORPSS={pss}, AORDPSS={errpss}, AORPC={pc}, AORAPPEFF={appeff},ACORTA={ota},ACORTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"

                                    elif "BORTA" in ycol:

                                        print('updating dual aoRPss - bSRta')
                                        pss,errpss,pc,ota,otaerr,appeff =np.nan,np.nan,np.nan,np.nan,np.nan,np.nan
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORFLAG=200, BORPSS={pss}, BORDPSS={errpss}, BORPC={pc}, BORAPPEFF={appeff},BCORTA={ota},BCORTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"

                                    print(stmt)

                            db.c.execute(stmt)
                            db.commit_changes()
                            db.close_db()
                            print("updated CALDB")
                            print(tablename,xcol,ycol)
                    
                            # complete the code here
                            # for the rest of them.
                    else:
                        self.write(f"Updating {self.dbFile} table: {tablename}, type: {srcType}",'info')
                        
                        print('\n-BEAMTYPE: ',self.df['BEAMTYPE'].iloc[i],'\n-srcType: ',srcType)

                        # update the database
                        if 'S' in  str(self.df['BEAMTYPE'].iloc[i]):

                            print(self.df['BEAMTYPE'].iloc[i])
                            
                            if "13.0S" == self.df['BEAMTYPE'].iloc[i]:
                                
                                if "TSYS1" in ycol or "TSYS2" in ycol:

                                    if 'TSYS1' in ycol:
                                        stot=self.df['SRCP'].iloc[i]
                                        stoterr=np.sqrt(self.df['SRCPERR'].iloc[i]**2)
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLTA='{np.nan}',  OLTAERR='{np.nan}', OLFLAG=200, SLCP='{np.nan}', SLCPERR='{np.nan}',  STOT='{stot}', STOTERR='{stoterr}' WHERE FILENAME = '{FN}' ;"

                                    if 'TSYS2' in ycol:
                                        stot=self.df['SLCP'].iloc[i]
                                        stoterr=np.sqrt(self.df['SLCPERR'].iloc[i]**2)
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORTA='{np.nan}', ORTAERR='{np.nan}', ORFLAG=200, SRCP='{np.nan}', SRCPERR='{np.nan}',  STOT='{stot}', STOTERR='{stoterr}' WHERE FILENAME = '{FN}' ;"

                                elif "OLTA" in ycol or "SLCP" in ycol :
                                    stot=self.df['SRCP'].iloc[i]
                                    stoterr=np.sqrt(self.df['SRCPERR'].iloc[i]**2)
                                    stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}',OLTAERR='{np.nan}', OLFLAG=201, TSYS1='{np.nan}', SLCP='{np.nan}', SLCPERR='{np.nan}', STOT='{stot}', STOTERR='{stoterr}' WHERE FILENAME = '{FN}' ;"

                                elif "ORTA" in ycol or "SRCP" in ycol:
                                    stot=self.df['SLCP'].iloc[i]
                                    stoterr=np.sqrt(self.df['SLCPERR'].iloc[i]**2)
                                    stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}',ORTAERR='{np.nan}', ORFLAG=201, TSYS2='{np.nan}', SRCP='{np.nan}', SRCPERR='{np.nan}',  STOT='{stot}', STOTERR='{stoterr}' WHERE FILENAME = '{FN}' ;"

                                # elif "SLCP" in ycol:
                                #     print('\nprint updating SLCP')
                                #     stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', SLCPERR='{np.nan}', OLFLAG=202, OLAPPEFF='{np.nan}' WHERE FILENAME = '{FN}' ;"

                                # elif "SRCP" in ycol:
                                #     print('\nprint updating SRCP')
                                #     stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORFLAG=202, ORDPSS='{np.nan}', ORAPPEFF='{np.nan}' WHERE FILENAME = '{FN}' ;"
                                       
                                print(stmt)
                                db.c.execute(stmt)
                                db.commit_changes()
                                db.close_db()
                                print(f"updated {self.dbFile}")
                                print(tablename,xcol,ycol)
                                print('\nDONE')
                                print("+"*30,"\n")

                            else:

                                if "TSYS1" in ycol or "TSYS2" in ycol:

                                    if 'TSYS1' in ycol:
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLTA='{np.nan}', OLTAERR='{np.nan}', COLTA='{np.nan}', COLTAERR='{np.nan}',  OLPC='{np.nan}', OLS2N=200,  \
                                            SLTA='{np.nan}', SLTAERR='{np.nan}', SLS2N='{np.nan}',\
                                            NLTA='{np.nan}', NLTAERR='{np.nan}', NLS2N='{np.nan}',\
                                            SLCP='{np.nan}', SLCPERR='{np.nan}',\
                                            SLCPPSS='{np.nan}', SLCPPSSERR='{np.nan}',\
                                            STOT='{np.nan}', STOTERR='{np.nan}' \
                                            WHERE FILENAME = '{FN}' ;"
                                        
                                    if 'TSYS2' in ycol:
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORTA='{np.nan}', ORTAERR='{np.nan}', CORTA='{np.nan}', CORTAERR='{np.nan}',  ORPC='{np.nan}', ORS2N=200,  \
                                            SRTA='{np.nan}', SRTAERR='{np.nan}', SRS2N='{np.nan}',\
                                            NRTA='{np.nan}', NRTAERR='{np.nan}', NRS2N='{np.nan}',\
                                            SRCP='{np.nan}', SRCPERR='{np.nan}',\
                                            SRCPPSS='{np.nan}', SRCPPSSERR='{np.nan}',\
                                            STOT='{np.nan}', STOTERR='{np.nan}' \
                                            WHERE FILENAME = '{FN}' ;"

                                elif "OLTA" in ycol or "NLTA" in ycol or "SLTA" in ycol:

                                        srcp=self.df['SRCP'].iloc[i]
                                        srcperr=self.df['SRCPERR'].iloc[i]

                                        
                                        if 'NLTA' in ycol:

                                                hpsTa=self.df['SLTA'].iloc[i]
                                                errHpsTa=self.df['SLTAERR'].iloc[i]
                                                onTa=self.df['OLTA'].iloc[i]
                                                errOnTa=self.df['OLTAERR'].iloc[i]
                                                pss=self.df['SLCPPSS'].iloc[i]
                                                errpss=self.df['SLCPPSSERR'].iloc[i]

                                                pc,corrta,errta=cp.calc_pc(0,  hpsTa, errHpsTa, 0, 0, onTa, errOnTa, self.df)

                                                slcp=corrta*pss
                                                slcperr=np.sqrt((corrta/errta)**2 + (pss/errpss)**2)*slcp

                                                stot = (slcp+srcp)/2.
                                                stoterr=0.5*((slcperr)**2 + (srcperr)**2)

                                                stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', NLTAERR='{np.nan}', OLFLAG=200, OLPC={pc}, COLTA={corrta}, COLTAERR={errta}, SLCP={slcp}, SLCPERR={slcperr},STOT={stot}, STOTERR={stoterr}  WHERE FILENAME = '{FN}' ;"
                                               
                                        elif 'SLTA' in ycol:

                                                hpnTa=self.df['NLTA'].iloc[i]
                                                errHpnTa=self.df['NLTAERR'].iloc[i]
                                                onTa=self.df['OLTA'].iloc[i]
                                                errOnTa=self.df['OLTAERR'].iloc[i]
                                                pss=self.df['SLCPPSS'].iloc[i]
                                                errpss=self.df['SLCPPSSERR'].iloc[i]

                                                pc,corrta,errta=cp.calc_pc(0,  0, 0, hpnTa, errHpnTa, onTa, errOnTa, self.df)

                                                slcp=corrta*pss
                                                slcperr=np.sqrt((corrta/errta)**2 + (pss/errpss)**2)*slcp

                                                stot = (slcp+srcp)/2.
                                                stoterr=0.5*((slcperr)**2 + (srcperr)**2)

                                                stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', SLTAERR='{np.nan}', OLFLAG=200, OLPC={pc}, COLTA={corrta}, COLTAERR={errta}, SLCP={slcp}, SLCPERR={slcperr},STOT={stot}, STOTERR={stoterr}  WHERE FILENAME = '{FN}' ;"
                                              
                                        else:
                                            # print('print updating OLTA')
                                            stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLTAERR='{np.nan}', SLTA='{np.nan}',SLTAERR='{np.nan}',NLTA='{np.nan}',\
                                                NLTAERR'{np.nan}',OLPC='{np.nan}', OLFLAG=200, COLTA='{np.nan}', COLTAERR='{np.nan}',OLAPPEFF='{np.nan}',SLCP='{np.nan}', \
                                                SLCPERR='{np.nan}',STOT={srcp},STOTERR={srcperr} WHERE FILENAME = '{FN}' ;"
                                         
                                        db.c.execute(stmt)
                                        db.commit_changes()
                                        db.close_db()
                                        print(f"\nupdated {self.dbFile} ")
                                        print(tablename,xcol,ycol)
                                        print('\nDONE')
                                        print("+"*30,"\n")

                                elif "ORTA" in ycol or "NRTA" in ycol or "SRTA" in ycol:

                                        slcp=self.df['SLCP'].iloc[i]
                                        slcperr=self.df['SLCPERR'].iloc[i]

                                        if 'NRTA' in ycol:

                                                hpsTa=self.df['SRTA'].iloc[i]
                                                errHpsTa=self.df['SRTAERR'].iloc[i]
                                                onTa=self.df['ORTA'].iloc[i]
                                                errOnTa=self.df['ORTAERR'].iloc[i]
                                                pss=self.df['SRCPPSS'].iloc[i]
                                                errpss=self.df['SRCPPSSERR'].iloc[i]

                                                pc,corrta,errta=cp.calc_pc(0,  hpsTa, errHpsTa, 0, 0, onTa, errOnTa, self.df)

                                                srcp=corrta*pss
                                                srcperr=np.sqrt((corrta/errta)**2 + (pss/errpss)**2)*slcp

                                                stot = (slcp+srcp)/2.
                                                stoterr=0.5*((slcperr)**2 + (srcperr)**2)

                                                stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', NRTAERR='{np.nan}', ORFLAG=200, ORPC={pc}, CORTA={corrta}, CORTAERR={errta}, SRCP={slcp}, SRCPERR={slcperr},STOT={stot}, STOTERR={stoterr}  WHERE FILENAME = '{FN}' ;"
                                               
                                        elif 'SRTA' in ycol:

                                                hpnTa=self.df['NLTA'].iloc[i]
                                                errHpnTa=self.df['NLTAERR'].iloc[i]
                                                onTa=self.df['OLTA'].iloc[i]
                                                errOnTa=self.df['OLTAERR'].iloc[i]
                                                pss=self.df['SRCPPSS'].iloc[i]
                                                errpss=self.df['SRCPPSSERR'].iloc[i]

                                                pc,corrta,errta=cp.calc_pc(0,  0, 0, hpnTa, errHpnTa, onTa, errOnTa, self.df)

                                                srcp=corrta*pss
                                                srcperr=np.sqrt((corrta/errta)**2 + (pss/errpss)**2)*slcp

                                                stot = (slcp+srcp)/2.
                                                stoterr=0.5*((slcperr)**2 + (srcperr)**2)

                                                stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', SRTAERR='{np.nan}', ORFLAG=200, ORPC={pc}, CORTA={corrta}, CORTAERR={errta}, SRCP={slcp}, SRCPERR={slcperr},STOT={stot}, STOTERR={stoterr}  WHERE FILENAME = '{FN}' ;"
                                              
                                        else:
                                            # print('print updating OLTA')
                                            stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORTAERR='{np.nan}', SRTA='{np.nan}',SRTAERR='{np.nan}',NRTA='{np.nan}',NRTAERR'{np.nan}',\
                                                ORPC='{np.nan}', ORFLAG=200, CORTA='{np.nan}', CORTAERR='{np.nan}',ORAPPEFF='{np.nan}',SRCP='{np.nan}', SRCPERR='{np.nan}',\
                                                STOT={slcp},STOTERR={slcperr} WHERE FILENAME = '{FN}' ;"
                                         
                                        db.c.execute(stmt)
                                        db.commit_changes()
                                        db.close_db()
                                        print(f"\nupdated {self.dbFile} ")
                                        print(tablename,xcol,ycol)
                                        print('\nDONE')
                                        print("+"*30,"\n")

                                elif "SLCP" in ycol:

                                        # print('\nprint updating OLPSS')
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', SLCPERR='{np.nan}', OLFLAG=201, \
                                            SLTA='{np.nan}', SLTAERR='{np.nan}', SLS2N='{np.nan}',\
                                            NLTA='{np.nan}', NLTAERR='{np.nan}', NLS2N='{np.nan}',\
                                            OLTA='{np.nan}', OLTAERR='{np.nan}', COLTA='{np.nan}', COLTAERR='{np.nan}', OLPC='{np.nan}', OLS2N=202,  \
                                            STOT={srcp}, STOTERR={srcperr}\
                                        WHERE FILENAME = '{FN}' ;"

                                        print(stmt)
                                        db.c.execute(stmt)
                                        db.commit_changes()
                                        db.close_db()
                                        print(f"updated {self.dbFile}")
                                        print(tablename,xcol,ycol)

                                elif "SRCP" in ycol:

                                        # print('\nprint updating ORPSS')
                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', SRCPERR='{np.nan}', ORFLAG=202, \
                                            SRTA='{np.nan}', SRTAERR='{np.nan}', SRS2N='{np.nan}',\
                                            NRTA='{np.nan}', NRTAERR='{np.nan}', NRS2N='{np.nan}',\
                                            ORTA='{np.nan}', ORTAERR='{np.nan}', CORTA='{np.nan}', CORTAERR='{np.nan}', ORPC='{np.nan}', ORS2N=202,  \
                                            STOT={srcp}, STOTERR={srcperr}\
                                        WHERE FILENAME = '{FN}' ;"

                                        print(stmt)
                                        db.c.execute(stmt)
                                        db.commit_changes()
                                        db.close_db()
                                        print(f"updated {self.dbFile}")
                                        print(tablename,xcol,ycol)

                                else:
                                    print('No update algorithm setup yet\n')

                        elif 'D' in str(self.df['BEAMTYPE'].iloc[0]):
                            # print("D in beamtype")1
                            aslcp=self.df['ASLCP'].iloc[i]
                            bslcp=self.df['BSLCP'].iloc[i]
                            asrcp=self.df['ASRCP'].iloc[i]
                            bsrcp=self.df['BSRCP'].iloc[i]
                            aslcperr=self.df['ASLCPERR'].iloc[i]
                            bslcperr=self.df['BSLCPERR'].iloc[i]
                            asrcperr=self.df['ASRCPERR'].iloc[i]
                            bsrcperr=self.df['BSRCPERR'].iloc[i]

                            if "TSYS1" in ycol or "TSYS2" in ycol:

                                if 'TSYS1' in ycol:
                                    stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', \
                                        AOLTA='{np.nan}', AOLTAERR='{np.nan}', OLFLAG=200, AOLPC='{np.nan}',  ACOLTA='{np.nan}', ACOLTAERR='{np.nan}', \
                                        ASLTA='{np.nan}', ASLTAERR='{np.nan}', SLFLAG=200, ANLTA='{np.nan}', ANLTAERR='{np.nan}' \
                                        BSLTA='{np.nan}', BSLTAERR='{np.nan}', NLFLAG=200, BNLTA='{np.nan}', BNLTAERR='{np.nan}', \
                                        BOLTA='{np.nan}', BOLTAERR='{np.nan}', BOLPC='{np.nan}',  BCOLTA='{np.nan}', BCOLTAERR='{np.nan}', \
                                        ASLCP='{np.nan}', ASLCPERR='{np.nan}',BSLCP='{np.nan}', BSLCPERR='{np.nan}'  WHERE FILENAME = '{FN}' ;"

                                if 'TSYS2' in ycol:
                                    stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', \
                                        AORTA='{np.nan}', AORTAERR='{np.nan}', ORFLAG=200, AORPC='{np.nan}', ACORTA='{np.nan}', ACORTAERR='{np.nan}', \
                                        ASRTA='{np.nan}', ASRTAERR='{np.nan}', SRFLAG=200, ANRTA='{np.nan}', ANRTAERR='{np.nan}', \
                                        BSRTA='{np.nan}', BSRTAERR='{np.nan}', NRFLAG=200, BNRTA='{np.nan}', BNRTAERR='{np.nan}', \
                                        BORTA='{np.nan}', BORTAERR='{np.nan}', BORFLAG=200, BORPC='{np.nan}', BCORTA='{np.nan}', BCORTAERR='{np.nan}', \
                                        ASRCP='{np.nan}', ASRCPERR='{np.nan}', BSRCP='{np.nan}', BSRCPERR='{np.nan}'  WHERE FILENAME = '{FN}' ;"

                            elif "ASLCP" in ycol:
                                s=[bslcp,asrcp,bsrcp]
                                er=[bslcperr,asrcperr,bsrcperr]
                                ss=[]
                                se=[]
                                       
                                for i in range(len(s)):
                                    if "nan" in str(s[i]):
                                        pass
                                    else:
                                        ss.append(s[i])
                                        se.append(er[i])
                                                
                                stot = (sum(ss))/len(ss)
                                stoterr=(1/len(se))*np.sqrt(sum([w**2 for w in se]))

                                stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ASLCPERR='{np.nan}',  OLFLAG=200, \
                                    STOT={stot},  STOTERR={stoterr} \
                                    WHERE FILENAME = '{FN}' ;"

                            elif "BSLCP" in ycol:
                                s=[aslcp,asrcp,bsrcp]
                                er=[aslcperr,asrcperr,bsrcperr]
                                ss=[]
                                se=[]
                                       
                                for i in range(len(s)):
                                    if "nan" in str(s[i]):
                                        pass
                                    else:
                                        ss.append(s[i])
                                        se.append(er[i])
                                                
                                stot = (sum(ss))/len(ss)
                                stoterr=(1/len(se))*np.sqrt(sum([w**2 for w in se]))

                                stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', BSLCPERR='{np.nan}',  OLFLAG=200, \
                                    STOT={stot},  STOTERR={stoterr} \
                                    WHERE FILENAME = '{FN}' ;"

                            elif "ASRCP" in ycol:
                                s=[bslcp,asrcp,bsrcp]
                                er=[bslcperr,asrcperr,bsrcperr]
                                ss=[]
                                se=[]
                                       
                                for i in range(len(s)):
                                    if "nan" in str(s[i]):
                                        pass
                                    else:
                                        ss.append(s[i])
                                        se.append(er[i])
                                                
                                stot = (sum(ss))/len(ss)
                                stoterr=(1/len(se))*np.sqrt(sum([w**2 for w in se]))

                                stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ASRCPERR='{np.nan}',  ORFLAG=200, \
                                    STOT={stot},  STOTERR={stoterr} \
                                    WHERE FILENAME = '{FN}' ;"

                            elif "BSRCP" in ycol:
                                s=[aslcp,asrcp,bsrcp]
                                er=[aslcperr,asrcperr,bsrcperr]
                                ss=[]
                                se=[]
                                       
                                for i in range(len(s)):
                                    if "nan" in str(s[i]):
                                        pass
                                    else:
                                        ss.append(s[i])
                                        se.append(er[i])
                                                
                                stot = (sum(ss))/len(ss)
                                stoterr=(1/len(se))*np.sqrt(sum([w**2 for w in se]))

                                stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', BSRCPERR='{np.nan}',  ORFLAG=200, \
                                    STOT={stot},  STOTERR={stoterr} \
                                    WHERE FILENAME = '{FN}' ;"

                            elif "AOLTA" in ycol:
                                stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', AOLTAERR='{np.nan}',  OLFLAG=200, AOLPC='{np.nan}',  ACOLTA='{np.nan}', ACOLTAERR='{np.nan}', \
                                    ASLTA='{np.nan}', ASLTAERR='{np.nan}', SLFLAG=200, \
                                    ANLTA='{np.nan}', ANLTAERR='{np.nan}', NLFLAG=200 \
                                    WHERE FILENAME = '{FN}' ;"

                            elif "AORTA" in ycol:
                                stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', AORTAERR='{np.nan}', ORFLAG=200, AORPC='{np.nan}', ACORTA='{np.nan}', ACORTAERR='{np.nan}', \
                                    ASRTA='{np.nan}', ASRTAERR='{np.nan}', SRFLAG=200, \
                                    ANRTA='{np.nan}', ANRTAERR='{np.nan}', NRFLAG=200 \
                                    WHERE FILENAME = '{FN}' ;"

                            elif "BOLTA" in ycol:
                                stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', BOLTAERR='{np.nan}', OLFLAG=200, BOLPC='{np.nan}',  BCOLTA='{np.nan}', BCOLTAERR='{np.nan}', \
                                    BSLTA='{np.nan}', BSLTAERR='{np.nan}', SLFLAG=200, \
                                    BNLTA='{np.nan}', BNLTAERR='{np.nan}', NLFLAG=200 \
                                    WHERE FILENAME = '{FN}' ;"

                            elif "BORTA" in ycol:
                                stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', BORTAERR='{np.nan}', ORFLAG=200, BORPC='{np.nan}',  BCORTA='{np.nan}', BCORTAERR='{np.nan}', \
                                    BSRTA='{np.nan}', BSRTAERR='{np.nan}', SRFLAG=200, \
                                    BNRTA='{np.nan}', BNRTAERR='{np.nan}', NRFLAG=200 \
                                    WHERE FILENAME = '{FN}' ;"

                            elif "ASLTA" in ycol or "BSLTA" in ycol:

                                    if "ASLTA" in ycol:

                                        # recalculate tot flux
                                        hpnTa=self.df['ANLTA'].iloc[i]
                                        errHpnTa=self.df['ANLTAERR'].iloc[i]
                                        onTa=self.df['AOLTA'].iloc[i]
                                        errOnTa=self.df['AOLTAERR'].iloc[i]
                                        pss=self.df['ALCPPSS'].iloc[i]
                                        errpss=self.df['ALCPPSSERR'].iloc[i]

                                        pc,corrta,errta=cp.calc_pc(0, 0, 0, hpnTa, errHpnTa, onTa, errOnTa, self.df)

                                        slcp=corrta*pss
                                        slcperr=np.sqrt((corrta/errta)**2 + (pss/errpss)**2)*slcp

                                        s=[slcp,bslcp,asrcp,bsrcp]
                                        er=[slcperr,bslcperr,asrcperr,bsrcperr]
                                        ss=[]
                                        se=[]
                                       
                                        for i in range(len(s)):
                                            if "nan" in str(s[i]):
                                                pass
                                            else:
                                                ss.append(s[i])
                                                se.append(er[i])
                                                
                                        stot = (sum(ss))/len(ss)
                                        stoterr=(1/len(se))*np.sqrt(sum([w**2 for w in se]))

                                        print('updating dual ASLTA')

                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLFLAG=200, \
                                            ASLTA='{np.nan}', ASLTAERR='{np.nan}', \
                                            AOLPC={pc}, ACOLTA={corrta},ACOLTAERR={errta}, \
                                            ASLCP={slcp}, ASLCPERR={slcperr}, STOT={stot}, STOTERR={stoterr}  WHERE FILENAME = '{FN}' ;"

                                    elif "BSLTA" in ycol:
                                        # recalculate tot flux
                                        hpnTa=self.df['BNLTA'].iloc[i]
                                        errHpnTa=self.df['BNLTAERR'].iloc[i]
                                        onTa=self.df['BOLTA'].iloc[i]
                                        errOnTa=self.df['BOLTAERR'].iloc[i]
                                        pss=self.df['BLCPPSS'].iloc[i]
                                        errpss=self.df['BLCPPSSERR'].iloc[i]

                                        pc,corrta,errta=cp.calc_pc(0, 0, 0, hpnTa, errHpnTa, onTa, errOnTa, self.df)

                                        slcp=corrta*pss
                                        slcperr=np.sqrt((corrta/errta)**2 + (pss/errpss)**2)*slcp

                                        s=[aslcp,slcp,asrcp,bsrcp]
                                        er=[aslcperr,slcperr,asrcperr,bsrcperr]
                                        ss=[]
                                        se=[]
                                       
                                        for i in range(len(s)):
                                            if "nan" in str(s[i]):
                                                pass
                                            else:
                                                ss.append(s[i])
                                                se.append(er[i])
                                                
                                        stot = (sum(ss))/len(ss)
                                        stoterr=(1/len(se))*np.sqrt(sum([w**2 for w in se]))

                                        print('updating dual ASLTA')

                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLFLAG=200, \
                                            BSLTA='{np.nan}', BSLTAERR='{np.nan}', \
                                            BOLPC={pc}, BCOLTA={corrta},BCOLTAERR={errta}, \
                                            BSLCP={slcp}, BSLCPERR={slcperr}, STOT={stot}, STOTERR={stoterr}  WHERE FILENAME = '{FN}' ;"

                            elif "ANLTA" in ycol or "BNLTA" in ycol:
                                    
                                    if "ANLTA" in ycol:
                                        # recalculate tot flux
                                        hpsTa=self.df['ASLTA'].iloc[i]
                                        errHpsTa=self.df['ASLTAERR'].iloc[i]
                                        onTa=self.df['AOLTA'].iloc[i]
                                        errOnTa=self.df['AOLTAERR'].iloc[i]
                                        pss=self.df['ALCPPSS'].iloc[i]
                                        errpss=self.df['ALCPPSSERR'].iloc[i]

                                        pc,corrta,errta=cp.calc_pc(0, hpsTa, errHpsTa, 0, 0, onTa, errOnTa, self.df)

                                        slcp=corrta*pss
                                        slcperr=np.sqrt((corrta/errta)**2 + (pss/errpss)**2)*slcp

                                        s=[slcp,bslcp,asrcp,bsrcp]
                                        er=[slcperr,bslcperr,asrcperr,bsrcperr]
                                        ss=[]
                                        se=[]
                                       
                                        for i in range(len(s)):
                                            if "nan" in str(s[i]):
                                                pass
                                            else:
                                                ss.append(s[i])
                                                se.append(er[i])
                                                
                                        stot = (sum(ss))/len(ss)
                                        stoterr=(1/len(se))*np.sqrt(sum([w**2 for w in se]))

                                        print('updating dual ANLTA')

                                        stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLFLAG=200, \
                                            ANLTA='{np.nan}', ANLTAERR='{np.nan}', \
                                            AOLPC={pc}, ACOLTA={corrta},ACOLTAERR={errta}, \
                                            ASLCP={slcp}, ASLCPERR={slcperr}, STOT={stot}, STOTERR={stoterr}  WHERE FILENAME = '{FN}' ;"
                                    
                                    # elif "BNLTA" in ycol:
                                    #     onta=self.df['BOLTA'].iloc[i]
                                    #     ontaerr=self.df['BOLTAERR'].iloc[i]
                                    #     sta=self.df['BSLTA'].iloc[i]
                                    #     staerr=self.df['BSLTAERR'].iloc[i]

                                    #     print('updating dual BNLTA')
                                    #     pc,ota,otaerr= cp.calc_pc(0,sta,staerr, 0.0,0.0,onta,ontaerr,self.df)
                                    #     stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLFLAG=200, BOLPC={pc}, BCOLTA={ota},BCOLTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"

                                    # print(stmt)

                            # elif "AOLTA" in ycol or "BOLTA" in ycol:
                                    
                            #         if "AOLTA" in ycol:

                            #             print('updating dual AOLTA')
                            #             pc,ota,otaerr = np.nan,np.nan,np.nan
                            #             stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLFLAG=200, AOLPC={pc}, ACOLTA={ota},ACOLTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"

                            #         elif "BOLTA" in ycol:

                            #             print('updating dual BOLTA')
                            #             pc,ota,otaerr=np.nan,np.nan,np.nan
                            #             stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', OLFLAG=200, BOLPC={pc}, BCOLTA={ota},BCOLTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"

                            #         print(stmt)

                            # elif "ASRTA" in ycol or "BSRTA" in ycol:
                                    
                            #         if "ASRTA" in ycol:
                            #             onta=self.df['AORTA'].iloc[i]
                            #             ontaerr=self.df['AORTAERR'].iloc[i]
                            #             nta=self.df['ANRTA'].iloc[i]
                            #             ntaerr=self.df['ANRTAERR'].iloc[i]

                            #             print('updating dual ASRTA')
                            #             pc,ota,otaerr = cp.calc_pc(0,0.0,0.0, nta, ntaerr, onta, ontaerr,self.df)
                            #             stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORFLAG=200,  AORPC={pc},ACORTA={ota},ACORTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"

                            #         elif "BSRTA" in ycol:
                            #             onta=self.df['BORTA'].iloc[i]
                            #             ontaerr=self.df['BORTAERR'].iloc[i]
                            #             nta=self.df['BNRTA'].iloc[i]
                            #             ntaerr=self.df['BNRTAERR'].iloc[i]

                            #             print('updating dual BSRTA')
                            #             pc,ota,otaerr = cp.calc_pc(0,0.0,0.0, nta,ntaerr,onta,ontaerr,self.df)
                            #             stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORFLAG=200, BORPC={pc}, BCORTA={ota},BCORTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"

                            #         print(stmt)

                            # elif "ANRTA" in ycol or "BNRTA" in ycol:
                                    
                            #         if "ANRTA" in ycol:
                            #             onta=self.df['AORTA'].iloc[i]
                            #             ontaerr=self.df['AORTAERR'].iloc[i]
                            #             sta=self.df['ASRTA'].iloc[i]
                            #             staerr=self.df['ASRTAERR'].iloc[i]

                            #             print('updating dual ANRTA')
                            #             pc,ota,otaerr = cp.calc_pc(0,sta,staerr, 0.0,0.0,onta,ontaerr,self.df)
                            #             stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORFLAG=200, AORPC={pc},ACORTA={ota},ACORTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"

                            #         elif "BNRTA" in ycol:
                            #             onta=self.df['BORTA'].iloc[i]
                            #             ontaerr=self.df['BORTAERR'].iloc[i]
                            #             sta=self.df['BSRTA'].iloc[i]
                            #             staerr=self.df['BSRTAERR'].iloc[i]

                            #             print('updating dual BNRTA')
                            #             pc,ota,otaerr = cp.calc_pc(0,sta,staerr, 0.0,0.0,onta,ontaerr,self.df)
                            #             stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORFLAG=200, BORPC={pc}, BCORTA={ota},BCORTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"

                            #         print(stmt)

                            # elif "AORTA" in ycol or "BORTA" in ycol:
                                    
                            #         if "AORTA" in ycol:

                            #             print('updating dual AORTA')
                            #             pc,ota,otaerr = np.nan, np.nan, np.nan
                            #             stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORFLAG=200,  AORPC={pc}, ACORTA={ota},ACORTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"

                            #         elif "BORTA" in ycol:

                            #             print('updating dual BORTA')
                            #             pc,ota,otaerr =np.nan, np.nan, np.nan
                            #             stmt = f"UPDATE {tablename} SET {ycol}='{np.nan}', ORFLAG=200,  BORPC={pc}, BCORTA={ota},BCORTAERR={otaerr}  WHERE FILENAME = '{FN}' ;"

                            #         

                            print(stmt)
                            db.c.execute(stmt)
                            db.commit_changes()
                            db.close_db()
                            print("updated CALDB")
                            print(tablename,xcol,ycol)
                    
                            # complete the code here
                            # for the rest of them.

                    print('After deleting: ',len(self.df))
                    print(self.df.iloc[i][yCol])
                    self.Canvas.clear_figure()
                    self.plot_cols_df()

    def reset_timeseries(self):

        self.df=self.orig_df

        # plot
        self.Canvas.clear_figure()

        self.plot_cols()
        
    def refresh_db(self):
        """refresh the database entries. Check for updates."""
        
        # open the database and get tables
        self.db = SQLiteDB(dbPath=self.dbFile, log=self.log)
        self.db.create_db()
        # self.db.close_db()

        # populate columns
        self.dbName=self.dbFile.split('/')[-1]
        self.tables=self.db.get_table_names(self.dbName)
        self.populate_cols()

        # update plot
        self.plot_cols()
        self.db.close_db()

    def save_time_db(self,filen=""):
        """Save the analysis results of the time series to a csv file"""
        
        if filen:
            self.df.to_csv(f"Analysis_of_table_{filen}.csv")
            print(f'saved results to {filen}.csv')
        else:
            self.df.to_csv("Analysis_results.csv")
            print('saved results to Analysis_results.csv')
        
    def plot_cols_df(self):
        """ Plot database columns. """

        # get col names
        xCol = self.time_ui.comboBoxColsX.currentText()
        yCol = self.time_ui.comboBoxColsY.currentText()

        if xCol == yCol:
            print("\nYou cannot plot the same column on X and Y\n")
        else:
            yErr = self.time_ui.comboBoxColsYerr.currentText()

            print(f"\nPlotting {xCol} vs {yCol} in table {self.table}\n")

            self.df[yCol]=self.df[yCol]#.apply(self.f)
            try:
                self.df[yErr]=self.df[yErr]#.apply(self.f)
                self.Canvas.plot_fig(self.df[xCol],self.df[yCol],xCol,yCol,data=self.df,yerr=self.df[yErr]) #,title=f"Plot of {self.df['SOURCEDIR']} obs. {self.df['FILENAME'][:8]}")#,data=self.)
            except:
                self.Canvas.plot_fig(self.df[xCol],self.df[yCol],xCol,yCol,data=self.df)#,title=f"Plot of {self.df['SOURCEDIR']} obs. {self.df['FILENAME'][:8]}")#,data=self.)

            self.Canvas.draw()
            
    


    # checked end ----------
    # -----------------------------

    # == Widget connections
    def connect_buttons(self):
        """ Connect button key presses to widgets. """

        msg_wrapper("debug", self.log.debug,"Connecting buttons to main canvas")

        # Plot parameters buttons
        self.drift_ui.BtnFilterData.clicked.connect(self.filter_data)
        self.drift_ui.BtnViewFit.clicked.connect(self.view_fit)

        # PSS values buttons
        self.drift_ui.BtnCalc.setEnabled(False)
        self.drift_ui.BtnCalc.setText("Calc PSS/Flux")
        # self.drift_ui.BtnCalc.clicked.connect(self.calc)
        # self.drift_ui.BtnPopulatePSS.clicked.connect(self.populate_pss_from_file)

        # beam fitting buttons
        self.drift_ui.BtnFitData.clicked.connect(self.fit_data)
        self.drift_ui.BtnClearSelection.clicked.connect(self.clear_selection)
        self.drift_ui.BtnSave.clicked.connect(self.save_fit)

        # Current plot selection
        self.drift_ui.BtnChoosePlot.clicked.connect(self.choose_plot)
        self.drift_ui.BtnOpenFile.clicked.connect(self.open_file)
        self.drift_ui.BtnResetPlot.clicked.connect(self.reset_plot)
        self.popup_msg_dict()
        self.drift_ui.BtnSaveToDb.clicked.connect(self.save_to_DB)

        # Current fit status buttons
        self.drift_ui.BtnResetStatus.clicked.connect(self.reset_status)
        self.drift_ui.BtnViewStatus.clicked.connect(self.view_status)

    
    
    
    


    
    
    

    def update_plot(self, x, y, title, res, label="", label2=""):
        """ Update the current figure. """

        msg_wrapper("debug", self.log.debug,
                    "Update the current figure.")

        self.Canvas.plot_figure(
            x, y, title, label)
        self.Canvas.plot_residual(res, label=label2)
    
    
    # === connections for fit_data() ===
    def get_fit_type(self):
        """ Get fit type from combobox."""

        msg_wrapper("debug", self.log.debug, "Get fit type")
        return self.drift_ui.ComboBoxFitType.currentText()
    
    def get_fit_order(self):
        """ Get order for fitting polynomial."""
        
        msg_wrapper("debug", self.log.debug, "Get polynomial order")
        return int(self.drift_ui.ComboBoxFitOrder.currentText())
    
    def get_fit_loc(self):
        """ Get fit location from combobox. """

        msg_wrapper("debug", self.log.debug, "Get fit location")
        return self.drift_ui.ComboBoxFitLoc.currentText()

    def clear_selection(self):
        """ Clear selections made for current scan. """

        self.write("Clearing selections for current scan.",'info')

        # Get the plot index
        plotIndex = self.get_plot_index()

        # Set plot title
        title = self.set_title()
        
        self.Canvas.plot_figure(self.x, self.y, title, "Cleared selection")
        self.Canvas.plot_residual()
        self.set_fit_parmeters()
        self.set_flags()
    
    

    
    def fit_data(self):
        """ Fit the drift scan. """

        # Open plot manager
        plotIndex = self.get_plot_index()

        # Get order to fit
        order = self.get_fit_order()
        fit_type = self.get_fit_type()

        if fit_type == "Polynomial":

            # Get location we are fitting
            fit_loc = self.get_fit_loc()

            # Check the selected fit type
            if fit_loc == "Base":

                # Get base locations
                if len(self.Canvas.click_index) == 0:
                    self.write("No points selected yet",'info')
                    self.clear_selection()

                else:
                    self.write("Fitting the baseline",'info')

                    # ensure we have a minimum of 4 points for the base fit
                    if len(self.Canvas.click_index) < 4 or len(self.Canvas.click_index) % 2 != 0:
                        self.write("Need a minimum of 4 points or an even set to fit a baseline.\nClicked points reset, pick new points",'info')
                        self.clear_selection()
                        self.write(f"selected points: {self.Canvas.click_index}",'info')
                        self.Canvas.click_index = []

                    else:

                        # prep Canvas and perform fit
                        self.Canvas.clear_canvas()        # Update figures

                        # Perform baseline fit
                        self.write("Fitting "+fit_loc+" with order "+str(order)+" "+fit_type,'info')
                        self.reset_peak(plotIndex)
                        self.fit_base(order, plotIndex)
                        self.update_base_fit(plotIndex)    # Update plot
                        self.peak_is_fit = 0
                        
            elif fit_loc == "Peak":

                    self.write("Fitting peak with poly",'info')

                    # Get base locations
                    if len(self.Canvas.click_index) == 0:
                        self.write("No points selected yet. ","info")
                        self.peak_is_fit = 0
                        self.clear_selection()

                    else:
                        # ensure we have a minimum of 2 points for the peak fit
                        if len(self.Canvas.click_index) < 2 or len(self.Canvas.click_index) % 2 != 0:
                            self.write("Need a minimum of 2 points or an even set to fit a peak.\nClicked points reset, pick new points",'info')

                            self.peak_is_fit = 0
                            self.Canvas.click_index = []
                            self.clear_selection()

                        else:

                            # Perform peak fit
                            self.write("Fitting "+fit_loc+" with order "+str(order)+" "+fit_type, 'info')

                            #CHECK IF DUAL BEAM
                            print(self.dataKeys)
                            # sys.exit()
                            if self.data['INSTRUME'] == "Dicke Switched":
                                
                                # Update figures
                                self.Canvas.clear_dual_canvas()
                                self.fit_dual_peak(order, plotIndex)
                                self.update_dual_peak_fit(plotIndex)  
                            else:
                                # Update figures
                                self.Canvas.clear_canvas()
                                self.fit_peak(order, plotIndex)
                                self.update_peak_fit(plotIndex)    # Update plot
                            
                            self.peak_is_fit = 1
                            #self.view_fit()
                            self.Canvas.click_index = []
                            #self.clear_selection()

        '''elif fit_type == "Gaussian":

            msg_wrapper("info", self.log.info,
                        "Fitting peak with gaussian\n")

            # Get base locations
            if len(self.Canvas.click_index) == 0:
                msg_wrapper("info", self.log.info,
                            "No points selected yet. ")
               
                self.peak_is_fit = 0

            else:

                # ensure we have a minimum of 2 points for the peak fit
                if len(self.Canvas.click_index) < 2 or len(self.Canvas.click_index) % 2 != 0:
                    msg_wrapper("info", self.log.info,
                    "We need a minimum of 2 points or an even set to fit a baseline")
                    msg_wrapper("info", self.log.info,
                                "Clicked points reset, pick new points")
               
                    self.peak_is_fit = 0
                    self.Canvas.click_index = []

                else:

                    # Perform baseline fit
                    
                    self.fit_peak(order, plotIndex)

                    # Update figures
                    self.Canvas.clear_canvas()
                    self.update_peak_fit(plotIndex)    # Update plot
                    self.peak_is_fit = 1
                    self.view_fit()
                    self.Canvas.click_index = []
        '''

    def update_dual_peak_fit(self, plotIndex):
        """
        Updates figure on Canvas
        """

        self.write("Update peak fit",'info')

        plotTitle = self.set_title()

        self.drift_ui.ComboBoxFitOrder.currentText()

        self.Canvas.plot_dual_residuals(self.peakResA, self.peakResB,label="Peak residual")

        if len(self.xpA) == 0 and len(self.xpB) != 0:
            self.Canvas.plot_dual_peaks([], [], 
                0.0, 0.0, self.xpB, self.peakModelB, 
                self.peakFitB, self.peakRmsB, self.x, self.y, plotTitle)

        elif len(self.xpA) != 0 and len(self.xpB) == 0:
            self.Canvas.plot_dual_peaks(self.xpA, self.peakModelA,
                                        self.peakFitA, self.peakRmsA, [], [],
                                        0.0, 0.0, self.x, self.y, plotTitle)

        elif len(self.xpA) != 0 and len(self.xpB) != 0:
            self.Canvas.plot_dual_peaks(self.xpA, self.peakModelA, 
                self.peakFitA, self.peakRmsA, self.xpB, self.peakModelB, 
                self.peakFitB, self.peakRmsB, self.x, self.y, plotTitle)

    def update_peak_fit(self, plotIndex):
        """
        Updates figure on Canvas
        """

        self.write("Update peak fit ",'info')

        plotTitle = self.set_title()

        self.drift_ui.ComboBoxFitOrder.currentText()

        self.Canvas.plot_residual(self.peakRes, label="Peak residual")
        self.Canvas.plot_peak(self.xp, self.peakModel, self.peakFit,
                              self.peakRms, self.x, self.y,  plotTitle)

    def fit_base(self, order, plotIndex):
        """ Fit the baseline. """

        self.write("Fitting baseline @ "+str(self.Canvas.click_index))
        self.write("Fit points: "+str(self.x[self.Canvas.click_index]))

        # Create tags for the plot file
        self.tag = self.create_tag(plotIndex)

        # Get baseline fitting locations
        self.xb, self.yb = fit.get_base_pts(
            self.x, self.y, self.Canvas.click_index)

        # Fit the baseline
        self.dataModel, self.driftModel, self.driftRes, self.base_rms, self.driftCoeffs = fit.correct_drift(
            self.xb, self.yb, self.x, self.log,order)

        # Set the slope,rms,x and y values
        self.baseSlope = self.driftCoeffs[0]
        self.write(
            "y = {:.3f}x + {:.3f}".format(self.baseSlope, self.driftCoeffs[1]))

        self.y = np.array(self.y - self.dataModel)
        self.x = np.array(self.x)

        # update fit parameter
        self.base_is_fit = 1

    def create_tag(self, ind):
        """ Create a tag for the plots according to the current scan being processed. e.g. ONRCP
        """

        msg_wrapper("debug", self.log.debug, "Setting up naming tags")
        #print(f'index: {ind}')
        if int(ind) > 2:
            tag = self._set_file_tag_nb()
        else:
            tag = self._set_file_tag_wb()

        return tag

    def _set_file_tag_wb(self):
        """
            A naming tag for wide beam data.
        """

        msg_wrapper("debug", self.log.debug, "Setting tag for wide beam data")

        plotIndex = self.get_plot_index()
        tagId = int(plotIndex)

        if tagId == 0:
            self.write("Processing: ONLCP\n")
            return "ON_LCP"
        else:
            self.write("rocessing: ONRCP\n")
            return "ON_RCP"
        
    def update_base_fit(self, plotIndex):
        """ Updates figure on Canvas """

        # Update plot
        self.write("Figure updated with fit")

        plotTitle = self.set_title()
        pi = self.Canvas.click_index
        self.update_plot(self.x, self.y, plotTitle, self.driftRes,
                         "Data: baseline corrected", label2="")
        pi = []

    def fit_peak(self, order, plotIndex):
        """ Fit peak """

        self.write("Fitting the Peak","info")
      
        self.xp, self.yp = fit.get_base_pts(
            self.x, self.y, self.Canvas.click_index)
        self.write("locs: "+str(self.x[self.Canvas.click_index]),'info')


        if self.drift_ui.ComboBoxFitType.currentText() == "Polynomial":

            # poly fit
            self.write("Fitting a polynomial",'info')

            degree = int(self.drift_ui.ComboBoxFitOrder.currentText())

            peak_res, peakRms, peakModel  = fit.fit_poly_peak(
                self.xp, self.yp, order=degree, log=self.log)  # Fit the peak

            peakLoc = self.xp[((np.where(peakModel == max(peakModel))[0])[0])]

            self.peakFit = max(peakModel)
            self.peakRms = peakRms
            self.peakRes = peak_res
            self.peakModel = peakModel 
            self.peakLoc = peakLoc

            # Calculate s2n
            try:
                # calculate s2n using drift residual
                self.s2n = misc.sig_to_noise(self.peakFit, self.driftRes,self.log)
            except Exception:
                # else calculate s2n using peak fit residual
                # if base is not corrected first
                self.s2n = misc.sig_to_noise(self.peakFit, self.peakRes,self.log)

        '''elif self.drift_ui.ComboBoxFitType.currentText() == "Gaussian":

            # gauss fit
            msg_wrapper("info", self.log.info,
                        "Fitting a gaussian")

            p0 = [max(self.yp), self.xp[np.argmax(self.yp)],
                  self.data["HPBW"]/2]
            gaus_coeff, var_matrix, gauss_fit, err_gauss_fit, res = fit.fit_gauss(self.xp, self.yp, p0)  # Fit the peak

            peakLoc = self.x[((np.where(peakModel == max(peakModel))[0])[0])]

            self.peakFit = max(gauss_fit)
            self.peakRms = err_gauss_fit
            self.peakRes = res
            self.peakModel = gauss_fit
            self.peakLoc = peakLoc

            # Calculate s2n
            try:
                # calculate s2n using drift residual
                self.s2n = fit.sig_to_noise(self.peakFit, self.driftRes)
            except Exception:
                # else calculate s2n using peak fit residual
                # if base is not corrected first
                self.s2n = fit.sig_to_noise(self.peakFit, self.peakRes)

         '''

        # Calculate PSS
        self.update_fit_parmeters()
        self.write("Ta = {:.3f} +- {:.3f} [K]".format(self.peakFit, self.peakRms),'info')

    def fit_dual_peak(self, order, plotIndex):
        """ Fit dual peaks. """

        self.write("Fitting the Peaks",'info')

        # get values of both peak click indeces
        p1ClickIndex, p2ClickIndex = [], []
        scan_mid=int(len(self.x)/2)
        [p1ClickIndex.append(n) for n in self.Canvas.click_index if n <= scan_mid]
        [p2ClickIndex.append(n) for n in self.Canvas.click_index if n > scan_mid]

        # fit the peaks
        if len(p1ClickIndex) !=0 and len(p2ClickIndex) !=0:
            self.fit_p1(p1ClickIndex)
            self.fit_p2(p2ClickIndex)

        if len(p1ClickIndex) !=0 and len(p2ClickIndex) ==0: 
            self.fit_p1(p1ClickIndex)
            self.fit_p2([])

        if len(p1ClickIndex) ==0 and len(p2ClickIndex) !=0:
            self.fit_p1([])
            self.fit_p2(p2ClickIndex)


        # Calculate PSS
        self.update_fit_parmeters()

    def fit_p1(self,locs):
        """ Fitting peak 1. """

        # Fit peak with selected points
        if len(locs) == 0:
            # no data, skip fit
            self.write("Peak 1 not fit",'info')
            self.peakFitA = np.nan
            self.peakRmsA = np.nan
            self.peakResA = np.nan
            self.peakModelA = np.nan
            self.peakLocA = np.nan
            self.s2nA = np.nan
            self.xpA = []
            self.ypA = []

        else:
            if len(locs) % 2 != 0:
                self.write("Need a minimum of 2 points or an even set on peakA in order to fit the peak.\nClicked points reset, pick new points",'info')

                self.peak_is_fit = 0
                self.Canvas.click_index = []
                self.clear_selection()
            else:
                self.xpA, self.ypA = fit.get_base_pts(
                    self.x, self.y, locs)
                self.write("locs: "+str(self.x[locs]),'info')
        
                if self.drift_ui.ComboBoxFitType.currentText() == "Polynomial":

                    # poly fit
                    self.write("Fitting a polynomial",'info')

                    degree = int(self.drift_ui.ComboBoxFitOrder.currentText())

                    peak_resA, peakRmsA, peakModelA = fit.fit_poly_peak(
                        self.xpA, self.ypA, order=degree, log=self.log)  # Fit the peak

                    peakLocA = self.x[((np.where(peakModelA == min(peakModelA))[0])[0])]

                    self.peakFitA = min(peakModelA)
                    self.peakRmsA = peakRmsA
                    self.peakResA = peak_resA
                    self.peakModelA = peakModelA
                    self.peakLocA = peakLocA

                    # Calculate s2n
                    try:
                        # calculate s2n using drift residual
                        self.s2nA = fit.sig_to_noise(
                            self.peakFitA, self.driftResA, self.log)
                    except Exception:
                        # else calculate s2n using peak fit residual
                        # if base is not corrected first
                        self.s2nA = fit.sig_to_noise(
                        self.peakFitA, self.peakResA, self.log)

    def fit_p2(self, locs):
        """ Fitting peak 2. """

        if len(locs) == 0:
            # no data, skip fit
            self.write("Peak 2 not fit",'info')
            self.peakFitB = np.nan
            self.peakRmsB = np.nan
            self.peakResB = np.nan
            self.peakModelB = np.nan
            self.peakLocB = np.nan
            self.s2nB = np.nan
            self.xpB = []
            self.ypB = []

        else:
            # Fit peak with selected points
            if len(locs) % 2 != 0:
                self.write(
                    "Need a minimum of 2 points or an even set on peakA in order to fit the peak.\nClicked points reset, pick new points",'info')

                self.peak_is_fit = 0
                self.Canvas.click_index = []
                self.clear_selection()
            else:
                self.xpB, self.ypB = fit.get_base_pts(
                    self.x, self.y, locs)
                self.write("locs: "+str(self.x[locs]),'info')

                if self.drift_ui.ComboBoxFitType.currentText() == "Polynomial":

                    # poly fit
                    self.write("Fitting a polynomial",'info')

                    degree = int(self.drift_ui.ComboBoxFitOrder.currentText())

                    peak_resB, peakRmsB, peakModelB = fit.fit_poly_peak(
                        self.xpB, self.ypB, order=degree, log=self.log)  # Fit the peak

                    peakLocB = self.x[(
                        (np.where(peakModelB == max(peakModelB))[0])[0])]

                    self.peakFitB = max(peakModelB)
                    self.peakRmsB = peakRmsB
                    self.peakResB = peak_resB
                    self.peakModelB = peakModelB
                    self.peakLocB = peakLocB

                    # Calculate s2n
                    try:
                        # calculate s2n using drift residual
                        self.s2nB = fit.sig_to_noise(
                            self.peakFitB, self.driftResB, self.log)
                    except Exception:
                        # else calculate s2n using peak fit residual
                        # if base is not corrected first
                        self.s2nB = fit.sig_to_noise(
                            self.peakFitB, self.peakResB, self.log)

    def update_fit_parmeters(self):
        """ Update fit parameters. """

        msg_wrapper("debug", self.log.debug, "Update fit parameters.")

        plotIndex = self.get_plot_index()

        if len(self.scans) == 2:

            if "13.0S" in self.data["FRONTEND"]:
                if self.scans[plotIndex] == "ONLCP":
                    data_update = ["OLTA", "OLTAERR", "OLS2N",
                                   "OLRMSB", "OLRMSA", "OLBSLOPE", "OLBSRMS", "OLTAPEAKLOC", "OLAPPEFF", "OLPSS", "OLDPSS"]
                    self.set_data(data_update)

                else:
                    data_update = ["ORTA", "ORTAERR", "ORS2N",
                                   "ORRMSB", "ORRMSA", "ORBSLOPE", "ORBSRMS", "ORTAPEAKLOC", "ORAPPEFF", "ORPSS", "ORDPSS"]
                    self.set_data(data_update)
            else:
                pass
        else:
            if "S" in self.data["FRONTEND"]:

                print(self.scans)
                print(self.scanKeys)
                # sys.exit()
                if self.scanKeys[plotIndex] == "HPSLCP":
                    data_update = ["SLTA", "SLTAERR", "SLS2N",
                                   "SLRMSB", "SLRMSA", "SLBSLOPE", "SLBSRMS", "SLTAPEAKLOC"]
                    self.set_nb_data(data_update)

                elif self.scanKeys[plotIndex] == "HPNLCP":
                    data_update = ["NLTA", "NLTAERR", "NLS2N",
                                   "NLRMSB", "NLRMSA", "NLBSLOPE", "NLBSRMS", "NLTAPEAKLOC"]
                    self.set_nb_data(data_update)

                elif self.scanKeys[plotIndex] == "ONLCP":
                    data_update = ["OLTA", "OLTAERR", "OLS2N",
                                   "OLRMSB", "OLRMSA", "OLBSLOPE", "OLBSRMS", "OLTAPEAKLOC"]

                    self.set_nb_data(data_update)
                    # if self.data["OBJECTTYPE"] == "CAL":
                    #     self.calc_pss_()
                    # else:
                    #     pass

                elif self.scanKeys[plotIndex] == "HPSRCP":
                    data_update = ["SRTA", "SRTAERR", "SRS2N",
                                   "SRRMSB", "SRRMSA", "SRBSLOPE", "SRBSRMS", "SRTAPEAKLOC"]
                    self.set_nb_data(data_update)

                elif self.scanKeys[plotIndex] == "HPNRCP":
                    data_update = ["NRTA", "NRTAERR", "NRS2N",
                                   "NRRMSB", "NRRMSA", "NRBSLOPE", "NRBSRMS", "NRTAPEAKLOC"]
                    self.set_nb_data(data_update)

                else:
                    data_update = ["ORTA", "ORTAERR", "ORS2N",
                                   "ORRMSB", "ORRMSA", "ORBSLOPE", "ORBSRMS", "ORTAPEAKLOC"]
                    self.set_nb_data(data_update)
                    # if self.data["OBJECTTYPE"] == "CAL":
                    #     self.calc_pss_()
                    # else:
                    #     pass

            if "D" in self.data["FRONTEND"]:
                

                if self.scanKeys[plotIndex] == "HPSLCP":
                    data_update = ["ASLTA", "ASLTAERR", "ASLS2N","ASLTAPEAKLOC", "BSLTA", "BSLTAERR", "BSLS2N","BSLTAPEAKLOC",
                                   "SLRMSB", "SLRMSA", "SLBSLOPE", "SLBSRMS"]
                    self.set_dual_data(data_update)

                elif self.scanKeys[plotIndex] == "HPNLCP":
                    data_update = ["ANLTA", "ANLTAERR", "ANLS2N", "ANLTAPEAKLOC", "BNLTA", "BNLTAERR", "BNLS2N", "BNLTAPEAKLOC",
                                   "NLRMSB", "NLRMSA", "NLBSLOPE", "NLBSRMS"]
                    self.set_dual_data(data_update)

                elif self.scanKeys[plotIndex] == "ONLCP":

                    data_update = ["AOLTA", "AOLTAERR", "AOLS2N","AOLTAPEAKLOC", "BOLTA", "BOLTAERR", "BOLS2N","BOLTAPEAKLOC", 
                                   "OLRMSB", "OLRMSA", "OLBSLOPE", "OLBSRMS"]

                    self.set_dual_data(data_update)

                    # if self.data["OBJECTTYPE"] == "CAL":
                    #     self.set_db_pss()
                    # else:
                    #     pass 

                elif self.scanKeys[plotIndex] == "HPSRCP":
                    data_update = ["ASRTA", "ASRTAERR", "ASRS2N", "ASRTAPEAKLOC", "BSRTA", "BSRTAERR", "BSRS2N", "BSRTAPEAKLOC",
                                   "SRRMSB", "SRRMSA", "SRBSLOPE", "SRBSRMS"]
                    self.set_dual_data(data_update)

                elif self.scanKeys[plotIndex] == "HPNRCP":
                    data_update = ["ANRTA", "ANRTAERR", "ANRS2N", "ANRTAPEAKLOC", "BNRTA", "BNRTAERR", "BNRS2N", "BNRTAPEAKLOC",
                                   "NRRMSB", "NRRMSA", "NRBSLOPE", "NRBSRMS"]
                    self.set_dual_data(data_update)

                else:
                    data_update = ["AORTA", "AORTAERR", "AORS2N", "AORTAPEAKLOC", "BORTA", "BORTAERR", "BORS2N", "BORTAPEAKLOC",
                                   "ORRMSB", "ORRMSA", "ORBSLOPE", "ORBSRMS"]

                    self.set_dual_data(data_update)

                    # if self.data["OBJECTTYPE"] == "CAL":
                    #     self.set_db_pss()
                    # else:
                    #     pass 

    def set_dual_data(self, data_update):
        """ Set the estimated values in the data dictionary.
        """

        try:
            self.data[data_update[0]] = self.peakFitA
        except:
            pass

        try:
            self.data[data_update[1]] = self.peakRmsA
        except:
            pass

        try:
            self.data[data_update[2]] = self.s2nA
        except:
            pass

        try:
            self.data[data_update[3]] = self.peakLocA
        except:
            pass

        try:
            self.data[data_update[4]] = self.peakFitB
        except:
            pass

        try:
            self.data[data_update[5]] = self.peakRmsB
        except:
            pass

        try:
            self.data[data_update[6]] = self.s2nB
        except:
            pass

        try:
            self.data[data_update[7]] = self.peakLocB
        except:
            pass

        try:
            self.data[data_update[8]] = self.rmsb
        except:
            pass

        try:
            self.data[data_update[9]] = self.rmsa
        except:
            pass

        try:
            self.data[data_update[10]] = self.baseSlope
        except:
            pass

        try:
            self.data[data_update[11]] = self.base_rms
        except:
            pass

    def set_nb_data(self, data_update):
        """ Set the estimated values in the data dictionary. """

        try:
            self.data[data_update[0]] = self.peakFit
        except:
            pass

        try:
            self.data[data_update[1]] = self.peakRms
        except:
            pass

        try:
            self.data[data_update[2]] = self.s2n
        except:
            pass

        try:
            self.data[data_update[3]] = self.rmsb
        except:
            pass

        try:
            self.data[data_update[4]] = self.rmsa
        except:
            pass

        try:
            self.data[data_update[5]] = self.baseSlope
        except:
            pass

        try:
            self.data[data_update[6]] = self.base_rms
        except:
            pass

        try:
            self.data[data_update[7]] = self.peakLoc
        except:
            pass

    def plot_new_fig(self):
        """
        Plot a new figure from the recently fit data.
        """

        self.write("plotting New Fig",'info')

        fig = self.Canvas.ax.get_figure()

        plot_tag = self.create_tag(len(self.plotBeamName))
        print(f'plot tag: {plot_tag}')
        fig_name = "plots/" + self.data["SOURCEDIR"] + \
            "/" + self.data["FILENAME"][:18] + "_" + plot_tag + ".png"

        self.file.create_folder("plots/" + self.data["SOURCEDIR"])
        fig.savefig(fig_name)

    

    
    

    def choose_plot(self):
        """ Select the plot to work with. """

        msg_wrapper("debug", self.log.debug, "Choose plot")

        self.fit_done = 0

        plotIndex = self.get_plot_index()

        self.reset_previous_fits(plotIndex)

        # Set default to base fit type
        if self.drift_ui.ComboBoxFitLoc.currentText() != "Base":
            self.drift_ui.ComboBoxFitLoc.setCurrentIndex(0)

        if len(self.scanKeys) == 2:

            # Clear the Canvas
            self.Canvas.clear_canvas()

            # Plot figure
            self.x = self.scanKeys["OFFSET"]
            scanName = self.scanKeys[plotIndex]
            self.y = self.scans[scanName]

            self.Canvas.plot_figure(self.x, self.y, label="data")
            self.Canvas.plot_residual()
            self.set_fit_parmeters()

        elif len(self.scanKeys) == 6:

            # Clear the Canvas
            self.Canvas.clear_canvas()

            # Plot figure
            self.write("Plotting: " +
                     self.drift_ui.ComboBoxPlotType.currentText(),'info')
            self.x = self.scans["OFFSET"]
            scanName = self.scanKeys[plotIndex]
            print(scanName.strip("_"), plotIndex, self.scans.keys())
            self.y = self.scans[scanName]

            self.Canvas.plot_figure(self.x, self.y,label="data")
            self.Canvas.plot_residual()
            self.set_fit_parmeters()

            if plotIndex == 0:
                # plot 1,2
                self.plotOnCanvas(self,1,2)

            elif plotIndex == 1:
                # plot 0,2
                self.plotOnCanvas(self,0,2)

            elif plotIndex == 2:
                # plot 0,1
                self.plotOnCanvas(self,0,1)

            elif plotIndex == 3:
                # plot 4,5
                self.plotOnCanvas(self,4,5)

            elif plotIndex == 4:
                # plot 3,5
                self.plotOnCanvas(self,3,5)

            elif plotIndex == 5:
                # plot 3,4
                self.plotOnCanvas(self,3,4)
    
        else:
            self.write("There are no scans provided. ",'info')

    

    def popup_msg_dict(self):
        """ Message dictionary for popups."""

        self.popup_msg = {
            "noBase": "Are you sure you want to save data without fitting the baseline ?",
            "noPeak": "Are you sure you want to save data without fitting the peak ?",
            "noFit": "Are you sure you want to save data without fitting the plot ?"
        }

    def save_fit(self):
        """
        Save the fit. If the data has been previously saved
        overwrite the previous fit.
        """

        # Update plot settings
        obj = self.data['OBJECTTYPE']
        beam = self.data['FRONTEND']

        plotIndex = self.get_plot_index()
        
        if "S" in beam:

            if self.base_is_fit == 0 and self.peak_is_fit == 0:

                
                # Set flag
                self.set_flags()

                # No fit done on figure
                reply = self.popUp(self.popup_msg["noFit"])
                if reply == "yes":
                    self.update_fit_parmeters()
                    self.plot_new_fig()
                    self.status[plotIndex] = 2
                else:
                    self.write("No fit done",'info')
                self.write("Saving fit> Fit status: %d%d%d" % (
                self.base_is_fit, self.peak_is_fit, self.plot_is_smoothed),"info")

            elif self.base_is_fit == 0 and self.peak_is_fit == 1:

                # Set flag
                self.set_flags(101)

                # Only peak fit done on figure
                reply = self.popUp(self.popup_msg["noBase"])
                if reply == "yes":
                    self.update_fit_parmeters()
                    self.plot_new_fig()
                    self.status[plotIndex] = 1
                else:
                    pass
                self.write("Saving fit> Fit status: %d%d%d" % (
                self.base_is_fit, self.peak_is_fit, self.plot_is_smoothed),"info")

            elif self.base_is_fit == 1 and self.peak_is_fit == 0:
                # Only base fit done on figure
                # Create a popup window to ask if user if sure about saving this

                # Set flag
                self.set_flags(110)
                print(self.data['OLFLAG'])
                reply = self.popUp(self.popup_msg["noPeak"])

                if reply == "yes":
                    self.update_fit_parmeters()
                    self.plot_new_fig()
                    self.status[plotIndex] =  0
                    #print(self.status, plotIndex)
                else:
                    pass
                self.write("Saving fit> Fit status: %d%d%d" % (
                self.base_is_fit, self.peak_is_fit, self.plot_is_smoothed),"info")

            elif self.base_is_fit == 1 and self.peak_is_fit == 1:
                # Both base and peak were fitted

                # Set flag
                self.set_flags(111)
                self.update_fit_parmeters()
                self.view_fit()
                self.plot_new_fig()
                self.status[plotIndex] = 1

                self.write("Saving fit> Fit status: %d%d%d" % (
                self.base_is_fit, self.peak_is_fit, self.plot_is_smoothed),"info")

        elif "D" in beam:
            # Save dual beam fits

            if self.base_is_fit == 0 and self.peak_is_fit == 0:

                # Set flag
                self.set_flags()

                # No fit done on figure
                reply = self.popUp(self.popup_msg["noFit"])
                if reply == "yes":
                    self.update_fit_parmeters()
                    self.plot_new_fig()
                    self.status[plotIndex] = 2
                else:
                    self.write("No fit done",'info')

            elif self.base_is_fit == 0 and self.peak_is_fit == 1:

                # Set flag
                self.set_flags(101)

                # Only peak fit done on figure
                reply = self.popUp(self.popup_msg["noBase"])
                if reply == "yes":
                    self.update_fit_parmeters()
                    self.plot_new_fig()
                    self.status[plotIndex] = 1
                else:
                    pass

            elif self.base_is_fit == 1 and self.peak_is_fit == 0:
                # Only base fit done on figure
                # Create a popup window to ask if user if sure about saving this

                # Set flag
                self.set_flags(110)
                reply = self.popUp(self.popup_msg["noPeak"])

                if reply == "yes":
                    self.update_fit_parmeters()
                    self.plot_new_fig()
                    self.status[plotIndex] = 0
                else:
                    pass

            elif self.base_is_fit == 1 and self.peak_is_fit == 1:
                # Both base and peak were fitted

                # Set flag
                self.set_flags(111)
                self.update_fit_parmeters()
                self.view_fit()
                self.plot_new_fig()
                self.status[plotIndex] = 1

        else:
            self.write("Cant' save data, basefit not done",'info')

        print(self.status)
        #sys.exit()

    def save_to_DB(self):
        """ Save fit to database. """

        self.write("Saving data to database.")

        plotIndex = self.get_plot_index()

        if self.data['OBJECTTYPE'] == 'CAL':

            # make a copy of the current working db
            analDb = "CALDB.db"
            
            # GET TABLE FROM DATABASE
            db = SQLiteDB(databaseName=analDb, log=self.log)
            db.create_db()
        else:
            # make a copy of the current working db
            analDb = "TARDB.db"
            db = SQLiteDB(databaseName=analDb, log=self.log)
            db.create_db()

        table = db.get_table_name(self.data['SOURCEDIR'])
        db.set_table_name(table)

        self.write("Updating table: {}\n".format(table),'info')

        # Check if file has been processed
        try:
            files = db.read_data_from_database("FILENAME")
        except Exception:
            db.create_table(self.data, table)
            files = []

        # File in DB
        # print("File in db: ", self.data['FILENAME'] in files, self.data['FILENAME'])

        if self.data['FILENAME'] in files:

            self.write("already processed: ".format(self.data['FILENAME']),'info')

            question = "Are you sure you want to overwrite the database entry for this source ?"
            result = self.popUp(question)

            if result == "yes":

                self.write("Status: "+ str(self.status),'info')
                #print(self.beamName)
                #sys.exit()
                      
                # Update db entry
                db.update_row_in_db(
                    table, self.data['FILENAME'], self.data, self.status, self.beamName)

                self.write('Updated row in table','info')

                # Save the figure
                self.plot_new_fig()

                if 1 in self.status or 2 in self.status:

                    # update corresponding plots
                    for i in range(len(self.beamName)):
                        x = self.x # Data
                        y = self.y#scans[i]

                        if str(self.status[i]) == '2' :
                            pl.plot(x, y, "r", label="raw data")
                            pl.suptitle(
                                "Plot "+self.data["FILENAME"][:18]+" of "+self.data["OBJECT"])
                            pl.title(
                                self.beamName[i]+" scan at "+str(self.data["CENTFREQ"])+" MHz", fontsize=10)
                            pl.xlabel("Scandist [deg]")
                            pl.ylabel("Ta [K]")
                            pl.legend(loc=2)
                            pl.savefig(
                                "plots/"+self.data["SOURCEDIR"]+"/"+self.data["FILENAME"][:18]+"_"+self.plotBeamName[i]+".png")
                            pl.close()
                            
                        elif str(self.status[i]) == '1' :
                            pl.plot(x, y, "C0", label="raw data")
                            pl.suptitle(
                                "Plot "+self.data["FILENAME"][:18]+" of "+self.data["OBJECT"])
                            pl.title(
                                self.beamName[i]+" scan at "+str(self.data["CENTFREQ"])+" MHz", fontsize=10)
                            pl.xlabel("Scandist [deg]")
                            pl.ylabel("Ta [K]")
                            pl.legend(loc=2)
                            pl.savefig(
                                "plots/"+self.data["SOURCEDIR"]+"/"+self.data["FILENAME"][:18]+"_"+self.plotBeamName[i]+".png")
                            pl.close()
                        else:
                            pass
                    
  

                else:
                    # In the case where drift scans were fit but the
                    # fit for all the scans are unsatisfactory.
                    # If there is no data to fit and you want to save
                    # the raw data to the database, plot raw fits for all
                    # data and save data as nan in the database

                    print(self.status)
                    # sys.exit()
                    
                    # update corresponding plots
                    #print(self.scans)
                    
                    for i in range(len(self.beamName)):
                        
                        x = self.x#Data
                        y = self.scans[self.beamName[i]]

                        pl.plot(x, y, "r", label="raw data")
                        pl.suptitle(
                            "Plot "+self.data["FILENAME"][:18]+" of "+self.data["OBJECT"])
                        pl.title(
                            self.beamName[i]+" scan at "+str(self.data["CENTFREQ"])+" MHz", fontsize=10)
                        pl.xlabel("Scandist [deg]")
                        pl.ylabel("Ta [K]")
                        pl.legend(loc=2)
                        pl.savefig(
                            "plots/"+self.data["SOURCEDIR"]+"/"+self.data["FILENAME"][:18]+"_"+self.plotBeamName[i]+".png")
                        pl.close()

            else:
                self.write("Entry not updated in database",'info')
                self.write("SELECT POINTS TO FIT",'info')

        else:

            self.write("Processing new source: " +
                     self.data['FILENAME'],'info')

            question = "Are you sure you want create a new entry for this source in the database ?"
            result = self.popUp(question)

            if result == "yes":
                self.write(
                    "Saving new entry to database",'info')
                # Update db

                # If source is a calibrator and is 2280-MHz
                # and int(self.data["CENTFREQ"]) == 2280:
                if self.data["OBJECTTYPE"] == "CAL":

                    # Save the figure
                    self.plot_new_fig()

                    db.create_table(self.data, table)
                    tbname = db.validate_table_name(table)
                    db.populate_table(self.data, tbname)

                # and int(self.data["CENTFREQ"]) == 2280:
                elif self.data["OBJECTTYPE"] == "TAR":

                    # Save the figure
                    self.plot_new_fig()
                
                    db.create_table(self.data, table)
                    tbname = db.validate_table_name(table)
                    db.populate_table(self.data, tbname)

                    self.write(
                    "Added new row to table",'info')
            else:
                self.write(
                    "Entry not added to database",'info')
                self.write(
                    "SELECT POINTS TO FIT",'info')

    def reset_status(self):
        self.status=[0,0,0,0,0,0]     

    def view_status(self):
        print("# Status: ",self.status)


