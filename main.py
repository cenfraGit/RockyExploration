# main.py

import wx
import wx.aui as aui
from utils import dip
from camera import PanelCamera
from view import PanelView
from panelinfo import PanelInfo
from statusbar import CustomStatusBar
from mqtt_handler import MQTTHandler
from vehiclestate import VehicleState
import json
import datetime
import cv2

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

        self.connection_status = False
        self.vehicle_state = VehicleState()

        self._mgr = aui.AuiManager()
        self._mgr.SetManagedWindow(self)

        self._panel_view = PanelView(self, self.vehicle_state)
        self._panel_info = PanelInfo(self)
        url = "http://172.20.10.11:81/stream"
        #self.capture = cv2.VideoCapture(0)
        #self.capture = cv2.VideoCapture(url)
        #self._panel_camera = PanelCamera(self, self.capture)
        self._panel_camera = wx.Panel(self)

        textctrl_font = wx.Font(10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Courier")

        self._textctrl_log = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.NO_BORDER, size=wx.Size(-1, 90))
        self._textctrl_log.SetFont(textctrl_font)
        self.AddLogMessage("INFO", "Initialized.")

        self._textctrl_mqtt = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.NO_BORDER, size=wx.Size(-1, 90))
        self._textctrl_mqtt.SetFont(textctrl_font)

        self._mgr.AddPane(self._panel_view, aui.AuiPaneInfo().Name("view").Top().CenterPane())
        self._mgr.AddPane(self._panel_info, aui.AuiPaneInfo().Name("info").Caption("Info").CloseButton(True))
        self._mgr.AddPane(self._panel_camera, aui.AuiPaneInfo().Name("camera").Caption("Camera footage").CloseButton(True))
        self._mgr.AddPane(self._textctrl_log, aui.AuiPaneInfo().Name("textctrl_log").Caption("Log").CloseButton(False))
        self._mgr.AddPane(self._textctrl_mqtt, aui.AuiPaneInfo().Name("textctrl_mqtt").Caption("MQTT").CloseButton(True))

        self._mgr.GetPane("view").Show().CenterPane()
        self._mgr.GetPane("camera").Show().Left().MinSize(wx.Size(300, 300))
        self._mgr.GetPane("textctrl_log").Show().Bottom()
        self._mgr.GetPane("textctrl_mqtt").Show().Left()
        self._mgr.GetPane("info").Show().Right().MinSize(wx.Size(300, -1))

        self._mgr.Update()

        self._mgr.GetArtProvider().SetColour(aui.AUI_DOCKART_INACTIVE_CAPTION_COLOUR, wx.Colour(100,151,177))
        self._mgr.GetArtProvider().SetMetric(aui.AUI_DOCKART_GRADIENT_TYPE, aui.AUI_GRADIENT_NONE)

        # ------------------------------------------------------------
        # menubar
        # ------------------------------------------------------------

        menubar = wx.MenuBar()
        
        # ------------ configuration ------------ #
        
        menu_configuration = wx.Menu()
        item_connect = wx.MenuItem(menu_configuration, -1, "&Connect...", "Connect to a MQTT server.")
        item_disconnect = wx.MenuItem(menu_configuration, -1, "&Disconnect...", "Disconnect from the server.")
        item_exit = wx.MenuItem(menu_configuration, wx.ID_EXIT, "&Exit...\tAlt+F4", "Exit the application.")
        menu_configuration.Append(item_connect)
        menu_configuration.Append(item_disconnect)
        menu_configuration.AppendSeparator()
        menu_configuration.Append(item_exit)

        self.Bind(wx.EVT_MENU, self.OnConnect, item_connect)
        self.Bind(wx.EVT_MENU, self.OnDisconnect, item_disconnect)
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

        self.statusbar = CustomStatusBar(self)
        self.SetStatusBar(self.statusbar)

        # ------------------------------------------------------------
        # mqtt
        # ------------------------------------------------------------

        self.mqtt_handler = MQTTHandler(self._textctrl_mqtt, self.vehicle_state)

    def OnConnect(self, event):
        with open("config.json", "r") as file:
            data = json.load(file)
        dlg = wx.TextEntryDialog(self, "Server address:", "MQTT Server", value=data["server_address"])
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        self.AddLogMessage("INFO", "MQTT: Connecting...")
        self.mqtt_handler.SetBrokerAddress(dlg.GetValue())
        self.connection_status = self.mqtt_handler.connect()
        self.statusbar.SetSTStatus(self.connection_status)
        if self.connection_status:
            self.AddLogMessage("INFO", f"MQTT: Successfully connected to {dlg.GetValue()}.")
            self.statusbar.SetSTAddress(dlg.GetValue())
        else:
            self.AddLogMessage("INFO", f"MQTT: Could not connect to \"{dlg.GetValue()}\". Please check the connection.")

    def OnDisconnect(self, event):
        if self.connection_status:
            self.mqtt_handler.disconnect()
            self.statusbar.SetSTStatus(False)
            self.statusbar.SetSTAddress("0.0.0.0")
            self.AddLogMessage("INFO", f"MQTT: Disconnected successfully.")
            self.connection_status = False
        else:
            wx.MessageDialog(self, "Server is offline.", "Disconnect failed.", style=wx.OK).ShowModal()

    def OnExit(self, event):
        self.Close()

    def OnCamera(self, event):
        pass

    def AddLogMessage(self, type: str, value:str):
        message = f">> {datetime.datetime.now().strftime("%H:%M:%S")} [{type}] - {value}\n"
        self._textctrl_log.AppendText(message)

if __name__ == "__main__":
    app = wx.App()
    instance = FrameMain(None)
    instance.Show()
    app.MainLoop()