import matplotlib.pylab as plt
# from dataclasses import dataclass, field
import numpy as np
import sys
from matplotlib.widgets import Button

def plot_scan(x,y,plotLab,title,saveTo,xlab='Scandist [deg]',ylab="T$_{A}$ [K]"):
        """Plot the drift scan """
        
        fig,axes=plt.subplots(1,1, dpi=100, figsize=(13,5))
        plt.plot(x,y,label=plotLab)
        plt.axhline(0,color='k',label='y=0 line',ls='--')
        plt.legend()
        plt.xlabel(xlab)
        plt.ylabel(ylab)
        plt.title(title)
        plt.savefig(saveTo)
        # plt.show()
        plt.close()
        # sys.exit()

def plot_no_fit(x,y,title,subtitle, saveTo, label="", xlabel="", ylabel=""):
        """ Plot corrupted data."""
        # fig,axes=plt.subplots(1,1, dpi=100, figsize=(13,8))
        plt.suptitle(title, fontsize=15)
        plt.title(subtitle, fontsize=12)

        if xlabel == "":
            plt.xlabel("Scandist [deg]")
        else:
            plt.xlabel(xlabel)

        if ylabel == "":
            plt.ylabel("T$_{A}$ [K]")
        else:
            plt.ylabel(ylabel)

        plt.plot(x, y, 'r', label=label)
        plt.legend(loc="best")
        plt.savefig(saveTo)
        plt.close('all')

def plot_overlap(x1,y1,x2,y2,title,plotLab1,plotLab2,saveTo,xlabel="",ylabel=""):
        """Overplot 2 scans """

        fig,axes=plt.subplots(1,1, dpi=100, figsize=(13,5))
        plt.plot(x1,y1,label=plotLab1)
        plt.plot(x2,y2,label=plotLab2)
        plt.axhline(0,color='k',label='y=0 line',ls='--')
        plt.legend()
        if xlabel == "":
            plt.xlabel("Scandist [deg]")
        else:
            plt.xlabel(xlabel)

        if ylabel == "":
            plt.ylabel("T$_{A}$ [K]")
        else:
            plt.ylabel(ylabel)
        plt.title(title)
        plt.savefig(saveTo)
        # plt.show()
        plt.close()
        # sys.exit()

def make_plot(plotlab):
        """plot data from plotting ionary"""

        fig,axes=plt.subplots(1,1, dpi=100, figsize=(13,5))
        plt.plot('x','y',label='pol')
        plt.axhline(0,color='k',label='y=0 line',ls='--')
        plt.legend()
        plt.xlabel('xlab')
        plt.ylabel('ylab')
        plt.title('title')
        plt.show()
        plt.close()
        sys.exit()

def make_qv_plots(lcp,rcp):

        # make plots of all scans

        if "north_scan" in list(lcp.keys()):
            scans=[lcp['offset'],rcp['offset'],lcp['north_scan'],lcp['centre_scan'],lcp['south_scan'],rcp['north_scan'],rcp['centre_scan'],rcp['south_scan']]
            scanNames=['lcp offset','rcp offset','LCP North scan','LCP Center scan','LCP South scan','RCP North scan','RCP Center scan','RCP South scan']
            
            plt.figure(figsize=(20,10))

            for i in range(1,7):
                plt.subplot(2,3,i)
                plt.ylabel('Ta [K]')
                plt.xlabel('Offset [deg]')
                if 'LCP' in scanNames[i+1]:
                    plt.plot(scans[0],scans[i+1])
                else:
                    plt.plot(scans[1],scans[i+1])
                plt.title(f'plot of {scanNames[i+1]}')
            plt.tight_layout()
            plt.savefig(f'quickview_{lcp["source"]}_{int(lcp["nu"])}-{lcp["file"]}.png')
            #plt.show()
            plt.close()
        else:
            scans=[lcp['offset'],rcp['offset'],lcp['centre_scan'],rcp['centre_scan']]
            scanNames=['lcp offset','rcp offset','LCP Center scan','RCP Center scan']
            
            plt.figure(figsize=(10,3))
            for i in range(1,3):
                plt.subplot(1,2,i)
                plt.ylabel('Ta [K]')
                plt.xlabel('Offset [deg]')
                if 'LCP' in scanNames[i+1]:
                    plt.plot(scans[0],scans[i+1])
                else:
                    plt.plot(scans[1],scans[i+1])
                plt.title(f'plot of {scanNames[i+1]}')
            plt.tight_layout()
            plt.savefig(f'quickview_{lcp["source"]}_{int(lcp["nu"])}-{lcp["file"]}.png')
            plt.show()
            plt.close()

def fit_plot():
        pass
  
