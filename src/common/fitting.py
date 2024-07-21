from .msgConfiguration import msg_wrapper
from .plotting import * 

from scipy import interpolate
from sklearn.metrics import mean_squared_error
import numpy as np
# import matplotlib.pyplot as pl
from scipy.optimize import curve_fit
import sys
import bisect

# import warnings
# def fxn():
#     warnings.warn("deprecated", DeprecationWarning)
# with warnings.catch_warnings(action="ignore"):
#     fxn()


def clean_rfi(x, y, log=""):
    """
        Clean the RFI in the data using iterative rms cuts. 
        
        Parameters:
            x (array): Array of the independent variable
            y (array): Array of the dependent variable
            log (object): file logging object

        returns: 
            finX (array): the data representing the x-axis after the removal of rfi data
            finY (array):the data representing the y-axis after the removal of rfi data
            rmsBeforeClean (int): the rms before removal of rfi data
            rmsAfterClean (int): the rms after removal of rfi data
            finspl (array): the spline of the cleaned data
            pointsDeleted (int): number of points deleted when cleaning the data
    """

    msg_wrapper("debug", log.debug, "Cleaning the data of RFI")

    # spline the data
    splined_data = spline(x, y,log=log)
    scanLen = len(x)
    resRFI, rmsBeforeClean, rmsAfterClean, finX, finY, finRes, finMaxSpl, finspl, pointsDeleted = clean_data(
        splined_data, x, y, scanLen,log)

    msg_wrapper("debug", log.debug, "Splined RMS before: after cleaning -> {:.3f}: {:.3f} \n".format
                (rmsBeforeClean, rmsAfterClean))

    return finX, finY, rmsBeforeClean, rmsAfterClean, finspl, pointsDeleted

def clean_data(spl, x, y, scanLen, log=""):
    """
        Clean the data using iterative fitting. 

        Args:
            spl : 1d array
                the splined data
            x : 1d array
                data representing the x-axis
            y : 1d array
                data representing the y-axis
            scanLen : int
                length of the drift scan array
            log : object
                file logging object

        Returns:
            resRFI: 1d array
                the residual before the rfi has been removed
            rmsBeforeClean: int
                the rms before removing rfi data
            rmsAfterClean: int
                the rms after removal of rfi data
            finX: 1d array
                the data representing the x-axis after the removal of rfi data
            finY: 1d array
                the data representing the y-axis after the removal of rfi data
            finRes: 1d array
                the residual of the cleaned data after the rfi has been removed
            finMaxSpl: int
                the maximum of the spline of the cleaned data
            finspl: 1d array
                the spline of the cleaned data
            pointsDeleted: int
                number of points deleted when cleaning the data
    """
    
    msg_wrapper("debug", log.debug, "Iterative cleaning of RFI")

    # calculate the residual and clean the data
    resRFI, rmsBeforeClean = calc_residual(spl, y,log)
    finX, finY, rmsAfterClean, finRes, finMaxSpl, finspl, pointsDeleted = clean_data_iterative_fitting(
        x, y, scanLen, resRFI, rmsBeforeClean,log)

    return resRFI, rmsBeforeClean, rmsAfterClean, finX, finY, finRes, finMaxSpl, finspl, pointsDeleted

def calc_residual(model, data, log=""):
    """
        Calculate the residual and rms between the model and the data.

        Parameters:
            model (array): 1D array containing the model data
            data (array): 1D array containing the raw data
            log (object): file logging object

        Returns
        -------
        res: 1d array
            the residual
        rms: int
            the rms value
    """

    res = np.array(model - data)
    rms = np.sqrt(mean_squared_error(data, model))

    return res, rms

def clean_data_iterative_fitting(x, y, scanLen, res, rms, log="",x2=""):
    ''' Find the best fit to the data by iteratively eliminating data points
    that fall beyond an established cut-off limit.

        Parameters
        ----------
        x : 1d array
            data representing the x-axis
        y : 1d array
            data representing the y-axis
        scanLen : int
            length of the drift scan array
        res: 1d array
            the residual
        rms: int
            the rms value
        log : object
            file logging object
        x2 : 1d array
            filenames

        Returns
        -------
            finalX: 1d array
                the data representing the x-axis after the removal of rfi data
            finalY: 1d array
                the data representing the y-axis after the removal of rfi data
            finalRms: int
                the rms after removal of rfi data
            finRes: 1d array
                the residual of the cleaned data after the rfi has been removed
            finMaxSpl: int
                the maximum of the spline of the cleaned data
            finalSplinedData: 1d array
                the spline of the cleaned data
            pointsDeleted: int
                number of points deleted when cleaning the data
    '''

    #msg_wrapper("debug", log.debug, "Performing RFI cuts on data")
    # ToDo: Make this more effecient

    # set initial values
    smallestY = y
    smallestX = x

    # set final value parameters
    finalNames=[]
    finalX = []
    finalY = []
    finalRms = []
    finalRes = []
    finalMaxSpl = []
    finalSplinedData = []
    smallest = True
    loop = 0

    while smallest:
        #While you don't have the smallest rms, process data

        loop = loop+1
        #print('loop: ',loop)

        #Remove spikes
        if len(x2)==0:
            newX, newY = _remove_RFI(smallestX, smallestY, res, rms)
        else:
            newX, newY ,newNames= _remove_RFI(smallestX, smallestY, res, rms,log,x2)
            finalNames=newNames

        newX = np.array(newX)
        newY = np.array(newY)
       
        #spline the data if you found RFI
        splineData2 = spline(newX, newY,log=log)
        maxSplineData2 = max(splineData2)
        res2, rms2 = calc_residual(splineData2, newY)

        if rms2 < rms:  # get better values
            rms = rms2
            res = res2
            smallestX = newX
            smallestY = newY
            finalX = newX
            finalY = newY
            finalRms = rms2
            finalRes = res2
            finalSplinedData = splineData2
            finalMaxSpl = maxSplineData2
            if len(x2)!=0:
                finalNames=newNames
            smallest = True
        else:
            smallest = False

    # If the rms cut only looped once, values dont change
    if loop == 1:

        # If you already have good data, keep values as they are
        finalX = x
        finalY = y
        finalRms = rms
        finalRes = res

        #spline the data
        finalSplinedData = spline(x, y,log=log)
        finalMaxSpl = max(finalSplinedData)

        if len(x2)==0:
            #print('p')
            finalNames=x2

    pointsDeleted = scanLen-len(finalY)

    if len(x2)==0:
        return finalX, finalY, finalRms, finalRes, finalMaxSpl, finalSplinedData, pointsDeleted
    else:
        print(f'\n{abs(len(x)-len(finalNames))} entries removed, after {loop} iterations\n{len(finalNames)} remaining\n')

        return finalX, finalY, finalRms, finalRes, finalMaxSpl, finalSplinedData, pointsDeleted, finalNames
    
def _remove_RFI(x, y, res, rms, log="",x2=""):
    '''
            Removes data points with a residual cutt-off
            more or less than 2.7*rms

            Parameters
            ----------
            x : 1d array
                data representing the x-axis
            y : 1d array
                data representing the y-axis
            res: 1d array
                the residual
            rms: int
                the rms value
            log : object
                file logging object

            Returns
            -------
            cleanX: 1d array
                array of data representing the x-axis
            cleanY: 1d array
                array of data representing the cleaned y-axis data
    '''

    scanLen = len(x)
    cleanX, cleanY, names = ([] for i in range(3))  # create new lists
    cut=3#2.7
    if len(x2)==0:
        for i in range(scanLen):
            if(abs(res[i]) > cut * rms):  # 2.5, 2.7 3.0
                pass
            else:
                # Keep points that lie within the cut_off
                cleanX.append(x[i])
                cleanY.append(y[i])

        return cleanX, cleanY
    else:
        #print('n')
        for i in range(scanLen):
            if(abs(res[i]) > cut* rms):  # 2.5, 2.7 3.0
                pass
            else:
                # Keep points that lie within the cut_off
                cleanX.append(x[i])
                cleanY.append(y[i])
                names.append(x2[i])

        #print('len names: ',len(names))
        return cleanX, cleanY, names
    
def gauss_lin(x, *p):
    """
        Generate a gaussian plus first-order polynomial to fit the drift 
        scan beam. Note that the width of the Gaussian is hard-coded 
        to the half-power beamwidth.

        Parameters
        ----------
            x : 1D array
                1D array of data representing the x-axis
            p : tuple
                tuple of gaussian parameters 

        Returns
        -------
            gaussFit: 1d array 
                array of data representing the gaussian fit
     """

    amp, mu, hpbw, a, c = p
    sigma = hpbw/(2*np.sqrt(2*np.log(2)))
    return amp*np.exp(-(x-mu)**2/(2.*sigma**2)) + a*x + c

def spline(x, y, anchor_points=9, order=3,log=""):
    '''
        Given a set of data points (x,y) determine a smooth spline
        approximation of degree k on the interval x[0] <= x <= x[n]

        Args:
            x (array): 1D array of data representing the x-axis
            y (array): 1D array of data representing the y-axis
            anchor_points (int): the number of anchor points in the data
            order (int): polynomial order to fit, preferrably a cubic spline
        Return:
            spline_fit (array): Spline of the data
    '''

    try:    
        msg_wrapper("debug", log.debug, "Spline the data to get estimate of underlying signal")
    except:
        pass

    scanLen = len(x)
    if scanLen <= anchor_points*2:
        print("Too few points to interpolate, consider entering lower knot points")
        print("spline not set")
        spline_fit=[]
    else:
        #anchor_points=7
        anchor_points_intervals = scanLen/anchor_points  # intervals where anchor points will be placed
        anchor_points_pos = [] # list to hold positions where anchor_points will be placed olong the array
        anchor_points_counter = 0 # position counter or locator 

        # create a list of the positions where the anchor_points will be located
        #anchor_points=10
        for i in range(anchor_points-1):
            anchor_points_counter = anchor_points_counter + anchor_points_intervals
            anchor_points_pos.append(int(anchor_points_counter))

        # interpolate the data
        # create linearly spaced data points
        x1 = np.linspace(1, scanLen, scanLen)
        x2 = np.array((anchor_points_pos), int)	# create array of anchor_points positions
        
        try:
            tck = interpolate.splrep(x1, y, k=order, task=-1,
                                    t=x2)  # interpolate, k=5 is max
            spline_fit = interpolate.splev(x1, tck, der=0)
        except:
            print("Failed to interpolate, Error on input data,too few points, min required = 9")
            spline_fit=y

    return spline_fit#,anchor_points_pos

def spline_fit(x, y, anchor_points=9, order=3):
    '''
        Given a set of data points (x,y) determine a smooth spline
        approximation of degree k on the interval x[0] <= x <= x[n]

        Args:
            x (array): 1D array of data representing the x-axis
            y (array): 1D array of data representing the y-axis
            anchor_points (int): the number of anchor points in the data
            order (int): polynomial order to fit, preferrably a cubic spline
        Return:
            spline_fit (array): Spline of the data
    '''

    nx=[]
    ny=[]
    # remove nan values
    for i in range(len(x)):
        #print(i,y[i],type(y[i]))
        if y[i] == np.nan or str(y[i]) =="nan":
            #print(i,y[i])
            pass
        else:
            nx.append(x[i])
            ny.append(y[i])

    scanLen = len(nx)
    if scanLen <= anchor_points*2:
        print("Too few points to interpolate, consider entering lower knot points")
        print("spline not set")
        spline_fit=[]
    else:
        #anchor_points=7
        anchor_points_intervals = scanLen/anchor_points  # intervals where anchor points will be placed
        anchor_points_pos = [] # list to hold positions where anchor_points will be placed olong the array
        anchor_points_counter = 0 # position counter or locator 

        # create a list of the positions where the anchor_points will be located
        #anchor_points=10
        for i in range(anchor_points-1):
            anchor_points_counter = anchor_points_counter + anchor_points_intervals
            anchor_points_pos.append(int(anchor_points_counter))

        # interpolate the data
        # create linearly spaced data points
        x1 = np.linspace(1, scanLen, scanLen)
        x2 = np.array((anchor_points_pos), int)	# create array of anchor_points positions
        
        try:
            tck = interpolate.splrep(x1, ny, k=order, task=-1,
                                    t=x2)  # interpolate, k=5 is max
            spline_fit = interpolate.splev(x1, tck, der=0)
        except:
            print("Failed to interpolate, Error on input data,too few points, min required = 9")
            spline_fit=ny

        #print(len(x),len(spline_fit))
        #print(spline_fit)
    #     pl.plot(x,y,'k.')
    #     pl.plot(nx,spline_fit,'r')
    #    # pl.plot(nx[anchor_points_pos],spline_fit[anchor_points_pos],'r.')
    #     pl.show()
    #     pl.close()
    #     print('closed')
    #     sys.exit()
    return nx,spline_fit#,anchor_points_pos

def gauss(x, *p):
        """
        Gaussian for fitting the beam 
        """
        amp, mu, hpbw = p
        sigma = hpbw/(2*np.sqrt(2*np.log(2)))  #a bit messy but not sure how to pass a constant through the curve fitting
        return amp*np.exp(-(x-mu)**2/(2.*sigma**2))

def test_gauss_fit(x,y,p0,log=""):
        """
        Fit the data using a gaussian

        Arguments:
            p0: initial fit guess
        """

        # fit initial guess parameters to data and get best fit parameters
        # returns best fit coeffecients and errors
        # Curve fitting is a type of optimization that finds an optimal set 
        # of parameters for a defined function that best fits a given set of observations.
        try:
            coeff, covarMatrix = curve_fit(gauss_lin, x,y, p0)
            fit = gauss_lin(x, *coeff)
            try:
                msg_wrapper("info", log.info, f"Passed gaussian fit test, Max peak =  {max(fit):.3f} [K]")
            except:
                pass
            return coeff,fit,""
        
        except Exception as e:
            print(e)
            try:
                msg_wrapper("warning", log.warning, "gaussian curve_fit algorithm failed")
            except:
                pass

            flag=3
            return [],[],flag
        
def test_position_validity(localMaxPositions,localMinPositions,maxPoints):
            """
            Test the position validity of the local min/max positions. The 
            local minimum positions cannot fall within the range of the 
            local maximum positions.

            Args:
                localMaxPositions (list): list of local max positions
                localMinPositions (list): list of local min positions
                p (int): maximum number of permissable points.
            Returns:
                pointsToDelete: index list of positions to delete
            """
            pointsToDelete = []
            halfMaxPoints=int(maxPoints/2)
            for i in range(len(localMaxPositions)):
                # create list of max positions bounded by the condition
                window=np.arange(localMaxPositions[i]-halfMaxPoints,localMaxPositions[i]+halfMaxPoints,1)
                for j in range(len(localMinPositions)):
                    if localMinPositions[j] in window:
                        print(j, localMinPositions[j] , i, localMaxPositions[i])#, window)
                        pointsToDelete.append(localMinPositions[j] )
            return pointsToDelete

