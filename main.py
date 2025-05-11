# main.py

import wx
from utils import dip
from camera import FrameCamera
from view import PanelView
from controls import FrameControlsVoice
from sidepanel import SidePanel

import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)

# ------------------------------------------------------------
# frame main
# ------------------------------------------------------------

class FrameMain(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # ------------- frame setup ------------- #
        
        self.SetTitle("Rocky Exploration UI - v1.0")
        self.SetClientSize(dip(800, 500))

        # all subpanels will be children of the main panel
        self.panel_main = wx.Panel(self)
        self.sizer = wx.GridBagSizer()
        self.panel_main.SetSizer(self.sizer)

        # -------------- panel view -------------- #

        self.panel_view = PanelView(self.panel_main)
        self.panel_view.SetBackgroundColour(wx.GREEN)
        self.sizer.Add(self.panel_view, pos=(0, 0), flag=wx.EXPAND)

        # ----------- panel info ----------- #
        
        self.panel_info = SidePanel(self.panel_main)
        self.sizer.Add(self.panel_info, pos=(0, 1), flag=wx.EXPAND)

        # ----------- sizer growables ----------- #
        
        self.sizer.AddGrowableCol(0, 3)
        self.sizer.AddGrowableCol(1, 1)
        self.sizer.AddGrowableRow(0, 1)
        self.sizer.Layout()

        self.controls_mode = "manual"

        # ------------------------------------------------------------
        # menubar
        # ------------------------------------------------------------

        menubar = wx.MenuBar()
        
        # ------------ configuration ------------ #
        
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
        menu_configuration.AppendSubMenu(submenu_control, "Control Mode", "Change Rocky's control mode.")
        menu_configuration.AppendSeparator()
        menu_configuration.Append(item_exit)

        self.Bind(wx.EVT_MENU, self.OnExit, item_exit)
        self.Bind(wx.EVT_MENU, self.OnMenubarControlsManual, radio_control_manual)
        self.Bind(wx.EVT_MENU, self.OnMenubarControlsVoice, radio_control_voice)

        # ----------------- view ----------------- #

        menu_view = wx.Menu()
        item_camera_footage = wx.MenuItem(menu_view, -1, "Show camera footage...", "Show Rocky's camera footage in an external window.")
        item_controls = wx.MenuItem(menu_view, -1, "Show controls...", "Show the control panel for the current control mode.")
        
        menu_view.Append(item_camera_footage)
        menu_view.Append(item_controls)

        self.Bind(wx.EVT_MENU, self.OnCamera, item_camera_footage)
        self.Bind(wx.EVT_MENU, self.OnControls, item_controls)

        # ----------------- help ----------------- #
        
        menu_help = wx.Menu()
        item_log = wx.MenuItem(menu_help, -1, "&Log...\tCtrl+T", "See log.")
        menu_help.Append(item_log)

        self.Bind(wx.EVT_MENU, self.OnLog, item_log)

        # ------------ setup menubar ------------ #

        menubar.Append(menu_configuration, "Configuration")
        menubar.Append(menu_view, "View")
        menubar.Append(menu_help, "Help")
        
        self.SetMenuBar(menubar)

        # -------------- statusbar -------------- #

        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText("Welcome to RE v1.0")

    def OnExit(self, event):
        self.Close()

    def OnCamera(self, event):
        frame = FrameCamera(self)
        frame.Show()

    def OnMenubarControlsManual(self, event):
        self.controls_mode = "manual"

    def OnMenubarControlsVoice(self, event):
        self.controls_mode = "voice"

    def OnControls(self, event):
        if self.controls_mode == "manual":
            pass
        if self.controls_mode == "voice":
            frame = FrameControlsVoice(self)
            frame.Show()

    def OnLog(self, event):
        pass

if __name__ == "__main__":
    app = wx.App()
    instance = FrameMain(None)
    instance.Show()
    app.MainLoop()
