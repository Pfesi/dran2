# =========================================================================== #
# File: _auto.py                                                              #
# Author: Pfesesani V. van Zyl      
# Email: pfesi24@gmail.com                                                    #
# =========================================================================== #

# Standard library imports
# --------------------------------------------------------------------------- #
import os, sys
import argparse
from config import __version__, __DBNAME__ 
import pandas as pd
import sqlite3
import numpy as np
import gc
import psutil
import subprocess
import atexit

# Module imports
# --------------------------------------------------------------------------- #
from common.miscellaneousFunctions import create_current_scan_directory, delete_logs
from common.logConfiguration import configure_logging
from common.msgConfiguration import msg_wrapper, load_prog
from common.observation import Observation
from common.contextManagers import open_database
from common.variables import sbCols, nbCols, nbCols22, nbCols22jup, dbCols
# =========================================================================== #

# TODO: CLEAN THIS CODE, ASAP!
             
def get_freq_band(freq:int):
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
    
def check_freqs(freq:int,log,src=''):
    # HartRAO frequency limits: https://www.sarao.ac.za/about/hartrao/hartrao-research-programmes/hartrao-26m-radio-telescope-details/
    # NASA limits: https://www.nasa.gov/general/what-are-the-spectrum-band-designators-and-bandwidths/

    # 18, 13,6,4.5,3.5,2.5,1.3 cm
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
  
