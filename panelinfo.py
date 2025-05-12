# panelinfo.py

import wx
from utils import dip
import datetime

class PanelInfo(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        # ------------------------------------------------------------
        # status
        # ------------------------------------------------------------
        
        # # create staticbox
        # sb_status = wx.StaticBox(self, label="Status")
        # sb_status_sizer = wx.GridBagSizer(dip(3), dip(3))
        # sb_status.SetSizer(sb_status_sizer)

        # # modifiable statictexts
        # self.statictext_status = wx.StaticText(sb_status, label="")
        # self.statictext_network = wx.StaticText(sb_status, label="")
        # self.statictext_server = wx.StaticText(sb_status, label="")
        
        # # add to staticbox sizer
        # sb_status_sizer.Add(wx.StaticText(sb_status, label="Status:"), pos=(0, 0), flag=wx.ALIGN_RIGHT|wx.TOP, border=dip(15))
        # sb_status_sizer.Add(self.statictext_status, pos=(0, 1), flag=wx.ALIGN_LEFT|wx.TOP, border=dip(15))
        # sb_status_sizer.Add(wx.StaticText(sb_status, label="Server:"), pos=(1, 0), flag=wx.ALIGN_RIGHT|wx.BOTTOM, border=dip(10))
        # sb_status_sizer.Add(self.statictext_server, pos=(1, 1), flag=wx.ALIGN_LEFT|wx.BOTTOM, border=dip(10))
        # sb_status_sizer.AddGrowableCol(0, 1)
        # sb_status_sizer.AddGrowableCol(1, 2)

        # # set default values
        # self.SetSTStatus(False)
        # self.SetSTServerAddress("None")

        # # add to main sizer
        # self.sizer.Add(sb_status, proportion=0, flag=wx.EXPAND|wx.LEFT|wx.TOP|wx.RIGHT, border=dip(5))

        # ------------------------------------------------------------
        # vehicle data
        # ------------------------------------------------------------

        # create staticbox
        sb_vehicledata = wx.StaticBox(self, label="Vehicle Data")
        sb_vehicledata_sizer = wx.GridBagSizer(dip(3), dip(3))
        sb_vehicledata.SetSizer(sb_vehicledata_sizer)

        # modifiable statictexts
        self.statictext_acceleration_x = wx.StaticText(sb_vehicledata, label="")
        self.statictext_acceleration_y = wx.StaticText(sb_vehicledata, label="")
        self.statictext_acceleration_z = wx.StaticText(sb_vehicledata, label="")
        self.statictext_angularvelocity_x = wx.StaticText(sb_vehicledata, label="")
        self.statictext_angularvelocity_y = wx.StaticText(sb_vehicledata, label="")
        self.statictext_angularvelocity_z = wx.StaticText(sb_vehicledata, label="")
        
        # add to staticbox sizer
        sb_vehicledata_sizer.Add(wx.StaticText(sb_vehicledata, label="Linear acceleration"), pos=(0, 0), span=(1, 2), flag=wx.ALIGN_CENTER|wx.TOP, border=dip(15))
        sb_vehicledata_sizer.Add(wx.StaticText(sb_vehicledata, label="X: "), pos=(1, 0), flag=wx.ALIGN_RIGHT)
        sb_vehicledata_sizer.Add(self.statictext_acceleration_x, pos=(1, 1), flag=wx.ALIGN_LEFT)
        sb_vehicledata_sizer.Add(wx.StaticText(sb_vehicledata, label="Y: "), pos=(2, 0), flag=wx.ALIGN_RIGHT)
        sb_vehicledata_sizer.Add(self.statictext_acceleration_y, pos=(2, 1), flag=wx.ALIGN_LEFT)
        sb_vehicledata_sizer.Add(wx.StaticText(sb_vehicledata, label="Z: "), pos=(3, 0), flag=wx.ALIGN_RIGHT)
        sb_vehicledata_sizer.Add(self.statictext_acceleration_z, pos=(3, 1), flag=wx.ALIGN_LEFT)

        sb_vehicledata_sizer.Add(wx.StaticText(sb_vehicledata, label="Angular velocity"), pos=(0, 2), span=(1, 2), flag=wx.ALIGN_CENTER|wx.TOP, border=dip(15))
        sb_vehicledata_sizer.Add(wx.StaticText(sb_vehicledata, label="X: "), pos=(1, 2), flag=wx.ALIGN_RIGHT)
        sb_vehicledata_sizer.Add(self.statictext_angularvelocity_x, pos=(1, 3), flag=wx.ALIGN_LEFT)
        sb_vehicledata_sizer.Add(wx.StaticText(sb_vehicledata, label="Y: "), pos=(2, 2), flag=wx.ALIGN_RIGHT)
        sb_vehicledata_sizer.Add(self.statictext_angularvelocity_y, pos=(2, 3), flag=wx.ALIGN_LEFT)
        sb_vehicledata_sizer.Add(wx.StaticText(sb_vehicledata, label="Z: "), pos=(3, 2), flag=wx.ALIGN_RIGHT)
        sb_vehicledata_sizer.Add(self.statictext_angularvelocity_z, pos=(3, 3), flag=wx.ALIGN_LEFT)

        sb_vehicledata_sizer.AddGrowableCol(0, 2)
        sb_vehicledata_sizer.AddGrowableCol(1, 1)
        sb_vehicledata_sizer.AddGrowableCol(2, 2)
        sb_vehicledata_sizer.AddGrowableCol(3, 1)

        # set default values
        self.SetSTAcceleration("0", "0", "0")
        self.SetSTAngularVelocity("0", "0", "0")

        # add to main sizer
        self.sizer.Add(sb_vehicledata, proportion=0, flag=wx.EXPAND|wx.LEFT|wx.TOP|wx.RIGHT, border=dip(5))

        # ------------------------------------------------------------
        # voice control
        # ------------------------------------------------------------

        # # create staticbox
        # sb_voicecontrol = wx.StaticBox(self, label="Voice control")
        # sb_voicecontrol_sizer = wx.GridBagSizer(dip(3), dip(3))
        # sb_voicecontrol.SetSizer(sb_voicecontrol_sizer)

        # # modifiable statictexts
        # self.test = wx.TextCtrl(sb_voicecontrol)
        # button_talk = wx.Button(sb_voicecontrol, label="Talk to Rocky...")
        
        # # add to staticbox sizer
        # sb_voicecontrol_sizer.Add(self.test, pos=(0, 0), flag=wx.EXPAND|wx.TOP, border=dip(15))
        # sb_voicecontrol_sizer.Add(button_talk, pos=(1, 0), flag=wx.EXPAND|wx.BOTTOM, border=dip(15))
        # sb_voicecontrol_sizer.AddGrowableCol(0, 1)

        # # add to main sizer
        # self.sizer.Add(sb_voicecontrol, proportion=0, flag=wx.EXPAND|wx.LEFT|wx.TOP|wx.RIGHT, border=dip(5))

        # ------------------------------------------------------------
        # log
        # ------------------------------------------------------------

        # # create staticbox
        # sb_log = wx.StaticBox(self, label="Log")
        # sb_log_sizer = wx.BoxSizer(wx.VERTICAL)
        # sb_log.SetSizer(sb_log_sizer)

        # self.textctrl_log = wx.TextCtrl(sb_log, style=wx.TE_MULTILINE|wx.TE_READONLY, size=wx.Size(-1, 200))
        # font = wx.Font(9, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Courier")
        # self.textctrl_log.SetFont(font)
        # self.AddLogMessage("INFO", "Initialized.")
        
        # # add to staticbox sizer
        # sb_log_sizer.AddSpacer(dip(15))
        # sb_log_sizer.Add(self.textctrl_log, flag=wx.EXPAND|wx.ALL, border=dip(3))

        # # add to main sizer
        # self.sizer.Add(sb_log, proportion=0, flag=wx.EXPAND|wx.LEFT|wx.TOP|wx.RIGHT, border=dip(5))

        self.sizer.Layout()

    def SetSTAcceleration(self, x:str="None", y:str="None", z:str="None"):
        self.statictext_acceleration_x.SetLabel(x)
        self.statictext_acceleration_y.SetLabel(y)
        self.statictext_acceleration_z.SetLabel(z)

    def SetSTAngularVelocity(self, x:str="None", y:str="None", z:str="None"):
        self.statictext_angularvelocity_x.SetLabel(x)
        self.statictext_angularvelocity_y.SetLabel(y)
        self.statictext_angularvelocity_z.SetLabel(z)