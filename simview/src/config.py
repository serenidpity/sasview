"""
    SimView Application settings
"""
import time

# Version of the application
__appname__ = "SimView"
__version__ = '0.2.0'
__download_page__ = 'http://danse.chem.utk.edu'
__update_URL__ = 'http://danse.chem.utk.edu/simview_version.php'


# Debug message flag
__EVT_DEBUG__ = True

# Flag for automated testing
__TEST__ = __EVT_DEBUG__

# Debug message should be written to a file?
__EVT_DEBUG_2_FILE__   = False
__EVT_DEBUG_FILENAME__ = "debug.log"

# About box info
_do_aboutbox=True
_acknowledgement =  \
'''This software was developed by the University of Tennessee as part of the
Distributed Data Analysis of Neutron Scattering Experiments (DANSE)
project funded by the US National Science Foundation. 

'''
_homepage = "http://danse.chem.utk.edu"
_download = "http://danse.chem.utk.edu/simview.html"
_authors = []
_paper = "http://danse.us/trac/sans/newticket"
_license = "mailto:sansdanse@gmail.com"

_nsf_logo = "images/nsf_logo.png"
_danse_logo = "images/danse_logo.png"
_inst_logo = "images/utlogo.gif"
_nsf_url = "http://www.nsf.gov"
_danse_url = "http://www.cacr.caltech.edu/projects/danse/release/index.html"
_inst_url = "http://www.utk.edu"
_corner_image = "images/angles_flat.png"
_welcome_image = "images/SVwelcome.png"
_copyright = "(c) 2009, University of Tennessee"

def printEVT(message):
    if __EVT_DEBUG__:
        print "%g:  %s" % (time.clock(), message)
        
        if __EVT_DEBUG_2_FILE__:
            out = open(__EVT_DEBUG_FILENAME__, 'a')
            out.write("%10g:  %s\n" % (time.clock(), message))
            out.close()
            