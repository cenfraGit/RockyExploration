# panel_view.py

import wx
import ctypes
import wx.glcanvas as glcanvas
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram

source_vertex = """
#version 330 core
layout (location = 0) in vec3 aPos;
void main() {
  gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0);
}
"""

source_fragment = """
#version 330 core
out vec4 FragColor;
void main() {
  FragColor = vec4(1.0f, 0.5f, 0.2f, 1.0f);
}
"""

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
            glClearColor(0.0, 0.0, 0.0, 1.0)
            glClearDepth(1.0)
            glEnable(GL_DEPTH_TEST)
            glDepthMask(GL_TRUE)
            glDepthFunc(GL_LEQUAL)
            glDepthRange(0.0, 1.0)
            glEnable(GL_MULTISAMPLE)
            # test
            vertex_shader = compileShader(source_vertex, GL_VERTEX_SHADER)
            fragment_shader = compileShader(source_fragment, GL_FRAGMENT_SHADER)
            self.shader_program = compileProgram(vertex_shader, fragment_shader)
            self.vertices = np.array([-0.5, -0.5, 0.0,
                                      0.5, -0.5, 0.0,
                                      0.0, 0.5, 0.0], dtype=np.float32)
            self.VAO = glGenVertexArrays(1)
            self.VBO = glGenBuffers(1)
            glBindVertexArray(self.VAO)
            glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
            glBufferData(GL_ARRAY_BUFFER, self.vertices.flatten(), GL_STATIC_DRAW)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * ctypes.sizeof(ctypes.c_float), ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)
            self.init = True

    def OnEraseBackground(self, event):
        pass

    def OnSize(self, event):
        size = self.GetClientSize()
        if self.context:
            self.SetCurrent(self.context)
            glViewport(0, 0, size.width, size.height)
        event.Skip()

    def OnPaint(self, event):
        self.InitGL()
        glClearColor(0.2, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # glBegin(GL_TRIANGLES)
        # glColor3f(1.0, 0.0, 0.0)
        # glVertex3f(0.0, 0.5, 0.0)
        # glColor3f(0.0, 1.0, 0.0)
        # glVertex3f(-0.5, -0.5, 0.0)
        # glColor3f(0.0, 0.0, 1.0)
        # glVertex3f(0.5, -0.5, 0.0)
        # glEnd()
        glUseProgram(self.shader_program)
        glBindVertexArray(self.VAO)
        glDrawArrays(GL_TRIANGLES, 0, 3)

        # self.renderer.render(self.scene, self.camera)

        self.SwapBuffers()
        event.Skip()
        
