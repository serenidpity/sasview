


################################################################################
#This software was developed by the University of Tennessee as part of the
#Distributed Data Analysis of Neutron Scattering Experiments (DANSE)
#project funded by the US National Science Foundation. 
#
#See the license text in license.txt
#
#copyright 2009, University of Tennessee
################################################################################


import wx
from wx.lib.scrolledpanel import ScrolledPanel

WIDTH = 400
HEIGHT = 200
        
class InvTextCtrl(wx.TextCtrl):
    """
    Text control for model and fit parameters.
    Binds the appropriate events for user interactions.
    """
    def __init__(self, *args, **kwds):
        wx.TextCtrl.__init__(self, *args, **kwds)
        ## Set to True when the mouse is clicked while 
        #the whole string is selected
        self.full_selection = False
        ## Call back for EVT_SET_FOCUS events
        _on_set_focus_callback = None

        # Bind appropriate events
        self.Bind(wx.EVT_LEFT_UP, self._highlight_text)
        self.Bind(wx.EVT_SET_FOCUS, self._on_set_focus)
        
    def _on_set_focus(self, event):
        """
        Catch when the text control is set in focus to highlight the whole
        text if necessary
        
        :param event: mouse event
        """
        event.Skip()
        self.full_selection = True
        
    def _highlight_text(self, event):
        """
        Highlight text of a TextCtrl only of no text has be selected
        
        :param event: mouse event
        """
        # Make sure the mouse event is available to other listeners
        event.Skip()
        control  = event.GetEventObject()
        if self.full_selection:
            self.full_selection = False
            # Check that we have a TextCtrl
            if issubclass(control.__class__, wx.TextCtrl):
                # Check whether text has been selected, 
                # if not, select the whole string
                (start, end) = control.GetSelection()
                if start == end:
                    control.SetSelection(-1, -1)
           

class OutputTextCtrl(wx.TextCtrl):
    """
    Text control used to display outputs.
    No editing allowed. The background is 
    grayed out. User can't select text.
    """
    def __init__(self, *args, **kwds):
        wx.TextCtrl.__init__(self, *args, **kwds)
        self.SetEditable(False)
        self.SetBackgroundColour(self.GetParent().GetBackgroundColour())
        
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
    
class DataDialog(wx.Dialog):
    """
    Allow file selection at loading time
    """
    def __init__(self, data_list, parent=None, text='', *args, **kwds):
        wx.Dialog.__init__(self, parent, *args, **kwds)
        self.SetTitle("Data Selection")
        self.SetSize((WIDTH, HEIGHT))
        self.list_of_ctrl = []
        if not data_list:
            return 
        self._sizer_main = wx.BoxSizer(wx.VERTICAL)
        self._sizer_txt = wx.BoxSizer(wx.VERTICAL)
        self._sizer_button = wx.BoxSizer(wx.HORIZONTAL)
        self._choice_sizer = wx.GridBagSizer(5, 5)
        self._panel = ScrolledPanel(self, style=wx.RAISED_BORDER,
                               size=(WIDTH-20, HEIGHT-50))
        self._panel.SetupScrolling()
        self.__do_layout(data_list, text=text)
        
    def __do_layout(self, data_list, text=''):
        """
        layout the dialog
        """
        if not data_list or len(data_list) <= 1:
            return 
        #add text
        if text.strip() == "":
            text = "This Perspective does not allow multiple data !\n"
            text += "Please select only one Data.\n"
        text_ctrl = wx.StaticText(self, -1, str(text))
        self._sizer_txt.Add(text_ctrl)
        iy = 0
        ix = 0
        rbox = wx.RadioButton(self._panel, -1, str(data_list[0].name), 
                                  (10, 10), style= wx.RB_GROUP)
        rbox.SetValue(True)
        self.list_of_ctrl.append((rbox, data_list[0]))
        self._choice_sizer.Add(rbox, (iy, ix), (1, 1),
                         wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        for i in range(1, len(data_list)):
            iy += 1
            rbox = wx.RadioButton(self._panel, -1, 
                                  str(data_list[i].name), (10, 10))
            rbox.SetValue(False)
            self.list_of_ctrl.append((rbox, data_list[i]))
            self._choice_sizer.Add(rbox, (iy, ix),
                           (1, 1), wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        self._panel.SetSizer(self._choice_sizer)
        #add sizer
        self._sizer_button.Add((20, 20), 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        button_cancel = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self._sizer_button.Add(button_cancel, 0,
                          wx.LEFT|wx.RIGHT|wx.ADJUST_MINSIZE, 10)
        button_OK = wx.Button(self, wx.ID_OK, "Ok")
        button_OK.SetFocus()
        self._sizer_button.Add(button_OK, 0,
                                wx.LEFT|wx.RIGHT|wx.ADJUST_MINSIZE, 10)
        static_line = wx.StaticLine(self, -1)
        
        self._sizer_txt.Add(self._panel, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        self._sizer_main.Add(self._sizer_txt, 1, wx.EXPAND|wx.ALL, 10)
        self._sizer_main.Add(static_line, 0, wx.EXPAND, 0)
        self._sizer_main.Add(self._sizer_button, 0, wx.EXPAND|wx.ALL, 10)
        self.SetSizer(self._sizer_main)
        self.Layout()
        
    def get_data(self):
        """
        return the selected data
        """
        for item in self.list_of_ctrl:
            rbox, data = item
            if rbox.GetValue():
                return data 

    

 