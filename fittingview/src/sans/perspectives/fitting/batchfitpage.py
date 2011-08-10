

import sys
import wx
import wx.lib.newevent
import numpy
import copy
import math
import time
from sans.models.dispersion_models import ArrayDispersion, GaussianDispersion
from sans.dataloader.data_info import Data1D
from sans.guiframe.events import StatusEvent    
from sans.guiframe.events import NewPlotEvent  
from sans.guiframe.utils import format_number,check_float

(Chi2UpdateEvent, EVT_CHI2_UPDATE)   = wx.lib.newevent.NewEvent()
_BOX_WIDTH = 76
_DATA_BOX_WIDTH = 300
SMEAR_SIZE_L = 0.00
SMEAR_SIZE_H = 0.00

import basepage
from basepage import BasicPage
from basepage import PageInfoEvent
from sans.models.qsmearing import smear_selection
from fitpage import FitPage

class BatchFitPage(FitPage):
    window_name = "BatchFit"
    window_caption  = "BatchFit"

    def __init__(self,parent, color='rand'):
        """ 
        Initialization of the Panel
        """
        FitPage.__init__(self, parent, color=color)
        self.window_name = "BatchFit"
        self.window_caption  = "BatchFit"
        
    def _fill_range_sizer(self):
        """
        Fill the sizer containing the plotting range
        add  access to npts
        """
        is_2Ddata = False
        
        # Check if data is 2D
        if self.data.__class__.__name__ ==  "Data2D" or \
                        self.enable2D:
            is_2Ddata = True
            
        title = "Fitting"
        #smear messages & titles
        smear_message_none  =  "No smearing is selected..."
        smear_message_dqdata  =  "The dQ data is being used for smearing..."
        smear_message_2d  =  "Higher accuracy is very time-expensive. Use it with care..."
        smear_message_new_ssmear  =  "Please enter only the value of interest to customize smearing..."
        smear_message_new_psmear  =  "Please enter both; the dQ will be generated by interpolation..."
        smear_message_2d_x_title = "<dQp>[1/A]:"
        smear_message_2d_y_title = "<dQs>[1/A]:"        
        smear_message_pinhole_min_title = "dQ_low[1/A]:"
        smear_message_pinhole_max_title = "dQ_high[1/A]:"
        smear_message_slit_height_title = "Slit height[1/A]:"
        smear_message_slit_width_title = "Slit width[1/A]:"
        
        self._get_smear_info()
        
        #Sizers
        box_description_range = wx.StaticBox(self, -1,str(title))
        boxsizer_range = wx.StaticBoxSizer(box_description_range, wx.VERTICAL)      
        self.sizer_set_smearer = wx.BoxSizer(wx.VERTICAL)
        sizer_smearer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_new_smear= wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_set_masking = wx.BoxSizer(wx.HORIZONTAL)
        sizer_chi2 = wx.BoxSizer(wx.VERTICAL)
        """
        smear_set_box= wx.StaticBox(self, -1,'Set Instrumental Smearing')
        sizer_smearer_box = wx.StaticBoxSizer(smear_set_box, wx.HORIZONTAL)
        sizer_smearer_box.SetMinSize((_DATA_BOX_WIDTH,85))
        """
        sizer_fit = wx.GridSizer(2, 4, 2, 6)
        """
        # combobox for smear2d accuracy selection
        self.smear_accuracy = wx.ComboBox(self, -1,size=(50,-1),style=wx.CB_READONLY)
        self._set_accuracy_list()
        self.smear_accuracy.SetValue(self.smear2d_accuracy)
        self.smear_accuracy.SetSelection(0)
        self.smear_accuracy.SetToolTipString("'Higher' uses more Gaussian points for smearing computation.")
                   
        wx.EVT_COMBOBOX(self.smear_accuracy,-1, self._on_select_accuracy)
        """
        #Fit button
        self.btFit = wx.Button(self,wx.NewId(),'Fit', size=(88,25))
        self.default_bt_colour =  self.btFit.GetDefaultAttributes()
        self.btFit.Bind(wx.EVT_BUTTON, self._onFit,id= self.btFit.GetId())
        self.btFit.SetToolTipString("Start fitting.")
        """
        #textcntrl for custom resolution
        self.smear_pinhole_max = self.ModelTextCtrl(self, -1,size=(_BOX_WIDTH-25,20),style=wx.TE_PROCESS_ENTER,
                                            text_enter_callback = self.onPinholeSmear)
        self.smear_pinhole_min = self.ModelTextCtrl(self, -1,size=(_BOX_WIDTH-25,20),style=wx.TE_PROCESS_ENTER,
                                            text_enter_callback = self.onPinholeSmear)
        self.smear_slit_height= self.ModelTextCtrl(self, -1,size=(_BOX_WIDTH-25,20),style=wx.TE_PROCESS_ENTER,
                                            text_enter_callback = self.onSlitSmear)
        self.smear_slit_width = self.ModelTextCtrl(self, -1,size=(_BOX_WIDTH-25,20),style=wx.TE_PROCESS_ENTER,
                                            text_enter_callback = self.onSlitSmear)

        ## smear
        self.smear_data_left= BGTextCtrl(self, -1, size=(_BOX_WIDTH-25,20), style=0)
        self.smear_data_left.SetValue(str(self.dq_l))
        self.smear_data_right = BGTextCtrl(self, -1, size=(_BOX_WIDTH-25,20), style=0)
        self.smear_data_right.SetValue(str(self.dq_r))

        #set default values for smear
        self.smear_pinhole_max.SetValue(str(self.dx_max))
        self.smear_pinhole_min.SetValue(str(self.dx_min))
        self.smear_slit_height.SetValue(str(self.dxl))
        self.smear_slit_width.SetValue(str(self.dxw))

        #Filling the sizer containing instruments smearing info.
        self.disable_smearer = wx.RadioButton(self, -1, 'None', style=wx.RB_GROUP)
        self.enable_smearer = wx.RadioButton(self, -1, 'Use dQ Data')
        #self.enable_smearer.SetToolTipString("Click to use the loaded dQ data for smearing.")
        self.pinhole_smearer = wx.RadioButton(self, -1, 'Custom Pinhole Smear')
        #self.pinhole_smearer.SetToolTipString("Click to input custom resolution for pinhole smearing.")
        self.slit_smearer = wx.RadioButton(self, -1, 'Custom Slit Smear')
        #self.slit_smearer.SetToolTipString("Click to input custom resolution for slit smearing.")
        self.Bind(wx.EVT_RADIOBUTTON, self.onSmear, id=self.disable_smearer.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.onSmear, id=self.enable_smearer.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.onPinholeSmear, id=self.pinhole_smearer.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.onSlitSmear, id=self.slit_smearer.GetId())
        self.disable_smearer.SetValue(True)
        
        # add 4 types of smearing to the sizer
        sizer_smearer.Add( self.disable_smearer,0, wx.LEFT, 10)
        sizer_smearer.Add((10,10))
        sizer_smearer.Add( self.enable_smearer)
        sizer_smearer.Add((10,10))
        sizer_smearer.Add( self.pinhole_smearer ) 
        sizer_smearer.Add((10,10))
        sizer_smearer.Add( self.slit_smearer ) 
        sizer_smearer.Add((10,10))  
        """     
        """
        # StaticText for chi2, N(for fitting), Npts
        self.tcChi    =  BGTextCtrl(self, -1, "-", size=(75,20), style=0)
        self.tcChi.SetToolTipString("Chi2/Npts(Fit)")
        self.Npts_fit    =  BGTextCtrl(self, -1, "-", size=(75,20), style=0)
        self.Npts_fit.SetToolTipString(\
                            " Npts : number of points selected for fitting")
        self.Npts_total  =  self.ModelTextCtrl(self, -1, size=(_BOX_WIDTH, 20), 
                        style=wx.TE_PROCESS_ENTER, 
                        text_enter_callback=self._onQrangeEnter)
        self.Npts_total.SetValue(format_number(self.npts_x))
        self.Npts_total.SetToolTipString(\
                                " Total Npts : total number of data points")
        """
        # Update and Draw button
        self.draw_button = wx.Button(self,wx.NewId(),'Compute', size=(88,24))
        self.draw_button.Bind(wx.EVT_BUTTON, \
                              self._onDraw,id= self.draw_button.GetId())
        self.draw_button.SetToolTipString("Compute and Draw.")
        """
        box_description_1= wx.StaticText(self, -1,'    Chi2/Npts')
        box_description_2= wx.StaticText(self, -1,'Npts(Fit)')
        box_description_3= wx.StaticText(self, -1,'Total Npts')
        box_description_3.SetToolTipString( \
                                " Total Npts : total number of data points")
        #box_description_4= wx.StaticText(self, -1,' ')
        """
        
        """
        sizer_fit.Add(box_description_1,0,0)
        sizer_fit.Add(box_description_2,0,0)
        sizer_fit.Add(box_description_3,0,0)  
        """     
        sizer_fit.Add(self.draw_button,0,0)
        """
        sizer_fit.Add(self.tcChi,0,0)
        sizer_fit.Add(self.Npts_fit ,0,0)
        sizer_fit.Add(self.Npts_total,0,0)
        """
        sizer_fit.Add(self.btFit,0,0) 
        """
        self.smear_description_none    =  wx.StaticText(self, -1, smear_message_none , style=wx.ALIGN_LEFT)
        self.smear_description_dqdata    =  wx.StaticText(self, -1, smear_message_dqdata , style=wx.ALIGN_LEFT)
        self.smear_description_type    =  wx.StaticText(self, -1, "Type:" , style=wx.ALIGN_LEFT)
        self.smear_description_accuracy_type    =  wx.StaticText(self, -1, "Accuracy:" , style=wx.ALIGN_LEFT)
        self.smear_description_smear_type    =  BGTextCtrl(self, -1, size=(57,20), style=0)
        self.smear_description_smear_type.SetValue(str(self.dq_l))
        self.SetBackgroundColour(self.GetParent().GetBackgroundColour())
        self.smear_description_2d     =  wx.StaticText(self, -1, smear_message_2d  , style=wx.ALIGN_LEFT)
        self.smear_message_new_s = wx.StaticText(self, -1, smear_message_new_ssmear  , style=wx.ALIGN_LEFT)
        self.smear_message_new_p = wx.StaticText(self, -1, smear_message_new_psmear  , style=wx.ALIGN_LEFT)
        self.smear_description_2d_x     =  wx.StaticText(self, -1, smear_message_2d_x_title  , style=wx.ALIGN_LEFT)
        self.smear_description_2d_x.SetToolTipString("  dQp(parallel) in q_r direction.")
        self.smear_description_2d_y     =  wx.StaticText(self, -1, smear_message_2d_y_title  , style=wx.ALIGN_LEFT)
        self.smear_description_2d_y.SetToolTipString(" dQs(perpendicular) in q_phi direction.")
        self.smear_description_pin_min     =  wx.StaticText(self, -1, smear_message_pinhole_min_title  , style=wx.ALIGN_LEFT)
        self.smear_description_pin_max     =  wx.StaticText(self, -1, smear_message_pinhole_max_title  , style=wx.ALIGN_LEFT)
        self.smear_description_slit_height    =  wx.StaticText(self, -1, smear_message_slit_height_title   , style=wx.ALIGN_LEFT)
        self.smear_description_slit_width    =  wx.StaticText(self, -1, smear_message_slit_width_title   , style=wx.ALIGN_LEFT)
        """
        #arrange sizers 
        #boxsizer1.Add( self.tcChi )  
        """
        self.sizer_set_smearer.Add(sizer_smearer )
        self.sizer_set_smearer.Add((10,10))
        self.sizer_set_smearer.Add( self.smear_description_none,0, wx.CENTER, 10 ) 
        self.sizer_set_smearer.Add( self.smear_description_dqdata,0, wx.CENTER, 10 )
        self.sizer_set_smearer.Add( self.smear_description_2d,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add( self.smear_description_type,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add( self.smear_description_accuracy_type,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add( self.smear_accuracy )
        self.sizer_new_smear.Add( self.smear_description_smear_type,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add((15,-1))
        self.sizer_new_smear.Add( self.smear_description_2d_x,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add( self.smear_description_pin_min,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add( self.smear_description_slit_height,0, wx.CENTER, 10 )

        self.sizer_new_smear.Add( self.smear_pinhole_min,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add( self.smear_slit_height,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add( self.smear_data_left,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add((20,-1))
        self.sizer_new_smear.Add( self.smear_description_2d_y,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add( self.smear_description_pin_max,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add( self.smear_description_slit_width,0, wx.CENTER, 10 )

        self.sizer_new_smear.Add( self.smear_pinhole_max,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add( self.smear_slit_width,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add( self.smear_data_right,0, wx.CENTER, 10 )
           
        self.sizer_set_smearer.Add( self.smear_message_new_s,0, wx.CENTER, 10)
        self.sizer_set_smearer.Add( self.smear_message_new_p,0, wx.CENTER, 10)
        self.sizer_set_smearer.Add((5,2))
        self.sizer_set_smearer.Add( self.sizer_new_smear,0, wx.CENTER, 10 )
        
        # add all to chi2 sizer 
        sizer_smearer_box.Add(self.sizer_set_smearer)    
           
        sizer_chi2.Add(sizer_smearer_box)
        """
        sizer_chi2.Add((-1,5))
        """
        # hide all smear messages and textctrl
        self._hide_all_smear_info()
        """
        # get smear_selection
        self.current_smearer= smear_selection( self.data, self.model )
        """
        # Show only the relevant smear messages, etc
        if self.current_smearer == None:
            if not is_2Ddata:
                self.smear_description_none.Show(True)
                self.enable_smearer.Disable()  
            else:
                self.smear_description_none.Show(True)
                #self.smear_description_2d.Show(True) 
                #self.pinhole_smearer.Disable() 
                self.slit_smearer.Disable()   
                #self.enable_smearer.Disable() 
            if self.data == None:
                self.slit_smearer.Disable() 
                self.pinhole_smearer.Disable() 
                self.enable_smearer.Disable() 
        else: self._show_smear_sizer()
        """
        boxsizer_range.Add(self.sizer_set_masking)
         #2D data? default
        is_2Ddata = False
        
        #check if it is 2D data
        if self.data.__class__.__name__ ==  "Data2D" or \
                        self.enable2D:
            is_2Ddata = True
            
        self.sizer5.Clear(True)
     
        self.qmin  = self.ModelTextCtrl(self, -1,size=(_BOX_WIDTH,20),
                                          style=wx.TE_PROCESS_ENTER,
                                    text_enter_callback = self._onQrangeEnter)
        self.qmin.SetValue(str(self.qmin_x))
        self.qmin.SetToolTipString("Minimun value of Q in linear scale.")
     
        self.qmax  = self.ModelTextCtrl(self, -1,size=(_BOX_WIDTH,20),
                                          style=wx.TE_PROCESS_ENTER,
                                        text_enter_callback=self._onQrangeEnter)
        self.qmax.SetValue(str(self.qmax_x))
        self.qmax.SetToolTipString("Maximum value of Q in linear scale.")
        
        id = wx.NewId()
        self.reset_qrange =wx.Button(self,id,'Reset',size=(77,20))
      
        self.reset_qrange.Bind(wx.EVT_BUTTON, self.on_reset_clicked,id=id)
        self.reset_qrange.SetToolTipString("Reset Q range to the default values")
     
        sizer_horizontal=wx.BoxSizer(wx.HORIZONTAL)
        sizer= wx.GridSizer(2, 4, 2, 6)

        self.btEditMask = wx.Button(self,wx.NewId(),'Editor', size=(88,23))
        self.btEditMask.Bind(wx.EVT_BUTTON, self._onMask,id= self.btEditMask.GetId())
        self.btEditMask.SetToolTipString("Edit Mask.")
        self.EditMask_title = wx.StaticText(self, -1, ' Masking(2D)')

        sizer.Add(wx.StaticText(self, -1, 'Q range'))     
        sizer.Add(wx.StaticText(self, -1, ' Min[1/A]'))
        sizer.Add(wx.StaticText(self, -1, ' Max[1/A]'))
        sizer.Add(self.EditMask_title)
        #sizer.Add(wx.StaticText(self, -1, ''))
        sizer.Add(self.reset_qrange)   
        sizer.Add(self.qmin)
        sizer.Add(self.qmax)
        #sizer.Add(self.theory_npts_tcrtl)
        sizer.Add(self.btEditMask)
        boxsizer_range.Add(sizer_chi2) 
        boxsizer_range.Add((10,10))
        boxsizer_range.Add(sizer)
        
        boxsizer_range.Add((10,15))
        boxsizer_range.Add(sizer_fit)
        if is_2Ddata:
            self.btEditMask.Enable()  
            self.EditMask_title.Enable() 
        else:
            self.btEditMask.Disable()  
            self.EditMask_title.Disable()
        """
        ## save state
        self.save_current_state()
        """
        self.sizer5.Add(boxsizer_range,0, wx.EXPAND | wx.ALL, 10)
        self.sizer5.Layout()
       
    def _on_select_model(self, event=None): 
        """
        call back for model selection
        """  
        
        self.Show(False)    
        self._on_select_model_helper() 
        self.set_model_param_sizer(self.model)                   
        if self.model is None:
            self._set_bookmark_flag(False)
            self._keep.Enable(False)
            self._set_save_flag(False)
        self.enable_disp.SetValue(False)
        self.disable_disp.SetValue(True)
        try:
            self.set_dispers_sizer()
        except:
            pass
        """
        #self.btFit.SetFocus() 
        self.state.enable_disp = self.enable_disp.GetValue()
        self.state.disable_disp = self.disable_disp.GetValue()
        self.state.pinhole_smearer = self.pinhole_smearer.GetValue()
        self.state.slit_smearer = self.slit_smearer.GetValue()
        """
        self.state.structurecombobox = self.structurebox.GetCurrentSelection()
        self.state.formfactorcombobox = self.formfactorbox.GetCurrentSelection()
      
        if self.model != None:
            self._set_copy_flag(True)
            self._set_paste_flag(True)
            if self.data != None:
                self._set_bookmark_flag(True)
                self._keep.Enable(True)
                
            temp_smear = None
            """
            #self._set_save_flag(True)
            # Reset smearer, model and data
            self._set_smear(self.data)
            try:
                # update smearer sizer
                self.onSmear(None)
                temp_smear = None
                if self.enable_smearer.GetValue():
                    # Set the smearer environments
                    temp_smear = self.smearer
            except:
                raise
                ## error occured on chisqr computation
                #pass
            """
            ## event to post model to fit to fitting plugins
            (ModelEventbox, EVT_MODEL_BOX) = wx.lib.newevent.NewEvent()
         
            ## set smearing value whether or not 
            #    the data contain the smearing info
            evt = ModelEventbox(model=self.model, 
                                        smearer=temp_smear, 
                                        qmin=float(self.qmin_x),
                                        uid=self.uid,
                                     qmax=float(self.qmax_x)) 
   
            self._manager._on_model_panel(evt=evt)
            self.mbox_description.SetLabel("Model [%s]" % str(self.model.name))
            self.state.model = self.model.clone()
            self.state.model.name = self.model.name

            
        if event != None:
            ## post state to fit panel
            new_event = PageInfoEvent(page = self)
            wx.PostEvent(self.parent, new_event) 
            #update list of plugins if new plugin is available
            if self.plugin_rbutton.GetValue():
                temp = self.parent.update_model_list()
                if temp:
                    self.model_list_box = temp
                    current_val = self.formfactorbox.GetValue()
                    pos = self.formfactorbox.GetSelection()
                    self._show_combox_helper()
                    self.formfactorbox.SetSelection(pos)
                    self.formfactorbox.SetValue(current_val)
            self._onDraw(event=None)
        else:
            self._draw_model()
        self.SetupScrolling()
        self.Show(True)   
        
    def _update_paramv_on_fit(self):
        """
        make sure that update param values just before the fitting
        """
        #flag for qmin qmax check values
        flag = True
        self.fitrange = True
        is_modified = False

        #wx.PostEvent(self._manager.parent, StatusEvent(status=" \
        #updating ... ",type="update"))

        ##So make sure that update param values on_Fit.
        #self._undo.Enable(True)
        if self.model !=None:           
            ##Check the values
            self._check_value_enter( self.fittable_param ,is_modified)
            self._check_value_enter( self.fixed_param ,is_modified)
            self._check_value_enter( self.parameters ,is_modified)

            # If qmin and qmax have been modified, update qmin and qmax and 
             # Here we should check whether the boundaries have been modified.
            # If qmin and qmax have been modified, update qmin and qmax and 
            # set the is_modified flag to True
            self.fitrange = self._validate_qrange(self.qmin, self.qmax)
            if self.fitrange:
                tempmin = float(self.qmin.GetValue())
                if tempmin != self.qmin_x:
                    self.qmin_x = tempmin
                tempmax = float(self.qmax.GetValue())
                if tempmax != self.qmax_x:
                    self.qmax_x = tempmax
                if tempmax == tempmin:
                    flag = False    
                temp_smearer = None
                """
                if not self.disable_smearer.GetValue():
                    temp_smearer= self.current_smearer
                    if self.slit_smearer.GetValue():
                        flag = self.update_slit_smear()
                    elif self.pinhole_smearer.GetValue():
                        flag = self.update_pinhole_smear()
                    else:
                        self._manager.set_smearer(smearer=temp_smearer,
                                                  uid=self.uid,
                                                     qmin=float(self.qmin_x),
                                                      qmax=float(self.qmax_x),
                                                      draw=False)
                elif not self._is_2D():
                    self._manager.set_smearer(smearer=temp_smearer,
                                              qmin=float(self.qmin_x),
                                              uid=self.uid, 
                                                 qmax= float(self.qmax_x),
                                                 draw=False)
                
                    if self.data != None:
                        index_data = ((self.qmin_x <= self.data.x)&\
                                      (self.data.x <= self.qmax_x))
                        val = str(len(self.data.x[index_data==True]))
                        self.Npts_fit.SetValue(val)
                    else:
                        # No data in the panel
                        try:
                            self.npts_x = float(self.Npts_total.GetValue())
                        except:
                            flag = False
                            return flag
                    flag = True
                    """
                if self._is_2D():
                    # only 2D case set mask  
                    flag = self._validate_Npts()
                    if not flag:
                        return flag
            else: flag = False
        else: 
            flag = False

        #For invalid q range, disable the mask editor and fit button, vs.    
        if not self.fitrange:
            #self.btFit.Disable()
            if self._is_2D():
                self.btEditMask.Disable()
        else:
            #self.btFit.Enable(True)
            if self._is_2D() and  self.data != None:
                self.btEditMask.Enable(True)

        if not flag:
            msg = "Cannot Plot or Fit :Must select a "
            msg += " model or Fitting range is not valid!!!  "
            wx.PostEvent(self.parent.parent, StatusEvent(status=msg))
        
        self.save_current_state()
   
        return flag  
    def save_current_state(self):
        """
        Currently no save option implemented for batch page
        """
        pass 
    def save_current_state_fit(self):
        """
        Currently no save option implemented for batch page
        """
        pass
    def set_data(self, data):
        """
        reset the current data 
        """
        id = None
        group_id = None
        flag = False
        if self.data is None and data is not None:
            flag = True
        if data is not None:
            id = data.id
            group_id = data.group_id
            if self.data is not None:
                flag = (data.id != self.data.id)
        self.data = data
        if self.data is None:
            data_min = ""
            data_max = ""
            data_name = ""
            self._set_bookmark_flag(False)
            self._keep.Enable(False)
            self._set_save_flag(False)
        else:
            if self.model != None:
                self._set_bookmark_flag(True)
                self._keep.Enable(True)
            self._set_save_flag(True)
            self._set_preview_flag(True)
            """
            self._set_smear(data)
            # more disables for 2D
            if self.data.__class__.__name__ ==  "Data2D" or \
                        self.enable2D:
                self.slit_smearer.Disable()
                self.pinhole_smearer.Enable(True) 
                self.default_mask = copy.deepcopy(self.data.mask)
            else:
                self.slit_smearer.Enable(True) 
                self.pinhole_smearer.Enable(True)      
             """   
            self.formfactorbox.Enable()
            self.structurebox.Enable()
            data_name = self.data.name
            #set maximum range for x in linear scale
            if not hasattr(self.data,"data"): #Display only for 1D data fit
                # Minimum value of data   
                data_min = min(self.data.x)
                # Maximum value of data  
                data_max = max(self.data.x)
                """
                #number of total data points
                self.Npts_total.SetValue(str(len(self.data.x)))
                #default:number of data points selected to fit
                self.Npts_fit.SetValue(str(len(self.data.x)))
                """
                self.btEditMask.Disable()  
                self.EditMask_title.Disable()
            else:
                
                ## Minimum value of data 
                data_min = 0
                x = max(math.fabs(self.data.xmin), math.fabs(self.data.xmax)) 
                y = max(math.fabs(self.data.ymin), math.fabs(self.data.ymax))
                ## Maximum value of data  
                data_max = math.sqrt(x*x + y*y)
                """
                #number of total data points
                self.Npts_total.SetValue(str(len(self.data.data)))
                #default:number of data points selected to fit
                self.Npts_fit.SetValue(str(len(self.data.data)))
                """
                self.btEditMask.Enable()  
                self.EditMask_title.Enable() 
        """
        self.Npts_total.SetEditable(False)
        self.Npts_total.SetBackgroundColour(\
                                    self.GetParent().GetBackgroundColour())
        
        self.Npts_total.Bind(wx.EVT_MOUSE_EVENTS, self._npts_click)
        #self.Npts_total.Disable()
        """
        self.dataSource.SetValue(data_name)
        self.qmin_x = data_min
        self.qmax_x = data_max
        #self.minimum_q.SetValue(str(data_min))
        #self.maximum_q.SetValue(str(data_max))
        self.qmin.SetValue(str(data_min))
        self.qmax.SetValue(str(data_max))
        self.qmin.SetBackgroundColour("white")
        self.qmax.SetBackgroundColour("white")
        self.state.data = data
        self.state.qmin = self.qmin_x
        self.state.qmax = self.qmax_x
        
        #update model plot with new data information
        if flag:
            #set model view button
            if self.data.__class__.__name__ == "Data2D":
                self.enable2D = True
                self.model_view.SetLabel("2D Mode")
            else:
                self.enable2D = False
                self.model_view.SetLabel("1D Mode")
                
            self.model_view.Disable()
            
            #replace data plot on combo box selection
            #by removing the previous selected data
            #wx.PostEvent(self._manager.parent, NewPlotEvent(action="remove",
            #                                        group_id=group_id, id=id))
            wx.PostEvent(self._manager.parent, 
                             NewPlotEvent(group_id=group_id,
                                               action="delete"))
            #plot the current selected data
            wx.PostEvent(self._manager.parent, NewPlotEvent(plot=self.data, 
                                                           title=str(self.data.title)))
            self._manager.store_data(uid=self.uid, data=data,
                                     data_list=self.data_list,
                                      caption=self.window_name)
            self._draw_model()
    

        
class BGTextCtrl(wx.TextCtrl):
    """
    Text control used to display outputs.
    No editing allowed. The background is 
    grayed out. User can't select text.
    """
    def __init__(self, *args, **kwds):
        wx.TextCtrl.__init__(self, *args, **kwds)
        self.SetEditable(False)
        self.SetBackgroundColour(self.GetParent().parent.GetBackgroundColour())
        
        # Bind to mouse event to avoid text highlighting
        # The event will be skipped once the call-back
        # is called.
        self.Bind(wx.EVT_MOUSE_EVENTS, self._click)
        
    def _click(self, event):
        """
        Prevent further handling of the mouse event
        by not calling Skip().
        """ 
        pass
 
