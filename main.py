# main.py

import wx
from utils import dip
from camera import FrameCamera
from view import PanelView
from sidepanel import SidePanel
from mqtt_handler import MQTTHandler
import json

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

        # ----------- mqtt ----------- #

        self.mqtt_handler = MQTTHandler()        

        # -------------- panel view -------------- #

        self.panel_view = PanelView(self.panel_main)
        self.sizer.Add(self.panel_view, pos=(0, 0), flag=wx.EXPAND)

        # ----------- panel info ----------- #
        
        self.panel_info = SidePanel(self.panel_main)
        self.sizer.Add(self.panel_info, pos=(0, 1), flag=wx.EXPAND)

        # ----------- sizer growables ----------- #
        
        self.sizer.AddGrowableCol(0, 3)
        self.sizer.AddGrowableCol(1, 1)
        self.sizer.AddGrowableRow(0, 1)
        self.sizer.Layout()

        # ------------------------------------------------------------
        # menubar
        # ------------------------------------------------------------

        menubar = wx.MenuBar()
        
        # ------------ configuration ------------ #
        
        menu_configuration = wx.Menu()
        item_connect = wx.MenuItem(menu_configuration, -1, "&Connect...", "Connect to a MQTT server.")
        item_exit = wx.MenuItem(menu_configuration, wx.ID_EXIT, "&Exit...\tAlt+F4", "Exit the application.")
        menu_configuration.Append(item_connect)
        menu_configuration.AppendSeparator()
        menu_configuration.Append(item_exit)

        self.Bind(wx.EVT_MENU, self.OnConnect, item_connect)
        self.Bind(wx.EVT_MENU, self.OnExit, item_exit)

        # ----------------- view ----------------- #

        menu_view = wx.Menu()
        item_camera_footage = wx.MenuItem(menu_view, -1, "Show camera footage...", "Show Rocky's camera footage in an external window.")
        item_topics = wx.MenuItem(menu_view, -1, "Show MQTT messages...", "Show all messages on the server.")
        
        menu_view.Append(item_camera_footage)
        menu_view.Append(item_topics)

        self.Bind(wx.EVT_MENU, self.OnCamera, item_camera_footage)

        # ------------ setup menubar ------------ #

        menubar.Append(menu_configuration, "Configuration")
        menubar.Append(menu_view, "View")
        
        self.SetMenuBar(menubar)

        # -------------- statusbar -------------- #

        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText("Welcome to RE v1.0")

    def OnConnect(self, event):
        with open("config.json", "r") as file:
            data = json.load(file)
        dlg = wx.TextEntryDialog(self, "IP:", "MQTT Server", value=data["server_address"])
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        self.mqtt_handler.SetBrokerAddress(dlg.GetValue())
        self.mqtt_handler.connect()

    def OnExit(self, event):
        self.Close()

    def OnCamera(self, event):
        frame = FrameCamera(self)
        frame.Show()

if __name__ == "__main__":
    app = wx.App()
    instance = FrameMain(None)
    instance.Show()
    app.MainLoop()