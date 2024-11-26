# ============================================================================#
# File: timeseries_canvas.py                                                  #
# Author: Pfesesani V. van Zyl                                                #
# ============================================================================#

# Standard library imports
# --------------------------------------------------------------------------- #
import sys, os
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
#import matplotlib.style as mplstyle
#mplstyle.use('fast')
import matplotlib.pyplot as plt
import webbrowser
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.dates as mdates ## Import required library

# Local imports
# --------------------------------------------------------------------------- #
# sys.path.append("src/")
from common.msgConfiguration import msg_wrapper
sys.path.append("plots/")
# =========================================================================== #

class TimeCanvas(FigureCanvas):

    def __init__(self, parent=None, wid=10, hgt=8,dpi=100,plotName="",log=""):
        """
        Initialize an empty canvas for all plots.
        """

        if log == "":
            self.log = print
        else:
            self.log = log

        self.previous_point=[]

        # Create a figure object
        fig = Figure(figsize=(wid, hgt), facecolor='w', edgecolor='k',dpi=dpi)

        # A canvas must be manually attached to the figure (pyplot would automatically
        # do it).  This is done by instantiating the canvas with the figure as
        # argument.
        # Create an axes object in the figure
        self.ax = fig.add_subplot(111)
        
        # Initialize the figure onto the canvas
        FigureCanvas.__init__(self, fig)
        self.fig=fig

        self.setParent(parent)

        # Setup clicks array to hold selected positions
        self.reset_lists()

        # set x,y
        self.x=[]
        self.y=[]
        self.xlab=[]
        self.ylab=[]
        
    def reset_lists(self):
        """
        Setup lists to store data for the click_index and fit_points.
        click_index : the indeces of the points clicked on the figure.
        fit_points: the values of the click_index
        """

        msg_wrapper("debug", self.log.debug,
                    "Reset fit points")
        self.click_index = []   # Indeces of clicked points along x-axis
        self.fit_points = []    # Points to be fit/modelled

    def plot_fig_errs(self, x=[], y=[], xlab="", ylab="", title="Main database plot window", col="C0.", errs=[],data=""):
        """
        Plot a figure with errorbars.
       
            A helper function to make a graph

            Parameters
            ----------
            ax : Axes
                The axes to draw to

            data1 : array
            The x data

            data2 : array
            The y data

            param_dict : dict
            Dictionary of kwargs to pass to ax.plot

            Returns
            -------
            out : list
                list of artists added
        """

        self.data=data # drift scan data

        if len(x) == 0:
            self.clear_figure()
            self.setLabelsNoLegend(self.ax, title)

        else:
            
            self.clear_figure()
            plt.xticks(rotation=70)
            self.x=x
            self.y=y
            self.xlab=xlab
            self.ylab=ylab
            self.ax.errorbar(x, y, yerr=errs,fmt=col, label="data", picker=5)
            self.setLabels(self.ax, xlab, ylab, title)
            self.mpl_connect('pick_event', self.onpick)

        self.draw()
    
    def replaceitem(self,x):
        '''replace an item in a list of items'''

        if x == None:
            return np.nan
        elif x == 'None':
            return np.nan
        elif x == 'NaT':
            return np.nan
        elif x =='':
            return np.nan
        else:
            return float(x)
        
    def replaceDateItem(self,x):
        '''replace an item in a list of items'''

        if type(x).__name__ == 'NaTType':
            # print('*',x)
            return np.nan
        elif x == 'None':
            # print('%',x)
            return np.nan
        elif x == 'NaT':
            # print('+',x)
            return np.nan
        else:
            # print('&',x)
            return float(x)
    
    
    def plot_fig(self, x=[], y=[], xlab="", ylab="", title="Main database plot window", col="C0.", data="",yerr=[]):
        # plot_fig(self.df[xCol],self.df[yCol],xCol,yCol,data=self.df,yerr=yerr)
        """
        Plot a figure.
       
            A helper function to make a graph

            Parameters
            ----------
            ax : Axes
                The axes to draw to

            data1 : array
            The x data

            data2 : array
            The y data

            param_dict : dict
            Dictionary of kwargs to pass to ax.plot

            Returns
            -------
            out : list
                list of artists added
        """

        # self.x
        self.data=data # drift scan data

        # print(type(x))
        # sys.exit()

        if len(x) == 0:
            self.clear_figure()
            self.setLabelsNoLegend(self.ax, title)

        else:
            
            self.clear_figure()
            plt.xticks(rotation=45)
            self.x=x
            self.y=y
            self.xlab=xlab
            self.ylab=ylab
           
            # print(yerr)
            # print(self.y)
            if len(yerr)==0 or str(yerr)=='None':
                self.ax.plot(self.x, self.y, col, label="data", picker=5)
            else:
                self.ax.errorbar(self.x, self.y, yerr,fmt=col, label="data", picker=5)

            self.setLabels(self.ax, xlab, ylab, title)

            if xlab=='OBSDATE':
                months = mdates.MonthLocator(bymonth=(1,7))#interval=6, bymonthday=-1)  ## 6 months apart & show last date
                self.ax.xaxis.set_major_locator(months) ## Set months as major locator
                self.ax.xaxis.set_minor_locator(mdates.MonthLocator()) 

            # TODO: create a button to toggle grid on/off
            # TODO: create button to change grid color, line width etc
            # TODO: Button to toggle step change locations on/off
            self.ax.grid(True,alpha=0.2)

            connection_id_0=self.mpl_connect('pick_event', self.onpick)
            connection_id = self.mpl_connect('button_press_event', self.onclick)
            #self.mpl_connect('pick_event', self.onpick)

            # rotate ticks
            self.fig.autofmt_xdate()
            self.fig.tight_layout()
            self.draw()
        self.draw()

    def plot_dual_fig(self, x=[], y=[],x1=[],y1=[], xlab="", ylab="", title="Main database plot window", col="C0.", data=""):
        """
        Plot a figure.
       
            A helper function to make a graph

            Parameters
            ----------
            ax : Axes
                The axes to draw to

            data1 : array
            The x data

            data2 : array
            The y data

            param_dict : dict
            Dictionary of kwargs to pass to ax.plot

            Returns
            -------
            out : list
                list of artists added
        """

        self.data=data # drift scan data

        if len(x) == 0:
            self.clear_figure()
            self.setLabelsNoLegend(self.ax, title)

        else:
            
            self.clear_figure()
            plt.xticks(rotation=45)
            self.x=x
            self.y=y
            self.xlab=xlab
            self.ylab=ylab
            self.ax.plot(x, y, col, label="data", picker=5)
            self.ax.plot(x1, y1, 'r', label="fit")
            self.setLabels(self.ax, xlab, ylab, title)
            #connection_id_0=self.mpl_connect('pick_event', self.onpick)
            #connection_id = self.mpl_connect('button_press_event', self.onclick)
            
            #self.mpl_connect('pick_event', self.onpick)

        self.draw()

    def clear_figure(self):
        """
            Clear the current figure 
        """
        self.ax.cla()  # .gcf().clear()  # which clears data and axes
        self.draw()

    def onclick(self,event):

        #print(event, "\n")
        
        if event.xdata==None:
            print('\nNothing selected, aim for the tiny blue dots ;)\n')
        else:

            #print(len(self.fit_points))

            if len(self.fit_points) == 0 or len(self.click_index) == 0:
                print("\nNo points selected, try aiming for the tiny blue dots\n")
            else:
                print("in\n")
                if len(self.click_index) == 1 and  len(self.fit_points) == 1:
                    print(f'Clicked the {event.button} button')
                    
                    if event.dblclick:
                        print('double clicked - ')
                        print(self.click_index)

                        print(f'Clicked: {event.button}\n')
                        print(f'x: {self.fit_points[0][0]}, \ny: {self.fit_points[0][1]}')
                        print('ind: ',self.click_index,'\n')

                    elif event.button == 1 or event.button == "MouseButton.LEFT":
                        print(self.previous_point, self.fit_points[0][0], self.fit_points[0][1])

                        if len(self.previous_point)==1:
                            print('test')
                            print(self.previous_point[0][0]==self.fit_points[0][0], self.previous_point[0][1]==self.fit_points[0][1])
                            cond=(self.previous_point[0][0]==self.fit_points[0][0]) 
                            if cond == True:
                                print('\naim for blue dots\n')
                                self.fit_points=[]
                                self.click_index=[]
                            else:
                                print('left - ')
                                #self.fitpoints=[]
                                #self.click_index=[]
                                print(f'Clicked: {event.button}\n')
                                print(f'x: {self.fit_points[0][0]}, \ny: {self.fit_points[0][1]}')
                                print('ind: ',self.click_index,'\n')
                                self.previous_point=[[self.fit_points[0][0],self.fit_points[0][1]]]
                        else:
                            #self.previous_point=[[self.fit_points[0][0],self.fit_points[0][1]]]
                            print('left - first time')
                            #self.fitpoints=[]
                            #self.click_index=[]
                            print(f'Clicked: {event.button}\n')
                            print(f'x: {self.fit_points[0][0]}, \ny: {self.fit_points[0][1]}')
                            print('ind: ',self.click_index,'\n')
                            self.previous_point=[[self.fit_points[0][0],self.fit_points[0][1]]]

                    elif event.button == 3:
                        if self.click_index==[]:
                            print('No click index')
                        else:
                            print(f'Clicked: {event.button}\n')
                            
                            # Points clicked to plot
                            self.ax.plot(self.fit_points[0][0], self.fit_points[0][1], 'r.')
                            if len(self.click_index)==1:
                                self.show_plots(self.click_index[0])
                            else:
                                self.show_plots(self.click_index[-1])
                            #sys.exit()

                    else:
                        print("Not sure what happend\n")
                else:
                    print('click index: ',len(self.click_index),self.click_index)

    def onpick(self, event):
        """ Click event handler."""

        if isinstance(event.artist, Line2D):
            thisline = event.artist
            xdata,ydata = thisline.get_xdata(), thisline.get_ydata()
            
            ind = event.ind

            pointsx = xdata[ind]
            pointsy = ydata[ind]

            try:
                print("\n","-"*30)
                print(f'picked: {str(pointsx[0])[:10]},{pointsy[0]} @ index: {ind[0]}')
            except (IndexError, TypeError):
                print("Error: Could not process the clicked point.")

            self.fit_points=[]
            self.click_index=[]

            self.fit_points.append([pointsx[0],pointsy[0]])
            self.click_index.append(ind[0])
            self.draw()

    def show_plots(self, index):
        """ Show plots on click event in a web browser. """

        self.data['CENTFREQ'] = self.data['CENTFREQ'].astype(float)
        data = self.data.iloc[index]
        source_name = data["OBJECT"].replace(" ", "")
        central_frequency = int(data["CENTFREQ"])
        file_name = data["FILENAME"]
        observation_date = str(data["OBSDATE"])[:10]

        # Check for image directory
        img_dir = f"plots/{source_name}/{central_frequency}"
        if not os.path.exists(img_dir):
            print(f"Missing images for {source_name}. Try processing data first.")
            return

        # Get image names (filtered by file name prefix)
        image_names = [
            name for name in sorted(os.listdir(img_dir)) if name.startswith(file_name[:18])
        ]

        if not image_names:
            print(f"No matching images found for {file_name}.")
            return

        # Build HTML content
        html_start = f"""<html>
    <head>
     <meta charset = "utf-8" >
    <meta name = "viewport" content = "width=device-width, initial-scale=1" > <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-BmbxuPwQa2lc/FVzBcNJ7UAyJxM6wuqIj61tLrc4wSX0szH/Ev+nYRRuWlolflfl" crossorigin="anonymous"> <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta2/dist/js/bootstrap.bundle.min.js" integrity="sha384-b5kHyXgcpbZJO/tY9Ul7kGkf1S0CWuKcCD38l8YkeH8z8QjE0GmW1gYU5S9FOnJ0" crossorigin="anonymous"></script> \
                """+"""<style> img {border: 2px solid  #ddd; /* Gray border */border-radius: 4px;  /* Rounded border */padding: 5px; /* Some padding */width: 400px; /* Set a small width */}/* Add a hover effect (blue shadow) */img:hover {box-shadow: 0 0 2px 1px rgba(0, 140, 186, 0.5);}</style> """+f"""
    <title>Plots</title>
    </head>
    <body>
    <div class="container-fluid">
        <div class="row">
        <hr>
            <h4> Plots of obs '{file_name[:18]}' (MJD {data['MJD']:.1f} or {observation_date}) for {source_name} at {central_frequency} MHz </h4>
    """
        html_mid = ""
        for image_name in image_names:
            img_path = os.path.join(img_dir, image_name)
            img_tag = image_name[19:-4]  # Extract image tag from filename

            html_mid += f"""<div class="card" style="width: 18rem;">
            <h5 class="card-title">{img_tag}</h5>
            <br/>
            <a target="_blank" href="{img_path}"><img src="{img_path}" class="card-img-top" alt="image goes here"></a>
            </div>"""

        html_end = "</body></html>"

        html = html_start + html_mid + html_end

        # Create and open the HTML file
        path = os.path.abspath("temp.html")
        url = f"file://{path}"

        with open(path, "w") as f:
            f.write(html)
        webbrowser.open(url)
        








