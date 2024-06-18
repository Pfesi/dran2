# =========================================================================== #
# File   : miscellaneousFunctions.py                                          #
# Author : Pfesesani V. van Zyl                                               #
# =========================================================================== #

# Standard library imports
# --------------------------------------------------------------------------- #
import numpy as np
import os
# =========================================================================== #

from .msgConfiguration import msg_wrapper
try:
    from ..config import logfile
except:
    from config import logfile
    
def set_dict_item(dictionary,key,value,description) -> None:
    """
    Set dictionary key, value and description

    Args:
        key (str): the key you are creating for the dictionary entry
        value (str,float,list,dict or int): the value of the dictionary entry
        description (_type_): the description of the dictionary entry
    """
    dictionary[key] = {'value':value, 'description':description}

def delete_object(objectName) -> None:
    """
    Delete an object from memory

    Args:
        objectName (str): the name of the object to delete
    """
    del objectName

def calc_log_freq(freq):
    """ Calculate the log(frequency) """

    # msg_wrapper("debug", self.log.debug, "Calculating log of frequency")
    try:
        logFreq = np.log10(float(freq))
    except:
        logFreq = np.nan
        # msg_wrapper("warning", self.log.debug, "missing 'CENTFREQ', setting it to NAN")
    return logFreq

def check_for_nans(x,log):
        """ Check for missing data or incomplete data.
        
            Parameters:
                x (array): A 1D array
                log (object): Logging object.
            
            Returns:
                flag (int): The flag value
                x (array) : A 1D array without any NAN values
        """

        isNan = np.argwhere(np.isnan(x))
        if len(isNan) > 0 or len(x) == 0:
            msg_wrapper("critical", log.critical,
                        "Found NANs, file has no data: skipping processing")
            x = np.zeros_like(x)
            flag = 1
            return x, flag
        else:
            msg_wrapper("debug", log.debug,
                        "Checked data for missing values")
            flag = 0
            return x, flag
        
def create_current_scan_directory():
        try:
            os.system('rm -r currentScanPlots')
        except:
            pass
        try:
            os.mkdir('currentScanPlots')
        except:
            pass

def catch_zeroDivError(col,colerr):
    try:
        return (colerr/col)
    except ZeroDivisionError:
        return 0
    
def sig_to_noise(signalPeak, noise,log):
    """ 
    Calculate the signal to noise ratio. i.e. Amplitude / (stdDeviation of noise)
    Taken from paper on 'Signal to Noise Ratio (SNR) Enhancement Comparison of Impulse-, 
    Coding- and Novel Linear-Frequency-Chirp-Based Optical Time Domain Reflectometry 
    (OTDR) for Passive Optical Network (PON) Monitoring Based on Unique Combinations of 
    Wavelength Selective Mirrors'

    Photonics 2014, 1, 33-46; doi:10.3390/photonics1010033
    https://www.mdpi.com/2304-6732/1/1/33
    https://www.mdpi.com/68484
    
    Args:
        signalPeak (float) : The maximum valueof a desired signal
        noise (array): array of fit residuals
        log(object): file logging object
        
    Returns:
        sig2noise (float): signal to noise ratio
    """

    msg=f'Calculate the signal to noise ratio'
    msg_wrapper("debug",log.debug,msg)

    sig2noise = signalPeak/np.std(noise)
    #sig2noise = signalPeak/(max(noise)+abs(min(noise)))
    return sig2noise

def delete_logs():
    """
    Delete the logfile if it exists
    """
    # delete any previous log file
    try:
        os.remove(logfile)
    except OSError:
        pass

def set_table_name(src,log):
    """
    Set the table name based on the declination.

    Args:
        src (str): source or table name
    """

    msg=f'Fromat database atable name for {src}'
    msg_wrapper("debug",log.debug,msg)

    if '-' in src:  
        src=src.replace('-','m').upper()
    elif '+' in src:
        src=src.replace('+','p').upper()

    return src

def fast_scandir(dirname):
    '''Scan directory for all folders in the given directory'''

    print(f'Scanning the {dirname} directory')
    subfolders= [f.path for f in os.scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(fast_scandir(dirname))
    return subfolders

# def reset_lists(listName):
#     listName = []