def locate_baseline_blocks_auto(x,y,peakCenterGuess, hfnbw,log,saveLoc):
        """
        Find the locations to fit a baseline automatically.

        These locations are found/determined by fitting a 
        spline to the data and using the 
        locations of the local minimum as baseline regions.

        Parameters:
            peakCenterGuess (float): value of x at peak center in x array
            hfnbw (float): half the first null beam width
            log (object): loffing object
        """
         
        # setup parameters
        msg = "" # message to write on plot
        flag = 0 # error flag, default to no error detected 

        # generate a spline to help locate where to best fit our baseline model.
        yspl = spline(x, y,log=log)

        # find location of maximum peak, assumed to be at center
        try:
            peakPosition = (np.where(x >= peakCenterGuess)[0])[0]
            peakSpline = np.where(yspl == max(yspl))[0]
        except Exception:
            msg = "Failed to determine center peak location"
            msg_wrapper("warning",log.warning,msg)
            flag = 22
            return [], [], [], 0, flag, msg, 0, 0, 0, 0
     
        # LOCATE LOCAL MINUMUM/MAXIMUM POSITIONS
        # these values are used to figure out where to
        # select our baseline points/locations for
        msg_wrapper("debug",log.debug,'Locate local min and max positions')
        localMinPositions = (np.diff(np.sign(np.diff(yspl))) > 0).nonzero()[0] + 1  # local min positions / first nulls
        localMaxPositions = (np.diff(np.sign(np.diff(yspl))) < 0).nonzero()[0] + 1  # local max positions / peak

        msg=f'Found positions of possible local mins at: {localMinPositions}, and local maxs at: {localMaxPositions}'
        msg_wrapper("debug",log.debug,msg)
        
        # get maximum of driftscan
        ymax = max(yspl)
        
        # Delete local min point within 50 points of either side of a local max point from the positions found above
        maxPoints=50 
        pointsToDelete=test_position_validity(localMaxPositions,localMinPositions,maxPoints)

        # If any invalid points found, delete them
        if len(pointsToDelete)!=0:
            for k in range(len(pointsToDelete)):
                if pointsToDelete[k] in localMinPositions:
                    localMinPositions=list(localMinPositions)
                    ind=localMinPositions.index(pointsToDelete[k])
                    del localMinPositions[ind]

        #ensure that the points are in an array
        localMinPositions=np.array(localMinPositions)
        msg=f'After validating points, the accepted positions for -> Min locs: {localMinPositions}, and Max locs: {localMaxPositions}'
        msg_wrapper("debug",log.debug,msg)
        
        # if len(localMinPositions)=0 try to establish other possible locations
        if len(localMinPositions) == 0 :
            msg = "- Failed to locate local min positions, set to FNBW locs"
            msg_wrapper("warning", log.warning, msg)
            flag = 21
            # sys.exit()
            try:
                h=np.where(x<=-hfnbw)[0][-1]
                print(h)
            except:
                h=x[0]
            
            try:
                #TODO write better notes on why i do this
                hh=[np.where(x>=hfnbw)[0][0]][0]
            except:
                hh=x[-1]

            localMinPositions=[h,hh]

        # if len(localMinPositions) still = 0 and len(localMaxPositions) == 0
        if len(localMinPositions) == 0 or len(localMaxPositions) == 0:
            msg = "Failed to locate local min and max positions"
            msg_wrapper("warning", log.warning, msg)
            flag = 19
            # print(msg)
            # sys.exit()
            return [], [], [], 1, flag, msg, 0, 0, 0, 0

        # localMinPositions must be = 2, number of local minimum positions found
        # IF MORE ARE FOUND WE MOST PROBABLY HAVE SIDELOBES
        numberOfMinPositions = len(localMinPositions)

        # Find the index or insertion point for the peakPosition in the
        # locMinPositions list. i.e. where we most likely expect the 
        # peak to be located.
        peakInd = bisect.bisect(localMinPositions, peakPosition)
        scanLen = len(x)

        # basic parameter info
        msg_wrapper("debug", log.debug, "\n")
        msg_wrapper("debug", log.debug, "-"*30)
        msg_wrapper("debug", log.debug,"Drift scan basic info: ")
        msg_wrapper("debug", log.debug,"-"*30)
        msg_wrapper("debug", log.debug,f"Found local minimums at = {localMinPositions}")
        msg_wrapper("debug", log.debug,f"Found local maximums at = {localMaxPositions}")
        msg_wrapper("debug", log.debug, f"no. of local min positions = {numberOfMinPositions}")
        msg_wrapper('debug', log.debug, f"index of peak in local mins = {peakInd}") # i.e. if peak were inserted  between the local mins, what would its index be
    
        # check location of peak
        msg_wrapper("debug", log.debug, "\n")
        msg_wrapper("debug", log.debug, "-"*20)
        msg_wrapper("debug", log.debug, "Peak locations: ")
        msg_wrapper("debug", log.debug, "-"*20)
        msg_wrapper("debug", log.debug, f"Peak pos from Gauss fit: {peakPosition}")
        msg_wrapper("debug", log.debug, f"Peak pos from Spline fit: {peakSpline[0]}")
        msg_wrapper("debug", log.debug, f"Peak pos if at mid of scan: {int(scanLen/2)}")

        # Ensure peak falls within expected range, beyond 25% of the beginning of the drift scan and
        # below 75% of the end of the drift scan.
        peakLocMinLimit = int(scanLen*.25)
        peakLocMaxLimit = int(scanLen*.75)
        
        # If the code has struggled to locate the local min/max,
        if ( peakPosition < peakLocMinLimit or peakPosition > peakLocMaxLimit ):
            msg = "Peak not within expected range."
            msg_wrapper("info", log.info, msg)
            flag=20
            msg_wrapper("info", log.info, f"Peak limit left: {peakLocMinLimit}")
            msg_wrapper("info", log.info, f"Peak position: {peakPosition}") 
            msg_wrapper("info", log.info, f"Peak limit right: {peakLocMaxLimit}")
            # sys.exit()
            return [],[],[],1,flag,msg,[],[],0,0

        else:

            # locate/setup fnbw location on left and right of beam
            # if we can't locate base locations program defaults
            # to fnbw locations
            try:
                leftFNBWPoint = (np.where(x >= (peakCenterGuess-hfnbw))[0])[0]
            except:
                leftFNBWPoint = 0

            try:
                rightFNBWPoint = (np.where(x >= (peakCenterGuess+hfnbw))[0])[0]
            except:
                rightFNBWPoint = len(x)

            if rightFNBWPoint == len(x) or leftFNBWPoint == 0:
                flag=27
                msg="Failed to locate FNBW locations"
                msg_wrapper("info", log.info, msg)
                # print(msg)
                # sys.exit()
                return [], [], [], 1, flag, msg, 0, 0, 0, 0

            # msg_wrapper("debug", log.debug, "\n")
            msg_wrapper("debug", log.debug, "\n")
            msg_wrapper("debug", log.debug, "-"*20)
            msg_wrapper("debug", log.debug, "Locate/setup location of FNBW: ")
            msg_wrapper("debug", log.debug, "-"*20)
            
            msg_wrapper("debug", log.debug, f"FNBW: {hfnbw*2}") 
            msg_wrapper("debug", log.debug, f"HFNBW: {hfnbw}") 
            msg_wrapper("debug", log.debug, f"left fnbw loc: {leftFNBWPoint}") 
            msg_wrapper("debug", log.debug, f"right fnbw loc: {rightFNBWPoint}")

            
            # SEARCH FOR MINIMUMS
            # We only need two points, one on left of peak and one on right of peak
            # if we have more points this means there are side lobes and we
            # need to adjust the baseline accordingly
            msg_wrapper("debug", log.debug, "\n")
            msg_wrapper("debug", log.debug, "-"*20)
            msg_wrapper("debug", log.debug, "Finding locations of local minimum from scan: ")
            msg_wrapper("debug", log.debug, "-"*20)
            
            # set fault parameters
            rf = 0  # right is faulty rf=1
            lf = 0  # left is faulty lf=1
            
            if peakInd == 0 and len(localMinPositions) == 1:
                # there is only one peak index position found

                msg_wrapper("debug", log.debug, f'peak ind: {peakInd}, local min pos: {len(localMinPositions)}')

                if localMinPositions[peakInd] < peakPosition:
                    # the position found is to the left of the assumed peak location

                    minPosOnLeftOfPeak = localMinPositions
                    minPosOnRightOfPeak = rightFNBWPoint
                    
                    flag = 6
                    rf = 1
                    msg = "Failed to locate right min pos"
                    msg_wrapper("info", log.info,msg)
                    msg_wrapper("debug", log.debug,
                                "leftMinLoc found: {}\n".format(minPosOnLeftOfPeak))
                    msg_wrapper("debug", log.debug, "setting rightMinLoc: {}\n".format(
                        minPosOnRightOfPeak))

                if localMinPositions[peakInd] > peakPosition:
                    # the position found is to the right of the assumed peak location

                    minPosOnLeftOfPeak = leftFNBWPoint
                    minPosOnRightOfPeak = localMinPositions
                    

                    flag = 7
                    lf = 1
                    msg = "Failed to locate left min pos"
                    msg_wrapper("info", log.info,msg)
                    msg_wrapper("debug", log.debug,"setting leftMinLoc: {}\n".format(minPosOnLeftOfPeak))
                    msg_wrapper("debug", log.debug,"rightMinLoc found: {}\n".format(
                        minPosOnRightOfPeak))

            elif peakInd < len(localMinPositions):
                msg_wrapper("debug", log.debug, f'peak ind < local min pos: {peakInd} < {len(localMinPositions)}; i.e. one peak, 2 or more local mins' )
                
                if (localMinPositions[peakInd] < peakPosition) or (localMinPositions[peakInd] > peakPosition):
                    
                    # grab all the local min positions to the left and right of the peak
                    minPosOnLeftOfPeak = localMinPositions[:peakInd]
                    minPosOnRightOfPeak = localMinPositions[peakInd:]
        
                    msg_wrapper("debug", log.debug,f"all leftMinLoc: {minPosOnLeftOfPeak}")
                    msg_wrapper("debug", log.debug,f"all rightMinLoc: {minPosOnRightOfPeak}")

                    if len(minPosOnLeftOfPeak) == 0:
                        # there are no left min positons, set left min to fnbw point
                        minPosOnLeftOfPeak = leftFNBWPoint
                        flag = 7
                        lf = 1
                        msg = "Failed to locate left min pos"
                        msg_wrapper("info", log.info, msg)

                    if len(minPosOnRightOfPeak) == 0:
                        # there are no right min positions, set right min to fnbw point
                        minPosOnRightOfPeak = rightFNBWPoint
                        flag = 6
                        rf = 1
                        msg = "Failed to locate right min pos"
                        msg_wrapper("info", log.info, msg)
                
            else:
                
                if localMinPositions[peakInd-1] < peakPosition:
                    # can't find local mins beyond peak

                    minPosOnLeftOfPeak = localMinPositions[:peakInd]
                    minPosOnRightOfPeak = rightFNBWPoint
                    

                    flag = 6
                    rf = 1
                    msg = "Failed to locate right min pos"
                    print(msg)
                    msg_wrapper("info", log.info,msg)
                    msg_wrapper("debug", log.debug,"leftMinLoc: {}\n".format(minPosOnLeftOfPeak))
                    msg_wrapper("debug", log.debug,"rightMinLoc: {}\n".format(
                        minPosOnRightOfPeak))

                if localMinPositions[0] > peakPosition:
                    # all local mins are beyond peak

                    minPosOnLeftOfPeak = leftFNBWPoint
                    minPosOnRightOfPeak = localMinPositions
                    

                    flag = 7
                    lf = 1
                    msg = "Failed to locate left min pos"
                    msg_wrapper("info", log.info,msg)
                    msg_wrapper("debug", log.debug,
                                "setting leftMinLocs : {}\n".format(minPosOnLeftOfPeak))
                    msg_wrapper("debug", log.debug, "rightMinLoc beyond peak: {}\n".format(
                        minPosOnRightOfPeak))

            # Determine if data has large sidelobes by evaluating the region
            # around the center peak
            maxPosInMaxs = localMaxPositions[np.abs(localMaxPositions-peakPosition).argmin()]
            indOfmaxPosInMaxs = np.where(localMaxPositions == maxPosInMaxs)[0]

            msg_wrapper("debug", log.debug, "\n")
            msg_wrapper("debug", log.debug, "-"*20)
            msg_wrapper("debug", log.debug, "Searching for sidelobes")
            msg_wrapper("debug", log.debug, "-"*20)
            
            msg_wrapper("debug", log.debug, f"local max positions: {localMaxPositions}")
            msg_wrapper("debug", log.debug, f"maxPosInMaxs: {maxPosInMaxs}")
            msg_wrapper("debug", log.debug, f"IndexOfMaxPos: {indOfmaxPosInMaxs}")
            msg_wrapper("debug", log.debug, f"lenmaxpos: {len(localMaxPositions)} ")

            sidelobes = 0  # data contains no sidelobes
            

            if len(localMaxPositions) > 1:
                # theres more than one peak
                if len(localMaxPositions) == indOfmaxPosInMaxs[0]:
                    leftSidelobe = localMaxPositions[indOfmaxPosInMaxs[0]-1]
                    rightSidelobe = localMaxPositions[indOfmaxPosInMaxs[0]]
                else:
                    if indOfmaxPosInMaxs == len(localMaxPositions)-1:
                        leftSidelobe = localMaxPositions[indOfmaxPosInMaxs[0]-1]
                        rightSidelobe = []
                    else:
                        leftSidelobe = localMaxPositions[indOfmaxPosInMaxs[0]-1]
                        rightSidelobe = localMaxPositions[indOfmaxPosInMaxs[0]+1]

                maxPeakInSpline = yspl[maxPosInMaxs]
                halfOfMaxPeakInSpline = 0.5*maxPeakInSpline

                # check if sidelobes are larger than half the peak
                if (yspl[leftSidelobe] >= halfOfMaxPeakInSpline) or (yspl[rightSidelobe] >= halfOfMaxPeakInSpline):

                    # large sidelobes detected
                    msg_wrapper("info", log.info, "Large sidelobes detected: {} < {} < {}".format(
                        yspl[leftSidelobe], maxPeakInSpline, yspl[rightSidelobe]))
                    sidelobes = 1
                    msg = "Large sidelobes detected"
                    flag = 9
                else:
                    msg_wrapper("info", log.info, "No sidelobes detected, moving on")


            elif len(localMaxPositions) == 1:
                msg_wrapper("info", log.info, "Passed sidelobe check: No sidelobes detected\n")
            else:
                msg_wrapper("info", log.info, "\nFailed to locate a maximum")
                sys.exit()

            maxloc = np.where(yspl==max(yspl))[0]
            #print(maxloc,maxloc[0],len(yspl),yspl[0],yspl[-1])
            
            # Make sure peak lies within FNBW window or points
            if maxloc[0] < leftFNBWPoint or maxloc[0]> rightFNBWPoint:
                # found peak in noise
                msg_wrapper("info", log.info,"peak found in baselocs")
                # sys.exit()
                msg = "peak found in baselocs"
                flag = 16

                # we have sidelobes
                # find local min positions ----------------------------------------
                locminpos = (np.diff(np.sign(np.diff(yspl))) > 0).nonzero()[0] + 1
                baseLine, leftBaselineBlock, rightBaselineBlock, minPosOnLeftOfPeak, minPosOnRightOfPeak, lp, rp = get_base(
                    locminpos,int((scanLen*.05)/2), len(x))
                    #locminpos, int((scanLen*.05)/2), len(x)), # why 5% ???
                # ----------------------------------------------------------------

                #print(lp, rp)

                # pl.plot(x,y)
                # pl.plot(x,yspl)
                # pl.plot(x[leftBaselineBlock], y[leftBaselineBlock], 'b.')
                # pl.plot(x[rightBaselineBlock],y[rightBaselineBlock],'m.')
                # pl.plot(x[lp], y[lp], 'k.')
                # pl.plot(x[rp],y[rp],'k*')
                # pl.plot(x[minPosOnLeftOfPeak],yspl[minPosOnLeftOfPeak],"y*")
                # pl.plot(x[minPosOnRightOfPeak], yspl[minPosOnRightOfPeak], "r*")
                # pl.show()
                # pl.close()
                # sys.exit()
                sidelobes=1
                #sys.exit()
                return baseLine, leftBaselineBlock, rightBaselineBlock, sidelobes, flag, msg, minPosOnLeftOfPeak, minPosOnRightOfPeak,lp,rp
                #return [],[],[],1,flag,msg,[],[],0,0

            else:

                # Check if you returned anything: sanity check
                try:
                    type(minPosOnRightOfPeak)
                    # check you are returned something, dummy check
        
                except:
                    flag=6
                    msg="Failed to locate right min pos"
                    msg_wrapper("info", log.info, msg)
                    return [], [], [], np.nan, flag, msg, np.nan, np.nan, [], []

                try:
                    # check you are returned something, dummy check
                    type(minPosOnLeftOfPeak)
                except:
                    flag=7
                    msg="Failed to locate left min pos"
                    msg_wrapper("info", log.info, msg)
                    return [], [], [], np.nan, flag, msg, np.nan, np.nan, [], []

                # print(type(minPosOnLeftOfPeak).__name__)
                # Get the locations of the local minimum positions, if not found, return the position to be within 
                # a hundred points from both extreme ends of the data array.
                if(type(minPosOnRightOfPeak).__name__) != 'ndarray':
                    if(type(minPosOnRightOfPeak).__name__) == 'list':
                        pass
                    else:
                        try:
                            minPosOnRightOfPeak=[minPosOnRightOfPeak]
                        except:
                            minPosOnRightOfPeak = [len(x)-100]

                if(type(minPosOnLeftOfPeak).__name__) != 'ndarray':
                    if(type(minPosOnRightOfPeak).__name__) == 'list':
                        ls=[]
                        # check all values are integers
                        try:
                            for val in minPosOnLeftOfPeak:
                                # print(type(val).__name__, val)
                                if "float" in (type(val).__name__):
                                    pass
                                else:
                                    ls.append(val)
                            minPosOnLeftOfPeak=ls
                        except:
                            pass
                    else:
                        try:
                            minPosOnLeftOfPeak=[minPosOnLeftOfPeak]
                        except:
                            minPosOnLeftOfPeak = [100]

                msg_wrapper("debug", log.debug, "\n")
                msg_wrapper("debug", log.debug, "-"*20)
                msg_wrapper("info", log.info,"Getting center of baseline blocks on left and right of peak: ")
                msg_wrapper("debug", log.debug, "-"*20)

                msg_wrapper("info", log.info,f"min pos left: {x[minPosOnLeftOfPeak]} @ loc/s {minPosOnLeftOfPeak}")
                msg_wrapper("info", log.info,f"min pos right: {x[minPosOnRightOfPeak]} @ loc/s {minPosOnRightOfPeak}")
                msg_wrapper("info", log.info,f"scan length: {scanLen}")

                # Plot possible locations to fit your baseline
                saveTo=f'{saveLoc}_baselocs.png'
                plotBaselineEstimate(x, y, yspl, minPosOnLeftOfPeak, minPosOnRightOfPeak, \
                                     "left local minumums", "right local minimums", "Baseline points selection", saveTo)

                # Locate the baselines
                # the number of points to use for baseline on each side of beam
                # limited to 5% of length of the scan, this works well for 
                # situations where there are large sidelobes e.g. Jupiter, so 
                # we apply it to all scans, if fit is bad you can always use the GUI
                # to fit by hand.
                maxPointsInBaselineBlock = int(scanLen*.05)
                hMaxPointsInBaselineBlock = int(maxPointsInBaselineBlock/2)
                nums = np.arange(1, scanLen, 1)  # array of numbers from 1 to len(list)

                # set left and right baseline points placeholders
                lb=[]
                rb=[]

                # Get baseline block on left of beam
                msg_wrapper("debug", log.debug, "\n")
                msg_wrapper("debug", log.debug, "-"*20)
                msg_wrapper("debug", log.debug,"Get baseline block on left of beam")
                msg_wrapper("debug", log.debug, "-"*20)
                if type(minPosOnLeftOfPeak).__name__ == "int64":

                    if lf == 1:
                        # left is faulty, set baseline points to half of the 5% limit
                        leftBaselineBlock = np.arange(0, minPosOnLeftOfPeak-hMaxPointsInBaselineBlock, 1)
                        lb = lb+[0, minPosOnLeftOfPeak-hMaxPointsInBaselineBlock]

                    else:
                        leftBaselineBlock = np.arange(
                            minPosOnLeftOfPeak-hMaxPointsInBaselineBlock, minPosOnLeftOfPeak+hMaxPointsInBaselineBlock, 1)
                        lb = lb+[minPosOnLeftOfPeak-hMaxPointsInBaselineBlock, minPosOnLeftOfPeak+hMaxPointsInBaselineBlock]

                        if minPosOnLeftOfPeak < len(leftBaselineBlock):
                            # min pos left is too close to the edge, adjust accordingly
                            leftBaselineBlock = np.arange(0, len(leftBaselineBlock), 1)
                            lb = lb+[0, len(leftBaselineBlock)]
                            msg_wrapper("debug", log.debug,f"mix: {leftBaselineBlock}")
                            sys.exit()
                else:

                    leftBaselineBlock = []
                    slots = []
                
                    if lf == 0: # left not faulty
                        for i in range(len(minPosOnLeftOfPeak)):
                            slots = (np.arange(
                                minPosOnLeftOfPeak[i]-hMaxPointsInBaselineBlock, minPosOnLeftOfPeak[i]+hMaxPointsInBaselineBlock, 1))
                            lb = lb+[minPosOnLeftOfPeak[i]-hMaxPointsInBaselineBlock,
                                    minPosOnLeftOfPeak[i]+hMaxPointsInBaselineBlock]
                            for j in range(len(slots)):
                                leftBaselineBlock.append(slots[j])
                    else:
                        # struggled to find left base so use all data to fnbw point
                        if len(minPosOnLeftOfPeak)==1:
                            leftBaselineBlock = np.arange(0,minPosOnLeftOfPeak[0],1)

                        lb = lb+[0,minPosOnLeftOfPeak[0]]
                        flag=7
                        msg="-- Failed to locate left min pos"
                        msg_wrapper("debug", log.debug,msg)
                        # TODO: Think about this a little bit more, 
                
                msg_wrapper("debug", log.debug, f"lb: {lb}")
                # msg_wrapper("debug", log.debug, f"leftBaselineBlock: {leftBaselineBlock}")
                
                # Get baseline block on right of beam
                msg_wrapper("debug", log.debug, "\n")
                msg_wrapper("debug", log.debug, "-"*20)
                msg_wrapper("debug", log.debug,"Get baseline block on right of beam")
                msg_wrapper("debug", log.debug, "-"*20)
                if type(minPosOnRightOfPeak).__name__ == "int64":
                    if rf == 1:
                        flag=6
                        msg="Failed to locate right min pos"
                        rightBaselineBlock = np.arange(minPosOnRightOfPeak+hMaxPointsInBaselineBlock, scanLen, 1)
                        rb= rb+[minPosOnRightOfPeak +
                                hMaxPointsInBaselineBlock, scanLen]
                        msg_wrapper("debug", log.debug,msg)
                    else:
                        rightBaselineBlock = np.arange(minPosOnRightOfPeak-hMaxPointsInBaselineBlock, minPosOnRightOfPeak+hMaxPointsInBaselineBlock, 1)
                        rb=rb+[minPosOnRightOfPeak-hMaxPointsInBaselineBlock,
                                minPosOnRightOfPeak+hMaxPointsInBaselineBlock]
                        if (scanLen - len(rightBaselineBlock)) < minPosOnRightOfPeak:
                            # min pos right is too close to the edge, adjust accordingly
                            rightBaselineBlock = np.arange(scanLen - len(rightBaselineBlock), scanLen, 1)
                            rb= rb+[scanLen - len(rightBaselineBlock), scanLen]
                else:
                    rightBaselineBlock=[]
                    slots = []
                    #rf=[]

                    if rf == 0:
                        for i in range(len(minPosOnRightOfPeak)):
                            end=minPosOnRightOfPeak[i]+hMaxPointsInBaselineBlock
                            if end>len(x):
                                end = len(x)#-1
                            else:
                                pass

                            slots=(np.arange(
                                minPosOnRightOfPeak[i]-hMaxPointsInBaselineBlock, end-1, 1))
                            rb = rb+[minPosOnRightOfPeak[i]-hMaxPointsInBaselineBlock, end-1]
                            for j in range(len(slots)):
                                rightBaselineBlock.append(slots[j])
                    else:
                        rightBaselineBlock = np.arange(
                            scanLen-maxPointsInBaselineBlock, scanLen, 1)
                        rb = rb+[scanLen-maxPointsInBaselineBlock, scanLen-1]
                        flag = 6
                        msg = "Failed to locate right min pos"
                        msg_wrapper("debug", log.debug,msg)

               
                msg_wrapper("debug", log.debug, f"rb: {rb}")

                # ensure data makes sense
                msg_wrapper("debug", log.debug, "\n")
                msg_wrapper("debug", log.debug, "-"*20)
                msg_wrapper("debug", log.debug,"Ensure data makes sense: more sanity checks")
                msg_wrapper("debug", log.debug, "-"*20)
                
                try:
                    # find if data contains negatives and move/shift points forward

                    zeroIndex = leftBaselineBlock.index(0)
                    #print("\nzeroIndex found at index: {}".format(zeroIndex))
                    
                    # find the difference between adjacent numbers and identify
                    # where to allocate shift
                    res = np.array([leftBaselineBlock[i + 1] - leftBaselineBlock[i] for i in range(len(leftBaselineBlock)-1)])
                        
                    if len(res)>0:
                            # if more than one location for baseline is selected,
                            # determine shift and adjust accordingly
                            l = np.where(res!=1)[0]
                            #("shift parameter: ",l)
                            #print("value at shift parametera: ",leftBaselineBlock[l[0]],"\n")
                            left = leftBaselineBlock[zeroIndex:l[0]+1]
                            right = leftBaselineBlock[l[0]+1:]
                            s = np.arange(
                                leftBaselineBlock[l[0]]+1, leftBaselineBlock[l[0]]+1+zeroIndex, 1)
                            shiftedBlock = left+list(s)+right #np.arange(0, shift,1)
                            #print("shiftedleftbaselineblock: ", shiftedBlock)
                            leftBaselineBlock = shiftedBlock
                            msg_wrapper("debug", log.debug, "Shifted baseline block")
                    else:
                        pass
                except Exception:
                    pass

                try:
                    # find if data contains goes beyond max of scan 
                    # and move/shift points backwards
                    maxIndex = rightBaselineBlock.index(scanLen)
                    #print("maxIndex: {}".format(maxIndex))
            
                    # find the difference between adjacent numbers and identify
                    # where to allocate shift
                    res = np.array([rightBaselineBlock[i + 1] - rightBaselineBlock[i] for i in range(len(rightBaselineBlock)-1)])
                    #print(res)

                    if len(res)>0:
                        # if more than one location for baseline is selected,
                        # determine shift and adjust accordingly
                        l = np.where(res != 1)[0]
                        #print("shift parameter: ",l)

                        if len(l) == 0:
                            msg_wrapper("debug", log.debug, "Shifting entire block")
                            
                            last = rightBaselineBlock[-1]
                            shift =abs(scanLen-last)
                            shiftedBlock = np.arange(
                                rightBaselineBlock[0]-shift, scanLen, 1)
                            #print("shiftedrightbaselineblock: ", shiftedBlock)
                            rightBaselineBlock = shiftedBlock

                        else:
                            #print("value at shift parameterb: ",
                            #    rightBaselineBlock[l[0]], "\n")
                            msg_wrapper("debug", log.debug, "Shifting block")

                            if len(l)==1:
                                left = rightBaselineBlock[:l[0]+1]
                                right = rightBaselineBlock[l[0]+1:]
                                shift = abs(rightBaselineBlock[-1]-scanLen)
                                s = np.arange(
                                    rightBaselineBlock[l[0]+1]-shift, rightBaselineBlock[-1]-shift, 1)
                                shiftedBlock = left+list(s)
                                #print("shiftedrightbaselineblock: ", shiftedBlock)
                                rightBaselineBlock = shiftedBlock

                            elif len(l)==2:
                                #print("Length l > 1")
                                
                                # find value closest to max
                                nearest = min(l, key=lambda t: abs(t-maxIndex))
                                index=[np.where(l==nearest)[0]][0]
                                #print(nearest,index[0])
                                #print("value at shift parameter: ",
                                #    rightBaselineBlock[nearest], "\n")
                                # shift backwards
                                left = rightBaselineBlock[:nearest+1]
                                right = rightBaselineBlock[nearest+1:]
                                #print("left: ", left)
                                #print("right: ", right)
                                shift = abs(rightBaselineBlock[-1]-scanLen)
                                #print("shifting back by: ", shift)
                                s = np.arange(
                                    rightBaselineBlock[nearest+1]-shift, rightBaselineBlock[-1]-shift, 1)
                                shiftedBlock = left+list(s)
                                #print("shiftedrightbaselineblock: ", shiftedBlock)
                                rightBaselineBlock = shiftedBlock

                            else:
                                #print("l > 2")
                                msg = "Too many shift parameters."
                                flag=18
                                msg_wrapper("debug", log.debug, f"Too many shift parameters: Peak limit left: {peakLocMinLimit}, Peak position: {peakPosition}, Peak limit right: {peakLocMaxLimit}")
                                sys.exit()
                                return [],[],[],1,flag,msg,np.nan    
                except Exception:
                    pass

                # msg_wrapper("debug", log.debug, f"lb: {lb}")
                # msg_wrapper("debug", log.debug, f"rb: {rb}")
                # print(len(x),len(y),len(yspl))
                # print(leftBaselineBlock)
                # print(rightBaselineBlock)
                
                saveTo=f'{saveLoc}_baselocsOutline.png'
                plotBaselineEstimate(x, y, yspl, lb, rb,'baselocs at left of beam','baselocs at rigth of beam',\
                                     "Plot with baseline blocks outlined", saveTo, leftBaselineBlock, rightBaselineBlock)

                
                # create a single baseline block
                baseLine = list(leftBaselineBlock) + list(rightBaselineBlock)
                baseLine = np.array(baseLine, int)

                return baseLine, leftBaselineBlock, rightBaselineBlock, sidelobes, flag, msg, minPosOnLeftOfPeak, minPosOnRightOfPeak,lb,rb

