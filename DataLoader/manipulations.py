
#####################################################################
#This software was developed by the University of Tennessee as part of the
#Distributed Data Analysis of Neutron Scattering Experiments (DANSE)
#project funded by the US National Science Foundation. 
#See the license text in license.txt
#copyright 2008, University of Tennessee
######################################################################

"""
Data manipulations for 2D data sets.
Using the meta data information, various types of averaging
are performed in Q-space 
"""
#TODO: copy the meta data from the 2D object to the resulting 1D object
import math
import numpy

#from data_info import plottable_2D
from data_info import Data1D


def get_q(dx, dy, det_dist, wavelength):
    """
    :param dx: x-distance from beam center [mm]
    :param dy: y-distance from beam center [mm]
    
    :return: q-value at the given position
    """
    # Distance from beam center in the plane of detector
    plane_dist = math.sqrt(dx*dx + dy*dy)
    # Half of the scattering angle
    theta = 0.5 * math.atan(plane_dist/det_dist)
    return (4.0 * math.pi/wavelength) * math.sin(theta)

def get_q_compo(dx, dy, det_dist, wavelength, compo=None):
    """
    This reduces tiny error at very large q.
    Implementation of this func is not started yet.<--ToDo
    """
    if dy == 0:
        if dx >= 0:
            angle_xy = 0
        else:
            angle_xy = math.pi
    else:
        angle_xy = math.atan(dx/dy)
        
    if compo == "x":
        out = get_q(dx, dy, det_dist, wavelength) * math.cos(angle_xy)
    elif compo == "y":
        out = get_q(dx, dy, det_dist, wavelength) * math.sin(angle_xy)
    else:
        out = get_q(dx, dy, det_dist, wavelength)
    return out

def flip_phi(phi):
    """
    Correct phi to within the 0 <= to <= 2pi range
    
    :return: phi in >=0 and <=2Pi
    """
    Pi = math.pi
    if phi < 0:
        phi_out = phi  + (2 * Pi)
    elif phi > (2 * Pi):
        phi_out = phi  - (2 * Pi)
    else:
        phi_out = phi 
    return phi_out

def reader2D_converter(data2d=None):
    """
    convert old 2d format opened by IhorReader or danse_reader
    to new Data2D format
    
    :param data2d: 2d array of Data2D object
    
    :return: 1d arrays of Data2D object
    
    """
    if data2d.data == None or data2d.x_bins == None or data2d.y_bins == None:
        raise ValueError, "Can't convert this data: data=None..."
    
    from DataLoader.data_info import Data2D

    new_x = numpy.tile(data2d.x_bins, (len(data2d.y_bins), 1))
    new_y = numpy.tile(data2d.y_bins, (len(data2d.x_bins), 1))
    new_y = new_y.swapaxes(0, 1)

    new_data = data2d.data.flatten()
    qx_data = new_x.flatten()
    qy_data = new_y.flatten()
    q_data = numpy.sqrt(qx_data*qx_data + qy_data*qy_data)
    if data2d.err_data == None or numpy.any(data2d.err_data <= 0): 
        new_err_data = numpy.sqrt(numpy.abs(new_data))
    else:
        new_err_data = data2d.err_data.flatten()
    mask    = numpy.ones(len(new_data), dtype=bool)

    output = Data2D()
    output = data2d
    output.data = new_data
    output.err_data = new_err_data
    output.qx_data = qx_data
    output.qy_data = qy_data
    output.q_data = q_data
    output.mask = mask

    return output

