# =========================================================================== #
# File: exceptions.py                                                         #
# Author: Pfesesani V. van Zyl                                                #
# =========================================================================== #

# Standard library imports
# --------------------------------------------------------------------------- #
import sys
# =========================================================================== #


class Error(Exception):
    """ Base class for other exceptions. """
    pass

class InvalidFilePath(Error):
    """ Raised when a file path is invalid. """
    pass

class InvalidFileExtensionError(Error):
    """ Raised when a file has an invalid file extension. """
    pass

class EmptyFilePathError(Error):
    """ Raised when an expected file path is empty. """
    pass

class EmptyFolderError(Error):
    """ Raised when a folder is empty """
    pass

class MissingChartHeaderError(Error):
    """ Raised when a fits file is missing a chart header unit. """
    pass

class MissingParameterException(Error):
    """ Raised when a fits file is missing a chart header unit. """
    pass

class EmptyTableError(Error):
    """ Raised when a database table is empty. """
    pass

class ValueOutOfRangeException(Error):
    """ Raised when a value is out of range. """
    pass

class FileResourceNotFoundError(Error):
    """ Raised when a file resource is not found or wasn't included in the distribution files"""
    pass

class DB_READ_ERROR(Error):
    """ Database read error"""
    pass

class DB_WRITE_ERROR(Error):
    """ Databae write error"""
    pass

class BeamTypeNotFoundError(Error):
    """ Beam type not found error"""
    pass