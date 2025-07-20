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
# from gui.mainGuiLogic import Main
from gui.mainGuiLogic2 import Main

def run(args):
    """Run the GUI application with optional file processing."""

    # initiate and configure logging
    delete_logs() # delete any previously generated logfiles
    log = configure_logging()

    load_prog("Graphical user interface (GUI) processing")

    # Initialize the Qt application
    app = QtWidgets.QApplication(sys.argv)

    # if args.p

    if args.f:

        # Check if the provided path is a file
        is_file= os.path.isfile(args.f)

        # load GUI with the given file
        msg_wrapper("info", log.info, f"Switching to GUI, opening file: {args.f}")
        gui=Main(log,is_file,args.p)
    else:
        # load GUI without a given file
        msg_wrapper("info", log.info, "Switching to GUI")
        gui=Main(log,args.p)
    
    gui.show()
    sys.exit(app.exec())

def get_version():
    # TODO: Need to fix this, it causes problems on astro1, code can't find the config file if the try block is removed.
    """ Get version from config file."""

    try:
        with open('config.py', 'r') as f:
            for line in f:
                if 'VERSION' in line:
                    return (line.split("=")[-1]).replace("'",'').replace("\n",'')
    except FileNotFoundError:
        return '1.0.0'

def main():
    """
    Command line interface for dran.
    Loads the command name and parameters from :py:data:'argv'.

    Usage:
        dran-gui -h
    """
    
    version=get_version()

    parser = argparse.ArgumentParser(
        prog='DRAN-GUI', 
        description="Begin processing HartRAO drift scan data"
    )

    parser.add_argument(
        "-f", 
        help="process file or folder at given path e.g.\
                        -f data/HydraA/HydraA_13NB/2019d133_16h12m15s_Cont_mike_\
                            HYDRA_A.fits or -f data/HydraA_13NB", 
        type=str, 
        required=False
    )

    parser.add_argument(
        "-p", 
        help="path to save directory e.g.\
                        -p /Users/pfesi/results/\
                        required if you want to \
                        recalculate pss/flux during changes. please use full path.", 
        type=str, 
        required=False
    )

    parser.add_argument(
        '--version', 
        action='version', 
        version='%(prog)s'.lower()+f' v{version}'
    )

    parser.set_defaults(func=run)
    
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()  