class _Slab(object):
    """
    Compute average I(Q) for a region of interest
    """
    def __init__(self, x_min=0.0, x_max=0.0, y_min=0.0,
                 y_max=0.0, bin_width=0.001):
        # Minimum Qx value [A-1]
        self.x_min = x_min
        # Maximum Qx value [A-1]
        self.x_max = x_max
        # Minimum Qy value [A-1]
        self.y_min = y_min
        # Maximum Qy value [A-1]
        self.y_max = y_max
        # Bin width (step size) [A-1]
        self.bin_width = bin_width
        # If True, I(|Q|) will be return, otherwise,
        # negative q-values are allowed
        self.fold = False
        
    def __call__(self, data2D):
        return NotImplemented
        
    def _avg(self, data2D, maj):
        """
        Compute average I(Q_maj) for a region of interest.
        The major axis is defined as the axis of Q_maj.
        The minor axis is the axis that we average over.
         
        :param data2D: Data2D object
        :param maj_min: min value on the major axis
        
        :return: Data1D object
        """
        if len(data2D.detector) != 1:
            msg = "_Slab._avg: invalid number of "
            msg += " detectors: %g" % len(data2D.detector)
            raise RuntimeError, msg
        
        # Get data 
        data = data2D.data[numpy.isfinite(data2D.data)]
        q_data = data2D.q_data[numpy.isfinite(data2D.data)]
        err_data = data2D.err_data[numpy.isfinite(data2D.data)]
        qx_data = data2D.qx_data[numpy.isfinite(data2D.data)] 
        qy_data = data2D.qy_data[numpy.isfinite(data2D.data)]
             
        # Build array of Q intervals
        if maj == 'x':
            if self.fold:
                x_min = 0     
            else:  x_min = self.x_min
            nbins = int(math.ceil((self.x_max - x_min)/self.bin_width))
            qbins = self.bin_width * numpy.arange(nbins) + x_min
        elif maj == 'y':
            if self.fold: y_min = 0     
            else:  y_min = self.y_min
            nbins = int(math.ceil((self.y_max - y_min)/self.bin_width))
            qbins = self.bin_width * numpy.arange(nbins) + y_min          
        else:
            raise RuntimeError, "_Slab._avg: unrecognized axis %s" % str(maj)
                                
        x  = numpy.zeros(nbins)
        y  = numpy.zeros(nbins)
        err_y = numpy.zeros(nbins)
        y_counts = numpy.zeros(nbins)

        # Average pixelsize in q space                                                
        for npts in range(len(data)): 
            # default frac                                               
            frac_x = 0
            frac_y = 0
            # get ROI
            if self.x_min <= qx_data[npts] and self.x_max > qx_data[npts]:
                frac_x = 1
            if self.y_min <= qy_data[npts] and self.y_max > qy_data[npts]:
                frac_y = 1
            frac = frac_x * frac_y
            
            if frac == 0:
                continue
            # binning: find axis of q
            if maj == 'x': 
                q_value = qx_data[npts]
                min = x_min 
            if maj == 'y': 
                q_value = qy_data[npts] 
                min = y_min 
            if self.fold and q_value < 0:
                q_value = -q_value   
            # bin
            i_q = int(math.ceil((q_value - min)/self.bin_width)) - 1
            
            # skip outside of max bins
            if i_q < 0 or i_q >= nbins:
                continue
            
            # give it full weight
            #frac = 1 
            
            #TODO: find better definition of x[i_q] based on q_data
            x[i_q] += frac * q_value#min + (i_q + 1) * self.bin_width / 2.0
            y[i_q] += frac * data[npts]
            
            if err_data == None or err_data[npts] == 0.0:
                if data[npts] < 0: data[npts] = -data[npts]
                err_y[i_q] += frac * frac * data[npts]
            else:
                err_y[i_q] += frac * frac * err_data[npts] * err_data[npts]
            y_counts[i_q]  += frac
                
        # Average the sums       
        for n in range(nbins):
            err_y[n] = math.sqrt(err_y[n])
          
        err_y = err_y / y_counts
        y    = y / y_counts
        x    = x / y_counts
        idx = (numpy.isfinite(y) & numpy.isfinite(x)) 
        
        if not idx.any(): 
            msg = "Average Error: No points inside ROI to average..." 
            raise ValueError, msg
        #elif len(y[idx])!= nbins:
        #    msg = "empty bin(s) due to tight binning..."
        #    print "resulted",nbins- len(y[idx]), msg
        return Data1D(x=x[idx], y=y[idx], dy=err_y[idx])
        
class SlabY(_Slab):
    """
    Compute average I(Qy) for a region of interest
    """
    def __call__(self, data2D):
        """
        Compute average I(Qy) for a region of interest
         
        :param data2D: Data2D object
        
        :return: Data1D object
        """
        return self._avg(data2D, 'y')
        
class SlabX(_Slab):
    """
    Compute average I(Qx) for a region of interest
    """
    def __call__(self, data2D):
        """
        Compute average I(Qx) for a region of interest
         
        :param data2D: Data2D object
        
        :return: Data1D object
        
        """
        return self._avg(data2D, 'x') 
        
class Boxsum(object):
    """
    Perform the sum of counts in a 2D region of interest.
    """
    def __init__(self, x_min=0.0, x_max=0.0, y_min=0.0, y_max=0.0):
        # Minimum Qx value [A-1]
        self.x_min = x_min
        # Maximum Qx value [A-1]
        self.x_max = x_max
        # Minimum Qy value [A-1]
        self.y_min = y_min
        # Maximum Qy value [A-1]
        self.y_max = y_max

    def __call__(self, data2D):
        """
        Perform the sum in the region of interest 
         
        :param data2D: Data2D object
        
        :return: number of counts, error on number of counts
        
        """
        y, err_y, y_counts = self._sum(data2D)
        
        # Average the sums
        counts = 0 if y_counts == 0 else y
        error  = 0 if y_counts == 0 else math.sqrt(err_y)
        
        return counts, error
        
    def _sum(self, data2D):
        """
        Perform the sum in the region of interest 
        
        :param data2D: Data2D object
        
        :return: number of counts, 
            error on number of counts, number of entries summed
        
        """
        if len(data2D.detector) != 1:
            msg = "Circular averaging: invalid number "
            msg += "of detectors: %g" % len(data2D.detector)
            raise RuntimeError, msg
        # Get data 
        data = data2D.data[numpy.isfinite(data2D.data)]
        q_data = data2D.q_data[numpy.isfinite(data2D.data)]
        err_data = data2D.err_data[numpy.isfinite(data2D.data)]
        qx_data = data2D.qx_data[numpy.isfinite(data2D.data)] 
        qy_data = data2D.qy_data[numpy.isfinite(data2D.data)]
   
        y  = 0.0
        err_y = 0.0
        y_counts = 0.0

        # Average pixelsize in q space                                                
        for npts in range(len(data)): 
            # default frac                                               
            frac_x = 0 
            frac_y = 0                 
            
            # get min and max at each points
            qx = qx_data[npts]
            qy = qy_data[npts]
            
            # get the ROI
            if self.x_min <= qx and self.x_max > qx:
                frac_x = 1
            if self.y_min <= qy and self.y_max > qy:
                frac_y = 1
            #Find the fraction along each directions            
            frac = frac_x * frac_y
            if frac == 0:
                continue
            y += frac * data[npts]
            if err_data == None or err_data[npts] == 0.0:
                if data[npts] < 0:
                    data[npts] = -data[npts]
                err_y += frac * frac * data[npts]
            else:
                err_y += frac * frac * err_data[npts] * err_data[npts]
            y_counts += frac     
        return y, err_y, y_counts


      
