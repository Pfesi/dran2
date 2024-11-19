# =========================================================================== #
# File: calibrate.py                                                          #
# Author: Pfesesani V. van Zyl                                                #
# =========================================================================== #

# Standard library imports
# --------------------------------------------------------------------------- #

#try:
from .miscellaneousFunctions import catch_zeroDivError
#except:
#    from common.miscellaneousFunctions import catch_zeroDivError

import numpy as np 
import sys

# =========================================================================== #

def calc_pss(flux:float, Ta:float, errTa:float):
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

    flux=float(flux)
    Ta=float(Ta)
    errTa=float(errTa)

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

    # print(data['FRONTEND'],data['BEAMTYPE'],data['OBJECT'],pc)
    
    # print(data.columns)

    Ta= float(Ta)
    pc=float(pc)
    if data["FRONTEND"] == "01.3S":
        if data["OBJECT"].upper() == "JUPITER":
                # Only applying a size correction factor and atmospheric correction to Jupiter
                # See van Zyl (2023) - in Prep
                abs=float(data["ATMOS_ABSORPTION_CORR"])
                scf=float( data["SIZE_CORRECTION_FACTOR"])
                corrTa = Ta * pc * abs * scf
                # print(corrTa,data["ATMOS_ABSORPTION_CORR"] , data["SIZE_CORRECTION_FACTOR"],data["ATMOS_ABSORPTION_CORR"] * data["SIZE_CORRECTION_FACTOR"])
                # sys.exit()
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

    try:
        Ta=float(Ta)
    except:
        Ta=np.nan

    try:
        errTa=float(errTa)
    except:
        errTa=np.nan

    return Ta, errTa 

def calc_pc_pss(hpsTa, errHpsTa, hpnTa, errHpnTa, onTa, errOnTa, flux,data):
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
        
        onTa=float(onTa)
        errOnTa=float(errOnTa)
        hpsTa=float(hpsTa)
        errHpsTa=float(errHpsTa)
        hpnTa=float(hpnTa)
        errHpnTa=float(errHpnTa)

        if onTa != 0.0:

            #if no hpnTa
            if((hpnTa == 0) and (hpsTa != 0)):
                # missing north
                #pc = exp[((ln(hpsTa) - ln(Ton) + ln(2))**2)/4ln(2)]
                #corrTa = Ton x pc

                term2 = 4*np.log(2)
                # calculate the pointing and corrected antenna temp and its error
                pc, der1, der2 = calc_pc_eq(hpsTa, onTa,term2,'n')
                corrTa = calc_tcorr(onTa, pc, data)
                errCorrTa = np.sqrt((errOnTa**2)*(der2**2) + (errHpsTa**2)*(der1**2))

                # Calculate the PSS and appeture effeciency
                pss, errPSS, appEff=calc_pss(flux, corrTa, errCorrTa)

                #print("\n,errCorrTa: %.3f, corrTa: %.3f, PSS: %.3f, errPSS: %.3f\n" %
                #      (errCorrTa, corrTa, pss,errPss))

            #if no hpsTa
            elif((hpnTa != 0) and (hpsTa == 0)):
                # missing south
                # pc = exp[((ln(Ton) - ln(hpnTa) + ln(2))**2)/4ln(2)]
                # corrTa = Ton x pc

                term2 = 4*np.log(2)
                # calculate the pointing and corrected antenna temp and its error
                pc,der1, der2 = calc_pc_eq(onTa, hpnTa,term2,'s')
                corrTa = calc_tcorr(onTa, pc, data)
                errCorrTa = np.sqrt((errOnTa**2)*(der1**2) + (errHpnTa**2)*(der2**2))

                # Calculate the PSS and appeture effeciency
                pss, errPSS, appEff=calc_pss(flux, corrTa, errCorrTa)

                #print("\n,errCorrTa: %.3f, corrTa: %.3f, PSS: %.3f, errPSS: %.3f\n" %
                #      (errCorrTa, corrTa, pss, errPss))

            #if all present
            elif((hpnTa != 0) and (hpsTa != 0)):
                # pc = exp[((ln(hpsTa) - ln(hpnTa)**2)/16ln(2)]
                # corrTa = Ton x pc

                # calculate the pointing and corrected antenna temp and its error
                term2 = 16*np.log(2)
                pc, der1, der2 = calc_pc_eq(hpsTa, hpnTa, term2)
                corrTa = calc_tcorr( onTa, pc, data)
                errCorrTa = np.sqrt((errHpnTa**2)*(der2**2) + (errHpsTa**2)*(der1**2))

                # Calculate the PSS and appeture effeciency
                pss, errPSS, appEff=calc_pss(flux, corrTa, errCorrTa)

                #print("\nTcorerr: %.3f, corrTa: %.3f, PSS: %.3f, errPSS: %.3f\n" %
                #      (errCorrTa, corrTa, pss, errPss))
         
            #if no hpnTa/hpsTa
            if((hpnTa == 0) and (hpsTa == 0)):
                pss, errPSS, appEff = set_pss_to_zero()
                corrTa, errCorrTa, pc = set_corr_ta_to_zero()
                
        else:
            # if there's no on scan observation, everything defaults to zero
            pss, errPSS, appEff = set_pss_to_zero()
            corrTa, errCorrTa, pc = set_corr_ta_to_zero()

        return pss, errPSS, pc, corrTa, errCorrTa, appEff

