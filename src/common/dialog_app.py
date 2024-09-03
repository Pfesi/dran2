# =========================================================================== #
# File: dialog_app.py                                                         #
# Author: Pfesesani V. van Zyl                                                #
# =========================================================================== #

# Standard library imports
# --------------------------------------------------------------------------- #
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog

# Local imports
# --------------------------------------------------------------------------- #
sys.path.append("src/")
from .exceptions import EmptyFolderError, EmptyFilePathError
from .msgConfiguration import msg_wrapper #COMMON.
# =========================================================================== #


class App(QWidget):
    """ 
        Dialog box application to get file/folder path.
        Had to use this because tkinter was crashing on my mac. 
    """

    def __init__(self,log):
        super().__init__()
        self.log = log

        msg_wrapper("debug",self.log.debug,"File dialog App initiated")

    def get_file_path(self):
        """ Get file path using the file open dialog. 
        
            Returns:
                file_path (str): Path to the requested file."""

        ext = "*.fits"  # File extension
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open File", "", "Fits Files ("+ext+");;Fits Files ("+ext+")", options=options)
            if file_path == '':
               raise EmptyFilePathError
            return file_path
        except EmptyFilePathError:
            msg_wrapper("debug", log.debug,
                        "FileHandler initialized")
            self.log.warning("Empty file path selected, try again.\n")
            sys.exit()

    def get_folder_path(self):
        """ Get directory path using the directory open dialog. 
        
            Returns:
                folder_path (str): The path to the directory requested.    
        """

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        try:
            folder_path = QFileDialog.getExistingDirectory(
                self, "Open Directory")
            if folder_path == "":
                raise EmptyFolderError
            return folder_path
        except EmptyFolderError:
            print("Empty folder path selected, try again.\n")
            sys.exit()
