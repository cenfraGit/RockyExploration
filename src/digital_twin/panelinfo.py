# panelinfo.py

import wx
import wx.grid as grid
from utils import dip

class PanelInfo(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

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

        self.sizer.Layout()
        

    def SetSTAcceleration(self, x:str="None", y:str="None", z:str="None"):
        self.statictext_acceleration_x.SetLabel(x)
        self.statictext_acceleration_y.SetLabel(y)
        self.statictext_acceleration_z.SetLabel(z)

    def SetSTAngularVelocity(self, x:str="None", y:str="None", z:str="None"):
        self.statictext_angularvelocity_x.SetLabel(x)
        self.statictext_angularvelocity_y.SetLabel(y)
        self.statictext_angularvelocity_z.SetLabel(z)
