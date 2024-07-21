import matplotlib.pylab as plt
# import matplotlib
# matplotlib.use('qtagg')

from dataclasses import dataclass, field
import numpy as np
import sys,os
from .msgConfiguration import msg_wrapper
from .miscellaneousFunctions import check_for_nans, sig_to_noise
from .fitting import clean_rfi, fit_dual_beam, fit_beam # fit_gauss_lin
from .plotting import plot_no_fit, plot_scan, plot_overlap, plotPeakFit,plotDualBeamFit
# from scipy.optimize import curve_fit
# from .prepScans import PrepareScans
import logging
logging.getLogger('matplotlib.font_manager').disabled = True

# import warnings
# def fxn():
#     warnings.warn("deprecated", DeprecationWarning)
# with warnings.catch_warnings(action="ignore"):
#     fxn()

@dataclass
class DataProcessingFlowManager:
    fileName:str #= ""
    freq:float #= np.nan
    src:str #= ""
    x:np.array #= np.zeros_like(1000)
    y:np.array #= np.zeros_like(1000)
    log:object
    flag:int
    applyRFIremoval:str
    savefolder:str
    srcTag:str
    pol:str
    frontend:str
    HPBW:float
    FNBW:float
    theoFit:str
    autoFit:str  # run an automated fit on pre-selected baseline locations
    force:str = 'n' # force a fit on the data or not, initially set to no
    # fileName,frq,src,x,lcp,log,0,'y',saveTo,'HPN_LCP','LCP',frontend,hpbw,fnbw


    def __post_init__(self):

        print('\n')
        print('#'*80)
        msg_wrapper("info", self.log.info, "PROCESSING/FITTING DRIFTSCAN INITIATED")
        print('#'*80)
        print('\n')

        saveTo='currentScanPlots'
        plotSavePath=f'plots/{self.src}/{int(self.freq)}'
        ext='.png'
        self.plotName=self.fileName[:18]
        self.plotPath = f"{plotSavePath}/{self.plotName}_{self.srcTag+ext}"
        # create_current_scan_directory()

        # 1. check data for nans
        # ========================
        self.y, self.flag=check_for_nans(self.y,self.log)
        # plot=ScanPlot(self.src,self.x,self.y,self.flag,self.log) 

        if self.flag == 1:
            msg="Flag 1: Found nans"
            plot_no_fit(self.x, self.y, "Plot of fitting error: No data","", self.plotPath, msg, xlabel="", ylabel="")
            
            if "D" in self.frontend:
                ret= {"correctedData":[],"driftRes":[],"driftRms":np.nan,
                        "driftCoeffs":[], "baseLocsCombined":[],
                        "baseLocsLeft":[],"baseLocsRight":[],
                    "leftPeakData":[],"leftPeakModelData":[],
                    "leftPeakFit":np.nan, "leftPeakFitErr":np.nan,"leftPeakFitRes":[],
                    "rightPeakData":[],"rightPeakModelData":[],
                    "rightPeakFit":np.nan, "rightPeakFitErr":np.nan,"rightPeakFitRes":[],
                    "msg":msg,"midXValueLeft":np.nan,"midXValueRight":np.nan
                    }
                ret['flag']=2
                self.__dict__[self.srcTag]=ret
                return
            else:
                ret={
                # "peakFit":np.nan,"peakModel":[], "peakRms":np.nan,"correctedData":[],"peakPts":[],
                # "msg":"","driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,
                # "flag":1,"baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":[],
                # "baseLeft":[],"baseRight":[],'s2n':np.nan}
                "peakFit":np.nan,"peakModel":[], "peakRms":np.nan,"correctedData":[],"peakPts":[],
                "msg":"","driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,
                "flag":1,"baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":[],
                "baseLeft":[],"baseRight":[],'s2n':np.nan}
                ret['flag']=1
                self.__dict__[self.srcTag]=ret
                return
                # sys.exit()
            
        else:
            # 2. Clean the data, remove RFI
            # ===============================
            # RFI can make fitting a drift scan imossible, this is why as 
            # part of the cleaning process we eliminate or remove any data
            # that is an outlier, surpassing all other data points by more than
            # 3 times the rms.

            # clean the data of RFI contamination
            self.clean_data()

            # make initial processing plots
            # make plots of the current scan for source overview
            # ----------------------------------------------------------------------
            tag=self.srcTag
            tagCleaned=self.srcTag+"Cleaned"
            src=self.src
            freq=int(self.freq)
            title=f"Plot of {self.src} file {self.fileName} {self.srcTag}"
  
            msg_wrapper("debug", self.log.debug, "\n")
            msg_wrapper("info", self.log.info, f'Plot path: {self.plotPath}')
            msg_wrapper("debug", self.log.debug, "\n")

            # plot raw data
            rawPath=f'{saveTo}/{self.plotName}_{tag}_raw.png'
            msg_wrapper("debug", self.log.debug, f'Plot {tag} raw data: {rawPath}')
            plot_scan(self.x, self.y,tag,f'Plot of {tag} raw data',rawPath)

            # plot cleaned data
            cleanPath=f'{saveTo}/{self.plotName}_{tag}_clean.png'
            msg_wrapper("debug", self.log.debug, f'Plot {tag} clean data: {cleanPath}')
            plot_scan(self.xCleaned, self.yCleaned,tag,f'Plot of {tag} clean data',cleanPath)

            # plot raw and cleaned data
            overlapPath=f'{saveTo}/{self.plotName}_{tag}_overlap.png'
            msg_wrapper("debug", self.log.debug, f'Plot {tag} overlap data: {overlapPath}')
            plot_overlap(self.x, self.y,self.xCleaned,self.yCleaned,'Plot of overlap data',"Raw",'Clean',overlapPath)

            
            # 3. Check rms for error handling of bad data
            # ============================================
            if self.RMSA >= 1.0:
                msg="RMS >= 1.0"
                self.flag = 2
                

                title=f"Plot of {self.src} file {self.fileName}"
                subtitle= "(Flag "+str(self.flag)+": High rms > 1)"
                msg_wrapper("warning", self.log.warning, msg)
                plot_no_fit(self.xCleaned, self.yCleaned, title,subtitle,self.plotPath ,self.srcTag)
                # print("High rms")

                if "D" in self.frontend:
                    ret= {"correctedData":[],"driftRes":[],"driftRms":np.nan,
                        "driftCoeffs":[], "baseLocsCombined":[],
                        "baseLocsLeft":[],"baseLocsRight":[],
                    "leftPeakData":[],"leftPeakModelData":[],
                    "leftPeakFit":np.nan, "leftPeakFitErr":np.nan,"leftPeakFitRes":[],
                    "rightPeakData":[],"rightPeakModelData":[],
                    "rightPeakFit":np.nan, "rightPeakFitErr":np.nan,"rightPeakFitRes":[],
                    "msg":msg,"midXValueLeft":np.nan,"midXValueRight":np.nan
                    }
                    ret['flag']=2
                    self.__dict__[self.srcTag]=ret
                    return
                else:
                    ret={
                        "peakFit":np.nan,"peakModel":[], "peakRms":np.nan,"correctedData":[],"peakPts":[],
                        "msg":"","driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,
                        "flag":1,"baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":[],
                        "baseLeft":[],"baseRight":[],'s2n':np.nan}
                    ret['flag']=2
                    self.__dict__[self.srcTag]=ret
                    return
                    # sys.exit()

            else:

                # 4. Correct baseline and Create a new data set with no drift
                # =============================================================
                if 'S' in self.frontend:
                    # sys.exit()

                    # fit the data using a gaussian
                    # set initial parameters for data fitting
                    p0 = [max(self.yCleaned), np.mean(self.xCleaned), self.HPBW, .01, .0]
                    # self.peakFit, self.peakModel, self.peakRms, yCorrected, peakPts, msg, \
                    #     self.driftRes, self.driftRms, self.driftCoeffs, self.fitRes, self.mid, \
                    #     self.flag,  self.baseLeft, self.baseRight, self.base, self.peakLoc, \
                    #     self.lb,self.rb = 
                    saveTag=f'{saveTo}/{self.plotName}_{tag}_'
                    #fit_beam(x, y, p, fnbw, force, log, saveTag, fitTheoretical, autoFit=None)
                    # print(self.autoFit)
                    # sys.exit()
                    ret = fit_beam(self.xCleaned, self.yCleaned, p0, self.FNBW, self.force, self.log, saveTag, self.theoFit['value'], self.autoFit['value'])

                    # print(len(ret['correctedData'])>1)
                    print(ret.keys())
                    # sys.exit()
                    if len(ret['correctedData'])>1:
                        if max(ret['peakModel']) < 0:
                            # self.flag=12
                            ret['flag']=12
                            saveTo=f'{plotSavePath}/{self.plotName}_{self.srcTag}{ext}'
                            plot_no_fit(self.x, self.y, "Plot of fitting error: Peak max < 0","", saveTo, 'Peak max < 0', xlabel="", ylabel="")
                            # ret['s2n']=np.nan
                            # print(ret)
                            sys.exit()

                        elif ret['peakRms'] > 1.:
                            # self.flag=13
                            ret['flag']=13
                            saveTo=f'{plotSavePath}/{self.plotName}_{self.srcTag}{ext}'
                            
                            plot_no_fit(self.x, self.y, "Plot of fitting error: Peak rms > 1","", saveTo, 'Peak rms > 1', xlabel="", ylabel="")
                            # print(ret)
                            # ret['s2n']=np.nan

                        elif np.isinf(ret['peakRms']):
                            # self.flag=14
                            ret['flag']=14
                            saveTo=f'{plotSavePath}/{self.plotName}_{self.srcTag}{ext}'
                            
                            plot_no_fit(self.x, self.y, "Plot of fitting error: RMS is +- inf","", saveTo, 'RMS is +- inf', xlabel="", ylabel="")
                            sys.exit()

                        else:

                            # =============================================
                            # Estimate the signal to noise ratio
                            # =============================================
                            msg=f"Peak = {ret['peakFit']:.3f} +- {ret['peakRms']:.3f} [K]" #.format(, )
                            msg_wrapper("info", self.log.info, msg)
                            s2n = sig_to_noise(max(ret['correctedData']), ret['driftRes'], self.log)
                            msg2="S/N: {:.2f}".format(s2n)
                            msg_wrapper("info", self.log.info, msg2)
                            ret['s2n']=s2n

                            if s2n < 3.0:
                                msg=("signal to noise ratio < 3")
                                # self.flag = 15
                                ret['flag']=15
                                msg_wrapper("warning", self.log.warning, msg)
                            else:
                                pass         

                    else:
                        msg_wrapper("error", self.log.error,'No corrected data found')
                        ret['flag']=55 # check if this is valid
                        ret['s2n']=np.nan
                        # print(ret)
                        # sys.exit()
                        saveTo=f'{plotSavePath}/{self.plotName}_{self.srcTag}{ext}'
                        plot_no_fit(self.x, self.y, " No corrected data found","", saveTo, 'No corrected data', xlabel="", ylabel="")
                        # sys.exit()
                        self.__dict__[self.srcTag]=ret
                        # ret={
                        #     "peakFit":np.nan,"peakModel":[], "peakRms":np.nan,"correctedData":[],"peakPts":[],
                        #     "msg":"","driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,
                        #     "flag":1,"baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":[],
                        #     "baseLeft":[],"baseRight":[],'s2n':np.nan}
                        # ret['flag']==55
                        # self.__dict__[self.srcTag]=ret
                        return

                    # print(self.srcTag)
                    self.__dict__[self.srcTag]=ret
                    # self.flag=ret['flag']
                    # print(ret.keys())
                    saveTo=f'{plotSavePath}/{self.plotName}_{self.srcTag}{ext}'
                    title=f'Plot of {self.plotName}_{self.srcTag}'
                    plotPeakFit(title,self.xCleaned,ret['correctedData'],ret['peakModel'],ret['peakRms'],ret['peakPts'],\
                                saveTo,xlabel="",ylabel="")
                    # print(self.__dict__)
                    # sys.exit()

                elif 'D' in self.frontend:
                    if self.frontend=='03.5D':
                        npts=100
                        factor=.6 # .65 (cal/tar)

                    elif self.frontend=='06.0D':
                        npts=150 # number of points used for baseline fit
                        factor=0.55 #.8 (cal/tar)

                    else:
                        print(f'Invalid frontend: {self.frontend}')
                        sys.exit()

                    saveTag=f'{saveTo}/{self.plotName}_{tag}_'
                    ret = fit_dual_beam(self.xCleaned, self.yCleaned, self.HPBW, self.FNBW, factor,saveTag,self.log)
                    # fit_dual_beam(x, y, hpbw, fnbw, factor, npts, dec, srcType, data, scanNum, force, log):

                    # ret={"correctedData":yCorrected,"driftRes":driftRes,"driftRms":driftRms,
                    #     "driftCoeffs":driftCoeffs, "baseLocsCombined":baseLocs,
                    #     "baseLocsLeft":baseLocsl,"baseLocsRight":baseLocsr,
                    # "leftPeakData":ypeakldata,"leftPeakModelData":ypeakl,
                    # "leftPeakFit":ymax, "leftPeakFitErr":err_peakl,"leftPeakFitRes":fitResl,
                    # "rightPeakData":ypeakrdata,"rightPeakModelData":ypeakr,
                    # "rightPeakFit":ymin, "rightPeakFitErr":err_peakr,"rightPeakFitRes":fitResr,
                    # "msg":"","midXValueLeft":peakLoca,"midXValueRight":peakLocb,
                    # "flag":flag
                    # }
                    # print(ret)
                    # sys.exit()
                    if len(ret['correctedData'])>1:
                        if ret['leftPeakFitErr'] > 1. or ret['rightPeakFitErr'] > 1.:
                            msg = "Peak rms > 1"
                            self.flag = 13
                            msg_wrapper("warning", self.log.warning, msg)
                            saveTo=f'{plotSavePath}/{self.plotName}_{self.srcTag}{ext}'
                            plot_no_fit(self.x, self.y, msg,"", saveTo, msg, xlabel="", ylabel="")
                            # ret['s2na']=np.nan
                            # ret['s2nb']=np.nan
                        elif np.isinf(ret['leftPeakFitErr']) or np.isinf(ret['rightPeakFitErr']):
                            msg = "Rms is +- inf"
                            self.flag = 14
                            msg_wrapper("warning", self.log.warning, msg)
                            saveTo=f'{plotSavePath}/{self.plotName}_{self.srcTag}{ext}'
                            plot_no_fit(self.x, self.y, msg,"", saveTo, msg, xlabel="", ylabel="")
                        
                        else:
                            # =============================================
                            # Estimate the signal to noise ratio
                            # =============================================
                            # A beam
                            msg=f"Peak A= {ret['leftPeakFit']:.3f} +- {ret['leftPeakFitErr']:.3f} [K]" #.format(, )
                            msg_wrapper("info", self.log.info, msg)
                            
                            s2na = sig_to_noise(abs(max(ret['leftPeakData'])), ret['driftRes'], self.log)
                            msga="S/N: {:.2f}".format(s2na)
                            msg_wrapper("info", self.log.info, msga)
                            ret['s2na']=s2na

                            # B beam
                            msg=f"Peak B = {ret['rightPeakFit']:.3f} +- {ret['rightPeakFitErr']:.3f} [K]" #.format(, )
                            msg_wrapper("info", self.log.info, msg)

                            s2nb = sig_to_noise(abs(min(ret['rightPeakData'])), ret['driftRes'], self.log)
                            msgb="S/N: {:.2f}".format(s2nb)
                            msg_wrapper("info", self.log.info, msgb)
                            ret['s2nb']=s2nb


                            # print("S/N A beam: {:.2f} \nS/N B beam: {:.2f}".format(s2na, s2nb))

                            if s2na < 3. or s2nb < 3.:
                                msg="Got a s2n < 3"
                                self.flag = 15
                                ret['flag']=self.flag
                                # ret['s2na']=np.nan
                                # ret['s2nb']=np.nan
                                msg_wrapper("warning", self.log.warning, msg)

                            else:
                                pass
                    else:
                        msg_wrapper("error", self.log.error,'No corrected data found')
                        ret['flag']=55 # check if this is valid
                        ret['s2na']=np.nan
                        ret['s2nb']=np.nan
                        saveTo=f'{plotSavePath}/{self.plotName}_{self.srcTag}{ext}'
                        plot_no_fit(self.x, self.y, "No corrected data found","", saveTo, 'No corrected data', xlabel="", ylabel="")
                        # sys.exit()
                        self.__dict__[self.srcTag]=ret
                        # ret={
                        #     "peakFit":np.nan,"peakModel":[], "peakRms":np.nan,"correctedData":[],"peakPts":[],
                        #     "msg":"","driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,
                        #     "flag":1,"baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":[],
                        #     "baseLeft":[],"baseRight":[],'s2n':np.nan}
                        # ret['flag']==55
                        
                        return
                    
                    # ret={"correctedData":yCorrected,"driftRes":driftRes,"driftRms":driftRms,
                    #     "driftCoeffs":driftCoeffs, "baseLocsCombined":baseLocs,
                    #     "baseLocsLeft":baseLocsl,"baseLocsRight":baseLocsr,
                    # "leftPeakData":ypeakldata,"leftPeakModelData":ypeakl,
                    # "leftPeakFit":ymax, "leftPeakFitErr":err_peakl,"leftPeakFitRes":fitResl,
                    # "rightPeakData":ypeakrdata,"rightPeakModelData":ypeakr,
                    # "rightPeakFit":ymin, "rightPeakFitErr":err_peakr,"rightPeakFitRes":fitResr,
                    # "msg":"","midXValueLeft":peakLoca,"midXValueRight":peakLocb,
                    # "flag":flag
                    # }

                    self.__dict__[self.srcTag]=ret
                    saveTo=f'{plotSavePath}/{self.plotName}_{self.srcTag}{ext}'
                    title=f'Plot of {self.plotName}_{self.srcTag}'
                    plotDualBeamFit(self.xCleaned,ret['correctedData'],ret['leftPeakData'],\
                                    ret['leftPeakModelData'],ret['rightPeakData'],\
                                    ret['rightPeakModelData'],title,\
                                    'corrected data',\
                                    "T$_{A}$ [K]"+f" = {ret['leftPeakFit']:.3f} +- {ret['leftPeakFitErr']:.3f}",\
                                    "T$_{A}$ [K]"+f" = {ret['rightPeakFit']:.3f} +- {ret['rightPeakFitErr']:.3f}",\
                                    saveTo,xlabel="",ylabel="")

                else:
                    print(f'Invalid frontend: {self.frontend}')
                    sys.exit()

      
    def fit_theoretical_baselines(self, coeff):
        """Fit the data at the theoretical baseline location."""
        
        print(coeff)
        
        hfnbw=self.FNBW/2
        offset=self.xCleaned

        # Get indices where the offset values are within the main beam
        offset_masked, amp_masked, main_beam=self.locate_baseline_blocks_masked(self,offset,coeff)

        #fit a polynomial of any order
        lin_first_null = np.poly1d(np.ma.polyfit(x=offset_masked, y=amp_masked,  deg=3))

        #Subtract the polynomial fitted to the baseline, then fit 2nd-order polynomial through the top of the beam.
        base_sub = self.yCleaned - lin_first_null(offset)
        self.flag=26

        return base_sub,main_beam,offset_masked, amp_masked
    
    def make_initial_plots(self,plot,title,plotlab, plotlabCleaned):
        """Make initial plots of the raw and cleaned data"""

        plot.add_data(plotlab,f'{title} raw data', self.x, self.y, "Scandist [Deg]", "T$_{A}$ [K]", self.pol, f'currentScanPlots/{self.srcTag}_raw.png')
        plot.add_data(plotlabCleaned,f'{title} cleaned data', self.xCleaned, self.yCleaned, "Scandist [Deg]", "T$_{A}$ [K]", self.pol, f'currentScanPlots/{self.srcTag}_cleaned.png')
                
        plot.plot_beam(plotlab)
        plot.plot_beam(plotlabCleaned)
        plot.overplot_2_scans(plotlab,plotlabCleaned,f"{title} raw vs cleaned data",'raw','cleaned', f'currentScanPlots/{self.srcTag}_overlay_data.png')
        return plot
    
    def clean_data(self):
        """
        Clean the data of possible RFI. Remove all data points
        larger that 3 times the standard deviation.
        """
        
        if self.applyRFIremoval=='n':
            self.xCleaned=self.x 
            self.yCleaned=self.y
            self.spl=np.nan
            self.pt=np.nan
            self.RMSB=np.nan
            self.RMSA=np.nan
        else:
            self.xCleaned, self.yCleaned,self.RMSB, self.RMSA, self.spl, self.pt = clean_rfi(
            self.x, self.y,self.log)
                
    def locate_main_beam_data(self,offset,coeff):

        # Get indices where the offset values are within the main beam
        hfnbw=self.FNBW/2.
        main_beam = np.where(np.logical_and(offset >= coeff[1]-hfnbw, offset <= coeff[1]+hfnbw))[0]
        return main_beam

    def locate_baseline_blocks_masked(self,offset,y,coeff):
        """ Locate baseline by masking the main beam. This doesn't work
        well because the data is not perfect and may contain sidelobes
        which may not necessarily be best addressed by looking at using higher 
        order polynomials."""

        main_beam = self.locate_main_beam_data(self,offset,coeff)
                            
        #mask the main beam for polynomial fit to the baseline
        mask = np.zeros(len(offset))
        mask[main_beam] = 1
        offset_masked = np.ma.array(offset,mask=mask)
        amp_masked = np.ma.array(y, mask=mask)
        
        return offset_masked, amp_masked, main_beam

    def locate_baseline_blocks_fnbw(self,x,hfnbw):
        """
            Find the locations to fit a baseline. We assume the 
            baseline gives a good fit beyond the fnbw points on either
            side of the beam.
        """

        # If all looks we'll get the locations or positions where
        # a first order polynomial is going to be fit in order to
        # correct for any drift in the data. We are assuming that the
        # data is devoid of any RFI beyond the fnbw locations on either
        # side of the main beam
        left=-hfnbw#coeff[1]-hfnbw
        right=hfnbw#coeff[1]+hfnbw
        baseLine = np.where(np.logical_or(
            x <= left, x >= right))[0]

        # get coeffecients of a first order polynomial fit to
        # either ends of the baseline selection locations
        # baseline locations to the left of the beam
        leftBaseline = np.where(x <= left)[0]
        # baseline locations to the right of the beam
        rightBaseline = np.where(x >= right)[0]

        sidelobes=0 # no sidelobes/sidelobes ignored

        return baseLine, leftBaseline, rightBaseline, sidelobes