class Boxavg(Boxsum):
    """
    Perform the average of counts in a 2D region of interest.
    """
    def __init__(self, x_min=0.0, x_max=0.0, y_min=0.0, y_max=0.0):
        super(Boxavg, self).__init__(x_min=x_min, x_max=x_max,
                                      y_min=y_min, y_max=y_max)

    def __call__(self, data2D):
        """
        Perform the sum in the region of interest 
         
        :param data2D: Data2D object
        
        :return: average counts, error on average counts
        
        """
        y, err_y, y_counts = self._sum(data2D)
        
        # Average the sums
        counts = 0 if y_counts == 0 else y/y_counts
        error  = 0 if y_counts == 0 else math.sqrt(err_y)/y_counts
        
        return counts, error
        
def get_pixel_fraction_square(x, xmin, xmax):
    """
    Return the fraction of the length 
    from xmin to x.::
   
     
           A            B
       +-----------+---------+
       xmin        x         xmax
     
    :param x: x-value
    :param xmin: minimum x for the length considered
    :param xmax: minimum x for the length considered
    
    :return: (x-xmin)/(xmax-xmin) when xmin < x < xmax
    
    """
    if x <= xmin:
        return 0.0
    if x > xmin and x < xmax:
        return (x - xmin) / (xmax - xmin)
    else:
        return 1.0