def correct_drift(xBase, yBase, x, log, order=1):
    '''
        Correct for a drifting baseline in the scan by fitting
        a first order polynomial to a region with no
        signal.	

        Parameters
        -----------
            xBase : x data of the baseline
            yBase : y data of the baseline
            x : x data of the entire drift scan
    '''

    # fit the baseline and get best fit coeffecients
    driftModel, driftRes, driftRms, driftCoeffs = calc_residual_and_rms(
        xBase, yBase,log, order)
    dataModel = np.polyval(driftCoeffs, x)

    
    msg_wrapper("info", log.info, "\n")
    msg_wrapper("info", log.info, "-"*30)
    msg_wrapper("info", log.info, "Fit the baseline")
    msg_wrapper("info", log.info,"-"*30)
    msg = "Fit = {:.3}x + ({:.3}), rms error = {:.3}".format(driftCoeffs[0], driftCoeffs[1], driftRms)
    msg_wrapper("info", log.info, msg)

    return dataModel, driftModel, driftRes, driftRms, driftCoeffs

def calc_residual_and_rms(x, y, log, order=1):
    """Calculate the residual and rms from data
    
        Args:
            x (array): 1d array
            data representing the x-axis
            y (array): 1d array
                data representing the y-axis
            deg(int): degree of the polynomial

        Return:
            model (array): model of 
            res (array):
            rms (float):
            coeff():
        """
    #TODO: remove redundant code
    
    # fit the baseline and get best fit coeffecients
    coeffs = poly_coeff(x, y, order)

    msg_wrapper("debug",log.debug,f'coeffs: {coeffs}')

    # get a model for the fit using the best fit coeffecients
    model = np.polyval(coeffs, x)

    # Calculate the residual and rms
    res, rms = calc_residual(y, model)

    return model, res, rms, coeffs

def calc_residual_and_rms_fit(x,y,order=1):
    """Calculate the residual and rms from data
    
        Args:
            x (array): 1d array
            data representing the x-axis
            y (array): 1d array
                data representing the y-axis
            deg(int): degree of the polynomial

        Return:
            model (array): model of 
            res (array):
            rms (float):
            coeff():
        """
    #TODO: remove redundant code
    
    nx=[]
    ny=[]
    # remove nan values
    for i in range(len(x)):
        #print(i,y[i],type(y[i]))
        if y[i] == np.nan or str(y[i]) =="nan":
            #print(i,y[i])
            pass
        else:
            nx.append(x[i])
            ny.append(y[i])

    # fit the baseline and get best fit coeffecients
    coeffs = poly_coeff(nx, ny, order)

    print('coeffs: ',coeffs)

    # get a model for the fit using the best fit coeffecients
    model = np.polyval(coeffs, nx)

    #print('model: ', model)

    # Calculate the residual and rms
    res, rms = calc_residual(ny, model)

    return nx, model, res, rms, coeffs
    
def poly_coeff(x, y, deg):
    '''
        Calculate the polynomial coeffecients depending 
        on the degree/order of the polynomial

        Args:
            x (array): 1d array
                data representing the x-axis
            y (array): 1d array
                data representing the y-axis
            deg(int): degree of the polynomial

        Return:
            array of polynomial fitted data
    '''

    return np.polyfit(x, y, deg)

