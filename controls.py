# controls.py

import wx

class FrameControls(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.SetTitle("Controls")
