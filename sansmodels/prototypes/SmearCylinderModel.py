#!/usr/bin/env python
""" Provide functionality for a C extension model

	WARNING: THIS FILE WAS GENERATED BY WRAPPERGENERATOR.PY
 	         DO NOT MODIFY THIS FILE, MODIFY smeared_cylinder.h
 	         AND RE-RUN THE GENERATOR SCRIPT

    @author: Mathieu Doucet / UTK
    @contact: mathieu.doucet@nist.gov
"""

from sans.models.BaseComponent import BaseComponent
from sans_extension.prototypes.c_models import CSmearCylinderModel
import copy    
    
class SmearCylinderModel(CSmearCylinderModel, BaseComponent):
    """ Class that evaluates a SmearCylinderModel model. 
    	This file was auto-generated from smeared_cylinder.h.
    	Refer to that file and the structure it contains
    	for details of the model.
    	List of default parameters:
         scale           = 1.0 
         radius          = 20.0 A
         length          = 400.0 A
         contrast        = 3e-006 A-2
         background      = 0.0 cm-1
         cyl_theta       = 1.0 rad
         cyl_phi         = 1.0 rad
         cyl_phi         = 0.0 rad
         sigma_theta     = 0.0 rad
         sigma_phi       = 0.0 rad
         sigma_radius    = 0.0 rad

    """
        
    def __init__(self):
        """ Initialization """
        
        # Initialize BaseComponent first, then sphere
        BaseComponent.__init__(self)
        CSmearCylinderModel.__init__(self)
        
        ## Name of the model
        self.name = "SmearCylinderModel"
   
    def clone(self):
        """ Return a identical copy of self """
        obj = SmearCylinderModel()
        obj.params = copy.deepcopy(self.params)
        return obj   
   
    def run(self, x = 0.0):
        """ Evaluate the model
            @param x: input q, or [q,phi]
            @return: scattering function P(q)
        """
        
        return CSmearCylinderModel.run(self, x)
   
# End of file