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
from config import __version__, __DBNAME__
import pandas as pd
import sqlite3

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
# =========================================================================== #

def get_tables_from_database(dbName=__DBNAME__):
    cnx = sqlite3.connect(dbName)
    dbTables= pd.read_sql_query("SELECT name FROM sqlite_schema WHERE type='table'", cnx)
    tables=list(dbTables['name'])
    cnx.close()
    return tables
    
def generate_table_name(files, folderPath,log):
    """Use a random fits file to get the source name and 
    frequency so you can generate a table name"""

    # check file is not a symlink
    for file in files:

        # try and sneak into first file and check frequency
        pathToFile = os.path.join(folderPath,file)
        isSymlink=os.path.islink(f'{pathToFile}')
        if not isSymlink:
            print(f'Processing file: {pathToFile}')
            
            obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log)
            obs.get_data_only()
            freq=int(obs.__dict__['CENTFREQ']['value'])
            src=obs.__dict__['OBJECT']['value']
            del obs  
            break
        else:
            pass

    # use freq and src name to create table
    table=f'{src}_{freq}'.replace(' ','')
    print(f'\n>>>> Working on table: {table}\n')

    return src, freq, table, pathToFile
    
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

                print(f'\nWorking on folder: {args.f}')
                print('*'*50)

                # check if file has been processed already
                pathToFile=args.f
                fileName: str = args.f.split('/')[-1]
                freq: int = args.f.split('/')[-2]
                src: str = (args.f.split('/')[-3]).upper()

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
                            obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log)
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
                files = sorted(os.listdir(args.f))

                # print(files)
                # sys.exit()
                if len(files)>0:
                    src, freq, table, pathToFile = generate_table_name(files, args.f,log)
                    # print(src, freq, table, pathToFile)

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
                                        obs.get_data()
                                        del obs
                                        # sys.exit()

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