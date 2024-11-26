# column data to save
COMMONCOLS= {'FILENAME':'TEXT','FILEPATH':'TEXT','CURDATETIME':'TEXT','MJD':'REAL','OBSDATE':'TEXT','OBSTIME':'TEXT'}

dbCols={'FILENAME':'TEXT','FILEPATH':'TEXT','CURDATETIME':'TEXT','MJD':'REAL','OBSDATE':'TEXT','OBSTIME':'TEXT',
                  'OBSDATETIME':'TEXT','FRONTEND':'TEXT','HDULENGTH':'INTEGER','OBJECT':'TEXT','SRC':'TEXT','OBSERVER':'TEXT',
                  'OBSLOCAL':'TEXT','OBSNAME':'TEXT','PROJNAME':'TEXT','PROPOSAL':'TEXT','TELESCOP':'TEXT','UPGRADE':'TEXT',
                    'CENTFREQ':'REAL','BANDWDTH':'REAL','LOGFREQ':'REAL','BEAMTYPE':'TEXT','HPBW':'REAL','FNBW':'REAL','SNBW':'REAL',
                    'FEEDTYPE':'TEXT','LONGITUD':'REAL','LATITUDE':'REAL','COORDSYS':'REAL','EQUINOX':'REAL','RADECSYS':'TEXT',
                    'FOCUS':'REAL','TILT':'REAL','TAMBIENT':'REAL','PRESSURE':'REAL','HUMIDITY':'REAL','WINDSPD':'REAL','SCANDIR':'TEXT',
                    'POINTING':'INTEGER','BMOFFHA':'REAL','BMOFFDEC':'REAL','HABMSEP':'REAL',
                    'DICHROIC':'TEXT','PHASECAL':'TEXT','NOMTSYS':'REAL','SCANDIST':'REAL','SCANTIME':'REAL','INSTRUME':'TEXT',
                    'INSTFLAG':'TEXT','HZPERK1':'REAL','HZKERR1':'REAL','HZPERK2':'REAL','HZKERR2':'REAL',
                    'TCAL1':'REAL','TCAL2':'REAL','TSYS1':'REAL','TSYSERR1':'REAL','TSYS2':'REAL','TSYSERR2':'REAL','ELEVATION':'REAL',
                    'ZA':'REAL','HA':'REAL','PWV':'REAL','SVP':'REAL','AVP':'REAL','DPT':'REAL','WVD':'REAL','SEC_Z':'REAL','X_Z':'REAL',
                    'DRY_ATMOS_TRANSMISSION':'REAL','ZENITH_TAU_AT_1400M':'REAL','ABSORPTION_AT_ZENITH':'REAL',
                    
                    'ANLTA':'REAL','ANLTAERR':'REAL','ANLMIDOFFSET':'REAL','ANLS2N':'REAL', 
                    'BNLTA':'REAL','BNLTAERR':'REAL','BNLMIDOFFSET':'REAL','BNLS2N':'REAL',
                    'NLFLAG':'REAL','NLBRMS':'REAL','NLSLOPE':'REAL',
                    'ANLBASELOCS':'REAL','BNLBASELOCS':'REAL','NLRMSB':'REAL', 'NLRMSA':'REAL',
                    
                    'ASLTA':'REAL','ASLTAERR':'REAL','ASLMIDOFFSET':'REAL','ASLS2N':'REAL', 
                    'BSLTA':'REAL','BSLTAERR':'REAL','BSLMIDOFFSET':'REAL','BSLS2N':'REAL',
                    'SLFLAG':'REAL','SLBRMS':'REAL','SLSLOPE':'REAL','ASLBASELOCS':'REAL','BSLBASELOCS':'REAL', 'SLRMSB':'REAL', 'SLRMSA':'REAL',
                    
                    'AOLTA':'REAL','AOLTAERR':'REAL','AOLMIDOFFSET':'REAL','AOLS2N':'REAL',
                    'BOLTA':'REAL','BOLTAERR':'REAL','BOLMIDOFFSET':'REAL','BOLS2N':'REAL',
                    'OLFLAG':'REAL','OLBRMS':'REAL','OLSLOPE':'REAL','AOLBASELOCS':'REAL','BOLBASELOCS':'REAL', 'OLRMSB':'REAL', 'OLRMSA':'REAL',
                    'AOLPC':'REAL','ACOLTA':'REAL','ACOLTAERR':'REAL','BOLPC':'REAL','BCOLTA':'REAL','BCOLTAERR':'REAL',
                    
                    'ANRTA':'REAL','ANRTAERR':'REAL','ANRMIDOFFSET':'REAL','ANRS2N':'REAL',
                    'BNRTA':'REAL','BNRTAERR':'REAL','BNRMIDOFFSET':'REAL','BNRS2N':'REAL',
                    'NRFLAG':'REAL','NRBRMS':'REAL','NRSLOPE':'REAL','ANRBASELOCS':'REAL','BNRBASELOCS':'REAL','NRRMSB':'REAL', 'NRRMSA':'REAL',

                    'ASRTA':'REAL','ASRTAERR':'REAL','ASRMIDOFFSET':'REAL','ASRS2N':'REAL',
                    'BSRTA':'REAL','BSRTAERR':'REAL','BSRMIDOFFSET':'REAL','BSRS2N':'REAL',
                    'SRFLAG':'REAL','SRBRMS':'REAL','SRSLOPE':'REAL','ASRBASELOCS':'REAL','BSRBASELOCS':'REAL','SRRMSB':'REAL', 'SRRMSA':'REAL',

                    'AORTA':'REAL','AORTAERR':'REAL','AORMIDOFFSET':'REAL','AORS2N':'REAL',
                    'BORTA':'REAL','BORTAERR':'REAL','BORMIDOFFSET':'REAL','BORS2N':'REAL',
                    'ORFLAG':'REAL','ORBRMS':'REAL','ORSLOPE':'REAL','AORBASELOCS':'REAL','BORBASELOCS':'REAL','ORRMSB':'REAL', 'ORRMSA':'REAL',
                    'AORPC':'REAL','ACORTA':'REAL','ACORTAERR':'REAL','BORPC':'REAL','BCORTA':'REAL','BCORTAERR':'REAL'}

