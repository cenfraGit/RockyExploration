# statusbar.py

import wx

class CustomStatusBar(wx.StatusBar):
    def __init__(self, parent):
        super().__init__(parent)

        self.SetFieldsCount(3)
        self.SetStatusWidths([-6, -1, -2])

        self.SetStatusText("Welcome to RE v1.0", 0)
        self.st_status = wx.StaticText(self, label="")
        self.st_address = wx.StaticText(self, label="")
        self.SetSTStatus(False)
        self.SetSTAddress("0.0.0.0")

        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnSize(self, event):
        self.Reposition()
        event.Skip()

    def Reposition(self):
        rect = self.GetFieldRect(1)
        rect = wx.Rect(rect.x+10, rect.y, rect.width-11, rect.height)
        self.st_status.SetRect(rect)
        rect = self.GetFieldRect(2)
        rect = wx.Rect(rect.x+10, rect.y, rect.width-11, rect.height)
        self.st_address.SetRect(rect)

    def SetSTStatus(self, value:bool):
        if value:
            self.st_status.SetLabel("Online")
            self.st_status.SetForegroundColour(wx.Colour(10, 160, 10))
        else:
            self.st_status.SetLabel("Offline")
            self.st_status.SetForegroundColour(wx.RED)

    def SetSTAddress(self, value:str):
        self.st_address.SetLabel(value)