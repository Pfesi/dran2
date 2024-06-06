Installation 
============

The DRAN program was developed using the anaconda virtual environment.
Running the code on a virtual environment is highly recommended to avoid 
package clashes, 
and the following installation shows how to do this using 
`anaconda <https://www.anaconda.com/products/individual>`_. 
Anaconda is a data science toolkit with a wide variety of open-source packages and 
and libraries under one hub for building powerful projects.

.. note::
  There is an issue with the installation of pyqt5 (the library required to run the GUI) on some machines while 
  loading the requirements file during program installation. Thus it is highly 
  recommended that the user utilizes an anaconda installation or a virtual environment of their choice
  when installing the program.
  Please also note that the software has only been tested on anaconda so using a different virtual 
  enviroment server might not work.  
  
Installing and running dran in an anaconda virtual environment
---------------------------------------------------------------

First you will need to `download anaconda <https://www.anaconda.com/products/individual>`_ and install it on your machine.
Once installed you will create the dran virtual environment and activate it
using the following commands 

.. code:: bash
 
   $ mkdir dran
   $ cd dran
   $ conda create --name dran --file requests.txt
   $ conda activate dran

Alternatively, you can use the pypi package manager 

.. code:: bash
 
   $ pip install dran

Once your virtual environment is activated. You can now head over 
to :doc:`tuts/tutorials` to start using DRAN.


.. note:: 
   The program has not been tested on pyenv or env yet. This is planned for future releases.