nbCols={'FILENAME':'TEXT','FILEPATH':'TEXT','CURDATETIME':'TEXT','MJD':'REAL','OBSDATE':'TEXT','OBSTIME':'TEXT',
                  'OBSDATETIME':'TEXT','FRONTEND':'TEXT','HDULENGTH':'INTEGER','OBJECT':'TEXT','SRC':'TEXT','OBSERVER':'TEXT',
                  'OBSLOCAL':'TEXT','OBSNAME':'TEXT','PROJNAME':'TEXT','PROPOSAL':'TEXT','TELESCOP':'TEXT','UPGRADE':'TEXT',
                    'CENTFREQ':'REAL','BANDWDTH':'REAL','LOGFREQ':'REAL','BEAMTYPE':'TEXT','HPBW':'REAL','FNBW':'REAL','SNBW':'REAL',
                    'FEEDTYPE':'TEXT','LONGITUD':'REAL','LATITUDE':'REAL','COORDSYS':'REAL','EQUINOX':'REAL','RADECSYS':'TEXT',
                    'FOCUS':'REAL','TILT':'REAL','TAMBIENT':'REAL','PRESSURE':'REAL','HUMIDITY':'REAL','WINDSPD':'REAL','SCANDIR':'TEXT',
                    'POINTING':'INTEGER','BMOFFHA':'REAL','BMOFFDEC':'REAL','HABMSEP':'REAL',
                    'DICHROIC':'TEXT','PHASECAL':'TEXT','NOMTSYS':'REAL','SCANDIST':'REAL','SCANTIME':'REAL','INSTRUME':'TEXT',
                    'INSTFLAG':'TEXT','HZPERK1':'REAL','HZKERR1':'REAL','HZPERK2':'REAL','HZKERR2':'REAL',
                    'TCAL1':'REAL','TCAL2':'REAL','TSYS1':'REAL','TSYSERR1':'REAL','TSYS2':'REAL','TSYSERR2':'REAL','ELEVATION':'REAL',
                    'ZA':'REAL','HA':'REAL','PWV':'REAL','SVP':'REAL','AVP':'REAL','DPT':'REAL','WVD':'REAL',

                    'MEAN_ATMOS_CORRECTION':'REAL','TAU10':'REAL','TAU15':'REAL','TBATMOS10':'REAL','TBATMOS15':'REAL',
                    
                    'NLTA':'REAL','NLTAERR':'REAL','NLMIDOFFSET':'REAL','NLS2N':'REAL', 
                    'NLFLAG':'REAL','NLBRMS':'REAL','NLSLOPE':'REAL',
                    'NLBASELEFT':'REAL','NLBASERIGHT':'REAL',
                    'NLRMSB':'REAL', 'NLRMSA':'REAL',
                    
                    'SLTA':'REAL','SLTAERR':'REAL','SLMIDOFFSET':'REAL','SLS2N':'REAL', 
                    'SLFLAG':'REAL','SLBRMS':'REAL','SLSLOPE':'REAL',
                    'SLBASELEFT':'REAL','SLBASERIGHT':'REAL',
                    'SLRMSB':'REAL', 'SLRMSA':'REAL',
                    
                    'OLTA':'REAL','OLTAERR':'REAL','OLMIDOFFSET':'REAL','OLS2N':'REAL',
                    'OLFLAG':'REAL','OLBRMS':'REAL','OLSLOPE':'REAL',
                    'OLBASELEFT':'REAL','OLBASERIGHT':'REAL',
                    'OLRMSB':'REAL', 'OLRMSA':'REAL',
                    'OLPC':'REAL','COLTA':'REAL','COLTAERR':'REAL',
                    
                    'NRTA':'REAL','NRTAERR':'REAL','NRMIDOFFSET':'REAL','NRS2N':'REAL',
                    'NRFLAG':'REAL','NRBRMS':'REAL','NRSLOPE':'REAL',
                    'NRBASELEFT':'REAL','NRBASERIGHT':'REAL',
                    'NRRMSB':'REAL', 'NRRMSA':'REAL',

                    'SRTA':'REAL','SRTAERR':'REAL','SRMIDOFFSET':'REAL','SRS2N':'REAL',
                    'SRFLAG':'REAL','SRBRMS':'REAL','SRSLOPE':'REAL',
                    'SRBASELEFT':'REAL','SRBASERIGHT':'REAL',
                    'SRRMSB':'REAL', 'SRRMSA':'REAL',

                    'ORTA':'REAL','ORTAERR':'REAL','ORMIDOFFSET':'REAL','ORS2N':'REAL',
                    'ORFLAG':'REAL','ORBRMS':'REAL','ORSLOPE':'REAL',
                    'ORBASELEFT':'REAL','ORBASERIGHT':'REAL',
                    'ORRMSB':'REAL', 'ORRMSA':'REAL',
                    'ORPC':'REAL','CORTA':'REAL','CORTAERR':'REAL'}

