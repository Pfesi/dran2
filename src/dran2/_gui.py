# =========================================================================== #
# File: _gui.py                                                               #
# Author: Pfesesani V. van Zyl                                                #
# Email: pfesi24@gmail.com                                                    #
# =========================================================================== #

# Standard library imports
# --------------------------------------------------------------------------- #
import os
import sys
import argparse
from PyQt5 import QtWidgets

# Local imports
# --------------------------------------------------------------------------- #
from common.msgConfiguration import msg_wrapper, load_prog
from common.miscellaneousFunctions import delete_logs
from common.logConfiguration import configure_logging
from gui.mainGuiLogic import Main


def run(args):

    # initiate and configure logging
    delete_logs() # delete any previously generated logfiles
    log = configure_logging()

    load_prog("Graphical user interface (GUI) processing")

    if args.f:

        # start the automated program
        # given a filename or folder name process the data
        readFile= os.path.isfile(args.f)

        # load GUI without given file
        msg_wrapper("info", log.info, f"Switching to GUI, opening file: \
                    {args.f}")
        app = QtWidgets.QApplication(sys.argv)
        gui=Main(log,readFile)
        gui.show()   
        app.exec() 
    else:
        # load GUI without given file
        msg_wrapper("info", log.info, "Switching to GUI")
        app = QtWidgets.QApplication(sys.argv)
        gui=Main(log)
        gui.show()
        
        # Start the event loop.
        app.exec()

def main():
    """
    Command line interface for dran.
    Loads the command name and parameters from :py:data:'argv'.

    Usage:
        dran-gui -h
    """
    try:    
        version=get_version()
    except:
        version='1.0.0'
    parser = argparse.ArgumentParser(prog='DRAN-GUI', 
        description="Begin processing HartRAO drift scan data")
    parser.add_argument("-f", help="process file or folder at given path e.g.\
                        -f data/HydraA/HydraA_13NB/2019d133_16h12m15s_Cont_mike_\
                            HYDRA_A.fits or -f data/HydraA_13NB", type=str, 
                            required=False)
    parser.add_argument('--version', action='version', version='%(prog)s'.lower()+f' v{version}')
    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)

def get_version():
    # TODO: Need to fix this, it causes problems on astro1, code can't find the config file if the try block is removed.
    """ Get version from config file."""
    with open('config.py', 'r') as f:
        for line in f:
            if 'VERSION' in line:
                return (line.split("=")[-1]).replace("'",'').replace("\n",'')

if __name__ == "__main__":
    main()  