class CircularAverage(object):
    """
    Perform circular averaging on 2D data
    
    The data returned is the distribution of counts
    as a function of Q
    """
    def __init__(self, r_min=0.0, r_max=0.0, bin_width=0.0005):
        # Minimum radius included in the average [A-1]
        self.r_min = r_min
        # Maximum radius included in the average [A-1]
        self.r_max = r_max
        # Bin width (step size) [A-1]
        self.bin_width = bin_width

    def __call__(self, data2D):
        """
        Perform circular averaging on the data
        
        :param data2D: Data2D object
        
        :return: Data1D object
        """
        # Get data W/ finite values
        data = data2D.data[numpy.isfinite(data2D.data)]
        q_data = data2D.q_data[numpy.isfinite(data2D.data)]
        qx_data = data2D.qx_data[numpy.isfinite(data2D.data)]
        err_data = data2D.err_data[numpy.isfinite(data2D.data)]
        
        dq_data = None
        
        # Get the dq for resolution averaging
        if data2D.dqx_data != None and data2D.dqy_data != None:
            # The pinholes and det. pix contribution present 
            # in both direction of the 2D which must be subtracted when
            # converting to 1D: dq_overlap should calculated ideally at
            # q = 0. Note This method works on only pinhole geometry. 
            # Extrapolate dqx(r) and dqy(phi) at q = 0, and take an average.
            z_max = max(data2D.q_data)
            z_min = min(data2D.q_data)
            x_max = data2D.dqx_data[data2D.q_data[z_max]]
            x_min = data2D.dqx_data[data2D.q_data[z_min]]    
            y_max = data2D.dqy_data[data2D.q_data[z_max]]
            y_min = data2D.dqy_data[data2D.q_data[z_min]]          
            # Find qdx at q = 0
            dq_overlap_x = (x_min * z_max - x_max * z_min) / (z_max - z_min)
            # when extrapolation goes wrong
            if dq_overlap_x > min(data2D.dqx_data):
                dq_overlap_x = min(data2D.dqx_data)
            dq_overlap_x *= dq_overlap_x 
            # Find qdx at q = 0
            dq_overlap_y = (y_min * z_max - y_max * z_min) / (z_max - z_min)
            # when extrapolation goes wrong
            if dq_overlap_y > min(data2D.dqy_data):
                dq_overlap_y = min(data2D.dqy_data)
            # get dq at q=0.
            dq_overlap_y *= dq_overlap_y

            dq_overlap = numpy.sqrt((dq_overlap_x + dq_overlap_y)/2.0)
            # Final protection of dq
            if dq_overlap < 0:
                dq_overlap = y_min
            dqx_data = data2D.dqx_data[numpy.isfinite(data2D.data)]
            dqy_data = data2D.dqy_data[numpy.isfinite(data2D.data)] - dq_overlap
            # def; dqx_data = dq_r dqy_data = dq_phi
            # Convert dq 2D to 1D here
            dqx = dqx_data * dqx_data            
            dqy = dqy_data * dqy_data
            dq_data = numpy.add(dqx, dqy)
            dq_data = numpy.sqrt(dq_data)
            
        #q_data_max = numpy.max(q_data)
        if len(data2D.q_data) == None:
            msg = "Circular averaging: invalid q_data: %g" % data2D.q_data
            raise RuntimeError, msg

        # Build array of Q intervals
        nbins = int(math.ceil((self.r_max - self.r_min) / self.bin_width))
        qbins = self.bin_width * numpy.arange(nbins) + self.r_min

        x  = numpy.zeros(nbins)
        y  = numpy.zeros(nbins)
        err_y = numpy.zeros(nbins)
        err_x = numpy.zeros(nbins)
        y_counts = numpy.zeros(nbins)

        for npt in range(len(data)):          
            frac = 0
            
            # q-value at the pixel (j,i)
            q_value = q_data[npt] 
            data_n = data[npt]                
            
            ## No need to calculate the frac when all data are within range
            if self.r_min >= self.r_max:
                raise ValueError, "Limit Error: min > max" 
            
            if self.r_min <= q_value and q_value <= self.r_max:
                frac = 1                       
            if frac == 0:
                continue 
            i_q = int(math.floor((q_value - self.r_min) / self.bin_width))    

            # Take care of the edge case at phi = 2pi. 
            if i_q == nbins:  
                i_q = nbins -1              
            y[i_q] += frac * data_n
            # Take dqs from data to get the q_average
            x[i_q] += frac * q_value
            if err_data == None or err_data[npt] == 0.0:
                if data_n < 0:
                    data_n = -data_n
                err_y[i_q] += frac * frac * data_n
            else:
                err_y[i_q] += frac * frac * err_data[npt] * err_data[npt]
            if dq_data != None:
                # To be consistent with dq calculation in 1d reduction, 
                # we need just the averages (not quadratures) because 
                # it should not depend on the number of the q points 
                # in the qr bins.
                err_x[i_q] += frac * dq_data[npt]
            else:
                err_x = None
            y_counts[i_q]  += frac
        
        # Average the sums       
        for n in range(nbins):
            if err_y[n] < 0: err_y[n] = -err_y[n]
            err_y[n] = math.sqrt(err_y[n])
            #if err_x != None:
            #    err_x[n] = math.sqrt(err_x[n])
            
        err_y = err_y / y_counts
        err_y[err_y==0] = numpy.average(err_y)
        y    = y / y_counts
        x    = x / y_counts
        idx = (numpy.isfinite(y)) & (numpy.isfinite(x)) 
        if err_x != None:
            d_x = err_x[idx] / y_counts[idx]
        else:
            d_x = None

        if not idx.any(): 
            msg = "Average Error: No points inside ROI to average..." 
            raise ValueError, msg
        
        return Data1D(x=x[idx], y=y[idx], dy=err_y[idx], dx=d_x)
    