def fit_beam(x, y, p, fnbw, force, log, saveTag, fitTheoretical, autoFit=None):
    """
        Fit single beam data.

        Parameters:
            x (array): 1D array of data representing the x-axis
            y (array): 1D array of data representing the y-axis
            p (list): list of initial fit parameters
            fnbw (float): source first null beam width from file
            dec (float): source declination
            data (dict): dictionary of source parameters
            scanNum (int):  Value representing the current scan
            force (str): String to determine whether to force a fit or not   
            log (object): loffing object
    """

    # Setup parameters
    scanLen = len(x)                # length of the scan
    hhpbw = p[2]/2                  # half of the hpbw
    hfnbw = fnbw/2                  # half of the fnbw
    flag = 0                        # default flag set to zero
    msg = ""                          # flag message to go on plot

    # Try to fit a gaussian to determine peak location
    # this also works as a bad scan filter
    coeff, fit, flag = test_gauss_fit(x, y, p,log)
    if len(coeff)==0:
        if force=="y":
            pass
        else:
            # return np.nan, [], np.nan, [], [], msg, [], [], [], [], np.nan, flag, [], [], [],np.nan,0,0
            return {"peakFit":np.nan,"peakModel":[],"peakRms":np.nan,"correctedData":[],"peakPts":[],"msg":msg,
                        "driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,"flag":flag,
                        "baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":np.nan,"baseLeft":[],
                        "baseRight":[]}

    if autoFit !=None and len(autoFit)>1:
        # If given fitting points 
        #------------------------
        
        #print(autoFit, autoFit['baselocs'])

        #print(float(autoFit['baselocs']))
        # fit baseline
        # 2) correct the drift in the data and get the residual and rms
        baseLocs=[]#np.where()[0]

        # print(autoFit)
        # sys.exit()
        for i in range(len(autoFit['baselocs'])):
            if i%2==0:
                #print(autoFit['baselocs'][i],autoFit['baselocs'][i+1])
                if i==0:
                    baseLocsl=np.where((x>=autoFit['baselocs'][i]) & (x<=autoFit['baselocs'][i+1]))[0]
                else:
                    baseLocsr=np.where((x>=autoFit['baselocs'][i]) & (x<=autoFit['baselocs'][i+1]))[0]

                d=np.where((x>=autoFit['baselocs'][i]) & (x<=autoFit['baselocs'][i+1]))[0]
                baseLocs=baseLocs+list(d)

        #print(baseLocs)
        #baseLocsl=x[b1]
        #baseLocsr=x[b2]
        lb=[baseLocsl[0],baseLocsl[-1]]
        rb=[baseLocsr[0],baseLocsr[-1]]
        #print(lb,rb)
        #sys.exit()
        # fit baseline blocks
        dataModel, driftModel, driftRes, driftRms, driftCoeffs = correct_drift(
            x[baseLocs], y[baseLocs], x,log)

        # 4) apply a polynomial fit to the baseline data
        lin_first_null = np.poly1d(np.polyfit(x[baseLocs], y[baseLocs], 1))

        # 5) Subtract the polynomial fitted to the baseline to get corrected beam
        yCorrected = y - lin_first_null(x)

        # 6) get sline of corrected data
        s = spline(x, yCorrected)

        plotCorrectedData(x,yCorrected,baseLocsl,baseLocsr,'Corrected data','blocks','Plot of baseline corrected data',f'{saveTo}corrected.png',xlabel="",ylabel="")
        plot_overlap(x,yCorrected,x,s,'Plot of splined data','corrected','spline fit',f'{saveTo}splined.png',xlabel="",ylabel="")
    
        # pl.title("Baseline corrected data")
        # pl.xlabel("Scandist [Deg]")
        # pl.ylabel("Ta [K]")
        # #pl.plot(x,y)
        # pl.plot(x, yCorrected, 'k',label="baseline corrected data")
        # #pl.plot(x[main_beam], yCorrected[main_beam])
        # pl.plot(x[baseLocs], yCorrected[baseLocs],".")
        # pl.plot(x[lb], yCorrected[lb],".")
        # #pl.plot(x,s)
        # pl.plot(x,np.zeros_like(x),'k')
        # #pl.grid()
        # pl.legend(loc="best")
        # try:
        #     pl.savefig(saveFolder+"baseline_corrected_data.png")
        # except:
        #     pass
        # #pl.show()
        # pl.close()
        # #sys.exit()

        # fit a polynomial to peak data

        msg_wrapper("info", log.info, "Fit the peak")
        print("*"*60)
        hmain_beam=np.where((x>=autoFit['peaklocs'][0]) & (x<=autoFit['peaklocs'][1]))[0]
        ypeak = np.polyval(np.polyfit(x[hmain_beam],
                                    yCorrected[hmain_beam],  2), x[hmain_beam])

        # get residual and rms of peak fit
        fitRes, err_peak = calc_residual(yCorrected[hmain_beam], ypeak)

        # pl.title("Plot of final peak fitted data")
        # pl.xlabel("Scandist [Deg]")
        # pl.ylabel("Ta [K]")
        # pl.plot(x, yCorrected, "k", label="corrected data")
        # #pl.plot(x[main_beam],yCorrected[main_beam])
        # pl.plot(x[hmain_beam], yCorrected[hmain_beam])
        # #pl.plot(x,fit)
        # pl.plot(x[hmain_beam],ypeak,"r",label="Ta[K] = %.3f +- %.3f" %(max(ypeak),err_peak))
        # pl.plot(x,np.zeros(scanLen),"k")
        # #pl.grid()
        # pl.legend(loc="best")
        # try:
        #     pl.savefig(saveFolder+"peak_fit_data.png")
        # except:
        #     pass
        # #pl.show()
        # pl.close()
        #sys.exit()

        # find final peak loc
        ploc = np.where(ypeak == max(ypeak))[0]
        peakLoc = (x[hmain_beam])[ploc[0]]
        
        # return max(ypeak), ypeak, err_peak, yCorrected, hmain_beam, "", driftRes, driftRms, driftCoeffs, fitRes, coeff[1], 
        # flag, baseLocsl, baseLocsr, baseLocs, peakLoc,lb,rb
        ret={
             "peakFit":max(ypeak),"peakModel":ypeak, "peakRms":err_peak,"correctedData":yCorrected,"peakPts":hmain_beam,
            "msg":"","driftRes":driftRes,"driftRms":driftRms,"driftCoeffs":driftCoeffs,"fitRes":fitRes,"midXValue":coeff[1],
            "flag":flag,"baseLocsLeft":baseLocsl,"baseLocsRight":baseLocsr,"baseLocsCombined":baseLocs,"peakLoc":peakLoc,
             "baseLeft":lb,"baseRight":rb
            }
        return ret
        sys.exit()
    else:
        # 1. Locate baseline blocks
        # These are the blocks that will be used to correct the drift in the data
        if force=="y" and flag==3:
            baseLocsl=[]
            baseLocsr=[]
        else:

            if fitTheoretical=="y":
                #baseLocs, baseLocsl, baseLocsr, sidelobes, flag, msg, minPosOnLeftOfPeak, minPosOnRightOfPeak, lb, rb = locate_baseline_blocks_auto(
                #x, y, coeff[1], hfnbw,log)
                baseLocs, baseLocsl, baseLocsr, sidelobes = locate_baseline_blocks_fnbw(
                x, hfnbw,)
                #print(baseLocsl,baseLocsr)
                flag = 26 
                msg =  "Fitting left and right theoretical (FNBW) points"
                minPosOnLeftOfPeak = baseLocsl[int(len(baseLocsl)/2)]
                minPosOnRightOfPeak = baseLocsr[int(len(baseLocsr)/2)]
                lb = [baseLocsl[0],baseLocsl[-1]]
                rb = [baseLocsr[0],baseLocsr[-1]]
                #sys.exit()

            else:
                msg_wrapper("info",log.info,"AUTO fitting started.")

                baseLocs, baseLocsl, baseLocsr, sidelobes, flag, msg, minPosOnLeftOfPeak, minPosOnRightOfPeak, lb, rb = locate_baseline_blocks_auto(
                x, y, coeff[1], hfnbw,log, saveTag)
                
                if 'int' in type(minPosOnRightOfPeak).__name__ or 'float' in type(minPosOnRightOfPeak).__name__ or len(minPosOnRightOfPeak) == 0:
                    print("Failed to locate right min pos")
                    flag=6
                    # return np.nan, [], np.nan, [], [], msg, [], [], [], [], np.nan, 6, [], [], [], np.nan,0,0
                    return {"peakFit":np.nan,"peakModel":[],"peakRms":np.nan,"correctedData":[],"peakPts":[],"msg":msg,
                        "driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,"flag":flag,
                        "baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":np.nan,"baseLeft":[],
                        "baseRight":[]}
                
                elif 'int' in type(minPosOnLeftOfPeak).__name__ or len(minPosOnLeftOfPeak) == 0:
                    print("Failed to locate left min pos")
                    flag=7
                    # return np.nan, [], np.nan, [], [], msg, [], [], [], [], np.nan, 7, [], [], [], np.nan,0,0
                    return {"peakFit":np.nan,"peakModel":[],"peakRms":np.nan,"correctedData":[],"peakPts":[],"msg":msg,
                        "driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,"flag":flag,
                        "baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":np.nan,"baseLeft":[],
                        "baseRight":[]}
                else:
                    pass

        if len(baseLocsl) == 0 or len(baseLocsr) == 0:

            # one side of the basline has could not be located possibly due to rfi
            msg = "*failed to locate base locs"
            msg_wrapper("warning", log.warning, msg)
            sys.exit()
            flag=30

            # Force the fit
            if force=="y":
                print("Forcing the fit")

                # set baseline points and fit edges or fnbw points
                #print()

                # 1. try fitting the data with the centre at 0
                baseLocs, baseLocsl, baseLocsr, sidelobes, flag, msg, minPosOnLeftOfPeak, minPosOnRightOfPeak, lb, rb = locate_baseline_blocks_auto(x, y, 0, hfnbw,log)
                msg="force fitted local mins"

                

                if len(baseLocsl) == 0 or len(baseLocsr) == 0:

                    # 2. try fitting the hfnbw points
                    baseLocsl  = (np.where(x <= (-hfnbw))[0]) 
                    baseLocsr = (np.where(x >= (hfnbw))[0])
                    baseLocs = list(baseLocsl)+list(baseLocsr)
                    msg="force fitted fnbw locs"
                sidelobes=2 #error fitting the data

                # if both methods failed, exit
                if len(baseLocsl) == 0 or len(baseLocsr) == 0:
                    # return np.nan, [], np.nan, [], [], msg, [], [], [], [], np.nan, flag, [], [], [], np.nan
                    return {"peakFit":np.nan,"peakModel":[],"peakRms":np.nan,"correctedData":[],"peakPts":[],"msg":msg,
                        "driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,"flag":flag,
                        "baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":np.nan,"baseLeft":[],
                        "baseRight":[]}

                '''pl.title("Plot of baseline corrected data")
                pl.xlabel("Scandist [Deg]")
                pl.ylabel("Ta [K]")
                #pl.plot(x,y)
                pl.plot(x, y, 'k',label="baseline corrected data")
                #pl.plot(x[main_beam], yCorrected[main_beam])
                pl.plot(x[baseLocs], y[baseLocs],".")
                pl.show()
                pl.close()
                sys.exit()'''

                # fit the baseline
                dataModel, driftModel, driftRes, driftRms, driftCoeffs = correct_drift(x[baseLocs], y[baseLocs], x,log)

                # get main beam
                try:
                    main_beam = np.where(np.logical_and(x >= coeff[1]-hfnbw, x <= coeff[1]+hfnbw))[0]
                except:
                    print("Failed to get coeff[1], setting beam to fnbw window")
                    main_beam = np.where(np.logical_and(
                        x >= hfnbw, x <= hfnbw))[0]

                # 4) apply a polynomial fit to the baseline data
                lin_first_null = np.poly1d(np.polyfit(x[baseLocs], y[baseLocs], 1))

                # 5) Subtract the polynomial fitted to the baseline to get corrected beam
                yCorrected = y - lin_first_null(x)

                # 6) get sline of corrected data
                s = spline(x, yCorrected)

                pl.title("Plot of baseline corrected data")
                pl.xlabel("Scandist [Deg]")
                pl.ylabel("Ta [K]")
                #pl.plot(x,y)
                pl.plot(x, yCorrected, 'k',label="baseline corrected data")
                #pl.plot(x[main_beam], yCorrected[main_beam])
                pl.plot(x[baseLocsl], yCorrected[baseLocsl],".")
                pl.plot(x[baseLocsr], yCorrected[baseLocsr],".")
                #pl.plot(x,s)
                pl.plot(x,np.zeros_like(x),'k')
                pl.grid()
                pl.legend(loc="best")
                try:
                    pl.savefig(saveFolder+"baseline_corrected_data.png")
                except:
                    pass
                #pl.show()
                pl.close()
                #sys.exit()

                # fit the peak
                # 3) GET LOCATIONS OF DATA FOR THE MAIN BEAM ONLY
                # this is limited by the fnbw
                # check peak is at centre
                main_beam = np.where(np.logical_and(
                    x >= -hfnbw, x <= hfnbw))[0]
                    
                # 4) apply a polynomial fit to the baseline data
                lin_first_null = np.poly1d(np.polyfit(x[baseLocs], y[baseLocs], 1))

                # 5) Subtract the polynomial fitted to the baseline to get corrected beam
                yCorrected = y - lin_first_null(x)

                # 6) get sline of corrected data
                s = spline(x, yCorrected)

                # 7. Fit the peak
                # find max location
                msg_wrapper("info", log.info, "Fit the peak")
                print("*"*60)
                maxp = max(s)
                maxloc = np.where(s == maxp)[0]
                xmaxloc = x[maxloc[0]]

                # max is not at center, found at extreme ends of scan
                if (max(s) == s[0]) or (max(s) == s[-1]):
                    msg = "max of peak is not at center, failed peak fit "
                    msg_wrapper("warning", log.warning, msg)
                    flag  = 10
                    # return np.nan, [], np.nan, [], [], msg, [], [], [], [], np.nan, flag, [], [], [],np.nan,0,0
                    return {"peakFit":np.nan,"peakModel":[],"peakRms":np.nan,"correctedData":[],"peakPts":[],"msg":msg,
                        "driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,"flag":flag,
                        "baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":np.nan,"baseLeft":[],
                        "baseRight":[]}
                else:
                    pass

                # 7) Get indices where the x values are within the main beam
                # Get top 30% of beam
                xMainBeam = x[main_beam]
                yMainBeam = s[main_beam]
                maxs = max(s[main_beam])

                loc = np.where(s[main_beam] == maxs)[0]
                midxMainBeam = xMainBeam[loc[0]]  

                # Get main beam for peak fitting
                try:
                    hmain_beamn = np.where(np.logical_and(
                        xMainBeam >= coeff[1]-hhpbw, xMainBeam <= coeff[1]+hhpbw))[0]
                except:
                    hmain_beamn = np.where(np.logical_and(
                        xMainBeam >= -hhpbw, xMainBeam <= hhpbw))[0]

                # Fit top 50% or 30% depending on sidelobe confirmation
                if sidelobes == 1:
                    hmain_beamp = np.where(yMainBeam[hmain_beamn] >= 0.5*maxp)[0]
                    flag = 9
                    msg = "large sidelobes detected"
                    msg_wrapper("warning", log.warning, msg)
                else:
                    hmain_beamp = np.where(yMainBeam[hmain_beamn] >= 0.7*maxp)[0]
                    flag = 0

                if (len(hmain_beamp) == 0) or len(hmain_beamn) ==0:
                    msg = "couldn't find peak main beam data"
                    flag=4
                    msg_wrapper("warning", log.warning, msg)

                    # find peak of spline
                    sloc = np.where(s == max(s))[0]
                    print("sloc: ", sloc, ", len: ", len(
                        yCorrected), ", mid: ", len(yCorrected)/2)

                    #print(data)
                    pl.title("Baseline corrected data")
                    pl.xlabel("Scandist [Deg]")
                    pl.ylabel("Ta [K]")
                    pl.plot(x,y)
                    pl.plot(x, yCorrected, 'k',label="baseline corrected data")
                    pl.plot(x[main_beam], yCorrected[main_beam])
                    pl.plot(x[baseLocsl], yCorrected[baseLocsl],".")
                    pl.plot(x[baseLocsr], yCorrected[baseLocsr],".")
                    #pl.plot(x,s)
                    pl.plot(x,np.zeros_like(x),'k')
                    #pl.grid()
                    pl.legend(loc="best")
                    #pl.savefig(saveFolder+"baseline_corrected_data.png")
                    pl.show()
                    pl.close()

                    sys.exit()
                    
                    # peak shifted left
                    if sloc < len(yCorrected)/2 and sloc != 0:
                        print("Peak is shifted to left, but not first element")
                        print(x[sloc], hhpbw)

                        # look for peak around new max loc
                        beam = np.where(np.logical_and(
                            x >= x[sloc]-hhpbw, x <= x[sloc]+hhpbw))[0]

                        # fit peak
                        if len(beam) > 0:
                            ypeak = np.polyval(np.polyfit(
                                    x[beam], yCorrected[beam],  2), x[beam])

                            # get residual and rms of peak fit
                            fitRes, err_peak = calc_residual(
                                    yCorrected[beam], ypeak)

                            # find final peak loc
                            ploc = np.where(ypeak == max(ypeak))[0]
                            peakLoc = (x[beam])[ploc[0]]
                            # return max(ypeak), ypeak, err_peak, yCorrected, beam, msg, driftRes, driftRms, driftCoeffs, fitRes, 
                            # np.nan, flag, baseLocsl, baseLocsr, baseLocs, peakLoc
                            ret={"peakFit":max(ypeak),"peakModel":ypeak, "peakRms":err_peak,"correctedData":yCorrected,"peakPts":beam,
                                "msg":"","driftRes":driftRes,"driftRms":driftRms,"driftCoeffs":driftCoeffs,"fitRes":fitRes,"midXValue":np.nan,
                                "flag":flag,"baseLocsLeft":baseLocsl,"baseLocsRight":baseLocsr,"baseLocsCombined":baseLocs,"peakLoc":peakLoc,
                                "baseLeft":[],"baseRight":[]
                            }
                            return ret
                        else:
                            # couldn't locate peak
                            # return np.nan, [], np.nan, [], [], msg, [], [], [], [], np.nan, flag, [], [], [], np.nan,0,0
                            return {"peakFit":np.nan,"peakModel":[],"peakRms":np.nan,"correctedData":[],"peakPts":[],"msg":msg,
                                "driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,"flag":flag,
                                "baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":np.nan,"baseLeft":[],
                                "baseRight":[]}

                    else:
                        # peak shifted right

                        print("Peak is shifted to left, but not first element")
                        print(x[sloc], hhpbw)

                        # look for peak around new max loc
                        beam = np.where(np.logical_and(
                            x >= x[sloc]-hhpbw, x <= x[sloc]+hhpbw))[0]

                        # fit peak
                        if len(beam) > 0:
                            ypeak = np.polyval(np.polyfit(
                                    x[beam], yCorrected[beam],  2), x[beam])

                            # get residual and rms of peak fit
                            fitRes, err_peak = calc_residual(
                                    yCorrected[beam], ypeak)

                            # find final peak loc
                            ploc = np.where(ypeak == max(ypeak))[0]
                            peakLoc = (x[beam])[ploc[0]]

                            #sys.exit()
                            # return max(ypeak), ypeak, err_peak, yCorrected, beam, msg, driftRes, driftRms, driftCoeffs, fitRes, np.nan, 
                            # flag, baseLocsl, baseLocsr, baseLocs, peakLoc
                            return {"peakFit":max(ypeak),"peakModel":ypeak, "peakRms":err_peak,"correctedData":yCorrected,"peakPts":beam,
                                "msg":"","driftRes":driftRes,"driftRms":driftRms,"driftCoeffs":driftCoeffs,"fitRes":fitRes,"midXValue":np.nan,
                                "flag":flag,"baseLocsLeft":baseLocsl,"baseLocsRight":baseLocsr,"baseLocsCombined":baseLocs,"peakLoc":peakLoc,
                                "baseLeft":[],"baseRight":[]
                            }
                        
                    # return np.nan, [], np.nan, [], [], msg, [], [], [], [], np.nan, flag, [], [], [],np.nan
                    return {"peakFit":np.nan,"peakModel":[],"peakRms":np.nan,"correctedData":[],"peakPts":[],"msg":msg,
                        "driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,"flag":flag,
                        "baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":np.nan,"baseLeft":[],
                        "baseRight":[]}
                
                hmain_beam = hmain_beamp + hmain_beamn[0]+main_beam[0]

                if hmain_beam[0] > baseLocsr[-1] or hmain_beam[-1] < baseLocsl[0]:
                    # peak loctaion is beyond fnbw locations
                    msg = "peak location is beyond fnbw locations"
                    msg_wrapper("warning", log.warning, msg)
                    flag = 24
                    # return np.nan, [], np.nan, [], [], msg, [], [], [], [], np.nan, flag, [], [], [],np.nan
                    return {"peakFit":np.nan,"peakModel":[],"peakRms":np.nan,"correctedData":[],"peakPts":[],"msg":msg,
                        "driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,"flag":flag,
                        "baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":np.nan,"baseLeft":[],
                        "baseRight":[]}

                # fit a polynomial to peak data
                ypeak = np.polyval(np.polyfit(x[hmain_beam],
                                            yCorrected[hmain_beam],  2), x[hmain_beam])

                # check if peak was fit correctly
                if max(ypeak) == ypeak[0] or max(ypeak) == ypeak[-1]:
                    # peak is concave, try fitting wider range
                    hmain_beamp = np.where(yMainBeam[hmain_beamn] >= 0.5*maxp)[0]
                    hmain_beam = hmain_beamp + hmain_beamn[0]+main_beam[0]
                    ypeak = np.polyval(np.polyfit(x[hmain_beam],
                                                yCorrected[hmain_beam],  2), x[hmain_beam])

                    if (max(ypeak) == ypeak[0]) or (max(ypeak) == ypeak[-1]):
                        # still struggling to fit ?, stop fitting
                        msg = "failed to accurately establish peak fit location, 1"
                        msg_wrapper("warning", log.warning, msg)
                        flag = 5

                        pl.title("Plot of baseline corrected data")
                        pl.xlabel("Scandist [Deg]")
                        pl.ylabel("Ta [K]")
                        #pl.plot(x,y)
                        pl.plot(x, yCorrected, 'k',label="baseline corrected data")
                        pl.plot(x,s)
                        pl.plot(x[hmain_beamp], yCorrected[hmain_beamp],label=msg)
                        pl.plot(x[baseLocsl], yCorrected[baseLocsl],".")
                        pl.plot(x[baseLocsr], yCorrected[baseLocsr],".")
                        #pl.plot(x,s)
                        pl.plot(x,np.zeros_like(x),'k')
                        pl.grid()
                        pl.legend(loc="best")
                        #pl.savefig(saveFolder+"baseline_corrected_data.png")
                        #pl.show()
                        pl.close()
                        #sys.exit()
                        
                        # find peak of spline
                        sloc = np.where(s==max(s))[0]
                        print("sloc: ",sloc,", len: ", len(yCorrected),", mid: ",len(yCorrected)/2)

                        # peak shifted left
                        if sloc < len(yCorrected)/2 and sloc!=0:
                            print("Peak is shifted to left, but not first element")
                            print(x[sloc],hhpbw)

                            # look for peak around new max loc
                            beam = np.where(np.logical_and(
                                x >= x[sloc]-hhpbw, x <= x[sloc]+hhpbw))[0]

                            # fit peak
                            if len(beam) > 0:
                                ypeak = np.polyval(np.polyfit(
                                    x[beam], yCorrected[beam],  2), x[beam])

                                # get residual and rms of peak fit
                                fitRes, err_peak = calc_residual(yCorrected[beam], ypeak)

                                # find final peak loc
                                ploc = np.where(ypeak == max(ypeak))[0]
                                peakLoc = (x[beam])[ploc[0]]
                                

                                # return max(ypeak), ypeak, err_peak, yCorrected, beam, msg, driftRes, driftRms, driftCoeffs, fitRes, np.nan, 
                                # flag, baseLocsl, baseLocsr, baseLocs,peakLoc
                                return {
                                    "peakFit":max(ypeak),"peakModel":ypeak, "peakRms":err_peak,"correctedData":yCorrected,"peakPts":beam,
                                    "msg":"","driftRes":driftRes,"driftRms":driftRms,"driftCoeffs":driftCoeffs,"fitRes":fitRes,"midXValue":np.nan,
                                    "flag":flag,"baseLocsLeft":baseLocsl,"baseLocsRight":baseLocsr,"baseLocsCombined":baseLocs,"peakLoc":peakLoc,
                                    "baseLeft":[],"baseRight":[],
                                }
                            else:
                                # couldn't locate peak
                                # return np.nan, [], np.nan, [], [], msg, [], [], [], [], np.nan, flag, [], [], [],np.nan
                                return {"peakFit":np.nan,"peakModel":[],"peakRms":np.nan,"correctedData":[],"peakPts":[],"msg":msg,
                                    "driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,"flag":flag,
                                    "baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":np.nan,"baseLeft":[],
                                    "baseRight":[]}

                        sys.exit()
                        # return np.nan, [], np.nan, [], [], msg, [], [], [], [], np.nan, flag, [], [], [],np.nan
                        return {"peakFit":np.nan,"peakModel":[],"peakRms":np.nan,"correctedData":[],"peakPts":[],"msg":msg,
                            "driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,"flag":flag,
                            "baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":np.nan,"baseLeft":[],
                            "baseRight":[]}

                # get residual and rms of peak fit
                fitRes, err_peak = calc_residual(yCorrected[hmain_beam], ypeak)

                # find final peak loc
                ploc = np.where(ypeak == max(ypeak))[0]
                peakLoc = (x[hmain_beam])[ploc[0]]
                
                # return max(ypeak), ypeak, err_peak, yCorrected, hmain_beam, "", driftRes, driftRms, driftCoeffs, fitRes, np.nan, 
                # flag, baseLocsl, baseLocsr, baseLocs,peakLoc
                return {
                        "peakFit":max(ypeak),"peakModel":ypeak, "peakRms":err_peak,"correctedData":yCorrected,"peakPts":hmain_beam,
                        "msg":"","driftRes":driftRes,"driftRms":driftRms,"driftCoeffs":driftCoeffs,"fitRes":fitRes,"midXValue":np.nan,
                        "flag":flag,"baseLocsLeft":baseLocsl,"baseLocsRight":baseLocsr,"baseLocsCombined":baseLocs,"peakLoc":peakLoc,
                        "baseLeft":[],"baseRight":[]
                    }
            else:
                flag = 37
                # return np.nan, [], np.nan, [], [], msg, [], [], [], [], np.nan, flag, [], [], [],np.nan,0,0
                return {"peakFit":np.nan,"peakModel":[],"peakRms":np.nan,"correctedData":[],"peakPts":[],"msg":msg,
                        "driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,"flag":flag,
                        "baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":np.nan,"baseLeft":[],
                        "baseRight":[]}
        else:
            pass

        # 2) correct the drift in the data and get the residual and rms
        dataModel, driftModel, driftRes, driftRms, driftCoeffs = correct_drift(
            x[baseLocs], y[baseLocs], x,log)

        # 3) GET LOCATIONS OF DATA FOR THE MAIN BEAM ONLY
        # this is limited by the fnbw
        # check peak is at centre
        main_beam = np.where(np.logical_and(
            x >= coeff[1]-hfnbw, x <= coeff[1]+hfnbw))[0]
        lin_first_null = np.poly1d(np.polyfit(x[baseLocs], y[baseLocs], 1)) # 4) apply a polynomial fit to the baseline data
        yCorrected = y - lin_first_null(x) # 5) Subtract the polynomial fitted to the baseline to get corrected beam
        s = spline(x, yCorrected) # 6) get spline of corrected data

        saveTo=f'{saveTag}corrected.png'
        plotCorrectedData(x,yCorrected,baseLocsl,baseLocsr,"baseline corrected data",'baseLocs','Plot of corrected data',saveTo)

        # 7. Fit the peak
        # find max location
        msg_wrapper("info", log.info, "\n")
        msg_wrapper("info", log.info, "-"*30)
        msg_wrapper("info", log.info, "Fit the peak")
        msg_wrapper("info", log.info,"-"*30)
        maxp = max(s)
        maxloc = np.where(s == maxp)[0]
        # xmaxloc = x[maxloc[0]]

        # max is not at center, found at extreme ends of scan
        if (max(s) == s[0]) or (max(s) == s[-1]):
            msg = "max of peak is not at center, failed peak fit "
            msg_wrapper("warning", log.warning, msg)
            flag  = 10
            # return np.nan, [], np.nan, [], [], msg, [], [], [], [], np.nan, flag, [], [], [],np.nan,0,0
            return {"peakFit":np.nan,"peakModel":[],"peakRms":np.nan,"correctedData":[],"peakPts":[],"msg":msg,
                        "driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,"flag":flag,
                        "baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":np.nan,"baseLeft":[],
                        "baseRight":[]}
        else:
            pass

        # 7) Get indices where the x values are within the main beam
        # Get top 30% of beam
        xMainBeam = x[main_beam]
        yMainBeam = s[main_beam]
    
        try:
            maxs = max(s[main_beam])
        except:
            msg = "max of peak is not at center, failed peak fit "
            msg_wrapper("warning", log.warning, msg)
            flag  = 10
            # return np.nan, [], np.nan, [], [], msg, [], [], [], [], np.nan, flag, [], [], [],np.nan,0,0
            return {"peakFit":np.nan,"peakModel":[],"peakRms":np.nan,"correctedData":[],"peakPts":[],"msg":msg,
                        "driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,"flag":flag,
                        "baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":np.nan,"baseLeft":[],
                        "baseRight":[]}
            
        loc = np.where(s[main_beam] == maxs)[0]
        midxMainBeam = xMainBeam[loc[0]]  

        # Try to fit a gaussian to confirm center peak location after correction of scan
        try:
            p0=[maxs, midxMainBeam, p[2], 0, 0]
            coeff, covarMatrix = curve_fit(gauss_lin, x,yCorrected, p0)
            fit = gauss_lin(x, *coeff)
            # coeff, fit = fit_gauss_lin(
            #     x, yCorrected, [maxs, midxMainBeam, p[2], 0, 0])
        except Exception:
            msg = "couldnt find max in main beam"
            msg_wrapper("warning", log.warning, msg)
            flag = 11
            # return np.nan, [], np.nan, [], [], msg, [], [], [], [], np.nan, flag, [], [], [],np.nan,0,0
            return {"peakFit":np.nan,"peakModel":[],"peakRms":np.nan,"correctedData":[],"peakPts":[],"msg":msg,
                        "driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,"flag":flag,
                        "baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":np.nan,"baseLeft":[],
                        "baseRight":[]}

        # Get main beam for peak fitting
        hmain_beamn = np.where(np.logical_and(
            xMainBeam >= coeff[1]-hhpbw, xMainBeam <= coeff[1]+hhpbw))[0]

        # Fit top 50% or 30% depending on sidelobe confirmation
        if sidelobes == 1:
            hmain_beamp = np.where(yMainBeam[hmain_beamn] >= 0.5*maxp)[0]
            flag = 9
            msg_wrapper("warning", log.warning, "large sidelobes detected")
        else:
            hmain_beamp = np.where(yMainBeam[hmain_beamn] >= 0.7*maxp)[0]
            flag = 0

        if (len(hmain_beamp) == 0) or len(hmain_beamn) ==0:
            msg = "couldn't find peak main beam data"
            flag=4
            msg_wrapper("warning", log.warning, msg)
            # sys.exit()
            #print(data)
            # pl.title("Baseline corrected data")
            # pl.xlabel("Scandist [Deg]")
            # pl.ylabel("Ta [K]")
            # pl.plot(x,y)
            # #pl.plot(x, yCorrected, 'k',label="baseline corrected data")
            # pl.plot(x[main_beam], yCorrected[main_beam])
            # pl.plot(x[baseLocsl], yCorrected[baseLocsl],".")
            # pl.plot(x[baseLocsr], yCorrected[baseLocsr],".")
            # #pl.plot(x,s)
            # pl.plot(x,np.zeros_like(x),'k')
            # #pl.grid()
            # pl.legend(loc="best")
            # #pl.savefig(saveFolder+"baseline_corrected_data.png")
            # #pl.show()
            # pl.close()
            # #sys.exit()
            # #sys.exit()
            
            # return np.nan, [], np.nan, [], [], msg, [], [], [], [], np.nan, flag, [], [], [], np.nan,0,0
            return {"peakFit":np.nan,"peakModel":[],"peakRms":np.nan,"correctedData":[],"peakPts":[],"msg":msg,
                        "driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,"flag":flag,
                        "baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":np.nan,"baseLeft":[],
                        "baseRight":[]}
        
        if (len(hmain_beamp) < 0.5*len(hmain_beamn)):
            msg = "peak main beam data too noisy"
            flag = 23
            msg_wrapper("warning", log.warning, msg)
            # sys.exit()
            # return np.nan, [], np.nan, [], [], msg, [], [], [], [], np.nan, flag, [], [], [],np.nan,0,0
            return {"peakFit":np.nan,"peakModel":[],"peakRms":np.nan,"correctedData":[],"peakPts":[],"msg":msg,
                        "driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,"flag":flag,
                        "baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":np.nan,"baseLeft":[],
                        "baseRight":[]}
        
        hmain_beam = hmain_beamp + hmain_beamn[0]+main_beam[0]

        if hmain_beam[0] > baseLocsr[-1] or hmain_beam[-1] < baseLocsl[0]:
            # peak loctaion is beyond fnbw locations
            msg = "peak location is beyond fnbw locations"
            msg_wrapper("warning", log.warning, msg)
            flag = 24
            # sys.exit()
            # return np.nan, [], np.nan, [], [], msg, [], [], [], [], np.nan, flag, [], [], [],np.nan,0,0
            return {"peakFit":np.nan,"peakModel":[],"peakRms":np.nan,"correctedData":[],"peakPts":[],"msg":msg,
                        "driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,"flag":flag,
                        "baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":np.nan,"baseLeft":[],
                        "baseRight":[]}

        # fit a polynomial to peak data
        ypeak = np.polyval(np.polyfit(x[hmain_beam],
                                    yCorrected[hmain_beam],  2), x[hmain_beam])

        # # check if peak was fit correctly
        msg=f'Test fit makes sense - left: {ypeak[0]:.3f}, center: {max(ypeak):.3f}, right: {ypeak[-1]:.3f}'
        msg_wrapper("debug", log.debug, msg)
        # print(max(ypeak),ypeak[0],ypeak[-1])
        if max(ypeak) == ypeak[0] or max(ypeak) == ypeak[-1]:

            # peak is concave, try fitting wider range
            hmain_beamp = np.where(yMainBeam[hmain_beamn] >= 0.5*maxp)[0]
            hmain_beam = hmain_beamp + hmain_beamn[0]+main_beam[0]
            ypeak = np.polyval(np.polyfit(x[hmain_beam],
                                        yCorrected[hmain_beam],  2), x[hmain_beam])

            if (max(ypeak) == ypeak[0]) or (max(ypeak) == ypeak[-1]):
                # still struggling to fit ?, try this then stop fitting

                try:
                    # LOCATE LOCAL MINUMUM/MAXIMUM POSITIONS
                    # these values are used to figure out where to
                    # select our baseline points/locations
                    localMinPositions = (np.diff(np.sign(np.diff(s))) > 0).nonzero()[
                        0] + 1  # local min positions / first nulls
                    localMaxPositions = (np.diff(np.sign(np.diff(s))) < 0).nonzero()[
                        0] + 1  # local max positions / peak

                    msg=f'mins: {localMinPositions}, maxs: {localMaxPositions}'
                    msg_wrapper("debug", log.debug, msg)


                    # find peak closest to zero
                    locs=x[localMaxPositions]
                    k = min(locs, key=lambda x:abs(x-0))
                    locs=list(locs)
                    #print(f'locs: {locs}, k: {k}')
                    msg=f'pos of possible center peak: {locs.index(k)}'
                    msg_wrapper("debug", log.debug, msg)

                    # use this peak as the main peak
                    kpos=np.where(x==k)[0]
                    msg=f'peak is at loc: {kpos}'
                    msg_wrapper("debug", log.debug, msg)
                    ymax=s[kpos] #max(s)
                    yhalf= ymax/2

                    # find surrounding mins
                    l=min(localMinPositions, key=lambda x:abs(x-kpos))
                    ppos=list(localMinPositions).index(l)
                    # print(l,ppos,kpos)
                    # print(localMinPositions)
                    if l>kpos:
                        v=[localMinPositions[ppos-1],localMinPositions[ppos]]
                        print('window - ',localMinPositions[ppos-1],kpos,localMinPositions[ppos])
                        left=localMinPositions[ppos-1]
                        right=localMinPositions[ppos]
                    elif l < kpos:
                        print(localMinPositions[ppos],kpos,localMinPositions[ppos+1])
                        left=localMinPositions[ppos]
                        right=localMinPositions[ppos+1]
                        print('l < kpos')
                        #sys.exit()
                    else:
                        print(localMinPositions[ppos],kpos,localMinPositions[ppos+1])
                        left=localMinPositions[ppos]
                        right=localMinPositions[ppos+1]
                        print('l ? kpos')
                        sys.exit()
                    top = np.where((s >= yhalf)&(x>x[left])&(x<x[right]))
                
                    # peak is concave, try fitting wider range
                    hmain_beamp = top#np.where(yMainBeam[hmain_beamn] >= 0.5*maxp)[0]
                    #hmain_beam = hmain_beamp + hmain_beamn[0]+main_beam[0]
                    ypeak = np.polyval(np.polyfit(x[hmain_beamp],
                                                yCorrected[hmain_beamp],  2), x[hmain_beamp])
                                                
                    # get residual and rms of peak fit
                    fitRes, err_peak = calc_residual(yCorrected[hmain_beamp], ypeak)

                    # find final peak loc
                    #ploc = np.where(ypeak == max(ypeak))[0]
                    peakLoc = (x[kpos])#[ploc[0]]
                    
                    msg = "attempted to accurately establish peak fit location"
                    msg_wrapper("warning", log.warning, msg)
                    flag = 37

                    
                    sys.exit()
                    pl.title("Plot of final peak fitted data")
                    pl.xlabel("Scandist [Deg]")
                    pl.ylabel("Ta [K]")
                    pl.plot(x, yCorrected, "k", label="corrected data")
                    #pl.plot(x[main_beam],yCorrected[main_beam])
                    pl.plot(x[hmain_beamp], yCorrected[hmain_beamp])
                    #pl.plot(x,fit)
                    pl.plot(x[hmain_beamp],ypeak,"r",label="Ta[K] = %.3f +- %.3f" %(max(ypeak),err_peak))
                    pl.plot(x,np.zeros(scanLen),"k")
                    #pl.grid()
                    pl.legend(loc="best")
                    try:
                        pl.savefig(saveFolder+"peak_fit_data.png")
                    except:
                        pass
                    #pl.show()
                    pl.close()
                    #sys.exit()

                    return {
                        "peakFit":max(ypeak),"peakModel":ypeak, "peakRms":err_peak,"correctedData":yCorrected,"peakPts":hmain_beamp,
                        "msg":"","driftRes":driftRes,"driftRms":driftRms,"driftCoeffs":driftCoeffs,"fitRes":fitRes,"midXValue":coeff[1],
                        "flag":flag,"baseLocsLeft":baseLocsl,"baseLocsRight":baseLocsr,"baseLocsCombined":baseLocs,"peakLoc":peakLoc,
                        "baseLeft":lb,"baseRight":rb,
                    }
                    # return max(ypeak), ypeak, err_peak, yCorrected, hmain_beamp, "", driftRes, driftRms, driftCoeffs, fitRes, 
                    # coeff[1], flag, baseLocsl, baseLocsr, baseLocs, peakLoc,lb,rb
                    
                except:
                    msg = "failed to accurately establish peak fit location"
                    msg_wrapper("warning", log.warning, msg)
                    flag = 5
                    print(msg)
                    # sys.exit()
                    # return np.nan, [], np.nan, [], [], msg, [], [], [], [], np.nan, flag, [], [], [],np.nan,0,0
                    return {"peakFit":np.nan,"peakModel":[],"peakRms":np.nan,"correctedData":[],"peakPts":[],"msg":msg,
                        "driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,"flag":flag,
                        "baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":np.nan,"baseLeft":[],
                        "baseRight":[]}

        # print(max(ypeak),ypeak[0],ypeak[-1],abs(min(yCorrected)) > max(yCorrected))
        if (abs(min(yCorrected)) > max(yCorrected)):
            # still struggling to fit ?, stop fitting
            msg = "min > max"
            msg_wrapper("warning", log.warning, msg)
            flag = 25
            # sys.exit()
            if force=="y":
                pass
            else:
                # return np.nan, [], np.nan, [], [], msg, [], [], [], [], np.nan, flag, [], [], [],np.nan,0,0
                return {"peakFit":np.nan,"peakModel":[],"peakRms":np.nan,"correctedData":[],"peakPts":[],"msg":msg,
                        "driftRes":[],"driftRms":[],"driftCoeffs":[],"fitRes":[],"midXValue":np.nan,"flag":flag,
                        "baseLocsLeft":[],"baseLocsRight":[],"baseLocsCombined":[],"peakLoc":np.nan,"baseLeft":[],
                        "baseRight":[]}
        
        else:
            pass

        # get residual and rms of peak fit
        fitRes, err_peak = calc_residual(yCorrected[hmain_beam], ypeak)
        saveTo=f'{saveTag}_peak_fit.png'
        plotPeakFit("Plot of final peak fitted data",x,yCorrected,ypeak,err_peak,hmain_beam,saveTo)

        # find final peak loc
        ploc = np.where(ypeak == max(ypeak))[0]
        peakLoc = (x[hmain_beam])[ploc[0]]
        # print('out')
        return {
            "peakFit":max(ypeak),"peakModel":ypeak, "peakRms":err_peak,"correctedData":yCorrected,"peakPts":hmain_beam,
            "msg":"","driftRes":driftRes,"driftRms":driftRms,"driftCoeffs":driftCoeffs,"fitRes":fitRes,"midXValue":coeff[1],
            "flag":flag,"baseLocsLeft":baseLocsl,"baseLocsRight":baseLocsr,"baseLocsCombined":baseLocs,"peakLoc":peakLoc,
            "baseLeft":lb,"baseRight":rb,
        }
        # return max(ypeak), ypeak, err_peak, yCorrected, hmain_beam, "", driftRes, driftRms, driftCoeffs, fitRes, coeff[1], flag, baseLocsl, baseLocsr, baseLocs, peakLoc,lb,rb

