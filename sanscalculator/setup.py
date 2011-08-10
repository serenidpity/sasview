"""
    Setup for Calculator plug-in
"""

from distutils.core import setup
import sys
if len(sys.argv) == 1:
    sys.argv.append('install')
setup(
    name="sans.calculator",
    version = "0.9.1",
    description = "Python module for sld  calculation",
    author = "University of Tennessee",
    url = "http://danse.chem.utk.edu",

    # Use the pure python modules
    package_dir = {"sans":"src/sans",
                   "sans.calculator":"src/sans/calculator"},
    packages = ["sans", "sans.calculator"],
    )