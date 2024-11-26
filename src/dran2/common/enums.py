from enum import Enum, auto

class ScanType(Enum):
    """
    Drift scan type 

    Args:
        Enum (enum): Enum of the different scan types

    Attributes:
        SBW - wide single beam
        SBN - narrow single beam
        DB - dual beam
    """

    SBW=auto()
    SBN=auto()
    DB=auto()

# class Weekday(Enum):
#     MONDAY = 1
#     TUESDAY = 2
#     WEDNESDAY = 3
#     THURSDAY = 4
#     FRIDAY = 5
#     SATURDAY = 6
#     SUNDAY = 7

class Month(Enum):
    Jan = '01'
    Feb = '02'
    Mar = '03'
    Apr = '04'
    May = '05'
    Jun = '06'
    Jul = '07'
    Aug = '08'
    Sep = '09'
    Oct = '10'
    Nov = '11'
    Dec = '12'