nbCols22jup={'FILENAME':'TEXT','FILEPATH':'TEXT','CURDATETIME':'TEXT','MJD':'REAL','OBSDATE':'TEXT','OBSTIME':'TEXT',
                  'OBSDATETIME':'TEXT','FRONTEND':'TEXT','HDULENGTH':'INTEGER','OBJECT':'TEXT','SRC':'TEXT','OBSERVER':'TEXT',
                  'OBSLOCAL':'TEXT','OBSNAME':'TEXT','PROJNAME':'TEXT','PROPOSAL':'TEXT','TELESCOP':'TEXT','UPGRADE':'TEXT',
                    'CENTFREQ':'REAL','BANDWDTH':'REAL','LOGFREQ':'REAL','BEAMTYPE':'TEXT','HPBW':'REAL','FNBW':'REAL','SNBW':'REAL',
                    'FEEDTYPE':'TEXT','LONGITUD':'REAL','LATITUDE':'REAL','COORDSYS':'REAL','EQUINOX':'REAL','RADECSYS':'TEXT',
                    'FOCUS':'REAL','TILT':'REAL','TAMBIENT':'REAL','PRESSURE':'REAL','HUMIDITY':'REAL','WINDSPD':'REAL','SCANDIR':'TEXT',
                    'POINTING':'INTEGER','BMOFFHA':'REAL','BMOFFDEC':'REAL','HABMSEP':'REAL',
                    'DICHROIC':'TEXT','PHASECAL':'TEXT','NOMTSYS':'REAL','SCANDIST':'REAL','SCANTIME':'REAL','INSTRUME':'TEXT',
                    'INSTFLAG':'TEXT','HZPERK1':'REAL','HZKERR1':'REAL','HZPERK2':'REAL','HZKERR2':'REAL',
                    'TCAL1':'REAL','TCAL2':'REAL','TSYS1':'REAL','TSYSERR1':'REAL','TSYS2':'REAL','TSYSERR2':'REAL','ELEVATION':'REAL',
                    'ZA':'REAL','HA':'REAL','PWV':'REAL','SVP':'REAL','AVP':'REAL','DPT':'REAL','WVD':'REAL',

                    'HPBW_ARCSEC':'REAL','ADOPTED_PLANET_TB':'REAL','PLANET_ANG_DIAM':'REAL','JUPITER_DIST_AU':'REAL',
                    'SYNCH_FLUX_DENSITY':'REAL','PLANET_ANG_EQ_RAD':'REAL','PLANET_SOLID_ANG':'REAL','THERMAL_PLANET_FLUX_D':'REAL',
                    'TOTAL_PLANET_FLUX_D':'REAL','TOTAL_PLANET_FLUX_D_WMAP':'REAL','SIZE_FACTOR_IN_BEAM':'REAL','SIZE_CORRECTION_FACTOR':'REAL',
                    'MEASURED_TCAL1':'REAL','MEASURED_TCAL2':'REAL','MEAS_TCAL1_CORR_FACTOR':'REAL','MEAS_TCAL2_CORR_FACTOR':'REAL',
                    'ATMOS_ABSORPTION_CORR':'REAL','ZA_RAD':'REAL','TAU221':'REAL','TAU2223':'REAL',
                    'TBATMOS221':'REAL','TBATMOS2223':'REAL',

                    'NLTA':'REAL','NLTAERR':'REAL','NLMIDOFFSET':'REAL','NLS2N':'REAL', 
                    'NLFLAG':'REAL','NLBRMS':'REAL','NLSLOPE':'REAL',
                    'NLBASELEFT':'REAL','NLBASERIGHT':'REAL',
                    'NLRMSB':'REAL', 'NLRMSA':'REAL',
                    
                    'SLTA':'REAL','SLTAERR':'REAL','SLMIDOFFSET':'REAL','SLS2N':'REAL', 
                    'SLFLAG':'REAL','SLBRMS':'REAL','SLSLOPE':'REAL',
                    'SLBASELEFT':'REAL','SLBASERIGHT':'REAL',
                    'SLRMSB':'REAL', 'SLRMSA':'REAL',
                    
                    'OLTA':'REAL','OLTAERR':'REAL','OLMIDOFFSET':'REAL','OLS2N':'REAL',
                    'OLFLAG':'REAL','OLBRMS':'REAL','OLSLOPE':'REAL',
                    'OLBASELEFT':'REAL','OLBASERIGHT':'REAL',
                    'OLRMSB':'REAL', 'OLRMSA':'REAL',
                    'OLPC':'REAL','COLTA':'REAL','COLTAERR':'REAL',
                    
                    'NRTA':'REAL','NRTAERR':'REAL','NRMIDOFFSET':'REAL','NRS2N':'REAL',
                    'NRFLAG':'REAL','NRBRMS':'REAL','NRSLOPE':'REAL',
                    'NRBASELEFT':'REAL','NRBASERIGHT':'REAL',
                    'NRRMSB':'REAL', 'NRRMSA':'REAL',

                    'SRTA':'REAL','SRTAERR':'REAL','SRMIDOFFSET':'REAL','SRS2N':'REAL',
                    'SRFLAG':'REAL','SRBRMS':'REAL','SRSLOPE':'REAL',
                    'SRBASELEFT':'REAL','SRBASERIGHT':'REAL',
                    'SRRMSB':'REAL', 'SRRMSA':'REAL',

                    'ORTA':'REAL','ORTAERR':'REAL','ORMIDOFFSET':'REAL','ORS2N':'REAL',
                    'ORFLAG':'REAL','ORBRMS':'REAL','ORSLOPE':'REAL',
                    'ORBASELEFT':'REAL','ORBASERIGHT':'REAL',
                    'ORRMSB':'REAL', 'ORRMSA':'REAL',
                    'ORPC':'REAL','CORTA':'REAL','CORTAERR':'REAL'}