class Ring(object):
    """
    Defines a ring on a 2D data set.
    The ring is defined by r_min, r_max, and
    the position of the center of the ring.
    
    The data returned is the distribution of counts
    around the ring as a function of phi.
    
    Phi_min and phi_max should be defined between 0 and 2*pi 
    in anti-clockwise starting from the x- axis on the left-hand side
    """
    #Todo: remove center.
    def __init__(self, r_min=0, r_max=0, center_x=0, center_y=0, nbins=20):
        # Minimum radius
        self.r_min = r_min
        # Maximum radius
        self.r_max = r_max
        # Center of the ring in x
        self.center_x = center_x
        # Center of the ring in y
        self.center_y = center_y
        # Number of angular bins
        self.nbins_phi = nbins
        
    def __call__(self, data2D):
        """
        Apply the ring to the data set.
        Returns the angular distribution for a given q range
        
        :param data2D: Data2D object
        
        :return: Data1D object
        """
        if data2D.__class__.__name__ not in ["Data2D", "plottable_2D"]:
            raise RuntimeError, "Ring averaging only take plottable_2D objects"
        
        Pi = math.pi
 
        # Get data
        data = data2D.data[numpy.isfinite(data2D.data)]
        q_data = data2D.q_data[numpy.isfinite(data2D.data)]
        err_data = data2D.err_data[numpy.isfinite(data2D.data)]
        qx_data = data2D.qx_data[numpy.isfinite(data2D.data)] 
        qy_data = data2D.qy_data[numpy.isfinite(data2D.data)]
        
        q_data_max = numpy.max(q_data)
        
        # Set space for 1d outputs
        phi_bins   = numpy.zeros(self.nbins_phi)
        phi_counts = numpy.zeros(self.nbins_phi)
        phi_values = numpy.zeros(self.nbins_phi)
        phi_err    = numpy.zeros(self.nbins_phi)
        
        for npt in range(len(data)):          
            frac = 0
            # q-value at the point (npt)
            q_value = q_data[npt]
            data_n = data[npt]    
                        
            # phi-value at the point (npt)
            phi_value = math.atan2(qy_data[npt], qx_data[npt]) + Pi
            
            if self.r_min <= q_value and q_value <= self.r_max:
                frac = 1                       
            if frac == 0:
                continue
            # binning           
            i_phi = int(math.floor((self.nbins_phi) * phi_value / (2 * Pi)))
            
            # Take care of the edge case at phi = 2pi. 
            if i_phi == self.nbins_phi:  
                i_phi =  self.nbins_phi - 1                            
            phi_bins[i_phi] += frac * data[npt]
            
            if err_data == None or err_data[npt] == 0.0:
                if data_n < 0:
                    data_n = -data_n
                phi_err[i_phi] += frac * frac * math.fabs(data_n)
            else:
                phi_err[i_phi] += frac * frac * err_data[npt] * err_data[npt]
            phi_counts[i_phi] += frac
                          
        for i in range(self.nbins_phi):
            phi_bins[i] = phi_bins[i] / phi_counts[i]
            phi_err[i] = math.sqrt(phi_err[i]) / phi_counts[i]
            phi_values[i] = 2.0 * math.pi / self.nbins_phi * (1.0 * i + 0.5)
            
        idx = (numpy.isfinite(phi_bins)) 

        if not idx.any():
            msg = "Average Error: No points inside ROI to average..." 
            raise ValueError, msg
        #elif len(phi_bins[idx])!= self.nbins_phi:
        #    print "resulted",self.nbins_phi- len(phi_bins[idx])
        #,"empty bin(s) due to tight binning..."
        return Data1D(x=phi_values[idx], y=phi_bins[idx], dy=phi_err[idx])
    
def get_pixel_fraction(qmax, q_00, q_01, q_10, q_11):
    """
    Returns the fraction of the pixel defined by
    the four corners (q_00, q_01, q_10, q_11) that 
    has q < qmax.::
    
                q_01                q_11
        y=1         +--------------+
                    |              |
                    |              |
                    |              |
        y=0         +--------------+
                q_00                q_10
        
                    x=0            x=1
    
    """
    # y side for x = minx
    x_0 = get_intercept(qmax, q_00, q_01)
    # y side for x = maxx
    x_1 = get_intercept(qmax, q_10, q_11)
    
    # x side for y = miny
    y_0 = get_intercept(qmax, q_00, q_10)
    # x side for y = maxy
    y_1 = get_intercept(qmax, q_01, q_11)
    
    # surface fraction for a 1x1 pixel
    frac_max = 0
    
    if x_0 and x_1:
        frac_max = (x_0 + x_1) / 2.0
    elif y_0 and y_1:
        frac_max = (y_0 + y_1) / 2.0
    elif x_0 and y_0:
        if q_00 < q_10:
            frac_max = x_0 * y_0 / 2.0
        else:
            frac_max = 1.0 - x_0 * y_0 / 2.0
    elif x_0 and y_1:
        if q_00 < q_10:
            frac_max = x_0 * y_1 / 2.0
        else:
            frac_max = 1.0 - x_0 * y_1 / 2.0
    elif x_1 and y_0:
        if q_00 > q_10:
            frac_max = x_1 * y_0 / 2.0
        else:
            frac_max = 1.0 - x_1 * y_0 / 2.0
    elif x_1 and y_1:
        if q_00 < q_10:
            frac_max = 1.0 - (1.0 - x_1) * (1.0 - y_1) / 2.0
        else:
            frac_max = (1.0 - x_1) * (1.0 - y_1) / 2.0
            
    # If we make it here, there is no intercept between
    # this pixel and the constant-q ring. We only need
    # to know if we have to include it or exclude it.
    elif (q_00 + q_01 + q_10 + q_11)/4.0 < qmax:
        frac_max = 1.0

    return frac_max
             
def get_intercept(q, q_0, q_1):
    """
    Returns the fraction of the side at which the
    q-value intercept the pixel, None otherwise.
    The values returned is the fraction ON THE SIDE
    OF THE LOWEST Q. ::
    
    
            A           B    
        +-----------+--------+    <--- pixel size
        0                    1     
        Q_0 -------- Q ----- Q_1   <--- equivalent Q range
        if Q_1 > Q_0, A is returned
        if Q_1 < Q_0, B is returned
        if Q is outside the range of [Q_0, Q_1], None is returned
         
    """
    if q_1 > q_0:
        if (q > q_0 and q <= q_1):
            return (q - q_0)/(q_1 - q_0)    
    else:
        if (q > q_1 and q <= q_0):
            return (q - q_1)/(q_0 - q_1)
    return None
     
