# =========================================================================== #
# File    : logConfiguration.py                                               #
# Author  : Pfesesani V. van Zyl                                              #
# =========================================================================== #

# Standard library imports
# --------------------------------------------------------------------------- #
import logging
import sys

# Local imports
# --------------------------------------------------------------------------- #
sys.path.append("src/")
from config import LOGFILE
# =========================================================================== #

# Setup logger object
logger = logging.getLogger('PIL')#.setLevel(logging.WARNING)

def configure_logging(toggle="off"):
    """Setup the logging configuration.

    This function creates the log object used to log the code in the program.
    By default, all logging information with a level of debug is saved to 
    file and only information with a logging level of info and above is 
    logged to the screen.

    Args:
        toggle (str): Toggle the console setting on or off. Default is 'on'.
            When 'on', debugging is printed to the console; else debugging 
            is printed to file.

    Returns:
        logger (object): The logging object.
    """

    # Create log file and set log levels
    logger.setLevel(logging.DEBUG) # set to info for production server
    # handler1 = logging.FileHandler(logfile, mode='w') #a
    # logger.addHandler(handler1)

    # Setup the format of the file logger
    formatter = logging.Formatter(
        # "%(asctime)s - %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")
        "%(asctime)s: %(message)s", "%Y-%m-%d %H:%M:%S")
    # handler1.setFormatter(formatter)
    logger.debug("Logging initiated")
    
    configure_console_logger(toggle)

    return logger

def configure_console_logger(toggle="off"):
    """Setup the console logger.

    Args:
        toggle (str): Toggle the console setting on or off. Default is 'on'.
            When 'on', debugging is printed to the console; else debugging 
            is printed to file.
    """
    handler2 = logging.StreamHandler(sys.stdout)

    # Configure message logging level to INFO by default
    if toggle == "off":
        handler2.setLevel(logging.INFO)
    else:
        handler2.setLevel(logging.DEBUG)
    logger.addHandler(handler2)