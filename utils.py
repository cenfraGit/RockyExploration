# utils.py

import wx

def dip(*args):
    if len(args) == 1:
        return wx.ScreenDC().FromDIP(wx.Size(args[0], args[0]))[0]
    elif len(args) == 2:
        return wx.ScreenDC().FromDIP(wx.Size(args[0], args[1]))