def fit_dual_beam(x, y, hpbw, fnbw, factor,saveTo,log): #, npts, dec, srcType, data, scanNum, force, log):
    
    # Setup parameters
    scanLen = len(x)              # length of the scan
    midLeftLoc = int(scanLen/4)   # estimated location of peak on left beam
    midRightLoc = midLeftLoc * 3  # estimated location of peak on right beam
    hhpbw = hpbw/2                # half of the hpbw
    hfnbw = fnbw/2                # half of the fnbw
    factoredfnbw = (fnbw*factor)  # fnbw multiplied by factor
    flag=0                        # default flag set to zero
    msg=""                        # flag message to go on plot image
    # saveFolder="currentScanPlots/"
    fl = 0                        # failed left gaussian fit
    fr = 0                        # failed right gaussian fit

    # LOCATE BASELINE BLOCKS
    msg_wrapper("debug", log.debug, "-- Locate baseline blocks")
    
    # we don't worry about sidelobes here so baseline
    # blocks are set to edges or fnbw points

    ptLimit = int(scanLen*0.04) # Point limit, number of allowed points per base block
    baseLocsLeft  = np.arange(0,ptLimit,1)
    baseLocsRight = np.arange(scanLen-ptLimit,scanLen,1)
    baseLocs      = list(baseLocsLeft)+list(baseLocsRight)

    if len(baseLocsLeft) == 0 or len(baseLocsRight) == 0:
        msg = "failed to locate base locs"
        flag = 30
        msg_wrapper("warning", log.warning, msg)
        # sys.exit()
        return {"correctedData":[],"driftRes":[],"driftRms":np.nan,
                        "driftCoeffs":[], "baseLocsCombined":[],
                        "baseLocsLeft":[],"baseLocsRight":[],
                    "leftPeakData":[],"leftPeakModelData":[],
                    "leftPeakFit":np.nan, "leftPeakFitErr":np.nan,"leftPeakFitRes":[],
                    "rightPeakData":[],"rightPeakModelData":[],
                    "rightPeakFit":np.nan, "rightPeakFitErr":[],"rightPeakFitRes":[],
                    "msg":"","midXValueLeft":[],"midXValueRight":[],
                    "flag":flag
                    }
    
    msg_wrapper("debug", log.debug,
                f'BaseLocsLeft: {baseLocsLeft[0]} to {baseLocsLeft[-1]} = {len(baseLocsLeft)} pts')
    msg_wrapper("debug", log.debug,
                f'BaseLocsLeft: {baseLocsRight[0]} to {baseLocsRight[-1]} = {len(baseLocsRight)} pts')
  
    dataModel, driftModel, driftRes, driftRms, driftCoeffs = correct_drift(x[baseLocs], y[baseLocs], x,log)

    # Correct the data and get global max/min
    yCorrected = y-dataModel
    maxyloc = np.argmax(yCorrected)
    minyloc = np.argmin(yCorrected)
    maxy = yCorrected[maxyloc]
    miny = yCorrected[minyloc]

    # Spline the data and get global max/min
    yspl = spline(x, yCorrected)
    ysplmaxloc = np.argmax(yspl)
    ysplminloc = np.argmin(yspl)
    ysplmax = yspl[ysplmaxloc]
    ysplmin = yspl[ysplminloc] 

    # make plots
    plotCorrectedData(x,yCorrected,baseLocsLeft,baseLocsRight,'Corrected data','Baseline blocks','Plot of baseline corrected data',f'{saveTo}corrected.png',xlabel="",ylabel="")
    plot_overlap(x,yCorrected,x,yspl,'Plot of splined data','corrected','spline fit',f'{saveTo}splined.png',xlabel="",ylabel="")
    # sys.exit()
    msg_wrapper("debug", log.debug, "maxyloc: {}, maxy: {:.3f}, minyloc: {}, miny: {:.3f}".format(maxyloc, maxy, minyloc, miny))
    msg_wrapper("debug", log.debug, "maxyloc: {}, maxy: {:.3f}, minyloc: {}, miny: {:.3f}\n".format(ysplmaxloc, ysplmax, ysplminloc, ysplmin))
    msg_wrapper("debug", log.debug, "A beam peakloc: {} \n# B beam peakloc: {}".format(ysplmaxloc, ysplminloc))


    # A/B BEAM DATA PROCESSING
    AbeamScan = np.where(np.logical_and(x > -factoredfnbw, x < 0))[0]
    BbeamScan = np.where(np.logical_and(x > 0, x < factoredfnbw))[0]

    if len(AbeamScan) == 0 or len(BbeamScan) == 0:
        msg="A/B beam scan data == 0, no data"
        flag = 8
        msg_wrapper("warning", log.warning, msg)
        return {"correctedData":[],"driftRes":[],"driftRms":np.nan,
                        "driftCoeffs":[], "baseLocsCombined":[],
                        "baseLocsLeft":[],"baseLocsRight":[],
                    "leftPeakData":[],"leftPeakModelData":[],
                    "leftPeakFit":np.nan, "leftPeakFitErr":np.nan,"leftPeakFitRes":[],
                    "rightPeakData":[],"rightPeakModelData":[],
                    "rightPeakFit":np.nan, "rightPeakFitErr":[],"rightPeakFitRes":[],
                    "msg":"","midXValueLeft":[],"midXValueRight":[],
                    "flag":flag
                    }
    
    msg_wrapper("debug", log.debug, "- Beam seperation:")
    msg_wrapper("debug", log.debug, "Left beam indeces: {} to {}".format(AbeamScan[0], AbeamScan[-1]))
    msg_wrapper("debug", log.debug, "Right beam indeces: {} to {}\n".format(
        BbeamScan[0], BbeamScan[-1]))

    msg_wrapper("debug", log.debug, "- Data Limits")
    msg_wrapper("debug", log.debug, "base left: {}, drift A left: {}, peak A: {}, drift A right: {}".format(baseLocsLeft[-1], AbeamScan[0], ysplminloc, AbeamScan[-1]))
    msg_wrapper("debug", log.debug, "drift B left: {}, peak B: {}, drift B right: {}, base right: {}\n".format(
        BbeamScan[0], ysplmaxloc, BbeamScan[-1], baseLocsRight[0]))

    # figure out orientation of beam. With some scans the beams
    # are flipped e.g, pks2326-502, A beam is positive, whereas
    # j0450-81 A beam is negative.
    # find value closest to zero and use the other value to determine
    # which side to fit positive/negative peak
    lstA=[min(yspl[AbeamScan]), max(yspl[AbeamScan])]
    minA = min(lstA,key=abs)
    fa=""
    if minA==min(yspl[AbeamScan]):
        # fit A beam positive B beam negative
        #print("Fitting positive")
        fa="p"

        
    else:
        # fit A beam negative B beam positive
        #print("Fitting negative")
        fa="n"

    # TODO: should make this an option
    # Decided to change this because the software now treats both 
    # target sources and calibrators the same way
    beamCut = 0.6 # fitting top 40%, 0.7 (30% for cals) or 0.5 (50% for targets) 

    # Ensure peak is within accepted limits
    if fa=="p":
        if ysplmaxloc > AbeamScan[-1]:# or ysplminloc > beamScan[0]:
            msg = "Max is beyond left baseline block"
            flag = 31
            msg_wrapper("warning", log.warning, msg)
            return {"correctedData":[],"driftRes":[],"driftRms":np.nan,
                        "driftCoeffs":[], "baseLocsCombined":[],
                        "baseLocsLeft":[],"baseLocsRight":[],
                    "leftPeakData":[],"leftPeakModelData":[],
                    "leftPeakFit":np.nan, "leftPeakFitErr":np.nan,"leftPeakFitRes":[],
                    "rightPeakData":[],"rightPeakModelData":[],
                    "rightPeakFit":np.nan, "rightPeakFitErr":[],"rightPeakFitRes":[],
                    "msg":"","midXValueLeft":[],"midXValueRight":[],
                    "flag":flag
                    }

        if ysplminloc < BbeamScan[0]:#baseLocsRight[0]:  # ysplminloc < BbeamScan[0] or
            msg="Min is beyond right baseline block"
            # print(msg)
            flag=32
            msg_wrapper("warning", log.warning, msg)
            return {"correctedData":[],"driftRes":[],"driftRms":np.nan,
                        "driftCoeffs":[], "baseLocsCombined":[],
                        "baseLocsLeft":[],"baseLocsRight":[],
                    "leftPeakData":[],"leftPeakModelData":[],
                    "leftPeakFit":np.nan, "leftPeakFitErr":np.nan,"leftPeakFitRes":[],
                    "rightPeakData":[],"rightPeakModelData":[],
                    "rightPeakFit":np.nan, "rightPeakFitErr":[],"rightPeakFitRes":[],
                    "msg":"","midXValueLeft":[],"midXValueRight":[],
                    "flag":flag
                    }

        # Try to fit a gaussian to determine peak parameters
        try:
            # set initial parameters for data fitting
            p = [max(y), x[midLeftLoc], hpbw, .01, .0]
            # Try to fit a gaussian to determine peak location
            # this also works as a bad scan filter
            coeffl, fitl, flagl = test_gauss_fit(x[AbeamScan], y[AbeamScan], p,log)
            # coeffl, covar_matrixl, fitLeft = fit_gauss_lin(
                # x[AbeamScan], y[AbeamScan], p)
        except Exception:
            fl=1
            msg = "gaussian curve_fit algorithm failed"
            msg_wrapper("debug", log.debug, msg)
            fitLeft = y[AbeamScan]
            flag = 3

        try:
            # set initial parameters for data fitting
            p = [min(y), x[midRightLoc], hpbw, .01, .0]
            coeffr, fitr, flagr = test_gauss_fit(x[AbeamScan], y[AbeamScan], p,log)
            
            # coeffr, covar_matrixr, fitRight = fit_gauss_lin(
                # x[BbeamScan], y[BbeamScan], p)
        except Exception:
            fr = 1
            msg = "gaussian curve_fit algorithm failed"
            msg_wrapper("debug", log.debug, msg)
            fitRight = y[BbeamScan]
            flag = 3

        # Determine peak fitting location
        BbeamLeftLimit  = x[ysplminloc]-hhpbw #coeffl[1] - hhpbw  # *2*.6
        BbeamRightLimit = x[ysplminloc]+hhpbw
        AbeamLeftLimit  = x[ysplmaxloc]-hhpbw #coeffl[1] - hhpbw  # *2*.6
        AbeamRightLimit = x[ysplmaxloc]+hhpbw

        leftlocs = np.where(np.logical_and(
            x >= AbeamLeftLimit, x <= AbeamRightLimit))[0]
        rightlocs = np.where(np.logical_and(
            x >= BbeamLeftLimit, x <= BbeamRightLimit))[0]
        
        
        # select part of beam to fit
        if ysplmax < 0.1:
            flag = 36
            msg = "fit entire left beam, max yspl < 0.1"
            msg_wrapper("warning", log.warning, msg)
            leftMainBeamLocs = leftlocs
            
        else:
            topCut = np.where(yspl[leftlocs] >= ysplmax*beamCut)[0]
            leftMainBeamLocs = leftlocs[0]+np.array(topCut)

        if ysplmin > -0.1:
            flag = 35
            msg = "fit entire right beam, min yspl > -0.1"
            msg_wrapper("warning", log.warning, msg)
            rightMainBeamLocs = rightlocs
        else:
            bottomCut = np.where(yspl[rightlocs] <= ysplmin*beamCut)[0]
            rightMainBeamLocs = rightlocs[0]+np.array(bottomCut)

    if fa=="n":
        # A beam is min
        if ysplmaxloc < AbeamScan[-1]:# or ysplminloc > beamScan[0]:
            msg = "Max is beyond left baseline block"
            flag = 31
            msg_wrapper("warning", log.warning, msg)
            return {"correctedData":[],"driftRes":[],"driftRms":np.nan,
                        "driftCoeffs":[], "baseLocsCombined":[],
                        "baseLocsLeft":[],"baseLocsRight":[],
                    "leftPeakData":[],"leftPeakModelData":[],
                    "leftPeakFit":np.nan, "leftPeakFitErr":np.nan,"leftPeakFitRes":[],
                    "rightPeakData":[],"rightPeakModelData":[],
                    "rightPeakFit":np.nan, "rightPeakFitErr":[],"rightPeakFitRes":[],
                    "msg":"","midXValueLeft":[],"midXValueRight":[],
                    "flag":flag
                    }

        if ysplminloc > BbeamScan[0]:#baseLocsRight[0]:  # ysplminloc < BbeamScan[0] or
            msg="Min is beyond right baseline block"
            # print(msg)
            flag=32
            msg_wrapper("warning", log.warning, msg)
            return {"correctedData":[],"driftRes":[],"driftRms":np.nan,
                        "driftCoeffs":[], "baseLocsCombined":[],
                        "baseLocsLeft":[],"baseLocsRight":[],
                    "leftPeakData":[],"leftPeakModelData":[],
                    "leftPeakFit":np.nan, "leftPeakFitErr":np.nan,"leftPeakFitRes":[],
                    "rightPeakData":[],"rightPeakModelData":[],
                    "rightPeakFit":np.nan, "rightPeakFitErr":[],"rightPeakFitRes":[],
                    "msg":"","midXValueLeft":[],"midXValueRight":[],
                    "flag":flag
                    }

        # Try to fit a gaussian to determine peak parameters
        try:
            # set initial parameters for data fitting
            p = [min(y), x[midLeftLoc], hpbw, .01, .0]
            coeffl, fitl, flag = test_gauss_fit(x[AbeamScan], y[AbeamScan], p,log)
            # coeffl, covar_matrixl, fitLeft = fit_gauss_lin(
            #     x[AbeamScan], y[AbeamScan], p)
        except Exception:
            fl=1
            msg = "gaussian curve_fit algorithm failed"
            msg_wrapper("debug", log.debug, msg)
            fitLeft = y[AbeamScan]
            flag = 3

        try:
            # set initial parameters for data fitting
            p = [max(y), x[midRightLoc], hpbw, .01, .0]
            coeffr, fitr, flagr = test_gauss_fit( x[BbeamScan], y[BbeamScan], p,log)
            # coeffr, covar_matrixr, fitRight = fit_gauss_lin(
            #     x[BbeamScan], y[BbeamScan], p)
        except Exception:
            fr = 1
            msg = "gaussian curve_fit algorithm failed"
            msg_wrapper("debug", log.debug, msg)
            fitRight = y[BbeamScan]
            flag = 3

    
        # Determine peak fitting location
        AbeamLeftLimit  = x[ysplminloc]-hhpbw #coeffl[1] - hhpbw  # *2*.6
        AbeamRightLimit = x[ysplminloc]+hhpbw
        BbeamLeftLimit  = x[ysplmaxloc]-hhpbw #coeffl[1] - hhpbw  # *2*.6
        BbeamRightLimit = x[ysplmaxloc]+hhpbw


        leftlocs = np.where(np.logical_and(
            x >= AbeamLeftLimit, x <= AbeamRightLimit))[0]
        rightlocs = np.where(np.logical_and(
            x >= BbeamLeftLimit, x <= BbeamRightLimit))[0]


        #select part of beam to fit
        if ysplmax < 0.1:
            flag = 36
            msg = "fit entire left beam, max yspl < 0.1"
            msg_wrapper("warning", log.warning, msg)
            rightMainBeamLocs = rightlocs
        else:
            topCut = np.where(yspl[rightlocs] >= ysplmax*beamCut)[0]
            rightMainBeamLocs = rightlocs[0]+np.array(topCut)

        if ysplmin > -0.1:
            flag = 35
            msg = "fit entire right beam, min yspl > -0.1"
            msg_wrapper("warning", log.warning, msg)
            leftMainBeamLocs = leftlocs
        else:
            bottomCut = np.where(yspl[leftlocs] <= ysplmin*beamCut)[0]
            leftMainBeamLocs = leftlocs[0]+np.array(bottomCut)

    # fit left peak
    ypeakl = np.polyval(np.polyfit(x[leftMainBeamLocs], yCorrected[leftMainBeamLocs],  2), x[leftMainBeamLocs])
    fitResl, err_peakl = calc_residual(yCorrected[leftMainBeamLocs], ypeakl)

    # fit right peak
    ypeakr = np.polyval(np.polyfit(
        x[rightMainBeamLocs], yCorrected[rightMainBeamLocs],  2), x[rightMainBeamLocs])
    fitResr, err_peakr = calc_residual(yCorrected[rightMainBeamLocs], ypeakr)

    if fa=="p":
        ymin = min(ypeakr)
        ymax = max(ypeakl)
    else:
        ymin = min(ypeakl)
        ymax = max(ypeakr)

    msg_wrapper("debug", log.debug, "A/B beam peak")
    if fa=="p":
        msg_wrapper("debug", log.debug, "left: {:.3f}, max: {:.3f}, right: {:.3f}".format(
            ypeakl[0], ymax, ypeakl[-1]))
        msg_wrapper("debug", log.debug, "left: {:.3f}, min: {:.3f}, right{:.3f}".format(
            ypeakr[0], ymin, ypeakr[-1]))

        ypeakrdata = x[rightMainBeamLocs]
        ypeakldata = x[leftMainBeamLocs]

        # check data doesn't overlap
        overlapRight = set(baseLocsRight) & set(rightMainBeamLocs)
        overlapLeft = set(baseLocsLeft) & set(leftMainBeamLocs)
        # overlapbeams = set(leftMainBeamLocs) & set(rightMainBeamLocs)

        msg=("checking for overlapping beams: ")
        msg_wrapper("debug", log.debug, msg)
        
        if len(overlapLeft) != 0:
            msg = "beams don't overlap on left"
            msg_wrapper("debug", log.debug, msg)

            if leftMainBeamLocs[0] > baseLocsLeft[int(
                    len(baseLocsLeft)*.8)]:
                pass
            else:
                overlap = next(iter(overlapLeft))
                shift = list(leftMainBeamLocs).index(int(overlap))
                msg = "Overlap found on A beam"
                flag = 33
                msg_wrapper("warning", log.warning, msg)

                # move beam to the left
                f = abs(len(leftMainBeamLocs)-shift)
                leftMainBeamLocs = abs(leftMainBeamLocs+f)

                # fit left peak
                ypeakl = np.polyval(np.polyfit(
                    x[leftMainBeamLocs], yCorrected[leftMainBeamLocs],  2), x[leftMainBeamLocs])
                fitResl, err_peakl = calc_residual(
                    yCorrected[leftMainBeamLocs], ypeakl)

                ymax = max(ypeakl)
                msg="left: {:.3f}, max: {:.3f}, right: {:.3f}".format(
                    ypeakl[0], ymax, ypeakl[-1])
                msg_wrapper("debug", log.debug, msg)

                if(ypeakl[0] >= ymax or ypeakl[-1] >= ymax):
                    ymax = np.nan
                    err_peakl = np.nan
                else:
                    flag = 36
                    msg = "fit entire left beam"
                    msg_wrapper("debug", log.debug, msg)

                return {"correctedData":[],"driftRes":[],"driftRms":np.nan,
                        "driftCoeffs":[], "baseLocsCombined":[],
                        "baseLocsLeft":[],"baseLocsRight":[],
                    "leftPeakData":[],"leftPeakModelData":[],
                    "leftPeakFit":np.nan, "leftPeakFitErr":np.nan,"leftPeakFitRes":[],
                    "rightPeakData":[],"rightPeakModelData":[],
                    "rightPeakFit":np.nan, "rightPeakFitErr":[],"rightPeakFitRes":[],
                    "msg":"","midXValueLeft":[],"midXValueRight":[],
                    "flag":flag
                    }

        if len(overlapRight) != 0:

            overlap = next(iter(overlapRight))
            shift = list(rightMainBeamLocs).index(int(overlap))

            msg = "Overlap found on B beam"
            flag = 34
            msg_wrapper("warning", log.warning, msg)

            # move beam to the RIGHT
            f = abs(len(rightMainBeamLocs)-shift)
            rightMainBeamLocs = abs(rightMainBeamLocs-f)

            msg="beam shifted to left by {} points".format(f)
            msg_wrapper("debug", log.debug, msg)

            # fit right peak
            ypeakr = np.polyval(np.polyfit(
                x[rightMainBeamLocs], yCorrected[rightMainBeamLocs],  2), x[rightMainBeamLocs])
            fitResr, err_peakr = calc_residual(
                yCorrected[rightMainBeamLocs], ypeakr)

            ymin = min(ypeakr)

            msg="left: {:.3f}, min: {:.3f}, right{:.3f}".format(
                ypeakr[0], ymin, ypeakr[-1])
            msg_wrapper("debug", log.debug, msg)

            if(ypeakr[0] <= ymin or ypeakr[-1] <= ymin):
                ymin = np.nan
                err_peakr = np.nan

            else:
                flag = 35
                msg = "fit entire right beam"
                msg_wrapper("debug", log.debug, msg)

            ypeakrdata = x[rightMainBeamLocs]

            #pl.plot(x, yCorrected)

            '''#pl.plot(x[leftlocs],yCorrected[leftlocs])
            #pl.plot(x[leftMainBeamLocs], yCorrected[leftMainBeamLocs])
            #pl.plot(x[rightlocs],yCorrected[rightlocs])
            pl.plot(x[rightMainBeamLocs], yCorrected[rightMainBeamLocs])
            #pl.plot(x[leftMainBeamLocs], ypeakl)
            pl.plot(x[rightMainBeamLocs], ypeakr)
            pl.plot(x, np.zeros(scanLen))
            pl.plot(x[baseLocs], yCorrected[baseLocs], ".")
            #pl.show()
            pl.close()
            #sys.exit()'''

            return {"correctedData":[],"driftRes":[],"driftRms":np.nan,
                        "driftCoeffs":[], "baseLocsCombined":[],
                        "baseLocsLeft":[],"baseLocsRight":[],
                    "leftPeakData":[],"leftPeakModelData":[],
                    "leftPeakFit":np.nan, "leftPeakFitErr":np.nan,"leftPeakFitRes":[],
                    "rightPeakData":[],"rightPeakModelData":[],
                    "rightPeakFit":np.nan, "rightPeakFitErr":[],"rightPeakFitRes":[],
                    "msg":"","midXValueLeft":[],"midXValueRight":[],
                    "flag":flag
                    }

        if ((x[leftMainBeamLocs])[-1] > 0):
            flag = 28
            msg = "left beam data goes beyond midpoint"
            msg_wrapper("warning", log.warning, msg)
            return {"correctedData":[],"driftRes":[],"driftRms":np.nan,
                        "driftCoeffs":[], "baseLocsCombined":[],
                        "baseLocsLeft":[],"baseLocsRight":[],
                    "leftPeakData":[],"leftPeakModelData":[],
                    "leftPeakFit":np.nan, "leftPeakFitErr":np.nan,"leftPeakFitRes":[],
                    "rightPeakData":[],"rightPeakModelData":[],
                    "rightPeakFit":np.nan, "rightPeakFitErr":[],"rightPeakFitRes":[],
                    "msg":"","midXValueLeft":[],"midXValueRight":[],
                    "flag":flag
                    }

        if ((x[rightMainBeamLocs])[-1] < 0):
            flag = 29
            msg = "right beam data goes beyond midpoint"
            msg_wrapper("warning", log.warning, msg)
            return {"correctedData":[],"driftRes":[],"driftRms":np.nan,
                        "driftCoeffs":[], "baseLocsCombined":[],
                        "baseLocsLeft":[],"baseLocsRight":[],
                    "leftPeakData":[],"leftPeakModelData":[],
                    "leftPeakFit":np.nan, "leftPeakFitErr":np.nan,"leftPeakFitRes":[],
                    "rightPeakData":[],"rightPeakModelData":[],
                    "rightPeakFit":np.nan, "rightPeakFitErr":[],"rightPeakFitRes":[],
                    "msg":"","midXValueLeft":[],"midXValueRight":[],
                    "flag":flag
                    }

        # import matplotlib.pyplot as pl
        # pl.plot(x, yCorrected, label="corrected data")
        # pl.plot(x[leftlocs], yCorrected[leftlocs], label="peakl data")
        # pl.plot(x[leftMainBeamLocs], yCorrected[leftMainBeamLocs])
        # pl.plot(x[rightlocs], yCorrected[rightlocs], label="peakr data")
        # pl.plot(x[rightMainBeamLocs], yCorrected[rightMainBeamLocs])
        # pl.plot(x[leftMainBeamLocs],
        #         ypeakl, label="peak fitl: {:.3f} +- {:.3f}".format(ymax, err_peakl))
        # pl.plot(x[rightMainBeamLocs], ypeakr,
        #         label="peak fitr: {:.3f} +- {:.3f}".format(ymin, err_peakr))
        # pl.plot(x[baseLocs], yCorrected[baseLocs], ".", label="baselocs")
        # pl.plot(x, np.zeros(scanLen))
        # pl.legend(loc="best")
        # pl.grid()
        # #pl.show()
        # try:
        #     pl.savefig(saveFolder+"fitted.png")
        # except:
        #     pass
        # pl.close()
        # sys.exit()
        
        msg_wrapper("info", log.info, "\n")
        msg_wrapper("info", log.info, "-"*30)
        msg_wrapper("info", log.info, "Fit the peaks")
        msg_wrapper("info", log.info,"-"*30)

        msg="\npeak left: {:.3f} +- {:.3f} K\npeak right: {:.3f} +- {:.3f} K\n".format(
            ymax, err_peakl, ymin, err_peakr)
        msg_wrapper("info", log.info, msg)
        
        # find final peak loc
        ploca = np.where(ypeakl == ymax)[0]
        if len(ploca)==0:
            peakLoca=np.nan
        else:
            peakLoca = (x[leftMainBeamLocs])[ploca[0]]

        # find final peak loc
        plocb = np.where(ypeakr == ymin)[0] 
        if len(plocb)==0:    
            peakLocb=np.nan
        else:
            peakLocb = (x[rightMainBeamLocs])[plocb[0]]


        return {"correctedData":yCorrected,"driftRes":driftRes,"driftRms":driftRms,
                        "driftCoeffs":driftCoeffs, "baseLocsCombined":baseLocs,
                        "baseLocsLeft":leftMainBeamLocs,"baseLocsRight":rightMainBeamLocs,
                    "leftPeakData":ypeakldata,"leftPeakModelData":ypeakl,
                    "leftPeakFit":ymax, "leftPeakFitErr":err_peakl,"leftPeakFitRes":fitResl,
                    "rightPeakData":ypeakrdata,"rightPeakModelData":ypeakr,
                    "rightPeakFit":ymin, "rightPeakFitErr":err_peakr,"rightPeakFitRes":fitResr,
                    "msg":"","midXValueLeft":peakLoca,"midXValueRight":peakLocb,
                    "flag":flag
                    }

    else:
        msg_wrapper("debug", log.debug, "left: {:.3f}, min: {:.3f}, right: {:.3f}".format(
            ypeakl[0], ymin, ypeakl[-1]))
        msg_wrapper("debug", log.debug, "left: {:.3f}, max: {:.3f}, right{:.3f}".format(
            ypeakr[0], ymax, ypeakr[-1]))

        ypeakrdata = x[rightMainBeamLocs]
        ypeakldata = x[leftMainBeamLocs]

        # check data doesn't overlap
        overlapRight = set(baseLocsRight) & set(rightMainBeamLocs)
        overlapLeft = set(baseLocsLeft) & set(leftMainBeamLocs)
        # overlapbeams = set(leftMainBeamLocs) & set(rightMainBeamLocs)

        msg=("checking for overlapping beams: ")
        msg_wrapper("debug", log.debug, msg)

        if len(overlapLeft) != 0:
            msg = "beams don't overlap on left"
            msg_wrapper("debug", log.debug, msg)

            if leftMainBeamLocs[0] > baseLocsLeft[int(
                    len(baseLocsLeft)*.8)]:
                pass
            else:
                overlap = next(iter(overlapLeft))
                shift = list(leftMainBeamLocs).index(int(overlap))
                msg = "Overlap found on A beam"
                flag = 33
                msg_wrapper("warning", log.warning, msg)

                # move beam to the left
                f = abs(len(leftMainBeamLocs)-shift)
                leftMainBeamLocs = abs(leftMainBeamLocs+f)

                # fit left peak
                ypeakl = np.polyval(np.polyfit(
                    x[leftMainBeamLocs], yCorrected[leftMainBeamLocs],  2), x[leftMainBeamLocs])
                fitResl, err_peakl = calc_residual(
                    yCorrected[leftMainBeamLocs], ypeakl)

                ymax = max(ypeakl)
                msg="left: {:.3f}, max: {:.3f}, right: {:.3f}".format(
                    ypeakl[0], ymax, ypeakl[-1])
                msg_wrapper("debug", log.debug, msg)

                if(ypeakl[0] <= ymax or ypeakl[-1] <= ymax):
                    ymax = np.nan
                    err_peakl = np.nan
                else:
                    flag = 36
                    msg = "fit entire left beam"
                    msg_wrapper("debug", log.debug, msg)

                ypeakldata = x[leftMainBeamLocs]

                '''pl.plot(x, yCorrected)
                pl.plot(x[leftMainBeamLocs], yCorrected[leftMainBeamLocs], 'b')
                #pl.plot(x[rightlocs],yCorrected[rightlocs])
                #pl.plot(x[rightMainBeamLocs], yCorrected[rightMainBeamLocs])
                pl.plot(x[leftMainBeamLocs], ypeakl, 'r')
                #pl.plot(x[rightMainBeamLocs], ypeakr)
                pl.plot(x, np.zeros(scanLen))
                pl.plot(x[baseLocs], yCorrected[baseLocs], ".")
                #pl.show()
                pl.close()
                #sys.exit()'''

                return {"correctedData":[],"driftRes":[],"driftRms":np.nan,
                        "driftCoeffs":[], "baseLocsCombined":[],
                        "baseLocsLeft":[],"baseLocsRight":[],
                    "leftPeakData":[],"leftPeakModelData":[],
                    "leftPeakFit":np.nan, "leftPeakFitErr":np.nan,"leftPeakFitRes":[],
                    "rightPeakData":[],"rightPeakModelData":[],
                    "rightPeakFit":np.nan, "rightPeakFitErr":[],"rightPeakFitRes":[],
                    "msg":"","midXValueLeft":[],"midXValueRight":[],
                    "flag":flag
                    }

        if len(overlapRight) != 0:

            overlap = next(iter(overlapRight))
            shift = list(rightMainBeamLocs).index(int(overlap))

            msg = "Overlap found on B beam"
            flag = 34
            msg_wrapper("warning", log.warning, msg)

            # move beam to the RIGHT
            f = abs(len(rightMainBeamLocs)-shift)
            rightMainBeamLocs = abs(rightMainBeamLocs-f)

            msg="beam shifted to left by {} points".format(f)
            msg_wrapper("debug", log.debug, msg)

            # fit right peak
            ypeakr = np.polyval(np.polyfit(
                x[rightMainBeamLocs], yCorrected[rightMainBeamLocs],  2), x[rightMainBeamLocs])
            fitResr, err_peakr = calc_residual(
                yCorrected[rightMainBeamLocs], ypeakr)

            ymin = min(ypeakr)

            msg="left: {:.3f}, min: {:.3f}, right{:.3f}".format(
                ypeakr[0], ymin, ypeakr[-1])
            msg_wrapper("debug", log.debug, msg)

            if(ypeakr[0] <= ymin or ypeakr[-1] <= ymin):
                ymin = np.nan
                err_peakr = np.nan

            else:
                flag = 35
                msg = "fit entire right beam"
                msg_wrapper("debug", log.debug, msg)

            ypeakrdata = x[rightMainBeamLocs]

            #pl.plot(x, yCorrected)

            '''#pl.plot(x[leftlocs],yCorrected[leftlocs])
            #pl.plot(x[leftMainBeamLocs], yCorrected[leftMainBeamLocs])
            #pl.plot(x[rightlocs],yCorrected[rightlocs])
            pl.plot(x[rightMainBeamLocs], yCorrected[rightMainBeamLocs])
            #pl.plot(x[leftMainBeamLocs], ypeakl)
            pl.plot(x[rightMainBeamLocs], ypeakr)
            pl.plot(x, np.zeros(scanLen))
            pl.plot(x[baseLocs], yCorrected[baseLocs], ".")
            #pl.show()
            pl.close()
            #sys.exit()'''

            return {"correctedData":[],"driftRes":[],"driftRms":np.nan,
                        "driftCoeffs":[], "baseLocsCombined":[],
                        "baseLocsLeft":[],"baseLocsRight":[],
                    "leftPeakData":[],"leftPeakModelData":[],
                    "leftPeakFit":np.nan, "leftPeakFitErr":np.nan,"leftPeakFitRes":[],
                    "rightPeakData":[],"rightPeakModelData":[],
                    "rightPeakFit":np.nan, "rightPeakFitErr":[],"rightPeakFitRes":[],
                    "msg":"","midXValueLeft":[],"midXValueRight":[],
                    "flag":flag
                    }

        if ((x[leftMainBeamLocs])[-1] > 0):
            flag = 28
            msg = "left beam data goes beyond midpoint"
            msg_wrapper("warning", log.warning, msg)
            return {"correctedData":[],"driftRes":[],"driftRms":np.nan,
                        "driftCoeffs":[], "baseLocsCombined":[],
                        "baseLocsLeft":[],"baseLocsRight":[],
                    "leftPeakData":[],"leftPeakModelData":[],
                    "leftPeakFit":np.nan, "leftPeakFitErr":np.nan,"leftPeakFitRes":[],
                    "rightPeakData":[],"rightPeakModelData":[],
                    "rightPeakFit":np.nan, "rightPeakFitErr":[],"rightPeakFitRes":[],
                    "msg":"","midXValueLeft":[],"midXValueRight":[],
                    "flag":flag
                    }

        if ((x[rightMainBeamLocs])[-1] < 0):
            flag = 29
            msg = "right beam data goes beyond midpoint"
            msg_wrapper("warning", log.warning, msg)
            # return [], [], [], np.nan, [], \
            #     [], [], np.nan, np.nan, [], \
            #     [], [], np.nan, np.nan, [],\
            #     msg, flag, np.nan, np.nan
            return {"correctedData":[],"driftRes":[],"driftRms":np.nan,
                        "driftCoeffs":[], "baseLocsCombined":[],
                        "baseLocsLeft":[],"baseLocsRight":[],
                    "leftPeakData":[],"leftPeakModelData":[],
                    "leftPeakFit":np.nan, "leftPeakFitErr":np.nan,"leftPeakFitRes":[],
                    "rightPeakData":[],"rightPeakModelData":[],
                    "rightPeakFit":np.nan, "rightPeakFitErr":[],"rightPeakFitRes":[],
                    "msg":"","midXValueLeft":[],"midXValueRight":[],
                    "flag":flag
                    }
            

        # import matplotlib.pyplot as pl 
        # pl.plot(x, yCorrected, label="corrected data")
        # pl.plot(x[leftlocs], yCorrected[leftlocs], label="peakl data")
        # pl.plot(x[leftMainBeamLocs], yCorrected[leftMainBeamLocs])
        # pl.plot(x[rightlocs], yCorrected[rightlocs], label="peakr data")
        # pl.plot(x[rightMainBeamLocs], yCorrected[rightMainBeamLocs])
        # pl.plot(x[leftMainBeamLocs],
        #         ypeakl, label="peak fitl: {:.3f} +- {:.3f}".format(ymin, err_peakl))
        # pl.plot(x[rightMainBeamLocs], ypeakr,
        #         label="peak fitr: {:.3f} +- {:.3f}".format(ymax, err_peakr))
        # pl.plot(x[baseLocs], yCorrected[baseLocs], ".", label="baselocs")
        # pl.plot(x, np.zeros(scanLen))
        # pl.legend(loc="best")
        # pl.show()
        # try:
        #     pl.savefig(saveFolder+"fitted.png")
        # except:
        #     pass
        # pl.close()
        # sys.exit()

        msg_wrapper("info", log.info, "\n")
        msg_wrapper("info", log.info, "-"*30)
        msg_wrapper("info", log.info, "Fit the peaks.")
        msg_wrapper("info", log.info,"-"*30)

        msg="\npeak left: {:.3f} +- {:.3f} K\npeak right: {:.3f} +- {:.3f} K\n".format(
            ymin, err_peakl, ymax, err_peakr)
        msg_wrapper("info", log.info, msg)
      
        # find final peak loc
        ploca = np.where(ypeakl == ymin)[0]
        if len(ploca)==0:
            peakLoca=np.nan
        else:
            peakLoca = (x[leftMainBeamLocs])[ploca[0]]

        # find final peak loc
        plocb = np.where(ypeakr == ymax)[0] 
        if len(plocb)==0:    
            peakLocb=np.nan
        else:
            peakLocb = (x[rightMainBeamLocs])[plocb[0]]

        return {"correctedData":yCorrected,"driftRes":driftRes,"driftRms":driftRms,
                        "driftCoeffs":driftCoeffs, "baseLocsCombined":baseLocs,
                        "baseLocsLeft":leftMainBeamLocs,"baseLocsRight":rightMainBeamLocs,
                    "leftPeakData":ypeakldata,"leftPeakModelData":ypeakl,
                    "leftPeakFit":ymax, "leftPeakFitErr":err_peakl,"leftPeakFitRes":fitResl,
                    "rightPeakData":ypeakrdata,"rightPeakModelData":ypeakr,
                    "rightPeakFit":ymin, "rightPeakFitErr":err_peakr,"rightPeakFitRes":fitResr,
                    "msg":"","midXValueLeft":peakLoca,"midXValueRight":peakLocb,
                    "flag":flag
                    }
                   
        # return yCorrected, driftRes, driftRms, driftCoeffs[0], baseLocs, \
        #     ypeakldata, ypeakl, ymin, err_peakl, fitResl, \
        #     ypeakrdata, ypeakr, ymax, err_peakr, fitResr,\
        #     msg, flag, peakLoca, peakLocb