def calibrate(hpsTa, errHpsTa, hpnTa, errHpnTa, onTa, errOnTa, data, log=''):
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
        
        # Check if data has nans
        onTa, errOnTa = test_for_nans(onTa, errOnTa)
        hpsTa, errHpsTa = test_for_nans(hpsTa, errHpsTa)
        hpnTa, errHpnTa = test_for_nans(hpnTa, errHpnTa)

        onTa=float(onTa)
        errOnTa=float(errOnTa)
        hpsTa=float(hpsTa)
        errHpsTa=float(errHpsTa)
        hpnTa=float(hpnTa)
        errHpnTa=float(errHpnTa)

        if onTa != 0.0:

            #if no hpnTa
            if((hpnTa == 0) and (hpsTa != 0)):
                # missing north
                #pc = exp[((ln(hpsTa) - ln(Ton) + ln(2))**2)/4ln(2)]
                #corrTa = Ton x pc

                term2 = 4*np.log(2)
                # calculate the pointing and corrected antenna temp and its error
                pc, der1, der2 = calc_pc_eq(hpsTa, onTa,term2,'n')
                corrTa = calc_tcorr( onTa, pc, data)
                errCorrTa = np.sqrt((errOnTa**2)*(der2**2) + (errHpsTa**2)*(der1**2))

            #if no hpsTa
            elif((hpnTa != 0) and (hpsTa == 0)):
                # missing south
                # pc = exp[((ln(Ton) - ln(hpnTa) + ln(2))**2)/4ln(2)]
                # corrTa = Ton x pc

                term2 = 4*np.log(2)
                # calculate the pointing and corrected antenna temp and its error
                pc, der1, der2 = calc_pc_eq(onTa, hpnTa,term2,'s')
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

def calc_pc_eq(Ta1, Ta2, term2="",pol=''):

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

    Ta1=float(Ta1)
    Ta2=float(Ta2)

    if term2=="":
        if pol=='n':
            # missing north
            term1 = (np.log(abs(Ta1)) - np.log(abs(Ta2)) + np.log(2))**2
        elif pol=='s':
            # missing south
            term1 = (np.log(abs(Ta1)) - np.log(abs(Ta2)) - np.log(2))**2
        term2 = 4*np.log(2)
    else:
        # print(Ta1,Ta2)
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
        sumflux=np.nansum([lcp,rcp])
        n=(np.array([lcp,rcp])>0).sum() 
        fluxtot=(sumflux/n)*2
        dfluxtot=(2/n)*np.sqrt(dlcp**2+drcp**2)

        return fluxtot,dfluxtot
    
def calc_dualtotFlux(slcp,dslcp,srcp,dsrcp,bslcp,bdslcp,bsrcp,bdsrcp):
        ''' Calculate the total flux density of the source'''
        sumflux=np.nansum([slcp,srcp,bslcp,bsrcp])
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
    
    for k in range(len(pssdf)):
        start = float(pssdf['MJD_START'].iloc[k])
        end   = float(pssdf['MJD_END'].iloc[k])

        if date>=start and date<=end:
            pss=pssdf['PSS'].iloc[k]
            dpss=pssdf['PSS_STDEV'].iloc[k]
            return pss,dpss
        else:
            pass
    return np.nan,np.nan

