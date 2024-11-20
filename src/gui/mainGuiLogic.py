# ============================================================================#
# File: main_gui_logic.py                                                     #
# Author: Pfesesani V. van Zyl                                                #
# ============================================================================#
# =========================================================================== #
# Standard Library Imports
import sys
import os
from datetime import datetime

# Third-Party Library Imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as pl
from matplotlib.backends.backend_qtagg import (FigureCanvasQTAgg as FigureCanvas, 
 NavigationToolbar2QT as NavigationToolbar)

from PyQt5 import QtWidgets
from astropy.time import Time
import glob
import webbrowser
# import pandas as pd
import sqlite3
import re
from datetime import datetime

# Local Imports
sys.path.append("src/")
from common.msgConfiguration import msg_wrapper
# from common.sqlite_db import SQLiteDB
from common.observation import Observation
from common.calibrate import calibrate,calc_pc_pss
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
import common.fitting as fit
import common.miscellaneousFunctions as misc
# =========================================================================== #

class Main(QtWidgets.QMainWindow, Ui_MainWindow):
    """The main class that handles all GUI operations."""

    def __init__(self, log):
        super().__init__() #super(Main, self).__init__()
        self.setupUi(self)

        self.log = log
        self.file_path = ""
        self.deleted = []
        self.initial_status = [0, 0, 0, 0, 0, 0]

        self.log.debug("GUI initiated") #msg_wrapper("debug", self.log.debug,"GUI initiated")

        self.setup_initial_state()
        self.setup_file_handler()

    def setup_initial_state(self):
        """Sets up the initial state of the GUI based on the file path."""
        
        print('\n***** Running setup_initial_state\n')
        if not self.file_path:
            self.set_button_properties(self.btn_edit_driftscan, "white", "black")
            self.set_button_properties(self.btn_edit_timeseries, "white", "black")
            self.set_button_properties(self.btn_view_plots, "white", "black")

            self.btn_edit_driftscan.clicked.connect(self.open_drift_window)
            self.btn_edit_timeseries.clicked.connect(self.open_timeseries_window)
            self.btn_view_plots.clicked.connect(self.open_plots_window)
        else:
            self.open_drift_window()

    def set_button_properties(self, button, bg_color, text_color):
        """Sets the background color and text color of a button."""

        print('\n***** Running set_button_properties\n')
        button.setStyleSheet(f"QPushButton {{background-color: {bg_color}; color: {text_color};}}")

    def setup_file_handler(self):
        print('\n***** Running setup_file_handler\n')
        self.file = FileHandler(self.log)

    # === Windows setup   ===
    def open_drift_window(self):
        """Opens the drift scan editing window and sets up its components."""

        print('\n***** Running open_drift_window\n')
        msg_wrapper("debug", self.log.debug, "Initiating drift scan editing window")

        # Create drift scan window and UI elements
        self.drift_window = QtWidgets.QMainWindow()
        self.drift_ui = Ui_DriftscanWindow()
        self.drift_ui.setupUi(self.drift_window)

        # Initialize canvas managers
        self.canvas = CanvasManager(log=self.log)
        self.secondary_canvas = SecondaryCanvasManager(log=self.log)

        # Create navigation toolbar
        self.ntb = NavigationToolbar(self.canvas, self)

        # Set up layouts
        plot_layout = self.drift_ui.PlotLayout
        other_plot_layout = self.drift_ui.otherPlotsLayout

        # Add elements to layouts
        plot_layout.addWidget(self.ntb)
        plot_layout.addWidget(self.canvas)
        other_plot_layout.addWidget(self.secondary_canvas)

        # Connect buttons (consider moving this to a separate function for better organization)
        self.connect_ui_events()

        # Welcome messages
        self.write("** DRAN GUI loaded successfully.", "info")
        self.write("** Open a file to get started.", "info")

        # Set initial status (consider using a dedicated class to manage status)
        self.status = self.initial_status  # Maybe use a status class with meaningful names for flags

        # Show the window
        self.drift_window.show()

    def open_timeseries_window(self):
        """Opens the timeseries editing window and initializes its components."""

        print('\n***** Running open_timeseries_window\n')
        self.log.debug("** Initiating timeseries editing window")

        # Create timeseries canvas and navigation toolbar
        self.canvas = TimeCanvas(log=self.log)
        self.ntb = NavigationToolbar(self.canvas, self)

        # Create timeseries window and UI elements
        self.time_window = QtWidgets.QMainWindow()
        self.time_ui = Ui_TimeSeriesWindow()
        self.time_ui.setupUi(self.time_window)

        # Set up layout
        plot_layout = self.time_ui.PlotLayout

        # Add elements to layout
        plot_layout.addWidget(self.ntb)
        plot_layout.addWidget(self.canvas)

        # Configure UI elements for timeseries editing
        self.time_ui.BtnResetPoint.setVisible(False)
        self.time_ui.BtnFit.setVisible(True)
        self.time_ui.BtnQuit.setVisible(False)#.setText("Update db")  # Consider a more descriptive verb
        self.time_ui.EdtSplKnots.setVisible(False)
        self.time_ui.LblSplKnots.setVisible(False)
        self.time_ui.BtnUpdateDB.setVisible(False)
        self.time_ui.BtnOpenDB.clicked.connect(self.open_db)
        self.time_ui.comboBoxColsYerr.setVisible(True)
        # Hide x-axis limits and y-axis limits for timeseries (optional)
        self.time_ui.Lblxlim.setVisible(False)
        self.time_ui.Lblylim.setVisible(False)
        self.time_ui.EdtxlimMin.setVisible(False)
        self.time_ui.EdtxlimMax.setVisible(False)
        self.time_ui.EdtylimMax.setVisible(False)
        self.time_ui.EdtylimMin.setVisible(False)
        self.time_ui.BtnFilter.setEnabled(False)  # Might need enabling based on context
        self.time_ui.BtnRefreshDB.setVisible(False)
        self.time_ui.BtnSaveDB.setVisible(False)
        self.time_ui.EdtFilter.setEnabled(False)  # Might need enabling based on context
        # Hide date/time pickers if not relevant for timeseries (optional)
        self.time_ui.EdtEndDate.setVisible(False)
        self.time_ui.EdtStartDate.setVisible(False)
        self.time_ui.LblEndDate.setVisible(False)
        self.time_ui.LblStartDate.setVisible(False)

        # Connect combo box selection changes
        self.time_ui.comboBoxTables.currentIndexChanged.connect(self.on_table_name_changed)
        self.time_ui.comboBoxFitTypes.currentIndexChanged.connect(self.on_fit_changed)

        # Show the window
        self.time_window.show()

    def open_plots_window(self):
        """Opens the plot viewer window and initializes its components."""

        print('\n***** Running open_plots_window\n')
        self.log.debug("** Initiating plot viewer window")

        # Create plot viewer window and UI elements
        self.plot_window = QtWidgets.QMainWindow()
        self.plot_ui = Ui_PlotViewer()
        self.plot_ui.setupUi(self.plot_window)

        # Disable UI elements initially
        self.disable_plot_controls()

        # Enable functions related to opening database
        self.plot_ui.btnOpen.clicked.connect(self.open_db_path)

        # Connect combo box selection changes
        self.plot_ui.comboBox.currentIndexChanged.connect(self.on_combo_changed)
        # self.plot_ui.comboBoxFilter.currentIndexChanged.connect(self.on_filter_changed)

        # Connect buttons (consider separate functions for complex logic)
        self.plot_ui.btnRefreshPlotList.clicked.connect(self.add_items_to_combobox)
        self.plot_ui.btnShow.clicked.connect(self.show_plot_browser)
        self.plot_ui.btnDelete.clicked.connect(self.delete_obs)

        # file_path = sys.path[0]
        # from pathlib import Path
        # print(Path(file_path).parent)
        # sys.exit()
        # Show the window
        self.plot_window.show()

    def disable_plot_controls(self):
        """Disables UI elements related to plot manipulation."""

        print('\n***** Running disable_plot_controls\n')
        self.plot_ui.btnDelete.setEnabled(False)
        self.plot_ui.btnRefreshPlotList.setEnabled(False)
        self.plot_ui.btnShow.setEnabled(False)
        self.plot_ui.comboBox.setEnabled(False)
        self.plot_ui.comboBoxFilter.setEnabled(False)
        self.plot_ui.comboBoxOptions.setEnabled(False)
        
    # def enable_plot_controls(self):
    #     """Enable UI elements related to plot manipulation"""
    #     self.plot_ui.txtBoxEnd.setEnabled(True)
    #     self.plot_ui.txtBoxStart.setEnabled(True)

    def parse_time(self,timeCol):
        """
        Parses the time column and returns only the date part.

        Args:
            timeCol (str): The time column to parse"""
        
        # print('\n***** Running parse_time\n')
        if 'T' in timeCol:
            return timeCol.split('T')[0]
        else:
            return timeCol.split(' ')[0]

    def create_df_from_db(self):
        """
        Creates a pandas DataFrame from a specified table in the database.

        Args:
            table (str): Name of the table to read data from.

        Returns:
            pd.DataFrame: The created DataFrame containing table data.
        """

        print('\n***** Running create_df_from_db\n')

        cnx = sqlite3.connect(self.dbFile)
        self.df = pd.read_sql_query(f"SELECT * FROM {self.tables[0]}", cnx)
        self.df.sort_values('FILENAME',inplace=True)
        self.df['OBSDATE'] = self.df.apply(lambda row: self.parse_time(row['OBSDATE']), axis=1)
        self.df["OBSDATE"] = pd.to_datetime(self.df["OBSDATE"], format="%Y-%m-%d")    

        # Correct all errors, ensure errors are positive, i.e. err > 0
        # ---------------------------------------------------------------

        errCols=[col for col in (self.df.columns) if 'ERR' in col]
        for col in errCols:
            self.df[col] = self.df.apply(lambda row: self.make_positive(row[col]), axis=1)

        cnx.close()
             
    def open_db(self):
        """Open the database."""

        print('\n***** Running open_db\n')
        # Get the database file path
        self.dbFile='/Users/pfesesanivanzyl/dran/resultsFromAnalysis/JUPITER/JUPITER.db'
        # self.dbFile = self.open_file_name_dialog("*.db")

        

        if not self.dbFile:
            print("No file selected")
            return

        if os.path.isfile(self.dbFile):
            pass
        else:
            print(f'File: "{self.dbFile}" does not exists\n')
            return 

        self.time_ui.EdtDB.setText(self.dbFile)
        self.time_ui.EdtDB.setEnabled(True)

        msg_wrapper("debug", self.log.debug, f"\nOpening database: {self.dbFile}")
        cnx = sqlite3.connect(self.dbFile)
        try:
            # Create your connection and read data from database.
            cnx = sqlite3.connect(self.dbFile)
            dbTableList=pd.read_sql_query("SELECT name FROM sqlite_schema WHERE type='table'", cnx)
            self.tables = dbTableList['name'].tolist()
            self.table=self.tables[0]
            self.df = pd.read_sql_query(f"SELECT * FROM {self.table}", cnx)
            self.orig_df=self.df.copy()
            cnx.close()

            print(f"Working with Tables: {self.tables}")
            
        except Exception as e:
            # Handle exceptions gracefully
            # print(f"Error opening database: {e}")
            self.log.error(f"Error opening database: {e}")

            # Consider disabling UI elements or providing feedback to the user
            self.time_ui.EdtDB.setEnabled(False)
            sys.exit()

        finally:
            msg_wrapper("debug", self.log.debug, f"Closing database: {self.dbFile}")

        # make floats
        colList = list(self.df.columns)
        floatList = [col for col in colList if 'FILE' not in col and 'FRONT' not in col and 'OBJ' not in col \
            and 'SRC' not in col and 'OBS' not in col and 'PRO' not in col and 'TELE' not in col and 'HDU' not in col\
            and 'id' not in col and 'DATE' not in col and 'UPGR' not in col and 'TYPE' not in col and 'COOR' not in col\
            and 'EQU' not in col and 'RADEC' not in col and 'SCAND' not in col and 'BMO' not in col and 'DICH' not in col\
            and 'PHAS' not in col and 'POINTI' not in col and 'TIME' not in col and 'INSTRU' not in col and 'INSTFL' not in col\
            and 'time' not in col and \
                    
            'HABM' not in col
            ]

        # Rather than fail, we might want 'pandas' to be considered a missing/bad 
        # numeric value. We can coerce invalid values to NaN as follows using the 
        # errors keyword argument:
        self.df[floatList] = self.df[floatList].apply(pd.to_numeric, errors='coerce')

        # Ensure all errors are +ve
        errCols=[c for c in self.df.columns if 'ERR' in c]
        for c in errCols:
            self.df[c]=self.df.apply(lambda row: self.make_positive(row[c]), axis=1)
            
        # Connect buttons
        self.enable_time_buttons()
        self.connect_ui_events()
        self.populate_cols()
            
        # self.time_ui.BtnRefreshDB.clicked.connect(self.refresh_db)  # Implement refresh the database

    def on_table_name_changed(self):
        """ update combobox when table name changes. """

        print('\n***** Running on_table_name_changed\n')
        self.populate_cols()

    def on_fit_changed(self):
        """  Toggle labels and edit boxes on or off when fit type is changed."""

        print('\n***** Running on_fit_changed\n')
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

    def open_file_name_dialog(self, ext):
        """Opens a file dialog to select a file with the specified extension.

        Args:
            ext: The file extension to filter for.

        Returns:
            The selected file path, or None if no file is selected.
        """

        print('\n***** Running open_file_name_dialog\n')
        msg_wrapper("debug", self.log.debug, "Opening file name dialog")

        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open File", "", f"Fits Files (*{ext});;Fits Files (*{ext})")

        return file_name
    
    def enable_time_buttons(self):
        """Enable time buttons."""

        print('\n***** Running enable_time_buttons\n')
        for widget_name in [
            "comboBoxTables",
            "comboBoxColsX",
            "comboBoxColsY",
            "comboBoxColsYerr",
            "EdtSplKnots",
            "BtnPlot",
            "comboBoxFilters",
            "EdtFilter",
            "BtnFilter",
            "comboBoxFitTypes",
            "comboBoxOrder",
            "BtnFit",
            "BtnDelPoint",
            "BtnDelBoth",
            "BtnResetPoint",
            "BtnReset",
            # "BtnRefreshDB",
            "BtnUpdateDB",
            "BtnSaveDB",
            # "BtnQuit",
        ]:
            getattr(self.time_ui, widget_name).setEnabled(True)

    def connect_ui_events(self):
        """Connect UI elements to their corresponding functions."""

        print('\n***** Running connect_ui_events\n')
        msg_wrapper("debug", self.log.debug, "Connecting buttons to main canvas")

        # Plot and Data Manipulation
        self.time_ui.BtnPlot.clicked.connect(self.plot_cols)
        self.time_ui.BtnFilter.clicked.connect(self.filter_timeseries_data)
        self.time_ui.BtnFit.clicked.connect(self.fit_timeseries)
        self.time_ui.BtnDelPoint.clicked.connect(self.update_point)
        self.time_ui.BtnDelBoth.clicked.connect(self.update_all_points)
        self.time_ui.BtnReset.clicked.connect(self.reset_timeseries)

        # Database Operations
        # self.time_ui.BtnRefreshDB.clicked.connect(self.refresh_db)
        self.time_ui.BtnSaveDB.clicked.connect(self.save_time_db)

        # Application Control
        # self.time_ui.BtnQuit.clicked.connect(self.update_db)  # Consider renaming or providing a clear comment
    
    def make_positive(self, val):
        """Returns the absolute value of the input value.

        Args:
            val: The input value.

        Returns:
            The absolute value of the input, or 0.0 if the input is not a number.
        """

        # print('\n***** Running make_positive\n')
        try:
            return abs(val)
        except TypeError as e:
            msg_wrapper('debug',self.log.debug,f"Error: Cannot calculate absolute value of {val} due to type mismatch. {e}\n")
            return 0.0
        except ValueError as e:
            msg_wrapper('debug',self.log.debug,f"Error: Invalid input value {val}. {e}\n")
            return 0.0
        except Exception as e:
            msg_wrapper('debug',self.log.debug,f"An unexpected error occurred: {e}\n")
            return 0.0
    
    def plot_cols(self, xcol="", ycol="", yerr=""):
        """Plot database columns."""

        print('\n***** Running plot_cols\n')

        # Get selected table
        self.table = self.time_ui.comboBoxTables.currentText()

        if not self.table:

            print("Please select a table")
            self.time_ui.comboBoxTables.clear()
            self.time_ui.comboBoxTables.clear()

            self.time_ui.comboBoxTables.addItems(self.tables)

        # tableCols = self.df.columns.tolist()

        # Get column names from UI or default values
        print('ycol :',ycol)
        xcol = xcol if xcol else self.time_ui.comboBoxColsX.currentText()
        ycol = ycol if ycol else self.time_ui.comboBoxColsY.currentText()
        yerr = yerr if yerr else self.time_ui.comboBoxColsYerr.currentText()
        print('ycol :',ycol)

        print(f"Plotting {xcol} vs {ycol} in table {self.table}")


        try:
            self.df[xcol]=self.df[xcol].astype(float)
        except:
            pass

        if xcol!='OBSDATE':
            self.df[xcol].fillna(value=0, inplace=True)
            self.df[xcol]=self.df[xcol].replace(np.nan, 0.0)

        try:
            self.df[ycol]=self.df[ycol].astype(float)
        except:
            pass

        
        self.df[ycol].fillna(value=0, inplace=True)
        self.df[ycol]=self.df[ycol].replace(np.nan, 0.0)

        # sometimes xx-axis is obsdate so need to account for that
        try:
            xvalues=self.df[xcol].astype(float)
        except:
            xvalues=self.df[xcol]

        yvalues=self.df[ycol].astype(float)
        # yvalues.fillna(value=0, inplace=True)
        yvalues=yvalues.replace(0,np.nan)

        isNotNone = str(yerr)=='None'

        if isNotNone == False: 
            self.df[yerr] = self.df.apply(lambda row: self.make_positive(row[yerr]), axis=1)
            self.df[yerr].fillna(value=0, inplace=True)
            self.df[yerr]=self.df[yerr].astype(float)
            self.df[yerr]=self.df[yerr].replace(np.nan, 0.0)
            yerrvalues=self.df[yerr].astype(float)
            self.canvas.plot_fig(xvalues, yvalues, xcol, ycol, data=self.df, yerr=yerrvalues)
        else:
            self.canvas.plot_fig(xvalues, yvalues, xcol, ycol, data=self.df)

    def filter_timeseries_data(self):
        """Filter the timeseries data based on user selection."""

        print('\n***** Running filter_timeseries_data\n')
        # Get filter text and value from UI
        filter_text = self.time_ui.comboBoxFilters.currentText()
        filter_value = self.time_ui.EdtFilter.text()

        if filter_text == "Type":
            print("Please select a filter type")
        else:
            # Handle comparison filters (>, >=, <, <=)
            if filter_text in (">", ">=", "<", "<="):
                try:
                    cut_value = float(filter_value)
                except ValueError:
                    print(f"{filter_value} is an invalid entry for filter {filter_text}")
                    cut_value = None

                if cut_value is not None:
                    print(f"Filtering data with {filter_text} {cut_value}")

                    # Check if data is plotted
                    if not self.canvas.has_data():
                        print("You need to plot the data first")
                        return

                    x, y = self.canvas.get_data()
                    x_col = self.canvas.x_label
                    y_col = self.canvas.y_label

                    # Apply filter based on operator
                    if filter_text == ">":
                        filtered_indices = np.where(y > cut_value)[0]
                    elif filter_text == ">=":
                        filtered_indices = np.where(y >= cut_value)[0]
                    elif filter_text == "<":
                        filtered_indices = np.where(y < cut_value)[0]
                    elif filter_text == "<=":
                        filtered_indices = np.where(y <= cut_value)[0]
                    else:
                        print("Invalid filter operator detected")
                        return

                    # Check if any data remains after filtering
                    if len(filtered_indices) > 0:
                        print(f"Dropping rows at indices: {filtered_indices}")
                        self.df = self.df.drop(self.df.index[filtered_indices])
                        self.deleted.extend(filtered_indices)
                        print(f"Deleted rows: {self.deleted}")

                        # Update plot with filtered data
                        self.canvas.plot_fig(
                            self.df[x_col],
                            self.df[y_col],
                            x_col,
                            y_col,
                            data=self.df,
                            title=f"Plot of {self.df['SRC'].iloc[-1]} - {x_col} vs {y_col}",
                        )
                    else:
                        print(f"No values found for {filter_text} {cut_value}")

            # Handle unsupported filter types
            elif filter_text == "rms cuts":
                print("RMS cuts not implemented yet")
            elif filter_text == "binning":
                print("Binning not implemented yet")

    def fit_timeseries(self):
        """Fits the timeseries data based on the selected fit type and order."""

        print('\n***** Running fit_timeseries\n')
        fit_type = self.time_ui.comboBoxFitTypes.currentText()
        fit_order = self.time_ui.comboBoxOrder.currentText()

        if fit_order == "Order" or fit_type == "Type":
            print("Please select a fit type and order")
            return

        x_col = self.canvas.x_label
        y_col = self.canvas.y_label

        if x_col != "MJD":
            print("X-axis must be MJD")
            return

        x = np.array(self.canvas.x).astype(float)
        y = np.array(self.canvas.y).astype(float)

        # Get start and end dates from UI inputs
        try:
            start_date = int(self.time_ui.EdtStartDate.text())
        except ValueError:
            start_date = None
        try:
            end_date = int(self.time_ui.EdtEndDate.text())
        except ValueError:
            end_date = None

        # Apply date range filtering
        if start_date is not None or end_date is not None:
            if start_date is not None and end_date is not None:
                mask = (x >= start_date) & (x <= end_date)
            elif start_date is not None:
                mask = x >= start_date
            else:
                mask = x <= end_date
            x, y = x[mask], y[mask]

        if fit_type == "Polynomial":
            # Perform polynomial fit
            
            xm, model, res, rma, coeffs = fit.calc_residual_and_rms_fit(x, y, int(fit_order))
            # ... (rest of the polynomial fit logic)

        elif fit_type == "Spline":
            knots = int(self.time_ui.EdtSplKnots.text())
            if knots < 9:
                knots = 9
            xm, model = fit.spline_fit(x, y, knots, int(fit_order))
            # ... (rest of the spline fit logic)

        # Plot the fitted model
        self.canvas.plot_dual_fig(x, y, xm, model, 'data', 'model', 'Plot of data vs fitted model')

    def update_point(self):
        """
        Updates the selected point in the database and plot.

        Raises:
            ValueError: If setting a column value to NaN fails.
        """

        print('\n***** Running update_point\n')
        # Get selected point and data
        fit_points = self.canvas.fit_points
        click_index = self.canvas.click_index

        if not fit_points or not click_index:
            print("No point selected.")
            return

        i = int(click_index[0])  # Point index to delete

        df=self.df.iloc[i]

        # Get data from DataFrame
        x_col = self.canvas.xlab
        y_col = self.canvas.ylab
        
        xp = self.df[x_col]
        yp = self.df[y_col]

        # Print confirmation message
        print(f'\nDeleting points from row: {i}')
        print(f'Object: {df["OBJECT"]}')
        print(f'Date: {df["OBSDATE"].date()}\n')
        print(f'Frequency: {df["CENTFREQ"]}\n')
        print(f"- x: {fit_points[0][0]}\n"
            f"- y: {fit_points[0][1]}\n"
            )

        freq=int(df['CENTFREQ'])
        srcname=df['OBJECT']


        # Update value in DataFrame
        try:
            self.df.at[i, y_col] = np.nan
        except ValueError:
            self.df.at[i, y_col] = 0.0
            print(f"Warning: Setting {y_col} to 0.0 instead of NaN")

        # sanity check
        cols=self.df.columns.tolist()

        for c in cols:
            if c.endswith('_'):
                self.df.drop(c, axis=1, inplace=True)

        for c in cols:
            for n in range(4):
                if f'_{n}' in c:
                    # print(c)
                    self.df.drop(c, axis=1, inplace=True)

        if freq>22000:
            POS=['S','N','O']#,'CO']
            BEAMS=['']
            POLS=['L','R']

            ta=[]
            for b in BEAMS:
                for l in POLS:
                    for s in POS:
                        # print(f'{b}{s}{l}TA',f'{b}{s}{l}TAERR')
                        ta.append(f'{b}{s}{l}TA')
                        ta.append(f'{b}{s}{l}TAERR')
                        self.df[f'{b}{s}{l}TAFERR'] = self.df[f'{b}{s}{l}TAERR']/self.df[f'{b}{s}{l}TA'].astype(float) 
                    print()

                    print(ta,'\n')
                    print(srcname)
                    if 'JUPITER' in srcname.upper():
                        self.df[f'CORR_{b}{s}{l}DATA'] = self.df.apply(lambda row: calc_pc_pss(row[ta[0]], row[ta[1]],row[ta[2]], row[ta[3]],row[ta[4]], row[ta[5]], row['TOTAL_PLANET_FLUX_D'],df), axis=1)
                        # print(f'{b}{s}{l}PSS', f'{b}{s}{l}PSSERR',f'{b}{s}{l}PC',f'C{b}{s}{l}TA',f'C{b}{s}{l}TAERR',f'{b}{s}{l}PPEFF')
                        self.df[[f'{b}{s}{l}PSS', f'{b}{s}{l}PSSERR',f'{b}{s}{l}PC',f'C{b}{s}{l}TA',f'C{b}{s}{l}TAERR',f'{b}{s}{l}APPEFF']] = pd.DataFrame(self.df[f'CORR_{b}{s}{l}DATA'].tolist(), index=self.df.index)
    
                        self.df[f'{b}{s}{l}PSS'] = self.df[f'{b}{s}{l}PSS'].replace(0, np.nan)
                        self.df.drop(f'CORR_{b}{s}{l}DATA', axis=1, inplace=True)
                        # self.df[[f'{b}{s}{l}PC',f'C{b}{s}{l}TA',f'C{b}{s}{l}TAERR']] = pd.DataFrame(self.df[f'CORR_{b}{s}{l}DATA'].tolist(), index=self.df.index)
                    else:
                        self.df[f'CORR_{b}{s}{l}DATA'] = self.df.apply(lambda row: calibrate(row[ta[0]], row[ta[1]],row[ta[2]], row[ta[3]],row[ta[4]], row[ta[5]], df), axis=1)
                        # print(f'{b}{s}{l}PC',f'C{b}{s}{l}TA',f'C{b}{s}{l}TAERR')
                        self.df[[f'{b}{s}{l}PC',f'C{b}{s}{l}TA',f'C{b}{s}{l}TAERR']] = pd.DataFrame(self.df[f'CORR_{b}{s}{l}DATA'].tolist(), index=self.df.index)
                        self.df.drop(f'CORR_{b}{s}{l}DATA', axis=1, inplace=True)
                    ta=[]

                    # sys.exit()
                    cnx = sqlite3.connect(self.dbFile)
                    self.df.to_sql(self.table,cnx,if_exists='replace',index=False)
                    cnx.close()

            self.plot_cols(x_col,y_col)

    def set_to_zero(self,on,val):
        """set value to zero based on value from another column. 
        e.g. set OLPSS=0 if OLTA==0"""
        try:
            on=float(on)
        except:
            pass
        if str(on) == 'nan' or str(on) == 'np.nan' or str(on)== '0' or on==None or str(on)=='None': #on==0 or on == np.nan or on == 
            return np.nan
        else:
            return val
        
    def update_all_points(self):
        """
        Updates the database and plot after deleting a point from the DataFrame.

        This function retrieves the selected point, updates the DataFrame and database,
        and then redraws the plot.

        Raises:
            Exception: If an error occurs while connecting to or updating the database.
        """

        print('\n***** Running update_all_points\n')
        # Get selected point and index
        fit_points = self.canvas.fit_points
        click_index = self.canvas.click_index

        if not fit_points or not click_index:
            print("No point selected.")
            return

        # Extract data from DataFrame
        i = int(click_index[0]) # Point index to delete

        df=self.df.iloc[i]

        # Get data from DataFrame
        x_col = self.canvas.xlab
        y_col = self.canvas.ylab

        xp = self.df[x_col]
        yp = self.df[y_col]

        # Print confirmation message
        print(f'\nDeleting points from row: {i}')
        print(f'Object: {df["OBJECT"]}')
        print(f'Date: {df["OBSDATE"].date()}\n')
        print(f'Frequency: {df["CENTFREQ"]}\n')
        print(f"- x: {fit_points[0][0]}\n"
            f"- y: {fit_points[0][1]}\n"
            )

        freq=int(df['CENTFREQ'])
        srcname=df['OBJECT']

        # sanity check
        cols=self.df.columns.tolist()
        for c in cols:
            if c.endswith('_'):
                self.df.drop(c, axis=1, inplace=True)

        for c in cols:
            for n in range(4):
                if f'_{n}' in c:
                    # print(c)
                    self.df.drop(c, axis=1, inplace=True)

        if freq>22000:
            POS=['S','N','O']
            BEAMS=['']
            POLS=['L','R']

            ta=[]
            del_ta=[]
            for b in BEAMS:
                for l in POLS:
                    for s in POS:
                        ta.append(f'{b}{s}{l}TA')
                        ta.append(f'{b}{s}{l}TAERR')

                        del_ta.append(f'{b}{s}{l}TA')
                        del_ta.append(f'{b}{s}{l}TAERR')

                        del_ta.append(f'{b}{s}{l}S2N')
                        del_ta.append(f'{b}{s}{l}FLAG')
                        del_ta.append(f'{b}{s}{l}BRMS')
                        del_ta.append(f'{b}{s}{l}SLOPE')
                        del_ta.append(f'{b}{s}{l}BASELEFT')
                        del_ta.append(f'{b}{s}{l}BASERIGHT')
                        del_ta.append(f'{b}{s}{l}RMSB')
                        del_ta.append(f'{b}{s}{l}RMSA')

                        if s=='O':
                            del_ta.append(f'{b}{s}{l}PSS')
                            del_ta.append(f'{b}{s}{l}PSSERR')
                            del_ta.append(f'{b}{s}{l}PC')
                            del_ta.append(f'C{b}{s}{l}TA')
                            del_ta.append(f'C{b}{s}{l}TAERR')
                            del_ta.append(f'{b}{s}{l}APPEFF')
                        
                        print(f'{b}{s}{l}FERR')
                        self.df[f'{b}{s}{l}TAFERR'] = self.df[f'{b}{s}{l}TAERR'].astype(float)/self.df[f'{b}{s}{l}TA'].astype(float) 

                    print()

                    for c in del_ta:
                        try:
                            self.df.at[i, c] = np.nan
                        except ValueError:
                            self.df.at[i, c] = 0.0
                            print(f"Warning: Setting {c} to 0.0 instead of NaN")
                            
                    print(ta,'\n')

                    if 'JUPITER' in srcname.upper():
                        self.df[f'CORR_{b}{s}{l}DATA'] = self.df.apply(lambda row: calc_pc_pss(row[ta[0]], row[ta[1]],row[ta[2]], row[ta[3]],row[ta[4]], row[ta[5]], row['TOTAL_PLANET_FLUX_D'], df), axis=1)
                        print(f'{b}{s}{l}PSS', f'{b}{s}{l}PSSERR',f'{b}{s}{l}PC',f'C{b}{s}{l}TA',f'C{b}{s}{l}TAERR',f'{b}{s}{l}PPEFF')
                        self.df[[f'{b}{s}{l}PSS', f'{b}{s}{l}PSSERR',f'{b}{s}{l}PC',f'C{b}{s}{l}TA',f'C{b}{s}{l}TAERR',f'{b}{s}{l}APPEFF']] = pd.DataFrame(self.df[f'CORR_{b}{s}{l}DATA'].tolist(), index=self.df.index)
                        self.df[f'{b}{s}{l}PSS'] = self.df[f'{b}{s}{l}PSS'].replace(0, np.nan)
                        self.df.drop(f'CORR_{b}{s}{l}DATA', axis=1, inplace=True)
                    
                    else:
                        self.df[f'CORR_{b}{s}{l}DATA'] = self.df.apply(lambda row: calibrate(row[ta[0]], row[ta[1]],row[ta[2]], row[ta[3]],row[ta[4]], row[ta[5]], df), axis=1)
                        print(f'{b}{s}{l}PC',f'C{b}{s}{l}TA',f'C{b}{s}{l}TAERR')
                        self.df[[f'{b}{s}{l}PC',f'C{b}{s}{l}TA',f'C{b}{s}{l}TAERR']] = pd.DataFrame(self.df[f'CORR_{b}{s}{l}DATA'].tolist(), index=self.df.index)
                        self.df.drop(f'CORR_{b}{s}{l}DATA', axis=1, inplace=True)
                    
                    cnx = sqlite3.connect(self.dbFile)
                    self.df.to_sql(self.table,cnx,if_exists='replace',index=False)
                    cnx.close()

                    ta=[]
                    del_ta=[]

            self.plot_cols(x_col,y_col)

    def reset_timeseries(self):
        """
        Resets the timeseries data to its original state and updates the plot.

        This function restores the original DataFrame (`orig_df`) to the `df`
        attribute and clears the current plot. It then calls the `plot_cols`
        function to redraw the plot with the original data.
        """

        print('\n***** Running reset_timeseries\n')
        self.df = self.orig_df.copy()  # Create a copy to avoid modifying the original
        self.canvas.clear_figure()
        self.plot_cols()
        
    def save_time_db(self, filename=""):
        """
        Saves the analysis results of the timeseries to a CSV file.

        Args:
            filename (str, optional): The desired filename for the CSV file.
                If not provided, a default filename will be used.

        Saves the current DataFrame (`self.df`) to a CSV file with the specified
        filename. If no filename is provided, the default filename "Analysis_results.csv"
        will be used.
        """

        print('\n***** Running save_time_db\n') 

        if not filename:
            filename = "Analysis_results.csv"

        self.df.to_csv(filename, index=False)  # Save without row indices
        print(f"Saved results to {filename}")

    def populate_cols(self,xcol='',ycol='',yerrcol=''):
        """Fetches data from the database and populates UI elements."""
        
        print('\n***** Running populate_cols\n')
        # create dataframe from current database table -> self.df
        self.create_df_from_db()

        # Handle empty table selection
        self.table = self.time_ui.comboBoxTables.currentText()

        if not self.table:
            self.time_ui.comboBoxTables.clear()
            self.time_ui.comboBoxTables.addItems(self.tables)
            self.table = self.time_ui.comboBoxTables.currentText()

        self.colNames = self.df.columns.tolist()

        # exclude the following columns from plotting
        plotCols=[]
        for name in self.colNames:
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
                pass
            else:
                plotCols.append(name)
        
        # setup error columns
        errcols=[]
        for name in self.colNames:
            if   'ERR' in name:
                errcols.append(name)
            else:
                pass

        # setup X and Y columns
        xCols=['OBSDATE','MJD','HA','ELEVATION']
        xCols=xCols+[c for c in self.colNames if 'RMS' in c or 'SLOPE' in c]

        yerr=['None']
        self.yErr=list(yerr)+list(errcols)

        # prep columns
        print('cols: ',xcol,ycol,yerrcol)
        self.time_ui.comboBoxColsX.clear()
        self.time_ui.comboBoxColsX.clear()
        if xcol!='':
            self.time_ui.comboBoxColsX.setCurrentText(xcol)
        else:
            self.time_ui.comboBoxColsX.addItems(xCols)
        self.time_ui.comboBoxColsY.clear()
        self.time_ui.comboBoxColsY.clear()
        if ycol!='':
            self.time_ui.comboBoxColsY.setCurrentText(ycol)
        else:
            self.time_ui.comboBoxColsY.addItems(plotCols)
       
        self.time_ui.comboBoxColsYerr.clear()
        self.time_ui.comboBoxColsYerr.clear()
        if yerrcol!='':
            self.time_ui.comboBoxColsYerr.setCurrentText(yerrcol)
        else:
            self.time_ui.comboBoxColsYerr.addItems(self.yErr)

        # print('cols: ',xcol,ycol,yerrcol)
        # self.time_ui.comboBoxColsX.addItems(xCols)
        # self.time_ui.comboBoxColsY.addItems(plotCols)
        # self.time_ui.comboBoxColsYerr.addItems(self.yErr)

    ### Pot viewer ###
    ### ----------- ###
    def open_db_path(self):
        # Open a database

        self.write("Opening DB",'info')

        print('\n***** Running open_db\n')
        # Get the database file path
        self.dbFile='/Users/pfesesanivanzyl/dran/resultsFromAnalysis/JUPITER/JUPITER.db'
        # self.dbFilePath = self.open_file_name_dialog("*.db")

        if self.dbFile == None:
            self.write("You need to select a file to open",'info')
            self.write("Please select a file",'info')
            pass
        else:

            # free all else
            free=True
            self.plot_ui.btnDelete.setEnabled(free)
            self.plot_ui.btnRefreshPlotList.setEnabled(free)
            self.plot_ui.btnShow.setEnabled(free)
            self.plot_ui.comboBox.setEnabled(free)
            self.plot_ui.comboBoxFilter.setEnabled(free)
            self.plot_ui.comboBoxOptions.setEnabled(free)
            self.plot_ui.txtBoxEnd.setEnabled(free)
            self.plot_ui.txtBoxStart.setEnabled(free)

            # open db and get tables
            cnx = sqlite3.connect(self.dbFile)
            dbTableList=pd.read_sql_query("SELECT name FROM sqlite_schema WHERE type='table'", cnx)
            self.plot_tables = sorted(dbTableList['name'].tolist())
            self.plot_table=self.plot_tables[0]
            self.plot_df = pd.read_sql_query(f"SELECT * FROM {self.plot_table}", cnx)
            self.plot_df.sort_values('FILENAME',inplace=True)
            self.plot_df['OBSDATE'] = self.plot_df.apply(lambda row: self.parse_time(row['OBSDATE']), axis=1)
            self.plot_df["OBSDATE"] = pd.to_datetime(self.plot_df["OBSDATE"], format="%Y-%m-%d")   

            self.orig_df=self.plot_df.copy()
            cnx.close()

            print('WTables:',self.plot_tables)

            self.plot_ui.comboBox.clear()     
            self.plot_ui.comboBox.clear()      
            self.plot_ui.comboBox.addItems(self.plot_tables)

    def on_combo_changed(self):

        print("\nChanged obs. to: ", self.plot_ui.comboBox.currentText())

        # get data from db
        # check folder name against table name
        folderName=self.plot_ui.comboBox.currentText()

        # get column names from db and put them in combobox
        colNames=self.plot_df.columns.tolist()

        plotCols=[]
        for name in colNames:
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
                pass
            else:
                plotCols.append(name)

        self.plot_ui.comboBoxOptions.clear()
        self.plot_ui.comboBoxOptions.clear()
        self.plot_ui.comboBoxOptions.addItems(plotCols)

        self.plot_ui.comboBoxFilter.clear()
        self.plot_ui.comboBoxFilter.clear()
        self.plot_ui.comboBoxFilter.addItems(['','>','>=','<','<='])#,'between']'=',)

    # def on_filter_changed(self):
    #     """Handles filter changes in the plot UI.

    #     Toggles the visibility of the second filter (range filter) based on
    #     the selected filter type.
    #     """

    #     filter_type = self.plot_ui.comboBoxFilter.currentText()
    #     # print(filter_type)

    #     if filter_type == "between":
    #         # Enable range filter
    #         self.toggle_range_filter(True)
    #         self.plot_ui.txtBoxFilter.setVisible(False)
    #     else:
    #         # Disable range filter
    #         self.toggle_range_filter(False)
    #         self.plot_ui.txtBoxFilter.setVisible(True)

    def toggle_range_filter(self,toggle):

        self.plot_ui.LblRangeFilter.setVisible(toggle)
        self.plot_ui.LblStart.setVisible(toggle)
        self.plot_ui.LblStop.setVisible(toggle)
        self.plot_ui.LblFormat.setVisible(toggle)
        # self.plot_ui.txtBoxEnd.setVisible(toggle)
        # self.plot_ui.txtBoxStart.setVisible(toggle)

    def add_items_to_combobox(self):
        """Refreshes the list of folders containing plots to be displayed."""

        # Clear all combo boxes
        for combo_box in (
            self.plot_ui.comboBox,
            self.plot_ui.comboBoxOptions,
            self.plot_ui.comboBoxFilter,
        ):
            combo_box.clear()

        # Add table names to the main combo box
        self.plot_ui.comboBox.addItems(sorted(self.plot_tables))

    # def get_filter_date(self,period):
    #     return 
    def write(self,msg,logType=""):
        """ Write to screen and gui """

        if logType=="info":
            msg_wrapper("info", self.log.info, msg)
        else:
            msg_wrapper("debug", self.log.debug, msg)

    def show_plot_browser(self):
        """Opens a web browser containing the plots to be displayed."""

        # Get filter options from the UI
        option = self.plot_ui.comboBoxOptions.currentText()
        filter_type = self.plot_ui.comboBoxFilter.currentText()
        filter_value = self.plot_ui.txtBoxFilter.text()

        # Validate input
        if not option:
            print("Please select an option.")
            return
        
        if not filter_type:
            print("Please select a filter type.")
            return
        
        if not filter_value:
            print("Please enter a filter value.")
            return
        
        start=self.plot_ui.txtBoxStart.text()
        end=self.plot_ui.txtBoxEnd.text()

        
        if start=='':
            print("Please select a start date. 'YYYY-MM-DD'")
            return

        if end=='' :
            print("Please select an end date. 'YYYY-MM-DD'")
            return
        
        
        # Get data from the database
        # folder_name = self.plot_ui.comboBox.currentText()
        df=self.plot_df.copy()

        print('\n','='*50,'\n')
        if start.upper()=='START':
            start=df['OBSDATE'].iloc[0].date()
            print(f"Start date. '{start}'")
            return
        
        if end.upper()=='END':
            start=df['OBSDATE'].iloc[-1].date()
            print(f"End date. '{end}'")
            return
        
        # Filter data based on the selected criteria
      
        try:
            filter_value = float(filter_value)
            # print(self.plot_df)
        except ValueError:
            print("Invalid filter value.")
            return
        
        df[option]=df[option].astype(float)
        print(f"*** Performing operation: self.plot_df['{option}'] {filter_type} {filter_value}")

        # first filter by date
        df=df[(df['OBSDATE']>=datetime.strptime(start, '%Y-%m-%d')) & (df['OBSDATE']<=datetime.strptime(end, '%Y-%m-%d'))]

        # then filter by condition
        if filter_type == '>':
            df = df[df[option] > filter_value].sort_values('FILENAME')
        elif filter_type == '>=':
            df = df[df[option] >= filter_value].sort_values('FILENAME')
        elif filter_type == '<':
            df = df[df[option] < filter_value].sort_values('FILENAME')
        elif filter_type == '<=':
            df = df[df[option] <= filter_value].sort_values('FILENAME')
        # elif filter_type == 'between':
        #     df = df[(df[f'{option}'] >= filter_value[0]) & (df[f'{option}'] <= filter_value[1])].sort_values('FILENAME')
        # df =df[df['OBSDATE']>=start and df['OBSDATE']<=end]
        
        # print(df.iloc[0])
            
        print(f'\nFound: {len(df)} rows")\n')
        # sys.exit()

        # Print basic statistics
        if len(df)>0:

            print(df[option])
            self.print_basic_stats(df, option)

            # sys.exit()
            
            # src info
            srcname=df['OBJECT'].iloc[0]
            freq = int(df['CENTFREQ'].iloc[0])

            print(f'Source name: {srcname}, freq: {freq} MHz')

            # Get plot paths
            image_dir = f"plots/{srcname}/{freq}"
            image_paths = []

            # print(df.columns.tolist())

            image_names=os.listdir(image_dir)

            print(f'\nSEARCHING THROUGH: {len(image_names)} IMAGES\n')

                # print(image_names)
                # sys.exit()

            file_path = sys.path[0]
            from pathlib import Path
            path=Path(file_path).parent
            # print()
            # sys.exit()

            for _, row in df.iterrows():
                    plot_tag = row['FILENAME'][:18]
                    # print(plot_tag)
                    # sys.exit()
                    for image_name in image_names:
                        if plot_tag in image_name:
                            for pos in ['N','S','O']:
                                for pol in ['L','R']:
                                    # print(option, f'{pos}{pol}'  ,image_name, f'HP{pos}_{pol}CP')
                                    # if f'{pos}{pol}' in option:
                                    if (f'HP{pos}_{pol}CP' in image_name) and (f'{pos}{pol}' in option):
                                            print( f'HP{pos}_{pol}CP' ,image_name, f'{pos}{pol}',option )
                                            image_paths.append(f'{path}/{os.path.join(image_dir, image_name)}')
                                            break
                                    elif (f'O{pos}_{pol}CP' in image_name) and (f'O{pol}' in option):
                                            print( f'O{pos}_{pol}CP' ,image_name, f'O{pos}{pol}',option )
                                            image_paths.append(f'{path}/{os.path.join(image_dir, image_name)}')
                                            break
            print(image_paths)
            

            if len(image_paths)==0:
                for _, row in df.iterrows():
                    plot_tag = row['FILENAME'][:18]
                    for image_name in image_names:
                            if plot_tag in image_name: 
                                # print(plot_tag, image_name)
                                image_paths.append(f'{path}/{os.path.join(image_dir, image_name)}')
     
            print(image_paths)
            # sys.exit()
            # htmlstart = '<html> <head>\
            #                 <meta charset = "utf-8" >\
            #                 <meta http-equiv="X-UA-Compatible" content="IE=edge">\
            #                 <meta name = "viewport" content = "width=device-width, initial-scale=1" > <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-BmbxuPwQa2lc/FVzBcNJ7UAyJxM6wuqIj61tLrc4wSX0szH/Ev+nYRRuWlolflfl" crossorigin="anonymous"> <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta2/dist/js/bootstrap.bundle.min.js" integrity="sha384-b5kHyXgcpbZJO/tY9Ul7kGkf1S0CWuKcCD38l8YkeH8z8QjE0GmW1gYU5S9FOnJ0" crossorigin="anonymous"></script> \
            #                         <style> \
            #                             img {border: 3px solid  # ddd; /* Gray border */border-radius: 5px;  /* Rounded border */padding: 5px; /* Some padding */width: 400px; /* Set a small width */}/* Add a hover effect (blue shadow) */\
            #                             img:hover {box-shadow: 0 0 2px 1px rgba(0, 140, 186, 0.5);}\
            #                         </style> \
            #                     <title>Driftscan plots</title>\
            #                     </head>\
            #                     <div class="container-fluid"> \
            #                         <div class="row">\
            #                             <hr>\
            #                             <h1> Plotting folder '+srcname.upper() + ' @ '+ str(int(freq)) +' MHz </h1> \
            #                             <p>'

            script = ''' const images='''+f'{image_paths}'+''';
            const imagesPerPage = 20;
      let currentPage = 1;

      function displayImages(page) {
        const gallery = document.getElementById("image-gallery");
        gallery.innerHTML = "";

        const startIndex = (page - 1) * imagesPerPage;
        const endIndex = startIndex + imagesPerPage;

        for (let i = startIndex; i < endIndex && i < images.length; i++) {
          const img = document.createElement("img");
          img.src = images[i];
          gallery.appendChild(img);
        }
      }

      function buildPagination() {
        const pagination = document.getElementById("pagination");
        pagination.innerHTML = "";

        const totalPages = Math.ceil(images.length / imagesPerPage);

        for (let i = 1; i <= totalPages; i++) {
          const li = document.createElement("li");
          li.classList.add("page-item");
          const a = document.createElement("a");
          a.classList.add("page-link");
          a.href = "#";
          a.textContent = i;
          a.addEventListener("click", () => {
            currentPage = i;
            displayImages(currentPage);
            updateActivePage();
          });
          li.appendChild(a);
          pagination.appendChild(li);
        }
      }

      function updateActivePage() {
        const pagination = document.getElementById("pagination");
        const pageItems = pagination.querySelectorAll(".page-item");
        pageItems.forEach((item, index) => {
          if (index + 1 === currentPage) {
            item.classList.add("active");
          } else {
            item.classList.remove("active");
          }
        });
      }

      displayImages(currentPage);
      buildPagination();
      updateActivePage();

            '''

            file_path = sys.path[0]
            # print(file_path)
            with open(f'{file_path}/gui/assets/script2.js','w+') as f:
                f.write(script)

            htmlstart = '<html> <head>\
                            <meta charset = "utf-8" >\
                            <meta http-equiv="X-UA-Compatible" content="IE=edge">\
                            <meta name = "viewport" content = "width=device-width, initial-scale=1" > \
                            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"/>\
                               <link rel="stylesheet" href="src/gui/assets/style.css">\
                                <title>Driftscan plots</title>\
                                </head>\
                                <body>\
                                        <h1> Plotting folder '+srcname.upper() + ' @ '+ str(int(freq)) +' MHz </h1> \
                                        <div class="gallery" id="image-gallery">\
                                            </div>\
                                        <ul class="pagination justify-content-center mt-4" id="pagination"></ul>\
                                <script src="src/gui/assets/script2.js"></script>\
                                </body></html>'        
                                                                     
            htmlmid=''
      
            # for img in image_paths:
                    # print(f'Showing: {img}')

            # for i in range(len(image_paths)):
                    #print(images.split("/")[1],images.split("/")[2])
                    # pathtoimg = images[i]
                    # img = '<small class="card-title">'+img.split("/")[3]+'</small><br/>\
                    #         <a target="_blank" href="'+img + \
                    #         '"><img src="'+img + \
                    #         '" class="card-img-top" alt="image goes here"></a>'
                    # imglink ='<div class = "card" style = "width: 13rem;" >\
                    #             '+img+'\
                    #                 </div>'
                    # htmlmid=htmlmid+imglink

            # htmlmid=htmlmid+'</p></div>'
            # htmlend = '</div></html>'
            # html = htmlstart+htmlmid+htmlend
            html=htmlstart

                # create the html file
            path = os.path.abspath('temp.html')
            url = 'file://' + path

            with open(path, 'w') as f:
                    f.write(html)
            webbrowser.open(url)
                
       

    def print_basic_stats(self, df, option):
        """Prints basic statistics for the given DataFrame and option."""

        print("\n--- Basic stats ---\n")
        
        try:
            print(f'DATE start: {df["OBSDATE"].iloc[0]}')
            print(f'DATE end: {df["OBSDATE"].iloc[-1]}')
            print(f'MJD start: {df["MJD"].iloc[0]:.1f}')
            print(f'MJD end: {df["MJD"].iloc[-1]:.1f}')
            print(f'3sigma upper limit: {df[option].mean() + (df[option].mean()*df[option].std()):.3f}')
            print(f'3sigma lower limit: {df[option].mean() - (df[option].mean()*df[option].std()):.3f}')
        except:
            print(f'DATE start: {df["OBSDATE"].iloc[0]}')
            print(f'DATE end: {df["OBSDATE"].iloc[-1]}')
            print(f'MJD start: {df["MJD"].iloc[0]:.1f}')
            print(f'MJD end: {df["MJD"].iloc[-1]:.1f}')
        
        print("Min:", df[option].min())
        print("Max:", df[option].max())
        print("Mean:", df[option].mean())
        print("Median:", df[option].median())
        print(f'Len:" {len(df)}')

        print("-" * 20, "\n")
        
    def delete_obs(self):
        ''' Delete an observation. '''

        option=self.plot_ui.comboBoxOptions.currentText()
        filter=self.plot_ui.comboBoxFilter.currentText()
        txt=self.plot_ui.txtBoxFilter.text()
        