def generate_table_name_from_path(pathToFolder:str):
    
    # work around for old file naming convention
    splitPath = pathToFolder.split('/')
    print(splitPath)

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
                freq=int(srcTable.split('_')[-1])#.replace('M','').replace('P',''))
                src=srcTable.split('_')[0]
            else:
                srcTable=(splitPath[-1]).upper()
                freq=int(srcTable.split('_')[-1])#.replace('M','').replace('P',''))
                src=srcTable.split('_')[0]
        except Exception as e:
            print('\nFailed to resolve frequency from table name')
            print(e)
            sys.exit()

    tableName=f'{src}_{freq}'.replace('-','M').replace('+','P')
    # print(tableName)
    # sys.exit()
    # srcName=splitPath[-3]

    # # the path to new file naming convention should be /data/Continuum/...
    # if srcName=='Continuum' or srcName=='Calibrators':
    #     try:
    #         freq=int(pathToFolder.split('/')[-1])
    #         src=pathToFolder.split('/')[-2]
    #     except:

    #     try:
    #         if pathToFolder.endswith('/'):
    #             freq=int(pathToFolder.split('/')[-2])
    #             src=pathToFolder.split('/')[-3]
    #         else:
    #             freq=int(pathToFolder.split('/')[-1])
    #             src=pathToFolder.split('/')[-2]
    #     except Exception as e:
    #         print('\nCould not resolve frequency from table name')
    #         print(e)
    #         sys.exit()
    # else:
    #     # old file naming convention
    #     if pathToFolder.endswith('/'):
    #         print('here1')
    #         srcTable=(splitPath[-2]).upper()
    #         if srcName in srcTable:
    #             freq=int(srcTable.split('_')[-1])
    #             src=srcName
    #         else:
    #             print('\nCould not resolve frequency from table name')
    #             sys.exit()
    #     else:
    #         print('here')
    #         srcTable=(splitPath[-1]).upper()
    #         if srcName in srcTable:
    #             freq=int(srcTable.split('_')[-1])
    #             src=srcName
    #         else:
    #             print('\nCould not resolve frequency from table name')
    #             sys.exit()
        

    # tableName=f'{src}_{freq}'
    # tableName=tableName.replace('-', 'M').replace('+', 'P') # convert for sqlite table name convention
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

    
    # print(proc,mem0)
    # gc.collect()
    # mem1 = proc.memory_info().rss
    # print(proc,mem1)
    # # p = psutil.Process(proc.pid)
    # # # p.terminate()  #or p.kill()
    # # print(proc.pid,mem0)
    # # print('\n',proc.terminate())
    # # print(proc)
    # print('done')
    # sys.exit()
    
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
                path=args.f
                for dirpath, dirs, files in os.walk(path):
                    
                    print(f'\n>>>>> Found {len(files)} files in {dirpath}\n')

                    if len(files) == 0:
                        pass
                    elif len(files) == 1:
                        if files[0]=='.DS_Store':
                            pass
                        else:
                            if files[0].endswith('.fits'):
                                print(f'file {files[0]} needs to get processed')
                                
                                # print(dirpath, files[0])

                                splitPath=dirpath.split('/')
                                print('\n',splitPath)

                                freq=int(splitPath[-1])
                                src=splitPath[-2].upper()

                                pathToFile = os.path.join(dirpath, files[0])#.replace('-','M').replace('+','P')
                                print(freq,src,len(files),pathToFile)
                                myCols=create_table_cols(freq,log,src)

                                tableName=f'{src}_{freq}'.replace('-','M').replace('+','P')

                                # check if table exists in database
                                tables = get_tables_from_database()
                                tables=[d for d in tables if 'sqlite_sequence' not in d]

                                print(tableName,tables,tableName in tables)

                                if tableName in tables:
                                    print(tableName,' in ', tables, '1')
                                    sys.exit()
                                else:
                                    # check if files have been processed already
                                    # Get all possible data from database similar to what 
                                    # is being processed.
                                    tableSrc=src.replace('-','M').replace('+','P')
                                    tableNameBand=get_freq_band(freq)

                                    # print(tableSrc,tableNameBand,tableName)

                                    # sys.exit()

                                    tfns=[] # table file names
                                    tbn=[] # table names

                                    for tb in tables:
                                        if tableSrc in tb:
                                            b=get_freq_band(int(tb.split('_')[-1]))
                                            if b==tableNameBand:
                                                print(tb,tableName,tableSrc, tableSrc in tb,b,tableNameBand)
                                                # sys.exit()
                                                # get data
                                                cnx = sqlite3.connect(__DBNAME__)
                                                tableData = pd.read_sql_query(f"SELECT * FROM {tb}", cnx)
                                                tableFilenames=sorted(list(tableData['FILENAME']))
                                                # print(tableFilenames)
                                                tfns=tfns+tableFilenames
                                                tbn.append(tb)

                                    # print(tfns)
                                    diff_list = np.setdiff1d(tfns,files)
                                    # yields the elements in list1 that are NOT in list2 for (list1,list2)

                                    print(diff_list)

                                    if len(diff_list)>0:
                                        for file in diff_list:
                                            if file.endswith('.fits'):
                                                print('-',pathToFile)
                                                sys.exit()
                                    else:
                                        print('Already in list')
                                sys.exit()

                                



                                isSymlink=os.path.islink(f'{pathToFile}')
                                if not isSymlink:
                                    obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log,dbCols=myCols)
                                    obs.get_data()    
                                    del obs  
                            else:
                                pass
                            sys.exit()

                    else:
                        print(f'\nWorking on Path: {dirpath}, ({len(files)}) files')
                        # sys.exit()
                        # Scenario 1
                        # If path ends with frequency
                        # /Users/pfesesanivanzyl/data/Continuum/J2253+1608/5000
                        # or /Users/pfesesanivanzyl/data/Continuum/J2253+1608/5000/
                        splitPath=dirpath.split('/')
                        print('\n--', splitPath,'\n')

                        done=False
                        if splitPath[-1]=='':
                            # ends with /
                            try:
                                freq=int(splitPath[-2])
                                src=splitPath[-3].upper().replace('-','M').replace('+','P')
                            except:
                                msg_wrapper("error",log.error,f"Error processing folder: {dirpath}")
                                # table name split
                                newSplit=splitPath[-2].split('_')
                                freq=int(newSplit[-1])
                                src=newSplit[0].upper().replace('-','M').replace('+','P')
                                # sys.exit()
                        else:
                            # ends with ''
                            try:
                                freq=int(splitPath[-1])
                                src=splitPath[-2].upper().replace('-','M').replace('+','P')
                            except:
                                msg_wrapper("error",log.error,f"Error processing folder: {dirpath}")
                                # table name split
                                newSplit=splitPath[-1].split('_')
                                freq=int(newSplit[-1])
                                src=newSplit[0].upper().replace('-','M').replace('+','P')
                                # sys.exit()

                        tableName=f'{src}_{freq}'.replace('-','M').replace('+','P')
                        tableNameFreqBand=get_freq_band(freq)

                        myCols=create_table_cols(freq,log,src)

                        print(f'\nFound freq: {freq}, for src: {src}')
                        print(f'\nCreated tableName: {tableName}')
                  
                        
                        # check if table exists in database
                        # ----------------------------------------------------------------

                        tablesFromDB = get_tables_from_database()
                        DBtables=[d for d in tablesFromDB if 'sqlite_sequence' not in d]

                        tableInDB = tableName in DBtables
                        unprocessedObs=[]

                        if tableInDB:
                            print(f'\nFound table in database: {tableName}')
                            print('Processing tables...')

                            # get data
                            cnx = sqlite3.connect(__DBNAME__)
                            tableData = pd.read_sql_query(f"SELECT * FROM {tableName}", cnx)
                            tableFilenames=sorted(list(tableData['FILENAME']))
                            
                            for file in files:   
                                if file in tableFilenames:
                                    pass
                                else:
                                    # print(f'>>>>> {file} not found in database tables')
                                    unprocessedObs.append(file)

                            print(len(tableFilenames), len(files), len(unprocessedObs))

                            if len(unprocessedObs)>0:
                                print(f'There are {len(unprocessedObs)} unprocessed observations')
                                # sys.exit()
                                for file in unprocessedObs:
                                    if file.endswith('.fits'):
                                        pathToFile = os.path.join(dirpath,file).replace(' ','')
                           
            #                           # check if symlink
                                        isSymlink=os.path.islink(f'{pathToFile}')
                                        # print(isSymlink)
                                        if not isSymlink:
                                            print(f'\nProcessing file: {pathToFile}')
                                            # sys.exit()
                                            obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log,dbCols=myCols)
                                            obs.get_data()
                                            del obs  
                                        else:
                                            print(f'File is a symlink: {pathToFile}. Stopped processing\n')
                                    else:
                                        print(f'>>>>> File : {file} is not a valid observing file')
                                        # sys.exit()
                            else:
                                print(f'Files already processed in table/s')
                            # sys.exit()
                        else:
                            print(f'\n!!!!! Table {tableName} not found in database.')
                            print(f'***** Looking for similar frequency band tables in database for src: {src}')
                        
                            # check if files have been processed already
                            # Get all possible data from database similar to what 
                            # is being processed.

                            dataInDBtables=[]
                            for table in DBtables:
                                if src in table:
                                    tableEntryfreqBand=get_freq_band(int(table.split('_')[-1]))
                                    if tableNameFreqBand==tableEntryfreqBand:
                                        # print(tableEntryfreqBand,src,table)
                                        print(f'>> Found similar {tableEntryfreqBand}-band freq in table:',table)
                                        
                                        # get data
                                        cnx = sqlite3.connect(__DBNAME__)
                                        tableData = pd.read_sql_query(f"SELECT * FROM {table}", cnx)
                                        tableFilenames=sorted(list(tableData['FILENAME']))
                                        dataInDBtables=dataInDBtables+tableFilenames
                                        # print(dataInDBtables)
                                        print('ok')

                            print(len(dataInDBtables), len(files))
                            # get all files that havent processed yet
                            unprocessedObs=[]
                            for file in files:   
                                if file in dataInDBtables:
                                    pass
                                else:
                                    print(f'>>>>> {file} not found in database tables')
                                    unprocessedObs.append(file)

                            # print(unprocessedObs)
                            # process all unprossed files
                            if len(unprocessedObs)>0:
                                print(f'There are {len(unprocessedObs)} unprocessed observations')
                                # sys.exit()
                                for file in unprocessedObs:
                                    if file.endswith('.fits'):
                                        pathToFile = os.path.join(dirpath,file).replace(' ','')
                           
            #                           # check if symlink
                                        isSymlink=os.path.islink(f'{pathToFile}')
                                        # print(isSymlink)
                                        if not isSymlink:
                                            print(f'\nProcessing file: {pathToFile}')
                                            # sys.exit()
                                            obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log,dbCols=myCols)
                                            obs.get_data()
                                            del obs  
                                        else:
                                            print(f'File is a symlink: {pathToFile}. Stopped processing\n')
                                    else:
                                        print(f'>>>>> File : {file} is not a valid observing file')
                                        # sys.exit()
                            else:
                                print(f'Files already processed in table/s')
                                # sys.exit()


            #                 # Process data for new table
            #                 for fl in files:

                                
            #                     if fl.endswith('.fits'):

            #                         # check if symlink
            #                         pathToFile=os.path.join(dirpath,fl)
            #                         print(pathToFile)

            #                         isSymlink=os.path.islink(f'{pathToFile}')
            #                         if not isSymlink:
            #                             obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log,dbCols=myCols)
            #                             obs.get_data()    
            #                             del obs  
            # #                                                         # sys.exit()


            #                         print('Found table\n')
            #                         cnx = sqlite3.connect(__DBNAME__)
            #                         tableData = pd.read_sql_query(f"SELECT * FROM {tableName}", cnx)
            #                         tableFilenames=sorted(list(tableData['FILENAME']))
            #                         print(tableFilenames)

            #                         # sys.exit()

            #                         # find missing files in tableFileNamers
            #                         for file in files:
            #                             if file in tableFilenames:
            #                                 print(f'Already processed: {file}')
            #                             else:
            #                                 print('Processing: ',file)
            #                                 if file.endswith('.fits'):
            #                                     pathToFile = os.path.join(dirpath,file).replace(' ','')

            #                                     # check if symlink
            #                                     isSymlink=os.path.islink(f'{pathToFile}')
                                                
            #                                     print('\n >>', pathToFile)

            #                                     if not isSymlink:
            #                                         obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log,dbCols=myCols)
            #                                         obs.get_data()    
            #                                         del obs  
            #                                     else:
            #                                         print(f'File is a symlink: {file}. Stopped processing')
            #                                 else:
            #                                     print(f'File : {file} is not a valid observing file')
                    

                        # print(freq,src,tableName)
                        # sys.exit()

                        # Scenario 2 
                        # Inside /Users/pfesesanivanzyl/data/Continuum/J2253+1608
                        # or /Users/pfesesanivanzyl/data/Continuum/J2253+1608/

                        # Scenario 3 
                        # Inside /Users/pfesesanivanzyl/data/Continuum
                        # or /Users/pfesesanivanzyl/data/Continuum/


                        # if 
                # sys.exit()
            #     filesInDir,foldersInDir = get_files_and_folders(dirList)
            #     filesInDir = sorted(filesInDir)
            #     # print(filesInDir,foldersInDir)
            #     # sys.exit()

            #     # process files in directory
            #     # -----------------------------
            #     if len(foldersInDir)==0:

            #         # Reading the files in the folder
            #         # --------------------------------

            #         # Check if table for this file exists
            #         tables = get_tables_from_database()
            #         tables=[d for d in tables if 'sqlite_sequence' not in d]
                                
            #         tableName, freq, src = generate_table_name_from_path(args.f)

            #         print(tables,tableName,tableName in  tables)

            #         # sys.exit()
            #         if tableName in tables:

            #             myCols=create_table_cols(freq,log,src)
                        
            #             print('Found table\n')
            #             cnx = sqlite3.connect(__DBNAME__)
            #             tableData = pd.read_sql_query(f"SELECT * FROM {tableName}", cnx)
            #             tableFilenames=sorted(list(tableData['FILENAME']))
            #             # print(tableFilenames)

            #             diff_list = np.setdiff1d(filesInDir,tableFilenames)
            #             # yields the elements in `filesInDir` that are NOT in `tableList`

            #             print(diff_list)

            #             # sys.exit()
            #             if len(diff_list)>0:
            #                 for file in diff_list:
            #                 # if file in tableFilenames:
            #                 #     print(f'Already processed: {file}')
            #                 # else:
            #                     if file.endswith('.fits'):
            #                         pathToFile = os.path.join(args.f,file).replace(' ','')
                                    
            #                         # check if symlink
            #                         isSymlink=os.path.islink(f'{pathToFile}')
            #                         if not isSymlink:
            #                             print(f'Processing file: {file}')
            #                             obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log,dbCols=myCols)
            #                             obs.get_data()
            #                             del obs  
            #                         else:
            #                             print(f'File is a symlink: {file}. Stopped processing')
            #                     else:
            #                         print(f'File : {file} is not a valid observing file')
            #         else:

            #             print(f'Table not found, creating new table {tableName}')
            #             # Look for similar frequency existing tables and check for overlap

            #             myCols=create_table_cols(freq,log,src)

            #             # Test file hasn't been processed elsewhere
            #             # search from previously processed tables if this source data 
            #             # has been previously processed.
                        
            #             tableList=[]
            #             tableSrc=tableName.split('_')[0]
            #             tableFrq=int(tableName.split('_')[1])
            #             tbFrqBand=get_freq_band(tableFrq)

            #             # oldtables=[]
            #             for table in tables:
            #                 if tableSrc in table:

            #                     # print(tableSrc)
            #                     tn=table.split('_')[0]
            #                     tf=int(table.split('_')[1])
            #                     tbNameFrqBand=get_freq_band(tf)
            #                     # print(tbFrqBand,tbNameFrqBand)

            #                     if tbFrqBand==tbNameFrqBand:
            #                         print('Found table: ',table,' similar to ',tableName)
            #                         # oldtables.append(tables)

            #                         cnx = sqlite3.connect(__DBNAME__)
            #                         tableData = pd.read_sql_query(f"SELECT * FROM {table}", cnx)
            #                         cnx.close()
            #                         tableFilenames=sorted(list(tableData['FILENAME']))
            #                         tableList=sorted(tableList+tableFilenames)

            #             print('\nitems in similar freqs tables: ',len(tableList))

            #             diff_list = np.setdiff1d(filesInDir,tableList)
            #             # yields the elements in `filesInDir` that are NOT in `tableList`

            #             print('From ',len(filesInDir),' files in filesInDir, we have ',len(diff_list),' new items')
            #             # print(tableList)

            #             # print (len(set(filesInDir)^set(tableList)), len(set(filesInDir)), len(set(tableList)))
            #             # print(diff_list)
            #             # sys.exit()
            #             # Loop through files

            #             if len(diff_list)>0:
            #                 for file in diff_list:
            #                     print(f'Processing: {file}')# in table {table}')
            #                     # else:
            #                     # sys.exit()
            #                     if file.endswith('.fits'):
            #                         pathToFile = os.path.join(args.f,file).replace(' ','')
            #                         print(pathToFile)
            #                         # sys.exit()
            #                             # check if symlink
            #                         isSymlink=os.path.islink(f'{pathToFile}')
            #                         if not isSymlink:
            #                             obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log,dbCols=myCols)
            #                             obs.get_data()    
            #                             del obs  
            #                             # print(proc,mem0)
            #                             gc.collect()
            #                             # mem1 = proc.memory_info().rss
            #                             # print(proc,mem1)
            #                             # sys.exit()
            #                             # p = psutil.Process(proc.pid)
            #                             # # p.terminate()  #or p.kill()
            #                             # print(proc.pid,mem0)
            #                             # print('\n',proc.terminate())
            #                             # print(proc)
            #                         else:
            #                             print(f'File is a symlink: {pathToFile}. Stopped processing')
            #             else:
            #                 print('diff_list =0')
            #                 sys.exit()
            #     else:
            #         print('folders: ', foldersInDir)
            #         # sys.exit()
            #         for folder in foldersInDir:
            #             path = "".join([f'{args.f}/',folder]).replace(' ','')
            #             print(path)
            #             # sys.exit()
            #             for dirpath, dirs, files in os.walk(path):
            #                 # print('--',dirpath,files)
            #                 # sys.exit()
            #                 try:
            #                     files.remove('.DS_Store')
            #                 except:
            #                     pass
                        
            #                 if len(files)>0:

            #                     # check if file has been processed already
            #                     # fileName: str = args.f.split('/')[-1]
            #                     freq: int = dirpath.split('/')[-1]
            #                     src: str = (dirpath.split('/')[-2]).upper()

            #                     # Check if table for this file exists
            #                     tables = get_tables_from_database()
            #                     tables=[d for d in tables if 'sqlite_sequence' not in d]
            #                     splitPath= dirpath.split('/')
            #                     if ('Continuum' in splitPath) or ('Calibration' in splitPath):
            #                         freq= int(splitPath[-1])
            #                         src=splitPath[-2]
            #                         if src=='':
            #                             src=splitPath[-3]
            #                         tableName=f'{src}_{freq}'.replace('-', 'M').replace('+', 'P')
            #                         print(tableName,freq,src)
            #                     else:
            #                         print('Setup issue')
            #                         print(splitPath)
            #                         sys.exit()

            #                     # sys.exit()

            #                     # tableName,freq,src = generate_table_name_from_path(dirpath)
            #                     myCols=create_table_cols(freq,log,src)

            #                     print(tableName)
            #                     # sys.exit()
                                
            #                     # if '+' in tableName or '-' in tableName:
            #                     #     print (tableName)
            #                     #     tableName=tableName.replace('+','P').replace('-','M')
            #                     print (tableName,sorted(tables),freq,src)
            #                     # sys.exit()

            #                     if tableName in tables:
            #                         # print(tableName,' in ', tables)

            #                         print('Found table\n')
            #                         cnx = sqlite3.connect(__DBNAME__)
            #                         tableData = pd.read_sql_query(f"SELECT * FROM {tableName}", cnx)
            #                         tableFilenames=sorted(list(tableData['FILENAME']))
            #                         print(tableFilenames)

            #                         # sys.exit()

            #                         # find missing files in tableFileNamers
            #                         for file in files:
            #                             if file in tableFilenames:
            #                                 print(f'Already processed: {file}')
            #                             else:
            #                                 print('Processing: ',file)
            #                                 if file.endswith('.fits'):
            #                                     pathToFile = os.path.join(dirpath,file).replace(' ','')

            #                                     # check if symlink
            #                                     isSymlink=os.path.islink(f'{pathToFile}')
                                                
            #                                     print('\n >>', pathToFile)

            #                                     if not isSymlink:
            #                                         obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log,dbCols=myCols)
            #                                         obs.get_data()    
            #                                         del obs  
            #                                     else:
            #                                         print(f'File is a symlink: {file}. Stopped processing')
            #                                 else:
            #                                     print(f'File : {file} is not a valid observing file')
                    
            #                     else:
            #                         # sys.exit()
            #                         # myCols=create_table_cols(freq,log,src)

            #                         # if int(freq)==2280:
            #                         #     print('---\n',myCols)
            #                         # for fl in
            #                             # sys.exit()
            #                         print(tableName,freq,src,'\n')

            #                         foundMatch='no'
            #                         for srcn in tables:
            #                             if src.replace('+','P').replace('-','M') in srcn:
            #                                 fr=srcn.split('_')[1]
            #                                 if (int(fr)>8000 and int(fr)<=12000):
            #                                     print(srcn==tableName)
            #                                     foundMatch='yes'
            #                                     if srcn==tableName:
            #                                         pass
            #                                     else:
            #                                         # get files from table
            #                                         cnx = sqlite3.connect(__DBNAME__)
            #                                         tableData = pd.read_sql_query(f"SELECT * FROM {srcn}", cnx)
            #                                         tableFilenames=sorted(list(tableData['FILENAME']))
            #                                         # print(sorted(tableFilenames))
            #                                         # print('\n',sorted(files))

            #                                         # find missing files in tableFileNames
            #                                         print('\n---', )

            #                                         newdata=list(set(files) - set(tableFilenames))
            #                                         if len(newdata)>0:
            #                                             print(newdata)
            #                                         else:
            #                                             # pass
            #                                             print('no new data to add')
            #                                 elif  (int(fr)>4000 and int(fr)<=6000):
            #                                     print(srcn==tableName)
            #                                     foundMatch='yes'
            #                                     if srcn==tableName:
            #                                         pass
            #                                     else:
            #                                         # get files from table
            #                                         cnx = sqlite3.connect(__DBNAME__)
            #                                         tableData = pd.read_sql_query(f"SELECT * FROM {srcn}", cnx)
            #                                         tableFilenames=sorted(list(tableData['FILENAME']))
            #                                         # print(sorted(tableFilenames))
            #                                         # print('\n',sorted(files))

            #                                         # find missing files in tableFileNames
            #                                         print('\n---', )

            #                                         newdata=list(set(files) - set(tableFilenames))
            #                                         if len(newdata)>0:
            #                                             print(newdata)
            #                                         else:
            #                                             # pass
            #                                             print('no new data to add')

            #                         # if int(freq)>8000 and int(freq)<12000:

            #                             # else:
            #                         # sys.exit()
            #                         if foundMatch == 'yes':
            #                             print('Match found, skipping')
            #                             # sys.exit()
            #                         else:
            #                             print('Match not found')
            #                             # sys.exit()
            #                             for fl in files:
            #                                 if '.DS_Store' in files:
            #                                     pass
            #                                 else:
            #                                     # check if files have been processed aslready
            #                                     print(dirpath)
            #                                     print(fl)

            #                                     if fl.endswith('.fits'):
            #                                         pathToFile = os.path.join(dirpath,fl).replace(' ','')

            #                                         print(pathToFile)
            #                                         # sys.exit()

            #                                         # check if symlink
            #                                         isSymlink=os.path.islink(f'{pathToFile}')

            #                                         # print(pathToFile)
            #                                         if not isSymlink:
            #                                             obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log,dbCols=myCols)
            #                                             obs.get_data()    
            #                                             del obs  
            #                                                         # sys.exit()
            #                                         else:
            #                                             print(f'File is a symlink: {fl}. Stopped processing')
                    
            #                 else:
            #                     print(f'Path "{path}", is empty')
            # else:
            #     print(f"{args.f} is neither an acceptable file nor folder path, please refer to the documentation and try again\n")
            #     sys.exit()
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

    proc = psutil.Process(os.getpid())

    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupted')
        # sys.exit()
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)

    proc.terminate()