def plotBaselineEstimate(x,y,yspl,posLeft,posRight,lab1,lab2,title,saveTo,lb=[],rb=[],xlabel='',ylabel=''):
    """
    Plot the positions or locations of the baseline local minimum estimate.

    Args:
        x (list/array): x-axis data
        y (list/array): y-axis data
        yspl (list/array): splined y-axis data
        posLeft (int): index of the local min to the left of the central peak
        posRight (int): index of the local min to the right of the central peak
        lab1 (str): label of posLeft
        lab2 (str): label of posRight
        title (str): title of plot
        saveTo (str): saving location
    """
    plt.title(title)
    plt.plot(x, y)
    plt.plot(x, yspl)
    # print(lb)
    # print(rb,len(x),len(y))
    # print(x)
    # print(y)
    lb=np.array(lb,int)
    rb=np.array(rb,int)
    x=np.array(x,float)
    y=np.array(y,float)
    yspl=np.array(yspl,float)
    if len(lb)>0:
        plt.plot(x[lb], y[lb], 'r.')
        plt.plot(x[rb], y[rb], 'r.')
    plt.plot(x[posLeft], yspl[posLeft], 'k*', label=lab1)
    plt.plot(x[posRight], yspl[posRight], 'y*',label=lab2)
    plt.legend(loc='best')

    if xlabel == "":
        plt.xlabel("Scandist [deg]")
    else:
        plt.xlabel(xlabel)

    if ylabel == "":
        plt.ylabel("T$_{A}$ [K]")
    else:
        plt.ylabel(ylabel)

    try:
        plt.savefig(saveTo)
    except:
        pass
    plt.close('all')

def plotCorrectedData(x,ycorr,posLeft,posRight,lab1,lab2,title,saveTo,xlabel="",ylabel=""):
    """
    Plot corrected data.

    Args:
        x (list/array): x-axis data
        y (list/array): y-axis data
        ycorr (list/array): corrected y-axis data
        posLeft (int): local mins to the left of the central peak
        posRight (int): local mins to the right of the central peak
        lab1 (str): label of raw data
        lab2 (str): label of corrected data
        title (str): title of plot
        saveTo (str): saving location
    """
    plt.title(title)
    plt.plot(x, ycorr, label=lab1)
    plt.plot(x[posLeft], ycorr[posLeft], 'y.',label=lab2)
    plt.plot(x[posRight], ycorr[posRight], 'y.')
    plt.plot(x,np.zeros_like(x),'k--')#,label='')
    plt.legend(loc='best')

    if xlabel == "":
        plt.xlabel("Scandist [deg]")
    else:
        plt.xlabel(xlabel)

    if ylabel == "":
        plt.ylabel("T$_{A}$ [K]")
    else:
        plt.ylabel(ylabel)

    try:
        plt.savefig(saveTo)
    except:
        pass
    plt.close('all')

def plotPeakFit(title,x,ycorr,ypeak,err_peak,peak_beam,saveTo,xlabel="",ylabel=""):
    """
    _summary_

    Args:
        title (_type_): _description_
        x (_type_): _description_
        ycorr (_type_): _description_
        ypeak (_type_): _description_
        err_peak (_type_): _description_
        peak_beam (_type_): _description_
        saveTo (_type_): _description_
        xlabel (str, optional): _description_. Defaults to "".
        ylabel (str, optional): _description_. Defaults to "".
    """
    plt.title(title)
    plt.plot(x, ycorr, "k", label="corrected data")
    plt.plot(x[peak_beam], ycorr[peak_beam])
    plt.plot(x[peak_beam], ypeak,"r",label="T$_{A}$ [K]" +f" = {max(ypeak):.3f} +- {err_peak:.3f}")
    plt.plot(x,np.zeros(len(x)),"c--",alpha=0.5)
    plt.legend(loc="best")
    
    if xlabel == "":
        plt.xlabel("Scandist [deg]")
    else:
        plt.xlabel(xlabel)

    if ylabel == "":
        plt.ylabel("T$_{A}$ [K]")
    else:
        plt.ylabel(ylabel)

    try:
        plt.savefig(saveTo)
    except:
        pass
    plt.close()

def plotDualBeamFit(x1,y1,x2,y2,x3,y3,title,plotLab1,plotLab2,plotLab3,saveTo,xlabel="",ylabel=""):
        """Plot dual beam scan """

        fig,axes=plt.subplots(1,1, dpi=100)#, figsize=(13,5))
        plt.plot(x1,y1,label=plotLab1)
        plt.plot(x2,y2,label=plotLab2)
        plt.plot(x3,y3,label=plotLab3)
        plt.axhline(0,color='k',label='y=0 line',ls='--')
        plt.legend()
        if xlabel == "":
            plt.xlabel("Scandist [deg]")
        else:
            plt.xlabel(xlabel)

        if ylabel == "":
            plt.ylabel("T$_{A}$ [K]")
        else:
            plt.ylabel(ylabel)
        plt.title(title)
        plt.savefig(saveTo)
        # plt.show()
        plt.close()
        # sys.exit()
