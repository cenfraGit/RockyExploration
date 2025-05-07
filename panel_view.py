# panel_view.py

import wx
import glm
import ctypes
import wx.glcanvas as glcanvas
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
from math import sin, cos

class PanelView(glcanvas.GLCanvas):
    def __init__(self, parent):

        dispAttrs = glcanvas.GLAttributes()
        dispAttrs.PlatformDefaults().Depth(16).DoubleBuffer().SampleBuffers(4).Samplers(4).EndList()

        super().__init__(parent, dispAttrs, size=wx.Size(300, 300))

        self.context = None
        self.init = False

        self.camera_position = glm.vec3(0.0, 0.0, 30.0)
        self.camera_front = glm.vec3(0.0, 0.0, -1.0)
        self.camera_up = glm.vec3(0.0, 1.0, 0.0)
        self.yaw = -90.0
        self.pitch = 0.0
        self.fov = 70.0
        self.projection = glm.perspective(glm.radians(self.fov), 300/300, 0.1, 500)

        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnPrimaryDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnPrimaryUp)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnSecondaryDown)
        self.Bind(wx.EVT_RIGHT_UP, self.OnSecondaryUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseDrag)

        self.Bind(wx.EVT_KEY_DOWN, self.OnKey)

    def get_shaders(self):

        source_vertex = """
        #version 330 core

        layout (location = 0) in vec3 v_pos;
        layout (location = 1) in vec3 v_color;
        //layout (location = 2) in vec3 v_normal;
        out vec3 color;

        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;

        void main() {
          gl_Position = projection * view * model * vec4(v_pos, 1.0f);
          color = v_color;
        }
        
        """

        source_fragment = """
        #version 330 core
        in vec3 color;
        out vec4 FragColor;
        void main() {
          FragColor = vec4(color.x, color.y, color.z, 1.0f);
        }
        """

        # source_vertex = """
        # #version 330 core
        
        # uniform mat4 matrix_projection;
        # uniform mat4 matrix_view;
        # uniform mat4 matrix_model;
        
        # layout (location = 0) in vec3 vertex_position;
        # layout (location = 1) in vec3 vertex_color;
        # layout (location = 2) in vec3 vertex_normal;
        
        # out vec3 normal;
        # out vec3 color;
        # out vec3 frag_pos;
        
        # void main() {
        #   normal = mat3(transpose(inverse(matrix_model))) * vertex_normal;
        #   color = vertex_color;
        #   frag_pos = vec3(matrix_model * vec4(vertex_position, 1.0));
        #   gl_Position = matrix_projection * matrix_view * matrix_model * vec4(vertex_position, 1.0);
        # }
        # """

        # source_fragment = """
        # #version 330 core

        # struct LightDirectional {
        #   vec3 direction;
        #   vec3 ambient;
        #   vec3 diffuse;
        #   vec3 specular;
        # };

        # struct Material {
        #   float shininess;
        #   vec3 ambient;
        #   vec3 diffuse;
        #   vec3 specular;
        # };

        # uniform bool bool_lighting;
        # uniform vec3 view_pos;
        
        # uniform LightDirectional light_directional;
        # uniform Material material;
        
        # in vec3 color;
        # in vec3 normal;
        # in vec3 frag_pos;
        # out vec4 frag_color;

        # // prototypes
        # vec3 CalcLightDir(LightDirectional light, vec3 normal, vec3 view_dir);
        
        # void main() {
        
        #   vec3 result;
        
        #   if (bool_lighting) {
        #     vec3 norm = normalize(normal);
        #     vec3 view_dir = normalize(view_pos - frag_pos);
        #     result = CalcLightDir(light_directional, norm, view_dir);
        #   } else {
        #     result = color;
        #   }
        #   frag_color = vec4(result, 1.0);
        # }

        # vec3 CalcLightDir(LightDirectional light, vec3 normal, vec3 view_dir) {
        #   vec3 light_dir = normalize(-light.direction);
        #   float diff = max(dot(normal, light_dir), 0.0);
        #   vec3 reflect_dir = reflect(-light_dir, normal);
        #   float spec = pow(max(dot(view_dir, reflect_dir), 0.0), material.shininess);

        #   vec3 ambient = light.ambient * material.ambient;
        #   vec3 diffuse = light.diffuse * diff * material.diffuse;
        #   vec3 specular = light.specular * spec * material.specular;

        #   return (ambient + diffuse + specular) * color;
        # }
        # """

        vertex_shader = compileShader(source_vertex, GL_VERTEX_SHADER)
        fragment_shader = compileShader(source_fragment, GL_FRAGMENT_SHADER)
        return vertex_shader, fragment_shader
        

    def InitGL(self):
        if self.context is None:
            self.context = glcanvas.GLContext(self)
        self.SetCurrent(self.context)
        if not self.init:
            glClearColor(0.0, 0.0, 0.0, 1.0)
            # glClearDepth(1.0)
            # glEnable(GL_DEPTH_TEST)
            # glDepthMask(GL_TRUE)
            # glDepthFunc(GL_LEQUAL)
            # glDepthRange(0.0, 1.0)
            # glEnable(GL_MULTISAMPLE)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

            vertex_shader, fragment_shader = self.get_shaders()
            self.shader_program = compileProgram(vertex_shader, fragment_shader)

            self.vertices, self.colors, self.normals, self.uvs = self.read_obj("objects/rocky.obj")

            # ----------------- vao ----------------- #
            self.VAO = glGenVertexArrays(1)
            glBindVertexArray(self.VAO)
            # --------------- position --------------- #
            vbo_position = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, vbo_position)
            glBufferData(GL_ARRAY_BUFFER, self.vertices.flatten(), GL_STATIC_DRAW)
            glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0)) # position
            glEnableVertexAttribArray(0)
            # ---------------- color ---------------- #
            vbo_colors = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, vbo_colors)
            glBufferData(GL_ARRAY_BUFFER, self.colors.flatten(), GL_STATIC_DRAW)
            glVertexAttribPointer(1, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0)) # color
            glEnableVertexAttribArray(1)
            # --------------- normals --------------- #
            # vbo_normals = glGenBuffers(1)
            # glBindBuffer(GL_ARRAY_BUFFER, vbo_normals)
            # glBufferData(GL_ARRAY_BUFFER, self.normals.flatten(), GL_STATIC_DRAW)
            # glVertexAttribPointer(2, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0)) # normal
            # glEnableVertexAttribArray(2)
            
            self.init = True

    def read_obj(self, filename, color=[1, 1, 1]):
        positions = []
        vertices = []
        faces = []
        normals = []
        uvs = []
        with open(filename) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                line_elements = line.split(' ')
                # check if vertex
                if (line_elements[0] == "v"):
                    vertices.append([float(line_elements[1]), float(line_elements[2]), float(line_elements[3])])
                # check if face
                elif (line_elements[0] == "f"):
                    face = []
                    # get data for each vertex in the face
                    for i in range(1, len(line_elements)):
                        # split vertex position/uv/normal data
                        vertex_data = line_elements[i].split('/')
                        face.append([int(v)-1 if v else None for v in vertex_data])
                    faces.append(face)
                # vertex normal
                elif (line_elements[0] == "vn"):
                    normals.append([float(line_elements[1]), float(line_elements[2]), float(line_elements[3])])
                # textures
                elif (line_elements[0] == "vt"):
                    uvs.append([float(line_elements[1]), float(line_elements[2])])

        positions = []
        normals_new = []
        uvs_new = []
        
        for face in faces:
            for vert in face:
                positions.append(vertices[vert[0]])

                if len(vert) > 1 and vert[1] is not None:
                    uvs_new.append(uvs[vert[1]])
                else:
                    uvs_new.append([0.0, 0.0])
                    
                if len(vert) > 2 and vert[2] is not None:
                    normals_new.append(normals[vert[2]])
                else:
                    normals_new.append([0.0, 1.0, 0.0]) 

        colors = [color for _ in range(len(positions))]

        return np.array(positions, dtype=np.float32), np.array(colors, dtype=np.float32), np.array(normals_new, dtype=np.float32), np.array(uvs_new, dtype=np.float32)

    def OnEraseBackground(self, event):
        pass

    def OnSize(self, event):
        size = self.GetClientSize()
        if self.context:
            self.SetCurrent(self.context)
            glViewport(0, 0, size.width, size.height)
            self.projection = glm.perspective(glm.radians(self.fov), size.width / size.height, 0.1, 500)
        event.Skip()

    def OnKey(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_UP or chr(keycode).lower() == 'w':
            self.camera_position.z += 1

        self.Refresh()
        event.Skip()

    def OnPrimaryDown(self, event):
        try:
            self.CaptureMouse()
        except:
            pass
        self.x, self.y = self.lastx, self.lasty = event.GetPosition()

    def OnPrimaryUp(self, event):
        self.ReleaseMouse()

    def OnSecondaryDown(self, event):
        try:
            self.CaptureMouse()
        except:
            pass
        self.x, self.y = self.lastx, self.lasty = event.GetPosition()

    def OnSecondaryUp(self, event):
        self.ReleaseMouse()

    def OnMouseDrag(self, event):
        
        # Camera rotation (primary click)
        
        if event.Dragging() and event.LeftIsDown():
            
            self.lastx, self.lasty = self.x, self.y
            self.x, self.y = event.GetPosition()
            self.Refresh(False)

            xoffset = self.x - self.lastx
            yoffset = self.y - self.lasty
            
            sensitivity = 0.1
            xoffset *= sensitivity
            yoffset *= sensitivity

            self.yaw += xoffset
            self.pitch -= yoffset

            self.pitch = 89 if self.pitch > 89 else self.pitch
            self.pitch = -89 if self.pitch < -89 else self.pitch

            front = glm.vec3()
            front.x = cos(glm.radians(self.yaw)) * cos(glm.radians(self.pitch))
            front.y = sin(glm.radians(self.pitch))
            front.z = sin(glm.radians(self.yaw)) * cos(glm.radians(self.pitch))
            self.camera_front = glm.normalize(front)

        # Camera closer/further to origin. (secondary click)        
        elif event.Dragging() and event.RightIsDown():

            self.lastx, self.lasty = self.x, self.y
            self.x, self.y = event.GetPosition()
            self.Refresh(False)

    def OnPaint(self, event):
        
        self.InitGL()
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glUseProgram(self.shader_program)

        model = glm.mat4(1.0)
        view = glm.mat4(1.0)
        projection = glm.mat4(1.0)
        
        # model = glm.rotate(model, 1.8, glm.vec3(0.5, 1.0, 0.0))

        model = glm.scale(glm.vec3(0.1, 0.1, 0.1))
        view = glm.lookAt(self.camera_position, self.camera_position + self.camera_front, self.camera_up)

        loc_model = glGetUniformLocation(self.shader_program, b"model")
        loc_view = glGetUniformLocation(self.shader_program, b"view")
        loc_projection = glGetUniformLocation(self.shader_program, b"projection")

        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(model))
        glUniformMatrix4fv(loc_view, 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(loc_projection, 1, GL_FALSE, glm.value_ptr(self.projection))
        
        glBindVertexArray(self.VAO)

        glPointSize(10)
        glDrawArrays(GL_TRIANGLES, 0, len(self.vertices) // 3)

        self.SwapBuffers()
        event.Skip()
        