def get_base(localMinPositions, block_width, scan_len):
        """ get the baseline block/s from data with large sidelobes. """

        base=[] # entire basline block points
        localMinPositions=sorted(localMinPositions)

        basel=[] # left baseline blocks
        baser=[] # right baseline blocks
        lp=[]
        rp=[]
        basell=[]
        baserr=[]

        ind=4
        for i in range(len(localMinPositions)):

            #print(localMinPositions[i], block_width)

            if localMinPositions[i]<=block_width:
                # get everything before and after
                # print("0",localMinPositions[i], block_width+localMinPositions[i])
                base=base+list(np.arange(0,block_width+localMinPositions[i]+1))

                if localMinPositions[i] <= scan_len/2:
                    basel = basel+list(np.arange(0, block_width+localMinPositions[i]+1))

                    lp=lp+[localMinPositions[i]]
                    #print("1- ",localMinPositions[i])
                    basell.append(0)
                    basell.append(block_width+localMinPositions[i]+1)
                
                elif localMinPositions[i] > scan_len/2:
                    baser = baser + \
                        list(np.arange(0, block_width+localMinPositions[i]+1))
                    
                    rp=rp+[localMinPositions[i]]
                    #print("2+ ", localMinPositions[i])
                    baserr.append(0)
                    baserr.append(block_width+localMinPositions[i]+1)

            elif localMinPositions[i]>=scan_len-block_width:
                # get everything before and after
                #print(localMinPositions[i]-block_width, localMinPositions[i], scan_len)
                base=base+list(np.arange(localMinPositions[i]-block_width,scan_len))

                if localMinPositions[i] <= scan_len/2:
                    basel = basel+list(
                            np.arange(localMinPositions[i]-block_width, scan_len))
                    lp=lp+[localMinPositions[i]]
                    #print("3- ", localMinPositions[i])
                    basell.append(localMinPositions[i]-block_width)
                    basell.append(scan_len)

                elif localMinPositions[i] > scan_len/2:
                    baser = baser+list(
                        np.arange(localMinPositions[i]-block_width, scan_len-1))
                    
                    baserr.append(localMinPositions[i]-block_width)
                    baserr.append(scan_len-1)
                    rp = rp+[localMinPositions[i]]
                    #print("4+ ", localMinPositions[i])

            else:
                
                #print(localMinPositions[i]-block_width, localMinPositions[i], block_width+localMinPositions[i])
                
                base=base+list(np.arange(localMinPositions[i]-block_width,block_width+localMinPositions[i]))

                if localMinPositions[i] <= scan_len/2:

                    #print("5- ", localMinPositions[i])

                    basel=basel+list(
                            np.arange(localMinPositions[i]-block_width, block_width+localMinPositions[i]))

                    #print("6- ",lp,localMinPositions[i])
                    lp = lp+[localMinPositions[i]]

                    basell.append(localMinPositions[i]-block_width)
                    basell.append(block_width+localMinPositions[i])

                elif localMinPositions[i] > scan_len/2:
                        baser= baser+list(
                        np.arange(localMinPositions[i]-block_width, block_width+localMinPositions[i]))
                        
                        rp = rp+[localMinPositions[i]]
                    
                        end = block_width+localMinPositions[i]
                        baserr.append(localMinPositions[i]-block_width)

                        if end >=scan_len:

                            baserr.append(scan_len)

        return base, basel,baser,basell,baserr,lp,rp

