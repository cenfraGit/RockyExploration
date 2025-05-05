# main.py

import wx
import cv2
from utils import dip
from panel_camera import PanelCamera
from panel_view import PanelView

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
        self.SetClientSize(dip(800, 500))

        # all subpanels will be children of the main panel
        self.panel_main = wx.Panel(self)
        self.sizer = wx.GridBagSizer()
        self.panel_main.SetSizer(self.sizer)

        # -------------- panel view -------------- #

        self.panel_view = PanelView(self.panel_main)
        self.panel_view.SetBackgroundColour(wx.GREEN)
        self.sizer.Add(self.panel_view, pos=(0, 0), flag=wx.EXPAND)

        # -------------- panel cam -------------- #
        
        self.capture = cv2.VideoCapture(0)
        self.panel = PanelCamera(self.panel_main, self.capture)
        self.sizer.Add(self.panel, pos=(0, 1), flag=wx.EXPAND)

        # ------------- bottom panel ------------- #

        self.panel_bottom = wx.Panel(self.panel_main)
        self.panel_bottom.SetBackgroundColour(wx.RED)
        self.sizer.Add(self.panel_bottom, pos=(1, 0), span=(1, 2), flag=wx.EXPAND)

        # ----------- sizer growables ----------- #
        
        self.sizer.AddGrowableCol(0, 1)
        self.sizer.AddGrowableCol(1, 1)
        self.sizer.AddGrowableRow(0, 1)
        self.sizer.AddGrowableRow(1, 1)
        self.sizer.Layout()

        # ------------------------------------------------------------
        # menubar
        # ------------------------------------------------------------

        menubar = wx.MenuBar()
        menu_configuration = wx.Menu()
        item_connect = wx.MenuItem(menu_configuration, -1, "&Connect...\tCtrl+C", "Connect to Rocky.")
        # submenu for control mode
        submenu_control = wx.Menu()
        radio_control_manual = wx.MenuItem(submenu_control, wx.ID_ANY, "Manual", kind=wx.ITEM_RADIO)
        radio_control_voice = wx.MenuItem(submenu_control, wx.ID_ANY, "Voice", kind=wx.ITEM_RADIO)
        submenu_control.Append(radio_control_manual)
        submenu_control.Append(radio_control_voice)
        item_exit = wx.MenuItem(menu_configuration, wx.ID_EXIT, "&Exit...\tAlt+F4", "Exit the application.")
        menu_configuration.Append(item_connect)
        menu_configuration.AppendSubMenu(submenu_control, "Control", "Change control mode.")
        menu_configuration.AppendSeparator()
        menu_configuration.Append(item_exit)

        menu_help = wx.Menu()
        item_log = wx.MenuItem(menu_help, -1, "&Log...\tCtrl+T", "See log.")
        menu_help.Append(item_log)

        menubar.Append(menu_configuration, "Configuration")
        menubar.Append(menu_help, "Help")
        
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnExit, item_exit)

        # -------------- statusbar -------------- #

        self.statusbar = self.CreateStatusBar()
        self.SetStatus("Offline")

    def SetStatus(self, text):
        self.statusbar.SetStatusText(f"Status: {text}")

    def OnExit(self, event):
        self.Close()

if __name__ == "__main__":
    app = wx.App()
    instance = FrameMain(None)
    instance.Show()
    app.MainLoop()

