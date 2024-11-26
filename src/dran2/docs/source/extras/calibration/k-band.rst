Calibrate K-band data
=======================

Calibration at K-band can be challenging. This is because at these high frequencies
the atmosphere in which the faint radio signals must travel becomes a problem. These 
issues need to be calibrated out before we can process the data.

At 22 GHz, there are few sources in the Southern Hemisphere bright enough to be detected 
by the HartRAO 26m antenna. For this reason, we use the planet Jupiter to calibrate our 
sources.


1. **Correct for atmospheric contributions:**
   - This is done using techniques such as the Atmospheric Dispersion Compensator (ADC) or the

::
    \begin{align*}
    \text{Corrected flux} = \frac{\text{Raw flux}}{\text{Beam response}}
    \end{align*}

2. **Correct for pointing errors:**
   - This is done using techniques such as the Atmospheric Dispersion Compensator (ADC) or the
