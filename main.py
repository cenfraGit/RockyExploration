# main.py

import wx
import cv2
from utils import dip
from panel_camera import PanelCamera

import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)

# ------------------------------------------------------------
# frame main
# ------------------------------------------------------------

class FrameMain(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # ------------- frame setup ------------- #
        
        self.SetTitle("Rocky")
        self.SetClientSize(dip(300, 300))

        # all subpanels will be children of the main panel
        self.panel_main = wx.Panel(self)
        self.sizer = wx.GridBagSizer()
        self.panel_main.SetSizer(self.sizer)

        # -------------- panel cam -------------- #
        
        self.capture = cv2.VideoCapture(0)
        self.panel = PanelCamera(self.panel_main, self.capture)
        self.sizer.Add(self.panel, pos=(0, 0), flag=wx.EXPAND)

        # -------------- panel view -------------- #

        self.panel_view = wx.Panel(self.panel_main)
        self.panel_view.SetBackgroundColour(wx.GREEN)
        self.sizer.Add(self.panel_view, pos=(0, 1), flag=wx.EXPAND)

        # ---------- panel instructions ---------- #

        self.panel_instructions = wx.Panel(self.panel_main)
        self.panel_instructions.SetBackgroundColour(wx.RED)
        self.sizer.Add(self.panel_instructions, pos=(1, 0), span=(1, 2), flag=wx.EXPAND)

        # ----------- sizer growables ----------- #
        
        self.sizer.AddGrowableCol(0, 1)
        self.sizer.AddGrowableCol(1, 1)
        self.sizer.AddGrowableRow(0, 1)
        self.sizer.AddGrowableRow(1, 1)
        self.sizer.Layout()

if __name__ == "__main__":
    app = wx.App()
    instance = FrameMain(None)
    instance.Show()
    app.MainLoop()

