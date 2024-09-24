# =========================================================================== #
# File   : miscellaneousFunctions.py                                          #
# Author : Pfesesani V. van Zyl                                               #
# =========================================================================== #

# Standard library imports
# --------------------------------------------------------------------------- #
import numpy as np
import os, sys
import pandas as pd
import sqlite3
# =========================================================================== #

try:
    from .msgConfiguration import msg_wrapper
except:
    from msgConfiguration import msg_wrapper
try:
    from ..config import LOGFILE
except:
    from config import LOGFILE
    
from .variables import sbCols, nbCols, nbCols22, nbCols22jup, dbCols
from .contextManagers import open_database
# from .observation import Observation

sys.path.append("..")
from config import VERSION, DBNAME 

def set_dict_item(dictionary: dict,key,value,description) -> None:
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

def calc_log_freq(freq: float):
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
    #sig2noise = signalPeak/(max(noise)+abs(min(noise))) - if there is RFI in the noise, this doesn't work very well
    return sig2noise

def delete_logs():
    """
    Delete the logfile if it exists
    """
    # delete any previous log file
    try:
        os.remove(LOGFILE)
    except OSError:
        pass

def set_table_name(src,log):
    """
    Set the table name based on the declination.

    Args:
        src (str): source or table name
    """

    msg=f'Format database table name for {src}'
    msg_wrapper("debug",log.debug,msg)

    if '-' in src:  
        src=src.replace('-','m').upper()
    elif '+' in src:
        src=src.replace('+','p').upper()

    return src

def get_freq_band(freq:int) -> str:
    """ Get the frequency band for a given frequency in MHz"""

    freq=int(freq)
    if freq >= 1000 and freq<= 2000: 
        return 'L'
    elif freq > 2000 and freq<= 4000: #
        return 'S'
    elif freq > 4000 and freq<= 6000:
        return 'C'
    elif freq > 6000 and freq<= 8000:
        # TODO: get correct frequency band for masers - ask Fanie vdHeever
        return 'M' # for methanol masers
    elif freq > 8000 and freq<= 12000: # 8580
        return 'X'
    elif freq > 12000 and freq<= 18000:
        return 'Ku' 
    elif freq >= 18000 and freq<= 27000:
        return 'K'

def get_freq_band2(freq:int) -> tuple[str, str]:
    """ Get frequency band given the frequency in MHz."""
    
    freq=int(freq)
    if freq >= 1000 and freq<= 2000: 
        return 'L', '18.0S'
    elif freq > 2000 and freq<= 4000: #
        return 'S', '13.0S'
    elif freq > 4000 and freq<= 6000:
        return 'C', '05.0D'
    elif freq > 6000 and freq<= 8000:
        # TODO: get correct frequency band for masers - ask Fanie vdHeever
        return 'M', '04.5S'# for methanol masers
    elif freq > 8000 and freq<= 12000: # 8580
        return 'X', '03.5D'
    elif freq > 12000 and freq<= 18000:
        return 'Ku', '02.5S'
    elif freq >= 18000 and freq<= 27000:
        return 'K', '01.3S'
    
def create_table_cols(freq,log,src=''):
    # HartRAO frequency limits: https://www.sarao.ac.za/about/hartrao/hartrao-research-programmes/hartrao-26m-radio-telescope-details/
    # NASA limits: https://www.nasa.gov/general/what-are-the-spectrum-band-designators-and-bandwidths/

    # 18, 13,6,4.5,3.5,2.5,1.3 cm
    cols=[]
    colTypes=[]

    freq=int(freq)

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

def get_source_properties(fname,path):

    try:
        freq = int(path.split('/')[-2])
    except:
        freq= int(path.split('/')[-2].split('_')[-1])

    src = (path.split('/')[-3]).upper()

    return path, fname, freq, src

# def process_file(fname,path,log,DBNAME,pathToFolder=''):

#     # check if file is in the correct folder/directory by matching the source name
#     # in file with path.
#     pathToFile, fileName, freq, src=get_source_properties(fname,path)
#     if pathToFolder == '':
#         pathToFolder ='/'.join(('/'.join(pathToFile.split('.fits')[:-1])).split('/')[:-1]).upper()
    
#     if 'HYDRA_A' in fileName:
#         srcNameFromFileName='HYDRAA'
#     else:
#         srcNameFromFileName=fileName.split('_')[-1].split('.fits')[0].upper() 

#     srcNameInPath=f'{srcNameFromFileName}' in pathToFolder.upper()

#     if not srcNameInPath:

#         # create a new directory for this src
#         print(f'File in wrong path: {pathToFile}')
#         with open('wrongpaths.txt','a') as f:
#             f.write(f'{pathToFile}\n')
#         sys.exit()

#     else:

#         assert pathToFile.endswith('.fits'), f'The program requires a fits file to work, got: {fileName}'
                    
