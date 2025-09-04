# =========================================================================== #
# File: calibrate.py                                                          #
# Author: Pfesesani V. van Zyl                                                #
# =========================================================================== #

# Standard library imports
# --------------------------------------------------------------------------- #

#try:
from .miscellaneousFunctions import catch_zeroDivError
#except:
#    from common.miscellaneousFunctions import catch_zeroDivError

import numpy as np 
import sys
import pandas as pd
from datetime import datetime
from typing import List

# =========================================================================== #

def calc_pss(flux:float, Ta:float, errTa:float):
    """
        Calculate the Point source sensitivity (PSS)
        and its error for data with no pointing correction
        applied.

        Args:
            flux: the flux density of the source
            Ta: the antenna temperature
            errTa: the error in the antenna temperature

        Returns:
            pss: the point source sensitivity
            errPSS: the error in the point source sensitivity
            appEff: the apperture effeciency
    """

    # print(flux,Ta,errTa)
    flux=float(flux)
    Ta=float(Ta)
    errTa=float(errTa)

    try:
        pss = flux/2.0/Ta
        errPSS = np.sqrt(errTa**2/Ta**2)*pss
        appEff = 1380.0/np.pi/(25.9/2.0)**2/pss

    except ZeroDivisionError:
        pss = .0
        errPSS = .0
        appEff = .0

    return pss, errPSS, appEff

# Date parsing
# -------------------------------------------------------------------
def parse_time(timeCol: str) -> str:
    """
    """
    
    if 'T' in timeCol:
        return timeCol.split('T')[0]
    else:
        return timeCol.split(' ')[0]
    
def parse_observation_dates(df: pd.DataFrame,form='m') -> pd.DataFrame:
    """
    Parse the observation date column into a datetime format.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: The DataFrame with parsed dates.
    """
    
    df['time'] = df['OBSDATE'].astype(str)
    df['OBSDATE'] = df['time'].apply(parse_time)
    df['OBSDATE'] = pd.to_datetime(df['OBSDATE']).dt.date
    df['OBSDATE'] = pd.to_datetime(df['OBSDATE'], format=f"%Y-%{form}-%d")
    return df

# Data prepping
# -------------------------------------------------------------------
def prep_data(dataframe: pd.DataFrame, source_name: str) -> pd.DataFrame:
    """
    Preprocess the data in the DataFrame for analysis.

    Args:
        dataframe (pd.DataFrame): The input DataFrame containing observational data.
        source_name (str): The name of the source being processed.

    Returns:
        pd.DataFrame: The processed DataFrame.
    """

    # --- Remove all data from Marisa's gain observations
    dataframe=dataframe.loc[~dataframe.FILENAME.str.contains('marisa')]

    # --- Sort the DataFrame by filename
    dataframe.sort_values(by='FILENAME', inplace=True)

    # --- Parse observation dates
    dataframe = parse_observation_dates(dataframe)

    # --- Identify columns to convert to numeric (excluding metadata columns)
    exclude_keywords = [
            'FILE', 'FRONT', 'OBJ', 'SRC', 'OBS', 'PRO', 'TELE', 'HDU', 'id', 'DATE',
            'UPGR', 'TYPE', 'COOR', 'EQU', 'RADEC', 'SCAND', 'BMO', 'DICH', 'PHAS',
            'POINTI', 'TIME', 'INSTRU', 'INSTFL', 'time', 'HABM'
        ]
    dataframe = convert_to_numeric(dataframe, exclude_keywords)

    # Add source name to the DataFrame
    dataframe['FILES'] = dataframe['FILENAME'].str[:18]
    dataframe['OBJECT'] = source_name

    # Ensure all error columns have positive values
    dataframe = ensure_positive_errors(dataframe)
    return dataframe

