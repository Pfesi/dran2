# =========================================================================== #
# File   : contextManagers.py                                                 #
# Author : Pfesesani V. van Zyl                                               #
# =========================================================================== #

# Standard library imports
# --------------------------------------------------------------------------- #
from contextlib import contextmanager
from astropy.io import fits as pyfits
import os
# import logging
import sqlite3
# =========================================================================== #


@contextmanager
def open_database(dbName:str):
    """
    Context manager for opening and closing a database file

    Args:
        file_name (str): filename of database

    Yields:
        cursor : cursor object to run database operations.
    """
    connection = sqlite3.connect(dbName)
    try:
        cursor = connection#.cursor()
        yield cursor
    finally:
        connection.commit()
        connection.close()

# Unused but may be useful in future
@contextmanager
def open_file(filePath: str):
    """
    Context manager to open fits file for processing

    The open_file function returns an object called an HDULIST which is a
    list-like collection of HDU objects. An HDU (Header Data Unit) is 
    the highest level component of the FITS file structure, consisting
    of a header and (typically) a data array or table.
    see https://docs.astropy.org/en/stable/io/fits/
    
    Args:
        file (str): path to file or filename
    """
    try:
        f = pyfits.open(filePath)
        print('\n')
        # logging.info(f'>>> Opened {filepath}')
        yield f
    except Exception as e:
        print()
        print(f"File processing for {filePath} skipped ")
        print("Error: ",e,'\n')
        # print("Error:  cannot access local variable 'f' where it is not associated with a value")
    finally:
        f.close()
        # logging.info(f'>>> Closed {filepath}\n')

@contextmanager
def change_dir(destination: str):
    """
    Context manager to change working directory

    Args:
        destination (str): path to directory
    """
    try:
        cwd=os.getcwd()
        os.chdir(destination)
        yield
    finally:
        os.chdir(cwd)
        # logging.info(f'Restored working directory to {cwd}')
