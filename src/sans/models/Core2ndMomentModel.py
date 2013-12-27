##############################################################################
# This software was developed by the University of Tennessee as part of the
# Distributed Data Analysis of Neutron Scattering Experiments (DANSE)
# project funded by the US National Science Foundation.
#
# If you use DANSE applications to do scientific research that leads to
# publication, we ask that you acknowledge the use of the software with the
# following sentence:
#
# This work benefited from DANSE software developed under NSF award DMR-0520547
#
# Copyright 2008-2011, University of Tennessee
##############################################################################

""" 
Provide functionality for a C extension model

:WARNING: THIS FILE WAS GENERATED BY WRAPPERGENERATOR.PY
         DO NOT MODIFY THIS FILE, MODIFY
            src\sans\models\include\coresecondmoment.h
         AND RE-RUN THE GENERATOR SCRIPT
"""

from sans.models.BaseComponent import BaseComponent
from sans.models.sans_extension.c_models import CCore2ndMomentModel

def create_Core2ndMomentModel():
    """
       Create a model instance
    """
    obj = Core2ndMomentModel()
    # CCore2ndMomentModel.__init__(obj) is called by
    # the Core2ndMomentModel constructor
    return obj

class Core2ndMomentModel(CCore2ndMomentModel, BaseComponent):
    """ 
    Class that evaluates a Core2ndMomentModel model. 
    This file was auto-generated from src\sans\models\include\coresecondmoment.h.
    Refer to that file and the structure it contains
    for details of the model.
    List of default parameters:
         scale           = 1.0 
         density_poly    = 0.7 [g/cm^(3)]
         sld_poly        = 1.5e-06 [1/A^(2)]
         radius_core     = 500.0 [A]
         volf_cores      = 0.14 
         ads_amount      = 1.9 [mg/m^(2)]
         sld_solv        = 6.3e-06 [1/A^(2)]
         second_moment   = 23.0 [A]
         background      = 0.0 [1/cm]

    """
        
    def __init__(self, multfactor=1):
        """ Initialization """
        self.__dict__ = {}
        
        # Initialize BaseComponent first, then sphere
        BaseComponent.__init__(self)
        #apply(CCore2ndMomentModel.__init__, (self,)) 

        CCore2ndMomentModel.__init__(self)
        self.is_multifunc = False
		        
        ## Name of the model
        self.name = "Core2ndMomentModel"
        ## Model description
        self.description = """
        Calculate CoreSecondMoment Model
		
		scale:calibration factor,
		density_poly: density of the layer
		sld_poly: the SLD of the layer
		volf_cores: volume fraction of cores
		ads_amount: adsorbed amount
		second_moment: second moment of the layer
		sld_solv: the SLD of the solvent
		background
		
        """
       
        ## Parameter details [units, min, max]
        self.details = {}
        self.details['scale'] = ['', None, None]
        self.details['density_poly'] = ['[g/cm^(3)]', None, None]
        self.details['sld_poly'] = ['[1/A^(2)]', None, None]
        self.details['radius_core'] = ['[A]', None, None]
        self.details['volf_cores'] = ['', None, None]
        self.details['ads_amount'] = ['[mg/m^(2)]', None, None]
        self.details['sld_solv'] = ['[1/A^(2)]', None, None]
        self.details['second_moment'] = ['[A]', None, None]
        self.details['background'] = ['[1/cm]', None, None]

        ## fittable parameters
        self.fixed = ['radius_core.width']
        
        ## non-fittable parameters
        self.non_fittable = []
        
        ## parameters with orientation
        self.orientation_params = []

        ## parameters with magnetism
        self.magnetic_params = []

        self.category = None
        self.multiplicity_info = None
        
    def __setstate__(self, state):
        """
        restore the state of a model from pickle
        """
        self.__dict__, self.params, self.dispersion = state
        
    def __reduce_ex__(self, proto):
        """
        Overwrite the __reduce_ex__ of PyTypeObject *type call in the init of 
        c model.
        """
        state = (self.__dict__, self.params, self.dispersion)
        return (create_Core2ndMomentModel, tuple(), state, None, None)
        
    def clone(self):
        """ Return a identical copy of self """
        return self._clone(Core2ndMomentModel())   
       	
    def run(self, x=0.0):
        """ 
        Evaluate the model
        
        :param x: input q, or [q,phi]
        
        :return: scattering function P(q)
        
        """
        return CCore2ndMomentModel.run(self, x)
   
    def runXY(self, x=0.0):
        """ 
        Evaluate the model in cartesian coordinates
        
        :param x: input q, or [qx, qy]
        
        :return: scattering function P(q)
        
        """
        return CCore2ndMomentModel.runXY(self, x)
        
    def evalDistribution(self, x):
        """ 
        Evaluate the model in cartesian coordinates
        
        :param x: input q[], or [qx[], qy[]]
        
        :return: scattering function P(q[])
        
        """
        return CCore2ndMomentModel.evalDistribution(self, x)
        
    def calculate_ER(self):
        """ 
        Calculate the effective radius for P(q)*S(q)
        
        :return: the value of the effective radius
        
        """       
        return CCore2ndMomentModel.calculate_ER(self)
        
    def calculate_VR(self):
        """ 
        Calculate the volf ratio for P(q)*S(q)
        
        :return: the value of the volf ratio
        
        """       
        return CCore2ndMomentModel.calculate_VR(self)
              
    def set_dispersion(self, parameter, dispersion):
        """
        Set the dispersion object for a model parameter
        
        :param parameter: name of the parameter [string]
        :param dispersion: dispersion object of type DispersionModel
        
        """
        return CCore2ndMomentModel.set_dispersion(self,
               parameter, dispersion.cdisp)
        
   
# End of file