class _Sector:
    """
    Defines a sector region on a 2D data set.
    The sector is defined by r_min, r_max, phi_min, phi_max,
    and the position of the center of the ring 
    where phi_min and phi_max are defined by the right
    and left lines wrt central line
    and phi_max could be less than phi_min. 
   
    Phi is defined between 0 and 2*pi in anti-clockwise 
    starting from the x- axis on the left-hand side
    """
    def __init__(self, r_min, r_max, phi_min=0, phi_max=2*math.pi, nbins=20):
        self.r_min = r_min
        self.r_max = r_max
        self.phi_min = phi_min
        self.phi_max = phi_max
        self.nbins = nbins
        
    
    def _agv(self, data2D, run='phi'):
        """
        Perform sector averaging.
        
        :param data2D: Data2D object
        :param run:  define the varying parameter ('phi' , 'q' , or 'q2')
        
        :return: Data1D object
        """
        if data2D.__class__.__name__ not in ["Data2D", "plottable_2D"]:
            raise RuntimeError, "Ring averaging only take plottable_2D objects"
        Pi = math.pi

        # Get the all data & info
        data = data2D.data[numpy.isfinite(data2D.data)]
        q_data = data2D.q_data[numpy.isfinite(data2D.data)]
        err_data = data2D.err_data[numpy.isfinite(data2D.data)]
        qx_data = data2D.qx_data[numpy.isfinite(data2D.data)] 
        qy_data = data2D.qy_data[numpy.isfinite(data2D.data)]
        dq_data = None
            
        # Get the dq for resolution averaging
        if data2D.dqx_data != None and data2D.dqy_data != None:
            # The pinholes and det. pix contribution present 
            # in both direction of the 2D which must be subtracted when
            # converting to 1D: dq_overlap should calculated ideally at
            # q = 0. 
            # Extrapolate dqy(perp) at q = 0
            z_max = max(data2D.q_data)
            z_min = min(data2D.q_data)
            x_max = data2D.dqx_data[data2D.q_data[z_max]]
            x_min = data2D.dqx_data[data2D.q_data[z_min]]    
            y_max = data2D.dqy_data[data2D.q_data[z_max]]
            y_min = data2D.dqy_data[data2D.q_data[z_min]]          
            # Find qdx at q = 0
            dq_overlap_x = (x_min * z_max - x_max * z_min) / (z_max - z_min)
            # when extrapolation goes wrong
            if dq_overlap_x > min(data2D.dqx_data):
                dq_overlap_x = min(data2D.dqx_data)
            dq_overlap_x *= dq_overlap_x 
            # Find qdx at q = 0
            dq_overlap_y = (y_min * z_max - y_max * z_min) / (z_max - z_min)
            # when extrapolation goes wrong
            if dq_overlap_y > min(data2D.dqy_data):
                dq_overlap_y = min(data2D.dqy_data)
            # get dq at q=0.
            dq_overlap_y *= dq_overlap_y

            dq_overlap = numpy.sqrt((dq_overlap_x + dq_overlap_y) / 2.0)  
            if dq_overlap < 0:
                dq_overlap = y_min
            dqx_data = data2D.dqx_data[numpy.isfinite(data2D.data)]
            dqy_data = data2D.dqy_data[numpy.isfinite(data2D.data)] - dq_overlap
            # def; dqx_data = dq_r dqy_data = dq_phi
            # Convert dq 2D to 1D here
            dqx = dqx_data * dqx_data            
            dqy = dqy_data * dqy_data
            dq_data = numpy.add(dqx, dqy)
            dq_data = numpy.sqrt(dq_data)
            
        #set space for 1d outputs
        x        = numpy.zeros(self.nbins)
        y        = numpy.zeros(self.nbins)
        y_err    = numpy.zeros(self.nbins)   
        x_err    = numpy.zeros(self.nbins)      
        y_counts = numpy.zeros(self.nbins)
                      
        # Get the min and max into the region: 0 <= phi < 2Pi
        phi_min = flip_phi(self.phi_min)
        phi_max = flip_phi(self.phi_max)
        
        q_data_max = numpy.max(q_data)
                      
        for n in range(len(data)):     
            frac = 0
            
            # q-value at the pixel (j,i)
            q_value = q_data[n]
            data_n = data[n]
            
            # Is pixel within range?
            is_in = False
            
            # phi-value of the pixel (j,i)
            phi_value = math.atan2(qy_data[n], qx_data[n]) + Pi 
            
            ## No need to calculate the frac when all data are within range
            if self.r_min <= q_value and q_value <= self.r_max:
                frac = 1                       
            if frac == 0:
                continue
            #In case of two ROIs (symmetric major and minor regions)(for 'q2')
            if run.lower()=='q2':
                ## For minor sector wing 
                # Calculate the minor wing phis
                phi_min_minor = flip_phi(phi_min - Pi)
                phi_max_minor = flip_phi(phi_max - Pi)
                # Check if phis of the minor ring is within 0 to 2pi
                if phi_min_minor > phi_max_minor:
                    is_in = (phi_value > phi_min_minor or \
                              phi_value < phi_max_minor)
                else:
                    is_in = (phi_value > phi_min_minor and \
                              phi_value < phi_max_minor)

            #For all cases(i.e.,for 'q', 'q2', and 'phi') 
            #Find pixels within ROI  
            if phi_min > phi_max: 
                is_in = is_in or (phi_value > phi_min or \
                                   phi_value < phi_max)         
            else:
                is_in = is_in or (phi_value >= phi_min  and \
                                    phi_value < phi_max)
            
            if not is_in:
                frac = 0                                                        
            if frac == 0:
                continue
            # Check which type of averaging we need
            if run.lower() == 'phi': 
                temp_x = (self.nbins) * (phi_value - self.phi_min)
                temp_y = (self.phi_max - self.phi_min)
                i_bin = int(math.floor(temp_x / temp_y))
            else:
                temp_x = (self.nbins) * (q_value - self.r_min)
                temp_y = (self.r_max - self.r_min)
                i_bin = int(math.floor(temp_x / temp_y))

            # Take care of the edge case at phi = 2pi. 
            if i_bin == self.nbins:  
                i_bin =  self.nbins - 1
                
            ## Get the total y          
            y[i_bin] += frac * data_n
            x[i_bin] += frac * q_value
            if err_data[n] == None or err_data[n] == 0.0:
                if data_n < 0:
                    data_n = -data_n
                y_err[i_bin] += frac * frac * data_n
            else:
                y_err[i_bin] += frac * frac * err_data[n] * err_data[n]
                
            if dq_data != None:
                # To be consistent with dq calculation in 1d reduction, 
                # we need just the averages (not quadratures) because 
                # it should not depend on the number of the q points 
                # in the qr bins.
                x_err[i_bin] += frac * dq_data[n]
            else:
                x_err = None
            y_counts[i_bin] += frac
   
        # Organize the results
        for i in range(self.nbins):
            y[i] = y[i] / y_counts[i]
            y_err[i] = math.sqrt(y_err[i]) / y_counts[i]

            # The type of averaging: phi,q2, or q
            # Calculate x[i]should be at the center of the bin
            if run.lower()=='phi':               
                x[i] = (self.phi_max - self.phi_min) / self.nbins * \
                    (1.0 * i + 0.5) + self.phi_min
            else:
                # We take the center of ring area, not radius.  
                # This is more accurate than taking the radial center of ring.
                #delta_r = (self.r_max - self.r_min) / self.nbins
                #r_inner = self.r_min + delta_r * i
                #r_outer = r_inner + delta_r
                #x[i] = math.sqrt((r_inner * r_inner + r_outer * r_outer) / 2)
                x[i] = x[i] / y_counts[i]
        y_err[y_err==0] = numpy.average(y_err)        
        idx = (numpy.isfinite(y) & numpy.isfinite(y_err))
        if x_err != None:
            d_x = x_err[idx] / y_counts[idx]
        else:
            d_x = None
        if not idx.any():
            msg = "Average Error: No points inside sector of ROI to average..." 
            raise ValueError, msg
        #elif len(y[idx])!= self.nbins:
        #    print "resulted",self.nbins- len(y[idx]),
        #"empty bin(s) due to tight binning..."
        return Data1D(x=x[idx], y=y[idx], dy=y_err[idx], dx=d_x)
                
