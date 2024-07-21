# ============================================================================#
# File: _auto.py                                                              #
# Author: Pfesesani V. van Zyl                                                #
# =========================================================================== #

# Standard library imports
# --------------------------------------------------------------------------- #
import os, sys
from dataclasses import dataclass, field
import numpy as np
from datetime import datetime
import argparse
from config import __version__, __DBNAME__ #, dbCols, nbCols, sbCols
import pandas as pd
import sqlite3
# from glob import glob
# import fnmatch

# Module imports
# --------------------------------------------------------------------------- #
import common.exceptions as ex
from common.contextManagers import open_file
from common.driftScans import DriftScans
from common.enums import ScanType
from common.miscellaneousFunctions import set_dict_item, create_current_scan_directory, delete_logs, set_table_name,fast_scandir
from common.logConfiguration import configure_logging
from common.msgConfiguration import msg_wrapper, load_prog
from common.sqlite_db import SQLiteDB
from common.observation import Observation
from common.contextManagers import open_database
# =========================================================================== #

# column data to save
dbCols={'FILENAME':'TEXT','FILEPATH':'TEXT','CURDATETIME':'TEXT','MJD':'REAL','OBSDATE':'TEXT','OBSTIME':'TEXT',
                  'OBSDATETIME':'TEXT','FRONTEND':'TEXT','HDULENGTH':'INTEGER','OBJECT':'TEXT','SRC':'TEXT','OBSERVER':'TEXT',
                  'OBSLOCAL':'TEXT','OBSNAME':'TEXT','PROJNAME':'TEXT','PROPOSAL':'TEXT','TELESCOP':'TEXT','UPGRADE':'TEXT',
                    'CENTFREQ':'REAL','BANDWDTH':'REAL','LOGFREQ':'REAL','BEAMTYPE':'TEXT','HPBW':'REAL','FNBW':'REAL','SNBW':'REAL',
                    'FEEDTYPE':'TEXT','LONGITUD':'REAL','LATITUDE':'REAL','COORDSYS':'REAL','EQUINOX':'REAL','RADECSYS':'TEXT',
                    'FOCUS':'REAL','TILT':'REAL','TAMBIENT':'REAL','PRESSURE':'REAL','HUMIDITY':'REAL','WINDSPD':'REAL','SCANDIR':'TEXT',
                    'POINTING':'INTEGER','BMOFFHA':'REAL','BMOFFDEC':'REAL','HABMSEP':'REAL',
                    'DICHROIC':'TEXT','PHASECAL':'TEXT','NOMTSYS':'REAL','SCANDIST':'REAL','SCANTIME':'REAL','INSTRUME':'TEXT',
                    'INSTFLAG':'TEXT','HZPERK1':'REAL','HZKERR1':'REAL','HZPERK2':'REAL','HZKERR2':'REAL',
                    'TCAL1':'REAL','TCAL2':'REAL','TSYS1':'REAL','TSYSERR1':'REAL','TSYS2':'REAL','TSYSERR2':'REAL','ELEVATION':'REAL',
                    'ZA':'REAL','HA':'REAL','PWV':'REAL','SVP':'REAL','AVP':'REAL','DPT':'REAL','WVD':'REAL','SEC_Z':'REAL','X_Z':'REAL',
                    'DRY_ATMOS_TRANSMISSION':'REAL','ZENITH_TAU_AT_1400M':'REAL','ABSORPTION_AT_ZENITH':'REAL',
                    
                    'ANLTA':'REAL','ANLTAERR':'REAL','ANLMIDOFFSET':'REAL','ANLS2N':'REAL', 
                    'BNLTA':'REAL','BNLTAERR':'REAL','BNLMIDOFFSET':'REAL','BNLS2N':'REAL',
                    'NLFLAG':'REAL','NLBRMS':'REAL','NLSLOPE':'REAL',
                    'ANLBASELOCS':'REAL','BNLBASELOCS':'REAL','NLRMSB':'REAL', 'NLRMSA':'REAL',
                    
                    'ASLTA':'REAL','ASLTAERR':'REAL','ASLMIDOFFSET':'REAL','ASLS2N':'REAL', 
                    'BSLTA':'REAL','BSLTAERR':'REAL','BSLMIDOFFSET':'REAL','BSLS2N':'REAL',
                    'SLFLAG':'REAL','SLBRMS':'REAL','SLSLOPE':'REAL','ASLBASELOCS':'REAL','BSLBASELOCS':'REAL', 'SLRMSB':'REAL', 'SLRMSA':'REAL',
                    
                    'AOLTA':'REAL','AOLTAERR':'REAL','AOLMIDOFFSET':'REAL','AOLS2N':'REAL',
                    'BOLTA':'REAL','BOLTAERR':'REAL','BOLMIDOFFSET':'REAL','BOLS2N':'REAL',
                    'OLFLAG':'REAL','OLBRMS':'REAL','OLSLOPE':'REAL','AOLBASELOCS':'REAL','BOLBASELOCS':'REAL', 'OLRMSB':'REAL', 'OLRMSA':'REAL',
                    'AOLPC':'REAL','ACOLTA':'REAL','ACOLTAERR':'REAL','BOLPC':'REAL','BCOLTA':'REAL','BCOLTAERR':'REAL',
                    
                    'ANRTA':'REAL','ANRTAERR':'REAL','ANRMIDOFFSET':'REAL','ANRS2N':'REAL',
                    'BNRTA':'REAL','BNRTAERR':'REAL','BNRMIDOFFSET':'REAL','BNRS2N':'REAL',
                    'NRFLAG':'REAL','NRBRMS':'REAL','NRSLOPE':'REAL','ANRBASELOCS':'REAL','BNRBASELOCS':'REAL','NRRMSB':'REAL', 'NRRMSA':'REAL',

                    'ASRTA':'REAL','ASRTAERR':'REAL','ASRMIDOFFSET':'REAL','ASRS2N':'REAL',
                    'BSRTA':'REAL','BSRTAERR':'REAL','BSRMIDOFFSET':'REAL','BSRS2N':'REAL',
                    'SRFLAG':'REAL','SRBRMS':'REAL','SRSLOPE':'REAL','ASRBASELOCS':'REAL','BSRBASELOCS':'REAL','SRRMSB':'REAL', 'SRRMSA':'REAL',

                    'AORTA':'REAL','AORTAERR':'REAL','AORMIDOFFSET':'REAL','AORS2N':'REAL',
                    'BORTA':'REAL','BORTAERR':'REAL','BORMIDOFFSET':'REAL','BORS2N':'REAL',
                    'ORFLAG':'REAL','ORBRMS':'REAL','ORSLOPE':'REAL','AORBASELOCS':'REAL','BORBASELOCS':'REAL','ORRMSB':'REAL', 'ORRMSA':'REAL',
                    'AORPC':'REAL','ACORTA':'REAL','ACORTAERR':'REAL','BORPC':'REAL','BCORTA':'REAL','BCORTAERR':'REAL'}

