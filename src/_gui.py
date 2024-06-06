# ============================================================================#
# File: _gui.py                                                     #
# Author: Pfesesani V. van Zyl                                                #
# ============================================================================#

# Standard library imports
# --------------------------------------------------------------------------- #
# The automated part of dran
import os
import sys
import argparse
from PyQt5 import QtWidgets

# Local imports
# --------------------------------------------------------------------------- #
from .common.messaging import msg_wrapper, load_prog
from .common.misc_funcs import delete_logs
from .common.log_conf import configure_logging
from gui.main_gui_logic import Main

def main():
    """
    Command line interface for dran.
    Loads the command name and parameters from :py:data:'argv'.

    Usage:
        dran-gui -h
    """

    parser = argparse.ArgumentParser(prog='DRAN-GUI', 
        description="Begin processing HartRAO drift scan data")
    parser.add_argument("-db", help="turn debugging on or off. e.g. -db on, \
                        by default debug is off", type=str, required=False)
    parser.add_argument("-f", help="process file or folder at given path e.g.\
                        -f data/HydraA_13NB/2019d133_16h12m15s_Cont_mike_\
                            HYDRA_A.fits or -f data/HydraA_13NB", type=str, 
                            required=False)
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()