class SectorPhi(_Sector):
    """
    Sector average as a function of phi.
    I(phi) is return and the data is averaged over Q.
    
    A sector is defined by r_min, r_max, phi_min, phi_max.
    The number of bin in phi also has to be defined.
    """
    def __call__(self, data2D):
        """
        Perform sector average and return I(phi).
        
        :param data2D: Data2D object
        :return: Data1D object
        """

        return self._agv(data2D, 'phi')
    
class SectorQ(_Sector):
    """
    Sector average as a function of Q for both symatric wings.
    I(Q) is return and the data is averaged over phi.
    
    A sector is defined by r_min, r_max, phi_min, phi_max.
    r_min, r_max, phi_min, phi_max >0.  
    The number of bin in Q also has to be defined.
    """
    def __call__(self, data2D):
        """
        Perform sector average and return I(Q).
        
        :param data2D: Data2D object
        
        :return: Data1D object
        """
        return self._agv(data2D, 'q2')

class Ringcut(object):
    """
    Defines a ring on a 2D data set.
    The ring is defined by r_min, r_max, and
    the position of the center of the ring.
    
    The data returned is the region inside the ring
    
    Phi_min and phi_max should be defined between 0 and 2*pi 
    in anti-clockwise starting from the x- axis on the left-hand side
    """
    def __init__(self, r_min=0, r_max=0, center_x=0, center_y=0 ):
        # Minimum radius
        self.r_min = r_min
        # Maximum radius
        self.r_max = r_max
        # Center of the ring in x
        self.center_x = center_x
        # Center of the ring in y
        self.center_y = center_y

        
    def __call__(self, data2D):
        """
        Apply the ring to the data set.
        Returns the angular distribution for a given q range
        
        :param data2D: Data2D object
        
        :return: index array in the range
        """
        if data2D.__class__.__name__ not in ["Data2D", "plottable_2D"]:
            raise RuntimeError, "Ring cut only take plottable_2D objects"

        # Get data
        qx_data = data2D.qx_data 
        qy_data = data2D.qy_data
        mask = data2D.mask
        q_data = numpy.sqrt(qx_data * qx_data + qy_data * qy_data)
        #q_data_max = numpy.max(q_data)

        # check whether or not the data point is inside ROI
        out = (self.r_min <= q_data) & (self.r_max >= q_data)

        return (out)
        

