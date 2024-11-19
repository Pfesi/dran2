# ============================================================================#
# File: driftScanData.py                                                      #
# Author: Pfesesani V. van Zyl                                                #
# ============================================================================#

# Standard library imports
# --------------------------------------------------------------------------- #
import numpy as np
import sys
import math
import matplotlib.pylab as plt
from datetime import datetime


from dataclasses import dataclass, field
from .miscellaneousFunctions import set_dict_item, calc_log_freq
from .contextManagers import open_file
from .msgConfiguration import msg_wrapper
from .getResources import get_jpl_results
from .exceptions import FileResourceNotFoundError, ValueOutOfRangeException 
# =========================================================================== #
# import logging
# logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

@dataclass
class DriftScanData(object):
    """
        Class of parameters to be collected/saved to a database from the drift 
        scan fits file. These are the values that will be populated in the 
        CALDB or TARDB databases.

        Args:
            parameters (dict): dictionary of all properties to be stored.
    """
    
    __dict__: object

    def __post_init__(self):

        # print(self.__dict__['CARDS'])
        msg_wrapper("debug", self.log.debug, "Get data from driftscans")
        
        lenhdu=int(self.__dict__['HDULENGTH']['value'])

        self.get_missing_params()

        # print(lenhdu)
        # sys.exit()

        # print(self.__dict__)
        # sys.exit()

        if(int(lenhdu)>5):
            self.get_chart_header_data(lenhdu-1)

        for k,v in self.__dict__['CARDS'].items():
            msg_wrapper("debug", self.log.debug, f'Getting driftscans from, {k}: {v}')
            # print(k,": ",v)
            frontend='FRONTEND'
                 
            if v.endswith('_HPNZ'):
                msg_wrapper("debug", self.log.debug, "Getting driftscans from HPN header")
                self.get_driftscans(k,'HPN')

            elif v.endswith('_ZC'):
                msg_wrapper("debug", self.log.debug, "Getting driftscans from ON/Center header")
                self.get_driftscans(k,'ON')

            elif v.endswith('_HPSZ'):
                msg_wrapper("debug", self.log.debug, "Getting driftscans from HPS header")
                self.get_driftscans(k,'HPS')

        # print(self.__dict__)
        # sys.exit()
        msg_wrapper("debug", self.log.debug, "Calculate the derived parameters")
        self._calc_water_vapour()

        msg_wrapper("debug", self.log.debug, "Calibrate the atmosphere parameters")
        self._calc_atmospheric_penetration()

    def get_missing_params(self):
        # set missing parameters from primary header
        
        LOGFREQ=calc_log_freq(self.__dict__['CENTFREQ']['value'])
        set_dict_item(self.__dict__,'LOGFREQ',LOGFREQ,'The log of the frequency: log(CENTFREQ)')
        self.log_multiple_entries('LOGFREQ')

    def get_frontend_header_data(self,index):
        # set missing parameters from frontend header
        pass

    def get_calibration_header_data(self,index):
        # set missing parameters from calibration header
        pass
      
    def log_multiple_entries(self,*args):
        for arg in args:
            msg_wrapper("debug",self.log.debug,f"{arg}: {str(self.__dict__[f'{arg}'])}")

    def get_driftscans(self,index,tag):
        """Get the driftscan data"""

        msg_wrapper("debug", self.log.debug, f'Processing {tag} header')

        with open_file(self.__dict__['FILEPATH']['value']) as g:
            data=g[int(index)]
            LCPDATA = data.data.field('Count1')
            RCPDATA = data.data.field('Count2')
            RA = data.data.field('RA_J2000')
            MJD = data.data.field('MJD')

            LENMJD=len(MJD) # length of MJD

            if 'ON' in tag:
                HA = data.data.field('Hour_Angle')
                ELEVATION = data.data.field('Elevation')

                # find centre point of the data
                MID = int(LENMJD/2)

                # get Julian date, elevation, ha and Zenith from center of center/on source scan
                MJD = MJD[MID]
                HA = HA[MID] # corrected with help from Jon/Marisa
                ELEVATION = ELEVATION[MID]
                ZA = 90.0 - ELEVATION

                # self.__dict__[column] = {'value':hdu[column],'description':hdu.comments[column]}
                set_dict_item(self.__dict__,f'ELEVATION',ELEVATION,'Source Elevation (deg) on CENTER scan')
                set_dict_item(self.__dict__,f'ZA',ZA,f'Zenith angle (deg) on CENTER scan')
                set_dict_item(self.__dict__,f'MJD',MJD,f'Modified julian date on CENTER scan')
                set_dict_item(self.__dict__,f'HA',HA,f'Hour angle (deg) on CENTER scan')
                self.log_multiple_entries('ELEVATION','ZA','MJD','HA')

            # Get OFFSET data
            scandist=self.__dict__['SCANDIST']['value']

            OFFSET=np.linspace(-scandist/2.0, scandist/2.0, LENMJD)
            set_dict_item(self.__dict__,f'{tag}_OFFSET',OFFSET,f'Offset of Scandist (deg) in {tag} header')
            set_dict_item(self.__dict__,f'{tag}_RA_J2000',RA,f'Right ascension (deg) in {tag} header')

            # # Get driftscan data
            set_dict_item(self.__dict__,f'RAW_{tag}_LCPDATA',LCPDATA,f'Raw LCP counts (deg) in {tag} header')
            set_dict_item(self.__dict__,f'RAW_{tag}_RCPDATA',RCPDATA,f'Raw RCP counts (deg) in {tag} header')

            testArray=data.data.field('Hour_Angle')
            testArray[:]=np.nan
            # print('empty:',(testArray))
            # # Convert data to antenna temperature
            try:
                TA_LCP=(LCPDATA-LCPDATA[0])/self.__dict__['HZPERK1']['value']
                set_dict_item(self.__dict__,f'{tag}_TA_LCP',TA_LCP,f'LCP scan in antenna temp (K) in {tag} header')
            except:
                msg_wrapper("info", self.log.info, 'Missing HZPERK1')
                set_dict_item(self.__dict__,'HZPERK1',testArray,'[Hz/K] Counter calibration')
                set_dict_item(self.__dict__,f'{tag}_TA_LCP',testArray,f'LCP scan in antenna temp (K) in {tag} header')

            try:
                TA_RCP=(RCPDATA-RCPDATA[0])/self.__dict__['HZPERK2']['value']
                set_dict_item(self.__dict__,f'{tag}_TA_RCP',TA_RCP,f'RCP scan in antenna temp (K)  in {tag} header')
            except:
                msg_wrapper("info", self.log.info, 'Missing HZPERK2')
                set_dict_item(self.__dict__,'HZPERK2',testArray,'[Hz/K] Counter calibration')
                set_dict_item(self.__dict__,f'{tag}_TA_RCP',testArray,f'RCP scan in antenna temp (K)  in {tag} header')

    def get_chart_header_data(self,index):
        # set missing parameters from chart header
        pass

    def _calc_water_vapour(self)->None:
        """ Calculate water vapor parameters"""

        msg_wrapper("debug", self.log.debug, "Calculate the water vapour parameters")

        # ensure PWV and WVD do not go negative! 
        # calculate PWV values - copy from Mikes drift_fits2asc_HINDv16.c file
        try:
            hum=self.__dict__['HUMIDITY']['value']
        except:
            hum=np.nan
            self.__dict__['HUMIDITY']={'value':hum,'description':'humidity'}

        try:
            temp=self.__dict__['TAMBIENT']['value']
        except:
            temp=np.nan
            self.__dict__['TAMBIENT']={'value':temp,'description':'ambient temperature'}

        try:
            pwv = max(0.0, 4.39 * hum/100.0/temp * math.exp(26.23-5416/temp))
            svp = 0.611 * math.exp(17.27*(temp-273.13)/(temp-273.13+237.3))
            avp = svp * hum/100.0
            if avp <= 0:
                dpt = 0
            else:
                dpt= (116.9 + 237.3*math.log(avp)) / (16.78-math.log(avp)) 
            wvd = max(0.0, 2164.0*avp/temp)
        except:
            #! why are we setting these to 1? Find out
            pwv=1
            svp=1
            avp=1
            dpt=1
            wvd=1

        self.__dict__['PWV']={'value':pwv,'description':'# [mm] precip_water_vapour'}
        self.__dict__['SVP']={'value':svp,'description':'[kPa] sat_vap_pressure'}
        self.__dict__['AVP']={'value':avp,'description':'[kPa] amb_vap_pressure'}
        self.__dict__['DPT']={'value':dpt,'description':'[oC] dew_point_temp'}
        self.__dict__['WVD']={'value':wvd,'description':'[g/m^3] water_vapour_density'}
        self.log_multiple_entries('PWV','SVP','AVP','DPT','WVD','HUMIDITY','TAMBIENT')

    # def set_frequency_bands(self):
    #     """
    #     Set frequency band limits
    #     Frequency bands taken from https://www.everythingrf.com/tech-resources/frequency-bands
    
    #     """
        
    #     # if float(self.__dict__['CENTFREQ'])
    #     freqs=  {  'L':{'low':1000,'high':2000},
    #                'S':{'low':2000,'high':4000},
    #                'C':{'low':4000,'high':8000},
    #                'X':{'low':8000,'high':12000},
    #                'Ku':{'low':12000,'high':18000},
    #                'K':{'low':18000,'high':26500},
    #                'Ka':{'low':26500,'high':40000}
    #                } 
        
    #     for k,v in freqs.items():
    #         print(k,v)
    #     sys.exit()
        
    def _calc_atmospheric_penetration(self):
        """
            Calculate the atmospheric optical depth Tau and brightness temperature Tb at zenith.
        """
        frontend=self.__dict__['FRONTEND']['value']
        #! Double check these values are correct
        if frontend == "02.5S":
            msg_wrapper("debug",self.log.debug,"Calculate optical depth")
         
            set_dict_item(self.__dict__,'TAU10',np.nan,f'Optical depth at 10GHz')
            set_dict_item(self.__dict__,'TAU15',np.nan,f'Optical depth at 15GHz')
            set_dict_item(self.__dict__,'TBATMOS10',np.nan,f'Atmospheric temperature at 10GHz')
            set_dict_item(self.__dict__,'TBATMOS15',np.nan,f'Atmospheric temperature at 15GHz')
            set_dict_item(self.__dict__,'MEAN_ATMOS_CORRECTION',np.nan,f'mean atmospheric correction')
            

            try:
                self.__dict__['TAU10']['value'] = 0.0071 + 0.00021 * self.__dict__['PWV']['value']  
                self.__dict__['TAU15']['value'] = (0.055 + 0.004 * self.__dict__['WVD']['value'])/4.343
                self.__dict__['TBATMOS10']['value'] = 260 * (1.0 - math.exp(-self.__dict__['TAU10']['value']))  
                self.__dict__['TBATMOS15']['value'] = 260 * (1.0 - math.exp(-self.__dict__['TAU15']['value'])) 
            except:
                #! why are we setting these to 1? Find out
                self.__dict__['TAU10']['value'] = 1
                self.__dict__['TAU15']['value'] = 1
                self.__dict__['TBATMOS10']['value'] = 1
                self.__dict__['TBATMOS15']['value'] = 1

            try:
                meanatm= np.exp((self.__dict__['TAU15']['value'] + self.__dict__['TAU10']['value'])/2.0/np.cos(self.__dict__['ZA']['value']*np.pi/180.0))
            except:
                meanatm=0.0
            self.__dict__['MEAN_ATMOS_CORRECTION']['value']=meanatm
            self.log_multiple_entries('TAU10','TAU15','TBATMOS10','TBATMOS15','MEAN_ATMOS_CORRECTION')

        elif frontend == "01.3S":
            msg_wrapper("debug",self.log.debug,"Calculate optical depth")
            
            set_dict_item(self.__dict__,'TAU221',np.nan,f'Optical depth at 22.1 GHz')
            set_dict_item(self.__dict__,'TAU2223',np.nan,f'Optical depth at 22.23 GHz')
            set_dict_item(self.__dict__,'TBATMOS221',np.nan,f'Atmospheric temperature at 22.1 GHz')
            set_dict_item(self.__dict__,'TBATMOS2223',np.nan,f'Atmospheric temperature at 22.23 GHz')

            try:
                self.__dict__['TAU221']['value']  = 0.0140 + 0.00780 * self.__dict__['PWV']['value']   
                self.__dict__['TAU2223']['value']  = (0.110 + 0.048 * self.__dict__['WVD']['value'])/4.343 
                self.__dict__['TBATMOS221']['value']  = 260 * (1.0 - math.exp(-self.__dict__['TAU221']['value']))  
                self.__dict__['TBATMOS2223']['value']  = 260 * (1.0 - math.exp(-self.__dict__['TAU2223']['value'])) 
            except:
                #! why are we setting these to 1? Find out
                self.__dict__['TAU221']['value']  = 1
                self.__dict__['TAU2223']['value']  = 1
                self.__dict__['TBATMOS221']['value']  = 1
                self.__dict__['TBATMOS2223']['value']  = 1

            # self.log_multiple_entries('TAU221','TAU2223','TBATMOS221','TBATMOS2223')
            # set_dict_item(self.__dict__,'TAU221',np.nan,f'Optical depth at 22.1 GHz')
            if self.__dict__['OBJECT']['value'].upper()=='JUPITER':
                self.calibrate_jupiter_atm()

        elif '13.0S' in frontend or '18.0S' in frontend: # or '04.5S' in frontend:
            # calculate the atmospheric absorbtion
            msg_wrapper("debug",self.log.debug,"Calculate atmospheric absorption")

            try:
                atmabs = np.exp(0.005/np.cos(self.__dict__['ZA']['value']*0.017453293))
            except:
                atmabs=0.0
            self.__dict__['ATMOSABS']={'value':atmabs, 'description':'Atmospheric absorption'}
            self.log_multiple_entries('ATMOSABS')

        elif '04.5S' in frontend:
            # TODO: Fanie to help with this
            # Currently nothing in place for atmospheric calibration. Fanie to update post processing. (03/09/2024 calibration meeting 10:30am)

            pass

        elif 'D' in frontend:
            msg_wrapper("debug",self.log.debug,"Calculate zenith absorption")

            dtr = 0.01745329 #! TODO: where does this number come from??

            set_dict_item(self.__dict__,'SEC_Z',np.nan,'')
            set_dict_item(self.__dict__,'X_Z',np.nan,'')
            set_dict_item(self.__dict__,'DRY_ATMOS_TRANSMISSION',np.nan,'')
            set_dict_item(self.__dict__,'ZENITH_TAU_AT_1400M',np.nan,'z')
            set_dict_item(self.__dict__,'ABSORPTION_AT_ZENITH',np.nan,'')

            self.__dict__['SEC_Z']['value'] = 1.0 / np.cos(self.__dict__['ZA']['value']  * dtr)
            self.__dict__['X_Z']['value']  = -0.0045 + 1.00672 * self.__dict__['SEC_Z']['value']  - 0.002234 * \
            self.__dict__['SEC_Z']['value']  ** 2 - 0.0006247 * self.__dict__['SEC_Z']['value'] **3
            self.__dict__['DRY_ATMOS_TRANSMISSION']['value']  = 1.0/np.exp(0.0069*(1/np.sin((90-self.__dict__['ZA']['value'] )*dtr)-1))
            self.__dict__['ZENITH_TAU_AT_1400M']['value']  = 0.00610 + 0.00018 * self.__dict__['PWV']['value'] 
            self.__dict__['ABSORPTION_AT_ZENITH']['value']  = np.exp(self.__dict__['ZENITH_TAU_AT_1400M']['value']  * self.__dict__['X_Z']['value'] )
            self.log_multiple_entries('SEC_Z','X_Z','DRY_ATMOS_TRANSMISSION','ZENITH_TAU_AT_1400M','ABSORPTION_AT_ZENITH')
        else:
            print(f'atmospheric calibration Not implemented for {frontend}. Contact author')
            sys.exit()


    def calibrate_jupiter_atm(self):
        """
            Calibrate the Jupiter atmosphere.
        """
        msg_wrapper("debug",self.log.debug,"Calibrate Jupiter atmospheric data.")
       
        self.get_planet_ang_diam()
        self.get_jupiter_dist()

        set_dict_item(self.__dict__,'HPBW_ARCSEC',np.nan,'')
        set_dict_item(self.__dict__,'ADOPTED_PLANET_TB',np.nan,'')
        set_dict_item(self.__dict__,'SYNCH_FLUX_DENSITY',np.nan,'')
        set_dict_item(self.__dict__,'PLANET_ANG_EQ_RAD',np.nan,'')
        set_dict_item(self.__dict__,'PLANET_SOLID_ANG',np.nan,'')
        set_dict_item(self.__dict__,'THERMAL_PLANET_FLUX_D',np.nan,'')
        set_dict_item(self.__dict__,'SIZE_FACTOR_IN_BEAM',np.nan,'')
        set_dict_item(self.__dict__,'SIZE_CORRECTION_FACTOR',np.nan,'')
        set_dict_item(self.__dict__,'MEASURED_TCAL1',np.nan,'')
        set_dict_item(self.__dict__,'MEASURED_TCAL2',np.nan,'')
        set_dict_item(self.__dict__,'MEAS_TCAL1_CORR_FACTOR',np.nan,'')
        set_dict_item(self.__dict__,'MEAS_TCAL2_CORR_FACTOR',np.nan,'')
        set_dict_item(self.__dict__,'ZA_RAD',np.nan,'')

        set_dict_item(self.__dict__,'TOTAL_PLANET_FLUX_D',np.nan,'')
        set_dict_item(self.__dict__,'TOTAL_PLANET_FLUX_D_WMAP',np.nan,'')
        set_dict_item(self.__dict__,'ATMOS_ABSORPTION_CORR',np.nan,'')

        # TODO: Verify this number
        self.__dict__["HPBW_ARCSEC"]['value'] = 0.033*3600  # why 0.033 ?, self.data["HPBW"]*3600

        # TODO: VERIFY ADOPTED TB
        # from Jupiter Tb = 138.2 + 1.6 K = 139.8 K: Gibson, Welch, de Pater 2005, Icarus 173, 439;
        self.__dict__["ADOPTED_PLANET_TB"]['value']  = 136
        self.__dict__["SYNCH_FLUX_DENSITY"]['value']  = 1.6 * (4.04/self.__dict__["JUPITER_DIST_AU"]['value'])**2
        self.__dict__["PLANET_ANG_EQ_RAD"]['value']  = self.__dict__["PLANET_ANG_DIAM"]['value']/3600*math.pi/180./2.
        self.__dict__["PLANET_SOLID_ANG"]['value']  = math.pi*self.__dict__["PLANET_ANG_EQ_RAD"]['value']**2*0.935
        self.__dict__["THERMAL_PLANET_FLUX_D"]['value'] = 2*1380*self.__dict__["ADOPTED_PLANET_TB"]['value'] * \
            self.__dict__["PLANET_SOLID_ANG"]['value']/(300/self.__dict__["CENTFREQ"]['value'])**2
        self.__dict__["TOTAL_PLANET_FLUX_D"]['value'] = self.__dict__["SYNCH_FLUX_DENSITY"]['value'] + \
            self.__dict__["THERMAL_PLANET_FLUX_D"]['value']
    
        self.__dict__["TOTAL_PLANET_FLUX_D_WMAP"]['value'] = 2*1380*135.2 * \
            self.__dict__["PLANET_SOLID_ANG"]['value']/(300/self.__dict__["CENTFREQ"]['value'])**2
        self.__dict__["SIZE_FACTOR_IN_BEAM"]['value'] = self.__dict__["PLANET_ANG_DIAM"]['value'] / \
            2.*np.sqrt(0.935)/(0.6*self.__dict__["HPBW_ARCSEC"]['value'])
        self.__dict__["SIZE_CORRECTION_FACTOR"] = (self.__dict__["SIZE_FACTOR_IN_BEAM"]['value'])**2 / \
            (1-math.exp(-1*(self.__dict__["SIZE_FACTOR_IN_BEAM"]['value'])**2))

        # from ztcal (zenith temperature calibration - read mikes notes)
        self.__dict__["MEASURED_TCAL1"]['value'] = 71.4 # zenith measured value
        self.__dict__["MEASURED_TCAL2"]['value'] = 70.1 # check mikes notes

        
        if self.__dict__["TCAL1"]['value']==0:
            self.__dict__["MEAS_TCAL1_CORR_FACTOR"]['value'] = 0
        else:
            self.__dict__["MEAS_TCAL1_CORR_FACTOR"]['value'] = self.__dict__["MEASURED_TCAL1"]['value']/self.__dict__["TCAL1"]['value']


        if self.__dict__["TCAL2"]['value'] == None or self.__dict__["TCAL2"]['value'] == np.nan:
            self.__dict__["MEAS_TCAL2_CORR_FACTOR"]['value'] = np.nan
        else:
            # print('TCAL: ',self.data["TCAL2"])
            if self.__dict__["TCAL2"]['value']==0:
                self.__dict__["MEAS_TCAL2_CORR_FACTOR"]['value'] = 0.0 #self.__dict__["MEASURED_TCAL2"]/self.__dict__["TCAL2"]
            else:
                self.__dict__["MEAS_TCAL2_CORR_FACTOR"]['value'] = self.__dict__["MEASURED_TCAL2"]['value']/self.__dict__["TCAL2"]['value']

        self.__dict__["ZA_RAD"]['value'] = self.__dict__["ZA"]['value']*math.pi/180.
        self.__dict__["ATMOS_ABSORPTION_CORR"]['value'] = math.exp(
            self.__dict__["TAU221"]['value']/math.cos(self.__dict__["ZA_RAD"]['value']))
        
    def get_planet_ang_diam(self):
        """
            Get the planet angular diameter from horizon data
        """

        msg_wrapper("debug", self.log.debug,
                    'Get the planet angular diameter from horizon data.')

        # Get observation date and split it
        date=datetime.strptime(self.__dict__['OBSDATE']['value'], '%Y-%m-%d')
        date=date.strftime('%Y-%b-%d')

        # extract data from file
        try:
            jplResults=get_jpl_results()
        except FileResourceNotFoundError:
            msg_wrapper("error", self.log.error,
                        "\nFileResourceNotFoundError: The 'nasa_jpl_results.txt' resource is not in the distribution\n")
            sys.exit()

        # print(jplResults)
        # print(date)
        # sys.exit()
        set_dict_item(self.__dict__,"PLANET_ANG_DIAM",np.nan,f'Planet angular diameter')
        try:
            # date=mydate.strftime("%Y-%b-%d")
            ret = jplResults[jplResults['DATE']==str(date)]
            self.__dict__["PLANET_ANG_DIAM"]['value'] = ret["ANG-DIAM"].iloc[0] # unit of arcseconds, see nasa jpl horizons file
        except ValueOutOfRangeException:
            print(f"\nValueOutOfRangeException: The date {date} has not been accounted for, contact mantainer")
            sys.exit()

    def get_jupiter_dist(self):
        """
        Get Jupiter AU distance from NASA Planets Physical Parameters
        https://ssd.jpl.nasa.gov/planets/phys_par.html
        We use the mean radius because using the equatorial radius requires corrections.
        Ask Jon Quick again to explain.
        
        """

        import datetime

        msg_wrapper("debug", self.log.debug,
                    'Get Jupiter AU distance from calsky data or calculation')

        # convert 1 arcsec to radians
        rad=4.84814e-6# 1/206264 , 1 arcsecond = 4.84814e-6 rad

        # calculate jupiter distance in km
        theta=self.__dict__["PLANET_ANG_DIAM"]['value']*rad # in radians
        jupDiameter = 69911*2 # from nasa jpl horizons ephemeris data, i.e. mean radius times 2, Last Updated 24/04/2024 
        jupDistance = jupDiameter/theta

        # convert to AU
        au=1.45979e8 # km, from 1 au= 149597870.700 km
        JUPITER_DIST_AU = jupDistance/au # should be between ~ 4 and 6 AU
        set_dict_item(self.__dict__,"JUPITER_DIST_AU",np.nan,f'Distance to Jupiter in astronomical units')
        self.__dict__["JUPITER_DIST_AU"]['value']=JUPITER_DIST_AU
        self.log_multiple_entries('JUPITER_DIST_AU','PLANET_ANG_DIAM')