nbCols={'FILENAME':'TEXT','FILEPATH':'TEXT','CURDATETIME':'TEXT','MJD':'REAL','OBSDATE':'TEXT','OBSTIME':'TEXT',
                  'OBSDATETIME':'TEXT','FRONTEND':'TEXT','HDULENGTH':'INTEGER','OBJECT':'TEXT','SRC':'TEXT','OBSERVER':'TEXT',
                  'OBSLOCAL':'TEXT','OBSNAME':'TEXT','PROJNAME':'TEXT','PROPOSAL':'TEXT','TELESCOP':'TEXT','UPGRADE':'TEXT',
                    'CENTFREQ':'REAL','BANDWDTH':'REAL','LOGFREQ':'REAL','BEAMTYPE':'TEXT','HPBW':'REAL','FNBW':'REAL','SNBW':'REAL',
                    'FEEDTYPE':'TEXT','LONGITUD':'REAL','LATITUDE':'REAL','COORDSYS':'REAL','EQUINOX':'REAL','RADECSYS':'TEXT',
                    'FOCUS':'REAL','TILT':'REAL','TAMBIENT':'REAL','PRESSURE':'REAL','HUMIDITY':'REAL','WINDSPD':'REAL','SCANDIR':'TEXT',
                    'POINTING':'INTEGER','BMOFFHA':'REAL','BMOFFDEC':'REAL','HABMSEP':'REAL',
                    'DICHROIC':'TEXT','PHASECAL':'TEXT','NOMTSYS':'REAL','SCANDIST':'REAL','SCANTIME':'REAL','INSTRUME':'TEXT',
                    'INSTFLAG':'TEXT','HZPERK1':'REAL','HZKERR1':'REAL','HZPERK2':'REAL','HZKERR2':'REAL',
                    'TCAL1':'REAL','TCAL2':'REAL','TSYS1':'REAL','TSYSERR1':'REAL','TSYS2':'REAL','TSYSERR2':'REAL','ELEVATION':'REAL',
                    'ZA':'REAL','HA':'REAL','PWV':'REAL','SVP':'REAL','AVP':'REAL','DPT':'REAL','WVD':'REAL',

                    'MEAN_ATMOS_CORRECTION':'REAL','TAU10':'REAL','TAU15':'REAL','TBATMOS10':'REAL','TBATMOS15':'REAL',
                    
                    'NLTA':'REAL','NLTAERR':'REAL','NLMIDOFFSET':'REAL','NLS2N':'REAL', 
                    'NLFLAG':'REAL','NLBRMS':'REAL','NLSLOPE':'REAL',
                    'NLBASELEFT':'REAL','NLBASERIGHT':'REAL',
                    'NLRMSB':'REAL', 'NLRMSA':'REAL',
                    
                    'SLTA':'REAL','SLTAERR':'REAL','SLMIDOFFSET':'REAL','SLS2N':'REAL', 
                    'SLFLAG':'REAL','SLBRMS':'REAL','SLSLOPE':'REAL',
                    'SLBASELEFT':'REAL','SLBASERIGHT':'REAL',
                    'SLRMSB':'REAL', 'SLRMSA':'REAL',
                    
                    'OLTA':'REAL','OLTAERR':'REAL','OLMIDOFFSET':'REAL','OLS2N':'REAL',
                    'OLFLAG':'REAL','OLBRMS':'REAL','OLSLOPE':'REAL',
                    'OLBASELEFT':'REAL','OLBASERIGHT':'REAL',
                    'OLRMSB':'REAL', 'OLRMSA':'REAL',
                    'OLPC':'REAL','COLTA':'REAL','COLTAERR':'REAL',
                    
                    'NRTA':'REAL','NRTAERR':'REAL','NRMIDOFFSET':'REAL','NRS2N':'REAL',
                    'NRFLAG':'REAL','NRBRMS':'REAL','NRSLOPE':'REAL',
                    'NRBASELEFT':'REAL','NRBASERIGHT':'REAL',
                    'NRRMSB':'REAL', 'NRRMSA':'REAL',

                    'SRTA':'REAL','SRTAERR':'REAL','SRMIDOFFSET':'REAL','SRS2N':'REAL',
                    'SRFLAG':'REAL','SRBRMS':'REAL','SRSLOPE':'REAL',
                    'SRBASELEFT':'REAL','SRBASERIGHT':'REAL',
                    'SRRMSB':'REAL', 'SRRMSA':'REAL',

                    'ORTA':'REAL','ORTAERR':'REAL','ORMIDOFFSET':'REAL','ORS2N':'REAL',
                    'ORFLAG':'REAL','ORBRMS':'REAL','ORSLOPE':'REAL',
                    'ORBASELEFT':'REAL','ORBASERIGHT':'REAL',
                    'ORRMSB':'REAL', 'ORRMSA':'REAL',
                    'ORPC':'REAL','CORTA':'REAL','CORTAERR':'REAL'}

nbCols22jup={'FILENAME':'TEXT','FILEPATH':'TEXT','CURDATETIME':'TEXT','MJD':'REAL','OBSDATE':'TEXT','OBSTIME':'TEXT',
                  'OBSDATETIME':'TEXT','FRONTEND':'TEXT','HDULENGTH':'INTEGER','OBJECT':'TEXT','SRC':'TEXT','OBSERVER':'TEXT',
                  'OBSLOCAL':'TEXT','OBSNAME':'TEXT','PROJNAME':'TEXT','PROPOSAL':'TEXT','TELESCOP':'TEXT','UPGRADE':'TEXT',
                    'CENTFREQ':'REAL','BANDWDTH':'REAL','LOGFREQ':'REAL','BEAMTYPE':'TEXT','HPBW':'REAL','FNBW':'REAL','SNBW':'REAL',
                    'FEEDTYPE':'TEXT','LONGITUD':'REAL','LATITUDE':'REAL','COORDSYS':'REAL','EQUINOX':'REAL','RADECSYS':'TEXT',
                    'FOCUS':'REAL','TILT':'REAL','TAMBIENT':'REAL','PRESSURE':'REAL','HUMIDITY':'REAL','WINDSPD':'REAL','SCANDIR':'TEXT',
                    'POINTING':'INTEGER','BMOFFHA':'REAL','BMOFFDEC':'REAL','HABMSEP':'REAL',
                    'DICHROIC':'TEXT','PHASECAL':'TEXT','NOMTSYS':'REAL','SCANDIST':'REAL','SCANTIME':'REAL','INSTRUME':'TEXT',
                    'INSTFLAG':'TEXT','HZPERK1':'REAL','HZKERR1':'REAL','HZPERK2':'REAL','HZKERR2':'REAL',
                    'TCAL1':'REAL','TCAL2':'REAL','TSYS1':'REAL','TSYSERR1':'REAL','TSYS2':'REAL','TSYSERR2':'REAL','ELEVATION':'REAL',
                    'ZA':'REAL','HA':'REAL','PWV':'REAL','SVP':'REAL','AVP':'REAL','DPT':'REAL','WVD':'REAL',

                    'HPBW_ARCSEC':'REAL','ADOPTED_PLANET_TB':'REAL','PLANET_ANG_DIAM':'REAL','JUPITER_DIST_AU':'REAL',
                    'SYNCH_FLUX_DENSITY':'REAL','PLANET_ANG_EQ_RAD':'REAL','PLANET_SOLID_ANG':'REAL','THERMAL_PLANET_FLUX_D':'REAL',
                    'TOTAL_PLANET_FLUX_D':'REAL','TOTAL_PLANET_FLUX_D_WMAP':'REAL','SIZE_FACTOR_IN_BEAM':'REAL','SIZE_CORRECTION_FACTOR':'REAL',
                    'MEASURED_TCAL1':'REAL','MEASURED_TCAL2':'REAL','MEAS_TCAL1_CORR_FACTOR':'REAL','MEAS_TCAL2_CORR_FACTOR':'REAL',
                    'ATMOS_ABSORPTION_CORR':'REAL','ZA_RAD':'REAL','TAU221':'REAL','TAU2223':'REAL',
                    'TBATMOS221':'REAL','TBATMOS2223':'REAL',

                    'NLTA':'REAL','NLTAERR':'REAL','NLMIDOFFSET':'REAL','NLS2N':'REAL', 
                    'NLFLAG':'REAL','NLBRMS':'REAL','NLSLOPE':'REAL',
                    'NLBASELEFT':'REAL','NLBASERIGHT':'REAL',
                    'NLRMSB':'REAL', 'NLRMSA':'REAL',
                    
                    'SLTA':'REAL','SLTAERR':'REAL','SLMIDOFFSET':'REAL','SLS2N':'REAL', 
                    'SLFLAG':'REAL','SLBRMS':'REAL','SLSLOPE':'REAL',
                    'SLBASELEFT':'REAL','SLBASERIGHT':'REAL',
                    'SLRMSB':'REAL', 'SLRMSA':'REAL',
                    
                    'OLTA':'REAL','OLTAERR':'REAL','OLMIDOFFSET':'REAL','OLS2N':'REAL',
                    'OLFLAG':'REAL','OLBRMS':'REAL','OLSLOPE':'REAL',
                    'OLBASELEFT':'REAL','OLBASERIGHT':'REAL',
                    'OLRMSB':'REAL', 'OLRMSA':'REAL',
                    'OLPC':'REAL','COLTA':'REAL','COLTAERR':'REAL',
                    
                    'NRTA':'REAL','NRTAERR':'REAL','NRMIDOFFSET':'REAL','NRS2N':'REAL',
                    'NRFLAG':'REAL','NRBRMS':'REAL','NRSLOPE':'REAL',
                    'NRBASELEFT':'REAL','NRBASERIGHT':'REAL',
                    'NRRMSB':'REAL', 'NRRMSA':'REAL',

                    'SRTA':'REAL','SRTAERR':'REAL','SRMIDOFFSET':'REAL','SRS2N':'REAL',
                    'SRFLAG':'REAL','SRBRMS':'REAL','SRSLOPE':'REAL',
                    'SRBASELEFT':'REAL','SRBASERIGHT':'REAL',
                    'SRRMSB':'REAL', 'SRRMSA':'REAL',

                    'ORTA':'REAL','ORTAERR':'REAL','ORMIDOFFSET':'REAL','ORS2N':'REAL',
                    'ORFLAG':'REAL','ORBRMS':'REAL','ORSLOPE':'REAL',
                    'ORBASELEFT':'REAL','ORBASERIGHT':'REAL',
                    'ORRMSB':'REAL', 'ORRMSA':'REAL',
                    'ORPC':'REAL','CORTA':'REAL','CORTAERR':'REAL'}

