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
# =========================================================================== #

@dataclass
class Observation:
    """
        Observation object containing the observation data of the observation.
    """

    # -- Observation parameters
    FILEPATH: str   # path to observing file
    theoFit: str    # theoretical fit implemented y/n
    autoFit:str     # automated fit implemented y/n
    log:object      # logger

    # -- Observation parameters not initialized when class called
    HDULIST: str = field(init=False)        # list of HDU objects
    HDULENGTH: str = field(init=False)      # length of HDULIST
    INFOHEADER: str = field(init=False)     # summarizes the content of the opened FITS file

    def __post_init__(self):
        """ Open file and get file info. 
        """

        # TODO: remember to include the value and description for these items when you're done
        
        try:
            msg_wrapper("info",self.log.info,f"Opening file {self.FILEPATH}")

            with open_file(self.FILEPATH) as f:
                self.HDULIST = f
                self.HDULENGTH=len(self.HDULIST)
                self.INFOHEADER = f.info

                # set values to dictionary
                msg_wrapper("debug",self.log.debug,f"Setting FILEPATH, HDULIST, HDULENGTH and INFOHEADER to internal dict")
                self.__dict__["HDULIST"]={'value':self.HDULIST, 'description':"Header data unit for observing file"}
                self.__dict__["HDULENGTH"]={'value':self.HDULENGTH, 'description':"Number of HDUs in observing file"}
                self.__dict__["INFOHEADER"]={'value':self.INFOHEADER, 'description':"Information header for observing file"}
                self.__dict__["FILEPATH"]={'value':self.FILEPATH, 'description':"Path to file or filename"}
        except Exception as e:
            # TODO:  put in proper file exception handling
            # see context manager
            return f'{self.FILEPATH} is corrupt'

    def set_key_value_pairs(self, key1, desc1, key2, desc2,indexKey,keys):
        """
        Set key/value pairs for keys that may be missing from the dictionary

        Args:
            key1 (_type_): missing key
            desc1 (_type_): description of missing key
            key2 (_type_): reference key
            desc2 (_type_): description of reference key
            indexKey (_type_): index key
        """
        if key1 in keys:
            pass
        else:
            keys=self.__dict__.keys()
            pos = list(keys).index(indexKey)
            items = list(self.__dict__.items())
            items.insert(pos+1, (key2, {'value':np.nan, 'description': desc2}))
            items.insert(pos+1, (key1, {'value':np.nan, 'description': desc1}))
            self.__dict__=dict(items)
            # print(f'No {key1}')
            msg=f'No {key1}'
            msg_wrapper("debug",self.log.debug,msg)
        return

    def get_data_only(self):
        """ Get data from fits file hdu. This is for the quick file view.
        """

        msg_wrapper("debug",self.log.debug,f"Getting data from fits file hdulist")
        msg_wrapper("debug",self.log.debug,f"Create dict object to store read parameters")
        self.__dict__['CARDS']={} #{'value':[], 'description':"Placeholder for hdu card titles or names"} # holds hdu card titles or names

        # print(self.__dict__)
        
        CURDATETIME = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg_wrapper("info",self.log.info,f"Date and time of data processing: {CURDATETIME}")
        self.__dict__["CURDATETIME"]={'value':CURDATETIME, 'description':"Current date and time of the data processing"}

        msg_wrapper("debug",self.log.debug,f"Looping over each HDU object in hdulist")

        try:
            hdulen=self.HDULENGTH['value']
        except:
            with open('faultyFiles.txt','a') as f:
                f.write(f'{self.FILEPATH}\n')
                print(f'\nFile is a symlink: {self.FILEPATH}. Stopped processing')
            return
        
        for index in range(hdulen):
            self.read_data_from_hdu_lists(index)

        keys=self.__dict__.keys()
        self.set_key_value_pairs('HZPERK1', 'HZPERK1', 'HZKERR1', '[Hz/K] Counter cal error','TCAL2',keys)
        self.set_key_value_pairs('HZPERK2', 'HZPERK2', 'HZKERR2', '[Hz/K] Counter cal error','HZKERR1',keys)
        self.set_key_value_pairs('TSYS1', 'TSYS1 [K]', 'TSYSERR1', '[K] System temperature','HZKERR2',keys)
        self.set_key_value_pairs('TSYS2', 'TSYS2[K]', 'TSYSERR2', '[K] System temperature','TSYSERR1',keys)
        
        # add other important bits
        # ----------------------------------

        # get drift scans
        # use hdu frontend to determine path to data processing
        frontend = self.__dict__['FRONTEND']['value']
        src = self.__dict__['OBJECT']['value']
        freq = self.__dict__['CENTFREQ']['value']

        # create_current_scan_directory()
        self.create_final_plot_directory(src,freq)
        
        if 'S' in (frontend):
            if '13.0S' in frontend or '18.0S' in frontend:
                set_dict_item(self.__dict__,'BEAMTYPE',ScanType.SBW.name, 'wide single beam drift scan')
            elif '02.5S' in frontend or '04.5S' in frontend or '01.3S' in frontend:
                set_dict_item(self.__dict__,'BEAMTYPE',ScanType.SBN.name, 'narrow single beam drift scan')
            else:
                print(f'Unknown beam type :{frontend} - contact author to have it included\n')
                sys.exit()

            # get driftscan data from file
            driftScans=DriftScans(self.__dict__)
            driftScans.process_data_only() # process the data
            del driftScans # release from memory

        elif 'D' in (frontend):
            set_dict_item(self.__dict__,'BEAMTYPE',ScanType.DB.name, 'dual beam drift scan')

            # get driftscan data from file
            driftScans=DriftScans(self.__dict__)
            driftScans.process_data_only() # process the data
            del driftScans # release from memory

    def get_data(self):
        """ Get data from fits file hdu
        """

        msg_wrapper("debug",self.log.debug,f"Getting data from fits file hdulist")
        msg_wrapper("debug",self.log.debug,f"Create dict object to store read parameters")
        self.__dict__['CARDS']={} #{'value':[], 'description':"Placeholder for hdu card titles or names"} # holds hdu card titles or names

        # print(self.__dict__)
        
        CURDATETIME = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg_wrapper("info",self.log.info,f"Date and time of data processing: {CURDATETIME}")
        self.__dict__["CURDATETIME"]={'value':CURDATETIME, 'description':"Current date and time of the data processing"}

        msg_wrapper("debug",self.log.debug,f"Looping over each HDU object in hdulist")

        try:
            hdulen=self.HDULENGTH['value']
        except:
            with open('faultyFiles.txt','a') as f:
                f.write(f'{self.FILEPATH}\n')
                print(f'\nFile is a symlink: {self.FILEPATH}. Stopped processing')
            return
        
        for index in range(hdulen):
            self.read_data_from_hdu_lists(index)

        keys=self.__dict__.keys()
        # print(keys)
        # sys.exit()
        self.set_key_value_pairs('HZPERK1', 'HZPERK1', 'HZKERR1', '[Hz/K] Counter cal error','TCAL2',keys)
        self.set_key_value_pairs('HZPERK2', 'HZPERK2', 'HZKERR2', '[Hz/K] Counter cal error','HZKERR1',keys)
        self.set_key_value_pairs('TSYS1', 'TSYS1 [K]', 'TSYSERR1', '[K] System temperature','HZKERR2',keys)
        self.set_key_value_pairs('TSYS2', 'TSYS2[K]', 'TSYSERR2', '[K] System temperature','TSYSERR1',keys)
        # if 'HZPERK1' in keys:
        #     pass
        # else:
        #     keys=self.__dict__.keys()
        #     pos = list(keys).index('TCAL2')
        #     items = list(self.__dict__.items())
        #     items.insert(pos+1, ('HZKERR1', {'value':np.nan, 'descritpion': 'HZKERR1'}))
        #     items.insert(pos+1, ('HZPERK1', {'value':np.nan, 'descritpion': 'HZPERK1'}))
        #     self.__dict__=dict(items)
        
        # if 'HZPERK2' in keys:
        #     pass
        # else:
        #     keys=self.__dict__.keys()
        #     pos = list(keys).index('HZKERR1')
        #     items = list(self.__dict__.items())
        #     items.insert(pos+1, ('HZKERR2', {'value':np.nan, 'descritpion': 'HZKERR2'}))
        #     items.insert(pos+1, ('HZPERK2', {'value':np.nan, 'descritpion': 'HZPERK2'}))
        #     self.__dict__=dict(items)
        #     print(' no hzperk2')
        
        # if 'TSYS1' in keys:
        #     pass
        # else:
        #     keys=self.__dict__.keys()
        #     pos = list(keys).index('HZKERR2')
        #     items = list(self.__dict__.items())
        #     items.insert(pos+1, ('TSYSERR1', {'value':np.nan, 'descritpion': 'TSYSERR1 [K]'}))
        #     items.insert(pos+1, ('TSYS1', {'value':np.nan, 'descritpion': 'TSYS1 [K]'}))
        #     self.__dict__=dict(items)

        # if 'TSYS2' in keys:
        #     pass
        # else:
        #     keys=self.__dict__.keys()
        #     pos = list(keys).index('TSYSERR1')
        #     items = list(self.__dict__.items())
        #     items.insert(pos+1, ('TSYSERR2', {'value':np.nan, 'descritpion': 'TSYSERR2 [K]'}))
        #     items.insert(pos+1, ('TSYS2', {'value':np.nan, 'descritpion': 'TSYS12[K]'}))
        #     self.__dict__=dict(items)
        #     print('no tsys2')

        
        # add other important bits
        # ----------------------------------

        # get drift scans
        # use hdu frontend to determine path to data processing
        frontend = self.__dict__['FRONTEND']['value']
        src = self.__dict__['OBJECT']['value']
        freq = self.__dict__['CENTFREQ']['value']

        # create_current_scan_directory()
        self.create_final_plot_directory(src,freq)
        
        if 'S' in (frontend):
            if '13.0S' in frontend or '18.0S' in frontend:
                set_dict_item(self.__dict__,'BEAMTYPE',ScanType.SBW.name, 'wide single beam drift scan')
            elif '02.5S' in frontend or '04.5S' in frontend or '01.3S' in frontend:
                set_dict_item(self.__dict__,'BEAMTYPE',ScanType.SBN.name, 'narrow single beam drift scan')
            else:
                print(f'Unknown beam type :{frontend} - contact author to have it included\n')
                sys.exit()

            # get driftscan data from file
            driftScans=DriftScans(self.__dict__)
            driftScans.process_data() # process the data
            del driftScans # release from memory

        elif 'D' in (frontend):
            set_dict_item(self.__dict__,'BEAMTYPE',ScanType.DB.name, 'dual beam drift scan')

            # get driftscan data from file
            driftScans=DriftScans(self.__dict__)
            driftScans.process_data() # process the data
            del driftScans # release from memory

    def get_hdu_info(self, hduindex: int) -> None:
        """Get information from individual hdu
        
            Args:
                hduindex (int): index of hdu to get info from
            Returns:
                None
        """

        msg_wrapper("debug",self.log.debug,f"Getting hdulist info for index {hduindex}")
        return (self.HDULIST['value'])[hduindex].header
    
    def read_data_from_hdu_lists(self, hduindex:int):
        """ Read data from fits file hdu. 

            Args:
                hduindex (int): index of hdu to read data from
        """

        # read data from all hdu lists
        hdu=self.get_hdu_info(hduindex)
        hduIndexName=self.HDULIST['value'][hduindex].name
        self.__dict__['CARDS'][f'{hduindex}'] = hduIndexName
        cols=list(hdu) # columns from hdu lists

        # print(hduIndexName)
        # sys.exit()
        msg_wrapper("debug",self.log.debug,f"Getting observing parameters from {hduIndexName} HEADER")


        # TODO: Decide on which data you want to save in the database
        # go through each column and only save relevant ones
        # print(cols)
        for column in cols:
            # print(column)
            if 'COMMENT' in column or 'SIMPLE' in column or 'BITPIX' in column or 'NAXIS' in column\
                or 'EXTEND' in column or 'SIMULATE' in column or 'START' in column or 'STOP' in column\
                or 'SCANS' in column or 'TTYPE' in column or  'TFORM' in column or 'TUNIT' in column \
                or 'TDISP' in column or 'PCOUNT' in column or 'GCOUNT' in column or 'TFIELDS' in column\
                or column=='SCAN' or 'XT' in column or 'TCALDAT' in column or 'SCANANGL' in column\
                or 'TCALFRQ' in column or 'HZZER' in column or 'SCANTYPE' in column or 'STEPSEQ' in column\
                or 'TCALSIG' in column:
                # self.__dict__[f'{column}_{hduindex}'] = {'value':hdu[column],'description':hdu.comments[column]}
                pass
            else:
                if 'BANDWDTH' in column or 'INSTRUME' in column or  'INSTFLAG' in column\
                    or 'CENTFREQ' in column or 'SCANDIST' in column or 'SCANTIME' in column:
                    if '_ZC' in hduIndexName:

                        self.__dict__[f'{column}'] = {'value':hdu[column],'description':hdu.comments[column]}
                        msg_wrapper("debug",self.log.debug,f"{column}: {str(self.__dict__[f'{column}'])}")

                elif 'FRONTEND' in column:
                    if '_CAL' in hduIndexName:

                        self.__dict__[f'{column}'] = {'value':hdu[column],'description':hdu.comments[column]}
                        msg_wrapper("debug",self.log.debug,f"{column}: {str(self.__dict__[f'{column}'])}")
                
                elif 'TCAL' in column or 'HZPERK' in column or 'HZKERR' in column:
                    # print('------',column)
                    try:
                        msg=f"{self.__dict__['FRONTEND']}, {hduIndexName}"
                        msg_wrapper("debug",self.log.debug,msg)
                    except:
                        self.__dict__['FRONTEND'] = {'value':hdu['FRONTEND'],'description':hdu.comments['FRONTEND']}

                    if 'D' in self.__dict__['FRONTEND']['value'] and '_CAL' in hduIndexName:
                        if '_CAL' in hduIndexName:
                            # print(column)#,hdu.columns())
                            # use low noise diode
                            try:
                                msg_wrapper("debug",self.log.debug,f"Using low noise diode for {self.__dict__['CENTFREQ']}")
                            except:
                                pass
                            self.__dict__[column] = {'value':hdu[column],'description':hdu.comments[column]}
                            msg_wrapper("debug",self.log.debug,f"{column}: {str(self.__dict__[f'{column}'])}")
                        else:
                            pass
                    elif 'S'  in self.__dict__['FRONTEND']['value'] :
                        # print('---',hduIndexName)
                        if 'Chart' in hduIndexName:
                        
                            # use high noise diode
                            try:
                                msg_wrapper("debug",self.log.debug,f"Using high noise diode for {self.__dict__['CENTFREQ']}")
                            except:
                                pass
                            self.__dict__[f'{column}'] = {'value':hdu[column],'description':hdu.comments[column]}
                            msg_wrapper("debug",self.log.debug,f"{column}: {str(self.__dict__[f'{column}'])}")
                        else:
                            if '04.5' in self.__dict__['FRONTEND']['value'] and '_CAL' in hduIndexName:
                                # print('******',hduIndexName,self.__dict__['FRONTEND']['value'])
                                self.__dict__[f'{column}'] = {'value':hdu[column],'description':hdu.comments[column]}
                                msg_wrapper("debug",self.log.debug,f"{column}: {str(self.__dict__[f'{column}'])} - couldn't find this value in chart so may cause problems down the line")

                elif column=='DATE':
                    date=hdu[column].split('T')
                    self.__dict__[f'{column}'] = {'value':hdu[column],'description':hdu.comments[column]}
                    self.__dict__['OBSDATE'] = {'value':date[0],'description':'Date of source observation, file creation date'}
                    self.__dict__['OBSTIME'] = {'value':date[1],'description':'Time of source observation'}
                    self.__dict__['OBSDATETIME'] = {'value':' '.join(date),'description':'Datetime of source observation'}
                    msg_wrapper("debug",self.log.debug,f"{column}: {str(self.__dict__[f'{column}'])}")

                else:
                    # data.append(f'{hduindex}_{column}')
                    # print(column,' - ',hdu[column]," : ",hdu.comments[column], hduIndexName)
                    self.__dict__[f'{column}'] = {'value':hdu[column],'description':hdu.comments[column]}
                    
                    msg_wrapper("debug",self.log.debug,f"{column}: {str(self.__dict__[f'{column}'])}")

        # sys.exit()

    def create_final_plot_directory(self, src: str,freq: float):
        """
        Create directory where final plots will be saved. The function takes 
        the source name and the frequency in MHz and creates a directory 
        with the source name and the frequency in MHz. The directory is 
        created if it does not already exist.

        Args:
            src (str): source name
            freq (float): frequency in MHz
        
        Returns:
            None
        """

        self.plotDir=(f'plots/{src}/{int(freq)}').replace(' ','')
        msg_wrapper("info",self.log.debug,f"Creating directory to store processed plots: {self.plotDir}")
        try:
            os.makedirs(self.plotDir)
        except:
            pass

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
        os.system('rm *.db')

    # convert database files to csv files
    if args.conv and not args.f:
        
        # Configure logging
        log = configure_logging()
         
        db=args.conv
        print('Converting database files')
        db = SQLiteDB(__DBNAME__,log)
        db.create_db()
        tables=db.get_table_names(__DBNAME__)

        for table in tables:
            print(f'Converting table {table} to csv')

            df = pd.read_sql_query(f"select * from {table}", db.conn)
            df.sort_values('FILENAME',inplace=True)
            df.to_csv(f'Table_{table}.csv',sep=',',index=False)
        sys.exit()

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
                msg_wrapper("error",log.error,f"File {args.f} does not exist")
                sys.exit()

            # check if file is a symlink
            elif os.path.islink(args.f):
                msg_wrapper("error",log.error,f"File {args.f} is a symlink")
                sys.exit()

            # check if file is a directory
            elif os.path.isdir(args.f):
                msg_wrapper("error",log.error,f"File {args.f} is a directory")
                sys.exit()
            
            else:
                obs=Observation(FILEPATH=args.f, theoFit='',autoFit='',log=log)
                obs.get_data_only()
                sys.exit()

        else:
        
            # Process the data from the specified file or folder
            readFile = os.path.isfile(args.f)
            readFolder = os.path.isdir(args.f)

            # split path into subdirectories
            src=(args.f).split('/')

            # get new faulty files from directory
            faultyFiles=[]
            with open('faultyFiles.txt','r') as f:
                for line in f:
                    faultyFiles.append(line.split('\n')[0])

            if readFile:

                # check if file has been processed already
                db = SQLiteDB(__DBNAME__,log)
                db.create_db()
                tables=db.get_table_names(__DBNAME__)
                db.close_db()

                print(f'There are {len(tables)} tables in {__DBNAME__}')
                
                # check source not in database already
                fileName=src[-1]
                freq=int(src[-2])
                srcName=src[-3]
                tbname=f'{srcName}_{freq}'.upper()
                tbname=set_table_name(tbname,log)

                if len(tables)==0 or tbname not in tables:
                    # check file is not a symlink
                    lnk=os.path.islink(f'{args.f}')
                    # print(lnk)
                    if lnk==True:
                        # faultyFiles=[]
                        with open('faultyFiles.txt','a') as f:
                            f.write(f'{args.f}\n')
                            print(f'\nFile is a symlink: {args.f}. Stopped processing')
                    else:
                        print('Reading new file')
                        obs=Observation(FILEPATH=args.f, theoFit='',autoFit='',log=log)
                        obs.get_data()
                        del obs 
                
                # sys.exit()
                elif tbname in tables:
                    # check file is not a symlink
                    lnk=os.path.islink(f'{args.f}')

                    if lnk==True:
                        # faultyFiles=[]
                        with open('faultyFiles.txt','a') as f:
                            f.write(f'{args.f}\n')
                            print(f'\nFile is a symlink: {args.f}. Stopped processing')
                    else:
                        # Check if file in table
                        db=SQLiteDB(__DBNAME__,log)
                        db.create_db()
                        col_inds, colNames, col_types=db.get_all_table_coloumns(tbname)
                        rows=db.get_rows(tbname)
                        db.close_db()

                        # Create datframe
                        df=pd.DataFrame(rows,columns=colNames)
                        files=list(df['FILENAME'])
                        if fileName in files:
                            print('File already in database')
                            pass
                        else:
                            print(f'Processing file: {fileName}')
                            obs=Observation(FILEPATH=args.f, theoFit='',autoFit='',log=log)
                            obs.get_data()
                            del obs     
                
                else:
                    print('Whats going on here')
                    sys.exit()
                    
            elif readFolder and args.f != "../":
                
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
                        tables=db.get_table_names(__DBNAME__)
                        db.close_db()

                        print(f'There are {len(tables)} tables in {__DBNAME__}')
                
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
                            print('\n',folder)

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
                                    print(f'Processing {len(newFiles)} new files')
                                    
                                    # check if files are faulty
                                    with open('faultyFiles.txt','r') as f:
                                        for line in f:
                                            
                                            ln=line.split('\n')[0]
                                            fl=ln.split('/')[-1]
                                            # print(fl)
                                            faultyFiles.append(fl)

                                    # get list of files in A that are not in B
                                    newFilesToProcess=list(set(newFiles) - set(faultyFiles))
                                    
                                    # print(newFilesToProcess)
                                    print(f'Processing {len(newFilesToProcess)} new files')
                                    
                                    if len(newFilesToProcess) == 0:
                                        print(f'No files to process')
                                    else:
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
                                if len(allFiles)>0:

                                    # check if files are faulty
                                    with open('faultyFiles.txt','r') as f:
                                        for line in f:
                                            
                                            ln=line.split('\n')[0]
                                            fl=ln.split('/')[-1]
                                            faultyFiles.append(fl)

                                    # get list of files in A that are not in B
                                    newFilesToProcess=list(set(allFiles) - set(faultyFiles))

                                    # print(newFilesToProcess)
                                    print(f'Processing {len(newFilesToProcess)} new files')
                                    
                                    if len(newFilesToProcess) == 0:
                                        print(f'No files to process')
                                    else:
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
                                                # sys.exit()
                                else:
                                    print(f'No files to process in {folder}')
                    else:
                        print(f'No files to process in {args.f}')
    
            else:
                print(f"{args.f} is neither an acceptable file nor folder path, please refer to the documentation and try again\n")
                # sys.exit()
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

    # create file to store faulty file names
    if os.path.isfile('faultyFiles.txt'):
        pass
    else:
        f1= open('faultyFiles.txt','w+')

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
    # create file to store faulty or symlink file names
    if os.path.isfile('faultyFiles.txt'):
        pass
    else:
        f1= open('faultyFiles.txt','w+')

    main()