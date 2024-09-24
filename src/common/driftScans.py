from .driftScanAttributes import DriftScanAttributes
from .driftScanData import DriftScanData
from .dataProcessingFlowManager import DataProcessingFlowManager
from .msgConfiguration import msg_wrapper
from .miscellaneousFunctions import set_table_name
from dataclasses import dataclass
import numpy as np
import sys,os 
from .miscellaneousFunctions import create_current_scan_directory
from .sqlite_db import SQLiteDB
from .calibrate import calibrate
import pandas as pd
import matplotlib.pyplot as plt
from config import DBNAME
import sqlite3

@dataclass
class DriftScans(DriftScanAttributes):
    """
    Driftscan object

    Args:
        data (dict): dictionary of fitsfile data
    """

    __dict__: dict
    
    def add_missing_values(self,myDict,listOfKeys):
        """Sometimes the data did not record properly and you get enitre
        missing scans. If this happens"""
        dbInfo={}
        for k,v in myDict:
            # print(k,v)
            try:
                if k in listOfKeys:
                    pass
                else:
                    if k=='FILEPATH':
                        filename=v['value'].split('/')[-1]
                        msg_wrapper("debug",self.log.debug,f'>>{k}: {v["value"]}')
                        dbInfo['FILENAME']=filename
                        dbInfo[k]=v['value']
                        msg_wrapper("debug",self.log.debug,f'>> FILENAME: {dbInfo["FILENAME"]}')
                    elif k=='DATE':
                        dbInfo['OBSDATE']=v['value']
                        msg_wrapper("debug",self.log.debug,f'^^{k}: {v["value"]}')
                    else:
                        dbInfo[k]=v['value']
                        msg_wrapper("debug",self.log.debug,f'**{k}: {v["value"]}') #self.__dict__)#['FILEPATH']['value'].split('/')[-1])
            except:
                # print('###',k,v)
                try:
                    msg_wrapper("debug",self.log.debug,f'--{k}: {v["value"]}')
                    dbInfo[k]=v['value']
                except:
                    if 'plot' in k:
                        pass
                    else:
                        msg_wrapper("debug",self.log.debug,f'--{k}: {v}')
                        dbInfo[k]=v
        return dbInfo
    
    def try_test(self,key,myDict,tag,val=''):
        
        try:
            x=myDict[key]
            # print(x)
            
            myDict[f'{tag}{key}']=x
            # print('+-+-+',f'{tag}{key}',key, tag, myDict[f'{tag}{key}'])
        except:
            if val=='':
                myDict[f'{tag}{key}']=np.nan
                # print('+---+',f'{tag}{key}',key, tag, myDict[f'{tag}{key}'])
            else:
                myDict[f'{tag}{key}']=val
                # print('+-/-+',f'{tag}{key}',key, tag, myDict[f'{tag}{key}'])

    def fill_in_missing_data_sb(self, myDict,tag=''):
        """ Fill in the missing data from the observing file"""
        keys=['RMSB','RMSA','TA','TAERR','BRMS','SLOPE',
            'MIDOFFSET','FLAG','PEAKLOC','BASELEFT','BASERIGHT',
            'S2N']
        for key in keys:
            self.try_test(key,myDict,tag)
        self.try_test('FLAG',myDict,tag,56)

    def fill_in_missing_data_db_common(self, myDict,tag=''):
        """ Fill in the missing data from the observing file"""
        keys=['RMSB','RMSA','BRMS','SLOPE',
            'MIDOFFSET','BASELEFT','BASERIGHT']
        for key in keys:
            self.try_test(key,myDict,tag)
        # self.try_test('FLAG',myDict,tag,56)

    def fill_in_missing_data_db_beams(self, myDict,tag=''):
        """ Fill in the missing data from the observing file"""
        keys=['TA','TAERR','FLAG','PEAKLOC','S2N']
        for key in keys:
            self.try_test(key,myDict,tag)
  
    def getScanData(self, key):
        try:
            return self.__dict__[key]['value']
        except:
            return []
        
    def get_scans(self, scanDict:dict, scanKey:str):
        offset=scanDict(f'{scanKey}_OFFSET') 
        lcp=scanDict(f'{scanKey}_TA_LCP') 
        rcp=scanDict(f'{scanKey}_TA_RCP') 
        return offset, lcp, rcp
    
    def process_data(self):
        """
        Process the drift scan observations. Get observations from the files
        and prepare it for analysis.
        """
        create_current_scan_directory()

        
        frontend=self.__dict__['FRONTEND']['value']
        theoFit=self.__dict__['theoFit']
        autoFit=self.__dict__['autoFit']
        frq=int(self.__dict__['CENTFREQ']['value'])
        
        hpbw=self.__dict__['HPBW']['value']
        fnbw=self.__dict__['FNBW']['value']
        log=self.__dict__['log']

        fileName=((self.__dict__['FILEPATH']['value']).split("/")[-1])[:18]
        self.__dict__['FILENAME']=fileName
        src=self.__dict__['OBJECT']['value']
        src=src.replace(' ','')
        saveTo=f'plots/{src}/{int(frq)}'

        # print(saveTo)
        msg_wrapper("debug",self.log.debug,f"Saving plots to: {saveTo}")
        msg_wrapper("info",self.log.info,f"Getting drift scans from file")
            
        # for k,v in self.__dict__.items():
        #     print(k,v)
        
        # print(frontend)
        # sys.exit()
        if 'S' in frontend: 

            #'13.0S' or "18.0S" or '02.5S' or "04.5S" or '01.3S' :
            
            # Get driftscan data
            data=DriftScanData(self.__dict__) # get the driftscan data
            
            # print(frontend)
            # sys.exit()
            if frontend == '13.0S' or frontend == "18.0S":
                # onOffset=self.getScanData('ON_OFFSET') #self.__dict__['ON_OFFSET']['value']
                # lcpOnScan=self.getScanData('ON_TA_LCP') #self.__dict__['ON_TA_LCP']['value']
                # rcpOnScan=self.getScanData('ON_TA_RCP') #self.__dict__['ON_TA_RCP']['value']
                onOffset, lcpOnScan, rcpOnScan = self.get_scans(self.getScanData,'ON')
                dataScans=[onOffset,lcpOnScan,rcpOnScan]
            else:
                # hpnOffset=self.getScanData('HPN_OFFSET') #self.__dict__['HPN_OFFSET']['value']
                # lcpHpnScan=self.getScanData('HPN_TA_LCP') #self.__dict__['HPN_TA_LCP']['value']
                # rcpHpnScan=self.getScanData('HPN_TA_RCP') #self.__dict__['HPN_TA_RCP']['value']
                hpnOffset, lcpHpnScan, rcpHpnScan = self.get_scans(self.getScanData,'HPN')

                # hpsOffset=self.getScanData('HPS_OFFSET') #self.__dict__['HPS_OFFSET']['value']
                # lcpHpsScan=self.getScanData('HPS_TA_LCP') #self.__dict__['HPS_TA_LCP']['value']
                # rcpHpsScan=self.getScanData('HPS_TA_RCP') #self.__dict__['HPS_TA_RCP']['value']
                hpsOffset, lcpHpsScan, rcpHpsScan = self.get_scans(self.getScanData,'HPS')

                # onOffset=self.getScanData('ON_OFFSET') #self.__dict__['ON_OFFSET']['value']
                # lcpOnScan=self.getScanData('ON_TA_LCP') #self.__dict__['ON_TA_LCP']['value']
                # rcpOnScan=self.getScanData('ON_TA_RCP') #self.__dict__['ON_TA_RCP']['value']
                onOffset, lcpOnScan, rcpOnScan = self.get_scans(self.getScanData,'ON')

                dataScans=[hpnOffset,lcpHpnScan,rcpHpnScan,
                    hpsOffset,lcpHpsScan,rcpHpsScan,
                    onOffset,lcpOnScan,rcpOnScan]
            
            # create tables for scans and database data structure
            scanData={} 
            tableData={} 

            # print(lcpHpsScan)
            # print(data)
            # sys.exit()

            if len(dataScans)==3:
                tag="ON"
                tags=[tag]
                x=dataScans[0]
                lcp=dataScans[1]
                rcp=dataScans[2]

                # process the data - i.e. run the fitting and plotting algorithms
                processedLCPData=DataProcessingFlowManager(fileName,frq,src,x,lcp,log,0,'y',saveTo,f'{tag}_LCP','LCP',frontend,hpbw,fnbw,theoFit, autoFit)
                processedRCPData=DataProcessingFlowManager(fileName,frq,src,x,rcp,log,0,'y',saveTo,f'{tag}_RCP','RCP',frontend,hpbw,fnbw,theoFit, autoFit)
                # sys.exit()
                self.fill_in_missing_data_sb(processedLCPData.__dict__,f'{tag[0]}L')
                self.fill_in_missing_data_sb(processedRCPData.__dict__,f'{tag[0]}R')

                scanData[tag]={'lcp':processedLCPData, 'rcp':processedRCPData}

                del processedLCPData
                del processedRCPData

                # get missing keys, 'plotDir',
                listOfKeys=['ON_OFFSET', 'ON_RA_J2000', 
                            'RAW_ON_LCPDATA', 'RAW_ON_RCPDATA', 
                            'ON_TA_LCP', 'ON_TA_RCP', 
                            'FILENAME', 'log', 'HDULIST', 
                            'INFOHEADER', 'theoFit', 'autoFit', 'CARDS']
            
            else:
                tags=['HPN','HPS','ON']
                for i in range(len(dataScans)):
                    if i%3==0:
                        if i == 0:
                            tag=tags[0]
                        elif i==3:
                            tag=tags[1]
                        elif i==6:
                            tag=tags[2]
                        x=dataScans[i]
                        lcp=dataScans[i+1]
                        rcp=dataScans[i+2]

                        # process the data - i.e. run the fitting and plotting algorithms
                        processedLCPData=DataProcessingFlowManager(fileName,frq,src,x,lcp,log,0,'y',saveTo,f'{tag}_LCP','LCP',frontend,hpbw,fnbw,theoFit, autoFit)
                        processedRCPData=DataProcessingFlowManager(fileName,frq,src,x,rcp,log,0,'y',saveTo,f'{tag}_RCP','RCP',frontend,hpbw,fnbw,theoFit, autoFit)
                        # if tag=='ON':
                        #     sys.exit()

                        if tag=='ON':
                            tg='O'
                        elif tag=='HPN':
                            tg='N'
                        elif tag=='HPS':
                            tg='S'

                        self.fill_in_missing_data_sb(processedLCPData.__dict__,f'{tg}L')
                        self.fill_in_missing_data_sb(processedRCPData.__dict__,f'{tg}R')

                        scanData[tag]={'lcp':processedLCPData, 'rcp':processedRCPData}

                        del processedLCPData
                        del processedRCPData

                # get missing keys, 'plotDir'   ,
                listOfKeys=['HPN_OFFSET','HPN_RA_J2000','RAW_HPN_LCPDATA','RAW_HPN_RCPDATA','HPN_TA_LCP','HPN_TA_RCP', 
                            'HPS_OFFSET','HPS_RA_J2000','RAW_HPS_LCPDATA','RAW_HPS_RCPDATA','HPS_TA_LCP','HPS_TA_RCP',
                            'ON_OFFSET' ,'ON_RA_J2000' ,'RAW_ON_LCPDATA','RAW_ON_RCPDATA','ON_TA_LCP' ,'ON_TA_RCP' ,
                            'FILENAME'  , 'log'      , 'HDULIST', 
                            'INFOHEADER','theoFit'   ,'autoFit'   , 'CARDS']

            myDict=self.__dict__.items()
            tableData=self.add_missing_values(myDict,listOfKeys)
            # print(len(scanData))
            
            pols=['lcp','rcp']
            # print(tags,pols)
            # sys.exit()
            # print(tableData)
            # sys.exit()

            for pol in pols:

                print()

                for tag in tags:

                    # print('\nWorking on:', tag,pol)
                    # sys.exit()
                    scan=scanData[f'{tag}'][pol].__dict__

                    # print(scan)
                    # sys.exit()
                    for k,v in scan.items():
                        # print('in - ',k,v)
                        # sys.exit()
                        if 'Cleaned' in k or 'log' == k or 'x' == k or 'y' == k\
                            or k=='applyRFIremoval' or k=='spl' or k=='pt'\
                                or k=='srcTag' or k=='flag' or k=='pol':
                            pass
                        elif f'{tag.upper()}_{pol.upper()}' in k:
                            # print(f'{tag.upper()}_{pol.upper()}')
                            # sys.exit()
                            for s,t in v.items():
                                if 'peakModel' in s or 'correctedData' in s\
                                    or 'peakPts' in s or 'Res' in s  or 'baseLocs' in s:
                                    # print('+',s)
                                    pass
                                else:
                                    
                                    # print('-<<',s,t)
                                    if tag=='ON':
                                        tg='O'
                                    elif tag=='HPN':
                                        tg="N"
                                    elif tag=="HPS":
                                        tg="S"
                                    # tg=tag
                                    div='' #divider = '_' or ""
                                    # print(tg,pol)
                                    if s=='peakFit':
                                        # print(f'{tg}{pol[0]}{div}TA'.upper(),t)
                                        tableData[f'{tg}{pol[0]}{div}TA'.upper()]=t
                                        # dbInfo[f'{c[i]}TA'.upper()]=n
                                    elif s=='peakRms':
                                        # print(f'{tg}{pol[0]}{div}TAERR'.upper(),t)
                                        tableData[f'{tg}{pol[0]}{div}TAERR'.upper()]=t
                                    elif s=='s2n':
                                        # print(f'${tg}{pol[0]}{div}s2n'.upper(),t)
                                        tableData[f'{tg}{pol[0]}{div}s2n'.upper()]=t
                                    elif s=='midXValue':
                                        # print(f'{tg}{pol[0]}{div}midoffset'.upper(),t)
                                        tableData[f'{tg}{pol[0]}{div}midoffset'.upper()]=t
                                    elif s=='driftRms':
                                        # print(f'{tg}{pol[0]}{div}BRMS'.upper(),t)
                                        tableData[f'{tg}{pol[0]}{div}BRMS'.upper()]=t
                                    elif 'driftCoeffs' in s:
                                        # print(f'{tg}{pol[0]}{div}SLOPE'.upper(),t[0])

                                        coeff=t #.split()

                                        try:
                                            tableData[f'{tg}{pol[0]}{div}SLOPE'.upper()]=float(coeff[0])
                                        except:
                                            tableData[f'{tg}{pol[0]}{div}SLOPE'.upper()]=np.nan
                                        # dbInfo[f'{c[i]}intercept']=float(coeff[1])
                                    
                                    elif 'base' in s:
                                        ch=str(t).replace(',',';').replace('[','').replace(']','')
                                        # print(s,ch)
                                        tableData[f'{tg}{pol[0]}{div}{s}'.upper()] = ch
                                        # print(f'{tg}{pol[0]}{div}{s}'.upper(),ch)
                                    else:
                                        if 'msg' in s:
                                            pass
                                        else:
                                            tableData[f'{tg}{pol[0]}{div}{s}'.upper()] = t
                                            # print(f'==== {tg}{pol[0]}{div}{s}'.upper(),t)
                        else:
                            # if pol==pols[0] and tag==tags[0]:
                                # print(f'{tag[0]}{pol[0]}')
                                # print('===',tag,pol[0])

                                if tag=='HPN':
                                    tg='N'
                                elif tag=='ON':
                                    tg='O'
                                elif tag=='HPS':
                                    tg='S'

                                key=f'{tg}{pol[0]}'.upper()
                                # print('$$$',key)
                                if k == 'fileName':
                                    tableData['OBSNAME']=v
                                    # print('<<',k,v)
                                # elif k.startswith(f'{tag[0]}{pol[0]}'.upper()): #'RMS' in k:
                                #     tableData[k]=v
                                #     print('>>',k,v)
                                elif 'RMSB' in k:
                                    if k==f'{key}RMSB' :
                                        # print('>>>',k,v) 
                                        tableData[k.upper()]=v
                                elif 'RMSA' in k:
                                    if k==f'{key}RMSA' :
                                        # print('<<<',k,v) 
                                        tableData[k.upper()]=v   
                                else:
                                    # print('<<-',k,v)
                                    if tag=='HPS' or tag=='HPN':
                                        # print(f'=*= {k}'.upper(), f'{tag[-1]}{pol[0]}rms'.upper())
                                        if f'{tag[-1]}{pol[0]}rms'.upper() in k:
                                            tableData[f'{div}{k}'.upper()]=v

            # sys.exit()
            # Calibrate the data
            for k,v in tableData.items():
                if k=='OLTA' and len(tags)>1:
                    pc,ta,taErr=calibrate(tableData['SLTA'], tableData['SLTAERR'], tableData['NLTA'], tableData['NLTAERR'], tableData['OLTA'], tableData['OLTAERR'], tableData, self.log)
                    tableData['OLPC']=pc
                    tableData['COLTA']=ta
                    tableData['COLTAERR']=taErr
                    break
                
            for k,v in tableData.items():
                if k=='ORTA' and len(tags)>1:
                    pc,ta,taErr=calibrate(tableData['SRTA'], tableData['SRTAERR'], tableData['NRTA'], tableData['NRTAERR'], tableData['ORTA'], tableData['ORTAERR'], tableData, self.log)        
                    tableData['ORPC']=pc
                    tableData['CORTA']=ta
                    tableData['CORTAERR']=taErr
                    break

            # for k,v in tableData.items():
            #     if k=='keys' or k=='values':
            #         pass
            #     else:
            #         if 'S2N' in k:# or 'RMS' in k:
            #             print('* ',k,': ',v)
            # sys.exit()
            tableData['SRC']=tableData['OBJECT'].replace(' ','')
            freq=int(tableData['CENTFREQ'])
            dbTable = f"{tableData['SRC']}_{freq}"#.replace('-','m').replace('+','p')
            dbTable=set_table_name(dbTable,self.log)

            try:
                int(dbTable[0])
                dbTable=f"_{dbTable}"
            except:
                pass

            print(f'Saving to Table: {dbTable}', freq)

            # sys.exit()
            # Get data to save to dictionary
            # --- Setup database where you will be storing information
            msg_wrapper("debug",self.log.debug,"Setup database")

            # df=pd.DataFrame(tableData)
            # print(df)

            # if 'S' in tableData['FRONTEND']: #=='13.0S':
            #     tableData.pop('HABMSEP',None)
            #     tableData.pop('SEC_Z',None)
            #     tableData.pop('X_Z',None)
            #     tableData.pop('DRY_ATMOS_TRANSMISSION',None)
            #     tableData.pop('ZENITH_TAU_AT_1400M',None)
            #     tableData.pop('ABSORPTION_AT_ZENITH',None)

            # print(tableData.keys())
            # sys.exit()

            finalDict={}
            for m in tableData['keys']:
                # print('\n',m)
                for k,v in tableData.items():
                    if m==k:
                        if m=='keys' or m=='values':
                            pass
                        else:
                            # print(m,k,v)
                            # if tableData['FRONTEND']=='13.0S' and tableData['']:
                            #     print(m,k,v)
                            #     print(tableData)
                            #     sys.exit()
                            try:
                                # print(m,k,v['value'])
                                finalDict[k]=v['value']
                            except:
                                # print(m,k,v)
                                finalDict[k]=v
                    
            # print(tableData['keys'])
            # # print(tableData['values'])
            # for l,v in finalDict.items():
            #     print(l,v)
            # sys.exit()

            # print(finalDict['OBSDATE'].split('T')[0])
            # Get date
            finalDict['OBSDATE']=finalDict['OBSDATE'].split('T')[0]
            # print(finalDict['OBSDATE'])
            # print(finalDict)
            # print(len(tableData['keys']),len(tableData['values'][:-1]),len(finalDict))
