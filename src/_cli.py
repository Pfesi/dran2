# =========================================================================== #
# File: _cli .py                                                              #
# Author: Pfesesani V. van Zyl                                                #
# Email: pfesi24@gmail.com                                                    #
# =========================================================================== #

# Standard library imports
# --------------------------------------------------------------------------- #
import os, sys
from dataclasses import dataclass, field
import numpy as np
from datetime import datetime
import argparse
from config import __version__, __DBNAME__
import pandas as pd

# Module imports
# --------------------------------------------------------------------------- #
import common.exceptions as ex
from common.contextManagers import open_file
from common.driftScans import DriftScans
from common.enums import ScanType
from common.miscellaneousFunctions import set_dict_item, create_current_scan_directory, delete_logs, set_table_name,fast_scandir
from common.logConfiguration import configure_logging
from common.msgConfiguration import msg_wrapper, load_prog
from common.sqlite_db import SQLiteDB
# =========================================================================== #

import click
#https://click.palletsprojects.com/en/8.1.x/quickstart/


@click.command()
@click.option('-db', help="Turn debugging on or off, e.g., -db on (default is off)", type=str, required=False)
def main():
    pass

@click.command()
@click.argument('file', default='.')
def open_file():
    print('Opened file')

if __name__ == '__main__':
    main()