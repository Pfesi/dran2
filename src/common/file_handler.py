# =========================================================================== #
# File    : file_handler.py                                                   #
# Author  : Pfesesani V. van Zyl                                              #
# =========================================================================== #

# Standard library imports
# --------------------------------------------------------------------------- #
import os.path
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog
import shutil 
from pathlib import Path

# Local imports
# --------------------------------------------------------------------------- #
sys.path.append("src/")
import common.exceptions as ex
from common.dialog_app import App
from common.msgConfiguration import msg_wrapper
# =========================================================================== #


class FileHandler:
    """ 
        FileHandler manages the access and modification of 
        files and their folders.

        Args:
            log (object): logging object
            path (str): Path to a file
    """ 

    def __init__(self, log, path=""):
        
        # configure logging
        self.log = log         
        self.path = path

    def __str__(self):
        return("FileHandler() object to manage document/file access.")

    def get_details_from_path(self,path=""):
        """ Get file name and containing directory and their from path. """

        if path == "":
            self.fileName=""
            self.folderName =""
            self.filePath=""
            self.folderPath=""
        else:
            self.fileName = os.path.basename(path)
            if self.fileName != "":
                self.filePath = path
            else:
                self.filePath=""
            self.folderName = os.path.basename(os.path.dirname(path))
            self.folderPath = os.path.dirname(path)

    def delete_file(self, fileName):
        """ Delete a file. 
        
            Args:
                fileName (str): The name of the file being deleted. 
        """

        print("\n")
        msg_wrapper("basic", self.log.debug,
                    "Delete file if it exists")
        try:
            os.remove(fileName)
            msg_wrapper("debug", self.log.debug,
                        "Deleted file: {}".format(fileName))
        except OSError:
            msg_wrapper("debug", self.log.debug,
                        "Can't delete file {}, it doesn't exist".format(fileName))

    def confirm_file_path_exists(self, filePath=""):
        """ Confirm the file path / file exists. 

            Args:
                filePath (str): The absolute path to a file

            returns:
                Boolean value representing whether the path exists or not. 
        """
        
        if filePath=="":
            filePath=self.filePath
        else:
            pass
        try:
            pathFound = os.path.exists(filePath)
            if pathFound == False:
                raise OSError
            else:
                msg_wrapper("debug", self.log.debug,
                            "File path validation passed")
                return pathFound
        except OSError:
            msg_wrapper("error", self.log.error,
                        "Path/File '{}' is invalid or doesn't exist. \nTry using the absolute path or relative path.\n".format(filePath))
            sys.exit()

    def confirm_file_path_exists_no_exit(self, filePath=""):
        """ Confirm the file path / file exists. 

            Args:
                filePath (str): The absolute path to a file
                
            returns:
                Boolean value representing whether the path exists or not. 
        """

        if filePath=="":
            filePath=self.filePath
        else:
            pass
        
        if os.path.exists(filePath) == False:
            msg_wrapper("warning", self.log.warning,
                        "Path/File '{}' is invalid or doesn't exist. \nTry using the absolute path or relative path.\n".format(filePath))
        else:
            msg_wrapper("debug", self.log.debug,
                            "File path validation passed")
            return os.path.exists(filePath)

    def get_file_name_from_path(self):
        """ return the name of a file from the path. """

        msg_wrapper("debug",self.log.debug,"Got filename from path: {}".format(self.path))
        path, fileName = os.path.split(self.path)
        return fileName

    def get_file_extension(self, fileName=""):
        """ Get file extension from file name. 
        
            Args:
                fileName (str): The name of the file. 
        """

        if fileName=="":
            fileName=self.fileName
        else:
            pass
        name, ext = os.path.splitext(fileName)
        msg_wrapper("debug", self.log.debug,
                    "File extension validated")
        return ext

    def confirm_file_extension(self,extension):
        """ Confirm that the file has the correct extension. 
            e.g. the program processes fits files so the extension should
            be .fits 
            
            Args: 
                extension (str): The file's extension  
        """

        print("\n")
        msg_wrapper("basic", self.log.debug,
                    "Validating file contains correct extension")
        try:
            fileExt = self.get_file_extension()
            if fileExt != extension:
                raise ex.InvalidFileExtensionError
        except ex.InvalidFileExtensionError:
            msg_wrapper("error", self.log.error,
                        "{} has an invalid file extension. Program processes *.fits files\n ".format(self.fileName))

    def validate_file(self):
        """ Perform file validations. Check if the file exists and if it is in the correct format."""

        print("\n")
        msg_wrapper("basic", self.log.debug,
                    "Validating file conforms to requirements")

        # check path exists, if path exixts return file name and get its extension
        pathFound = self.confirm_file_path_exists()
        
        # confirm file extension matches required extension
        self.confirm_file_extension(".fits")

    def create_folder(self,folderName):
        """ Create a folder.

            Args:
                folderName (str): String of folder name
        """

        if os.path.exists(folderName) == True:
            msg_wrapper("debug", self.log.debug,
                        folderName + " folder already exists, moving on")
        else:
            msg_wrapper("basic", self.log.debug,
                        "Create " + folderName + " folder")
            os.makedirs(folderName)

    def create_folder_overwrite_existing(self, folderName):
        """ Create a folder."""

        msg_wrapper("basic", self.log.debug,
                    "Created " + folderName + " folder")

        if os.path.exists(folderName) == True:
            os.system("rm -r "+folderName)
            os.makedirs(folderName)
        else:
            os.makedirs(folderName)

    def get_file_name_and_containing_folder(self):
        """ Get the name of the file and its containing folder. """

        if self.filePath == "":
            self.filePath = self.get_file_path_from_dialog_box()
        else:
            pass

        self.get_file_name_from_path()
        self.get_folder_name_from_path()
        self.print_path_info()

    def get_directory_name(dirPath="", filePath=""):
        """ Get directory name from path. You can supply a file path or the full path to the directory.

        Parameters
        ----------    
            dirPath: str
                path to directory  
            filePath: str
                Path to file  
            log: object
                logging object

        Returns
        -------
            name of opened directory
        """

        if dirPath == "":
            return os.path.basename(os.path.dirname(filePath))
        else:
            return Path(dirPath).name

    def print_path_info(self):
        """ Print information on the file. """

        self.log.info("-"*80)
        self.log.info("Path name: {}".format(self.filePath))
        self.log.info("File name: {}".format(self.fileName))
        self.log.info("Folder name: {}".format(self.folderName))
        self.log.info("-"*80+"\n")
    
    def get_folder_name_from_path(self):
        """ Get the name of the containing folder from a path. """

        msg_wrapper("debug",self.log.debug,"Getting folder name from path")
        self.folderName = os.path.basename(
                os.path.dirname(self.filePath))

    def get_file_path_from_dialog_box(self):
        """ Get a file using the file dialog box. """

        msg_wrapper("debug",self.log.debug,"Launching file dialog box for file selection.")
        app1=QApplication(sys.argv)
        myapp = App(self.log)
        filePath = myapp.get_file_path()
        sys.exit(app1.exec_())
        return filePath

    def get_folder_path_from_dialog_box(self):
        """ Get a file using the file dialog box. """

        msg_wrapper("debug", self.log.debug,
                    "Launching file dialog box for file selection.")
        app = QApplication(sys.argv)
        myApp = App(self.log)
        filePath = myApp.get_folder_path()
        sys.exit()
        return filePath