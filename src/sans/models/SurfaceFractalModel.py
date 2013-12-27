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
            src\sans\models\include\surfacefractal.h
         AND RE-RUN THE GENERATOR SCRIPT
"""

from sans.models.BaseComponent import BaseComponent
from sans.models.sans_extension.c_models import CSurfaceFractalModel

def create_SurfaceFractalModel():
    """
       Create a model instance
    """
    obj = SurfaceFractalModel()
    # CSurfaceFractalModel.__init__(obj) is called by
    # the SurfaceFractalModel constructor
    return obj

class SurfaceFractalModel(CSurfaceFractalModel, BaseComponent):
    """ 
    Class that evaluates a SurfaceFractalModel model. 
    This file was auto-generated from src\sans\models\include\surfacefractal.h.
    Refer to that file and the structure it contains
    for details of the model.
    List of default parameters:
         scale           = 1.0 
         radius          = 10.0 [A]
         surface_dim     = 2.0 
         co_length       = 500.0 [A]
         background      = 0.0 

    """
        
    def __init__(self, multfactor=1):
        """ Initialization """
        self.__dict__ = {}
        
        # Initialize BaseComponent first, then sphere
        BaseComponent.__init__(self)
        #apply(CSurfaceFractalModel.__init__, (self,)) 

        CSurfaceFractalModel.__init__(self)
        self.is_multifunc = False
		        
        ## Name of the model
        self.name = "SurfaceFractalModel"
        ## Model description
        self.description = """
         The scattering intensity  I(x) = scale*P(x)*S(x) + background, where
		scale = scale_factor  * V * delta^(2)
		p(x)=  F(x*radius)^(2)
		F(x) = 3*[sin(x)-x cos(x)]/x**3
		S(x) = [(gamma(5-Ds)*colength^(5-Ds)*[1+(x^2*colength^2)]^((Ds-5)/2)
		* sin[(Ds-5)*arctan(x*colength)])/x]
		where delta = sldParticle -sldSolv.
		radius       =  Particle radius
		surface_dim  =  Surface fractal dimension (Ds)
		co_length  =  Cut-off length
		background   =  background
		Ref.:Mildner, Hall,J Phys D Appl Phys(1986), 19, 1535-1545
		Note I: This model is valid for 1<surface_dim<3 with limited q range.
		Note II: This model is not in absolute scale.
        """
       
        ## Parameter details [units, min, max]
        self.details = {}
        self.details['scale'] = ['', None, None]
        self.details['radius'] = ['[A]', None, None]
        self.details['surface_dim'] = ['', None, None]
        self.details['co_length'] = ['[A]', None, None]
        self.details['background'] = ['', None, None]

        ## fittable parameters
        self.fixed = []
        
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
        return (create_SurfaceFractalModel, tuple(), state, None, None)
        
    def clone(self):
        """ Return a identical copy of self """
        return self._clone(SurfaceFractalModel())   
       	
    def run(self, x=0.0):
        """ 
        Evaluate the model
        
        :param x: input q, or [q,phi]
        
        :return: scattering function P(q)
        
        """
        return CSurfaceFractalModel.run(self, x)
   
    def runXY(self, x=0.0):
        """ 
        Evaluate the model in cartesian coordinates
        
        :param x: input q, or [qx, qy]
        
        :return: scattering function P(q)
        
        """
        return CSurfaceFractalModel.runXY(self, x)
        
    def evalDistribution(self, x):
        """ 
        Evaluate the model in cartesian coordinates
        
        :param x: input q[], or [qx[], qy[]]
        
        :return: scattering function P(q[])
        
        """
        return CSurfaceFractalModel.evalDistribution(self, x)
        
    def calculate_ER(self):
        """ 
        Calculate the effective radius for P(q)*S(q)
        
        :return: the value of the effective radius
        
        """       
        return CSurfaceFractalModel.calculate_ER(self)
        
    def calculate_VR(self):
        """ 
        Calculate the volf ratio for P(q)*S(q)
        
        :return: the value of the volf ratio
        
        """       
        return CSurfaceFractalModel.calculate_VR(self)
              
    def set_dispersion(self, parameter, dispersion):
        """
        Set the dispersion object for a model parameter
        
        :param parameter: name of the parameter [string]
        :param dispersion: dispersion object of type DispersionModel
        
        """
        return CSurfaceFractalModel.set_dispersion(self,
               parameter, dispersion.cdisp)
        
   
# End of file

