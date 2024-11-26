Calibration
===========

Data calibration is a critical step in the data analysis process. Commonalibration ensures that
systematic, instrumental, or environmental effects that occur during observations are accounted 
for and corrected to maintain the integrity of the data. Ensuring that measurements
are appropriately adjusted, calibration safeguards against inaccuracies that could render 
the data unusable for scientific analysis, ultimately refining the precision and accuracy of the
measurements obtained.

The process of data calibration involves several key steps which vary according to the frequency
of observation.

The HartRAO 26m antenna currently monitors the following calibrators

.. list-table:: HartRAO monitored calibrator sources
   :widths: 15 10 30 15 10 10 15
   :header-rows: 2

   * - IVS 
     - J2000 
     - RA 
     - Dec 
     - Freq 
     - Freq 
     - Obs./Central 
  
   * -  name
     -  name
     - [deg]
     - [deg]
     - band
     - range
     - freqs[GHz]
  
   * - -
     - Jupiter
     - -
     - -
     - K 
     - -
     - 20.346, 20.971, 22, 23.121
  
   * - 0433+296
     - 3C123
     - 69.26
     - 29.67
     - - 
     - -
     - 1.668, 2.28, 4.874, 6.7, 8.4, 12.2

   * - 0134+329 (J0137+3309) 
     - 3C48
     - 24.42
     - 33.15
     - - 
     - -
     - 2.28, 4.874, 8.4
  
   * - 0624-058
     - 3C161
     - 96.79
     - -5.88
     - -
     - -
     - 2.28, 4.874, 8.4
  
   * - 1328+307 (J1331+3030)
     - 3C286
     - 202.78
     - 30.50
     - -
     - -
     - 4.874, 8.4
  
   * - 0915-11
     - HYDRA A (3C218)
     - 139.52
     - -12.09
     - -
     - -
     - 1.668, 2.28, 4.874, 6.7, 8.4, 12.2
  
   * - -
     - TAURUS A
     - 83.63
     - 22.01
     - - 
     - -
     - 1668
  
   * - 1228+127
     - VIRGO A (3C274)
     - 187.80
     - 12.39
     - - 
     - -
     - 4.874, 6.7, 8.4, 12.2, 20.346, 20.971, 22, 23.121
  
   


.. list-table:: HartRAO observing parameters
   :widths: 10 10 10 10 10
   :header-rows: 1

   * - Freq. band 
     - Wavelength [cm]
     - Freq. range 
     - Bandwidth 
     - Central freq. 
  
   * - L
     - 18 
     - 1000 - 2000
     - -
     - 1668 
   * - S
     - 13 
     - 2000 - 4000
     - -
     - 2280
   * - C
     - 6 
     - 4000 - 8000
     - -
     - 4800, 5040
   * - X
     - 3.5 
     - 8000 - 12000
     - -
     - 8280, 8400
   * - Ku
     - 2.5 
     - 12000 - 18000
     - -
     - 12218, 12178 
   * - K
     - 1.3 
     - 18000 - 23000
     - -
     - 23000

The radio astronomy flux-density scale has long been based on the polynomial 
expressions given in `Ott et al. (1994) <https://articles.adsabs.harvard.edu/cgi-bin/nph-iarticle_query?1994A%26A...284..331O&defaultprint=YES&filetype=.pdf>`_ . 

.. math::
    :name: flux density

    log(S_{\nu}) = a_{0} + a_{1}*log(\nu) + a_{2}*log^{2}(\nu) [MHz]

The ``flux density`` equation

To calibrate HartRAO data, select one of the following paths:

  1. :doc:`calibration/s-band`
  2. :doc:`calibration/cx-band`
  3. :doc:`calibration/maser-band`
  4. :doc:`calibration/ku-band`
  5. :doc:`calibration/k-band`