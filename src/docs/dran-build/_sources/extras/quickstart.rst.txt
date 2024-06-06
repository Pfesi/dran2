Quickstart Guide
=================

After the successful `installation <installation.rst>`_ of the package libraries you can now start reducing the data. DRAN provides you with a variety of options to process drift scan data which are
discussed below.

Starting the program without commands
-------------------------------------

As a beginner, it is advised to start running your analysis by basically just entering the program name without any options. This is useful as it starts the program and shows you step by step options you can select to reduce and analyse your data. 

To start the program type 

.. code:: python

   dran 

This command starts the program and displays a set of options a user 
can select to begin processing drift scan data. :: 


   #########################################################
   # 								                                #
   # 		 ######  ######  ###### #    #  		              #
   # 		 #     # #    #  #    # # #  #  		              #
   # 		 #     # #####   ###### #  # #  		              #
   # 		 #     # #    #  #    # #   ##  		              #
   # 		 ######  #    #  #    # #    #  		              #
   # 								                                #
   #########################################################

   #	 PROGRAM STARTED


   ## SELECT OPTION:
   ----------------------------------- 

   1. Data reduction
   2. Open GUI
   3. Run command line analysis
   4. Open documentation
   5. Open dashboard
   6. Exit program

   Please select an option


   Option Selected: 







Starting the program with command line options
-----------------------------------------------

To start the program with command line options.

The program also has an added functionality to let a user type in specific commands that can be run directly 
from the comman line.
To see these commands, type the following 

.. code:: python

   dran -h

This will print out the set of options listed below,::

   usage: dran.py [-h] [-db DB] [-f F] [-force FORCE] [-c C] [-b B]
                  [-delete_db DELETE_DB] [-mfp MFP] [-keep KEEP]
                  [-deleteFrom DELETEFROM] [-conv CONV] [-saveLocs SAVELOCS]
                  [-fitTheoretical FITTHEORETICAL]
                  [-applyRFIremoval APPLYRFIREMOVAL] [-fitLocs FITLOCS]

   Begin processing HartRAO drift scan data

   optional arguments:
   -h, --help            show this help message and exit
   -db DB                turn debugging on or off. e.g. -db on, by default
                           debug is off
   -f F                  process file or folder at given path e.g. -f data/Hydr
                           aA_13NB/2019d133_16h12m15s_Cont_mike_HYDRA_A.fits or
                           -f data/HydraA_13NB
   -force FORCE          force fit all drift scans y/n e.g. -force y. Default
                           is set to n
   -c C                  initiate the command to run program. e.g. -c gui or -c
                           analysis or -c cli
   -b B                  initiate browser. e.g. -b docs or -b dash
   -delete_db DELETE_DB  delete database on program run. e.g. -delete_db y or
                           -delete_db CALDB.db
   -mfp MFP              multi-file processing of data between two dates. e.g.
                           -mfp fileList.txt
   -keep KEEP            keep original plots while processing data. e.g. -keep
                           y
   -deleteFrom DELETEFROM
                           in coordination eith the filename, use deleteFrom to
                           delete a row from a database e.g. deleteFrom CALDB
   -conv CONV            convert database tables to csv. e.g. -conv CALDB
   -saveLocs SAVELOCS    Save fit locations. e.g. -saveLocs y , default is no
   -fitTheoretical FITTHEORETICAL
                           Fit theoretical locations of the baseline, i.e. the
                           FNBW locs. e.g. -fitTheoretical y , default is no.
   -applyRFIremoval APPLYRFIREMOVAL
                           Apply or don't apply RFI removal e.g. -applyRFIremoval
                           n, default is yes
   -fitLocs FITLOCS      Fit data at sepcified locations e.g. -fitLocs
                           pathToFile


.. warning:: 

   If you enter a command that doesn't exist the following error pops up

   e.g. $ python dran.py command_that_doesnt_exists

   usage: dran.py [-h] [-db DB] [-f F] [-force FORCE] [-c C] [-b B]
   [-delete_db DELETE_DB] [-mfp MFP] [-keep KEEP]
   [-deleteFrom DELETEFROM] [-conv CONV] [-saveLocs SAVELOCS]
   [-fitTheoretical FITTHEORETICAL]
   [-applyRFIremoval APPLYRFIREMOVAL] [-fitLocs FITLOCS]

   dran.py: error: unrecognized arguments: command_that_doesnt_exists


### For example:

To perform data reduction on a single file, type in 

dran


This will bring up the menu shown below with options to select how you want to proceeed with your data reduction or analysis. 



In our case we would select option 1 as we are looking to get an automated reduction.

#### Option 1 

Upon selecting option 1, the following propmt will be displayed



Here you will be shown 3 more options.
- Option 1 : reduce 1 file
- Option 2 : reduce a folder containg files of 1 source at a particular frequency
- Option 3 : reduce all files in the directory where all of your sources are located.

In our case we will select option 1 again as we are only looking to process a single file. From here a gui will pop up asking you to locate the file you want to process. Once the file has been located, the program will automatically process and fit your data and make plots of the fit which will be locate in the plots folder. Congratulations, you have just ran your first data reduction.


#### Option 2 

Allows the user to manually reduce the data. With this option the user can tinker with fitting settings and options to get the best fit possible for what they are working on.

#### Option 3 

Opens up the the GUI.

#### Option 4 

Opens up the web resource. The resource contains the code documentation as well as **step by step tutorials** and results from the test data.

#### Option 0 

Exits the program

As shown above some options contain follow up options to further refine your processing selection. Its ultimately up to the user to decide how they want to process their data.

### More examples.


To perform autotomated data reduction on a single file given the absolute path

dran -f filepath

i.e. 
dran -f /Users/pfesesanivanzyl/Final-PhD/code/all_hartrao_data/HydraA_13NB/2014d047_20h30m12s_Cont_mike_HYDRA_A.fits

To perform data reduction on a single file with debugging

dran -f filepath -db y

i.e.
dran -f /Users/pfesesanivanzyl/Final-PhD/code/all_hartrao_data/HydraA_13NB/2014d047_20h30m12s_Cont_mike_HYDRA_A.fits -db y

To perform data reduction/analysis using the GUI
dran -g gui

Once the GUI landing page pops up select the "Edit Driftscan" option.

For a full tutorial please view the web resource on option 4.

.. $ python -m venv .venv
.. $ source .venv/bin/activate
.. (.venv) $ python -m pip install sphinx