nbCols22={'FILENAME':'TEXT','FILEPATH':'TEXT','CURDATETIME':'TEXT','MJD':'REAL','OBSDATE':'TEXT','OBSTIME':'TEXT',
                  'OBSDATETIME':'TEXT','FRONTEND':'TEXT','HDULENGTH':'INTEGER','OBJECT':'TEXT','SRC':'TEXT','OBSERVER':'TEXT',
                  'OBSLOCAL':'TEXT','OBSNAME':'TEXT','PROJNAME':'TEXT','PROPOSAL':'TEXT','TELESCOP':'TEXT','UPGRADE':'TEXT',
                    'CENTFREQ':'REAL','BANDWDTH':'REAL','LOGFREQ':'REAL','BEAMTYPE':'TEXT','HPBW':'REAL','FNBW':'REAL','SNBW':'REAL',
                    'FEEDTYPE':'TEXT','LONGITUD':'REAL','LATITUDE':'REAL','COORDSYS':'REAL','EQUINOX':'REAL','RADECSYS':'TEXT',
                    'FOCUS':'REAL','TILT':'REAL','TAMBIENT':'REAL','PRESSURE':'REAL','HUMIDITY':'REAL','WINDSPD':'REAL','SCANDIR':'TEXT',
                    'POINTING':'INTEGER','BMOFFHA':'REAL','BMOFFDEC':'REAL',#'HABMSEP':'REAL',
                    'DICHROIC':'TEXT','PHASECAL':'TEXT','NOMTSYS':'REAL','SCANDIST':'REAL','SCANTIME':'REAL','INSTRUME':'TEXT',
                    'INSTFLAG':'TEXT','HZPERK1':'REAL','HZKERR1':'REAL','HZPERK2':'REAL','HZKERR2':'REAL',
                    'TCAL1':'REAL','TCAL2':'REAL','TSYS1':'REAL','TSYSERR1':'REAL','TSYS2':'REAL','TSYSERR2':'REAL','ELEVATION':'REAL',
                    'ZA':'REAL','HA':'REAL','PWV':'REAL','SVP':'REAL','AVP':'REAL','DPT':'REAL','WVD':'REAL',

                    #'HPBW_ARCSEC':'REAL',
                    #'ADOPTED_PLANET_TB':'REAL','PLANET_ANG_DIAM':'REAL','JUPITER_DIST_AU':'REAL',
                    #'SYNCH_FLUX_DENSITY':'REAL','PLANET_ANG_EQ_RAD':'REAL','PLANET_SOLID_ANG':'REAL','THERMAL_PLANET_FLUX_D':'REAL',
                    #'TOTAL_PLANET_FLUX_D':'REAL','TOTAL_PLANET_FLUX_D_WMAP':'REAL','SIZE_FACTOR_IN_BEAM':'REAL','SIZE_CORRECTION_FACTOR':'REAL',
                    # 'MEASURED_TCAL1':'REAL','MEASURED_TCAL2':'REAL','MEAS_TCAL1_CORR_FACTOR':'REAL','MEAS_TCAL2_CORR_FACTOR':'REAL',
                    
                    #'ATMOS_ABSORPTION_CORR':'REAL','ZA_RAD':'REAL',
                    'TAU221':'REAL','TAU2223':'REAL',
                    'TBATMOS221':'REAL','TBATMOS2223':'REAL',

                    'NLTA':'REAL','NLTAERR':'REAL','NLMIDOFFSET':'REAL','NLS2N':'REAL', 
                    'NLFLAG':'REAL','NLBRMS':'REAL','NLSLOPE':'REAL',
                    'NLBASELEFT':'REAL','NLBASERIGHT':'REAL',
                    'NLRMSB':'REAL', 'NLRMSA':'REAL',
                    
                    'SLTA':'REAL','SLTAERR':'REAL','SLMIDOFFSET':'REAL','SLS2N':'REAL', 
                    'SLFLAG':'REAL','SLBRMS':'REAL','SLSLOPE':'REAL',
                    'SLBASELEFT':'REAL','SLBASERIGHT':'REAL',
                    'SLRMSB':'REAL', 'SLRMSA':'REAL',
                    
                    'OLTA':'REAL','OLTAERR':'REAL','OLMIDOFFSET':'REAL','OLS2N':'REAL',
                    'OLFLAG':'REAL','OLBRMS':'REAL','OLSLOPE':'REAL',
                    'OLBASELEFT':'REAL','OLBASERIGHT':'REAL',
                    'OLRMSB':'REAL', 'OLRMSA':'REAL',
                    'OLPC':'REAL','COLTA':'REAL','COLTAERR':'REAL',
                    
                    'NRTA':'REAL','NRTAERR':'REAL','NRMIDOFFSET':'REAL','NRS2N':'REAL',
                    'NRFLAG':'REAL','NRBRMS':'REAL','NRSLOPE':'REAL',
                    'NRBASELEFT':'REAL','NRBASERIGHT':'REAL',
                    'NRRMSB':'REAL', 'NRRMSA':'REAL',

                    'SRTA':'REAL','SRTAERR':'REAL','SRMIDOFFSET':'REAL','ASRS2N':'REAL',
                    'SRFLAG':'REAL','SRBRMS':'REAL','SRSLOPE':'REAL',
                    'SRBASELEFT':'REAL','SRBASERIGHT':'REAL',
                    'SRRMSB':'REAL', 'SRRMSA':'REAL',

                    'ORTA':'REAL','ORTAERR':'REAL','ORMIDOFFSET':'REAL','AORS2N':'REAL',
                    'ORFLAG':'REAL','ORBRMS':'REAL','ORSLOPE':'REAL',
                    'ORBASELEFT':'REAL','ORBASERIGHT':'REAL',
                    'ORRMSB':'REAL', 'ORRMSA':'REAL',
                    'ORPC':'REAL','CORTA':'REAL','CORTAERR':'REAL'}

sbCols={'FILENAME':'TEXT','FILEPATH':'TEXT','CURDATETIME':'TEXT','MJD':'REAL','OBSDATE':'TEXT','OBSTIME':'TEXT',
        'OBSDATETIME':'TEXT','FRONTEND':'TEXT','HDULENGTH':'INTEGER','OBJECT':'TEXT','SRC':'TEXT','OBSERVER':'TEXT',
        'OBSLOCAL':'TEXT','OBSNAME':'TEXT','PROJNAME':'TEXT','PROPOSAL':'TEXT','TELESCOP':'TEXT','UPGRADE':'TEXT',
        'CENTFREQ':'REAL','BANDWDTH':'REAL','LOGFREQ':'REAL','BEAMTYPE':'TEXT','HPBW':'REAL','FNBW':'REAL','SNBW':'REAL',
        'FEEDTYPE':'TEXT','LONGITUD':'REAL','LATITUDE':'REAL','COORDSYS':'REAL','EQUINOX':'REAL','RADECSYS':'TEXT',
        'FOCUS':'REAL','TILT':'REAL','TAMBIENT':'REAL','PRESSURE':'REAL',
        'HUMIDITY':'REAL','WINDSPD':'REAL','SCANDIR':'TEXT',
        'POINTING':'INTEGER','BMOFFHA':'REAL','BMOFFDEC':'REAL', 
                    #'HABMSEP':'REAL',
        'DICHROIC':'TEXT','PHASECAL':'TEXT','NOMTSYS':'REAL','SCANDIST':'REAL','SCANTIME':'REAL','INSTRUME':'TEXT',
        'INSTFLAG':'TEXT','HZPERK1':'REAL','HZKERR1':'REAL','HZPERK2':'REAL','HZKERR2':'REAL',
        'TCAL1':'REAL','TCAL2':'REAL','TSYS1':'REAL','TSYSERR1':'REAL','TSYS2':'REAL','TSYSERR2':'REAL','ELEVATION':'REAL',
        'ZA':'REAL','HA':'REAL', 'ATMOSABS':'REAL',
                    
        'PWV':'REAL', 'SVP':'REAL','AVP':'REAL','DPT':'REAL','WVD':'REAL',
                    
                    #'SEC_Z':'REAL','X_Z':'REAL',
                    #'DRY_ATMOS_TRANSMISSION':'REAL','ZENITH_TAU_AT_1400M':'REAL','ABSORPTION_AT_ZENITH':'REAL',
                    
        'OLTA':'REAL','OLTAERR':'REAL','OLMIDOFFSET':'REAL','OLS2N':'REAL',
        'OLFLAG':'REAL','OLBRMS':'REAL','OLSLOPE':'REAL',
        'OLBASELEFT':'REAL','OLBASERIGHT':'REAL',
        'OLRMSB':'REAL','OLRMSA':'REAL',
        
        'ORTA':'REAL','ORTAERR':'REAL','ORMIDOFFSET':'REAL','ORS2N':'REAL',
        'ORFLAG':'REAL','ORBRMS':'REAL','ORSLOPE':'REAL',
        'ORBASELEFT':'REAL','ORBASERIGHT':'REAL',
        'ORRMSB':'REAL','ORRMSA':'REAL'}
                   
