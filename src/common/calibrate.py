# =========================================================================== #
# File: calc_pss.py                                                           #
# Author: Pfesesani V. van Zyl                                                #
# =========================================================================== #

# Standard library imports
# --------------------------------------------------------------------------- #
import numpy as np 
import sys
from .miscellaneousFunctions import catch_zeroDivError
# =========================================================================== #

def calc_pss(flux, Ta, errTa):
    """
        Calculate the Point source sensitivity (PSS)
        and its error for data with no pointing correction
        applied.

        Args:
            flux: the flux density of the source
            Ta: the antenna temperature
            errTa: the error in the antenna temperature

        Returns:
            pss: the point source sensitivity
            errPSS: the error in the point source sensitivity
            appEff: the apperture effeciency
    """

    try:
        pss = flux/2.0/Ta
        errPSS = np.sqrt(errTa**2/Ta**2)*pss
        appEff = 1380.0/np.pi/(25.9/2.0)**2/pss

    except ZeroDivisionError:
        pss = .0
        errPSS = .0
        appEff = .0

    return pss, errPSS, appEff

def calc_tcorr(Ta, pc, data):
    """
        Calculate the antenna temperature correction for high frequencies.

        Args:
            Ta - the on scan antenna temperature 
            pc - the pointing correction 
            data - the dictionary containing all the drift scan parameters

        Returns:
            corrTa - the corrected antenna temperature
    """

    # print(data['FRONTEND'],data['BEAMTYPE'],data['OBJECT'])
    # sys.exit()

    if data["FRONTEND"] == "01.3S":
        if data["OBJECT"].upper() == "JUPITER":
                # Only applying a size correction factor and atmospheric correction to Jupiter
                # See van Zyl (2023) - in Prep
                corrTa = Ta * pc * data["ATMOS_ABSORPTION_CORR"] * data["SIZE_CORRECTION_FACTOR"]
                return corrTa
        else:
            # do we also apply a atmospheric correcttion factor directly to the target source ?
            # find out, for now I'm not applyin it
            # tests this ASAP
            corrTa = Ta * pc #* data["ATMOS_ABSORPTION_CORR"]
            return corrTa
    else:
        corrTa = Ta*pc
        return corrTa

def test_for_nans(Ta,errTa):
    """
        Test if data has nans
    
        Returns: 
            Ta : antenna temperature
            errTa: error in antenna temperature
    """

    if str(Ta) == "nan" or Ta is None or Ta==np.nan:
        Ta=0.0
        errTa=0.0
    else:
        pass
    return Ta, errTa 

