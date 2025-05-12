# sidepanel.py

import wx
from utils import dip
import datetime

class SidePanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        # ------------------------------------------------------------
        # status
        # ------------------------------------------------------------
        
        # create staticbox
        sb_status = wx.StaticBox(self, label="Status")
        sb_status_sizer = wx.GridBagSizer(dip(3), dip(3))
        sb_status.SetSizer(sb_status_sizer)

        # modifiable statictexts
        self.statictext_status = wx.StaticText(sb_status, label="")
        self.statictext_network = wx.StaticText(sb_status, label="")
        self.statictext_server = wx.StaticText(sb_status, label="")
        
        # add to staticbox sizer
        sb_status_sizer.Add(wx.StaticText(sb_status, label="Status:"), pos=(0, 0), flag=wx.ALIGN_RIGHT|wx.TOP, border=dip(15))
        sb_status_sizer.Add(self.statictext_status, pos=(0, 1), flag=wx.ALIGN_LEFT|wx.TOP, border=dip(15))
        sb_status_sizer.Add(wx.StaticText(sb_status, label="Network:"), pos=(1, 0), flag=wx.ALIGN_RIGHT)
        sb_status_sizer.Add(self.statictext_network, pos=(1, 1), flag=wx.ALIGN_LEFT)
        sb_status_sizer.Add(wx.StaticText(sb_status, label="Server:"), pos=(2, 0), flag=wx.ALIGN_RIGHT)
        sb_status_sizer.Add(self.statictext_server, pos=(2, 1), flag=wx.ALIGN_LEFT)
        sb_status_sizer.AddGrowableCol(0, 1)
        sb_status_sizer.AddGrowableCol(1, 2)

        # set default values
        self.SetSTStatus(True)
        self.SetSTNetworkName("TotalPlay")
        self.SetSTServerIP("10.01.10.10")

        # add to main sizer
        self.sizer.Add(sb_status, proportion=0, flag=wx.EXPAND|wx.LEFT|wx.TOP|wx.RIGHT, border=dip(5))

        # ------------------------------------------------------------
        # vehicle data
        # ------------------------------------------------------------

        # create staticbox
        sb_vehicledata = wx.StaticBox(self, label="Vehicle Data")
        sb_vehicledata_sizer = wx.GridBagSizer(dip(3), dip(3))
        sb_vehicledata.SetSizer(sb_vehicledata_sizer)

        # modifiable statictexts
        self.statictext_acceleration = wx.StaticText(sb_vehicledata, label="")
        self.statictext_velocity = wx.StaticText(sb_vehicledata, label="")
        
        # add to staticbox sizer
        sb_vehicledata_sizer.Add(wx.StaticText(sb_vehicledata, label="Acceleration:"), pos=(0, 0), flag=wx.ALIGN_RIGHT|wx.TOP, border=dip(15))
        sb_vehicledata_sizer.Add(self.statictext_acceleration, pos=(0, 1), flag=wx.ALIGN_LEFT|wx.TOP, border=dip(15))
        sb_vehicledata_sizer.Add(wx.StaticText(sb_vehicledata, label="Velocity:"), pos=(1, 0), flag=wx.ALIGN_RIGHT)
        sb_vehicledata_sizer.Add(self.statictext_velocity, pos=(1, 1), flag=wx.ALIGN_LEFT)
        sb_vehicledata_sizer.AddGrowableCol(0, 1)
        sb_vehicledata_sizer.AddGrowableCol(1, 2)

        # set default values
        self.SetSTAcceleration("0.0 m/s^2")

        # add to main sizer
        self.sizer.Add(sb_vehicledata, proportion=0, flag=wx.EXPAND|wx.LEFT|wx.TOP|wx.RIGHT, border=dip(5))

        # ------------------------------------------------------------
        # voice control
        # ------------------------------------------------------------

        # create staticbox
        sb_voicecontrol = wx.StaticBox(self, label="Voice Control")
        sb_voicecontrol_sizer = wx.GridBagSizer(dip(3), dip(3))
        sb_voicecontrol.SetSizer(sb_voicecontrol_sizer)

        # modifiable statictexts
        self.test = wx.TextCtrl(sb_voicecontrol)
        button_talk = wx.Button(sb_voicecontrol, label="Talk to Rocky...")
        
        # add to staticbox sizer
        sb_voicecontrol_sizer.Add(self.test, pos=(0, 0), flag=wx.EXPAND|wx.TOP, border=dip(15))
        sb_voicecontrol_sizer.Add(button_talk, pos=(1, 0), flag=wx.EXPAND|wx.BOTTOM, border=dip(15))
        sb_voicecontrol_sizer.AddGrowableCol(0, 1)

        # add to main sizer
        self.sizer.Add(sb_voicecontrol, proportion=0, flag=wx.EXPAND|wx.LEFT|wx.TOP|wx.RIGHT, border=dip(5))

        # ------------------------------------------------------------
        # log
        # ------------------------------------------------------------

        # create staticbox
        sb_log = wx.StaticBox(self, label="Log")
        sb_log_sizer = wx.BoxSizer(wx.VERTICAL)
        sb_log.SetSizer(sb_log_sizer)

        self.textctrl_log = wx.TextCtrl(sb_log, style=wx.TE_MULTILINE|wx.TE_READONLY, size=wx.Size(-1, 200))
        self.AddLogMessage("INFO", "MQTT:Connecting...")
        
        # add to staticbox sizer
        sb_log_sizer.AddSpacer(dip(15))
        sb_log_sizer.Add(self.textctrl_log, flag=wx.EXPAND|wx.ALL, border=dip(3))

        # add to main sizer
        self.sizer.Add(sb_log, proportion=0, flag=wx.EXPAND|wx.LEFT|wx.TOP|wx.RIGHT, border=dip(5))



        self.sizer.Layout()

    def AddLogMessage(self, type: str, value:str):
        message = f"{datetime.datetime.now().strftime("%H:%M:%S")}  [{type}] - {value}\n"
        self.textctrl_log.AppendText(message)

    def SetSTStatus(self, value:bool):
        if value:
            self.statictext_status.SetLabel("Online")
            self.statictext_status.SetForegroundColour(wx.Colour(10, 160, 10))
        else:
            self.statictext_status.SetLabel("Offline")
            self.statictext_status.SetForegroundColour(wx.RED)

    def SetSTNetworkName(self, value:str):
        self.statictext_network.SetLabel(value)

    def SetSTServerIP(self, value:str):
        self.statictext_server.SetLabel(value)

    def SetSTAcceleration(self, value:str):
        self.statictext_acceleration.SetLabel(value)