# 
            # print('here')
            # print(finalDict['FILEPATH'])
            # sys.exit()

            db= SQLiteDB('HART26DATA.db',self.log)
            db.create_db()
            table=db.create_table(finalDict,dbTable)
            db.populate_table(finalDict, table)
            db.close_db()

            # print(finalDict['FILEPATH'])
            # sys.exit()
            # sys.exit()
   
        elif 'D' in frontend: 
            # '03.5D' or "06.0D"

            # Get driftscan data
            data=DriftScanData(self.__dict__)
            # for k,v in data.__dict__.items():
            #     print('---',k,v)
            # sys.exit()
            hpnOffset=self.getScanData('HPN_OFFSET') #self.__dict__['HPN_OFFSET']['value']
            lcpHpnScan=self.getScanData('HPN_TA_LCP') #self.__dict__['HPN_TA_LCP']['value']
            rcpHpnScan=self.getScanData('HPN_TA_RCP') #self.__dict__['HPN_TA_RCP']['value']

            hpsOffset=self.getScanData('HPS_OFFSET') #self.__dict__['HPS_OFFSET']['value']
            lcpHpsScan=self.getScanData('HPS_TA_LCP') #self.__dict__['HPS_TA_LCP']['value']
            rcpHpsScan=self.getScanData('HPS_TA_RCP') #self.__dict__['HPS_TA_RCP']['value']

            onOffset=self.getScanData('ON_OFFSET') #self.__dict__['ON_OFFSET']['value']
            lcpOnScan=self.getScanData('ON_TA_LCP') #self.__dict__['ON_TA_LCP']['value']
            rcpOnScan=self.getScanData('ON_TA_RCP') #self.__dict__['ON_TA_RCP']['value']

            dataScans=[hpnOffset,lcpHpnScan,rcpHpnScan,
                    hpsOffset,lcpHpsScan,rcpHpsScan,
                    onOffset,lcpOnScan,rcpOnScan]
            
            # create tables for scans and database data structure
            scanData={} 
            tableData={} 

            tags=['HPN','HPS','ON']
            for i in range(len(dataScans)):
                if i%3==0:
                    if i == 0:
                        tag=tags[0]
                    elif i==3:
                        tag=tags[1]
                    elif i==6:
                        tag=tags[2]
                    x=dataScans[i]
                    lcp=dataScans[i+1]
                    rcp=dataScans[i+2]

                    # process the data - i.e. run the fitting and plotting algorithms
                    processedLCPData=DataProcessingFlowManager(fileName,frq,src,x,lcp,log,0,'y',saveTo,f'{tag}_LCP','LCP',frontend,hpbw,fnbw,theoFit, autoFit)
                    processedRCPData=DataProcessingFlowManager(fileName,frq,src,x,rcp,log,0,'y',saveTo,f'{tag}_RCP','RCP',frontend,hpbw,fnbw,theoFit, autoFit)
                    if tag=='ON':
                        tg='O'
                    else:
                        tg=tag[-1]
                    
                    myTag=f'{tg}L'
                    # print(myTag,f'A{myTag}',f'B{myTag}')
                    # print(processedLCPData.__dict__.keys())
                    # print(processedRCPData.__dict__.keys())
                    # sys.exit()
                    
                    self.fill_in_missing_data_db_common(processedLCPData.__dict__,myTag)
                    self.fill_in_missing_data_db_beams(processedLCPData.__dict__,f'A{myTag}')
                    self.fill_in_missing_data_db_beams(processedLCPData.__dict__,f'B{myTag}')
                    self.fill_in_missing_data_db_common(processedRCPData.__dict__,myTag)
                    self.fill_in_missing_data_db_beams(processedRCPData.__dict__,f'A{myTag}')
                    self.fill_in_missing_data_db_beams(processedRCPData.__dict__,f'B{myTag}')
                    
                    
                    scanData[tag]={'lcp':processedLCPData, 'rcp':processedRCPData}

                    # print(processedLCPData)
                    # sys.exit()

                    del processedLCPData
                    del processedRCPData

                    # get missing keys, 'plotDir',
                    listOfKeys=['HPN_OFFSET','HPN_RA_J2000','RAW_HPN_LCPDATA','RAW_HPN_RCPDATA','HPN_TA_LCP','HPN_TA_RCP', 
                            'HPS_OFFSET','HPS_RA_J2000','RAW_HPS_LCPDATA','RAW_HPS_RCPDATA','HPS_TA_LCP','HPS_TA_RCP',
                            'ON_OFFSET' ,'ON_RA_J2000' ,'RAW_ON_LCPDATA','RAW_ON_RCPDATA','ON_TA_LCP' ,'ON_TA_RCP' ,
                            'FILENAME'  , 'log'      , 'HDULIST', 
                            'INFOHEADER','theoFit'   ,'autoFit'   , 'CARDS']

            myDict=self.__dict__.items()
            tableData=self.add_missing_values(myDict,listOfKeys)
            pols=['lcp','rcp']
            beams=['A','B']

            # print(myDict)
            # sys.exit()
            # for beam in beams:
            # cnt=0
            for pol in pols:
                print()
                for tag in tags:
                    # print('\nWorking on:', tag,pol)
                    # print(f'{tag.upper()}_{pol.upper()}')
                    # print(scanData.keys())
                    scan=scanData[f'{tag}'][pol].__dict__
                    # print(scan.keys())
                    # sys.exit()
                    for k,v in scan.items():
                        # print(k)
                        if 'Cleaned' in k or 'log' == k or 'x' == k or 'y' == k\
                            or k=='applyRFIremoval' or k=='spl' or k=='pt'\
                            or k=='srcTag' or k=='flag' or k=='pol':
                            pass

                        elif f'{tag.upper()}_{pol.upper()}' in k:
                            # print(f'{tag.upper()}_{pol.upper()}')

                            for s,t in v.items():
                                # print('-+-',s)

                                if 'PeakModel' in s or 'correctedData' in s\
                                    or 'PeakData' in s or 'Res' in s: # or  'baseLocs' in s:
                                    # print('+',s)
                                    pass
                                
                                else:

                                    # print('-<<',k,s,t)
                                    if tag=='ON':
                                        tg='O'
                                    elif tag=='HPN':
                                        tg="N"
                                    elif tag=="HPS":
                                        tg="S"

                                    div='' #divider = '_' or ""

                                    if s=='leftPeakFit':
                                        # print(f'{beams[0]}{tg}{pol[0]}{div}TA'.upper(),t)
                                        tableData[f'{beams[0]}{tg}{pol[0]}{div}TA'.upper()]=t
                                        #     # dbInfo[f'{c[i]}TA'.upper()]=n
                                    elif s=='leftPeakFitErr':
                                        # print(f'{beams[0]}{tg}{pol[0]}{div}TAERR'.upper(),t)
                                        tableData[f'{beams[0]}{tg}{pol[0]}{div}TAERR'.upper()]=t
                                    elif s=='s2na':
                                        # print(f'{beams[0]}{tg}{pol[0]}{div}s2n'.upper(),t)
                                        tableData[f'{beams[0]}{tg}{pol[0]}{div}s2n'.upper()]=t
                                    elif s=='midXValueLeft':
                                        # print(f'{beams[0]}{tg}{pol[0]}{div}midoffset'.upper(),t)
                                        tableData[f'{beams[0]}{tg}{pol[0]}{div}midoffset'.upper()]=t
                                            
                                    elif s=='rightPeakFit':
                                        # print(f'{beams[1]}{tg}{pol[0]}{div}TA'.upper(),t)
                                        tableData[f'{beams[1]}{tg}{pol[0]}{div}TA'.upper()]=t
                                        #     # dbInfo[f'{c[i]}TA'.upper()]=n
                                    elif s=='rightPeakFitErr':
                                        # print(f'{beams[1]}{tg}{pol[0]}{div}TAERR'.upper(),t)
                                        tableData[f'{beams[1]}{tg}{pol[0]}{div}TAERR'.upper()]=t
                                    elif s=='s2nb':
                                        # print(f'{beams[1]}{tg}{pol[0]}{div}s2n'.upper(),t)
                                        tableData[f'{beams[1]}{tg}{pol[0]}{div}s2n'.upper()]=t
                                    elif s=='midXValueRight':
                                        # print(f'{beams[1]}{tg}{pol[0]}{div}midoffset'.upper(),t)
                                        tableData[f'{beams[1]}{tg}{pol[0]}{div}midoffset'.upper()]=t
                                    
                                    elif s=='driftRms':
                                            # print('drift rms: ', f'{tg}{pol[0]}{div}BRMS'.upper(),t)
                                            tableData[f'{tg}{pol[0]}{div}BRMS'.upper()]=t
                                    elif 'driftCoeffs' in s:
                                        # print('driftCoeffs: ', f'{tg}{pol[0]}{div}BRMS'.upper(),t)
                                        # print(f'{tg}{pol[0]}{div}SLOPE'.upper(),t[0])

                                        # coeff=t #.split()
                                        # print(t)
                                        try:
                                            if len(t)==0:

                                                # tableData[f'{beams[0]}{tg}{pol[0]}{div}BASELocs'.upper()] = np.nan
                                                tableData[f'{tg}{pol[0]}{div}SLOPE'.upper()]=np.nan
                                                # print(f'### {tg}{pol[0]}{div}SLOPE'.upper())
                                            else:
                                                tableData[f'{tg}{pol[0]}{div}SLOPE'.upper()]=t[0]
                                                # print(f'xxx {tg}{pol[0]}{div}SLOPE'.upper())
                                        except:
                                            tableData[f'{tg}{pol[0]}{div}SLOPE'.upper()]=np.nan
                                            # print(f'--- {tg}{pol[0]}{div}SLOPE'.upper())
                                        # dbInfo[f'{c[i]}intercept']=float(coeff[1])
                                    elif 'baseLocsLeft' in s:
                                        # print(f'{beams[0]}{tg}{pol[0]}{div}BASELeft'.upper(), f'{t[0]};{t[-1]}')
                                        #     ch=str(t).replace(',',';').replace('[','').replace(']','')
                                        #     # print(s,ch)
                                        # print(s)
                                        # print(t)
                                        # print('out')
                                        if len(t)==0:
                                            tableData[f'{beams[0]}{tg}{pol[0]}{div}BASELocs'.upper()] = ''
                                        else:
                                            tableData[f'{beams[0]}{tg}{pol[0]}{div}BASELocs'.upper()] = f'{t[0]};{t[-1]}'
                                        #     # print(f'{tg}{pol[0]}{div}{s}'.upper(),ch)
                                    elif 'baseLocsRight' in s:
                                        # print(f'{beams[1]}{tg}{pol[0]}{div}BASERight'.upper(),f'{t[0]};{t[-1]}')
                                        #     ch=str(t).replace(',',';').replace('[','').replace(']','')
                                        #     # print(s,ch)
                                        if len(t)==0:
                                            tableData[f'{beams[1]}{tg}{pol[0]}{div}BASELocs'.upper()] = ''
                                        else:
                                            tableData[f'{beams[1]}{tg}{pol[0]}{div}BASElocs'.upper()] = f'{t[0]};{t[-1]}'
                                        #     # print(f'{tg}{pol[0]}{div}{s}'.upper(),ch)
                                    elif 'Combined' in s:
                                        pass
                                    else:
                                        if 'msg' in s:
                                            pass
                                        else:
                                            tableData[f'{tg}{pol[0]}{div}{s}'.upper()] = t
                                            # print(f'>>>> {tg}{pol[0]}{div}{s}'.upper(),t)

                        else:
                            # pass
                            # print('-----',k,beams[0])

                            # if k == 'fileName':
                            #     tableData['OBSNAME']=v
                            if tag=='ON':
                                tg='O'
                            elif tag=='HPN':
                                tg="N"
                            elif tag=="HPS":
                                tg="S"
                            div=''

                            if 'RMSB' in k: # or 'RMSA' in k:
                                tg=f'{tg}{pol[0]}'.upper()
                                
                                if pol=='rcp' :
                                    tg=f'{tg}R'.upper()
                                    k=k.replace('L','R')
                                    # print(k,v,tg)
                                    tableData[f'{k}'.upper()]=v
                                else:
                                    if tg in k:
                                        # print(pol,tag,k,v, 'L')
                                        # print(k,v)
                                        tableData[f'{k}'.upper()]=v
                                    else:
                                        pass
                            # elif 'RMSA' in k: # or 'RMSA' in k:
                                
                                # print(pol,tag,k,v)
                                
                                # # tableData[k]=v
                            elif 'RMSA' in k: # or 'RMSA' in k:
                                
                                # print(tg)
                                if pol=='rcp' :
                                    tg=f'{tg}R'.upper()
                                    k=k.replace('L','R')
                                    # print(k,v,tg)
                                    tableData[f'{k}'.upper()]=v
                                    # print('>>>',tg,pol)
                                    # if tg in k:
                                    #     print(pol,tag,k,v,'R')
                                    # else:
                                    #     pass
                                else:
                                    tg=f'{tg}{pol[0]}'.upper()
                                    if tg in k:
                                        # print(pol,tag,k,v, 'L')
                                        # print(k,v)
                                        tableData[f'{k}'.upper()]=v
                                    else:
                                        pass
                            # elif 'RMSA' in k: # or 'RMSA' in k:
                                
                                # print(pol,tag,k,v)

                                
                                # if pol=='LCP' or pol=='lcp':
                                #     p='L'
                                # elif pol=='RCP' or pol=='rcp':
                                #     p='R'
                                # else:
                                #     print(pol)
                                #     print('ERROR: unknown polarization')
                                #     sys.exit()
                                #     # continue
                                # print('pol: ', pol)

                                # if k=='RMSA' or k=='RMSB':
                                #     print('((((()))))',k,f'{tg}{p}{k}'.upper(),v)
                                # else:
                          
                                #     print('-->>-',k, tag,f'{k}'.upper(),v)
                            #     tableData[f'{k}'.upper()]=v
                                # tableData[f'{beams[0]}{tg}{p}{k}'.upper()]=v

                            # else:
                            #     pass

            # sys.exit()

            # for k,v in tableData.items():
            #     print(k,v)

            for beam in beams:
                for k,v in tableData.items():
                    if k==f'{beam}OLTA':
                        pc,ta,taErr=calibrate(tableData[f'{beam}SLTA'], tableData[f'{beam}SLTAERR'], tableData[f'{beam}NLTA'], tableData[f'{beam}NLTAERR'], tableData[f'{beam}OLTA'], tableData[f'{beam}OLTAERR'], tableData, self.log)
                        tableData[f'{beam}OLPC']=pc
                        tableData[f'{beam}COLTA']=ta
                        tableData[f'{beam}COLTAERR']=taErr
                        break

            for beam in beams:
                for k,v in tableData.items():
                    if k==f'{beam}ORTA':
                        # print('----',tableData[f'{beam}SRTAERR'])

                        srta=float(tableData[f'{beam}SRTA'])
                        try:
                            srtaerr= float(tableData[f'{beam}SRTAERR'])
                        except:
                            srtaerr=np.nan
                            tableData[f'{beam}SRTAERR']=np.nan

                        nrta= float(tableData[f'{beam}NRTA'])

                        try:
                            nrtaerr= float(tableData[f'{beam}NRTAERR'])
                        except:
                            nrtaerr= np.nan
                            tableData[f'{beam}NRTAERR']=np.nan
                        orta=float(tableData[f'{beam}ORTA'])

                        try:
                            ortaerr=float( tableData[f'{beam}ORTAERR'])
                        except:
                            ortaerr=np.nan
                            tableData[f'{beam}ORTAERR']=np.nan
                            
                        # print(srta,srtaerr,orta,ortaerr,nrta,nrtaerr)
                        pc,ta,taErr=calibrate(srta, srtaerr, nrta,nrtaerr, orta,ortaerr, tableData, self.log)
                        tableData[f'{beam}ORPC']=pc
                        tableData[f'{beam}CORTA']=ta
                        tableData[f'{beam}CORTAERR']=taErr
                        break

            # Calibrate the data
            finalData={}
            for k,v in tableData.items():
                if k=='keys' or k=='values':
                    pass
                else:
                    
                    if k=='RMSA' or k=='RMSB':
                        pass
                    else:
                        # print('* ',k,': ',v)
                        finalData[k]=v
                # if 'RMS' in k:
                # #     print(k)
                #     print('* ',k,': ',v)
                # #     sys.exit()

            # Save to table
            finalData['SRC']=finalData['OBJECT'].replace(' ','')
            freq=int(finalData['CENTFREQ'])
            dbTable = f"{finalData['SRC']}_{freq}"

            # print(dbTable)
            # sys.exit()
            try:
                int(dbTable[0])
                dbTable=f"_{dbTable}"
            except:
                pass

            print(f'Table: {dbTable}', freq, frq)
            print(self.__dict__['FILEPATH']['value'])

            # sys.exit()
            # dbTable=set_table_name(dbTable, self.log)

            # Get data to save to dictionary
            # --- Setup database where you will be storing information
            msg_wrapper("debug",self.log.debug,"Setup database")
            db= SQLiteDB(DBNAME,self.log)
            db.create_db()
            table=db.create_table(finalData,dbTable)

            # print(table)

            # if str(int(freq)) in self.__dict__['FILEPATH']['value']:
            #     print('same freq')
            db.populate_table(finalData, table)
            db.close_db()
            # else:
            #     print("Frequency of source doesn't match path frequency")
            #     # open database and match
            #     # check if table exists in database
            #     cnx = sqlite3.connect(DBNAME)
            #     # dbTables= pd.read_sql_query("SELECT name FROM sqlite_schema WHERE type='table'", cnx)
            #     # tables=list(dbTables['name'])
            #     tableData = pd.read_sql_query(f"SELECT * FROM {table}", cnx)
            #     tableFilenames=sorted(list(tableData['FILENAME']))

            #     for file in tableFilenames:
            #         if self.__dict__['FILENAME'] in file:
            #             print('Already processed file: ',self.__dict__['FILEPATH']['value'], 'in table: ', table)
                    # else:
                    #     print('--')
                        # sys.exit()
                # print(tableFilenames, self.__dict__['FILENAME'])
                # if '+' in tables
                # sys.exit()
        
        else:
            print(f"Unknown source frontend value : {self.__dict__[frontend]['value']}. Contact author to have it included.")
            sys.exit()
        
    def process_data_only(self,qv='no'):
        """
        Process the drift scan observations. Get observations from the files
        and prepare it for analysis.
        """
        create_current_scan_directory()

        
        frontend=self.__dict__['FRONTEND']['value']
        theoFit=self.__dict__['theoFit']
        autoFit=self.__dict__['autoFit']
        frq=int(self.__dict__['CENTFREQ']['value'])
        
        hpbw=self.__dict__['HPBW']['value']
        fnbw=self.__dict__['FNBW']['value']
        log=self.__dict__['log']

        fileName=((self.__dict__['FILEPATH']['value']).split("/")[-1])[:18]
        self.__dict__['FILENAME']=fileName
        src=self.__dict__['OBJECT']['value']
        src=src.replace(' ','')
        saveTo=f'plots/{src}/{int(frq)}'

        msg_wrapper("debug",self.log.debug,f"Saving plots to: {saveTo}")
        msg_wrapper("info",self.log.info,f"Getting drift scans from file")
            
        
        if 'S' in frontend: 
            #'13.0S' or "18.0S" or '02.5S' or "04.5S" or '01.3S' :
            
            # Get driftscan data
            data=DriftScanData(self.__dict__) # get the driftscan data
            
            if frontend == '13.0S' or frontend == "18.0S":
                onOffset=self.getScanData('ON_OFFSET') #self.__dict__['ON_OFFSET']['value']
                lcpOnScan=self.getScanData('ON_TA_LCP') #self.__dict__['ON_TA_LCP']['value']
                rcpOnScan=self.getScanData('ON_TA_RCP') #self.__dict__['ON_TA_RCP']['value']

                dataScans=[onOffset,lcpOnScan,rcpOnScan]
                scans=['ON_OFFSET', 'ON_LCP', 'ON_RCP']
                plt.figure(figsize=(10,3))
            else:
                hpnOffset=self.getScanData('HPN_OFFSET') #self.__dict__['HPN_OFFSET']['value']
                lcpHpnScan=self.getScanData('HPN_TA_LCP') #self.__dict__['HPN_TA_LCP']['value']
                rcpHpnScan=self.getScanData('HPN_TA_RCP') #self.__dict__['HPN_TA_RCP']['value']

                hpsOffset=self.getScanData('HPS_OFFSET') #self.__dict__['HPS_OFFSET']['value']
                lcpHpsScan=self.getScanData('HPS_TA_LCP') #self.__dict__['HPS_TA_LCP']['value']
                rcpHpsScan=self.getScanData('HPS_TA_RCP') #self.__dict__['HPS_TA_RCP']['value']

                onOffset=self.getScanData('ON_OFFSET') #self.__dict__['ON_OFFSET']['value']
                lcpOnScan=self.getScanData('ON_TA_LCP') #self.__dict__['ON_TA_LCP']['value']
                rcpOnScan=self.getScanData('ON_TA_RCP') #self.__dict__['ON_TA_RCP']['value']

                dataScans=[hpnOffset,lcpHpnScan,rcpHpnScan,
                    hpsOffset,lcpHpsScan,rcpHpsScan,
                    onOffset,lcpOnScan,rcpOnScan]
                scans=['HPN_OFFSET', 'HPN_LCP', 'HPN_RCP',
                   'HPS_OFFSET', 'HPS_LCP', 'HPS_RCP',
                   'ON_OFFSET', 'ON_LCP', 'ON_RCP']
                plt.figure(figsize=(20,10))
            
            cnt=1
            # print(cnt)
            # plt.title(f'Plot of {self.__dict__['FILENAME']}')
            # print(len(scans))
            
            if qv!='no':
                if frontend != '13.0S' and frontend != "18.0S":
                    for i in range(len(scans)):
                        # print(i)
                        
                        if i%3==0:
                            # print('--',i,i+1,i+2)
                            plt.subplot(3,2,cnt)
                            plt.ylabel('Ta [K]')
                            plt.xlabel('Offset [deg]')
                            plt.title(f'{scans[i+1]} - scan of {fileName}')
                            # plt.title(f'{scans[i+1]}')
                            plt.plot(dataScans[i],dataScans[i+1])
                            print(dataScans[i+1])

                            plt.subplot(3,2,cnt+1)
                            plt.ylabel('Ta [K]')
                            plt.xlabel('Offset [deg]')
                            # plt.title(f'{scans[i+2]}')
                            plt.title(f'{scans[i+2]} - scan of {fileName}')
                            plt.plot(dataScans[i],dataScans[i+2])
                            cnt=cnt+2
                        
                        # print('--',cnt)
                else:
                    cnt=1
                    for i in range(len(scans)):
                        if cnt<=2:
                            # print(i+1)
                            plt.subplot(1,2,cnt)
                            plt.ylabel('Ta [K]')
                            plt.xlabel('Offset [deg]')
                            plt.title(f'{scans[i+1]} - scan of {fileName}')
                            # plt.title(f'{scans[i+1]}')
                            plt.plot(dataScans[0],dataScans[i+1])
                            # print(dataScans[i+1])
                        cnt=cnt+1

                plt.tight_layout()
            if qv=='yes':
                plt.savefig(f'quickview_{src}_{int(frq)}-{fileName}.png')
                msg_wrapper("info",self.log.info,f'Quickview file saved to: quickview_{src}_{int(frq)}-{fileName}.png')
         
            else:
                pass
            # plt.show()
            plt.close()
            
        elif 'D' in frontend: 
            # '03.5D' or "06.0D"

            # Get driftscan data
            data=DriftScanData(self.__dict__)
            # for k,v in data.__dict__.items():
            #     # print('---',k,v)
            
            hpnOffset=self.getScanData('HPN_OFFSET') #self.__dict__['HPN_OFFSET']['value']
            lcpHpnScan=self.getScanData('HPN_TA_LCP') #self.__dict__['HPN_TA_LCP']['value']
            rcpHpnScan=self.getScanData('HPN_TA_RCP') #self.__dict__['HPN_TA_RCP']['value']

            hpsOffset=self.getScanData('HPS_OFFSET') #self.__dict__['HPS_OFFSET']['value']
            lcpHpsScan=self.getScanData('HPS_TA_LCP') #self.__dict__['HPS_TA_LCP']['value']
            rcpHpsScan=self.getScanData('HPS_TA_RCP') #self.__dict__['HPS_TA_RCP']['value']

            onOffset=self.getScanData('ON_OFFSET') #self.__dict__['ON_OFFSET']['value']
            lcpOnScan=self.getScanData('ON_TA_LCP') #self.__dict__['ON_TA_LCP']['value']
            rcpOnScan=self.getScanData('ON_TA_RCP') #self.__dict__['ON_TA_RCP']['value']

            dataScans=[hpnOffset,lcpHpnScan,rcpHpnScan,
                    hpsOffset,lcpHpsScan,rcpHpsScan,
                    onOffset,lcpOnScan,rcpOnScan]
            scans=['HPN_OFFSET', 'HPN_LCP', 'HPN_RCP',
                   'HPS_OFFSET', 'HPS_LCP', 'HPS_RCP',
                   'ON_OFFSET', 'ON_LCP', 'ON_RCP']
            
            cnt=1
            # print(cnt)
            plt.figure(figsize=(20,10))
            # plt.title(f'Plot of {self.__dict__['FILENAME']}')
            for i in range(len(scans)):
                # print(i)
                
                if i%3==0:
                    # print('--',i,i+1,i+2)
                    plt.subplot(3,2,cnt)
                    plt.ylabel('Ta [K]')
                    plt.xlabel('Offset [deg]')
                    plt.title(f'{scans[i+1]} - scan of {fileName}')
                    # plt.title(f'{scans[i+1]}')
                    plt.plot(dataScans[i],dataScans[i+1])
                    # print(dataScans[i+1])

                    plt.subplot(3,2,cnt+1)
                    plt.ylabel('Ta [K]')
                    plt.xlabel('Offset [deg]')
                    # plt.title(f'{scans[i+2]}')
                    plt.title(f'{scans[i+2]} - scan of {fileName}')
                    plt.plot(dataScans[i],dataScans[i+2])
                    cnt=cnt+2
                    
                    # print('--',cnt)

            if qv=='no':
                plt.close()
            else:
                plt.tight_layout()
                plt.savefig(f'quickview_{src}_{int(frq)}-{fileName}.png')
                # plt.show()
                plt.close()
                msg_wrapper("info",self.log.info,f'Quickview file saved to: quickview_{src}_{int(frq)}-{fileName}.png')
            
        else:
            print(f"Unknown source frontend value : {self.__dict__[frontend]['value']}. Contact author to have it included.")
            sys.exit()