class Boxcut(object):
    """
    Find a rectangular 2D region of interest.
    """
    def __init__(self, x_min=0.0, x_max=0.0, y_min=0.0, y_max=0.0):
        # Minimum Qx value [A-1]
        self.x_min = x_min
        # Maximum Qx value [A-1]
        self.x_max = x_max
        # Minimum Qy value [A-1]
        self.y_min = y_min
        # Maximum Qy value [A-1]
        self.y_max = y_max

    def __call__(self, data2D):
        """
       Find a rectangular 2D region of interest.
         
       :param data2D: Data2D object
       :return: mask, 1d array (len = len(data)) 
           with Trues where the data points are inside ROI, otherwise False
        """
        mask = self._find(data2D)
        
        return mask
        
    def _find(self, data2D):
        """
        Find a rectangular 2D region of interest. 
        
        :param data2D: Data2D object
        
        :return: out, 1d array (length = len(data)) 
           with Trues where the data points are inside ROI, otherwise Falses
        """
        if data2D.__class__.__name__ not in ["Data2D", "plottable_2D"]:
            raise RuntimeError, "Boxcut take only plottable_2D objects"
        # Get qx_ and qy_data 
        qx_data = data2D.qx_data
        qy_data = data2D.qy_data
        mask = data2D.mask
        
        # check whether or not the data point is inside ROI
        outx = (self.x_min <= qx_data) & (self.x_max > qx_data)
        outy = (self.y_min <= qy_data) & (self.y_max > qy_data)

        return (outx & outy)

class Sectorcut(object):
    """
    Defines a sector (major + minor) region on a 2D data set.
    The sector is defined by phi_min, phi_max,
    where phi_min and phi_max are defined by the right 
    and left lines wrt central line. 
   
    Phi_min and phi_max are given in units of radian 
    and (phi_max-phi_min) should not be larger than pi
    """
    def __init__(self, phi_min=0, phi_max=math.pi):
        self.phi_min = phi_min
        self.phi_max = phi_max
              
    def __call__(self, data2D):
        """
        Find a rectangular 2D region of interest.
        
        :param data2D: Data2D object
        
        :return: mask, 1d array (len = len(data)) 
        
        with Trues where the data points are inside ROI, otherwise False
        """
        mask = self._find(data2D)
        
        return mask
        
    def _find(self, data2D):
        """
        Find a rectangular 2D region of interest. 
        
        :param data2D: Data2D object
        
        :return: out, 1d array (length = len(data)) 
        
        with Trues where the data points are inside ROI, otherwise Falses
        """
        if data2D.__class__.__name__ not in ["Data2D", "plottable_2D"]:
            raise RuntimeError, "Sectorcut take only plottable_2D objects" 
        Pi = math.pi
        # Get data 
        qx_data = data2D.qx_data
        qy_data = data2D.qy_data        
        phi_data = numpy.zeros(len(qx_data))

        # get phi from data
        phi_data = numpy.arctan2(qy_data, qx_data)
        
        # Get the min and max into the region: -pi <= phi < Pi
        phi_min_major = flip_phi(self.phi_min + Pi) - Pi
        phi_max_major = flip_phi(self.phi_max + Pi) - Pi  
        # check for major sector
        if phi_min_major > phi_max_major:
            out_major = (phi_min_major <= phi_data) + (phi_max_major > phi_data)
        else:
            out_major = (phi_min_major <= phi_data) & (phi_max_major > phi_data)
          
        # minor sector
        # Get the min and max into the region: -pi <= phi < Pi
        phi_min_minor = flip_phi(self.phi_min) - Pi
        phi_max_minor = flip_phi(self.phi_max) - Pi
              
        # check for minor sector
        if phi_min_minor > phi_max_minor:
            out_minor = (phi_min_minor <= phi_data) + \
                            (phi_max_minor >= phi_data) 
        else:
            out_minor = (phi_min_minor <= phi_data) & \
                            (phi_max_minor >= phi_data) 
        out = out_major + out_minor
        
        return out

if __name__ == "__main__": 

    from loader import Loader
    

    d = Loader().load('test/MAR07232_rest.ASC')
    #d = Loader().load('test/MP_New.sans')

    
    r = SectorQ(r_min=.000001, r_max=.01, phi_min=0.0, phi_max=2*math.pi)
    o = r(d)
    
    s = Ring(r_min=.000001, r_max=.01) 
    p = s(d)
    
    for i in range(len(o.x)):
        print o.x[i], o.y[i], o.dy[i]
    
 
    