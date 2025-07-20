# ============================================================================#
# File: main_gui_logic.py                                                     #
# Author: Pfesesani V. van Zyl                                                #
# ============================================================================#
# =========================================================================== #
# Standard Library Imports
import sys
import os
from datetime import datetime
import datetime as dt
from sqlalchemy import create_engine

import matplotlib
matplotlib.use('WebAgg')

# Third-Party Library Imports
import matplotlib.dates as mdates 
import numpy as np
import pandas as pd
# pd.options.mode.copy_on_write = True  # https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
pd.set_option("mode.copy_on_write", True)

import matplotlib.pyplot as pl
from matplotlib.backends.backend_qtagg import (FigureCanvasQTAgg as FigureCanvas, 
 NavigationToolbar2QT as NavigationToolbar)

from PyQt5 import QtWidgets
from astropy.time import Time
import glob
import webbrowser
import sqlite3
from datetime import datetime
from pathlib import Path


# Local Imports
sys.path.append("src/")
from common.msgConfiguration import msg_wrapper
from common.calibrate import _get_pss_values,getpss,calc_dualtotFlux2, calibrate, calc_pc_pss, calc_flux, calc_totFlux, calc_dualtotFlux, get_fluxes_df
from common import fitting as fit
from common.file_handler import FileHandler
from common import miscellaneousFunctions as misc

from .main_window import Ui_MainWindow
from .edit_driftscan_window1 import Ui_DriftscanWindow
from .edit_timeseries_window3 import Ui_TimeSeriesWindow
from .view_plots_window import Ui_PlotViewer
from .canvasManager import CanvasManager
from .secondaryCanvasManager import SecondaryCanvasManager
from .timeseries_canvas import TimeCanvas

# =========================================================================== #