def get_calibrator_flux(data,calibrationPaper=''):
        """
            Calculate the source flux for the calibrator.
            Use the Ott and Baars system.
        """
        # baars = { 
        #     # Baars 1977 paper - J. W. M. Baars, R. Genzel, T. T. K. Pauliny-Toth,A. Witzel, 
        #     # 'The Absolute Spectrum of Cas A; An Accurate Flux Density Scale and a Set of 
        #     # Secondary Calibrators," Astronomy & Astrophysics, 61, 1977, pp. 99-106.
            
        #     "CYGNUSA"   : {'range_from': 2000,  'range_to': 31000, 'a': 7.161, 'b': -1.244, 'c':0     },
        #     "CYGNUS A"   : {'range_from': 2000,  'range_to': 31000, 'a': 7.161, 'b': -1.244, 'c':0     },
        #     "CYG A"   : {'range_from': 2000,  'range_to': 31000, 'a': 7.161, 'b': -1.244, 'c':0     },
        #     "3C405"   : {'range_from': 2000,  'range_to': 31000, 'a': 7.161, 'b': -1.244, 'c':0     }, # aka CYGNUS A

        #     "TAURUSA"   : {'range_from': 1000,  'range_to': 35000, 'a': 3.915, 'b': -0.299, 'c':0     },
        #     "TAURUS A"   : {'range_from': 1000,  'range_to': 35000, 'a': 3.915, 'b': -0.299, 'c':0     },
        #     "TAU A"   : {'range_from': 1000,  'range_to': 35000, 'a': 3.915, 'b': -0.299, 'c':0     },
        #     "3C144"   : {'range_from': 1000,  'range_to': 35000, 'a': 3.915, 'b': -0.299, 'c':0     }, # aka TAU A

        #     "VIRGOA"   : {'range_from': 400,   'range_to': 25000, 'a': 5.023, 'b': -0.856, 'c':0     },
        #     "VIRGO A"   : {'range_from': 400,   'range_to': 25000, 'a': 5.023, 'b': -0.856, 'c':0     },
        #     "VIR A"   : {'range_from': 400,   'range_to': 25000, 'a': 5.023, 'b': -0.856, 'c':0     },
        #     "3C274"   : {'range_from': 400,   'range_to': 25000, 'a': 5.023, 'b': -0.856, 'c':0     }, # aka virgo a

        #     "3C48"      : {'range_from': 405,   'range_to': 15000, 'a': 2.345, 'b':0.071,   'c':-0.138},
        #     "3C123"     : {'range_from': 405,   'range_to': 15000, 'a': 2.921, 'b': -0.002, 'c':-0.124},
        #     "3C161"     : {'range_from': 405,   'range_to': 10700, 'a': 1.633, 'b': 0.498,  'c':0.194 },

        #     "HYDRAA"   : {'range_from': 405,   'range_to': 10700, 'a': 4.497, 'b': -0.910, 'c':0     },
        #     "HYDRA A"   : {'range_from': 405,   'range_to': 10700, 'a': 4.497, 'b': -0.910, 'c':0     },
        #     "3C218"     : {'range_from': 405,   'range_to': 10700, 'a': 4.497, 'b': -0.910, 'c':0     }, #aka HYDRA A

        #     "3C286"     : {'range_from': 405,   'range_to': 15000, 'a': 1.480, 'b': 0.292,  'c':-0.124},

        #     "3C348"     : {'range_from': 405,   'range_to': 10700, 'a': 4.963, 'b': -1.052, 'c':0     },
        #     "HERCULES A"     : {'range_from': 405,   'range_to': 10700, 'a': 4.963, 'b': -1.052, 'c':0     }, #aka 3C348
        #     "HERCULESA"     : {'range_from': 405,   'range_to': 10700, 'a': 4.963, 'b': -1.052, 'c':0     }, #aka 3C348

        #     "3C353"     : {'range_from': 405,   'range_to': 10700, 'a': 2.944, 'b': -0.034, 'c':-0.109},
        #     'DR21'      : {'range_from': 7000,  'range_to': 31000, 'a': 1.81,  'b': -0.122, 'c':0     },
        #     "NGC7027"   : {'range_from': 10000, 'range_to': 31000, 'a': 1.32,  'b': -0.127, 'c':0     }
        # }
              
        ott = { 
            # OTT 1994 PAPER - M. Ott, A. Quirrenbach, T. P. Krichbaum, K. J. Standke, C. J. Schalinski, and C. A. Hummel,
            # An updated list of radio flux density calibrators, Astronomy & Astrophysics, 284, 1994, pp. 331-339.

                "3C48"    : {'range_from': 1408,  'range_to': 23780, 'a': 2.465, 'b': -0.004, 'c': -0.1251},
                "3C123"   : {'range_from': 1408,  'range_to': 23780, 'a': 2.525, 'b': 0.246, 'c': -0.1638},
                "3C147"   : {'range_from': 1408,  'range_to': 23780, 'a': 2.806, 'b': -0.140, 'c': -0.1031},
                "3C161"   : {'range_from': 1408,  'range_to': 10550, 'a': 1.250, 'b': 0.726, 'c': -0.2286},

                # Hydra A at 12GHz does not have a proper calibration flux, thus I will be adapting 
                # this to calibrate at 12500 MHz to include the 12 GHz observations at (12218 MHz)
                # True Flux limit 'range_to' is 10550. When we start using Ott, this should revert back.
                "HYDRAA"  : {'range_from': 1408,  'range_to': 12500, 'a': 4.729, 'b': -1.025, 'c':  0.0130}, 
                "HYDRA A" : {'range_from': 1408,  'range_to': 12500, 'a': 4.729, 'b': -1.025, 'c':  0.0130},
                "3C218"   : {'range_from': 1408,  'range_to': 12500, 'a': 4.729, 'b': -1.025, 'c':  0.0130}, #aka HYDRA A
                "0915-119"   : {'range_from': 1408,  'range_to': 12500, 'a': 4.729, 'b': -1.025, 'c':  0.0130}, #aka HYDRA A
                "0915-11"   : {'range_from': 1408,  'range_to': 12500, 'a': 4.729, 'b': -1.025, 'c':  0.0130}, #aka HYDRA A
                "J0918-1205"   : {'range_from': 1408,  'range_to': 12500, 'a': 4.729, 'b': -1.025, 'c':  0.0130}, #aka HYDRA A

                "3C227"   : {'range_from': 1408,  'range_to': 4750,  'a': 6.757, 'b': -2.801, 'c':  0.2969},
                "3C249.1" : {'range_from': 1408,  'range_to': 4750,  'a': 2.537, 'b': -0.565, 'c': -0.0404},

                "VIRGOA"  : {'range_from': 1408,  'range_to': 10550, 'a': 4.484, 'b': -0.603, 'c': -0.0280}, 
                "VIRGO A" : {'range_from': 1408,  'range_to': 10550, 'a': 4.484, 'b': -0.603, 'c': -0.0280}, 
                "VIR A"   : {'range_from': 1408,  'range_to': 10550, 'a': 4.484, 'b': -0.603, 'c': -0.0280}, 
                "3C274"   : {'range_from': 1408,  'range_to': 10550, 'a': 4.484, 'b': -0.603, 'c': -0.0280},  # AKA VIRGO A

                "3C286"   : {'range_from': 1408,  'range_to': 43200, 'a': 0.956, 'b': 0.584, 'c': -0.1644},
                "3C295"   : {'range_from': 1408,  'range_to': 32000, 'a': 1.490, 'b': 0.756, 'c': -0.2545},
                "3C309.1" : {'range_from': 1408,  'range_to': 32000, 'a': 2.617, 'b': -0.437, 'c': -0.0373},

                "3C348"   : {'range_from': 1408,  'range_to': 10550,  'a': 3.852, 'b': -0.361, 'c': -0.1053},
                "HERCULESA"   : {'range_from': 1408,  'range_to': 10550,  'a': 3.852, 'b': -0.361, 'c': -0.1053}, # AKA 3C348
                "HERCULES A"   : {'range_from': 1408,  'range_to': 10550,  'a': 3.852, 'b': -0.361, 'c': -0.1053},

                "3C353"   : {'range_from': 1408,  'range_to': 10550,  'a': 3.148, 'b': -0.157, 'c': -0.0911},

                "CYGNUSA" : {'range_from': 4750,  'range_to': 10550,  'a': 8.360, 'b': 1.565,  'c':0},
                "CYGNUS A": {'range_from': 4750,  'range_to': 10550,  'a': 8.360, 'b': 1.565,  'c':0},
                "CYG A"   : {'range_from': 4750,  'range_to': 10550,  'a': 8.360, 'b': 1.565,  'c':0},
                "3C405"   : {'range_from': 4750,  'range_to': 10550,  'a': 8.360, 'b': 1.565,  'c':0}, #AKA CYGNUS A

                "NGC7027" : {'range_from': 10550, 'range_to': 43200, 'a': 1.322, 'b': -0.134, 'c': 0}
                }
        
        # perley = { 
            # # PERLEY 2017 PAPER - R. A. Perley and B. J. Butler
            # # An accurate flux density scale from 50 MHz to 50 GHz, Astrophysical Journal Supplement Series, 230:7, 2017, (18pp)
            # # https://doi.org/10.3847/1538-4365/aa6df9

            #     "3C48"      : {'range_from': 50, 'range_to': 50000, 'a': 1.3253, 'b': -0.7553, 'c': -0.1914,  'd': 0.0498,  'e': 0,      'f':0},
            #     "3C123"     : {'range_from': 50, 'range_to': 50000, 'a': 1.8017, 'b': -0.7884, 'c': -0.1035,  'd': -0.0248, 'e': 0.0090, 'f':0},
            #     "PICTORA"   : {'range_from': 20, 'range_to': 4000,  'a': 1.9380, 'b': -0.7470, 'c':-0.0739,   'd':0,        'e':0,       'f':0},
            #     "PICTOR A"  : {'range_from': 20, 'range_to': 4000,  'a': 1.9380, 'b': -0.7470, 'c':-0.0739,   'd':0,        'e':0,       'f':0},

            #     "TAURUSA"   : {'range_from': 50, 'range_to': 4000,  'a': 2.9516, 'b': -0.2173, 'c':-0.0473,   'd':-0.0674,  'e':0,       'f':0},
            #     "TAURUS A"  : {'range_from': 50, 'range_to': 4000,  'a': 2.9516, 'b': -0.2173, 'c':-0.0473,   'd':-0.0674,  'e':0,       'f':0},
            #     "TAU A"     : {'range_from': 50, 'range_to': 4000,  'a': 2.9516, 'b': -0.2173, 'c':-0.0473,   'd':-0.0674,  'e':0,       'f':0},
            #     "3C144"     : {'range_from': 50, 'range_to': 4000,  'a': 2.9516, 'b': -0.2173, 'c':-0.0473,   'd':-0.0674,  'e':0,       'f':0}, # aka TAU A

            #     # Hydra A at 12GHz does not have a proper calibration flux, thus I will be adapting 
            #     # this to calibrate at 12500 MHz to include the 12 GHz observations at (12218 MHz)
            #     # True Flux limit 'range_to' is 11512, see page 3, Table 4
            #     "3C218"     : {'range_from': 50, 'range_to': 12000, 'a': 1.7795, 'b': -0.9176, 'c':-0.0843,   'd': -0.0139, 'e': 0.0295, 'f':0}, # aka HYDRA A
            #     "HYDRAA"    : {'range_from': 50, 'range_to': 12000, 'a': 1.7795, 'b': -0.9176, 'c':-0.0843,   'd': -0.0139, 'e': 0.0295, 'f':0},
            #     "HYDRA A"   : {'range_from': 50, 'range_to': 12000, 'a': 1.7795, 'b': -0.9176, 'c':-0.0843,   'd': -0.0139, 'e': 0.0295, 'f':0},

            #     "VIRGOA"    : {'range_from': 50, 'range_to': 3000,  'a': 2.4466, 'b': -0.8116, 'c':-0.0483,   'd': 0,       'e': 0,      'f':0}, 
            #     "VIRGO A"   : {'range_from': 50, 'range_to': 3000,  'a': 2.4466, 'b': -0.8116, 'c':-0.0483,   'd': 0,       'e': 0,      'f':0}, 
            #     "VIR A"     : {'range_from': 50, 'range_to': 3000,  'a': 2.4466, 'b': -0.8116, 'c':-0.0483,   'd': 0,       'e': 0,      'f':0}, 
            #     "3C286"     : {'range_from': 50, 'range_to': 50000, 'a': 1.2481, 'b': -0.4507, 'c':0.0357,    'd': 0,       'e': 0,      'f':0},

            #     "HERCULESA" : {'range_from': 20, 'range_to': 12000, 'a': 1.8298, 'b': -1.0247, 'c':-0.0951,   'd': 0,       'e': 0,      'f':0},
            #     "HERCULES A": {'range_from': 20, 'range_to': 12000, 'a': 1.8298, 'b': -1.0247, 'c':-0.0951,   'd': 0,       'e': 0,      'f':0},
            #     "3C348"     : {'range_from': 20, 'range_to': 12000, 'a': 1.8298, 'b': -1.0247, 'c':-0.0951,   'd': 0,       'e': 0,      'f':0}, # AKA HERCULES A

            #     "CYGNUSA"   : {'range_from': 50, 'range_to': 12000, 'a': 3.3498, 'b': -1.0022, 'c':-0.2246,   'd': 0.0227,  'e': 0.0425, 'f':0},
            #     "CYGNUS A"  : {'range_from': 50, 'range_to': 12000, 'a': 3.3498, 'b': -1.0022, 'c':-0.2246,   'd': 0.0227,  'e': 0.0425, 'f':0},
            #     "3C405"     : {'range_from': 50, 'range_to': 12000, 'a': 3.3498, 'b': -1.0022, 'c':-0.2246,   'd': 0.0227,  'e': 0.0425, 'f':0}, # AKA CYGNUS A

            #     "3C353"     : {'range_from': 20, 'range_to': 4000,  'a': 1.8627, 'b': -0.06938, 'c': -0.0998, 'd': -0.0732, 'e': 0,      'f':0},
            #     }
        
        #if cal!="":
            # if self.data['OBJECT'].upper() in perley.keys():
            #     if perley[self.data['OBJECT']]["range_from"] < self.data['CENTFREQ'] < perley[self.data['OBJECT']]["range_to"]:
            #         self.data['FLUX'] = (10**(perley[self.data['OBJECT']]["a"] +
            #                                   perley[self.data['OBJECT']]["b"]*self.data['LOGFREQ'] + 
            #                                   perley[self.data['OBJECT']]["c"]*(self.data['LOGFREQ'])**2 + 
            #                                   perley[self.data['OBJECT']]["d"]*(self.data['LOGFREQ'])**3 + 
            #                                   perley[self.data['OBJECT']]["e"]*(self.data['LOGFREQ'])**4 + 
            #                                   perley[self.data['OBJECT']]["f"]*(self.data['LOGFREQ'])**5 ))
                    
            # el

            # We are ignoring Perley for now, their calibration flux is 9 Jy,  Ott and Baars are ~27
        if data['OBJECT'].upper() in ott.keys():
                if ott[data['OBJECT']]["range_from"] < data['CENTFREQ'] < ott[data['OBJECT']]["range_to"]:
                    data['FLUX'] = (10**(ott[data['OBJECT']]["a"] + 
                                              ott[data['OBJECT']]["b"]*data['LOGFREQ'] + 
                                              ott[data['OBJECT']]["c"]*data['LOGFREQ']**2))
                    
        # elif data['OBJECT'].upper() in baars.keys():
        #             if baars[data['OBJECT']]["range_from"] < data['CENTFREQ'] < baars[data['OBJECT']]["range_to"]:
        #                 data['FLUX'] = (10**(baars[data['OBJECT']]["a"] + 
        #                                           baars[data['OBJECT']]["b"]*data['LOGFREQ'] + 
        #                                           baars[data['OBJECT']]["c"]*data['LOGFREQ']**2))
        else:
                print(f'{data["OBJECT"]} - does not have calibration flux density spectral parameters in Ott 1994 or Barrs 1977.')
                print('Contact author about this.')
                data['FLUX']=0.0
                # sys.exit()