def calc_pc_pss(scanNum, hpsTa, errHpsTa, hpnTa, errHpnTa, onTa, errOnTa, flux,data):
        """
            Calculate the pss for pointing corrected observations.

            Args:
                scanNum: the index of the current scan, see plot_manager.py
                hpsTa: the half power south antenna temperature
                errHpsTa: the error in the half power south antenna temperature
                hpnTa: the half power north antenna temperature
                errHpnTa: the error in the half power north antenna temperature
                onTa: the on source antenna temperature
                errOnTa: the error in the on source antenna temperature
                flux: the source flux density
                data: the dictionary containing all the drift scan parameters

            Returns:
                pss: the point source sensitivity
                errPss: the error in the point source sensitivity
                appEff: the apperture effeciency
                corrTa: the corrected antenna temperature 
                errCorrTa: the error in the corrected antenna temperature
                appEff: the apperture effeciency
        """

        # Check if data has nans
        onTa, errOnTa = test_for_nans(onTa,errOnTa)
        hpsTa, errHpsTa = test_for_nans(hpsTa,errHpsTa)
        hpnTa, errHpnTa = test_for_nans(hpnTa,errHpnTa)
        
        if onTa != 0.0:

            #if no hpnTa
            if((hpnTa == 0) and (hpsTa != 0)):
                #pc = exp[((ln(hpnTa) - ln(onTa) + ln(2))**2)/4ln(2)]
                #corrTa = onTa x pc

                # calculate the pointing and corrected antenna temp and its error
                pc, der1, der2 = calc_pc_eq(hpsTa, onTa)
                corrTa = calc_tcorr(scanNum,onTa, pc, data)
                errCorrTa = np.sqrt((errOnTa**2)*(der2**2) + (errHpsTa**2)*(der1**2))

                # Calculate the PSS and appeture effeciency
                pss = abs(float(flux)/2.0/corrTa)  # 0.0
                errPss = np.sqrt(abs(errCorrTa/corrTa))*pss
                appEff = 1380.0/np.pi/(25.9/2.0)**2/pss

                #print("\n,errCorrTa: %.3f, corrTa: %.3f, PSS: %.3f, errPSS: %.3f\n" %
                #      (errCorrTa, corrTa, pss,errPss))

            #if no hpsTa
            elif((hpnTa != 0) and (hpsTa == 0)):
                # pc = exp[((ln(onTa) - ln(hpnTa) + ln(2))**2)/4ln(2)]
                # corrTa = onTa x pc

                # calculate the pointing and corrected antenna temp and its error
                pc,der1, der2 = calc_pc_eq(onTa, hpnTa)
                corrTa = calc_tcorr(scanNum,onTa, pc, data)
                errCorrTa = np.sqrt((errOnTa**2)*(der1**2) + (errHpnTa**2)*(der2**2))

                # Calculate the PSS and apeture effeciency
                pss = abs(float(flux)/2.0/corrTa)  # 0.0
                errPss = np.sqrt(abs(errCorrTa/corrTa))*pss
                appEff = 1380.0/np.pi/(25.9/2.0)**2/pss

                #print("\n,errCorrTa: %.3f, corrTa: %.3f, PSS: %.3f, errPSS: %.3f\n" %
                #      (errCorrTa, corrTa, pss, errPss))

            #if all present
            elif((hpnTa != 0) and (hpsTa != 0)):
                # pc = exp[((ln(hpsTa) - ln(hpnTa)**2)/16ln(2)]
                # corrTa = Ton x pc

                # calculate the pointing and corrected antenna temp and its error
                term2 = 16*np.log(2)
                pc, der1, der2 = calc_pc_eq(hpsTa, hpnTa, term2)
                corrTa = calc_tcorr(scanNum, onTa, pc, data)
                errCorrTa = np.sqrt((errHpnTa**2)*(der2**2) + (errHpsTa**2)*(der1**2))

                # Calculate the PSS and apeture effeciency
                pss = abs(float(flux)/2.0/corrTa) 
                errPss = np.sqrt(abs(errCorrTa/corrTa))*pss
                appEff = 1380.0/np.pi/(25.9/2.0)**2/pss

                #print("\nTcorerr: %.3f, corrTa: %.3f, PSS: %.3f, errPSS: %.3f\n" %
                #      (errCorrTa, corrTa, pss, errPss))
         
            #if no hpnTa/hpsTa
            if((hpnTa == 0) and (hpsTa == 0)):
                pss, errPss, appEff = set_pss_to_zero()
                corrTa, errCorrTa, pc = set_corr_ta_to_zero()
                
        else:
            # if there's no on scan observation, everything defaults to zero
            pss, errPss, appEff = set_pss_to_zero()
            corrTa, errCorrTa, pc = set_corr_ta_to_zero()

        return pss, errPss, pc, corrTa, errCorrTa, appEff

def calibrate(  hpsTa, errHpsTa, hpnTa, errHpnTa, onTa, errOnTa, data, log):
        """
            Calculate the pointing corrected antenna temperature.
    
            Parameters:
                hpsTa: the half power south antenna temperature
                errHpsTa: the error in the half power south antenna temperature
                hpnTa: the half power north antenna temperature
                errHpnTa: the error in the half power north antenna temperature
                onTa: the on source antenna temperature
                errOnTa: the error in the on source antenna temperature
                data: the dictionary containing all the drift scan parameters

            Returns:
                pc: the pointing correction
                corrTa: the corrected antenna temperature 
                errCorrTa: the error in the corrected antenna temperature
        """
        # # Check if data has nans
        onTa, errOnTa = test_for_nans(onTa, errOnTa)
        hpsTa, errHpsTa = test_for_nans(hpsTa, errHpsTa)
        hpnTa, errHpnTa = test_for_nans(hpnTa, errHpnTa)
        
        if onTa != 0.0:

            #if no hpnTa
            if((hpnTa == 0) and (hpsTa != 0)):
                #pc = exp[((ln(hpsTa) - ln(Ton) + ln(2))**2)/4ln(2)]
                #corrTa = Ton x pc

                # calculate the pointing and corrected antenna temp and its error
                pc, der1, der2 = calc_pc_eq(hpsTa, onTa)
                corrTa = calc_tcorr( onTa, pc, data)
                errCorrTa = np.sqrt((errOnTa**2)*(der2**2) + (errHpsTa**2)*(der1**2))

            #if no hpsTa
            elif((hpnTa != 0) and (hpsTa == 0)):
                # pc = exp[((ln(Ton) - ln(hpnTa) + ln(2))**2)/4ln(2)]
                # corrTa = Ton x pc

                # calculate the pointing and corrected antenna temp and its error
                pc, der1, der2 = calc_pc_eq(onTa, hpnTa)
                corrTa = calc_tcorr(onTa, pc, data)
                errCorrTa = np.sqrt((errOnTa**2)*(der1**2) + (errHpnTa**2)*(der2**2))

            #if all present
            elif((hpnTa != 0) and (hpsTa != 0)):
                # pc = exp[((ln(hpsTa) - ln(hpnTa)**2)/16ln(2)]
                # corrTa = Ton x pc

                # calculate the pointing and corrected antenna temp and its error
                term2 = 16*np.log(2)
                pc, der1, der2 = calc_pc_eq(hpsTa, hpnTa, term2)
                corrTa = calc_tcorr( onTa, pc, data)
                errCorrTa = np.sqrt((errHpnTa**2)*(der2**2) +
                                  (errHpsTa**2)*(der1**2))

            #if no hpnTa/hpsTa
            if((hpnTa == 0) and (hpsTa == 0)):
                corrTa, errCorrTa, pc = set_corr_ta_to_zero()
        else:
            corrTa, errCorrTa, pc = set_corr_ta_to_zero()
            
        #print("\npc: {}, corrTa: {}, Tcorrerr: {}\n".format(pc, corrTa, errCorrTa))
        return pc, corrTa, errCorrTa