nbCols22={'FILENAME':'TEXT','FILEPATH':'TEXT','CURDATETIME':'TEXT','MJD':'REAL','OBSDATE':'TEXT','OBSTIME':'TEXT',
                  'OBSDATETIME':'TEXT','FRONTEND':'TEXT','HDULENGTH':'INTEGER','OBJECT':'TEXT','SRC':'TEXT','OBSERVER':'TEXT',
                  'OBSLOCAL':'TEXT','OBSNAME':'TEXT','PROJNAME':'TEXT','PROPOSAL':'TEXT','TELESCOP':'TEXT','UPGRADE':'TEXT',
                    'CENTFREQ':'REAL','BANDWDTH':'REAL','LOGFREQ':'REAL','BEAMTYPE':'TEXT','HPBW':'REAL','FNBW':'REAL','SNBW':'REAL',
                    'FEEDTYPE':'TEXT','LONGITUD':'REAL','LATITUDE':'REAL','COORDSYS':'REAL','EQUINOX':'REAL','RADECSYS':'TEXT',
                    'FOCUS':'REAL','TILT':'REAL','TAMBIENT':'REAL','PRESSURE':'REAL','HUMIDITY':'REAL','WINDSPD':'REAL','SCANDIR':'TEXT',
                    'POINTING':'INTEGER','BMOFFHA':'REAL','BMOFFDEC':'REAL',
                    'DICHROIC':'TEXT','PHASECAL':'TEXT','NOMTSYS':'REAL','SCANDIST':'REAL','SCANTIME':'REAL','INSTRUME':'TEXT',
                    'INSTFLAG':'TEXT','HZPERK1':'REAL','HZKERR1':'REAL','HZPERK2':'REAL','HZKERR2':'REAL',
                    'TCAL1':'REAL','TCAL2':'REAL','TSYS1':'REAL','TSYSERR1':'REAL','TSYS2':'REAL','TSYSERR2':'REAL','ELEVATION':'REAL',
                    'ZA':'REAL','HA':'REAL','PWV':'REAL','SVP':'REAL','AVP':'REAL','DPT':'REAL','WVD':'REAL',

                    'TAU221':'REAL','TAU2223':'REAL',
                    'TBATMOS221':'REAL','TBATMOS2223':'REAL',

                    'NLTA':'REAL','NLTAERR':'REAL','NLMIDOFFSET':'REAL','NLS2N':'REAL', 
                    'NLFLAG':'REAL','NLBRMS':'REAL','NLSLOPE':'REAL',
                    'NLBASELEFT':'REAL','NLBASERIGHT':'REAL',
                    'NLRMSB':'REAL', 'NLRMSA':'REAL',
                    
                    'SLTA':'REAL','SLTAERR':'REAL','SLMIDOFFSET':'REAL','SLS2N':'REAL', 
                    'SLFLAG':'REAL','SLBRMS':'REAL','SLSLOPE':'REAL',
                    'SLBASELEFT':'REAL','SLBASERIGHT':'REAL',
                    'SLRMSB':'REAL', 'SLRMSA':'REAL',
                    
                    'OLTA':'REAL','OLTAERR':'REAL','OLMIDOFFSET':'REAL','OLS2N':'REAL',
                    'OLFLAG':'REAL','OLBRMS':'REAL','OLSLOPE':'REAL',
                    'OLBASELEFT':'REAL','OLBASERIGHT':'REAL',
                    'OLRMSB':'REAL', 'OLRMSA':'REAL',
                    'OLPC':'REAL','COLTA':'REAL','COLTAERR':'REAL',
                    
                    'NRTA':'REAL','NRTAERR':'REAL','NRMIDOFFSET':'REAL','NRS2N':'REAL',
                    'NRFLAG':'REAL','NRBRMS':'REAL','NRSLOPE':'REAL',
                    'NRBASELEFT':'REAL','NRBASERIGHT':'REAL',
                    'NRRMSB':'REAL', 'NRRMSA':'REAL',

                    'SRTA':'REAL','SRTAERR':'REAL','SRMIDOFFSET':'REAL','ASRS2N':'REAL',
                    'SRFLAG':'REAL','SRBRMS':'REAL','SRSLOPE':'REAL',
                    'SRBASELEFT':'REAL','SRBASERIGHT':'REAL',
                    'SRRMSB':'REAL', 'SRRMSA':'REAL',

                    'ORTA':'REAL','ORTAERR':'REAL','ORMIDOFFSET':'REAL','AORS2N':'REAL',
                    'ORFLAG':'REAL','ORBRMS':'REAL','ORSLOPE':'REAL',
                    'ORBASELEFT':'REAL','ORBASERIGHT':'REAL',
                    'ORRMSB':'REAL', 'ORRMSA':'REAL',
                    'ORPC':'REAL','CORTA':'REAL','CORTAERR':'REAL'}

