# CHANGELOG


##### v1.4.8 (2024-11-26 09:29)
- fixed issue with skipping data processing for continuum sources at 22 GHz if fit was difficult. probably need to redo all 22ghz obs for all sources, especially the faint ones


##### v1.4.7 (2024-11-26 09:12)
- fixed bugs in file resource location


##### v1.4.6 (2024-11-26 08:53)
- moved all folders into src/dran2


##### v1.4.5 (2024-11-26 08:43)
- moved _auto.py to src to fix moduleNotFound error


##### v1.4.3 (2024-11-25 14:57)
- fixed bug - couldn't locate config file


##### v1.3.2 (2024-11-25 14:49)
- fixed bug - couldn't locate config file


##### v1.4.0 (2024-11-25 14:46)
- Enabled GUI functionality

##### v1.2.3 (2024-11-25 10:02)
- changed build to hatchling


##### v1.2.2 (2024-11-25 09:40)
- testing new config arrangement


##### v1.2.1 (2024-11-25 09:08)
- Added a MANIFEST.in file


##### v1.2.0 (2024-11-25 09:00)
- Added method to GUI module to get latest version of program from config file. 
-  Cleaned up some of the code.

##### v1.1.1 (2024-11-23 08:22)
- Updated the version manager, no longer using settings file, now using config file in src folder.


##### v1.1.0 (2024-11-23 06:46)
- Added functionality to manage version control, updates the changelog file


## Older updates
- removed atmospheric calibration at 6.7 GHz. Was causing issues with the data processing pipeline.