#---------------------------------------------------------------------------

    def pop(self):
        """
        """
        print("Ask to remove: ", self.img_loc[self.click_index[-1]])
        #img = Image.open("plots/"+self.img_loc[self.click_index[-1]])
        #plt.imshow(img)

        # show image of plot
        #pl.plot()

        #fig = Figure(figsize=(100, 100), facecolor='w', edgecolor='k')

        # A canvas must be manually attached to the figure (pyplot would automatically
        # do it).  This is done by instantiating the canvas with the figure as
        # argument.
        # Create an axes object in the figure
        #ax = fig.add_subplot(111)
        #app = QApplication(sys.argv)

        #sys.exit(app.exec_())

        #img = Image.open("plots/"+self.img_loc[self.click_index[-1]])
        #plt.imshow(img)
        # Initialize the figure onto the canvas

        #self.toolbar = NavigationToolbar(self,fig)

    def dday(self, x, y):
        """
        Date handler
        """

        #d1 = x[0]
        #d2 = x[-1]

        #print(d1,d2)
        #string = d1#"19 Nov 2015  18:45:00.000"

        #date = datetime.datetime.strptime(string, "%Y-%m-%d")# %H:%M:%S.%f")
        #print(date, date.year, date.month, date.day)

        #sys.exit()
        #date1 = datetime.date(2002, 1, 5)
        #date2 = datetime.date(2003, 12, 1)

        # every monday
        mondays = WeekdayLocator(MONDAY)

        # every 3rd month
        months = MonthLocator(range(1, 13), bymonthday=1, interval=3)
        monthsFmt = DateFormatter("%b '%y")

        dates = x#[q[0] for q in quotes]
        opens = y#[q[1] for q in quotes]

        self.clear_figure()
        #fig, ax = plt.subplots()
        self.ax.plot_date(dates, opens, '-')
        self.ax.xaxis.set_major_locator(months)
        self.ax.xaxis.set_major_formatter(monthsFmt)
        self.ax.xaxis.set_minor_locator(mondays)
        self.ax.autoscale_view()
        #ax.xaxis.grid(False, 'major')
        #ax.xaxis.grid(True, 'minor')
        #ax.grid(True)

        #self.fig.autofmt_xdate()

        #plt.show()
        self.draw()

    def setLabelsNoLegend(self, ax, title="My title"):
        """
        Set labels for basic plot.
        """

        ax.set_title(title, fontsize='x-large')  # pad=3
        ax.set_ylabel("Y-axis", fontsize="medium")
        ax.set_xlabel("X-axis", fontsize="medium")

    def setLabels(self, ax, xlab, ylab,title="My title"):
        """
        Set labels for basic plot.
        """

        ax.set_title(title, fontsize='x-large')  # pad=3
        ax.set_ylabel(ylab, fontsize="medium")
        ax.set_xlabel(xlab, fontsize="medium")
        ax.legend(loc="best", fontsize="small", fancybox=True, framealpha=0.5)