sbCols={'FILENAME':'TEXT','FILEPATH':'TEXT','CURDATETIME':'TEXT','MJD':'REAL','OBSDATE':'TEXT','OBSTIME':'TEXT',
        'OBSDATETIME':'TEXT','FRONTEND':'TEXT','HDULENGTH':'INTEGER','OBJECT':'TEXT','SRC':'TEXT','OBSERVER':'TEXT',
        'OBSLOCAL':'TEXT','OBSNAME':'TEXT','PROJNAME':'TEXT','PROPOSAL':'TEXT','TELESCOP':'TEXT','UPGRADE':'TEXT',
        'CENTFREQ':'REAL','BANDWDTH':'REAL','LOGFREQ':'REAL','BEAMTYPE':'TEXT','HPBW':'REAL','FNBW':'REAL','SNBW':'REAL',
        'FEEDTYPE':'TEXT','LONGITUD':'REAL','LATITUDE':'REAL','COORDSYS':'REAL','EQUINOX':'REAL','RADECSYS':'TEXT',
        'FOCUS':'REAL','TILT':'REAL','TAMBIENT':'REAL','PRESSURE':'REAL',
        'HUMIDITY':'REAL','WINDSPD':'REAL','SCANDIR':'TEXT',
        'POINTING':'INTEGER','BMOFFHA':'REAL','BMOFFDEC':'REAL', 

        'DICHROIC':'TEXT','PHASECAL':'TEXT','NOMTSYS':'REAL','SCANDIST':'REAL','SCANTIME':'REAL','INSTRUME':'TEXT',
        'INSTFLAG':'TEXT','HZPERK1':'REAL','HZKERR1':'REAL','HZPERK2':'REAL','HZKERR2':'REAL',
        'TCAL1':'REAL','TCAL2':'REAL','TSYS1':'REAL','TSYSERR1':'REAL','TSYS2':'REAL','TSYSERR2':'REAL','ELEVATION':'REAL',
        'ZA':'REAL','HA':'REAL', 'ATMOSABS':'REAL',
                    
        'PWV':'REAL', 'SVP':'REAL','AVP':'REAL','DPT':'REAL','WVD':'REAL',
                    
        'OLTA':'REAL','OLTAERR':'REAL','OLMIDOFFSET':'REAL','OLS2N':'REAL',
        'OLFLAG':'REAL','OLBRMS':'REAL','OLSLOPE':'REAL',
        'OLBASELEFT':'REAL','OLBASERIGHT':'REAL',
        'OLRMSB':'REAL','OLRMSA':'REAL',
        
        'ORTA':'REAL','ORTAERR':'REAL','ORMIDOFFSET':'REAL','ORS2N':'REAL',
        'ORFLAG':'REAL','ORBRMS':'REAL','ORSLOPE':'REAL',
        'ORBASELEFT':'REAL','ORBASERIGHT':'REAL',
        'ORRMSB':'REAL','ORRMSA':'REAL'}
      