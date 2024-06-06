# ============================================================================#
# File: driftScanAttributes.py                                                    #
# Author: Pfesesani V. van Zyl                                                #
# ============================================================================#

# Standard library imports
# --------------------------------------------------------------------------- #
import numpy as np
import sys
from dataclasses import dataclass
from .miscellaneousFunctions import set_dict_item
# =========================================================================== #

@dataclass
class DriftScanAttributes:
    """
        Class of parameters to be collected/saved to a database from the drift 
        scan fits file. These are the values that will be populated in the 
        CALDB or TARDB databases.

        Args:
            parameters (dict): dictionary of all properties to be stored.
    """
    

    def print_keys(self):
        """ Print the keys of the dictionary. """

        print(self.__dict__.keys())

    def print_dict(self):
        """ Print the dictionary key value pairs. """

        print("\n# parameters: \n")
        [print(i, ": ", j) for i, j in zip(
                list(self.__dict__.keys()), list(self.__dict__.values()))]
    
    def reset_dict(self):
        """ Reset the dictionary. """

        self.__dict__ = {}

    # =========================================================================
    #   COMMON SETTINGS
    # =========================================================================

    def set_common_parameters(self):
        """
            Dictionary of default values for parameters common to all scan types.
        """
        
        set_dict_item(self.__dict__,"FILENAME","","Name of fits file being processed")
        set_dict_item(self.__dict__,"SOURCEDIR","","Name of folder containing fits file")
        set_dict_item(self.__dict__,"MJD",np.nan,"Modified julian date of observation")
        set_dict_item(self.__dict__,"LOGFREQ",np.nan,"Log of central frequency")
        set_dict_item(self.__dict__,"HA",np.nan,"Hour angle")
        set_dict_item(self.__dict__,"ZA",np.nan,"Zenith angle , used to be DEC")
        set_dict_item(self.__dict__,"ELEVATION",np.nan,"Elevation")
        set_dict_item(self.__dict__,"ATMOSABS",np.nan,"Atmospheric absorption")

    # =========================================================================
    #   WIDE BEAM SCAN SETTINGS
    # =========================================================================

    def set_wb_parameters(self,pols):
        """ Set the parameters specific to a wide beam on lcp drift scan. """

        for pol in pols:
            set_dict_item(self.__dict__,f'O{pol}TA',np.nan,"Peak antenna temperature [K]")
            set_dict_item(self.__dict__,f'O{pol}TAERR',np.nan,"Error in peak antenna temperature [K]")
            set_dict_item(self.__dict__,f'O{pol}S2N',np.nan,"signal to noise ratio")
            set_dict_item(self.__dict__,f'O{pol}TAPEAKLOC',np.nan,"Location of peak antenna temperature ")
            set_dict_item(self.__dict__,f'O{pol}RMSB',np.nan,"RMS before spline fit to all data")
            set_dict_item(self.__dict__,f'O{pol}RMSA',np.nan,"RMS after spline fit to all data")
            set_dict_item(self.__dict__,f'O{pol}BSLOPE',np.nan,"Slope of baseline correction")
            set_dict_item(self.__dict__,f'O{pol}BRMS',np.nan,"RMS of baseline correction fit")
            set_dict_item(self.__dict__,f"O{pol}FLAG",np.nan,f"ON scan {pol}CP flag parameter")

    def set_wb_dict(self):
        """ Combine wide beam common calibration parameters. """

        self.set_common_parameters()
        self.set_tau_parameters()
        self.set_wb_parameters(['L','R'])

    # =========================================================================
    #   NARROW BEAM, 6.7, 12 & 22 GHZ SCAN SETTINGS
    # =========================================================================

    def set_tau_parameters(self):
        """ Set tau (optical depth) parameters. """

        # TODO! Fix this NOW, figure out what exactly we are doing with the 15 GHz data
        #! Figure out where all these values come from
        if '02.5S' in self.__dict__['FRONTEND']['value']:
            # I think we decided to use the 10 GHz optical depth because its closer to 
            # 12 GHz, but need to confirm.

            set_dict_item(self.__dict__,f'TAU10',np.nan,"Optical depth at 10 GHz: # from SKA doc, i.e. measurements made in karnavon")
            set_dict_item(self.__dict__,f'TAU15',np.nan,"Optical depth at 15 GHz: # from Meeks 1976 exptl Physics 12B p175")
            set_dict_item(self.__dict__,f'MEAN_ATMOS_CORRECTION',np.nan,"Mean atmospheric correction.")
       
        elif '01.3S' in self.__dict__['FRONTEND']['value']:
            set_dict_item(self.__dict__,f'TAU221',np.nan,"Optical depth at 22.1 GHz: # from SKA doc")
            set_dict_item(self.__dict__,f'TAU2223',np.nan,"Optical depth at 22.23 GHz: ??")
        
        elif '13.0S' in self.__dict__['FRONTEND']['value']:
            set_dict_item(self.__dict__,f'MEAN_ATMOS_CORRECTION',np.nan,"Mean atmospheric correction")

    def set_tbatmos_parameters(self):
        """ Set tbatmos (atmospheric temperature) parameters. """

        # See  set_tau_parameters()
        if '02.5S' in self.__dict__['FRONTEND']['value']:
            set_dict_item(self.__dict__,f'TBATMOS10',np.nan,"Optical depth at 10 GHz")
            set_dict_item(self.__dict__,f'TBATMOS15',np.nan,"Optical depth at 15 GHz")
       
        elif '01.3S' in self.__dict__['FRONTEND']['value']:
            set_dict_item(self.__dict__,f'TBATMOS221',np.nan,"Optical depth at 22.1 GHz")
            set_dict_item(self.__dict__,f'TBATMOS2223',np.nan,"Optical depth at 22.23 GHz")

    def set_comm_weather_parameters(self):
        """
        Set Common weather parameters.
        """

        # TODO: finalize descriptions
        set_dict_item(self.__dict__,f'PWV',np.nan,"Precipitable water vapour")
        set_dict_item(self.__dict__,f'SVP',np.nan,"Saturated vapour pressure")
        set_dict_item(self.__dict__,f'AVP',np.nan,"Ambient vapour pressure")
        set_dict_item(self.__dict__,f'DPT',np.nan,"Dew point temperature")
        set_dict_item(self.__dict__,f'WVD',np.nan,"Water vapor density")

    def set_nb_fit_parameters(self,pols,scanDirection):
        """
        Set the parameters specific to a narrow beam drift scan.

        Attributes:
        -----------
            pols : list
                List of polarizations - left circular polarization: LCP (L), : right circular polarization RCP (R).
            scanDirection : list
                List of scan directions - north (N), south (S) or center ON (O). Using O because C makes things confusing.
        """

        for pol in pols:
            for direction in scanDirection:
                set_dict_item(self.__dict__,f'{direction}{pol}TA',np.nan,f"Peak antenna temperature [K] for {direction} {pol}CP")
                set_dict_item(self.__dict__,f'{direction}{pol}TAERR',np.nan,f"Error in peak antenna temperature [K] for {direction} {pol}CP")
                
                if direction == 'C':
                    set_dict_item(self.__dict__,f'{direction}{pol}PC',np.nan,f"Pointing correction factor for {direction} {pol}CP")
                    set_dict_item(self.__dict__,f'C{direction}{pol}TA',np.nan,f"Peak CORRECTED antenna temperature [K] for {direction} {pol}CP")
                    set_dict_item(self.__dict__,f'C{direction}{pol}TAERR',np.nan,f"Error in peak CORRECTED antenna temperature [K] for {direction} {pol}CP")
                
                set_dict_item(self.__dict__,f'{direction}{pol}S2N',np.nan,f"signal to noise ratio for {direction} {pol}CP ")
                set_dict_item(self.__dict__,f'{direction}{pol}TAPEAKLOC',np.nan,f"Location of peak antenna temperature for {direction} {pol}CP ")
                set_dict_item(self.__dict__,f'{direction}{pol}RMSB',np.nan,f"RMS before spline fit to all data for {direction} {pol}CP ")
                set_dict_item(self.__dict__,f'{direction}{pol}RMSA',np.nan,f"RMS after spline fit to all data for {direction} {pol}CP ")
                set_dict_item(self.__dict__,f'{direction}{pol}BSLOPE',np.nan,f"Slope of baseline correction for {direction} {pol}CP ")
                set_dict_item(self.__dict__,f'{direction}{pol}BRMS',np.nan,f"RMS of baseline correction fit for {direction} {pol}CP ")
                set_dict_item(self.__dict__,f"{direction}{pol}FLAG",np.nan,f"{direction} scan {pol}CP flag parameter")

    def set_nb_dict(self):
        """
            Set Narrow beam calibration data dictionary.
        """

        self.set_common_parameters()
        self.set_comm_weather_parameters()
        self.set_tau_parameters()
        self.set_tbatmos_parameters()
        self.set_nb_fit_parameters(['L','R'],['N','S','O'])

    # =========================================================================
    #   DUAL BEAM, 4.8 & 8.4 GHz SETTINGS
    # =========================================================================

    def set_db_fit_parameters(self,pols,beams,scanDirection):
        """
        Set dual beam fit parameters.

        Attributes:
        -----------
        pols : list
            List of polarizations - left circular polarization: LCP (L), : right circular polarization RCP (R).
        beams : list
            List of drift scan beams - left (A) and right (B), beams are either +ve or -ve depending on frequency.
        scanDirection : list
            List of scan directions - north (N), south (S) or center ON (O). Using O because C makes things confusing.
        
        """

        for pol in pols:
            for beam in beams:
                for direction in scanDirection:
                    set_dict_item(self.__dict__,f'{beam}{direction}{pol}TA',np.nan,f"Peak antenna temperature [K] for {beam} beam {direction} {pol}CP")
                    set_dict_item(self.__dict__,f'{beam}{direction}{pol}TAERR',np.nan,f"Error in peak antenna temperature [K] for {beam} beam {direction} {pol}CP")
                
                    if direction == 'O':
                        set_dict_item(self.__dict__,f'{beam}{direction}{pol}PC',np.nan,f"Pointing correction factor for {beam} beam {direction} {pol}CP")
                        set_dict_item(self.__dict__,f'{beam}C{direction}{pol}TA',np.nan,f"Peak CORRECTED antenna temperature [K] for {beam} beam {direction} {pol}CP")
                        set_dict_item(self.__dict__,f'{beam}C{direction}{pol}TAERR',np.nan,f"Error in peak CORRECTED antenna temperature [K] for {beam} beam {direction} {pol}CP")
                    
                    set_dict_item(self.__dict__,f'{beam}{direction}{pol}S2N',np.nan,f"signal to noise ratio for {beam} beam {direction} {pol}CP ")
                    set_dict_item(self.__dict__,f'{beam}{direction}{pol}TAPEAKLOC',np.nan,f"Location of peak antenna temperature for {beam} beam {direction} {pol}CP ")
                    set_dict_item(self.__dict__,f'{beam}{direction}{pol}RMSB',np.nan,f"RMS before spline fit to all data for {beam} beam {direction} {pol}CP ")
                    set_dict_item(self.__dict__,f'{beam}{direction}{pol}RMSA',np.nan,f"RMS after spline fit to all data for {beam} beam {direction} {pol}CP ")
                    set_dict_item(self.__dict__,f'{beam}{direction}{pol}BSLOPE',np.nan,f"Slope of baseline correction for {beam} beam {direction} {pol}CP ")
                    set_dict_item(self.__dict__,f'{beam}{direction}{pol}BRMS',np.nan,f"RMS of baseline correction fit for {beam} beam {direction} {pol}CP ")
                    set_dict_item(self.__dict__,f"{beam}{direction}{pol}FLAG",np.nan,f"{beam} beam {direction} scan {pol}CP flag parameter")

    def set_db_weather_parameters(self):
        """
        Set dual beam weather related parameters.
        """

        # TODO: finalize descriptions
        # find out exactly what these mean or do
        set_dict_item(self.__dict__,f'SEC_Z',np.nan,"secant of zenith ???")
        set_dict_item(self.__dict__,f'X_Z',np.nan,"")
        set_dict_item(self.__dict__,f'DRY_ATMOS_TRANSMISSION',np.nan,"dry atmospheric transmission")
        set_dict_item(self.__dict__,f'ZENITH_TAU_AT_1400M',np.nan,"zenith tau (optical depth) at 1400m")
        set_dict_item(self.__dict__,f'ABSORPTION_AT_ZENITH',np.nan,"absorption at zenith")

    def set_db_dict(self):
        """
        Set dual beam observation parameters.
        """

        self.set_comm_weather_parameters()
        self.set_db_weather_parameters()
        self.set_db_fit_parameters(['L','R'],['A','B'],['N','S','O'])