def check_freqs(freq:int,log,src=''):
    # HartRAO frequency limits: https://www.sarao.ac.za/about/hartrao/hartrao-research-programmes/hartrao-26m-radio-telescope-details/
    # NASA limits: https://www.nasa.gov/general/what-are-the-spectrum-band-designators-and-bandwidths/


    # 18, 13,6,4.5,3.5,2.5,1.3 cm
    cols=[]
    colTypes=[]

    # CREATE TABLE HYDRAA_4600 (id INTEGER PRIMARY KEY AUTOINCREMENT, FILENAME TEXT UNIQUE , FILEPATH TEXT , HDULENGTH INTEGER , CURDATETIME TEXT , OBSDATE TEXT , OBSTIME TEXT , OBSDATETIME TEXT , OBJECT TEXT , LONGITUD REAL , LATITUDE REAL , COORDSYS TEXT , EQUINOX REAL , RADECSYS TEXT , OBSERVER TEXT , OBSLOCAL TEXT , PROJNAME TEXT , PROPOSAL TEXT , TELESCOP TEXT , UPGRADE TEXT , FOCUS REAL , TILT REAL , TAMBIENT REAL , PRESSURE REAL , HUMIDITY REAL , WINDSPD REAL , SCANDIR TEXT , POINTING INTEGER , FEEDTYPE TEXT , BMOFFHA REAL , BMOFFDEC REAL , HABMSEP REAL , HPBW REAL , FNBW REAL , SNBW REAL , DICHROIC TEXT , PHASECAL TEXT , NOMTSYS REAL , FRONTEND TEXT , TCAL1 REAL , TCAL2 REAL , HZPERK1 REAL , HZKERR1 REAL , HZPERK2 REAL , HZKERR2 REAL , CENTFREQ REAL , BANDWDTH REAL , INSTRUME TEXT , INSTFLAG TEXT , SCANDIST REAL , SCANTIME REAL , TSYS1 REAL , TSYSERR1 REAL , TSYS2 REAL , TSYSERR2 REAL , BEAMTYPE TEXT , LOGFREQ REAL , ELEVATION REAL , ZA REAL , MJD REAL , HA REAL , PWV REAL , SVP REAL , AVP REAL , DPT REAL , WVD REAL , SEC_Z REAL , X_Z REAL , DRY_ATMOS_TRANSMISSION REAL , ZENITH_TAU_AT_1400M REAL , ABSORPTION_AT_ZENITH REAL , OBSNAME TEXT , NLBRMS REAL , NLSLOPE REAL , ANLBASELOCS TEXT , BNLBASELOCS TEXT , ANLTA REAL , ANLTAERR REAL , BNLTA REAL , BNLTAERR REAL , ANLMIDOFFSET REAL , BNLMIDOFFSET REAL , NLFLAG INTEGER , ANLS2N REAL , BNLS2N REAL , SLBRMS REAL , SLSLOPE REAL , ASLBASELOCS TEXT , BSLBASELOCS TEXT , ASLTA REAL , ASLTAERR REAL , BSLTA REAL , BSLTAERR REAL , ASLMIDOFFSET REAL , BSLMIDOFFSET REAL , SLFLAG INTEGER , ASLS2N REAL , BSLS2N REAL , OLBRMS REAL , OLSLOPE REAL , AOLBASELOCS TEXT , BOLBASELOCS TEXT , AOLTA REAL , AOLTAERR REAL , BOLTA REAL , BOLTAERR REAL , AOLMIDOFFSET REAL , BOLMIDOFFSET REAL , OLFLAG INTEGER , AOLS2N REAL , BOLS2N REAL , NRBRMS REAL , NRSLOPE REAL , ANRBASELOCS TEXT , BNRBASELOCS TEXT , ANRTA REAL , ANRTAERR REAL , BNRTA REAL , BNRTAERR REAL , ANRMIDOFFSET REAL , BNRMIDOFFSET REAL , NRFLAG INTEGER , ANRS2N REAL , BNRS2N REAL , SRBRMS REAL , SRSLOPE REAL , ASRBASELOCS TEXT , BSRBASELOCS TEXT , ASRTA REAL , ASRTAERR REAL , BSRTA REAL , BSRTAERR REAL , ASRMIDOFFSET REAL , BSRMIDOFFSET REAL , SRFLAG INTEGER , ASRS2N REAL , BSRS2N REAL , ORBRMS REAL , ORSLOPE REAL , AORBASELOCS TEXT , BORBASELOCS TEXT , AORTA REAL , AORTAERR REAL , BORTA REAL , BORTAERR REAL , AORMIDOFFSET REAL , BORMIDOFFSET REAL , ORFLAG INTEGER , AORS2N REAL , BORS2N REAL , AOLPC REAL , ACOLTA REAL , ACOLTAERR REAL , BOLPC REAL , BCOLTA REAL , BCOLTAERR REAL , AORPC REAL , ACORTA REAL , ACORTAERR REAL , BORPC REAL , BCORTA REAL , BCORTAERR REAL , SRC TEXT )
    if freq >= 1000 and freq<= 2000: # 1662
        msg_wrapper('debug',log.debug,'Preparing 18cm column labels')
        colTypes=sbCols

    elif freq > 2000 and freq<= 4000: # 2280
        msg_wrapper('debug',log.debug,'Preparing 13cm column labels')
        colTypes=sbCols

    elif freq > 4000 and freq<= 6000: # 5000
        msg_wrapper('debug',log.debug,'Preparing 6cm column labels')
        colTypes=dbCols

    elif freq > 6000 and freq<= 8000: # 6670, maser science
        msg_wrapper('debug',log.debug,'Preparing 4.5cm column labels')
        colTypes=nbCols

    elif freq > 8000 and freq<= 12000: # 8580
        msg_wrapper('debug',log.debug,'Preparing 3.5cm column labels')
        colTypes=dbCols

    elif freq > 12000 and freq<= 18000: # 12180
        msg_wrapper('debug',log.debug,'Preparing 2.5cm column labels')
        colTypes=nbCols

    elif freq >= 18000 and freq<= 27000: # 23000
        if src.upper()=='JUPITER':
            msg_wrapper('debug',log.debug,'Preparing 1.3cm column labels')
            colTypes=nbCols22jup
        else:
            colTypes=nbCols22

    return colTypes

def create_table_cols(freq:int,log,src=''):
    # HartRAO frequency limits: https://www.sarao.ac.za/about/hartrao/hartrao-research-programmes/hartrao-26m-radio-telescope-details/
    # NASA limits: https://www.nasa.gov/general/what-are-the-spectrum-band-designators-and-bandwidths/

    # 18, 13,6,4.5,3.5,2.5,1.3 cm
    cols=[]
    colTypes=[]

    # CREATE TABLE HYDRAA_4600 (id INTEGER PRIMARY KEY AUTOINCREMENT, FILENAME TEXT UNIQUE , FILEPATH TEXT , HDULENGTH INTEGER , CURDATETIME TEXT , OBSDATE TEXT , OBSTIME TEXT , OBSDATETIME TEXT , OBJECT TEXT , LONGITUD REAL , LATITUDE REAL , COORDSYS TEXT , EQUINOX REAL , RADECSYS TEXT , OBSERVER TEXT , OBSLOCAL TEXT , PROJNAME TEXT , PROPOSAL TEXT , TELESCOP TEXT , UPGRADE TEXT , FOCUS REAL , TILT REAL , TAMBIENT REAL , PRESSURE REAL , HUMIDITY REAL , WINDSPD REAL , SCANDIR TEXT , POINTING INTEGER , FEEDTYPE TEXT , BMOFFHA REAL , BMOFFDEC REAL , HABMSEP REAL , HPBW REAL , FNBW REAL , SNBW REAL , DICHROIC TEXT , PHASECAL TEXT , NOMTSYS REAL , FRONTEND TEXT , TCAL1 REAL , TCAL2 REAL , HZPERK1 REAL , HZKERR1 REAL , HZPERK2 REAL , HZKERR2 REAL , CENTFREQ REAL , BANDWDTH REAL , INSTRUME TEXT , INSTFLAG TEXT , SCANDIST REAL , SCANTIME REAL , TSYS1 REAL , TSYSERR1 REAL , TSYS2 REAL , TSYSERR2 REAL , BEAMTYPE TEXT , LOGFREQ REAL , ELEVATION REAL , ZA REAL , MJD REAL , HA REAL , PWV REAL , SVP REAL , AVP REAL , DPT REAL , WVD REAL , SEC_Z REAL , X_Z REAL , DRY_ATMOS_TRANSMISSION REAL , ZENITH_TAU_AT_1400M REAL , ABSORPTION_AT_ZENITH REAL , OBSNAME TEXT , NLBRMS REAL , NLSLOPE REAL , ANLBASELOCS TEXT , BNLBASELOCS TEXT , ANLTA REAL , ANLTAERR REAL , BNLTA REAL , BNLTAERR REAL , ANLMIDOFFSET REAL , BNLMIDOFFSET REAL , NLFLAG INTEGER , ANLS2N REAL , BNLS2N REAL , SLBRMS REAL , SLSLOPE REAL , ASLBASELOCS TEXT , BSLBASELOCS TEXT , ASLTA REAL , ASLTAERR REAL , BSLTA REAL , BSLTAERR REAL , ASLMIDOFFSET REAL , BSLMIDOFFSET REAL , SLFLAG INTEGER , ASLS2N REAL , BSLS2N REAL , OLBRMS REAL , OLSLOPE REAL , AOLBASELOCS TEXT , BOLBASELOCS TEXT , AOLTA REAL , AOLTAERR REAL , BOLTA REAL , BOLTAERR REAL , AOLMIDOFFSET REAL , BOLMIDOFFSET REAL , OLFLAG INTEGER , AOLS2N REAL , BOLS2N REAL , NRBRMS REAL , NRSLOPE REAL , ANRBASELOCS TEXT , BNRBASELOCS TEXT , ANRTA REAL , ANRTAERR REAL , BNRTA REAL , BNRTAERR REAL , ANRMIDOFFSET REAL , BNRMIDOFFSET REAL , NRFLAG INTEGER , ANRS2N REAL , BNRS2N REAL , SRBRMS REAL , SRSLOPE REAL , ASRBASELOCS TEXT , BSRBASELOCS TEXT , ASRTA REAL , ASRTAERR REAL , BSRTA REAL , BSRTAERR REAL , ASRMIDOFFSET REAL , BSRMIDOFFSET REAL , SRFLAG INTEGER , ASRS2N REAL , BSRS2N REAL , ORBRMS REAL , ORSLOPE REAL , AORBASELOCS TEXT , BORBASELOCS TEXT , AORTA REAL , AORTAERR REAL , BORTA REAL , BORTAERR REAL , AORMIDOFFSET REAL , BORMIDOFFSET REAL , ORFLAG INTEGER , AORS2N REAL , BORS2N REAL , AOLPC REAL , ACOLTA REAL , ACOLTAERR REAL , BOLPC REAL , BCOLTA REAL , BCOLTAERR REAL , AORPC REAL , ACORTA REAL , ACORTAERR REAL , BORPC REAL , BCORTA REAL , BCORTAERR REAL , SRC TEXT )
    if freq >= 1000 and freq<= 2000: # 1662
        msg_wrapper('debug',log.debug,'Preparing 18cm column labels')
        colTypes=sbCols

    elif freq > 2000 and freq<= 4000: # 2280
        msg_wrapper('debug',log.debug,'Preparing 13cm column labels')
        colTypes=sbCols

    elif freq > 4000 and freq<= 6000: # 5000
        msg_wrapper('debug',log.debug,'Preparing 6cm column labels')
        colTypes=dbCols

    elif freq > 6000 and freq<= 8000: # 6670, maser science
        msg_wrapper('debug',log.debug,'Preparing 4.5cm column labels')
        colTypes=nbCols

    elif freq > 8000 and freq<= 12000: # 8580
        msg_wrapper('debug',log.debug,'Preparing 3.5cm column labels')
        colTypes=dbCols

    elif freq > 12000 and freq<= 18000: # 12180
        msg_wrapper('debug',log.debug,'Preparing 2.5cm column labels')
        colTypes=nbCols

    elif freq >= 18000 and freq<= 27000: # 23000
        if src.upper()=='JUPITER':
            msg_wrapper('debug',log.debug,'Preparing 1.3cm column labels')
            colTypes=nbCols22jup
        else:
            colTypes=nbCols22

    return colTypes