def ensure_positive_errors(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure all error columns have positive values.

    Args:
        dataframe (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: The DataFrame with positive error values.
    """
    err_cols = df.filter(like='ERR').columns
    df[err_cols] = df[err_cols].map(make_positive)

    return df

def make_positive(value):
    """
    Ensure the input value is positive and convert it to a float. If the value is invalid or negative, return NaN.

    Args:
        value (Any): The input value to process.

    Returns:
        float: The positive float value or NaN if the value is invalid or negative.
    """
    # Check if the value is None or an empty string
    if value is None or value == '':
        return np.nan

    try:
        # Convert the value to a float
        numeric_value = float(value)
        # Return the value if it is non-negative, otherwise return NaN
        return numeric_value if numeric_value >= 0 else np.nan
    except (ValueError, TypeError):
        # Handle invalid values (e.g., non-numeric strings)
        return np.nan

def ensure_positive_errors_db(df):
    
    # Ensure all errors are +ve
    # ---------------------------
    err_cols = df.filter(like='ERR').columns
    df[err_cols] = df[err_cols].map(make_positive_db)


def make_positive_db(value):
#     """Ensures a value is positive."""
    if value=='None' or value==None:
        return np.nan
    else:
        return abs(value)
    
# Column conversions
# -------------------------------------------------------------------
def convert_to_numeric(dataframe: pd.DataFrame, exclude_keywords: List[str]) -> pd.DataFrame:
    """
    Convert columns to numeric, excluding those containing specific keywords.

    Args:
        dataframe (pd.DataFrame): The input DataFrame.
        exclude_keywords (List[str]): Keywords to exclude from numeric conversion.

    Returns:
        pd.DataFrame: The DataFrame with numeric columns.
    """

    colList=list(dataframe.columns)
    floatList = [col for col in colList if not any(excl in col for excl in exclude_keywords)]
    # --- Rather than fail, we might want 'pandas' to be considered a missing/bad numeric value. We can coerce invalid values to NaN as follows using the errors keyword argument:
    dataframe[floatList] = dataframe[floatList].apply(pd.to_numeric, errors='coerce')

    return dataframe

def calc_tcorr(Ta, pc, data):
    """
        Calculate the antenna temperature correction for high frequencies.

        Args:
            Ta - the on scan antenna temperature 
            pc - the pointing correction 
            data - the dictionary containing all the drift scan parameters

        Returns:
            corrTa - the corrected antenna temperature
    """

    # print(data['FRONTEND'],data['BEAMTYPE'],data['OBJECT'],pc)
    
    # print(data.columns)

    Ta= float(Ta)
    pc=float(pc)
    if data["FRONTEND"] == "01.3S":
        if data["OBJECT"].upper() == "JUPITER":
                # Only applying a size correction factor and atmospheric correction to Jupiter
                # See van Zyl (2023) - in Prep
                abs=float(data["ATMOS_ABSORPTION_CORR"])
                scf=float( data["SIZE_CORRECTION_FACTOR"])
                corrTa = Ta * pc * abs * scf
                # print(corrTa,data["ATMOS_ABSORPTION_CORR"] , data["SIZE_CORRECTION_FACTOR"],data["ATMOS_ABSORPTION_CORR"] * data["SIZE_CORRECTION_FACTOR"])
                # sys.exit()
                return corrTa
        else:
            # do we also apply a atmospheric correcttion factor directly to the target source ?
            # find out, for now I'm not applyin it
            # tests this ASAP
            corrTa = Ta * pc #* data["ATMOS_ABSORPTION_CORR"]
            return corrTa
    else:
        corrTa = Ta*pc
        return corrTa

def test_for_nans(Ta,errTa):
    """
        Test if data has nans
    
        Returns: 
            Ta : antenna temperature
            errTa: error in antenna temperature
    """

    if str(Ta) == "nan" or Ta is None or Ta==np.nan:
        Ta=0.0
        errTa=0.0
    else:
        pass

    try:
        Ta=float(Ta)
    except:
        Ta=np.nan

    try:
        errTa=float(errTa)
    except:
        errTa=np.nan

    return Ta, errTa 

def calc_pc_pss(hpsTa, errHpsTa, hpnTa, errHpnTa, onTa, errOnTa, flux,data):
        """
            Calculate the pss for pointing corrected observations.

            Args:
                scanNum: the index of the current scan, see plot_manager.py
                hpsTa: the half power south antenna temperature
                errHpsTa: the error in the half power south antenna temperature
                hpnTa: the half power north antenna temperature
                errHpnTa: the error in the half power north antenna temperature
                onTa: the on source antenna temperature
                errOnTa: the error in the on source antenna temperature
                flux: the source flux density
                data: the dictionary containing all the drift scan parameters

            Returns:
                pss: the point source sensitivity
                errPss: the error in the point source sensitivity
                appEff: the apperture effeciency
                corrTa: the corrected antenna temperature 
                errCorrTa: the error in the corrected antenna temperature
                appEff: the apperture effeciency
        """

        # Check if data has nans
        onTa, errOnTa = test_for_nans(onTa,errOnTa)
        hpsTa, errHpsTa = test_for_nans(hpsTa,errHpsTa)
        hpnTa, errHpnTa = test_for_nans(hpnTa,errHpnTa)
        
        onTa=float(onTa)
        errOnTa=float(errOnTa)
        hpsTa=float(hpsTa)
        errHpsTa=float(errHpsTa)
        hpnTa=float(hpnTa)
        errHpnTa=float(errHpnTa)

        if onTa != 0.0:

            #if no hpnTa
            if((hpnTa == 0) and (hpsTa != 0)):
                # missing north
                #pc = exp[((ln(hpsTa) - ln(Ton) + ln(2))**2)/4ln(2)]
                #corrTa = Ton x pc

                term2 = 4*np.log(2)
                # calculate the pointing and corrected antenna temp and its error
                pc, der1, der2 = calc_pc_eq(hpsTa, onTa,term2,'n')
                corrTa = calc_tcorr(onTa, pc, data)
                errCorrTa = np.sqrt((errOnTa**2)*(der2**2) + (errHpsTa**2)*(der1**2))

                # Calculate the PSS and appeture effeciency
                pss, errPSS, appEff=calc_pss(flux, corrTa, errCorrTa)

                #print("\n,errCorrTa: %.3f, corrTa: %.3f, PSS: %.3f, errPSS: %.3f\n" %
                #      (errCorrTa, corrTa, pss,errPss))

            #if no hpsTa
            elif((hpnTa != 0) and (hpsTa == 0)):
                # missing south
                # pc = exp[((ln(Ton) - ln(hpnTa) + ln(2))**2)/4ln(2)]
                # corrTa = Ton x pc

                term2 = 4*np.log(2)
                # calculate the pointing and corrected antenna temp and its error
                pc,der1, der2 = calc_pc_eq(onTa, hpnTa,term2,'s')
                corrTa = calc_tcorr(onTa, pc, data)
                errCorrTa = np.sqrt((errOnTa**2)*(der1**2) + (errHpnTa**2)*(der2**2))

                # Calculate the PSS and appeture effeciency
                pss, errPSS, appEff=calc_pss(flux, corrTa, errCorrTa)

                #print("\n,errCorrTa: %.3f, corrTa: %.3f, PSS: %.3f, errPSS: %.3f\n" %
                #      (errCorrTa, corrTa, pss, errPss))

            #if all present
            elif((hpnTa != 0) and (hpsTa != 0)):
                # pc = exp[((ln(hpsTa) - ln(hpnTa)**2)/16ln(2)]
                # corrTa = Ton x pc

                # calculate the pointing and corrected antenna temp and its error
                term2 = 16*np.log(2)
                pc, der1, der2 = calc_pc_eq(hpsTa, hpnTa, term2)
                corrTa = calc_tcorr( onTa, pc, data)
                errCorrTa = np.sqrt((errHpnTa**2)*(der2**2) + (errHpsTa**2)*(der1**2))

                # Calculate the PSS and appeture effeciency
                pss, errPSS, appEff=calc_pss(flux, corrTa, errCorrTa)

                #print("\nTcorerr: %.3f, corrTa: %.3f, PSS: %.3f, errPSS: %.3f\n" %
                #      (errCorrTa, corrTa, pss, errPss))
         
            #if no hpnTa/hpsTa
            if((hpnTa == 0) and (hpsTa == 0)):
                pss, errPSS, appEff = set_pss_to_zero()
                corrTa, errCorrTa, pc = set_corr_ta_to_zero()
                
        else:
            # if there's no on scan observation, everything defaults to zero
            pss, errPSS, appEff = set_pss_to_zero()
            corrTa, errCorrTa, pc = set_corr_ta_to_zero()

        return pss, errPSS, pc, corrTa, errCorrTa, appEff

def calibrate(hpsTa, errHpsTa, hpnTa, errHpnTa, onTa, errOnTa, data, log=''):
        """
            Calculate the pointing corrected antenna temperature.
    
            Parameters:
                hpsTa: the half power south antenna temperature
                errHpsTa: the error in the half power south antenna temperature
                hpnTa: the half power north antenna temperature
                errHpnTa: the error in the half power north antenna temperature
                onTa: the on source antenna temperature
                errOnTa: the error in the on source antenna temperature
                data: the dictionary containing all the drift scan parameters

            Returns:
                pc: the pointing correction
                corrTa: the corrected antenna temperature 
                errCorrTa: the error in the corrected antenna temperature
        """
        
        # Check if data has nans
        onTa, errOnTa = test_for_nans(onTa, errOnTa)
        hpsTa, errHpsTa = test_for_nans(hpsTa, errHpsTa)
        hpnTa, errHpnTa = test_for_nans(hpnTa, errHpnTa)

        onTa=float(onTa)
        errOnTa=float(errOnTa)
        hpsTa=float(hpsTa)
        errHpsTa=float(errHpsTa)
        hpnTa=float(hpnTa)
        errHpnTa=float(errHpnTa)

        if onTa != 0.0:

            #if no hpnTa
            if((hpnTa == 0) and (hpsTa != 0)):
                # missing north
                #pc = exp[((ln(hpsTa) - ln(Ton) + ln(2))**2)/4ln(2)]
                #corrTa = Ton x pc

                term2 = 4*np.log(2)
                # calculate the pointing and corrected antenna temp and its error
                pc, der1, der2 = calc_pc_eq(hpsTa, onTa,term2,'n')
                corrTa = calc_tcorr( onTa, pc, data)
                errCorrTa = np.sqrt((errOnTa**2)*(der2**2) + (errHpsTa**2)*(der1**2))

            #if no hpsTa
            elif((hpnTa != 0) and (hpsTa == 0)):
                # missing south
                # pc = exp[((ln(Ton) - ln(hpnTa) + ln(2))**2)/4ln(2)]
                # corrTa = Ton x pc

                term2 = 4*np.log(2)
                # calculate the pointing and corrected antenna temp and its error
                pc, der1, der2 = calc_pc_eq(onTa, hpnTa,term2,'s')
                corrTa = calc_tcorr(onTa, pc, data)
                errCorrTa = np.sqrt((errOnTa**2)*(der1**2) + (errHpnTa**2)*(der2**2))

            #if all present
            elif((hpnTa != 0) and (hpsTa != 0)):
                # pc = exp[((ln(hpsTa) - ln(hpnTa)**2)/16ln(2)]
                # corrTa = Ton x pc

                # calculate the pointing and corrected antenna temp and its error
                term2 = 16*np.log(2)
                pc, der1, der2 = calc_pc_eq(hpsTa, hpnTa, term2)
                corrTa = calc_tcorr( onTa, pc, data)
                errCorrTa = np.sqrt((errHpnTa**2)*(der2**2) +
                                  (errHpsTa**2)*(der1**2))

            #if no hpnTa/hpsTa
            if((hpnTa == 0) and (hpsTa == 0)):
                corrTa, errCorrTa, pc = set_corr_ta_to_zero()
        else:
            corrTa, errCorrTa, pc = set_corr_ta_to_zero()
            
        #print("\npc: {}, corrTa: {}, Tcorrerr: {}\n".format(pc, corrTa, errCorrTa))
        return pc, corrTa, errCorrTa

def calc_pc_eq(Ta1, Ta2, term2="",pol=''):

    """ Calculate the pointing correction and its derivatives.
    The pointing equations are given in the method 
    calc_pc_pss()
    
    Parameters:
        Ta1: first temperature
        Ta2: second temperature
        term2: the second term of the pointing correction equation as defined 
        in thesis/reference.  

    Returns:
        pc: the pointing correction
        der1: first derivative with respect to Ta1
        der2: first derivative with respect to Ta2
    """

    Ta1=float(Ta1)
    Ta2=float(Ta2)

    if term2=="":
        if pol=='n':
            # missing north
            term1 = (np.log(abs(Ta1)) - np.log(abs(Ta2)) + np.log(2))**2
        elif pol=='s':
            # missing south
            term1 = (np.log(abs(Ta1)) - np.log(abs(Ta2)) - np.log(2))**2
        term2 = 4*np.log(2)
    else:
        # print(Ta1,Ta2)
        term1 = (np.log(abs(Ta1)) - np.log(abs(Ta2)))**2
    term3 = term1/term2
    pc = np.exp(term3)

    # calculate the derivatives
    der1 = pc * 2.0 * term3 * (1.0/Ta1)
    der2 = pc * 2.0 * term3 * (-1.0/Ta2)

    return pc, der1, der2

def set_pss_to_zero():
    """ Set the estimation of the pss and apperture effeciency to zero """

    pss, errPss, appEff = .0, .0, .0
    return pss, errPss, appEff

def set_corr_ta_to_zero():
    """ Set the estimation of the corrected antenna temp to zero. """

    corrTa, corrTaErr, pc = .0, .0, .0
    return corrTa, corrTaErr, pc

def calc_flux(ta,dta,pss,dpss):
        """Calculate the flux density. """

        ta=float(ta)
        dta=float(dta)
        pss=float(pss)
        dpss=float(dpss)
        
        if float(ta) != np.nan and float(pss)!=np.nan:
#             print(ta,pss)
            flux=ta*pss
            lta=catch_zeroDivError(ta,dta)
            lps=catch_zeroDivError(pss,dpss)
            errta=(lta)**2
            errpss=(lps)**2
            dflux=flux*np.sqrt(errta+errpss)

        else:
            flux=np.nan
            dflux=np.nan
        return flux,dflux

def calc_totFlux(lcp,dlcp,rcp,drcp):
        ''' Calculate the total flux density of the source'''
        sumflux=np.nansum([lcp,rcp])
        n=(np.array([lcp,rcp])>0).sum() 
        fluxtot=(sumflux/n)*2
        dfluxtot=(2/n)*np.sqrt(dlcp**2+drcp**2)

        return fluxtot,dfluxtot

def calc_ta_and_ferrs_fast(df, pol, pos,beams=[]):
    """
    Faster TA + fractional error computation.
    - Drops prints and redundant loops
    - Replaces apply(axis=1) with list-comprehensions over NumPy arrays
    - Avoids temp DATA columns; assigns results directly

    Assumes:
      * len(pos) >= 3; uses the first three as (p0, p1, p2)
      * calibrate(...) -> (PC, CTA, CTAERR)
    """
    if len(pos) < 3:
        raise ValueError("pos must have at least 3 entries (e.g., ['N','S','R']).")

    p0, p1, p2 = pos[:3]

    # Materialize rows once as plain dicts (faster indexing inside calibrate than Series)
    rows = df.to_dict("records")

    for pol_code in pol:

        for b in beams:
            # Preload needed columns once per pol as NumPy arrays
            a_ta   = df[f'{b}{p0}{pol_code}TA'   ].to_numpy()
            a_err  = df[f'{b}{p0}{pol_code}TAERR'].to_numpy()
            b_ta   = df[f'{b}{p1}{pol_code}TA'   ].to_numpy()
            b_err  = df[f'{b}{p1}{pol_code}TAERR'].to_numpy()
            c_ta   = df[f'{b}{p2}{pol_code}TA'   ].to_numpy()
            c_err  = df[f'{b}{p2}{pol_code}TAERR'].to_numpy()

            print(f'{b}{p0}{pol_code}TA')

            # --- full/combined: use (a,aerr,b,berr,c,cerr)
            out_all = np.array([
                calibrate(at, ae, bt, be, ct, ce, r)
                for at, ae, bt, be, ct, ce, r in zip(a_ta, a_err, b_ta, b_err, c_ta, c_err, rows)
            ])
            # NOTE: original code used the last 's' from the loop for naming; that maps to p2 here.
            df[[f'{b}{p2}{pol_code}PC', f'{b}C{p2}{pol_code}TA', f'{b}C{p2}{pol_code}TAERR']] = out_all

            # --- fractional errors (vectorized), one pass per (TA,TAERR) pair
            # for name_ta, name_err in (
            #     (f'{p0}{pol_code}TA', f'{p0}{pol_code}TAERR'),
            #     (f'{p1}{pol_code}TA', f'{p1}{pol_code}TAERR'),
            #     (f'{p2}{pol_code}TA', f'{p2}{pol_code}TAERR'),
            # ):
            #     with np.errstate(divide='ignore', invalid='ignore'):
            #         ferr = np.abs(df[name_err].to_numpy() / df[name_ta].to_numpy())
            #     df[f'{name_ta}FERR'] = ferr.astype(float)

        # These follow your original logic (kept as-is)
        # df['TSYS1FERR'] = (df['TSYSERR1'] / df['TSYS1']).astype(float)
        # df['TSYS2FERR'] = (df['TSYSERR1'] / df['TSYS2']).astype(float)

    return df

# GET FLUX
def get_fluxes_db(df,beams=['A','B']):
    # beams=
    pols=['L','R']
    for b in beams:
        for p in pols:
#             print(f'{b}{p}')
            df[f'{b}S{p}OUT']=df.apply(lambda rf: calc_flux(rf[f'{b}CO{p}TA'],rf[f'{b}CO{p}TAERR'],rf[f'{b}O{p}PSS'],rf[f'{b}O{p}PSSERR']),axis=1)
            df[[f'{b}S{p}CP', f'{b}S{p}CPERR']] = pd.DataFrame(df[f'{b}S{p}OUT'].tolist(), index=df.index)
            
    for r,c in df.iterrows():
        df['STOUT']=df.apply(lambda rf: calc_dualtotFlux2(rf['ASLCP'],rf['ASLCPERR'],rf['ASRCP'],rf['ASRCPERR'],rf['BSLCP'],rf['BSLCPERR'],rf['BSRCP'],rf['BSRCPERR']),axis=1)
        df[['STOT', 'STOTERR','n','s']] = pd.DataFrame(df[f'STOUT'].tolist(), index=df.index)
    return df

def get_fluxes_df(df,caldf):
    
    beams=['A','B']
    pos=['O']
    pols=['L','R']

    for b in beams:
        for p in pos:
            for l in pols:
    #             print(f'{b}{p}{l}PSS',f'{b}{p}{l}PSSERR')
                df[f'{b}{p}{l}PSS']=np.nan
                df[f'{b}{p}{l}PSSERR']=np.nan
                df[f'{b}S{l}CP']=np.nan
                df[f'{b}S{l}CPERR']=np.nan
#             print()

    indl=''
    indr=''
    indl2=''
    indr2=''

    for r,row in df.iterrows():
    #     print(r,row)
        idx=row['id']
        fn=row['FILENAME']
        obsdate=str(row['OBSDATE']).split(' ')[0]
        time=row['time']

    #     print(idx,fn)
        n={}
        n['idx']=idx
        updates={}
    #     n['fn']=fn

        for b in beams:
            for p in pos:
                for l in pols:

    #                 print(f'{b}{p}{l}TA')
                    ta=abs(row[f'{b}{p}{l}TA'])
                    taerr=row[f'{b}{p}{l}TAERR']
                    pss=row[f'{b}{p}{l}PSS']
                    psse=row[f'{b}{p}{l}PSSERR']

                    if str(ta)!='nan':
    #                     print(idx,fn,obsdate,ta,pss,psse)

                        d=caldf[caldf['start']<=obsdate]
                        # print('\nlen d: ',len(d))

                        if len(d)==0:
                            n[f'{b}{p}{l}TA']=np.nan
                            updates[f'{b}PSS_{l}CP']=np.nan
                            updates[f'{b}PSS_{l}CP_SE']=np.nan
                            updates[f'{b}S{l}CP']=np.nan
                            updates[f'{b}S{l}CPERR']=np.nan
                        else:
                            start=d['start'].iloc[-1]
                            end=d['end'].iloc[-1]

                            if obsdate >= start and obsdate <= end:
                                pss=d[f'{b}PSS_{l}CP'].iloc[-1]
                                psse=d[f'{b}PSS_{l}CP_SE'].iloc[-1]

                                n['start']=start
                                n['obs']=obsdate
                                n['end']=end
        #                         n['obs']=obsdate
        #                         print(f'start: {start}, obs: {obsdate}, end: {end}, ta: {ta:.3f}, {b}PSS_{l}CP: {pss:.3f} +- {psse:.3f}')
                                n[f'{b}{p}{l}TA']=f'{ta:.3f}'
        #                         updates[f'{b}{p}{l}TA']=f'{ta:.3f}'

                                f,fe=calc_flux(ta,taerr,pss,psse)
                                updates[f'{b}PSS_{l}CP']=float(f'{pss:f}')
                                updates[f'{b}PSS_{l}CP_SE']=float(f'{psse:f}')
                                updates[f'{b}S{l}CP']=float(f'{f:f}')
                                updates[f'{b}S{l}CPERR']=float(f'{fe:f}')

        #                         df = df.apply(lambda rw: update_vals(rw,fn,lpss,lpsse,'AOLPSS','AOLPSSERR'),axis=1)

                            else:
                                # use the preious PSS value, when reaching end of DF
                                pss=d[f'{b}PSS_{l}CP'].iloc[-1]
                                psse=d[f'{b}PSS_{l}CP_SE'].iloc[-1]
                                print(idx,fn,obsdate,ta,pss,psse, start,end)

                                n['start']=start
                                n['obs']=obsdate
                                n['end']=end

                                n[f'{b}{p}{l}TA']=f'{ta:.3f}'
                                f,fe=calc_flux(ta,taerr,pss,psse)
                                updates[f'{b}PSS_{l}CP']=float(f'{pss:f}')
                                updates[f'{b}PSS_{l}CP_SE']=float(f'{psse:f}')
                                updates[f'{b}S{l}CP']=float(f'{f:f}')
                                updates[f'{b}S{l}CPERR']=float(f'{fe:f}')

                                print('issue1')
                                # sys.exit()
                        
                    else:
                        n[f'{b}{p}{l}TA']=np.nan
                        updates[f'{b}PSS_{l}CP']=np.nan
                        updates[f'{b}PSS_{l}CP_SE']=np.nan
                        updates[f'{b}S{l}CP']=np.nan
                        updates[f'{b}S{l}CPERR']=np.nan

        stot,stoterr,n,s=calc_dualtotFlux2(updates['ASLCP'],updates['ASLCPERR'],
                                      updates['ASRCP'],updates['ASRCPERR'],
                                      updates['BSLCP'],updates['BSLCPERR'],
                                      updates['BSRCP'],updates['BSRCPERR'])
        updates['STOT']=float(stot)
        updates['STOTERR']=float(stoterr)

        for k,v in updates.items():
            df.loc[r,k] = v
        
    return df
  
def get_fluxes_db2(df, beams=('A','B')):
    """
    Vectorized flux computation.
    - Computes (CP, CPERR) for each beam/pol in one pass per pair.
    - Avoids temporary *OUT columns.
    - Computes STOT and STOTERR exactly once (the original loop recomputed them N times).
    - Leaves rows as NaN where required inputs are missing.
    """
    out = df.copy()
    pols = ('L','R')

    # Vectorize your scalar functions without rewriting them
    v_calc_flux = np.frompyfunc(calc_flux, 4, 2)          # returns (cp, cpe)
    v_tot_flux  = np.frompyfunc(calc_dualtotFlux2, 8, 4)  # returns (STOT, STOTERR, n, s)

    # --- Per beam/pol CP & CPERR ---
    for b in beams:
        for p in pols:
            ta   = out[f'{b}CO{p}TA'     ].to_numpy()
            tae  = out[f'{b}CO{p}TAERR'  ].to_numpy()
            pss  = out[f'{b}O{p}PSS'     ].to_numpy()
            psse = out[f'{b}O{p}PSSERR'  ].to_numpy()

            cp, cpe = v_calc_flux(ta, tae, pss, psse)  # elementwise calls to calc_flux
            # cp, cpe = calc_flux(ta, tae, pss, psse)  # returns float arrays
            # frompyfunc outputs dtype=object; cast to float
            out[f'{b}S{p}CP']    = np.asarray(cp, dtype='float64')
            out[f'{b}S{p}CPERR'] = np.asarray(cpe, dtype='float64')

    # --- Totals (computed ONCE) ---
    ASL, ASLe = out['ASLCP'   ].to_numpy(), out['ASLCPERR' ].to_numpy()
    ASR, ASRe = out['ASRCP'   ].to_numpy(), out['ASRCPERR' ].to_numpy()
    BSL, BSLe = out['BSLCP'   ].to_numpy(), out['BSLCPERR' ].to_numpy()
    BSR, BSRe = out['BSRCP'   ].to_numpy(), out['BSRCPERR' ].to_numpy()

    stot, stot_e, n, s = v_tot_flux(ASL, ASLe, ASR, ASRe, BSL, BSLe, BSR, BSRe)
    # stot, stot_e, n, s = calc_dualtotFlux2(ASL, ASLe, ASR, ASRe, BSL, BSLe, BSR, BSRe)

    out['STOT']     = np.asarray(stot,   dtype='float64')
    out['STOTERR']  = np.asarray(stot_e, dtype='float64')
    out['n']        = np.asarray(n,      dtype='float64')  # or int, depending on your function
    out['s']        = np.asarray(s,      dtype='float64')  # or int

    return out

def calc_dualtotFlux2(slcp, dslcp, srcp, dsrcp, bslcp, bdslcp, bsrcp, bdsrcp):
    """
    Vectorized total flux over 4 inputs (A-L, A-R, B-L, B-R):
      sumflux    = sum of |flux_i| over valid (finite & >0) channels
      sumfluxerr = sqrt( sum of err_i^2 )    (NaN errors treated as 0)
      n          = count of valid channels
      fluxtot    = (sumflux / n) * 2         (NaN if n == 0)
      dfluxtot   = (2 / n) * sumfluxerr      (NaN if n == 0)
    Returns: (fluxtot, dfluxtot, n, sumflux)
    """

    # Stack and absolute-value fluxes & errors
    f = np.abs(np.stack([slcp,  srcp,  bslcp,  bsrcp ], axis=0)).astype(float)
    e = np.abs(np.stack([dslcp, dsrcp, bdslcp, bdsrcp], axis=0)).astype(float)

    # Valid channel = finite and strictly > 0 (matches your (>0) test after abs)
    valid = np.isfinite(f) & (f > 0)

    # Sum of flux across valid channels (treat invalid as 0)
    sumflux = np.where(valid, f, 0.0).sum(axis=0)

    # Quadrature error: treat NaN errors as 0; (optionally mask by 'valid' if desired)
    var_sum = np.where(np.isfinite(e), e**2, 0.0).sum(axis=0)
    sumfluxerr = np.sqrt(var_sum)

    # Count of contributing channels
    n = valid.sum(axis=0)

    # Totals with safe division
    with np.errstate(divide='ignore', invalid='ignore'):
        fluxtot  = (sumflux / n) * 2.0
        dfluxtot = (2.0 / n) * sumfluxerr

    # If no valid channels, set NaN
    zero = (n == 0)
    if np.any(zero):
        fluxtot  = np.where(zero, np.nan, fluxtot)
        dfluxtot = np.where(zero, np.nan, dfluxtot)

    return fluxtot, dfluxtot, n, sumflux

def calc_flux(ta, dta, pss, dpss):
    """
    Vectorized flux and uncertainty:
      flux  = TA * PSS
      dflux = |flux| * sqrt( (dTA/TA)^2 + (dPSS/PSS)^2 ), with safe division.
    Accepts scalars or arrays; returns NumPy arrays (flux, dflux).
    """

    ta   = abs(np.asarray(ta,   dtype=float))
    dta  = abs(np.asarray(dta,  dtype=float))
    pss  = abs(np.asarray(pss,  dtype=float))
    dpss = abs(np.asarray(dpss, dtype=float))

    # Base flux
    flux = ta * pss

    # Safe relative errors (0 when denominator is 0)
    rel_ta  = np.where(ta  != 0.0, dta  / ta,  0.0)
    rel_pss = np.where(pss != 0.0, dpss / pss, 0.0)

    dflux = np.abs(flux) * np.sqrt(rel_ta**2 + rel_pss**2)

    # If TA or PSS is NaN, invalidate both outputs
    invalid = np.isnan(ta) | np.isnan(pss)
    if invalid.any():
        flux  = np.where(invalid, np.nan, flux)
        dflux = np.where(invalid, np.nan, dflux)

    return flux, dflux

def add_pss_db_fast2(df, caldf, pol, pos, beams):
    """
    Vectorized: map each OBSDATE to its calibration interval and assign PSS/PSSERR.
    - Uses merge_asof(start) + OBSDATE < end to choose the active calibration row.
    - Falls back to the most recent *positive* PSS before the interval if current is missing/nonpositive.
    - Only fills rows where the corresponding TA exists (matches your original behavior).

    Expects:
      df columns include: 'FILENAME', 'OBSDATE', 'id', and per-beam/pol TA columns like f'{b}CO{p}TA'.
      caldf columns include: 'start','end' and per-beam/pol PSS columns like f'{b}PSS_{p}CP' and f'{b}PSS_{p}CP_SE'.
    """

    # --- Normalize date types ---
    df = df.copy()
    df['OBSDATE'] = pd.to_datetime(df['OBSDATE']).dt.floor('D')

    cal = caldf.copy()
    cal['start'] = pd.to_datetime(cal['start']).dt.floor('D')
    cal['end']   = pd.to_datetime(cal['end']).dt.floor('D')
    cal = cal.sort_values('start', kind='mergesort').reset_index(drop=True)

    # --- Precompute per-beam/pol "previous valid (>0)" fallback in cal table ---
    # This lets us grab the most recent positive PSS when current interval's value is NaN or <= 0.
    prev_cols = []
    for b in beams:
        for p in pol:
            pss_col    = f'{b}PSS_{p}CP'
            pss_se_col = f'{b}PSS_{p}CP_SE'
            if pss_col in cal.columns:
                cal[f'__prev_{b}{p}_pss']    = cal[pss_col   ].where(cal[pss_col   ] > 0).ffill()
                prev_cols.append(f'__prev_{b}{p}_pss')
            if pss_se_col in cal.columns:
                cal[f'__prev_{b}{p}_psse']   = cal[pss_se_col].where(cal[pss_se_col] > 0).ffill()
                prev_cols.append(f'__prev_{b}{p}_psse')

    # --- Merge each observation onto the most recent calibration row by start ---
    order = df.index
    tmp = df[['OBSDATE']].sort_values('OBSDATE', kind='mergesort').copy()
    tmp['__row'] = tmp.index

    # Bring only columns we need from cal into the merge to keep it lean
    needed_cols = ['start', 'end']
    for b in beams:
        for p in pol:
            needed_cols += [c for c in (f'{b}PSS_{p}CP', f'{b}PSS_{p}CP_SE') if c in cal.columns]
    needed_cols = list(dict.fromkeys(needed_cols + prev_cols))  # de-dup while preserving order

    merged = pd.merge_asof(
        tmp, cal[needed_cols].sort_values('start', kind='mergesort'),
        left_on='OBSDATE', right_on='start', direction='backward'
    )

    # Keep rows whose OBSDATE falls before the interval end (i.e., start <= OBSDATE < end)
    valid_mask = merged['OBSDATE'].lt(merged['end'])
    merged = merged.set_index('__row').reindex(order)  # back to original order
    valid_mask = valid_mask.reindex(order).fillna(False)

    # --- Initialize output columns (once) ---
    init_cols = {}
    for b in beams:
        for p in pol:
            for s in pos:
                if s == 'O':
                    init_cols[f'{b}{s}{p}PSS']    = np.nan
                    init_cols[f'{b}{s}{p}PSSERR'] = np.nan
                else:
                    init_cols[f'{b}{s}{p}CP']     = np.nan
                    init_cols[f'{b}{s}{p}CPERR']  = np.nan
    for k, v in init_cols.items():
        if k not in df.columns:
            df[k] = v

    # --- Fill PSS for on-source positions where TA is present ---
    for b in beams:
        for p in pol:
            ta_col = f'{b}CO{p}TA'
            if ta_col not in df.columns:
                # If the TA column isn't present, skip quietly.
                continue

            # Only compute where we have TA and a valid calibration match
            fill_mask = df[ta_col].notna() & valid_mask

            pss_col    = f'{b}PSS_{p}CP'
            pss_se_col = f'{b}PSS_{p}CP_SE'

            # Pull current interval values
            cur_pss  = merged[pss_col]    if pss_col in merged.columns    else pd.Series(index=df.index, dtype='float64')
            cur_psse = merged[pss_se_col] if pss_se_col in merged.columns else pd.Series(index=df.index, dtype='float64')

            # Fallback to most recent *positive* value prior to this interval
            prev_pss  = merged.get(f'__prev_{b}{p}_pss',  pd.Series(index=df.index, dtype='float64'))
            prev_psse = merged.get(f'__prev_{b}{p}_psse', pd.Series(index=df.index, dtype='float64'))

            eff_pss  = np.where((cur_pss  > 0), cur_pss,  prev_pss)
            eff_psse = np.where((cur_psse > 0), cur_psse, prev_psse)

            # Assign to on-source PSS columns (abs like your helper did)
            df.loc[fill_mask, f'{b}O{p}PSS']    = np.abs(eff_pss[fill_mask])
            df.loc[fill_mask, f'{b}O{p}PSSERR'] = np.abs(eff_psse[fill_mask])

            # If/when you want CP computed directly from TA, uncomment and supply your calc:
            # df.loc[fill_mask, f'{b}S{p}CP'], df.loc[fill_mask, f'{b}S{p}CPERR'] = calc_flux(
            #     df.loc[fill_mask, ta_col], df.loc[fill_mask, f'{b}CO{p}TAERR'],
            #     df.loc[fill_mask, f'{b}O{p}PSS'], df.loc[fill_mask, f'{b}O{p}PSSERR']
            # )

    return df


def calc_dualtotFlux2(slcp,dslcp, srcp,dsrcp, bslcp,bdslcp, bsrcp,bdsrcp):
        ''' Calculate the total flux density of the source'''
        
        slcp,dslcp=abs(slcp),abs(dslcp)
        srcp,dsrcp=abs(srcp),abs(dsrcp)
        bslcp,bdslcp=abs(bslcp),abs(bdslcp)
        bsrcp,bdsrcp=abs(bsrcp),abs(bdsrcp)

        sumflux=np.nansum([slcp,srcp,bslcp,bsrcp])
        sumfluxerr=np.sqrt(np.nansum([dslcp**2,dsrcp**2,bdslcp**2,bdsrcp**2]))
        n=(np.array([slcp,srcp,bslcp,bsrcp])>0).sum() 
        fluxtot=(sumflux/n)*2
        dfluxtot=(2/n)*sumfluxerr#np.sqrt(dslcp**2+dsrcp**2+bdslcp**2+bdsrcp**2)

        return fluxtot,dfluxtot,n,sumflux

def calc_dualtotFlux(slcp,dslcp,srcp,dsrcp,bslcp,bdslcp,bsrcp,bdsrcp):
        ''' Calculate the total flux density of the source'''
        sumflux=np.nansum([slcp,srcp,bslcp,bsrcp])
        n=(np.array([slcp,srcp,bslcp,bsrcp])>0).sum() 
        fluxtot=(sumflux/n)*2
        dfluxtot=(2/n)*np.sqrt(dslcp**2+dsrcp**2+bdslcp**2+bdsrcp**2)

        return fluxtot,dfluxtot

def getpss(pssdf, date):
    """ Get the PSS of a given bin time-range.
    
        pssdf: dataframe containing the pss bins.
        date: the date used to estimate the required bin range in order to extract the PSS. """
    
    date=float(date)
    pss=np.nan
    dpss=np.nan
    
    for k in range(len(pssdf)):
        start = float(pssdf['MJD_START'].iloc[k])
        end   = float(pssdf['MJD_END'].iloc[k])

        if date>=start and date<=end:
            pss=pssdf['PSS'].iloc[k]
            dpss=pssdf['PSS_STDEV'].iloc[k]
            return pss,dpss
        else:
            pass
    return np.nan,np.nan

def get_calibrator_flux(data,calibrationPaper=''):
        """
            Calculate the source flux for the calibrator.
            Use the Ott and Baars system.
        """
        # baars = { 
        #     # Baars 1977 paper - J. W. M. Baars, R. Genzel, T. T. K. Pauliny-Toth,A. Witzel, 
        #     # 'The Absolute Spectrum of Cas A; An Accurate Flux Density Scale and a Set of 
        #     # Secondary Calibrators," Astronomy & Astrophysics, 61, 1977, pp. 99-106.
            
        #     "CYGNUSA"   : {'range_from': 2000,  'range_to': 31000, 'a': 7.161, 'b': -1.244, 'c':0     },
        #     "CYGNUS A"   : {'range_from': 2000,  'range_to': 31000, 'a': 7.161, 'b': -1.244, 'c':0     },
        #     "CYG A"   : {'range_from': 2000,  'range_to': 31000, 'a': 7.161, 'b': -1.244, 'c':0     },
        #     "3C405"   : {'range_from': 2000,  'range_to': 31000, 'a': 7.161, 'b': -1.244, 'c':0     }, # aka CYGNUS A

        #     "TAURUSA"   : {'range_from': 1000,  'range_to': 35000, 'a': 3.915, 'b': -0.299, 'c':0     },
        #     "TAURUS A"   : {'range_from': 1000,  'range_to': 35000, 'a': 3.915, 'b': -0.299, 'c':0     },
        #     "TAU A"   : {'range_from': 1000,  'range_to': 35000, 'a': 3.915, 'b': -0.299, 'c':0     },
        #     "3C144"   : {'range_from': 1000,  'range_to': 35000, 'a': 3.915, 'b': -0.299, 'c':0     }, # aka TAU A

        #     "VIRGOA"   : {'range_from': 400,   'range_to': 25000, 'a': 5.023, 'b': -0.856, 'c':0     },
        #     "VIRGO A"   : {'range_from': 400,   'range_to': 25000, 'a': 5.023, 'b': -0.856, 'c':0     },
        #     "VIR A"   : {'range_from': 400,   'range_to': 25000, 'a': 5.023, 'b': -0.856, 'c':0     },
        #     "3C274"   : {'range_from': 400,   'range_to': 25000, 'a': 5.023, 'b': -0.856, 'c':0     }, # aka virgo a

        #     "3C48"      : {'range_from': 405,   'range_to': 15000, 'a': 2.345, 'b':0.071,   'c':-0.138},
        #     "3C123"     : {'range_from': 405,   'range_to': 15000, 'a': 2.921, 'b': -0.002, 'c':-0.124},
        #     "3C161"     : {'range_from': 405,   'range_to': 10700, 'a': 1.633, 'b': 0.498,  'c':0.194 },

        #     "HYDRAA"   : {'range_from': 405,   'range_to': 10700, 'a': 4.497, 'b': -0.910, 'c':0     },
        #     "HYDRA A"   : {'range_from': 405,   'range_to': 10700, 'a': 4.497, 'b': -0.910, 'c':0     },
        #     "3C218"     : {'range_from': 405,   'range_to': 10700, 'a': 4.497, 'b': -0.910, 'c':0     }, #aka HYDRA A

        #     "3C286"     : {'range_from': 405,   'range_to': 15000, 'a': 1.480, 'b': 0.292,  'c':-0.124},

        #     "3C348"     : {'range_from': 405,   'range_to': 10700, 'a': 4.963, 'b': -1.052, 'c':0     },
        #     "HERCULES A"     : {'range_from': 405,   'range_to': 10700, 'a': 4.963, 'b': -1.052, 'c':0     }, #aka 3C348
        #     "HERCULESA"     : {'range_from': 405,   'range_to': 10700, 'a': 4.963, 'b': -1.052, 'c':0     }, #aka 3C348

        #     "3C353"     : {'range_from': 405,   'range_to': 10700, 'a': 2.944, 'b': -0.034, 'c':-0.109},
        #     'DR21'      : {'range_from': 7000,  'range_to': 31000, 'a': 1.81,  'b': -0.122, 'c':0     },
        #     "NGC7027"   : {'range_from': 10000, 'range_to': 31000, 'a': 1.32,  'b': -0.127, 'c':0     }
        # }
              
        ott = { 
            # OTT 1994 PAPER - M. Ott, A. Quirrenbach, T. P. Krichbaum, K. J. Standke, C. J. Schalinski, and C. A. Hummel,
            # An updated list of radio flux density calibrators, Astronomy & Astrophysics, 284, 1994, pp. 331-339.

                "3C48"    : {'range_from': 1408,  'range_to': 23780, 'a': 2.465, 'b': -0.004, 'c': -0.1251},
                "3C123"   : {'range_from': 1408,  'range_to': 23780, 'a': 2.525, 'b': 0.246, 'c': -0.1638},
                "3C147"   : {'range_from': 1408,  'range_to': 23780, 'a': 2.806, 'b': -0.140, 'c': -0.1031},
                "3C161"   : {'range_from': 1408,  'range_to': 10550, 'a': 1.250, 'b': 0.726, 'c': -0.2286},

                # Hydra A at 12GHz does not have a proper calibration flux, thus I will be adapting 
                # this to calibrate at 12500 MHz to include the 12 GHz observations at (12218 MHz)
                # True Flux limit 'range_to' is 10550. When we start using Ott, this should revert back.
                "HYDRAA"  : {'range_from': 1408,  'range_to': 12500, 'a': 4.729, 'b': -1.025, 'c':  0.0130}, 
                "HYDRA A" : {'range_from': 1408,  'range_to': 12500, 'a': 4.729, 'b': -1.025, 'c':  0.0130},
                "3C218"   : {'range_from': 1408,  'range_to': 12500, 'a': 4.729, 'b': -1.025, 'c':  0.0130}, #aka HYDRA A
                "0915-119"   : {'range_from': 1408,  'range_to': 12500, 'a': 4.729, 'b': -1.025, 'c':  0.0130}, #aka HYDRA A
                "0915-11"   : {'range_from': 1408,  'range_to': 12500, 'a': 4.729, 'b': -1.025, 'c':  0.0130}, #aka HYDRA A
                "J0918-1205"   : {'range_from': 1408,  'range_to': 12500, 'a': 4.729, 'b': -1.025, 'c':  0.0130}, #aka HYDRA A

                "3C227"   : {'range_from': 1408,  'range_to': 4750,  'a': 6.757, 'b': -2.801, 'c':  0.2969},
                "3C249.1" : {'range_from': 1408,  'range_to': 4750,  'a': 2.537, 'b': -0.565, 'c': -0.0404},

                "VIRGOA"  : {'range_from': 1408,  'range_to': 10550, 'a': 4.484, 'b': -0.603, 'c': -0.0280}, 
                "VIRGO A" : {'range_from': 1408,  'range_to': 10550, 'a': 4.484, 'b': -0.603, 'c': -0.0280}, 
                "VIR A"   : {'range_from': 1408,  'range_to': 10550, 'a': 4.484, 'b': -0.603, 'c': -0.0280}, 
                "3C274"   : {'range_from': 1408,  'range_to': 10550, 'a': 4.484, 'b': -0.603, 'c': -0.0280},  # AKA VIRGO A

                "3C286"   : {'range_from': 1408,  'range_to': 43200, 'a': 0.956, 'b': 0.584, 'c': -0.1644},
                "3C295"   : {'range_from': 1408,  'range_to': 32000, 'a': 1.490, 'b': 0.756, 'c': -0.2545},
                "3C309.1" : {'range_from': 1408,  'range_to': 32000, 'a': 2.617, 'b': -0.437, 'c': -0.0373},

                "3C348"   : {'range_from': 1408,  'range_to': 10550,  'a': 3.852, 'b': -0.361, 'c': -0.1053},
                "HERCULESA"   : {'range_from': 1408,  'range_to': 10550,  'a': 3.852, 'b': -0.361, 'c': -0.1053}, # AKA 3C348
                "HERCULES A"   : {'range_from': 1408,  'range_to': 10550,  'a': 3.852, 'b': -0.361, 'c': -0.1053},

                "3C353"   : {'range_from': 1408,  'range_to': 10550,  'a': 3.148, 'b': -0.157, 'c': -0.0911},

                "CYGNUSA" : {'range_from': 4750,  'range_to': 10550,  'a': 8.360, 'b': 1.565,  'c':0},
                "CYGNUS A": {'range_from': 4750,  'range_to': 10550,  'a': 8.360, 'b': 1.565,  'c':0},
                "CYG A"   : {'range_from': 4750,  'range_to': 10550,  'a': 8.360, 'b': 1.565,  'c':0},
                "3C405"   : {'range_from': 4750,  'range_to': 10550,  'a': 8.360, 'b': 1.565,  'c':0}, #AKA CYGNUS A

                "NGC7027" : {'range_from': 10550, 'range_to': 43200, 'a': 1.322, 'b': -0.134, 'c': 0}
                }
        
        # perley = { 
            # # PERLEY 2017 PAPER - R. A. Perley and B. J. Butler
            # # An accurate flux density scale from 50 MHz to 50 GHz, Astrophysical Journal Supplement Series, 230:7, 2017, (18pp)
            # # https://doi.org/10.3847/1538-4365/aa6df9

            #     "3C48"      : {'range_from': 50, 'range_to': 50000, 'a': 1.3253, 'b': -0.7553, 'c': -0.1914,  'd': 0.0498,  'e': 0,      'f':0},
            #     "3C123"     : {'range_from': 50, 'range_to': 50000, 'a': 1.8017, 'b': -0.7884, 'c': -0.1035,  'd': -0.0248, 'e': 0.0090, 'f':0},
            #     "PICTORA"   : {'range_from': 20, 'range_to': 4000,  'a': 1.9380, 'b': -0.7470, 'c':-0.0739,   'd':0,        'e':0,       'f':0},
            #     "PICTOR A"  : {'range_from': 20, 'range_to': 4000,  'a': 1.9380, 'b': -0.7470, 'c':-0.0739,   'd':0,        'e':0,       'f':0},

            #     "TAURUSA"   : {'range_from': 50, 'range_to': 4000,  'a': 2.9516, 'b': -0.2173, 'c':-0.0473,   'd':-0.0674,  'e':0,       'f':0},
            #     "TAURUS A"  : {'range_from': 50, 'range_to': 4000,  'a': 2.9516, 'b': -0.2173, 'c':-0.0473,   'd':-0.0674,  'e':0,       'f':0},
            #     "TAU A"     : {'range_from': 50, 'range_to': 4000,  'a': 2.9516, 'b': -0.2173, 'c':-0.0473,   'd':-0.0674,  'e':0,       'f':0},
            #     "3C144"     : {'range_from': 50, 'range_to': 4000,  'a': 2.9516, 'b': -0.2173, 'c':-0.0473,   'd':-0.0674,  'e':0,       'f':0}, # aka TAU A

            #     # Hydra A at 12GHz does not have a proper calibration flux, thus I will be adapting 
            #     # this to calibrate at 12500 MHz to include the 12 GHz observations at (12218 MHz)
            #     # True Flux limit 'range_to' is 11512, see page 3, Table 4
            #     "3C218"     : {'range_from': 50, 'range_to': 12000, 'a': 1.7795, 'b': -0.9176, 'c':-0.0843,   'd': -0.0139, 'e': 0.0295, 'f':0}, # aka HYDRA A
            #     "HYDRAA"    : {'range_from': 50, 'range_to': 12000, 'a': 1.7795, 'b': -0.9176, 'c':-0.0843,   'd': -0.0139, 'e': 0.0295, 'f':0},
            #     "HYDRA A"   : {'range_from': 50, 'range_to': 12000, 'a': 1.7795, 'b': -0.9176, 'c':-0.0843,   'd': -0.0139, 'e': 0.0295, 'f':0},

            #     "VIRGOA"    : {'range_from': 50, 'range_to': 3000,  'a': 2.4466, 'b': -0.8116, 'c':-0.0483,   'd': 0,       'e': 0,      'f':0}, 
            #     "VIRGO A"   : {'range_from': 50, 'range_to': 3000,  'a': 2.4466, 'b': -0.8116, 'c':-0.0483,   'd': 0,       'e': 0,      'f':0}, 
            #     "VIR A"     : {'range_from': 50, 'range_to': 3000,  'a': 2.4466, 'b': -0.8116, 'c':-0.0483,   'd': 0,       'e': 0,      'f':0}, 
            #     "3C286"     : {'range_from': 50, 'range_to': 50000, 'a': 1.2481, 'b': -0.4507, 'c':0.0357,    'd': 0,       'e': 0,      'f':0},

            #     "HERCULESA" : {'range_from': 20, 'range_to': 12000, 'a': 1.8298, 'b': -1.0247, 'c':-0.0951,   'd': 0,       'e': 0,      'f':0},
            #     "HERCULES A": {'range_from': 20, 'range_to': 12000, 'a': 1.8298, 'b': -1.0247, 'c':-0.0951,   'd': 0,       'e': 0,      'f':0},
            #     "3C348"     : {'range_from': 20, 'range_to': 12000, 'a': 1.8298, 'b': -1.0247, 'c':-0.0951,   'd': 0,       'e': 0,      'f':0}, # AKA HERCULES A

            #     "CYGNUSA"   : {'range_from': 50, 'range_to': 12000, 'a': 3.3498, 'b': -1.0022, 'c':-0.2246,   'd': 0.0227,  'e': 0.0425, 'f':0},
            #     "CYGNUS A"  : {'range_from': 50, 'range_to': 12000, 'a': 3.3498, 'b': -1.0022, 'c':-0.2246,   'd': 0.0227,  'e': 0.0425, 'f':0},
            #     "3C405"     : {'range_from': 50, 'range_to': 12000, 'a': 3.3498, 'b': -1.0022, 'c':-0.2246,   'd': 0.0227,  'e': 0.0425, 'f':0}, # AKA CYGNUS A

            #     "3C353"     : {'range_from': 20, 'range_to': 4000,  'a': 1.8627, 'b': -0.06938, 'c': -0.0998, 'd': -0.0732, 'e': 0,      'f':0},
            #     }
        
        #if cal!="":
            # if self.data['OBJECT'].upper() in perley.keys():
            #     if perley[self.data['OBJECT']]["range_from"] < self.data['CENTFREQ'] < perley[self.data['OBJECT']]["range_to"]:
            #         self.data['FLUX'] = (10**(perley[self.data['OBJECT']]["a"] +
            #                                   perley[self.data['OBJECT']]["b"]*self.data['LOGFREQ'] + 
            #                                   perley[self.data['OBJECT']]["c"]*(self.data['LOGFREQ'])**2 + 
            #                                   perley[self.data['OBJECT']]["d"]*(self.data['LOGFREQ'])**3 + 
            #                                   perley[self.data['OBJECT']]["e"]*(self.data['LOGFREQ'])**4 + 
            #                                   perley[self.data['OBJECT']]["f"]*(self.data['LOGFREQ'])**5 ))
                    
            # el

            # We are ignoring Perley for now, their calibration flux is 9 Jy,  Ott and Baars are ~27
        
        if data['OBJECT'].upper() in ott.keys():
                # print(data['OBJECT'], ott[data['OBJECT']]["range_from"], data['CENTFREQ'] , ott[data['OBJECT']]["range_to"])
                
                if float(ott[data['OBJECT']]["range_from"]) < float(data['CENTFREQ']) < float(ott[data['OBJECT']]["range_to"]):
                    # data['FLUX'] = (10**(ott[data['OBJECT']]["a"] + 
                    #                           ott[data['OBJECT']]["b"]*data['LOGFREQ'] + 
                    #                           ott[data['OBJECT']]["c"]*data['LOGFREQ']**2))
                    return (10**(ott[data['OBJECT']]["a"] + 
                                              ott[data['OBJECT']]["b"]*data['LOGFREQ'] + 
                                              ott[data['OBJECT']]["c"]*data['LOGFREQ']**2))
                    
                    # print(data['FLUX'])
                    # sys.exit()
        # elif data['OBJECT'].upper() in baars.keys():
        #             if baars[data['OBJECT']]["range_from"] < data['CENTFREQ'] < baars[data['OBJECT']]["range_to"]:
        #                 data['FLUX'] = (10**(baars[data['OBJECT']]["a"] + 
        #                                           baars[data['OBJECT']]["b"]*data['LOGFREQ'] + 
        #                                           baars[data['OBJECT']]["c"]*data['LOGFREQ']**2))
        else:
                print(f'{data["OBJECT"]} - does not have calibration flux density spectral parameters in Ott 1994 or Barrs 1977.')
                print('Contact author about this.')
                # data['FLUX']=0.0
                return 0.0
                # sys.exit()

def calc_ta_and_ferrs(df,pol,pos):
    print('\n> Calculating TA and FERRS')
    c=[]

    for p in pol:
        ta=[]
        for s in pos:
            print(f'{s}{p}TA',f'{s}{p}TAERR')
            ta.append(f'{s}{p}TA')
            ta.append(f'{s}{p}TAERR')

# #         if key=='s':
#         df[f'PC_{s}{p}DATAs'] = df.apply(lambda row: calibrate(0,0,row[ta[2]], row[ta[3]],row[ta[4]], row[ta[5]], row), axis=1)
#         df[[f'{s}{p}PCs',f'C{s}{p}TAs',f'C{s}{p}TAERRs']] = pd.DataFrame(df[f'PC_{s}{p}DATAs'].tolist(), index=df.index)  
            
# #         elif key=='n':
#         df[f'PC_{s}{p}DATAn'] = df.apply(lambda row: calibrate(row[ta[0]], row[ta[1]],0,0,row[ta[4]], row[ta[5]], row), axis=1)
#         df[[f'{s}{p}PCn',f'C{s}{p}TAn',f'C{s}{p}TAERRn']] = pd.DataFrame(df[f'PC_{s}{p}DATAn'].tolist(), index=df.index)  
# #         else:
        df[f'PC_{s}{p}DATA'] = df.apply(lambda row: calibrate(row[ta[0]], row[ta[1]],row[ta[2]], row[ta[3]],row[ta[4]], row[ta[5]], row), axis=1)
        df[[f'{s}{p}PC',f'C{s}{p}TA',f'C{s}{p}TAERR']] = pd.DataFrame(df[f'PC_{s}{p}DATA'].tolist(), index=df.index)  
#     return dfx

# #         # estimate fractional errors
        df[f'{ta[0]}FERR']=abs(df[ta[1]]/df[ta[0]]).astype(float)
        df[f'{ta[2]}FERR']=abs(df[ta[3]]/df[ta[2]]).astype(float)
        df[f'{ta[4]}FERR']=abs(df[ta[5]]/df[ta[4]]).astype(float)
        
    df['TSYS1FERR']=(df['TSYSERR1']/df['TSYS1']).astype(float)
    df['TSYS2FERR']=(df['TSYSERR1']/df['TSYS2']).astype(float) 


def calc_pss_and_ferrs(df, pol, pos):
    """
    Calculate PSS (Primary Spectral Standard) values and fractional errors for given polarizations and positions.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Input DataFrame containing observational data.
    pol : list
        List of polarizations (e.g., ['L', 'R']).
    pos : list
        List of positions (e.g., ['HPS', 'HPN', 'ON']).
    
    Returns:
    --------
    None (modifies the input DataFrame in-place).
    """
    
    for s in pol:
        ta = []
        for p in pos:
            ta.extend([f'{p}{s}TA', f'{p}{s}TAERR'])  # Collect TA and TAERR columns
        
        # Determine flux source (Jupiter or calibrator)
        if 'TOTAL_PLANET_FLUX_D' in df.columns:
            # Case: Jupiter (flux from 'TOTAL_PLANET_FLUX_D')
            df[f'PC_{p}{s}DATA'] = df.apply(
                lambda row: calc_pc_pss(
                    row[ta[0]], row[ta[1]], 
                    row[ta[2]], row[ta[3]], 
                    row[ta[4]], row[ta[5]], 
                    row['TOTAL_PLANET_FLUX_D'], row
                ), axis=1
            )
        else:
            # Case: Other calibrator (fetch flux dynamically)
            # get_calibrator_flux=(df[['CENTFREQ','OBJECT','LOGFREQ']].iloc[-1])

           
            df['FLUX'] = df.apply(lambda row: get_calibrator_flux(row), axis=1)
            # print(df['FLUX'])
            # sys.exit()
            df[f'PC_{p}{s}DATA'] = df.apply(
                lambda row: calc_pc_pss(
                    row[ta[0]], row[ta[1]], 
                    row[ta[2]], row[ta[3]], 
                    row[ta[4]], row[ta[5]], 
                    row['FLUX'], row
                ), axis=1
            )
        
        # Unpack results into DataFrame columns
        result_columns = [
            f'{p}{s}PSS', f'{p}{s}PSSERR', f'{p}{s}PC',
            f'C{p}{s}TA', f'C{p}{s}TAERR', f'{p}{s}APPEFF'
        ]
        df[result_columns] = pd.DataFrame(
            df[f'PC_{p}{s}DATA'].tolist(), 
            index=df.index
        )
        
        # Replace zeros with NaN for PSS
        df[f'{p}{s}PSS'] = df[f'{p}{s}PSS'].replace(0, np.nan)
        
        # Calculate fractional errors
        for i in range(0, len(ta), 2):
            ta_col, taerr_col = ta[i], ta[i+1]
            df[f'{ta_col}FERR'] = (df[taerr_col] / df[ta_col]).abs()
        
        df[f'{p}{s}PSSFERR'] = (df[f'{p}{s}PSSERR'] / df[f'{p}{s}PSS']).abs()
    
    # Calculate TSYS fractional errors
    df['TSYS1FERR'] = (df['TSYSERR1'] / df['TSYS1']).abs()
    df['TSYS2FERR'] = (df['TSYSERR2'] / df['TSYS2']).abs()  


def calc_ta_and_ferrs_db(df,pol,pos,beams):

    print('\n> Calculating TA and FERRS')
    c=[]

    for b in beams:
        for p in pol:
            ta=[]
            for s in pos:
                key=f'{b}{s}{p}'
#                 print(f'{b}{s}{p}TA',f'{s}{p}TAERR')
                ta.append(f'{key}TA')
                ta.append(f'{key}TAERR')
#             print()
            print(ta,'\n')

    #         if key=='s':
    #         df[f'PC_{key}DATAs'] = df.apply(lambda row: calibrate(0,0,row[ta[2]], row[ta[3]],row[ta[4]], row[ta[5]], row), axis=1)
    #         df[[f'{key}PCs',f'C{key}TAs',f'C{key}TAERRs']] = pd.DataFrame(df[f'PC_{key}DATAs'].tolist(), index=df.index)  

    # #         elif key=='n':
    #         df[f'PC_{key}DATAn'] = df.apply(lambda row: calibrate(row[ta[0]], row[ta[1]],0,0,row[ta[4]], row[ta[5]], row), axis=1)
    #         df[[f'{key}PCn',f'C{key}TAn',f'C{key}TAERRn']] = pd.DataFrame(df[f'PC_{key}DATAn'].tolist(), index=df.index)  
    #         else:
            df[f'PC_{key}DATA'] = df.apply(lambda row: calibrate(row[ta[0]], row[ta[1]],row[ta[2]], row[ta[3]],row[ta[4]], row[ta[5]], row), axis=1)
            df[[f'{key}PC',f'{b}C{key}TA',f'{b}C{key}TAERR']] = pd.DataFrame(df[f'PC_{key}DATA'].tolist(), index=df.index)  
    #     return dfx

    # #         # estimate fractional errors
        #     df[f'{ta[0]}FERR']=abs(df[ta[1]]/df[ta[0]]).astype(float)
        #     df[f'{ta[2]}FERR']=abs(df[ta[3]]/df[ta[2]]).astype(float)
        #     df[f'{ta[4]}FERR']=abs(df[ta[5]]/df[ta[4]]).astype(float)

        # df['TSYS1FERR']=(df['TSYSERR1']/df['TSYS1']).astype(float)
        # df['TSYS2FERR']=(df['TSYSERR1']/df['TSYS2']).astype(float)

def calc_pss_and_ferrs_db(df,pol,pos,beams):
    print('\n> Calculating PSS and FERRS')
    pssvals=[]
    c=[]

    df['FLUX']=''
    for r,c in df.iterrows():
        flux=get_calibrator_flux(c)

        df.at[r,'FLUX']=flux
        
    for b in beams:
        for p in pol:
            ta=[]
            for s in pos:
                key=f'{b}{s}{p}'
                # print(f'{p}{s}TA',f'{p}{s}TAERR')
                ta.append(f'{key}TA')
                ta.append(f'{key}TAERR')
                pssvals.append(f'{key}TA')
                pssvals.append(f'{key}TAERR')

            # print()
            # print(ta)
            df[f'PC_{key}DATA'] = df.apply(lambda row: calc_pc_pss(row[ta[0]], row[ta[1]],row[ta[2]], row[ta[3]],row[ta[4]], row[ta[5]], row['FLUX'], row), axis=1)
            df[[f'{key}PSS', f'{key}PSSERR',f'{key}PC',f'C{key}TA',f'C{key}TAERR',f'{key}APPEFF']] = pd.DataFrame(df[f'PC_{key}DATA'].tolist(), index=df.index)

            df[f'{key}PSS'] = df[f'{key}PSS'].replace(0, np.nan)

            if b=='B': 
                df[f'{key}PSS'] = -1*df[f'{key}PSS']

#             # estimate fractional errors
            df[f'{ta[0]}FERR']=abs(df[ta[1]]/df[ta[0]]).astype(float)
            df[f'{ta[2]}FERR']=abs(df[ta[3]]/df[ta[2]]).astype(float)
            df[f'{ta[4]}FERR']=abs(df[ta[5]]/df[ta[4]]).astype(float)

            # print(f'{p}{s}PSSFERR')
            df[f'{key}PSSFERR']=abs(df[f'{key}PSSERR']/df[f'{key}PSS']).astype(float)

        df['TSYS1FERR']=(df['TSYSERR1']/df['TSYS1']).astype(float)
        df['TSYS2FERR']=(df['TSYSERR1']/df['TSYS2']).astype(float) 


def add_pss(df, caldf):
    """
        Calculates and updates PSS (Polarized Source Strength) and related values in the input DataFrame.

        Args:
            df (pd.DataFrame): Input DataFrame containing observation data.  Must have columns:
                            'FILENAME', 'OBSDATE', 'time', 'OLTA', 'ORTA', 'id'.
            caldf (pd.DataFrame): Calibration DataFrame containing PSS values. Must have columns:
                                'start', 'end', 'PSS_LCP', 'PSS_LCP_STD', 'PSS_LCP_SE',
                                'PSS_RCP', 'PSS_RCP_STD', 'PSS_RCP_SE'.

        Returns:
            pd.DataFrame: Updated DataFrame with calculated PSS values.
    """

    BEAMS=['A','B']
    POSITIONS=['S','N','O'] # hps,hpn,on
    POLARIZATIONS = ['L', 'R'] 

    # Initialize new columns more efficiently
    for b in BEAMS:
        for p in POLARIZATIONS:
            for s in POSITIONS:
                if s=='O':
                    df[[f'{b}{s}{p}PSS',f'{b}{s}{p}PSSERR',f'{b}{s}{p}CP',f'{b}{s}{p}CPERR']]=np.nan
                else:
                    df[[f'{b}{s}{p}CP',f'{b}{s}{p}CPERR']]=np.nan

#     df[['OLPSS', 'OLPSSERR', 'ORPSS', 'ORPSSERR', 'SLCP', 'SLCPERR', 'SRCP', 'SRCPERR', 'STOT', 'STOTERR']] = np.nan

    for index, row in df.iterrows():  # Use iterrows for efficient row access
        for b in BEAMS:
            for p in POLARIZATIONS:
                fn = row['FILENAME']
                obsdate = str(row['OBSDATE']).split(' ')[0]
                ta = row[f'{b}CO{p}TA']
                tae = row[f'{b}CO{p}TAERR']
#                 orta = row[f'{b}CORTA']
#                 ortae = row[f'{b}CORTAERR']
                idx = row['id']

                # Process OLTA (Left Circular Polarization)
        #         print(obsdate)
                if pd.notna(ta):  # Use pd.notna for NaN check
                    pss, psse,g = _get_pss_values(caldf, obsdate, f'{b}PSS_{p}CP', f'{b}PSS_{p}CP_SE',f'{p}cp')
                    if pd.notna(pss):
                        df.loc[index, [f'{b}O{p}PSS', f'{b}O{p}PSSERR']] = pss, psse  # More efficient update

#                         df.loc[index, [f'{b}S{p}CP', f'{b}S{p}CPERR']] = calc_flux(ta,tae,pss, psse)#Calculate SLCP directly
#                 print(f'{b}O{p}PSS', f'{b}O{p}PSSERR',f'{b}S{p}CP', f'{b}S{p}CPERR')
 
    return df

def add_pss_db(df, caldf,pol,pos,beams):
    """
    Calculates and updates PSS (Polarized Source Strength) and related values in the input DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame containing observation data.  Must have columns:
                           'FILENAME', 'OBSDATE', 'time', 'OLTA', 'ORTA', 'id'.
        caldf (pd.DataFrame): Calibration DataFrame containing PSS values. Must have columns:
                            'start', 'end', 'PSS_LCP', 'PSS_LCP_STD', 'PSS_LCP_SE',
                            'PSS_RCP', 'PSS_RCP_STD', 'PSS_RCP_SE'.

    Returns:
        pd.DataFrame: Updated DataFrame with calculated PSS values.
    """

    # Initialize new columns more efficiently
    for b in beams:
        for p in pol:
            for s in pos:
                if s=='O':
                    df[[f'{b}{s}{p}PSS',f'{b}{s}{p}PSSERR',f'{b}{s}{p}CP',f'{b}{s}{p}CPERR']]=np.nan
                else:
                    df[[f'{b}{s}{p}CP',f'{b}{s}{p}CPERR']]=np.nan
#     df[['OLPSS', 'OLPSSERR', 'ORPSS', 'ORPSSERR', 'SLCP', 'SLCPERR', 'SRCP', 'SRCPERR', 'STOT', 'STOTERR']] = np.nan

    
    for index, row in df.iterrows():  # Use iterrows for efficient row access
        for b in beams:
            for p in pol:
                fn = row['FILENAME']
                obsdate = str(row['OBSDATE']).split(' ')[0]
                ta = row[f'{b}CO{p}TA']
                tae = row[f'{b}CO{p}TAERR']
#                 orta = row[f'{b}CORTA']
#                 ortae = row[f'{b}CORTAERR']
                idx = row['id']

                # Process OLTA (Left Circular Polarization)
        #         print(obsdate)
                if pd.notna(ta):  # Use pd.notna for NaN check
                    pss, psse,g = _get_pss_values(caldf, obsdate, f'{b}PSS_{p}CP', f'{b}PSS_{p}CP_SE',f'{p}cp')
                    if pd.notna(pss):
                        df.loc[index, [f'{b}O{p}PSS', f'{b}O{p}PSSERR']] = pss, psse  # More efficient update
#                         df.loc[index, [f'{b}S{p}CP', f'{b}S{p}CPERR']] = calc_flux(ta,tae,pss, psse)#Calculate SLCP directly
#                 print(f'{b}O{p}PSS', f'{b}O{p}PSSERR',f'{b}S{p}CP', f'{b}S{p}CPERR')
 
    return df



def _get_pss_values(caldf, obsdate, pss_col, pss_err_col, pol):

    """Helper function to find and return PSS values from calibration DataFrame."""
    for _, c2 in caldf.iterrows():
        # print(c2)
        
        start = c2['start']
        end = c2['end']

#       print(start,end)
        if obsdate >= start and obsdate < end:
            lpss = c2[pss_col]
            lpsse = c2[pss_err_col]

#           print(start,obsdate,end,lpss,lpsse,pol)
            if pd.notna(lpss):
                return abs(lpss), abs(lpsse), np.nan  # Return values directly
            
            else:
                # Handle missing PSS, try previous value (if needed)
                lpss, lpsse,ind= _get_previous_pss(caldf, start, pss_col, pss_err_col) # removed unused index
                return lpss, lpsse, ind
            
    return np.nan, np.nan, np.nan # Return None if no suitable PSS is found

def _get_previous_pss(mydf,latest_date,col,colerr):
    x=mydf[mydf[col]>0]
#     print(f'>> Cant find pss at {latest_date}, looking at next best pss')
#     sys.exit()
    y=x[x['start']<=latest_date]
#     print(y)
#     sys.exit()

    if len(y)==0:
#         print('No previous pss found\n')
        return np.nan, np.nan, np.nan
    else:
#         print(f'found next best at {y.iloc[-1]} FOR DATE {latest_date}, {col}')
#         sys.exit()
        pss=y.iloc[-1][col]
        psserr=y.iloc[-1][colerr]
        ind=1#int(y.iloc[-1]['ind'])
        return abs(pss),abs(psserr),ind