class Main(QtWidgets.QMainWindow, Ui_MainWindow):
    """Main application window handling GUI operations and core functionality.
    
    Args:
        log: Logger instance for application logging
    """
    
    def __init__(self, log):
        super().__init__()
        self.setupUi(self)

        # Initialize dependencies
        self.log = log
        self._initialize_application_state()
        self._setup_components()
        
        self.log.debug("GUI initiated successfully")
        
    def _initialize_application_state(self):
        """Initialize all application state variables."""
        self.file_path = ""  # Current active file path
        self.deleted_items = []  # Track deleted items for undo functionality
        self.initial_status = [0, 0, 0, 0, 0, 0]  # Default status values
        
    def _setup_components(self):
        """Initialize and configure all UI components."""
        
        self.setup_initial_state()
        # self._setup_file_handler()
        # self._connect_signals()

    def setup_initial_state(self):
        """Sets up the initial GUI state based on whether a file is loaded.
        
        Configures button properties and connections differently depending on whether
        a file is currently loaded (self.file_path exists) or not.
        """
        self.log.debug("Initializing GUI state")
        
        try:
            if not self.file_path:
                self._setup_no_file_state()
            else:
                self._setup_with_file_state()
        except Exception as e:
            self.log.error(f"Failed to initialize GUI state: {str(e)}")
            self.statusBar().showMessage("Initialization error")
            raise

    def _setup_no_file_state(self):
        """Configure UI for state when no file is loaded."""
        buttons_config = [
            (self.btn_edit_driftscan, self.open_drift_window, "white", "black"),
            (self.btn_edit_timeseries, self.open_timeseries_window, "white", "black"), 
            # (self.btn_view_plots, self.open_plots_window, "white", "black")
        ]
        
        for btn, handler, bg_color, text_color in buttons_config:
            self._configure_button(btn, bg_color, text_color)
            btn.clicked.connect(handler)
        
        self.log.debug("Configured UI for no-file state")

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
        self.time_ui.BtnQuit.setVisible(False) #.setText("Update db")  # Consider a more descriptive verb
        self.time_ui.EdtSplKnots.setVisible(False)
        self.time_ui.LblSplKnots.setVisible(False)
        self.time_ui.BtnUpdateDB.setVisible(False)
        self.time_ui.BtnDeleteZoomedPoints.setVisible(True)
        self.time_ui.BtnViewZoomedArea.setVisible(True)
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

        # self.time_ui.BtnDeleteZoomedPoints.setVisible(False)
        # self.time_ui.BtnViewZoomedArea.setVisible(False)

        # Connect combo box selection changes
        self.time_ui.comboBoxTables.currentIndexChanged.connect(self.on_table_name_changed)
        self.time_ui.comboBoxFitTypes.currentIndexChanged.connect(self.on_fit_changed)
        
        
        # self.time_ui.BtnDeleteZoomedPoints.cl
        # self.time_ui.BtnDelBoth.clicked.connect(self.delete_obs)
        # self.plot_ui.btnDelete.clicked.connect(self.delete_obs)
        # Show the window
        self.time_window.show()
        
    def on_table_name_changed(self):
        """Update UI components when the selected table changes in the combobox."""
    
        print('\n***** Running on_table_name_changed\n')

        # Get selected table and update dataframe
        table=self.time_ui.comboBoxTables.currentText()
        self.create_df_from_db(table)

        # Initialize column lists
        self.colNames = self.df.columns.tolist()
        
        # Process error columns
        self._process_error_columns()

        # Process X and Y axis columns
        xCols = self._get_x_columns()
        plotCols = self._get_plot_columns()

        print(f'Getting data from table: {table}')

        # Update UI components
        self._update_column_comboboxes(xCols, plotCols)
        
        # Plot with default columns
        self.plot_cols(xcol=xCols[0], ycol=plotCols[0], yerr="")

    def plot_cols(self, xcol="", ycol="", yerr=""):
        """Plot selected columns from the database with optional error bars.
        
        Args:
            xcol (str): Column name for x-axis data. If empty, uses current UI selection.
            ycol (str): Column name for y-axis data. If empty, uses current UI selection.
            yerr (str): Column name for error data. If empty or "None", no error bars are shown.
        """
        print('\n***** Running plot_cols\n')
        
        # Get selected table from UI
        self.table = self.time_ui.comboBoxTables.currentText()

         # Handle case where no table is selected
        if not self.table:
            print("Please select a table")
            self._update_ui_components()

        # Get column names from UI or default values
        xcol = xcol if xcol else self.time_ui.comboBoxColsX.currentText()
        ycol = ycol if ycol else self.time_ui.comboBoxColsY.currentText()
        yerr = yerr if yerr else self.time_ui.comboBoxColsYerr.currentText()


        print(f"\nPlotting {xcol} vs {ycol} in table {self.table}")

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

        # 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value)
        # self.df[ycol].fillna(value=0, inplace=True)

        self.df.fillna({ycol:0}, inplace=True)
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
        # print(isNotNone)

        if isNotNone == False: 
            self.df[yerr] = self.df.apply(lambda row: self.make_positive(row[yerr]), axis=1)
            self.df[yerr].fillna(value=0, inplace=True)
            self.df[yerr]=self.df[yerr].astype(float)
            self.df[yerr]=self.df[yerr].replace(np.nan, 0.0)
            yerrvalues=self.df[yerr].astype(float)
            self.canvas.plot_fig(xvalues, yvalues, xcol, ycol, data=self.df, yerr=yerrvalues)
        else:
            self.canvas.plot_fig(xvalues, yvalues, xcol, ycol, data=self.df)
            # print('what')


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


    def _process_error_columns(self):
        """Identify and process error columns from the dataframe."""
        errcols = [name for name in self.colNames if 'ERR' in name]
        self.yErr = ['None'] + errcols

    def _get_x_columns(self):
        """Get columns suitable for X-axis plotting."""
        base_x_cols = ['OBSDATE', 'MJD', 'HA', 'ELEVATION']
        additional_x_cols = [c for c in self.colNames if 'RMS' in c or 'SLOPE' in c]
        return base_x_cols + additional_x_cols

    def _get_plot_columns(self):
        """Get columns suitable for Y-axis plotting by excluding unwanted columns."""
        exclude_patterns = [
            'id', 'LOGFREQ', 'CURDATETIME', 'FILE', 'OBSD', 'MJD', 'OBS', 'OBJ',
            'RAD', 'TYPE', 'PRO', 'TELE', 'UPGR', 'INST', 'SCANDIR', 'SRC',
            'COORDSYS', 'LONGITUD', 'LATITUDE', 'POINTING', 'DICHROIC', 'PHASECAL',
            'HPBW', 'FNBW', 'SNBW', 'FRONTEND', 'BASE'
        ]
        
        return [
            name for name in self.colNames
            if not any(pattern in name for pattern in exclude_patterns)
            and name != 'id'  # Special case for exact match
        ]

    def _update_column_comboboxes(self, xCols, plotCols):
        """Update the X, Y, and error column comboboxes in the UI."""
        # Clear and populate X-axis combobox
        self.time_ui.comboBoxColsX.clear()
        self.time_ui.comboBoxColsX.addItems(xCols)
        
        # Clear and populate Y-axis combobox
        self.time_ui.comboBoxColsY.clear()
        self.time_ui.comboBoxColsY.addItems(plotCols)
        
        # Clear and populate error combobox
        self.time_ui.comboBoxColsYerr.clear()
        self.time_ui.comboBoxColsYerr.addItems(self.yErr)
        
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
    
    def open_db(self):
        """Open and process a SQLite database file, initializing UI components and data structures."""


        print('\n***** Running open_db\n')

        # Get the database file path
        # self.dbFile='/Users/pfesesanivanzyl/dran/HART26DATA.db'#resultsFromAnalysis/JUPITER/JUPITER.db'
        self.dbFile = self.open_file_name_dialog("*.db")
        # self.dbFile='/Users/pfesesanivanzyl/dran-analysis/resultsFromAnalysis/3C48/3C48.db'#resultsFromAnalysis/JUPITER/JUPITER.db'
        
        # Validate file selection
        if not self.dbFile:
            print("No file selected")
            return

        # Verify file exists
        if os.path.isfile(self.dbFile):
            pass
        else:
            print(f'File: "{self.dbFile}" does not exists\n')
            return 

        # Update UI with database path
        self.time_ui.EdtDB.setText(self.dbFile)
        self.time_ui.EdtDB.setEnabled(True)
        
        # Log database opening
        msg_wrapper("debug", self.log.debug, f"\nOpening database: {self.dbFile}")
        
        # Connect to database and process data
        cnx = sqlite3.connect(self.dbFile)
        # try:
            # Create your connection and read data from database.
        self._load_database_tables(cnx)
        self._process_dataframe()

            # # Correct all errors, ensure errors are positive, i.e. err > 0
            # # ---------------------------------------------------------------
            # errCols=[col for col in (self.df.columns) if 'ERR' in col]
            # for col in errCols:
            #     self.df[col] = self.df.apply(lambda row: self.make_positive(row[col]), axis=1)

        cnx.close()

            # Update UI components
        self._update_ui_components()
            
            # Process numeric columns and errors
        self._process_numeric_columns()
        self._ensure_positive_errors()
            
            # Final setup
        self._finalize_setup()
        
            
        # except Exception as e:
        #     # Handle exceptions gracefully
        #     # print(f"Error opening database: {e}")
        #     self.log.error(f"Error opening database: {e}")

        #     # Consider disabling UI elements or providing feedback to the user
        #     self.time_ui.EdtDB.setEnabled(False)
        #     sys.exit()

    def _update_ui_components(self):
        """Update UI components with loaded data."""
        print(f"Working with Tables: {self.tables}")
        self.time_ui.comboBoxTables.clear()
        self.time_ui.comboBoxTables.addItems(self.tables)

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
        

    def create_df_from_db(self,table=''):
        """
        Creates a pandas DataFrame from a specified table in the database.

        Args:
            table (str): Name of the table to read data from.

        Returns:
            pd.DataFrame: The created DataFrame containing table data.
        """

        print('\n***** Running create_df_from_db\n')


        cnx = sqlite3.connect(self.dbFile)
        # print(self.tables)
        # sys.exit()

        if table:
            self.df = pd.read_sql_query(f"SELECT * FROM '{table}'", cnx)
        else:
            self.df = pd.read_sql_query(f"SELECT * FROM '{self.tables[0]}'", cnx)
            
        self.df.sort_values('FILENAME',inplace=True)
        self.df['OBSDATE'] = self.df.apply(lambda row: self.parse_time(row['OBSDATE']), axis=1)
        self.df["OBSDATE"] = pd.to_datetime(self.df["OBSDATE"]).dt.date
        self.df["OBSDATE"] = pd.to_datetime(self.df["OBSDATE"], format="%Y-%m-%d")    

        # Correct all errors, ensure errors are positive, i.e. err > 0
        # ---------------------------------------------------------------
        errCols=[col for col in (self.df.columns) if 'ERR' in col]
        for col in errCols:
            self.df[col] = self.df.apply(lambda row: self.make_positive(row[col]), axis=1)

        cnx.close()

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
            "BtnDeleteZoomedPoints",
            "BtnViewZoomedArea",
            # "BtnQuit",
        ]:
            getattr(self.time_ui, widget_name).setEnabled(True)

    def view_zoomed_area(self):

        xlim,ylim=self.canvas.onzoom()

        xCol=self.time_ui.comboBoxColsX.currentText()
        yCol=self.time_ui.comboBoxColsY.currentText()

        print('\n',xCol,yCol)

        if xCol=='OBSDATE':
            xmin = str(mdates.num2date(xlim[0]).date())
            xmax = str(mdates.num2date(xlim[1]).date())
            xmin=datetime.strptime(xmin, '%Y-%m-%d')
            xmax=datetime.strptime(xmax, '%Y-%m-%d')
        else:
            xmin = xlim[0]
            xmax = xlim[1]
        
        ymin = ylim[0]
        ymax = ylim[1]

        print(xmin,xmax)
        print(f"Zoomed: ymin={ymin}, ymax={ymax}")
        print(f"Zoomed: xmin={xmin}, xmax={xmax}")

        # conditions
        cond1=(self.df[xCol]>=xmin) & (self.df[xCol]<=xmax)
        cond2=(self.df[yCol]>=ymin) & (self.df[yCol]<=ymax)

        # get data based on zoomed area
        df=self.df[cond1&cond2]
        # df=df[cond2]

        print(df['OBSDATE'])#[[xCol,yCol]])

        # show plots of zoomed area

        # sys.exit()

        # # src info
        srcname=df['OBJECT'].iloc[0]

        if srcname.startswith('P'):
            l=srcname[1:]
            if 'M' in l:
                l='P'+l.replace('M','-')
            elif 'P' in l:
                l='P'+l.replace('P','+')
            srcname=l

        elif srcname.startswith('J'):
            l=srcname[1:]
            if 'M' in l:
                l='J'+l.replace('M','-')
            elif 'P' in l:
                l='J'+l.replace('P','+')
            srcname=l
        else:
            pass

        

        freq = int(df['CENTFREQ'].iloc[0])

        print(f'\nPlotting data for {srcname} at freq: {freq} MHz')

        # # Get plot paths
        # image_dir = f"plots/{srcname}/{freq}"
        image_dir=os.path.join(os.path.abspath('.'),'plots')
        image_paths = []

        image_names=os.listdir(f'{image_dir}/{srcname}/{freq}/')

        print(f'\nSEARCHING THROUGH: {len(image_names)} IMAGES\n')

        # print(image_names)
        df['FILES'] = df['FILENAME'].str[:18]
        files=sorted(df['FILES'].tolist())
        # filepaths=sorted(df['FILENAME'].tolist())

        # print(df['FILES'].tolist())
        # sys.exit()

        for fl in files:
        #     for pos in ['N','S','O']:
        #         for pol in ['L','R']:
            for flimg in image_names:
                if fl in flimg:
                    image_paths.append(f'{image_dir}/{srcname}/{freq}/{flimg}')
        
        image_paths=sorted(image_paths)
        # print(image_paths)
        
        self.print_basic_stats(df, yCol)

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
        print(file_path)
        

        with open(f'{file_path}/gui/assets/script2.js','w+') as f:
            f.write(script)

        htmlstart = '<html> <head>\
                            <meta charset = "utf-8" >\
                            <meta http-equiv="X-UA-Compatible" content="IE=edge">\
                            <meta name = "viewport" content = "width=device-width, initial-scale=1" > \
                            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"/>\
                               <link rel="stylesheet" href="src/dran2/gui/assets/style2.css">\
                                <title>Driftscan plots</title>\
                                </head>\
                                <body>\
                                        <h1> Plotting folder '+srcname.upper() + ' @ '+ str(int(freq)) +' MHz </h1> \
                                        <div class="gallery-container">\
                                            <div class="gallery" id="gallery"></div>\
                                            <div class="pagination" id="pagination">\
                                                <button id="prev-btn" disabled>Previous</button>\
                                                <div id="page-numbers"></div>\
                                                <button id="next-btn">Next</button>\
                                            </div>\
                                        </div>\
                                <script src="src/dran2/gui/assets/script3.js"></script>\
                                </body></html>'        
                                                                     
        htmlmid=''
      
        html=htmlstart

                # create the html file
        path = os.path.abspath('temp.html')
        print(path)
        url = 'file://' + path

        print(url)
        # sys.exit()
        with open(path, 'w') as f:
            f.write(html)
        webbrowser.open(url)

    def delete_zoomed_area(self):
        pass

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


    def _process_numeric_columns(self):
        """Convert appropriate columns to numeric values."""
        # List of column patterns to exclude from numeric conversion
        exclude_patterns = [
            'FILE', 'FRONT', 'OBJ', 'SRC', 'OBS', 'PRO', 'TELE', 'HDU',
            'id', 'DATE', 'UPGR', 'TYPE', 'COOR', 'EQU', 'RADEC', 'SCAND',
            'BMO', 'DICH', 'PHAS', 'POINTI', 'TIME', 'INSTRU', 'INSTFL',
            'time', 'HABM'
        ]
        
        # Get columns to convert to numeric
        float_cols = [
            col for col in self.df.columns 
            if not any(pattern in col for pattern in exclude_patterns)
        ]
        
        # Convert to numeric, coercing errors to NaN
        self.df[float_cols] = self.df[float_cols].apply(
            pd.to_numeric, 
            errors='coerce'
        )

    def _ensure_positive_errors(self):
        """Ensure all error columns contain positive values."""
        err_cols = [c for c in self.df.columns if 'ERR' in c]
        for col in err_cols:
            self.df[col] = self.df.apply(
                lambda row: self.make_positive(row[col]), 
                axis=1
            )

    def _finalize_setup(self):
        """Finalize UI and event connections."""
        self.enable_time_buttons()
        self.connect_ui_events()
        # self.populate_cols()
        
    def _load_database_tables(self, cnx):
        """Load tables from database and initialize main dataframe."""
        dbTableList = pd.read_sql_query(
            "SELECT name FROM sqlite_schema WHERE type='table'", 
            cnx
        )
        self.tables = sorted(dbTableList['name'].tolist())
        
        # Filter out sqlite system tables
        self.tables = [c for c in self.tables if 'sqlite' not in c]
        
        if not self.tables:
            raise ValueError("No valid tables found in database")
        
        self.table = self.tables[0]
        self.df = pd.read_sql_query(f"SELECT * FROM '{self.table}'", cnx)
        self.orig_df = self.df.copy()

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
        
    def _process_dataframe(self):
        """Process and clean the main dataframe."""

        # Sort and process dates
        self.df.sort_values('FILENAME', inplace=True)
        self.df['OBSDATE'] = self.df.apply(
            lambda row: self.parse_time(row['OBSDATE']), 
            axis=1
        )
        self.df["OBSDATE"] = pd.to_datetime(self.df["OBSDATE"]).dt.date
        self.df["OBSDATE"] = pd.to_datetime(self.df["OBSDATE"], format="%Y-%m-%d")
        
        # Remove duplicates
        # ids = self.df['MJD']
        # self.df = self.df[ids.isin(ids[ids.duplicated()])].sort_values("MJD")
        # self.df = self.df.drop_duplicates(
        #     subset=['time'],
        #     keep="first"
        # ).sort_values(by='time', ascending=True)
 
    # def open_db_path(self):
    #     """Open a SQLite database file, load its contents, and initialize UI components."""
    

    #     self.write("Opening DB",'info')
    #     print('\n***** Running open_db\n')

    #     # Get the database file path
    #     # self.dbFile='/Users/pfesesanivanzyl/dran/resultsFromAnalysis/JUPITER/JUPITER.db'
    #     self.dbFilePath = self.open_file_name_dialog("*.db")

    #     if self.dbFilePath == None:
    #         self.write("You need to select a file to open",'info')
    #         self.write("Please select a file",'info')
    #         pass
    #     else:

    #         # free all else
    #         # Enable UI components
    #         self._enable_plot_ui_components(True)

    #         # open db and get tables
    #         cnx = sqlite3.connect(self.dbFilePath)
    #         dbTableList=pd.read_sql_query("SELECT name FROM sqlite_schema WHERE type='table'", cnx)
    #         self.plot_tables = sorted(dbTableList['name'].tolist())
    #         self.plot_table=self.plot_tables[0]

    #         self.plot_df = pd.read_sql_query(f"SELECT * FROM '{self.plot_table}'", cnx)
    #         self.plot_df.sort_values('FILENAME',inplace=True)
    #         self.plot_df['OBSDATE'] = self.plot_df.apply(lambda row: self.parse_time(row['OBSDATE']), axis=1)
    #         self.plot_df["OBSDATE"] = pd.to_datetime(self.plot_df["OBSDATE"], format="%Y-%m-%d")   

    #         self.orig_df=self.plot_df.copy()
    #         cnx.close()

    #         # remove duplicates
    #         ids=self.plot_df['MJD']
    #         self.plot_df=self.plot_df[ids.isin(ids[ids.duplicated()])].sort_values("MJD")
    #         # self.plot_df=self.plot_df.drop_duplicates(subset=['time'],keep="first").sort_values(by='time',ascending=True)
            

    #         print('Plot Tables:',self.plot_tables)

    #         self._update_plot_ui_combobox()

    def _update_plot_ui_combobox(self):
        """Update the combo box with available tables."""
        self.plot_ui.comboBox.clear()
        self.plot_ui.comboBox.addItems(self.plot_tables)

    def _enable_plot_ui_components(self, enable: bool):
        """Enable or disable plot UI components."""
        components = [
            self.plot_ui.btnDelete,
            self.plot_ui.btnRefreshPlotList,
            self.plot_ui.btnShow,
            self.plot_ui.comboBox,
            self.plot_ui.comboBoxFilter,
            self.plot_ui.comboBoxOptions,
            self.plot_ui.txtBoxEnd,
            self.plot_ui.txtBoxStart
        ]
        for component in components:
            component.setEnabled(enable)
    
    def _setup_with_file_state(self):
        """Configure UI for state when a file is loaded."""
        self.open_drift_window()
        self.log.debug("Auto-opened drift window for loaded file")

    def _configure_button(self, button, background_color, text_color):
        """Helper method to standardize button styling.
        
        Args:
            button: QPushButton to configure
            background_color: str color name or hex value
            text_color: str color name or hex value
        """
        button.setStyleSheet(
            f"QPushButton {{ background-color: {background_color}; color: {text_color}; }}"
        )
        button.setEnabled(True)

    def open_drift_window(self):
        """Initializes and displays the drift scan editing window with all components.
        
        Creates the window, sets up canvases, configures layouts, connects signals,
        and displays the window with initial messages.
        """

        self.log.debug("Initializing drift scan window")
        
        try:
            self._initialize_drift_window()
            self._setup_canvases()
            self._setup_layouts()
            self._show_initial_messages()
            # self._initialize_status()
            
            self.drift_window.show()
            self.log.debug("Drift scan window displayed successfully")

            # Welcome messages
            self.write("** DRAN GUI loaded successfully.", "info")
            self.write("** Open a file to get started.", "info")

            # Set initial status (consider using a dedicated class to manage status)
            self.status = self.initial_status  # Maybe use a status class with meaningful names for flags

            # Show the window
            self.drift_window.show()

        except Exception as e:
            self.log.error(f"Failed to initialize drift window: {str(e)}")
            self.write(f"Error opening drift window: {str(e)}", "error")
            raise

    def _initialize_drift_window(self):
        """Create and configure the main drift window instance."""
        self.drift_window = QtWidgets.QMainWindow()
        self.drift_ui = Ui_DriftscanWindow()
        self.drift_ui.setupUi(self.drift_window)
        self.drift_window.setWindowTitle("Drift Scan Editor")

    def _setup_canvases(self):
        """Initialize and configure all canvas components."""
        self.canvas = CanvasManager(log=self.log)
        self.secondary_canvas = SecondaryCanvasManager(log=self.log)
        self.nav_toolbar = NavigationToolbar(self.canvas, self)

    def _setup_layouts(self):
        """Configure and populate all UI layouts."""
        layout_mapping = {
            self.drift_ui.PlotLayout: [self.nav_toolbar, self.canvas],
            self.drift_ui.otherPlotsLayout: [self.secondary_canvas]
        }
        
        for layout, widgets in layout_mapping.items():
            self._populate_layout(layout, widgets)

    def _populate_layout(self, layout, widgets):
        """Add widgets to a layout with standardized spacing."""
        # layout.setSpacing(10)
        # layout.setContentsMargins(5, 5, 5, 5)
        for widget in widgets:
            layout.addWidget(widget)

    def _show_initial_messages(self):
        """Display initial informational messages to the user."""
        welcome_messages = [
            ("** DRAN GUI loaded successfully.", "info"),
            ("** Open a file to get started.", "info")
        ]
        
        for msg, msg_type in welcome_messages:
            self.log.debug(msg, msg_type)

    def write(self, msg: str, log_type: str = "debug") -> None:
        """Write a message to both the GUI and application logs.
        
        Args:
            msg: The message text to display/log
            log_type: The message type - "info", "debug", "warning", or "error"
            
        Examples:
            >>> self.write("Operation completed", "info")
            >>> self.write("Debug value: 42")
        """

        # Validate input types
        if not isinstance(msg, str):
            raise TypeError(f"Message must be string, got {type(msg).__name__}")
        
        # Normalize log type and validate
        log_type = log_type.lower().strip()
        valid_types = {"info", "debug", "warning", "error"}
        if log_type not in valid_types:
            raise ValueError(f"Invalid log type '{log_type}'. Must be one of {valid_types}")
        
        # Map log types to appropriate handlers
        log_handlers = {
            "info": self.log.info,
            "debug": self.log.debug,
            "warning": self.log.warning,
            "error": self.log.error
        }
        
        # Get the appropriate logger function
        logger_func = log_handlers.get(log_type, self.log.debug)
        
        try:
            # Log the message
            msg_wrapper(log_type, logger_func, msg)
            
            # Also update GUI display if needed
            if hasattr(self, 'statusBar'):
                self.statusBar().showMessage(msg, 5000)  # Show for 5 seconds
                
        except Exception as e:
            # Fallback to basic logging if fancy wrapper fails
            self.log.error(f"Failed to write message: {str(e)}")
            print(f"[{log_type.upper()}] {msg}")  # Absolute fallback
            
    def connect_ui_events(self):
        """Connects all UI signals to their corresponding event handlers.
        
        Organizes connections by functional categories and provides clear debugging.
        """
        self.log.debug("Connecting UI signals to event handlers")
        
        try:
            self._connect_plot_operations()
            self._connect_data_operations()
            self._connect_database_operations()
        except Exception as e:
            self.log.error(f"Failed to connect UI events: {str(e)}")
            raise

    def _connect_plot_operations(self):
        """Connect signals for plot-related operations."""
        self.time_ui.BtnPlot.clicked.connect(self.plot_cols)
        self.time_ui.BtnViewZoomedArea.clicked.connect(self.view_zoomed_area)
        self.time_ui.BtnDeleteZoomedPoints.clicked.connect(self.delete_zoomed_area)

    def _connect_data_operations(self):
        """Connect signals for data manipulation operations."""
        self.time_ui.BtnFilter.clicked.connect(self.filter_timeseries_data)
        self.time_ui.BtnFit.clicked.connect(self.fit_timeseries)
        # self.time_ui.BtnReset.clicked.connect(self.reset_timeseries)

    def _connect_database_operations(self):
        """Connect signals for database-related operations."""
        # self.time_ui.BtnRefreshDB.clicked.connect(self.refresh_db)  # Disabled for now
        # self.time_ui.BtnSaveDB.clicked.connect(self.save_time_db)
        pass

    def _connect_point_editing(self):
        """Connect signals for point editing operations."""
        self.time_ui.BtnDelPoint.clicked.connect(self.update_point)
        self.time_ui.BtnDelBoth.clicked.connect(self.update_all_points)

    
    def fit_timeseries(self):
        """Fit the timeseries data using the selected fit method and parameters.
    
        Handles polynomial and spline fits with optional date range filtering.
        """

        print('\n***** Running fit_timeseries\n')
        
        # Validate fit parameters
        if not self._validate_fit_parameters():
            return
        
        # Get current plot data
        if not self._validate_plot_data():
            return

     


        # if fit_type == "Polynomial":
        #     # Perform polynomial fit
            
        #     xm, model, res, rma, coeffs = fit.calc_residual_and_rms_fit(x, y, int(fit_order))
        #     # ... (rest of the polynomial fit logic)

        # elif fit_type == "Spline":
        #     knots = int(self.time_ui.EdtSplKnots.text())
        #     if knots < 9:
        #         knots = 9
        #     xm, model = fit.spline_fit(x, y, knots, int(fit_order))
        #     # ... (rest of the spline fit logic)

        # # Plot the fitted model
        # self.canvas.plot_dual_fig(x, y, xm, model, 'data', 'model', 'Plot of data vs fitted model')

    def _validate_fit_parameters(self):
        """Check that valid fit type and order are selected."""
        fit_type = self.time_ui.comboBoxFitTypes.currentText()
        fit_order = self.time_ui.comboBoxOrder.currentText()
        
        if fit_order == "Order" or fit_type == "Type":
            print("Please select both a fit type and order")
            return False
        return True

    def _validate_plot_data(self):
        """Verify we have valid plot data with MJD x-axis."""
        if not self.canvas.has_data():
            print("No data available for fitting")
            return False
            
        if self.canvas.x_label != "MJD":
            print("X-axis must be MJD for fitting")
            return False
            
        return True

    def _prepare_fit_data(self):
        """Prepare and filter the data for fitting."""
        try:
            x = np.array(self.canvas.x).astype(float)
            y = np.array(self.canvas.y).astype(float)
            
            # Apply date range filtering if specified
            start_date, end_date = self._get_date_range()
            if start_date is not None or end_date is not None:
                mask = self._create_date_mask(x, start_date, end_date)
                x, y = x[mask], y[mask]
                
            return x, y
            
        except Exception as e:
            print(f"Error preparing fit data: {e}")
            return None, None
        
    def _get_date_range(self):
        """Get start and end dates from UI inputs."""
        try:
            start_date = int(self.time_ui.EdtStartDate.text()) if self.time_ui.EdtStartDate.text() else None
            end_date = int(self.time_ui.EdtEndDate.text()) if self.time_ui.EdtEndDate.text() else None
            return start_date, end_date
        except ValueError:
            print("Invalid date range - using full dataset")
            return None, None

    def _create_date_mask(self, x, start_date, end_date):
        """Create mask for date range filtering."""
        if start_date is not None and end_date is not None:
            return (x >= start_date) & (x <= end_date)
        elif start_date is not None:
            return x >= start_date
        elif end_date is not None:
            return x <= end_date
        return slice(None)  # No filtering



    def print_stats(self, df, column):
        """Prints basic statistics for the given DataFrame and specified column.
        
        Args:
            df (pd.DataFrame): Input dataframe containing the data
            option (str): Column name for which to calculate statistics
        """
        print("\n=== Statistics ===\n")
        
        try:
            # Date info
            print("Date Range:")
            print(f'Start: {df["OBSDATE"].iloc[0]} (MJD: {df["MJD"].iloc[0]:.1f})')
            print(f'End:   {df["OBSDATE"].iloc[-1]} (MJD: {df["MJD"].iloc[-1]:.1f})\n')
            
            # Column stats
            values = df[column]
            mean = values.mean()
            std = values.std()
            
            print(f"Column: {column}")
            print(f"3sigma range: ({mean - 3*std:.3f}, {mean + 3*std:.3f})")
            print(f"Min/Max: {values.min():.3f} / {values.max():.3f}")
            print(f"Mean: {mean:.3f}")
            print(f"Median: {values.median():.3f}")
            print(f"Count: {len(values)}")
            
        except KeyError as e:
            print(f"Error: Column {str(e)} not found")
        except Exception as e:
            print(f"Error calculating stats: {str(e)}")
        
        print("\n" + "-"*20)