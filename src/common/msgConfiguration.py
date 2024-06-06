# =========================================================================== #
# File   : msgConfiguration.py                                                #
# Author : Pfesesani V. van Zyl                                               #
# =========================================================================== #

# Standard library imports
# --------------------------------------------------------------------------- #
import os
# =========================================================================== #

def print_start():
    """Prints program banner."""

    noTabs = 2  # number of tab spaces
    print("###########"*(noTabs*3))
    print("#", "\t"*(noTabs*4), "#")
    print("#", "\t"*noTabs, "######  ######  ###### #    # ", "\t"*noTabs, "#")
    print("#", "\t"*noTabs, "#     # #    #  #    # # #  # ", "\t"*noTabs, "#")
    print("#", "\t"*noTabs, "#     # #####   ###### #  # # ", "\t"*noTabs, "#")
    print("#", "\t"*noTabs, "#     # #    #  #    # #   ## ", "\t"*noTabs, "#")
    print("#", "\t"*noTabs, "######  #    #  #    # #    # ", "\t"*noTabs, "#")
    print("#", "\t"*(noTabs*4), "#")
    print("###########"*(noTabs*3))
    disclaimer()

def disclaimer():
    """Prints disclaimer."""

    print("\n* Disclaimer *: DRAN is a data reduction and analysis software ")
    print("pipeline developed to systematically reduce and analyze HartRAO's ")
    print("26m telescope drift scan data. It comes with no guarantees ")
    print("whatsoever, but the author does attempt to assist those who use it")
    print("to get meaningful results.")
    
def msg_wrapper(logName:str, log:object, msg:str):
    """Wraps logging messages.

    Args:
        log_name (str): The name of the logger e.g. info
        log (object): The logging object
        msg (str): The message to be wrapped.
    """

    # setup wrappers
    wrappers = {
        'debug'    : "<<<<< DEBUG: ",
        'info'     : "***** INFO: ",
        'warning'  : "!!!!! WARNING!: ",
        'error'    : "##### ERROR: ",
        'critical' : "XXXXX CRITICAL: "
    }

    log(wrappers[logName] + msg)

def load_prog(prog:str):
    """Print message to load the selected program."""

    os.system("clear")
    print_start()
    n = 66  # number of asterisks
    print("\n")
    print("*" * n, "\n")
    print(f"\tLoading: {prog}\n")
    print("*" * n, "\n")