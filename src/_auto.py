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
import datetime

# Module imports
# --------------------------------------------------------------------------- #
from config import VERSION, DBNAME 
from common.miscellaneousFunctions import process_file,process_new_file,fast_scandir,run_fast_scandir,parse_source_path, get_previously_processed_files, generate_quick_view, convert_database_to_table, delete_db, get_freq_band, get_tables_from_database, create_table_cols, create_current_scan_directory, delete_logs
from common.logConfiguration import configure_logging
from common.msgConfiguration import msg_wrapper, load_prog
from common.observation import Observation


# =========================================================================== #

# TODO: CLEAN THIS CODE, ASAP!

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

                filePath=args.f

                print(f'\nWorking on file: {filePath}')
                print('*'*50)
                
                process_file(filePath, log,Observation)
                sys.exit()  

            elif readFolder and args.f != "../":
                
                msg_wrapper('info',log.info,f'Working on folder: {args.f}')
                msg_wrapper('info',log.info,'*'*50)

                # print(datetime.datetime.now().date(),str(datetime.datetime.now().time()).replace(':','-')[:8] )
                
                today=str(datetime.datetime.now().date())
                dirpath = args.f                

                with open(f'processed_files_{today}.txt','w') as fl:
                    folders = fast_scandir(dirpath,log,Observation,fl)
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