# GUI operation
def get_base_pts(x, y, base_index_list):
    """ Get baseline points from a list of 
        indexes.
    """

    # Get data between the indexes selected
    ind_list = sorted(base_index_list)

    # get location of all points
    xb_data = []
    yb_data = []

    if len(ind_list) == 2:
        ind_1 = ind_list[0]
        ind_2 = ind_list[1]
        #print(i, i+1, ind_1, ind_2, len(ind_list))
        xb_data = xb_data + list(x[ind_1:ind_2])
        yb_data = yb_data + list(y[ind_1:ind_2])
    else:
        for i in range(len(ind_list)):
            if i % 2 == 0 and i != 1:
                ind_1 = ind_list[i]
                ind_2 = ind_list[i+1]
                #print(i, i+1, ind_1, ind_2, len(ind_list))
                xb_data = xb_data + list(x[ind_1:ind_2])
                yb_data = yb_data + list(y[ind_1:ind_2])

    return xb_data, yb_data

def filter_scans(x, window_len=10, window='flat'):
    """
        smooth the data using a window with requested size.
    
        This method is based on the convolution of a scaled window with the signal.
        The signal is prepared by introducing reflected copies of the signal 
        (with the window size) in both ends so that transient parts are minimized
        in the begining and end part of the output signal.
        
        Args:
            x: the input signal 
            window_len: the dimension of the smoothing window; should be an odd integer
            window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 
                'blackman' flat window will produce a moving average smoothing.

        Returns:
            the smoothed signal
    """

    if x.ndim != 1:
        raise (ValueError, "smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise (ValueError, "Input vector needs to be bigger than window size.")

    if window_len < 3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise (
            ValueError, "Window is one of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")

    s = np.r_[x[window_len-1:0:-1], x, x[-2:-window_len-1:-1]]

    if window == 'flat':  # moving average
        w = np.ones(window_len, 'd')
    else:
        w = eval('np.'+window+'(window_len)')

    y = np.convolve(w/w.sum(), s, mode='valid')
    return y

def fit_poly_peak(xp, yp, order,log):
    """
        Fit the peak and estimate the errors.
    """

    peakCoeffs = poly_coeff(xp, yp, order)
    peakModel = np.polyval(peakCoeffs, xp)

    # Calculate the residual and rms of the peak fit
    peakRes, peakRms = calc_residual(peakModel, yp,log)
    return peakRes, peakRms, peakModel

