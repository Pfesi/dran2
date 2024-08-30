# ============================================================================#
# File: _auto.py                                                              #
# Author: Pfesesani V. van Zyl                                                #
# =========================================================================== #

# Standard library imports
# --------------------------------------------------------------------------- #
import os, sys
# from dataclasses import dataclass, field
# import numpy as np
# from datetime import datetime
import argparse
from config import __version__, __DBNAME__ #, dbCols, nbCols, sbCols
import pandas as pd
import sqlite3

# Module imports
# --------------------------------------------------------------------------- #
# import common.exceptions as ex
# from common.contextManagers import open_file
# from common.driftScans import DriftScans
# from common.enums import ScanType
from common.miscellaneousFunctions import set_dict_item, create_current_scan_directory, delete_logs, set_table_name,fast_scandir
from common.logConfiguration import configure_logging
from common.msgConfiguration import msg_wrapper, load_prog
# from common.sqlite_db import SQLiteDB
from common.observation import Observation
from common.contextManagers import open_database
from common.variables import sbCols, nbCols, nbCols22, nbCols22jup, dbCols
# =========================================================================== #

# TODO: CLEAN THIS CODE, ASAP!
             
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
  
def generate_table_name_from_path(pathToFolder):

    # work around for old file naming convention
    splitPath = pathToFolder.split('/')
    srcName=splitPath[-3]

    # the path to new file naming convention should be /data/Continuum/...
    if srcName=='Continuum' or srcName=='Calibrators':
        try:
            if pathToFolder.endswith('/'):
                freq=int(pathToFolder.split('/')[-2])
                src=pathToFolder.split('/')[-3]
            else:
                freq=int(pathToFolder.split('/')[-1])
                src=pathToFolder.split('/')[-2]
        except Exception as e:
            print('\nCould not resolve frequency from table name')
            print(e)
            sys.exit()
    else:
        # old file naming convention
        srcTable=(splitPath[-2]).upper()
        if srcName in srcTable:
            freq=int(srcTable.split('_')[-1])
            src=srcName
        else:
            print('\nCould not resolve frequency from table name')
            sys.exit()

    tableName=f'{src}_{freq}'
    tableName=tableName.replace('-', 'M').replace('+', 'P') # convert for sqlite table name convention
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

                    print(tables,tableName)
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
                            tableList=sorted(tableList+tableFilenames)
                            # print(len(tableFilenames))
                        print(len(tableList))
                        print(tableList)

                        # sys.exit()
                        # Loop through files
                        for file in filesInDir:
                            # print('>>> ',file)
                            if file in tableList:
                                print(f'Already processed: {file}')# in table {table}')
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
                    # sys.exit()
                    for folder in foldersInDir:
                        path = "".join([f'{args.f}/',folder]).replace(' ','')
                        print(path)
                        # sys.exit()
                        for dirpath, dirs, files in os.walk(path):
                            # print('--',dirpath,files)
                            # sys.exit()
                            try:
                                files.remove('.DS_Store')
                            except:
                                pass
                        
                            if len(files)>0:

                                # check if file has been processed already
                                # fileName: str = args.f.split('/')[-1]
                                freq: int = dirpath.split('/')[-1]
                                src: str = (dirpath.split('/')[-2]).upper()

                                # Check if table for this file exists
                                tables = get_tables_from_database()
                                tables=[d for d in tables if 'sqlite_sequence' not in d]

                                tableName,freq,src = generate_table_name_from_path(dirpath)
                                myCols=create_table_cols(freq,log,src)

                                
                                if '+' in tableName or '-' in tableName:
                                    print (tableName)
                                    tableName=tableName.replace('+','P').replace('-','M')
                                # print (tableName,sorted(tables),freq,src)
                                # sys.exit()

                                if tableName in tables:
                                    # print(tableName,' in ', tables)

                                    print('Found table\n')
                                    cnx = sqlite3.connect(__DBNAME__)
                                    tableData = pd.read_sql_query(f"SELECT * FROM {tableName}", cnx)
                                    tableFilenames=sorted(list(tableData['FILENAME']))
                                    print(tableFilenames)

                                    # sys.exit()

                                    # find missing files in tableFileNamers
                                    for file in files:
                                        if file in tableFilenames:
                                            print(f'Already processed: {file}')
                                        else:
                                            print('Processing: ',file)
                                            if file.endswith('.fits'):
                                                pathToFile = os.path.join(dirpath,file).replace(' ','')

                                                # check if symlink
                                                isSymlink=os.path.islink(f'{pathToFile}')
                                                
                                                print('\n >>', pathToFile)

                                                if not isSymlink:
                                                    obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log,dbCols=myCols)
                                                    obs.get_data()    
                                                    del obs  
                                                else:
                                                    print(f'File is a symlink: {file}. Stopped processing')
                                            else:
                                                print(f'File : {file} is not a valid observing file')
                    
                                else:
                                    # sys.exit()
                                    # myCols=create_table_cols(freq,log,src)

                                    # if int(freq)==2280:
                                    #     print('---\n',myCols)
                                    # for fl in
                                        # sys.exit()
                                    print(tableName,freq,src,'\n')

                                    foundMatch='no'
                                    for srcn in tables:
                                        if src.replace('+','P').replace('-','M') in srcn:
                                            fr=srcn.split('_')[1]
                                            if (int(fr)>8000 and int(fr)<=12000):
                                                print(srcn==tableName)
                                                foundMatch='yes'
                                                if srcn==tableName:
                                                    pass
                                                else:
                                                    # get files from table
                                                    cnx = sqlite3.connect(__DBNAME__)
                                                    tableData = pd.read_sql_query(f"SELECT * FROM {srcn}", cnx)
                                                    tableFilenames=sorted(list(tableData['FILENAME']))
                                                    # print(sorted(tableFilenames))
                                                    # print('\n',sorted(files))

                                                    # find missing files in tableFileNames
                                                    print('\n---', )

                                                    newdata=list(set(files) - set(tableFilenames))
                                                    if len(newdata)>0:
                                                        print(newdata)
                                                    else:
                                                        # pass
                                                        print('no new data to add')
                                            elif  (int(fr)>4000 and int(fr)<=6000):
                                                print(srcn==tableName)
                                                foundMatch='yes'
                                                if srcn==tableName:
                                                    pass
                                                else:
                                                    # get files from table
                                                    cnx = sqlite3.connect(__DBNAME__)
                                                    tableData = pd.read_sql_query(f"SELECT * FROM {srcn}", cnx)
                                                    tableFilenames=sorted(list(tableData['FILENAME']))
                                                    # print(sorted(tableFilenames))
                                                    # print('\n',sorted(files))

                                                    # find missing files in tableFileNames
                                                    print('\n---', )

                                                    newdata=list(set(files) - set(tableFilenames))
                                                    if len(newdata)>0:
                                                        print(newdata)
                                                    else:
                                                        # pass
                                                        print('no new data to add')

                                    # if int(freq)>8000 and int(freq)<12000:

                                        # else:
                                    # sys.exit()
                                    if foundMatch == 'yes':
                                        print('Match found, skipping')
                                        # sys.exit()
                                    else:
                                        print('Match not found')
                                        # sys.exit()
                                        for fl in files:
                                            if '.DS_Store' in files:
                                                pass
                                            else:
                                                # check if files have been processed aslready
                                                print(dirpath)
                                                print(fl)

                                                if fl.endswith('.fits'):
                                                    pathToFile = os.path.join(dirpath,fl).replace(' ','')

                                                    print(pathToFile)
                                                    # sys.exit()

                                                    # check if symlink
                                                    isSymlink=os.path.islink(f'{pathToFile}')

                                                    # print(pathToFile)
                                                    if not isSymlink:
                                                        obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log,dbCols=myCols)
                                                        obs.get_data()    
                                                        del obs  
                                                                    # sys.exit()
                                                    else:
                                                        print(f'File is a symlink: {fl}. Stopped processing')
                    
                            else:
                                print(f'Path "{path}", is empty')
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