def get_tables_from_database(dbName=__DBNAME__):

    with open_database(dbName) as f:
        # cnx = sqlite3.connect(dbName)
        dbTables= pd.read_sql_query("SELECT name FROM sqlite_schema WHERE type='table'", f)
        tables=list(dbTables['name'])
        # cnx.close()
    return tables

def get_files_and_folders(dirList):

    data={'files':'', 'folders':''}
    
    if len(dirList)>0:
        for dirItem in dirList:
            if dirItem.endswith('.fits'):
                data['files']+=f'{dirItem},'
            else:
                if '.DS_Store' in dirItem:
                    pass
                else:
                    data['folders']+=f'{dirItem},'
    
    return data['files'].split(',')[:-1], data['folders'].split(',')[:-1]
  
def generate_table_name_from_path(pathToFolder):
    try:
        if pathToFolder.endswith('/'):
            freq=int(pathToFolder.split('/')[-2])
            src=pathToFolder.split('/')[-3]
        else:
            freq=int(pathToFolder.split('/')[-1])
            src=pathToFolder.split('/')[-2]
    except Exception as e:
        print(e)
        sys.exit()

    tableName=f'{src}_{freq}'
    return tableName.upper(),freq,src

def run(args):
    """
        # TODO: update this to be more representative of whats going on here

        The `run` method handles the automated data processing within the 
        DRAN-AUTO program. It is responsible for processing the data based on 
        the provided command-line arguments. 

        Parameters:
        - `args` (argparse.Namespace): A namespace containing parsed 
        command-line arguments that control the program's behavior.

        Returns:
        - None

        Usage:
        The `run` method is typically called from the `main` function and is 
        responsible for executing the automated data processing based on 
        user-configured command-line arguments.
     """

    # initiate and configure logging
    delete_logs() # delete any previously generated logfiles

    # load the program banner
    load_prog('DRAN')

    # delete database if option selected
    if args.delete_db:
        if args.delete_db=='all':
            os.system('rm *.db')
        else:
            try:
                os.system(f'rm {args.delete_db}.db')
            except:
                print(f'Can not delete {args.delete_db}.db')
                sys.exit()

    # convert database files to csv files
    if args.conv and not args.f:
        
        # Configure logging
        log = configure_logging()
         
        db=args.conv
        print('Converting database files')
        tables=get_tables_from_database()
        
        if len(tables)>0:
            for table in tables:
                print(f'Converting table {table} to csv')
                cnx = sqlite3.connect(__DBNAME__)
                df = pd.read_sql_query(f"select * from {table}", cnx)
                df.sort_values('FILENAME',inplace=True)

                try:
                    os.mkdir('Tables')
                except:
                    pass
                df.to_csv(f'Tables/Table_{table}.csv',sep=',',index=False)
            sys.exit()
        else:
            print('No tables found in the database')

    else:
        pass
        
    if args.f:

        # setup debugging
        if args.db:
            # Configure logging
            log = configure_logging(args.db)
        else:
            # Configure logging
            log = configure_logging()
            
        # run a quickview
        if args.quickview:
            
            # check if file exists
            if not os.path.exists(args.f):
                msg_wrapper("error",log.error,f"File {args.f} does not exist, stopping quickview")
                sys.exit()

            # check if file is a symlink
            elif os.path.islink(args.f):
                msg_wrapper("error",log.error,f"File {args.f} is a symlink, stopping quickview")
                sys.exit()

            # check if file is a directory
            elif os.path.isdir(args.f):
                msg_wrapper("error",log.error,f"File {args.f} is a directory, stopping quickview")
                sys.exit()
            
            else:
                obs=Observation(FILEPATH=args.f, theoFit='',autoFit='',log=log)
                obs.get_data_only(qv='yes')
                sys.exit()

        else:
        
            # Process the data from the specified file or folder
            readFile = os.path.isfile(args.f)
            readFolder = os.path.isdir(args.f)

            # split path into subdirectories
            src=(args.f).split('/')

            # print(readFile)
            # print(readFolder)

            # sys.exit()

            if readFile:

                print(f'\nWorking on file: {args.f}')
                print('*'*50)

                # check if file has been processed already
                pathToFile=args.f
                fileName: str = args.f.split('/')[-1]
                freq: int = args.f.split('/')[-2]
                src: str = (args.f.split('/')[-3]).upper()

                # get table columns
                myCols=create_table_cols(freq,log)

                assert pathToFile.endswith('.fits'), f'The program requires a fits file to work, got: {fileName}'
                
                table=f'{src}_{freq}'

                # check if table exists in database
                cnx = sqlite3.connect(__DBNAME__)
                dbTables= pd.read_sql_query("SELECT name FROM sqlite_schema WHERE type='table'", cnx)
                tables=list(dbTables['name'])

                if table in tables:
                    tableData = pd.read_sql_query(f"SELECT * FROM {table}", cnx)
                    tableFilenames=sorted(list(tableData['FILENAME']))
                    if fileName in tableFilenames:
                        print(f'Already processed: {fileName}')
                        sys.exit()
                    else:
                        print(f'Processing file: {pathToFile}')

                        # check if symlink
                        isSymlink=os.path.islink(f'{pathToFile}')
                        if not isSymlink:
                            obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log,dbCols=myCols)
                            obs.get_data()
                            del obs  
                            sys.exit()
                        else:
                            print(f'File is a symlink: {args.f}. Stopped processing')
                else:
                    # check if symlink
                        isSymlink=os.path.islink(f'{pathToFile}')
                        if not isSymlink:
                            print(f'Processing file: {pathToFile}')
                            obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log)
                            obs.get_data()
                            del obs  
                            sys.exit()
                        else:
                            print(f'File is a symlink: {args.f}. Stopped processing')
                    
            elif readFolder and args.f != "../":
                
                # Ok! we're reading from a folder
                # 1. Check if there are existing files in the folder
                print(f'\nWorking on folder: {args.f}')
                print('*'*50)

                # search for files
                dirList = sorted(os.listdir(args.f))
                filesInDir,foldersInDir = get_files_and_folders(dirList)
                filesInDir = sorted(filesInDir)
                # print(filesInDir,foldersInDir)
                # sys.exit()

                # process files in directory
                # -----------------------------
                if len(foldersInDir)==0:

                    # Reading the files in the folder
                    # --------------------------------

                    # Check if table for this file exists
                    tables = get_tables_from_database()
                    tables=[d for d in tables if 'sqlite_sequence' not in d]
                                
                    tableName,freq,src = generate_table_name_from_path(args.f)

                    # print(tables,tableName)
                    # sys.exit()
                    if tableName in tables:

                        myCols=create_table_cols(freq,log,src)
                        
                        print('Found table\n')
                        cnx = sqlite3.connect(__DBNAME__)
                        tableData = pd.read_sql_query(f"SELECT * FROM {tableName}", cnx)
                        tableFilenames=sorted(list(tableData['FILENAME']))
                        print(tableFilenames)
                        
                        for file in filesInDir:
                            if file in tableFilenames:
                                print(f'Already processed: {file}')
                            else:
                                if file.endswith('.fits'):
                                    pathToFile = os.path.join(args.f,file).replace(' ','')
                                    # check if symlink
                                    isSymlink=os.path.islink(f'{pathToFile}')
                                    if not isSymlink:
                                        print(f'Processing file: {file}')
                                        obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log,dbCols=myCols)
                                        obs.get_data()
                                        del obs  
                                        # sys.exit()
                                    else:
                                        print(f'File is a symlink: {file}. Stopped processing')
                                else:
                                    print(f'File : {file} is not a valid observing file')

                        # sys.exit()

                    else:
                        print(f'Table not found, creating new table {tableName}')
                        myCols=create_table_cols(freq,log,src)

                        # Test file hasn't been processed elsewhere
                        # search from previously processed tables if this source data 
                        # has been previously processed.
                        # print(freq,tables)
                        # sys.exit()
                        
                        tableList=[]
                        for table in tables:
                            # print('---',table)
                            # sys.exit()
                            cnx = sqlite3.connect(__DBNAME__)
                            tableData = pd.read_sql_query(f"SELECT * FROM {table}", cnx)
                            cnx.close()
                            tableFilenames=sorted(list(tableData['FILENAME']))
                            tableList=tableList+tableFilenames
                            # print(len(tableFilenames))
                        # print(len(tableList))

                        # sys.exit()
                        # Loop through files
                        for file in filesInDir:
                            if file in tableFilenames:
                                print(f'Already processed: {file} in table {table}')
                            else:
                                if file.endswith('.fits'):
                                    pathToFile = os.path.join(args.f,file).replace(' ','')

                                    # check if symlink
                                    isSymlink=os.path.islink(f'{pathToFile}')

                                    # print(pathToFile)
                                    if not isSymlink:
                                        obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log,dbCols=myCols)
                                        obs.get_data()    
                                        del obs  
                                        # sys.exit()
                                    else:
                                        print(f'File is a symlink: {file}. Stopped processing')
                
                else:
                    print('folders: ', foldersInDir)
                    sys.exit()
                    for folder in foldersInDir:
                        path = "".join([args.f,folder]).replace(' ','')

                        # print(glob(path, recursive=True),'\n')
                        for dirpath, dirs, files in os.walk(path):
                            for filename in files: 
                                fname = os.path.join(dirpath,filename)  
                                
                                if fname.endswith('.fits'):

                                    print(fname)
                                sys.exit()
                            print()
                        # print(path) 
                        # sys.exit()
                        # for root, dirnames, filenames in os.walk(myDir):

                sys.exit()
                if len(files)>0:

                    src, freq, table, pathToFile = generate_table_name(files, args.f,log)
                    print(src, freq, table, pathToFile)

                    sys.exit()
                    # check if table exists in database
                    cnx = sqlite3.connect(__DBNAME__)
                    dbTables= pd.read_sql_query("SELECT name FROM sqlite_schema WHERE type='table'", cnx)
                    tables=list(dbTables['name'])

                    if len(tables)==0:
                        print('>>>> No tables found')
                        print(f'\n>>>> Creating table {table}')

                        for file in files:
                            pathToFile = os.path.join(args.f,file)
                            isSymlink=os.path.islink(f'{pathToFile}')

                            if not isSymlink:

                                # print(f'\nPath to  file: {pathToFile}')
                                print(f'Processing file: {pathToFile}')
                                obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log)
                                obs.get_data_only()
                                freq=int(obs.__dict__['CENTFREQ']['value'])
                                src=obs.__dict__['OBJECT']['value']
                                table=f'{src}_{freq}'.replace(' ','')
                                tablePath=table.replace('_','/')

                                if tablePath not in pathToFile.upper():
                                    # move file to appropriate folder
                                    print('\n',tablePath)
                                    print(pathToFile,'\n')

                                    frq=pathToFile.split('/')[-2]
                                    newpath=pathToFile.replace(frq,str(freq))
                                    newpathFolder = '/'.join(newpath.split('/')[:-1])

                                    try:
                                        os.makedirs(newpathFolder)
                                        print('Crated new directory: ',newpathFolder)
                                    except:
                                        print(f"Cant create {newpathFolder}, already exists")

                                    try:    
                                        os.system(f'mv {pathToFile} {newpath}')
                                    except:
                                        print(f'mv {pathToFile} to {newpath}')

                                    # process data at new path
                                    obs=Observation(FILEPATH=newpath, theoFit='',autoFit='',log=log)
                                    obs.get_data()
                                    del obs 
                                    # sys.exit()

                                else:
                                    print('now were talking')
                                    print(table, tablePath)
                                    sys.exit()

                            else:
                                pass

                    else:
                        if table in tables:
                            tableData = pd.read_sql_query(f"SELECT * FROM {table}", cnx)
                            tableFilenames=sorted(list(tableData['FILENAME']))

                            lista=set(files)
                            listb=set(tableFilenames)
                            newFiles = [x for x in lista if x not in listb]

                            # print(newFiles)#,lista^listb)
                            print(len(newFiles),len(lista),len(listb), newFiles in files, newFiles in tableFilenames)
                            # print(len(lista),len(listb),len(temp3))
                            # print(tableFilenames in temp3, files in temp3)
                            # sys.exit()

                            if len(newFiles) ==0:
                                print(f'No new files in {args.f}')
                                print('No new files to process')
                                # sys.exit()
                            else:
                                print(f'Found {len(newFiles)} new files:')
                              
                                for file in newFiles:
                                    pathToFile = os.path.join(args.f,file)
                                    isSymlink=os.path.islink(f'{pathToFile}')

                                    if not isSymlink:
                                        print(f'Processing file: {pathToFile}')
                                        obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log)
                                        print(obs.__dict__)
                                        
                                        try:
                                            x=obs.__dict__['COORSYS']
                                        except:
                                            print('not found')
                                            obs.__dict__['COORSYS']
                                            sys.exit()
                                        sys.exit()
                                        obs.get_data()
                                        del obs
                                        sys.exit()

                                    else:
                                        print(f'File is a symlink: {args.f}/{file}. Stopped processing')
                        else:
                            # new table
                            print(f'No existing table {table}')
                            print(f'Creating table {table}')

                            for file in files:
                                pathToFile = os.path.join(args.f,file)
                                isSymlink=os.path.islink(f'{pathToFile}')

                                if not isSymlink:

                                    print(f'Processing file: {pathToFile}')
                                    obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log)
                                    obs.get_data()
                                    del obs

                                else:
                                    print(f'File is a symlink: {args.f}/{file}. Stopped processing')
                        
                else:
                    print('no files found')
                    sys.exit()

                # print(files)
                sys.exit()
                # check if file ends with frequency
                if src[-1]=='':
                    src=src[:-1]
                else:
                    pass

                try:
                    freq=int(src[-1])
                    table=f'{src[-2]}_{freq}'.upper()
                    table=set_table_name(table,log)
                except:
                    freq=''
                
                if freq!='': # if file ends with frequency
                    files=os.listdir(args.f)

                    if len(files)>0:

                        # housekeeping
                        try:
                            ind=files.index('.DS_Store')
                            files.pop(ind)
                        except:
                            pass

                        # set path to files
                        if args.f.endswith('/'):
                            path=args.f
                        else:
                            path=f'{args.f}/'

                        # check for processed files
                        # Check if file in table
                        db=SQLiteDB(__DBNAME__,log)
                        db.create_db()
                        tables=sorted(db.get_table_names(__DBNAME__))
                        db.close_db()

                        print(f'There are {len(tables)} tables in {__DBNAME__}\n')
                        print('='*50,'\n')
                        # print(table)
                        # print(tables)
                        # sys.exit()

                        if table in tables:

                            print('Already created tables', table)

                            # Get pre-existing data from table
                            db=SQLiteDB(__DBNAME__,log)
                            db.create_db()
                            tables=db.get_table_names(__DBNAME__)
                            col_inds, colNames, col_types=db.get_all_table_coloumns(table)
                            rows=db.get_rows(table)
                            db.close_db()

                            # Create datframe
                            df=pd.DataFrame(rows,columns=colNames)
                            filesFromTable=list(df['FILENAME'])

                            # print(filesFromTable)
                            # sys.exit()
                            # print(files)
                            # print(len(filesFromTable),len(files))
                            # print(list(set(filesFromTable)^set(files)))
                            # print(len(filesFromTable),len(files),len(list(set(filesFromTable)^set(files))))
                            
                            newFiles=list(set(filesFromTable)^set(files))
                            if len(newFiles)==0:
                                print('No new files to process')
                            else:
                                print(f'Processing {len(newFiles)} new files')
                                
                                # check if files are faulty
                                with open('faultyFiles.txt','r') as f:
                                    for line in f:
                                        
                                        ln=line.split('\n')[0]
                                        fl=ln.split('/')[-1]
                                        # print(fl)
                                        faultyFiles.append(fl)
                                        # sys.exit()
                                # print(faultyFiles)

                                # get list of files in A that are not in B
                                newFilesToProcess=list(set(newFiles) - set(faultyFiles))
  
                                print(f'Processing {len(newFilesToProcess)} new files')
                                
                                if len(newFilesToProcess) == 0:
                                    print(f'No files to process')
                                else:
                                    for fn in newFilesToProcess:

                                        pathToFile=os.path.join(args.f,fn)
        
                                        # check file is not a symlink
                                        lnk=os.path.islink(f'{pathToFile}')
                                        if lnk==True:
                                            # faultyFiles=[]
                                            with open('faultyFiles.txt','a') as f:
                                                f.write(f'{pathToFile}\n')
                                                print(f'\nFile is a symlink: {pathToFile}. Stopped processing')
                                        else:
                                            print(f'Processing file: {pathToFile}')
                                            obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log)
                                            obs.get_data()
                                            del obs  
                                            # sys.exit()
                            
                        else:
                            print('We have a new source table')
                            files=os.listdir(args.f)
                            # print(tables)
                            # print(table)
                            # print(files)
                            # sys.exit()
                            if len(files) == 0:
                                print(f'No files to process')
                            else:
                                print(f'Processing {len(files)} new files')
                                
                                # check if files are faulty
                                with open('faultyFiles.txt','r') as f:
                                    for line in f:
                                        
                                        ln=line.split('\n')[0]
                                        fl=ln.split('/')[-1]
                                        # print(fl)
                                        faultyFiles.append(fl)
                                        # sys.exit()

                                # get list of files in A that are not in B
                                newFilesToProcess=list(set(files) - set(faultyFiles))

                                print(f'Processing {len(newFilesToProcess)} new files')
                                # sys.exit()
                                if len(newFilesToProcess) == 0:
                                    print(f'No files to process')
                                else:

                                    print(f'No table {table} found in {__DBNAME__}')
                                    print('Checking for incorrect table name')

                                    for t in tables:
                                        if '8400' in table:# or '8440' in table:
                                            print(table)
                                            # sys.exit()
                                            for fqs in ['8280','8440']:
                                                tb=table.replace('8400',fqs)
                                                for st in tables:
                                                    if tb == st:
                                                        print(st,' found misnamed folder')
                                                        print(tb,st,'\n')
                                                        sys.exit()
                                                        cnx = sqlite3.connect(__DBNAME__)
                                                        tdf = pd.read_sql_query(f"SELECT * FROM {st}", cnx)
                                                        fns=sorted(list(tdf['FILENAME']))
                                                        nf=list(set(newFilesToProcess) - set(fns))
                                                        # print(len(nf))

                                                        if len(nf)==0:
                                                            print('No new files to process')
                                                        else:
                                                            print(f'Processing {len(nf)} new files from {len(newFilesToProcess)}')
                                                            # sys.exit()
                                                            for fn in nf:
                                                                # pathToFile=os.path.join(folder,fn)
                                                                v=tdf['FILEPATH'].iloc[0].split('/')
                                                                pathToFile='/'.join(v[:-1])+'/'+fn
                                                                # print(v,pathToFile)
                                                                # sys.exit()

                                                                # check file is not a symlink
                                                                lnk=os.path.islink(f'{pathToFile}')
                                                                if lnk==True:
                                                                    # faultyFiles=[]
                                                                    with open('faultyFiles.txt','a') as f:
                                                                        f.write(f'{pathToFile}\n')
                                                                        print(f'\nFile is a symlink: {pathToFile}. Stopped processing')
                                                                else:
                                                                    print(f'Processing file: {pathToFile}')
                                                                    obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log)
                                                                    obs.get_data()
                                                                    del obs  
                                                                    # sys.exit()
                                                        # break
                                                    else:
                                                        pass
                                        else:
                                            sys.exit()
                                        # sys.exit()

                                    sys.exit()
                                    for fn in newFilesToProcess:
                                        pathToFile=os.path.join(args.f,fn)

                                        # check file is not a symlink
                                        lnk=os.path.islink(f'{pathToFile}')
                                        if lnk==True:
                                            # faultyFiles=[]
                                            with open('faultyFiles.txt','a') as f:
                                                f.write(f'{pathToFile}\n')
                                                print(f'\nFile is a symlink: {pathToFile}. Stopped processing')
                                        else:
                                            print(f'Processing file: {pathToFile}')
                                            obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log)
                                            obs.get_data()
                                            del obs  
                
                    else:
                        print(f"No files to process in {args.f}")

                else: # if file ends with src name or path
                    
                    # cnt =1
                    paths=[]

                    # Get all folders in the path
                    print('If you do not use a path direct to the file folder, this process will take longer than necessary or break.')
                    print('searching for all files in path')

                    alldirs=fast_scandir(args.f)
                    if len(alldirs)>0:
                        for folder in alldirs:
                            print(f'\n*** Working on Folder: {folder}\n')

                            # split path into subdirectories
                            src=(folder).split('/')
                            try:
                                freq=int(src[-1])
                            except:
                                freq=folder.split('_')[-1]

                            table=f'{src[-2]}_{freq}'.upper()
                            table=set_table_name(table,log)
                            allFiles=os.listdir(folder)

                            # check for processed files
                            # Check if file in table
                            db=SQLiteDB(__DBNAME__,log)
                            db.create_db()
                            tables=db.get_table_names(__DBNAME__)
                            db.close_db()

                            print(f'There are {len(tables)} tables in {__DBNAME__}')

                            if table in tables:

                                print('Already created table', table)

                                # Get pre-existing data from table
                                db=SQLiteDB(__DBNAME__,log)
                                db.create_db()
                                tables=db.get_table_names(__DBNAME__)
                                col_inds, colNames, col_types=db.get_all_table_coloumns(table)
                                rows=db.get_rows(table)
                                db.close_db()

                                # Create datframe
                                df=pd.DataFrame(rows,columns=colNames)
                                filesFromTable=list(df['FILENAME'])
                            
                                newFiles=list(set(filesFromTable)^set(allFiles))



                                if len(newFiles)==0:
                                    print('No new files to process')
                                else:
                                    print(f'-- Processing {len(newFiles)} new files')
                                    
                                    # check if files are faulty
                                    with open('faultyFiles.txt','r') as f:
                                        for line in f:
                                            
                                            ln=line.split('\n')[0]
                                            fl=ln.split('/')[-1]
                                            # print(fl)
                                            faultyFiles.append(fl)

                                    # get list of files in A that are not in B
                                    newFilesToProcess=sorted(list(set(newFiles) - set(faultyFiles)))
                                    
                                    # print(newFilesToProcess)
                                    print(f'Processing {len(newFilesToProcess)} new files')
                                    
                                    if len(newFilesToProcess) == 0:
                                        print(f'No files to process')
                                    else:

                                        # check if files in database
                                        cnx = sqlite3.connect(__DBNAME__)
                                        caldbTables = pd.read_sql_query("SELECT name FROM sqlite_schema WHERE type='table'", cnx)
                                        calTables=sorted([c for c in list(caldbTables['name']) if 'sqlite_sequence' not in c])
                                        # tdf = pd.read_sql_query(f"SELECT * FROM {table}", cnx)
                                        # df=df.sort_values('FILENAME')

                                        found=False
                                        for t in calTables:
                                            if t==table:
                                                found=True
                                                break

                                        print(f'found: {found}')

                                        sys.exit()
                                        for fn in newFilesToProcess:
                                            pathToFile=os.path.join(folder,fn)

                                            # check file is not a symlink
                                            lnk=os.path.islink(f'{pathToFile}')
                                            if lnk==True:
                                                # faultyFiles=[]
                                                with open('faultyFiles.txt','a') as f:
                                                    f.write(f'{pathToFile}\n')
                                                    print(f'\nFile is a symlink: {pathToFile}. Stopped processing')
                                            else:
                                                print(f'Processing file: {pathToFile}')

                                                obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log)
                                                obs.get_data()
                                                del obs  
                            
                            else:

                                # print('here')
                                # sys.exit()

                                if len(allFiles)>0:

                                    # check if files are faulty
                                    # with open('faultyFiles.txt','r') as f:
                                    #     for line in f:
                                            
                                    #         ln=line.split('\n')[0]
                                    #         fl=ln.split('/')[-1]
                                    #         faultyFiles.append(fl)

                                    # # get list of files in A that are not in B
                                    # newFilesToProcess=list(set(allFiles) - set(faultyFiles))

                                    # print(f'Processing {len(newFilesToProcess)} new files')
                                    
                                    # if len(newFilesToProcess) == 0:
                                    #     print(f'No files to process')
                                    # else:
                                        # print(newFilesToProcess)
                                        # pass

                                    # def check_folder_in_database(self):
                                        # check if files in database
                                        # print(__DBNAME__)
                                        cnx = sqlite3.connect(__DBNAME__)
                                        dbTables = pd.read_sql_query("SELECT name FROM sqlite_schema WHERE type='table'", cnx)
                                        tables=sorted([c for c in list(dbTables['name']) if 'sqlite_sequence' not in c])
                                        # tdf = pd.read_sql_query(f"SELECT * FROM {table}", cnx)
                                        # df=df.sort_values('FILENAME')
                                
                                        # print(calTables)

                                        # sys.exit()
                                        found=False
                                        for t in tables:
                                            if t==table:
                                                found=True
                                                break
                                        
                                        # print(found)
                                        # sys.exit()
                                        if found==False:
                                            print(f'No table {table} found in {__DBNAME__}')
                                            print('Checking for correct table name')
                                            # sys.exit()

                                            
                                            if len(tables)==0:
                                                
                                                for filen in allFiles:
                                                    pathToFile=os.path.join(folder,filen)
                                                    print(pathToFile)
                                                    # sys.exit()

                                                    print(f'Processing file: {pathToFile}')
                                                    # obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log)
                                                    # data=obs.get_data_only()
                                                    # print(data)
                                                    # del obs  
                                                    sys.exit()
                                                    
                                                sys.exit()
                                            else:
                                                sys.exit()
                                            for t in calTables:
                                                # print(t,table,t==table)
                                                
                                                if '8400' in table or '8440' in table:
                                                    # print(table)
                                                    for fqs in ['8280']:
                                                        tb=table.replace('8400','8280')
                                                        # name
                                                        for st in calTables:
                                                            if tb==st:
                                                                print(st,' found misnamed folder')
                                                                tdf = pd.read_sql_query(f"SELECT * FROM {st}", cnx)
                                                                fns=sorted(list(tdf['FILENAME']))
                                                                # print(fns)
                                                                # print(newFilesToProcess)
                                                                nf=list(set(newFilesToProcess) - set(fns))
                                                                # sys.exit()
                                                                if len(nf)==0:
                                                                    print('No new files to process')
                                                                else:
                                                                    print(f'Processing {len(nf)} new files from {len(newFilesToProcess)}')
                                                                    # sys.exit()
                                                                    for fn in nf:
                                                                        pathToFile=os.path.join(folder,fn)

                                                                        # check file is not a symlink
                                                                        lnk=os.path.islink(f'{pathToFile}')
                                                                        if lnk==True:
                                                                            # faultyFiles=[]
                                                                            with open('faultyFiles.txt','a') as f:
                                                                                f.write(f'{pathToFile}\n')
                                                                                print(f'\nFile is a symlink: {pathToFile}. Stopped processing')
                                                                        else:
                                                                            print(f'Processing file: {pathToFile}')
                                                                            obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log)
                                                                            obs.get_data()
                                                                            del obs  
                                                                            # sys.exit()
                                                                    break
                                                            else:
                                                                pass
                                                elif '5000' in table or '5040' in table:
                                                    # print(table)
                                                    for fqs in ['4800']:
                                                        tb=table.replace('5000',fqs)

                                                        for st in calTables:
                                                            if tb==st:
                                                                print(st,' found misnamed folder')
                                                                tdf = pd.read_sql_query(f"SELECT * FROM {st}", cnx)
                                                                fns=sorted(list(tdf['FILENAME']))
                                                                # print(fns)
                                                                # print(newFilesToProcess)
                                                                nf=list(set(newFilesToProcess) - set(fns))
                                                                # sys.exit()
                                                                if len(nf)==0:
                                                                    print('No new files to process')
                                                                else:
                                                                    print(f'Processing {len(nf)} new files from {len(newFilesToProcess)}')
                                                                    # sys.exit()
                                                                    for fn in nf:
                                                                        pathToFile=os.path.join(folder,fn)

                                                                        # check file is not a symlink
                                                                        lnk=os.path.islink(f'{pathToFile}')
                                                                        if lnk==True:
                                                                            # faultyFiles=[]
                                                                            with open('faultyFiles.txt','a') as f:
                                                                                f.write(f'{pathToFile}\n')
                                                                                print(f'\nFile is a symlink: {pathToFile}. Stopped processing')
                                                                        else:
                                                                            print(f'Processing file: {pathToFile}')
                                                                            obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log)
                                                                            obs.get_data()
                                                                            del obs  
                                                                            sys.exit()
                                                                    break
                                                            else:
                                                                pass
                                                elif '22000' in table:
                                                    # print(table)

                                                    for fqs in ['22040']:
                                                        tb=table.replace('22000',fqs)

                                                        print('\n',table,tb )
                                                        # sys.exit()
                                                        for st in calTables:
                                                            if tb==st:
                                                                print(st,' found misnamed folder')
                                                                tdf = pd.read_sql_query(f"SELECT * FROM {st}", cnx)
                                                                fns=sorted(list(tdf['FILENAME']))
                                                                # print(fns)
                                                                # print(sorted(newFilesToProcess))
                                                                nf=sorted(list(set(newFilesToProcess) - set(fns)))
                                                                print(nf)
                                                                # sys.exit()
                                                                
                                                                if len(nf)==0:
                                                                    print('No new files to process')
                                                                    break
                                                                else:
                                                                    print(f'Processing {len(nf)} new files from {len(newFilesToProcess)}')
                                                                    sys.exit()
                                                                    print('\n',table,tb,'\n')
                                                                    print(fns,'\n')
                                                                    print(nf)
                                                                    # sys.exit()
                                                                    for filen in nf:
                                                                        pathToFile=os.path.join(folder,filen)
                                                                        print(pathToFile)
                                                                        # sys.exit()

                                                                        # check file is not a symlink
                                                                        lnk=os.path.islink(f'{pathToFile}')
                                                                        if lnk==True:
                                                                            # faultyFiles=[]
                                                                            with open('faultyFiles.txt','a') as f:
                                                                                f.write(f'{pathToFile}\n')
                                                                                print(f'\nFile is a symlink: {pathToFile}. Stopped processing')
                                                                        else:
                                                                            print(f'Processing file: {pathToFile}')
                                                                            obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log)
                                                                            obs.get_data()
                                                                            del obs  
                                                                            sys.exit()
                                                                    break
                                                            else:
                                                                pass

                                                else:                     
                                                    # sys.exit()
                                                    pass

                                        else:
                                            # # print(caldbTables)
                                            
                                            for fn in newFilesToProcess:

                                                pathToFile=os.path.join(folder,fn)

                                                # check file is not a symlink
                                                lnk=os.path.islink(f'{pathToFile}')
                                                if lnk==True:
                                                    # faultyFiles=[]
                                                    with open('faultyFiles.txt','a') as f:
                                                        f.write(f'{pathToFile}\n')
                                                        print(f'\nFile is a symlink: {pathToFile}. Stopped processing')
                                                else:
                                                    # check if files already in database
                                                    cnx = sqlite3.connect(__DBNAME__)
                                                    tdf = pd.read_sql_query(f"SELECT * FROM {table}", cnx)
                                                    # calTables=sorted([c for c in list(caldbTables['name']) if 'sqlite_sequence' not in c])
                                                    ft=list(tdf['FILENAME'])

                                                    if fn in ft:
                                                        pass
                                                    else:
                                                        print(f'Processing file: {pathToFile}')
                                                        obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log)
                                                        obs.get_data()
                                                        del obs  
                                                        # sys.exit()
                                else:
                                    print(f'No files to process in {folder}')
                    else:
                        print(f'No files to process in {args.f}')
    
            else:
                print(f"{args.f} is neither an acceptable file nor folder path, please refer to the documentation and try again\n")
                sys.exit()
    else:
        if args.db:
            print('You havent specified the file or folder to process')
        else:
            msg_wrapper("info",log.info,'Please specify your arguments\n')

