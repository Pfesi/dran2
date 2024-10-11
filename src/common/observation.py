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
from config import VERSION, DBNAME
import pandas as pd
import sqlite3

# Module imports
# --------------------------------------------------------------------------- #
import common.exceptions as ex
from common.contextManagers import open_file
from common.driftScans import DriftScans
from common.enums import ScanType
from common.miscellaneousFunctions import set_dict_item, create_current_scan_directory, delete_logs, set_table_name,fast_scandir, get_freq_band2
from common.logConfiguration import configure_logging
from common.msgConfiguration import msg_wrapper, load_prog
from common.sqlite_db import SQLiteDB
from common.plotting import make_qv_plots
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
    dbCols: dict    # dictionary of table columns
    

    # -- Observation parameters not initialized when class called
    HDULIST: str = field(init=False)        # list of HDU objects
    HDULENGTH: str = field(init=False)      # length of HDULIST
    INFOHEADER: str = field(init=False)     # summarizes the content of the opened FITS file
    
    
    def __post_init__(self):
        """ Open file and get file info. 
        """

        # TODO: remember to include the value and description for these items when you're done

        # print('\n dbCol: ',self.dbCols)
        # sys.exit()
        if len(self.dbCols)==0:
            # probably gui self processing tool 

            # print(self.__dict__)
            # setup a dictionary with all the parameters pre-set  
            
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
                sys.exit()
            
        else:
            msg_wrapper('info',self.log.info,'Using predefined cols')
            
            self.dbCols['keys']=list(self.dbCols.keys())
            self.dbCols['values']=list(self.dbCols.values())

            self.dbCols['FILEPATH']={'value':self.FILEPATH, 'description':'Path to file'}
            self.dbCols['theoFit']={'value':self.theoFit, 'description':'Theoretical fit to be used'}
            self.dbCols['autoFit']={'value':self.autoFit, 'description':'Automated fitting to be used'}
            self.dbCols['log']=self.log

            # print('--++--\n',self.dbCols)
            # sys.exit()

            try:
                msg_wrapper("info",self.log.info,f"Opening file {self.FILEPATH}")

                with open_file(self.FILEPATH) as f:
                    self.HDULIST = f
                    self.HDULENGTH=len(self.HDULIST)
                    self.INFOHEADER = f.info

                #     # set values to dictionary
                    msg_wrapper("debug",self.log.debug,f"Setting FILEPATH, HDULIST, HDULENGTH and INFOHEADER to internal dict")
                    self.dbCols["HDULIST"]={'value':self.HDULIST, 'description':"Header data unit for observing file"}
                    self.dbCols["HDULENGTH"]={'value':self.HDULENGTH, 'description':"Number of HDUs in observing file"}
                    self.dbCols["INFOHEADER"]={'value':self.INFOHEADER, 'description':"Information header for observing file"}
                    self.__dict__= self.dbCols

            except Exception as e:
                # TODO:  put in proper file exception handling
                print('error: ',e)
                # sys.exit()
                # see context manager
                return f'{self.FILEPATH} is corrupt'
            
            # sys.exit()
            for k,v in self.__dict__.items():
                if type(v).__name__ =='dict' or k=='log' or k=='keys' or k=='values':
                    pass
                else:
                    # print(k,v)
                    self.__dict__[k]={'value':np.nan, 'description':''}

            # for k,v in self.__dict__.items():
            #     print(k,v)
            # sys.exit()    

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

    def get_data_only(self,qv=False):
        """ Get data from fits file hdu. This is for the quick file view.
        """

        msg_wrapper("debug",self.log.debug,f"Getting data from fits file hdulist")
        msg_wrapper("debug",self.log.debug,f"Create dict object to store read parameters")
        self.__dict__['CARDS']={} #{'value':[], 'description':"Placeholder for hdu card titles or names"} # holds hdu card titles or names

        # 
        
        CURDATETIME = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg_wrapper("info",self.log.info,f"Date and time of data processing: {CURDATETIME}")
        self.__dict__["CURDATETIME"]={'value':CURDATETIME, 'description':"Current date and time of the data processing"}

        msg_wrapper("debug",self.log.debug,f"Looping over each HDU object in hdulist")

        try:
            hdulen=self.HDULENGTH['value']
        except:
            msg_wrapper("debug",self.log.debug,f'File is a symlink: {self.FILEPATH}. Stopped processing')
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

            print(self.__dict__.keys())
            hdulen = self.__dict__['HDULENGTH']['value']

            if qv=='yes':
                
                print('Plotting views')
                if hdulen==5:
                    #Create dict objects
                    LCP = {'date' : self.__dict__['OBSDATE']['value'],
                        'file':os.path.basename(self.__dict__['FILEPATH']['value']).split(".fits")[0][:18],
                        'source' :  self.__dict__['OBJECT']['value'],
                        'offset' :  self.__dict__['ON_OFFSET']['value'], 
                        'hpbw' :  self.__dict__['HPBW']['value'],
                        'hfnbw' :  self.__dict__['FNBW']['value']/2.,
                        'nu' :  self.__dict__['CENTFREQ']['value'],
                        'centre_scan' :  self.__dict__['ON_TA_LCP']['value'],
                        }

                    RCP = {'date' : self.__dict__['OBSDATE']['value'],
                        'file':os.path.basename(self.__dict__['FILEPATH']['value']).split(".fits")[0][:18],
                        'source' :  self.__dict__['OBJECT']['value'],
                        'offset' :  self.__dict__['ON_OFFSET']['value'], 
                        'hpbw' :  self.__dict__['HPBW']['value'],
                        'hfnbw' :  self.__dict__['FNBW']['value']/2.,
                        'nu' :  self.__dict__['CENTFREQ']['value'],
                        'centre_scan' :  self.__dict__['ON_TA_RCP']['value'],
                        }
                    
                else:
                    #Create dict objects
                    LCP = {'date' : self.__dict__['OBSDATE']['value'],
                        'file':os.path.basename(self.__dict__['FILEPATH']['value']).split(".fits")[0][:18],
                        'source' :  self.__dict__['OBJECT']['value'],
                        'offset' :  self.__dict__['ON_OFFSET']['value'], 
                        'hpbw' :  self.__dict__['HPBW']['value'],
                        'hfnbw' :  self.__dict__['FNBW']['value']/2.,
                        'nu' :  self.__dict__['CENTFREQ']['value'],
                        'north_scan' : self.__dict__['HPN_TA_LCP']['value'],
                        'centre_scan' :self.__dict__['ON_TA_LCP']['value'],
                        'south_scan' : self.__dict__['HPS_TA_LCP']['value'],
                        }

                    RCP = {'date' : self.__dict__['OBSDATE']['value'],
                        'file':os.path.basename(self.__dict__['FILEPATH']['value']).split(".fits")[0][:18],
                        'source' :  self.__dict__['OBJECT']['value'],
                        'offset' :  self.__dict__['ON_OFFSET']['value'], 
                        'hpbw' :  self.__dict__['HPBW']['value'],
                        'hfnbw' :  self.__dict__['FNBW']['value']/2.,
                        'nu' :  self.__dict__['CENTFREQ']['value'],
                        'north_scan' : self.__dict__['HPN_TA_RCP']['value'],
                        'centre_scan' :  self.__dict__['ON_TA_RCP']['value'],
                        'south_scan' : self.__dict__['HPS_TA_RCP']['value'],
                        }
                    
                # create plots
                make_qv_plots(LCP,RCP)

        elif 'D' in (frontend):
            set_dict_item(self.__dict__,'BEAMTYPE',ScanType.DB.name, 'dual beam drift scan')
            # sys.exit()
            # get driftscan data from file
            driftScans=DriftScans(self.__dict__)
            # sys.exit()
            driftScans.process_data_only() # process the data
            del driftScans # release from memory

            if qv=='yes':
                print('Plotting views')
                if hdulen==5:
                    #Create dict objects
                    LCP = {'date' : self.__dict__['OBSDATE']['value'],
                        'file':os.path.basename(self.__dict__['FILEPATH']['value']).split(".fits")[0][:18],
                        'source' :  self.__dict__['OBJECT']['value'],
                        'offset' :  self.__dict__['ON_OFFSET']['value'], 
                        'hpbw' :  self.__dict__['HPBW']['value'],
                        'hfnbw' :  self.__dict__['FNBW']['value']/2.,
                        'nu' :  self.__dict__['CENTFREQ']['value'],
                        'centre_scan' :  self.__dict__['ON_TA_LCP']['value'],
                        }

                    RCP = {'date' : self.__dict__['OBSDATE']['value'],
                        'file':os.path.basename(self.__dict__['FILEPATH']['value']).split(".fits")[0][:18],
                        'source' :  self.__dict__['OBJECT']['value'],
                        'offset' :  self.__dict__['ON_OFFSET']['value'], 
                        'hpbw' :  self.__dict__['HPBW']['value'],
                        'hfnbw' :  self.__dict__['FNBW']['value']/2.,
                        'nu' :  self.__dict__['CENTFREQ']['value'],
                        'centre_scan' :  self.__dict__['ON_TA_RCP']['value'],
                        }
                    
                else:
                    #Create dict objects
                    LCP = {'date' : self.__dict__['OBSDATE']['value'],
                        'file':os.path.basename(self.__dict__['FILEPATH']['value']).split(".fits")[0][:18],
                        'source' :  self.__dict__['OBJECT']['value'],
                        'offset' :  self.__dict__['ON_OFFSET']['value'], 
                        'hpbw' :  self.__dict__['HPBW']['value'],
                        'hfnbw' :  self.__dict__['FNBW']['value']/2.,
                        'nu' :  self.__dict__['CENTFREQ']['value'],
                        'north_scan' : self.__dict__['HPN_TA_LCP']['value'],
                        'centre_scan' :self.__dict__['ON_TA_LCP']['value'],
                        'south_scan' : self.__dict__['HPS_TA_LCP']['value'],
                        }

                    RCP = {'date' : self.__dict__['OBSDATE']['value'],
                        'file':os.path.basename(self.__dict__['FILEPATH']['value']).split(".fits")[0][:18],
                        'source' :  self.__dict__['OBJECT']['value'],
                        'offset' :  self.__dict__['ON_OFFSET']['value'], 
                        'hpbw' :  self.__dict__['HPBW']['value'],
                        'hfnbw' :  self.__dict__['FNBW']['value']/2.,
                        'nu' :  self.__dict__['CENTFREQ']['value'],
                        'north_scan' : self.__dict__['HPN_TA_RCP']['value'],
                        'centre_scan' :  self.__dict__['ON_TA_RCP']['value'],
                        'south_scan' : self.__dict__['HPS_TA_RCP']['value'],
                        }
                    
                # create plots
                make_qv_plots(LCP,RCP)

    def get_data(self):
        """ Get data from fits file hdu
        """

        # print('get data')
        # sys.exit()
        msg_wrapper("debug",self.log.debug,f"Getting data from fits file hdulist")
        msg_wrapper("debug",self.log.debug,f"Create dict object to store read parameters")
        self.__dict__['CARDS']={} #{'value':[], 'description':"Placeholder for hdu card titles or names"} # holds hdu card titles or names
        
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

        # print(freq,type(freq))
        if str(freq)=="nan":
            print('Fronend is nan')
            freq='nans'

        try :
            f=int(freq)
        except:

        # if freq == np.nan:
            print("Couldn't find frequency, creating frequency from path")
            f=self.__dict__['FILEPATH']['value'].split('/')[-2]
            try:
                freq=int(f)
                print(freq)
                # if freq>= and freq<= :
                band,frontend=get_freq_band2(freq)
                print(f'Freq: {freq}, band: {band}, frontend: {frontend}')
                self.__dict__['FRONTEND']['value']=frontend
                # sys.exit()
            except:
                print('Path not in valid path layout')
                sys.exit()
            print(f)

            # sys.exit()
        # create_current_scan_directory()
        self.create_final_plot_directory(src,freq)
        
        print(f'For frontend: {frontend}')
        # sys.exit()
        self.__dict__['CENTFREQ']['value']=freq
        if 'S' in (frontend):

            if '13.0S' in frontend or '18.0S' in frontend:
                set_dict_item(self.__dict__,'BEAMTYPE',ScanType.SBW.name, 'wide single beam drift scan')
            elif '02.5S' in frontend or '04.5S' in frontend or '01.3S' in frontend:
                set_dict_item(self.__dict__,'BEAMTYPE',ScanType.SBN.name, 'narrow single beam drift scan')
            else:
                print(f'Unknown beam type :{frontend} - contact author to have it included\n')
                sys.exit()

            # get driftscan data from file
            for k,v in self.__dict__.items():
                if 'CENTFREQ' in k:
                    freq=int(v['value'])
                if 'FILEPATH' in k:
                    fpath=v['value']
            
            # TODO: decide what to do with this
            if str(freq) in fpath:
                pass
            else:
                print('Frequency and path dont match')
                print(fpath,freq)

                # check if source has been processed    
                
                # create required table

                
            driftScans=DriftScans(self.__dict__)
            driftScans.process_data() # process the data
            del driftScans # release from memory

        elif 'D' in (frontend):
            set_dict_item(self.__dict__,'BEAMTYPE',ScanType.DB.name, 'dual beam drift scan')

            # get driftscan data from \file
            driftScans=DriftScans(self.__dict__)
            driftScans.process_data() # process the data
            del driftScans # release from memory

    def get_data_from_predefined_cols(self):
        """ Get data from fits file hdu
        """

        msg_wrapper("debug",self.log.debug,f"Getting data from fits file hdulist")
        msg_wrapper("debug",self.log.debug,f"Create dict object to store read parameters")
        self.__dict__['CARDS']={} #{'value':[], 'description':"Placeholder for hdu card titles or names"} # holds hdu card titles or names

        # print(self.__dict__)
        # sys.exit()
        # 
        
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
        # print(self.__dict__.keys())
        # sys.exit()

        frontend = self.__dict__['FRONTEND']['value']
        src = self.__dict__['OBJECT']['value']
        freq = self.__dict__['CENTFREQ']['value']

        keys=self.__dict__['keys']
        values=self.__dict__['values'][:-1]
        lenValues=len(values)
        lenKeys=len(keys)
        
        # create table with frequency:
        # -------------------------------

       
        # fn=
        # print()
        # sys.exit()
        print(freq)
        # if freq=='nan':
        fp=self.__dict__["FILEPATH"]['value']
        fn=fp.split('/')[-1]
        # print(fn)

        # sys.exit()
        # print(freq)
        tbFreq=int(freq)
        table=f'{src}_{tbFreq}'.upper().replace(' ', '')
        # print(table)

        sys.exit()
        cnx = sqlite3.connect(__DBNAME__)
        dbTables= pd.read_sql_query("SELECT name FROM sqlite_schema WHERE type='table'", cnx)
        tables=list(dbTables['name'])
        print(tables)
        if table in tables:
            pass
        else:
            sqlStmt=''
            if lenKeys==lenValues:
                for i in range(lenValues):
                    # print('---',key,value)
                    if keys[i]=='FILENAME':
                        sqlStmt +=f'CREATE TABLE IF NOT EXISTS {table} ('
                        idKey = sqlStmt + "id INTEGER PRIMARY KEY AUTOINCREMENT" + ", "
                        sqlStmt = idKey + keys[i] + " " + "TEXT" + " UNIQUE , "
                                                    # print(sqlStmt)
                    else:
                        if keys[i]=='log' or keys[i]=='CARDS' or keys[i]=='INFOHEADER' or keys[i]=='HDULIST':
                            pass
                        else:
                            sqlStmt = sqlStmt + keys[i] + f" {values[i]}, "
                                                    # print(key,value)
                        pass
                stmt=sqlStmt[:-2]+')'

            print(stmt)
        cnx.close()
        # sys.exit()

        # create_current_scan_directory()
        self.create_final_plot_directory(src,tbFreq)
        # sys.exit()

        if 'S' in (frontend):
            if '13.0S' in frontend or '18.0S' in frontend:
                set_dict_item(self.__dict__,'BEAMTYPE',ScanType.SBW.name, 'wide single beam drift scan')
            elif '02.5S' in frontend or '04.5S' in frontend or '01.3S' in frontend:
                set_dict_item(self.__dict__,'BEAMTYPE',ScanType.SBN.name, 'narrow single beam drift scan')
            else:
                print(f'Unknown beam type :{frontend} - contact author to have it included\n')
                sys.exit()

            print('about to process')
            sys.exit()
            # get driftscan data from file
            driftScans=DriftScans(self.__dict__)
            driftScans.process_data() # process the data
            del driftScans # release from memory

        elif 'D' in (frontend):
            set_dict_item(self.__dict__,'BEAMTYPE',ScanType.DB.name, 'dual beam drift scan')
            # sys.exit()
            # get driftscan data from file
            driftScans=DriftScans(self.__dict__)
            driftScans.process_data() # process the data
            del driftScans # release from memory
            # sys.exit()

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
                or 'TCALSIG' in column or 'HAPOINTC' in column or 'DEPOINTC' in column:
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

                    
                    if 'D' in str(self.__dict__['FRONTEND']['value']) and '_CAL' in hduIndexName:
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
                    elif 'S'  in str(self.__dict__['FRONTEND']['value']):
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

        print(src, freq)
        self.plotDir=(f'plots/{src}/{int(freq)}').replace(' ','')
        msg_wrapper("info",self.log.debug,f"Creating directory to store processed plots: {self.plotDir}")
        try:
            os.makedirs(self.plotDir)
        except:
            pass
