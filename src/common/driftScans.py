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

import matplotlib.pyplot as plt

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
                # print('+--+',f'{tag}{key}',key, tag, myDict[f'{tag}{key}'])

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
            'MIDOFFSET','BASELEFT','BASERIGHT','COORDSYS']
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
            
            # create tables for scans and database data structure
            scanData={} 
            tableData={} 

            if len(dataScans)==3:
                tag="ON"
                tags=[tag]
                x=dataScans[0]
                lcp=dataScans[1]
                rcp=dataScans[2]

                # process the data - i.e. run the fitting and plotting algorithms
                processedLCPData=DataProcessingFlowManager(fileName,frq,src,x,lcp,log,0,'y',saveTo,f'{tag}_LCP','LCP',frontend,hpbw,fnbw,theoFit, autoFit)
                processedRCPData=DataProcessingFlowManager(fileName,frq,src,x,rcp,log,0,'y',saveTo,f'{tag}_RCP','RCP',frontend,hpbw,fnbw,theoFit, autoFit)
                
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
                        self.fill_in_missing_data_sb(processedLCPData.__dict__,f'{tag[0]}L')
                        self.fill_in_missing_data_sb(processedRCPData.__dict__,f'{tag[0]}R')

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
                for tag in tags:

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
                                    or 'peakPts' in s or 'Res' in s or 'baseLocs' in s:
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
                                if k == 'fileName':
                                    tableData['OBSNAME']=v
                                    # print('<<',k,v)
                                # elif k.startswith(f'{tag[0]}{pol[0]}'.upper()): #'RMS' in k:
                                #     tableData[k]=v
                                #     print('>>',k,v)
                                else:
                                    # print('<<-',k,v)
                                    if tag=='HPS' or tag=='HPN':
                                        # print(f'=*= {k}'.upper(), f'{tag[-1]}{pol[0]}rms'.upper())
                                        if f'{tag[-1]}{pol[0]}rms'.upper() in k:
                                            tableData[f'{div}{k}'.upper()]=v
                                            # print(f'{tag[-1]}{pol[0]}rms'.upper())
                                    # else:
                                        
                                    # else:
                                    #     print(f'==={k}'.upper())
                                    #     if f'{tag[0]}{pol[0]}rms'.upper() in k:
                                    #         tableData[f'{div}{k}'.upper()]=v
                                    #         print(f'=== {div}{k}'.upper())
                                    # pass
                            # else: 
                            #     pass
                    # print()
            # fill in missing data
            # 

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
            #     print('* ',k,': ',v)
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

            print(f'Table: {dbTable}', freq)

            # Get data to save to dictionary
            # --- Setup database where you will be storing information
            msg_wrapper("debug",self.log.debug,"Setup database")
            db= SQLiteDB('HART26DATA.db',self.log)
            db.create_db()
            table=db.create_table(tableData,dbTable)
            db.populate_table(tableData, table)
            db.close_db()
            # sys.exit()
            # sys.exit()
   
        elif 'D' in frontend: 
            # '03.5D' or "06.0D"

            # Get driftscan data
            data=DriftScanData(self.__dict__)
            for k,v in data.__dict__.items():
                print('---',k,v)

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
                    print(myTag,f'A{myTag}',f'B{myTag}')
                    print(processedLCPData.__dict__.keys())
                    print(processedRCPData.__dict__.keys())
                    # sys.exit()
                    
                    self.fill_in_missing_data_db_common(processedLCPData.__dict__,myTag)
                    self.fill_in_missing_data_db_beams(processedLCPData.__dict__,f'A{myTag}')
                    self.fill_in_missing_data_db_beams(processedLCPData.__dict__,f'B{myTag}')
                    self.fill_in_missing_data_db_common(processedRCPData.__dict__,myTag)
                    self.fill_in_missing_data_db_beams(processedRCPData.__dict__,f'A{myTag}')
                    self.fill_in_missing_data_db_beams(processedRCPData.__dict__,f'B{myTag}')
                    
                    
                    scanData[tag]={'lcp':processedLCPData, 'rcp':processedRCPData}

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

            # for beam in beams:
            for pol in pols:
                for tag in tags:
                    # print('Working on:', tag,pol)
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
                                # print('---',s)
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
                                    # tg=tag
                                    div='' #divider = '_' or ""
                                    # print(tg,pol)
                                    
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
                                            # print(f'{tg}{pol[0]}{div}BRMS'.upper(),t)
                                            tableData[f'{tg}{pol[0]}{div}BRMS'.upper()]=t
                                    elif 'driftCoeffs' in s:
                                        # print(f'{tg}{pol[0]}{div}SLOPE'.upper(),t[0])

                                        # coeff=t #.split()
                                        try:
                                            if len(t)==0:
                                                tableData[f'{beams[0]}{tg}{pol[0]}{div}BASELocs'.upper()] = np.nan
                                            else:
                                                tableData[f'{tg}{pol[0]}{div}SLOPE'.upper()]=t[0]
                                        except:
                                            tableData[f'{tg}{pol[0]}{div}SLOPE'.upper()]=np.nan
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
                                            tableData[f'{beams[0]}{tg}{pol[0]}{div}BASELocs'.upper()] = ''
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
                                            # print(f'{tg}{pol[0]}{div}{s}'.upper(),t)

                        else:
                            if k == 'fileName':
                                tableData['OBSNAME']=v
                            else:
                                pass
                                # print('$$',k)     
            # print()
            # for k,v in tableData.items():
            #     print('*',k,v)
            # sys.exit()
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
                        pc,ta,taErr=calibrate(tableData[f'{beam}SRTA'], tableData[f'{beam}SRTAERR'], tableData[f'{beam}NRTA'], tableData[f'{beam}NRTAERR'], tableData[f'{beam}ORTA'], tableData[f'{beam}ORTAERR'], tableData, self.log)
                        tableData[f'{beam}ORPC']=pc
                        tableData[f'{beam}CORTA']=ta
                        tableData[f'{beam}CORTAERR']=taErr
                        break

            # Calibrate the data
            # for k,v in tableData.items():
            #     print('* ',k,': ',v)

            tableData['SRC']=tableData['OBJECT'].replace(' ','')
            freq=int(tableData['CENTFREQ'])
            dbTable = f"{tableData['SRC']}_{freq}"

            try:
                int(dbTable[0])
                dbTable=f"_{dbTable}"
            except:
                pass

            # print(f'Table: {dbTable}', freq)
            dbTable=set_table_name(dbTable, self.log)

            # Get data to save to dictionary
            # --- Setup database where you will be storing information
            msg_wrapper("debug",self.log.debug,"Setup database")
            db= SQLiteDB('HART26DATA.db',self.log)
            db.create_db()
            table=db.create_table(tableData,dbTable)
            db.populate_table(tableData, table)
            db.close_db()
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
            print(len(scans))
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
            else:
                pass
            # plt.show()
            plt.close()
            msg_wrapper("info",self.log.info,f'Quickview file saved to: quickview_{src}_{int(frq)}-{fileName}.png')
         
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

            plt.tight_layout()
            plt.savefig(f'quickview_{src}_{int(frq)}-{fileName}.png')
            # plt.show()
            plt.close()
            msg_wrapper("info",self.log.info,f'Quickview file saved to: quickview_{src}_{int(frq)}-{fileName}.png')
         
        else:
            print(f"Unknown source frontend value : {self.__dict__[frontend]['value']}. Contact author to have it included.")
            sys.exit()