#         # get processed files from database
#         tableName, myCols, tableFileNames, tableNames = get_previously_processed_files(src, freq,log,DBNAME)

#         if fileName in tableFileNames:
#             print(f'Already processed: {pathToFile}')
#         else:
#             print(f'Processing file: {pathToFile}')
#             process_new_file(pathToFile, log, myCols, theofit='',autofit='')


def get_tables_from_database(dbName):

    with open_database(dbName) as f:
        dbTables= pd.read_sql_query("SELECT name FROM sqlite_schema WHERE type='table'", f)
        dbTables=sorted(list(dbTables['name']))
        dbTables=[d for d in dbTables if 'sqlite_sequence' not in d]
    return dbTables

def get_previously_processed_files(src, freq,log,dbname):
    # create table name and get table relevant columns
    # - ensure table name adheres to database naming convention
    src=src.replace('-','M').replace('+','P')
    tableName=f'{src}_{freq}'
    myCols=create_table_cols(freq,log,src)

    # print(src,tableName)
    # sys.exit()
                    
    # - get frequency band for the observations
    tableFreqBand=get_freq_band(int(freq))

    # check if table exists in database
    # - get all tables from database
    dbTables = get_tables_from_database(dbname)

    # - create storage lists for 
    tableFileNames=[] # table file names
    tableNames=[] # table names

    # print(tableName)
    # print(tableFreqBand)
    # print(dbTables)
    # print(src,'\n')
    for table in dbTables:
        if src in table:
                            
            # get frequency band from table in database
            freqBand=get_freq_band(int(table.split('_')[-1]))
                            
            # compare table freq band from table in databse to the one generated from file path
            cnx = sqlite3.connect(DBNAME)
            # print(freqBand,tableFreqBand,src,table)
            if freqBand==tableFreqBand:

                # get filenames from table in database
                tableDf= pd.read_sql_query(f"SELECT * FROM {table}", cnx)
                filesInTable=sorted(list(tableDf['FILENAME']))
                tableFileNames+=filesInTable
                tableNames.append(table)
            cnx.close()

    return tableName, myCols, tableFileNames, tableNames

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
  
def generate_table_name_from_path(pathToFolder:str):
    
    # work around for old file naming convention
    splitPath = pathToFolder.split('/')
    # print(splitPath)

    # path ends with frequency
    try:
        if pathToFolder.endswith('/'):
            freq=int(pathToFolder.split('/')[-2])
            src=pathToFolder.split('/')[-3]
        else:
            freq=int(pathToFolder.split('/')[-1])
            src=pathToFolder.split('/')[-2]
    except Exception as e:
        print('\nCould not resolve frequency from table name')
        print('Trying old naming convention resolution')

        try:
            if pathToFolder.endswith('/'):
                srcTable=(splitPath[-2]).upper()
                freq=int(srcTable.split('_')[-1])
                src=srcTable.split('_')[0]
            else:
                srcTable=(splitPath[-1]).upper()
                freq=int(srcTable.split('_')[-1])
                src=srcTable.split('_')[0]
        except Exception as e:
            print('\nFailed to resolve frequency from table name')
            print(e)
            sys.exit()

    tableName=f'{src}_{freq}'.replace('-','M').replace('+','P')

    return tableName.upper(),freq,src

def convert_database_to_table(dbname):
    print('Converting database tables to csv tables')
    tables=get_tables_from_database(dbname)
        
    if len(tables)>0:
        for table in tables:
            print(f'Converting table {table} to csv')
            cnx = sqlite3.connect(dbname)
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

def delete_db(dbName):
    if dbName=='all':
        os.system('rm *.db')
    else:
        try:
            os.system(f'rm {dbName}.db')
        except:
            print(f'Can not delete {dbName}.db')
            sys.exit()

def generate_quick_view(arg,log,Observation):
    # check if file exists
    if not os.path.exists(arg):
        msg_wrapper("error",log.error,f"File {arg} does not exist, stopping quickview")
        sys.exit()

    # check if file is a symlink
    elif os.path.islink(arg):
        msg_wrapper("error",log.error,f"File {arg} is a symlink, stopping quickview")
        sys.exit()

    # check if file is a directory
    elif os.path.isdir(arg):
        msg_wrapper("error",log.error,f"File {arg} is a directory, stopping quickview")
        sys.exit()
            
    else:
        obs=Observation(FILEPATH=arg, theoFit='',autoFit='',log=log)
        obs.get_data_only(qv='yes')
        sys.exit()


# Unused but may be useful in future
def fast_scandir(dirname):
    '''Scan directory for all folders in the given directory'''

    print(f'Scanning the {dirname} directory')
    subfolders= [f.path for f in os.scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(fast_scandir(dirname))
    return subfolders