# panel_view.py

import wx
import wx.glcanvas as glcanvas
import numpy as np
from OpenGL import GL
from OpenGL.GL import shaders

class PanelView(glcanvas.GLCanvas):
    def __init__(self, parent):

        dispAttrs = glcanvas.GLAttributes()
        dispAttrs.PlatformDefaults().Depth(16).DoubleBuffer().SampleBuffers(4).Samplers(4).EndList()

        super().__init__(parent, dispAttrs, size=wx.Size(300, 300))

        self.context = None
        self.init = False

        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def InitGL(self):
        if self.context is None:
            self.context = glcanvas.GLContext(self)
        self.SetCurrent(self.context)
        if not self.init:
            GL.glClearColor(0.0, 0.0, 0.0, 1.0)
            self.init = True

    def OnEraseBackground(self, event):
        pass

    def OnSize(self, event):
        size = self.GetClientSize()
        if self.context:
            self.SetCurrent(self.context)
            GL.glViewport(0, 0, size.width, size.height)
        event.Skip()

    def OnPaint(self, event):
        self.InitGL()
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glBegin(GL.GL_TRIANGLES)
        GL.glColor3f(1.0, 0.0, 0.0)
        GL.glVertex3f(0.0, 0.5, 0.0)
        GL.glColor3f(0.0, 1.0, 0.0)
        GL.glVertex3f(-0.5, -0.5, 0.0)
        GL.glColor3f(0.0, 0.0, 1.0)
        GL.glVertex3f(0.5, -0.5, 0.0)
        GL.glEnd()

        self.SwapBuffers()
        event.Skip()
        