def main():
    """
        The `main` function is the entry point for the DRAN-AUTO program, 
        which facilitates the automated processing of HartRAO drift scan data. 
        It parses command-line arguments using the `argparse` module to provide 
        control and configuration options for the program. The function 
        initializes and configures the program based on the provided arguments.

        Attributes:
            None

        Methods:
            run(args): Responsible for handling the automated data processing 
            based on the provided command-line arguments. It sets up logging, 
            processes specified files or folders, and invokes the appropriate 
            functions for data processing.

            process_file(file_path): Processes data from a specified file. Use 
            generators or iterators as needed to optimize memory usage when 
            dealing with large files.

            process_folder(folder_path): Processes data from files in a 
            specified folder. Utilize memory-efficient data structures and 
            iterators when processing data from multiple files.

            main(): The main entry point for the DRAN-AUTO program. Parses 
            command-line arguments, defines available options, and executes 
            the appropriate function based on the provided arguments.

        Usage:
            Call the `main` function to run the DRAN-AUTO program, specifying 
            command-line arguments to configure and 
            control the automated data processing.
            e.g. _auto.py -h
    """

    # Create storage directory for processing files
    create_current_scan_directory()

    parser = argparse.ArgumentParser(prog='DRAN-AUTO', description="Begin \
                                     processing HartRAO drift scan data")
    parser.add_argument("-db", help="Turn debugging on or off, e.g., -db on \
                        (default is off)", type=str, required=False)
    parser.add_argument("-f", help="Process a file or folder at the given \
                        path, e.g., -f data/HydraA_13NB/2019d133_16h12m15s_Cont\
                            _mike_HYDRA_A.fits or -f data/HydraA_13NB", 
                            type=str, required=False)
    parser.add_argument("-delete_db", help="Delete the database on program run,\
                        e.g., -delete_db all or -delete_db CALDB.db", 
                        type=str, required=False)
    parser.add_argument("-conv", help="Convert database tables to CSV, e.g., \
                        -conv CALDB", type=str, required=False)
    parser.add_argument("-quickview", help="Get a quick view of data, e.g., \
                        -quickview y", type=str.lower, required=False, 
                        choices=['y', 'yes'])
    parser.add_argument('-version', action='version', version='%(prog)s ' + 
                        f'{__version__}')
    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':   
    main()