def calc_pc_eq(Ta1, Ta2, term2=""):

    """ Calculate the pointing correction and its derivatives.
    The pointing equations are given in the method 
    calc_pc_pss()
    
    Parameters:
        Ta1: first temperature
        Ta2: second temperature
        term2: the second term of the pointing correction equation as defined 
        in thesis/reference.  

    Returns:
        pc: the pointing correction
        der1: first derivative with respect to Ta1
        der2: first derivative with respect to Ta2
    """

    if term2=="":
        term1 = (np.log(abs(Ta1)) - np.log(abs(Ta2)) - np.log(2))**2
        term2 = 4*np.log(2)
    else:
        term1 = (np.log(abs(Ta1)) - np.log(abs(Ta2)))**2
    term3 = term1/term2
    pc = np.exp(term3)

    # calculate the derivatives
    der1 = pc * 2.0 * term3 * (1.0/Ta1)
    der2 = pc * 2.0 * term3 * (-1.0/Ta2)

    return pc, der1, der2

def set_pss_to_zero():
    """ Set the estimation of the pss and apperture effeciency to zero """

    pss, errPss, appEff = .0, .0, .0
    return pss, errPss, appEff

def set_corr_ta_to_zero():
    """ Set the estimation of the corrected antenna temp to zero. """

    corrTa, corrTaErr, pc = .0, .0, .0
    return corrTa, corrTaErr, pc

def calc_flux(ta,dta,pss,dpss):
        """Calculate the flux density. """

        ta=float(ta)
        dta=float(dta)
        pss=float(pss)
        dpss=float(dpss)
        
        if float(ta) != np.nan and float(pss)!=np.nan:
#             print(ta,pss)
            
            flux=ta*pss
            lta=catch_zeroDivError(ta,dta)
            lps=catch_zeroDivError(pss,dpss)
            errta=(lta)**2
            errpss=(lps)**2
            dflux=flux*np.sqrt(errta+errpss)

            
        else:
            flux=np.nan
            dflux=np.nan
        return flux,dflux

def calc_totFlux(lcp,dlcp,rcp,drcp):
        ''' Calculate the total flux density of the source'''
        sumflux=np.sum([lcp,rcp])
        n=(np.array([lcp,rcp])>0).sum() 
        fluxtot=(sumflux/n)*2
        dfluxtot=(2/n)*np.sqrt(dlcp**2+drcp**2)

        return fluxtot,dfluxtot
    
def calc_dualtotFlux(slcp,dslcp,srcp,dsrcp,bslcp,bdslcp,bsrcp,bdsrcp):
        ''' Calculate the total flux density of the source'''
        sumflux=np.sum([slcp,srcp,bslcp,bsrcp])
        n=(np.array([slcp,srcp,bslcp,bsrcp])>0).sum() 
        fluxtot=(sumflux/n)*2
        dfluxtot=(2/n)*np.sqrt(dslcp**2+dsrcp**2+bdslcp**2+bdsrcp**2)

        return fluxtot,dfluxtot

def getpss(pssdf, date):
    """ Get the PSS of a given bin time-range.
    
        pssdf: dataframe containing the pss bins.
        date: the date used to estimate the required bin range in order to extract the PSS. """
    
    date=float(date)
    pss=np.nan
    dpss=np.nan
#     print(pssdf.columns)
    for k in range(len(pssdf)):
        start = float(pssdf['MJD_START'].iloc[k])
        end   = float(pssdf['MJD_END'].iloc[k])
#         print(start,date,end)
        
        if date>=start and date<=end:
#             print(start,date,end)
            
            pss=pssdf['PSS'].iloc[k]
            dpss=pssdf['PSS_STDEV'].iloc[k]
            return pss,dpss
        else:
            pass
    return np.nan,np.nan