#if __name__ == '__main__':
    
    '''def plotRawData(self, x=[], y=[]):
        """
        Plot raw data
        """

        #zero = np.zeros(len(x))
        if len(x) == 0:
            pass
        else:
            self.clear_figure(self.ax2)
            self.ax2.plot(x, y, 'k', label="Raw data")
            #plotRawplotRawDataself.ax2.plot(x, zero, 'c')
            self.ax2.legend(loc="best")
            self.ax2.set_xlabel("Dist [deg]")
            self.draw()

    def resetLists(self):
        """
        Setup lists to store the following data of: 
        """
        self.click_index = []   # Indeces of picked points along x-axis
        self.fit_points = []   # Points to be fit/modelled

    def plotRes(self, x=[], title="Residuals"):
        """
        Plot the residuals
        """

        self.clear_figure(self.ax1)

        if len(x) == 0:

            self.ax1.set_title(title)
        else:
            pass

            # get resid min/max
            res_min = max(x)
            res_max = min(x)
            res_mean = np.mean(x)
            sd = 3*np.std(x)
            res_3sdmax = res_mean + sd
            res_3sdmin = res_mean - sd

            sdd = np.zeros_like(x)
            sdmx = np.ones_like(x)*res_3sdmax
            sdmn = np.ones_like(x)*res_3sdmin

            # label="res mean +- 3 std"
            self.ax1.plot(sdd, sdmx)  # , fontsize="medium")
            self.ax1.plot(sdd, sdmn)

        self.ax1.plot(x)
        self.ax1.set_xlabel("N", fontsize="medium")
        self.ax1.set_ylabel("res", fontsize="medium")
        self.draw()

    def plotBaseLocs(self, ax, left_locs, right_locs, x, y):
        """
        Add baseline correction locations
        """
        ax.plot(x[left_locs], y[left_locs], "m.")
        ax.plot(x[right_locs], y[right_locs], "m.")
        self.draw()

    def addLineToAxis(self, ax, x, y, lab):
        """
        Add data to axis
        """
        #if t=="--":
        #    ax.plot(x,y,c="b", label=lab)
        #    ax.legend(loc="best")
        #    self.draw()
        #else:
        ax.plot(x, y, 'm.', label=lab, lw=1)
        ax.legend(loc="best")
        self.draw()

#==========================================================

    def setLegendParms(self):
        """
        Legend parameters.
        """

        legend_parms_fontsize = ['xx-small', 'x-small',
                                 'small', 'medium', 'large', 'x-large', 'xx-large']
        legend_parms_loc = ['best', 'upper right', 'upper left', 'lower left',
                            'lower right', 'right', 'center left', 'center right', 'lower center', 'center']
        _facecolor = []
        _edgecolor = []
        _title = []
        _title_fontsize = []
        #from matplotlib import rcParams
        #rcParams['axes.titlepad'] = 20

    def setMainFigurecustomization(self):
        """
        Customize the main figure look.
        """

        pass
        """plt.rc('font', family = 'serif')
        plt.rc('legend', fontsize='small')
        plt.rc('xtick', color='red', labelsize = 'x-small')
        plt.rc('xtick', color='r', labelsize='medium', direction='out')
        plt.rc('xtick.major', size=4, pad=4)
        plt.rc('xtick.minor', size=2, pad=4)"""
        #xtick.major.size     : 4      # major tick size in points
        #xtick.minor.size     : 2      # minor tick size in points
        #xtick.major.pad      : 4      # distance to major tick label in points
        #xtick.minor.pad      : 4      # distance to the minor tick label in points
        #xtick.color          : r      # color of the tick labels
        #xtick.labelsize      : medium # fontsize of the tick labels
        #xtick.direction      : out     # direction: in or out
        #plt.rcdefaults # To reset rc parameters

    def setResidualFigurecustomization(self):
        """
        Customize the residual figure look.
        """

        pass

    def setTimeseriesFigurecustomization(self):
        """
        Customize the residual figure look.
        """

        pass

    def setTicks(self):
        """
        Set tick properties for the figure.
        """

        for tick in self.ax.xaxis.get_ticklabels():
            tick.set_fontsize('medium')
            tick.set_fontname('serif')  # Times New Roman')
            tick.set_color('blue')
            tick.set_weight('bold')

    def plotPeak(self, xp, yp, x=[], y=[], title="Basic plot window"):

        self.fit_points = []    # List of points selected for fitting
        self.click_index = []   # List of Index of point selected for fitting

        if len(x) == 0:
            print("\n-- This plot has no data")
            #data = [random.random() for i in range(25)]
            #self.ax.plot(data, 'b')
        else:
            self.ax.plot(x, y, 'b', label="data", picker=1)
            self.ax.plot(xp, yp, 'r', label='fit')
            #

        self.ax.set_title(title)
        self.ax.set_ylabel("Ta [K]")
        self.ax.set_xlabel("Dist [Deg]")
        self.ax.legend(loc="best")
        #Cursor(self.ax, useblit=True, color='red', linewidth=1)
        #self.mpl_connect('pick_event', self.onpick1)
        self.draw()

    def plotNoPick(self, ax, res):
        """
        Plot the residual.
        """

        #ax.set_ylabel("Res")
        #ax.set_xlabel("N")
        ax.plot(res)
        ax.draw()'''
