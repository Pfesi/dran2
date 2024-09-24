# =========================================================================== #
# File: _auto.py                                                              #
# Author: Pfesesani V. van Zyl                                                #
# Email: pfesi24@gmail.com                                                    #
# =========================================================================== #

# Standard library imports
# --------------------------------------------------------------------------- #
import os, sys
import argparse
import pandas as pd
import sqlite3
import numpy as np
import gc
import psutil

# Module imports
# --------------------------------------------------------------------------- #
from config import VERSION, DBNAME 
from common.miscellaneousFunctions import get_source_properties, get_previously_processed_files, generate_quick_view, convert_database_to_table, delete_db, get_freq_band, get_tables_from_database, create_table_cols, create_current_scan_directory, delete_logs
from common.logConfiguration import configure_logging
from common.msgConfiguration import msg_wrapper, load_prog
from common.observation import Observation


# =========================================================================== #

# TODO: CLEAN THIS CODE, ASAP!

def process_new_file(pathToFile, log, myCols, theofit='',autofit=''):
    
    # check if symlink
    isSymlink=os.path.islink(f'{pathToFile}')
    if not isSymlink:
        obs=Observation(FILEPATH=pathToFile, theoFit=theofit, autoFit=autofit, log=log, dbCols=myCols)
        obs.get_data()
        del obs  
        gc.collect()
    else:
        print(f'File is a symlink: {pathToFile}. Stopped processing')     

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

    # Configure logging
    log = configure_logging()
    
    # delete database if option selected
    if args.delete_db:
        delete_db(args.delete_db)
        
    # convert database files to csv files
    if args.conv and not args.f:
        convert_database_to_table(DBNAME)
        
    if args.f:

        # setup debugging
        if args.db:
            # Configure logging
            log = configure_logging(args.db)
            
        # run a quickview
        if args.quickview:
            generate_quick_view(args.f,log,Observation)
        else:
        
            # Process the data from the specified file or folder
            readFile = os.path.isfile(args.f)
            readFolder = os.path.isdir(args.f)

            # split path into subdirectories
            src=(args.f).split('/')

            if readFile:

                print(f'\nWorking on file: {args.f}')
                print('*'*50)

                # process_file(args.f,args.f.split('/')[-1],log,DBNAME,pathToFolder='')
                # process_file(fname,path,log,DBNAME,pathToFolder='')
                
                # check if file is in the correct folder/directory by matching the source name
                # in file with path.
                pathToFile, fileName, freq, src=get_source_properties(args.f.split('/')[-1],args.f)
                pathToFolder ='/'.join(('/'.join(pathToFile.split('.fits')[:-1])).split('/')[:-1]).upper()

                if 'HYDRA_A' in fileName:
                    srcNameFromFileName='HYDRAA'
                else:
                    srcNameFromFileName=fileName.split('_')[-1].split('.fits')[0].upper() 

                srcNameInPath=f'{srcNameFromFileName}' in pathToFolder.upper()

                if not srcNameInPath:

                    # create a new directory for this src
                    print(f'File in wrong path: {pathToFile}')
                    with open('wrongpaths.txt','a') as f:
                        f.write(f'{pathToFile}\n')
                    sys.exit()

                else:

                    assert pathToFile.endswith('.fits'), f'The program requires a fits file to work, got: {fileName}'
                    
                    # get processed files from database
                    tableName, myCols, tableFileNames, tableNames = get_previously_processed_files(src, freq,log,DBNAME)

                    if fileName in tableFileNames:
                        print(f'Already processed: {pathToFile}')
                    else:
                        print(f'Processing file: {pathToFile}')
                        process_new_file(pathToFile, log, myCols, theofit='',autofit='')
                sys.exit()  

            elif readFolder and args.f != "../":
                
                msg_wrapper('info',log.info,f'Working on folder: {args.f}')
                msg_wrapper('info',log.info,'*'*50)
                
                # Loop through all folders or files in path
                for dirpath, dirs, files in os.walk(args.f):
                    msg_wrapper('info',log.info,f'Found {len(files)} files in {dirpath}\n')
                    
                    # print(files)
                    if len(files) == 0:
                        msg_wrapper('info',log.info,f'No files found in {dirpath}')

                    elif len(files) == 1:
                        
                        if files[0]=='.DS_Store':
                            pass
                        else:
                            if files[0].endswith('.fits'):
                                msg_wrapper('info',log.info,f'Working in folder: {dirpath}')
                                msg_wrapper('info',log.info,f'Processing file: {files[0]}')
                                print('*'*50)

                                # process_file(files[0],os.path.join(dirpath,files[0]),log,DBNAME,dirpath)

                                # check if file is in the correct folder/directory by matching the source name
                                # in file with path.
                                pathToFile, fileName, freq, src=get_source_properties(files[0],os.path.join(dirpath,files[0]))
                                pathToFolder = dirpath

                                if 'HYDRA_A' in fileName:
                                    srcNameFromFileName='HYDRAA'
                                else:
                                    srcNameFromFileName=fileName.split('_')[-1].split('.fits')[0].upper() 

                                srcNameInPath=f'{srcNameFromFileName}' in pathToFolder.upper()

                                if not srcNameInPath:

                                    # create a new directory for this src
                                    print(f'File in wrong path: {pathToFile}')
                                    with open('wrongpaths.txt','a') as f:
                                        f.write(f'{pathToFile}\n')
                                    sys.exit()
                                else:
                                    assert pathToFile.endswith('.fits'), f'The program requires a fits file to work, got: {fileName}'
                    
                                    # get processed files from database
                                    tableName, myCols, tableFileNames, tableNames = get_previously_processed_files(src, freq,log,DBNAME)

                                    
                                    if fileName in tableFileNames:
                                        print(f'Already processed: {pathToFile}')
                                    else:

                                        # print(tableName, myCols, tableFileNames, tableNames )
                                        # sys.exit()
                                        print(f'Processing file: {pathToFile}')
                                        process_new_file(pathToFile, log, myCols, theofit='',autofit='')
                                        # sys.exit() 

                            else:
                                print(f'>>>>> File : {files[0]} is not a valid observing file')

                    else:
                        
                        # get the names of all the sources in the directory from the file names
                        # check if file is in the correct folder/directory by matching the source name
                        # in file with path.
                        srcs=[]
                        for file in files:
                            if not file.endswith('.fits'):
                                pass
                            else:
                                if 'HYDRA' in file: # solves 'HYDRA_A' issue
                                    srcs.append('HYDRAA')
                                else:
                                    srcs.append(file.split('.fits')[0].split('_')[-1])

                        srcsinfile=list(set(srcs))
                        msg_wrapper('info',log.info,f'Sources found in directory: {srcsinfile}\n')
                        
                        
                        if len(srcsinfile)>1:
                            print('We have imposters, aka. files that dont belong here')
                            sys.exit()
                            # move the imposter files
                            savef=''

                            for f in srcsinfile:
                                # print(f,dirpath)
                                if f in dirpath:
                                    savef=f
                                    print('>>> ',f)

                            # print(dirpath, srcsinfile, savef)

                            # sys.exit()

                            if savef=='':
                                print(f'\nInvalid file or path format: {srcsinfile}')
                                print('skipping processing\n')
                            else:
                                pass
                                idx=srcsinfile.index(savef)
                                srcsinfile.pop(idx)

                                # The files we are kicking out

                                print(dirpath, srcsinfile, savef)

                                print(f'\nThe files we are kicking out contain: {srcsinfile}')

                                sys.exit()

                                if savef == "":
                                    print('Houston, we have a problem!')
                                    sys.exit()
                                else:
                                #     # print('\n',savef,file)
                                #     # print(srcsinfile,file)
                                # if True:    
                                #     idx=srcsinfile.index(savef)
                                #     srcsinfile.pop(idx)

                                #     print(idx, srcsinfile, savef)

                                    for s in srcsinfile:
                                        for x in files:
                                            if s in x:
                                                savePath = dirpath.replace(savef,s)
                                                # print(savePath)
                                                curPath = os.path.join(dirpath,x)
                                                newPath = dirpath.replace(savef,s)

                                                try:
                                                    os.makedirs(newPath)
                                                except:
                                                    pass

                                                # print(f"move: {curPath} to {newPath} ")
                                                print(newPath)
                                                print(os.path.join(dirpath,x))
                                                print(os.path.join(savePath,x))

                                                # Check if the file is a symlink
                                                isSymlink=os.path.islink(newPath)
                                                if not isSymlink:
                                                    # os.rename(os.path.join(dirpath,x), os.path.join(savePath,x))
                                                    print(f'Moving file: {x} to {newPath}')
                                                else:
                                                    print(f'File is a symlink: {x}. Stopped processing')
                                                #     # sys.exit()
                                                    # done=True
                                                    # break
                                                # else:
                                                #     print(f'File {x} already exists in the database')
                                                #     # sys.exit()
                                                #     # done=True
                                                #     # break
                                                # else:
                                                #     print(f'File {x} is not a valid observing file')
                                                #     # sys.exit()
                                                #     # done=True
                                                #     # break

                                                # if done:
                                                #     break





                                                # os.system('mv {x} {dirpath.replace(savef,s)}')
                                    #             print(f'Moving file: {x} to ') #{dirpath.replace(s,savef)}
                                                # os.rename(os.path.join(dirpath,x), os.path.join(dirpath.replace(s,savef),x))
                                                # done=True
                                                # break
                                        # dirpath=dirpath.replace(s,savef)
                                    print(dirpath)

                                    splitPath=dirpath.split('/')
                                    # print('\n--', splitPath,'\n')

                                    sys.exit()

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
                                    tableNameFreqBand=get_freq_band(int(freq))

                                    myCols=create_table_cols(freq,log,src)

                                    print(f'\nFound freq: {freq}, for src: {src}')
                                    print(f'\nCreated tableName: {tableName}')
                                    # sys.exit()

                                    # check if table exists in database
                                    # ----------------------------------------------------------------

                                    tablesFromDB = get_tables_from_database()
                                    DBtables=[d for d in tablesFromDB if 'sqlite_sequence' not in d]

                                    # get processed files from the database
                                    dataInDBtables=[]
                                    for table in DBtables:
                                        if src in table:
                                            tableEntryfreqBand=get_freq_band(int(table.split('_')[-1]))
                                            if tableNameFreqBand==tableEntryfreqBand:

                                                print(f'>> Found similar {tableEntryfreqBand}-band freq in table:',table)
                                                    
                                                # get data
                                                cnx = sqlite3.connect(DBNAME)
                                                tableData = pd.read_sql_query(f"SELECT * FROM {table}", cnx)
                                                tableFilenames=sorted(list(tableData['FILENAME']))
                                                dataInDBtables=dataInDBtables+tableFilenames

                                    # print(dataInDBtables)
                                    # sys.exit()
                                    # get all files that havent processed yet
                                    unprocessedObs=[]
                                    for fl in files:   
                                        if fl in dataInDBtables:
                                            pass
                                        else:
                                            unprocessedObs.append(fl)

                                    # print(unprocessedObs)


                                    # sys.exit()
                                    # process all unprossed files
                                    if len(unprocessedObs)>0:

                                        unprocessedObs=sorted(unprocessedObs)
                                        print(f'There are {len(unprocessedObs)} unprocessed observations')
                                        # sys.exit()

                                        for ufile in unprocessedObs:
                                            if ufile.endswith('.fits'):



                                                pathToFile = os.path.join(dirpath,ufile).replace(' ','')

                                                print(pathToFile)
                                                print(freq, src, file, ufile)
                                                sys.exit()

                                    
                                                # check if symlink
                                                isSymlink=os.path.islink(f'{pathToFile}')
                                                if not isSymlink:
                                                    print(f'\nProcessing file: {pathToFile}')
                                                    obs=Observation(FILEPATH=pathToFile, theoFit='',autoFit='',log=log,dbCols=myCols)
                                                    obs.get_data()
                                                    del obs  
                                                    gc.collect()

                                                else:
                                                    print(f'File is a symlink: {pathToFile}. Stopped processing\n')
                                            else:
                                                print(f'>>>>> File : {file} is not a valid observing file')
                                    else:
                                        print(f'Files already processed in table/s')

                        else:

                            pathToFolder = dirpath
                            print(f'Processing files in directory: {pathToFolder}')
                            
                            # split the path to determine how to process the data if it ends
                            # with / or ''
                            splitPath=dirpath.split('/')
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

                            else:
                                # ends with ''
                                try:
                                    freq=int(splitPath[-1])
                                    src=splitPath[-2].upper().replace('-','M').replace('+','P')
                                except:
                                    msg_wrapper("error",log.error,f"Error processing folder: {dirpath}")
                                    # table name split
                                    newSplit=splitPath[-1].split('_')

                                    try:
                                        freq=int(newSplit[-1])
                                        src=newSplit[0].upper().replace('-','M').replace('+','P')
                                    except:
                                        print('File path format is not what is expected.')
                                        print(f'Treating this as a directory: {dirpath}')
                                        print('Please make sure your path points to the source folder of the source you are trying to process')

                                        #TODO: Create processing of data in any path. Do this later.
                                        sys.exit()
                                        if len(dirs)>0:
                                            print('We have directories')

                                            for fdir in dirs:
                                                if '.ipynb' in fdir or '.D_Store' in fdir:
                                                    pass
                                                else:
                                                    print(fdir)
                                            sys.exit()
                                        else:
                                            print('Stopping processing, there are no directories to process.')
                                            sys.exit()

                            # get processed files from database
                            tableName, myCols, filesInDAB, tableNames = get_previously_processed_files(src, freq,log,DBNAME)

                            print(tableName,tableNames)
                            # get all files that havent processed yet
                            unprocessedObs=[]
                            
                            print(len(filesInDAB),len(files))
                            # sys.exit()
                            for fl in files:   
                                if fl in filesInDAB:
                                    pass
                                else:
                                    if '.DS_Store' in fl:
                                        pass
                                    else:
                                        unprocessedObs.append(fl)


                            # process all unprossed files
                            if len(unprocessedObs)>0:
                                unprocessedObs=sorted(unprocessedObs)
                                print(f'There are {len(unprocessedObs)} unprocessed observations')
                                # print(files)
                                # sys.exit()

                                for ufile in unprocessedObs:
                                    if ufile.endswith('.fits'):
                                        pathToFile = os.path.join(dirpath,ufile).replace(' ','')

                                        print(f'Processing file: {pathToFile}')
                                        process_new_file(pathToFile, log, myCols, theofit='',autofit='')
                                    else:
                                        print(f'>>>>> File : {ufile} is not a valid observing file, skipping processing')
                                        
                            else:
                                print(f'Files already processed in table/s')

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
                        f'{VERSION}')
    parser.set_defaults(func=run)
    args = parser.parse_args()

    args.func(args)
    # try:
    #     args.func(args)
    # except:
    #     proc = psutil.Process(os.getpid())
    #     print('\n>>>>> Program interrupted. Terminating program.')
    #     proc.terminate()

if __name__ == '__main__':   

    proc = psutil.Process(os.getpid())
    main()
    # try:
    #     main()
    # except KeyboardInterrupt:
    #     print('\n>>>>> Program interrupted. Terminating program.')

    proc.terminate()


