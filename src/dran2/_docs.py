# =========================================================================== #
# File: _docs.py                                                              #
# Author: Pfesesani V. van Zyl                                                #
# Email: pfesi24@gmail.com                                                    #
# =========================================================================== #

# Standard library imports
# --------------------------------------------------------------------------- #
import webbrowser
import os, sys
# --------------------------------------------------------------------------- #

import importlib.resources as resources

def main():
    """ 
    Open the source documentation.
    """
    
    # set path to docs
    dir_path = os.path.dirname(os.path.realpath(__file__))
    x=os.path.join(dir_path,'docs/dran-build/index.html')

    print("Opening docs")
    print(resources.contents('docs'))

    try:
        webbrowser.open_new_tab('file://' + x)
        print('Browser opened ')
    except:
        print("There's a problem with the browser launching, contact the author or visit the readthedocs site")
        sys.exit()

if __name__ == "__main__":
    main()