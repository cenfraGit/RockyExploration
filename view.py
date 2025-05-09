# view.py

import wx
import glm
import ctypes
import wx.glcanvas as glcanvas
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
from math import sin, cos
from utils import read_obj
import time
from random import uniform

class Camera:
    def __init__(self):
        self.position = glm.vec3(0.0, 0.0, 30.0)
        self.front = glm.vec3(0.0, 0.0, -1.0)
        self.up = glm.vec3(0.0, 1.0, 0.0)
        
        self.yaw = -90.0
        self.pitch = 0.0
        self.fov = 80.0
        self.projection = glm.perspective(glm.radians(self.fov), 500/300, 0.1, 10000)

class VehicleBase:
    def __init__(self):

        self.shader_program = None
        self.vertex_count = 0
        self.model = glm.mat4(1.0)

        self.material_data = {
            "shininess": 16.0,
            "ambient": [1.0, 1.0, 1.0],
            "diffuse": [0.5, 0.5, 0.5],
            "specular": [0.2, 0.2, 0.2]
        }

    def init_object(self) -> None:

        source_vertex = """
        #version 330 core
        
        uniform mat4 projection;
        uniform mat4 view;
        uniform mat4 model;
        
        layout (location = 0) in vec3 vertex_position;
        layout (location = 1) in vec3 vertex_color;
        layout (location = 2) in vec3 vertex_normal;
        
        out vec3 normal;
        out vec3 color;
        out vec3 frag_pos;
        
        void main() {
          normal = mat3(transpose(inverse(model))) * vertex_normal;
          color = vertex_color;
          frag_pos = vec3(model * vec4(vertex_position, 1.0));
          gl_Position = projection * view * model * vec4(vertex_position, 1.0);
        }
        """

        source_fragment = """
        #version 330 core

        struct LightDirectional {
          vec3 direction;
          vec3 ambient;
          vec3 diffuse;
          vec3 specular;
        };

        struct Material {
          float shininess;
          vec3 ambient;
          vec3 diffuse;
          vec3 specular;
        };

        uniform bool bool_lighting;
        uniform vec3 view_pos;
        
        uniform LightDirectional light_directional;
        uniform Material material;
        
        in vec3 color;
        in vec3 normal;
        in vec3 frag_pos;
        out vec4 frag_color;

        // prototypes
        vec3 CalcLightDir(LightDirectional light, vec3 normal, vec3 view_dir);
        
        void main() {
        
          vec3 result;
        
          if (bool_lighting) {
            vec3 norm = normalize(normal);
            vec3 view_dir = normalize(view_pos - frag_pos);
            result = CalcLightDir(light_directional, norm, view_dir);
          } else {
            result = color;
          }
          frag_color = vec4(result, 1.0);
          //frag_color = vec4(1.0, 1.0, 1.0, 1.0);
        }

        vec3 CalcLightDir(LightDirectional light, vec3 normal, vec3 view_dir) {
          vec3 light_dir = normalize(-light.direction);
          float diff = max(dot(normal, light_dir), 0.0);
          vec3 reflect_dir = reflect(-light_dir, normal);
          float spec = pow(max(dot(view_dir, reflect_dir), 0.0), material.shininess);

          vec3 ambient = light.ambient * material.ambient;
          vec3 diffuse = light.diffuse * diff * material.diffuse;
          vec3 specular = light.specular * spec * material.specular;

          return (ambient + diffuse + specular) * color;
        }
        """

        # ------------------------------------------------------------
        # compilation
        # ------------------------------------------------------------

        vertex_shader = compileShader(source_vertex, GL_VERTEX_SHADER)
        fragment_shader = compileShader(source_fragment, GL_FRAGMENT_SHADER)
        self.shader_program = compileProgram(vertex_shader, fragment_shader)

        source_vertex = """
        #version 330 core

        layout (location = 0) in vec3 v_pos;
 
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;

        void main() {
          gl_Position = projection * view * model * vec4(v_pos, 1.0f);
        }
        """

        source_fragment = """
        #version 330 core
        out vec4 FragColor;
        void main() {
          FragColor = vec4(90/255.0,121/255.0,200/255.0, 1.0f); // 0.6 red only // 90/255.0, 121/255.0, 200/255.0
        }
        """

        vertex_shader_wire = compileShader(source_vertex, GL_VERTEX_SHADER)
        fragment_shader_wire = compileShader(source_fragment, GL_FRAGMENT_SHADER)
        self.shader_program_wire = compileProgram(vertex_shader_wire, fragment_shader_wire)

        vertices, colors, normals, uvs = read_obj("objects/rocky.obj", [0.1, 0.1, 0.1])

        # ----------------- vao ----------------- #
        self.VAO = glGenVertexArrays(1)
        glBindVertexArray(self.VAO)
        # --------------- position --------------- #
        vbo_position = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_position)
        glBufferData(GL_ARRAY_BUFFER, vertices.flatten(), GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0)) # position
        glEnableVertexAttribArray(0)
        # ---------------- color ---------------- #
        vbo_colors = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_colors)
        glBufferData(GL_ARRAY_BUFFER, colors.flatten(), GL_STATIC_DRAW)
        glVertexAttribPointer(1, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0)) # color
        glEnableVertexAttribArray(1)
        # --------------- normals --------------- #
        vbo_normals = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_normals)
        glBufferData(GL_ARRAY_BUFFER, normals.flatten(), GL_STATIC_DRAW)
        glVertexAttribPointer(2, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0)) # normal
        glEnableVertexAttribArray(2)

        self.vertex_count = len(vertices)

    def get_position(self) -> glm.vec3:
        return glm.vec3(self.model[3][0],
                        self.model[3][1],
                        self.model[3][2])

    def draw_object(self, camera: Camera, light_directional: dict) -> None:

        if self.shader_program == None:
            return

        view = glm.lookAt(camera.position, camera.position + camera.front, camera.up)

        glUseProgram(self.shader_program_wire)
        
        loc_model = glGetUniformLocation(self.shader_program_wire, b"model")
        loc_view = glGetUniformLocation(self.shader_program_wire, b"view")
        loc_projection = glGetUniformLocation(self.shader_program_wire, b"projection")
        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(self.model))
        glUniformMatrix4fv(loc_view, 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(loc_projection, 1, GL_FALSE, glm.value_ptr(camera.projection))

        glBindVertexArray(self.VAO)

        glCullFace(GL_FRONT)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glLineWidth(4)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

        glCullFace(GL_BACK)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
        glUseProgram(self.shader_program)
        
        loc_model = glGetUniformLocation(self.shader_program, b"model")
        loc_view = glGetUniformLocation(self.shader_program, b"view")
        loc_projection = glGetUniformLocation(self.shader_program, b"projection")

        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(self.model))
        glUniformMatrix4fv(loc_view, 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(loc_projection, 1, GL_FALSE, glm.value_ptr(camera.projection))

        # fragment uniforms
        
        glUniform1i(glGetUniformLocation(self.shader_program, b"bool_lighting"), 1)
        glUniform3f(glGetUniformLocation(self.shader_program, b"view_pos"),
                    camera.position.x,
                    camera.position.y,
                    camera.position.z)

        glUniform3f(glGetUniformLocation(self.shader_program, b"light_directional.direction"), *light_directional["direction"])
        glUniform3f(glGetUniformLocation(self.shader_program, b"light_directional.ambient"), *light_directional["ambient"])
        glUniform3f(glGetUniformLocation(self.shader_program, b"light_directional.diffuse"), *light_directional["diffuse"])
        glUniform3f(glGetUniformLocation(self.shader_program, b"light_directional.specular"), *light_directional["specular"])

        glUniform1f(glGetUniformLocation(self.shader_program, b"material.shininess"), self.material_data["shininess"])
        glUniform3f(glGetUniformLocation(self.shader_program, b"material.ambient"), *self.material_data["ambient"])
        glUniform3f(glGetUniformLocation(self.shader_program, b"material.diffuse"), *self.material_data["diffuse"])
        glUniform3f(glGetUniformLocation(self.shader_program, b"material.specular"), *self.material_data["specular"])
        
        glBindVertexArray(self.VAO)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

class WarningPanel:
    def __init__(self, width=140, height=140):

        self.shader_program = None
        self.vertex_count = 0
        self.width = width
        self.height = height

    def init_object(self) -> None:

        source_vertex = """
        #version 330 core

        layout (location = 0) in vec3 v_pos;
        layout (location = 1) in vec3 v_color;
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
          FragColor = vec4(color.x, color.y, color.z, 0.5f);
        }
        """

        # ------------------------------------------------------------
        # compilation
        # ------------------------------------------------------------

        vertex_shader = compileShader(source_vertex, GL_VERTEX_SHADER)
        fragment_shader = compileShader(source_fragment, GL_FRAGMENT_SHADER)
        self.shader_program = compileProgram(vertex_shader, fragment_shader)

        half_width = self.width / 2.0
        half_height = self.height / 2.0
        vertices = [
            [-half_width, -half_height, 0.0],
            [half_width, -half_height, 0.0],
            [half_width, half_height, 0.0],

            [-half_width, -half_height, 0.0],
            [half_width, half_height, 0.0],
            [-half_width, half_height, 0.0],
        ]

        color = [189/255, 0, 0]
        colors = [color] * 6

        vertices = np.array(vertices, dtype=np.float32)
        colors = np.array(colors, dtype=np.float32)

        # ----------------- vao ----------------- #
        self.VAO = glGenVertexArrays(1)
        glBindVertexArray(self.VAO)
        # --------------- position --------------- #
        vbo_position = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_position)
        glBufferData(GL_ARRAY_BUFFER, vertices.flatten(), GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0)) # position
        glEnableVertexAttribArray(0)
        # ---------------- color ---------------- #
        vbo_colors = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_colors)
        glBufferData(GL_ARRAY_BUFFER, colors.flatten(), GL_STATIC_DRAW)
        glVertexAttribPointer(1, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0)) # color
        glEnableVertexAttribArray(1)

        self.vertex_count = len(vertices)

    def draw_object(self, camera: Camera, vehicle_base: VehicleBase, side:str, show:bool) -> None:

        if self.shader_program == None:
            return

        if not show:
            return
        
        glUseProgram(self.shader_program)

        model = vehicle_base.model

        offset_north_south = 190
        offset_east_west = 170
        
        if side == "north":
            model = glm.translate(model, glm.vec3(0.0, 7.0, -offset_north_south))
        elif side == "south":
            model = glm.translate(model, glm.vec3(0.0, 7.0, offset_north_south))
        elif side == "east":
            model = glm.translate(model, glm.vec3(offset_east_west, 7.0, 0.0))
            model = glm.rotate(model, -glm.pi()/2, glm.vec3(0.0, 1.0, 0.0))
        elif side == "west":
            model = glm.translate(model, glm.vec3(-offset_east_west, 7.0, 0.0))
            model = glm.rotate(model, -glm.pi()/2, glm.vec3(0.0, 1.0, 0.0))

        view = glm.mat4(1.0)
        view = glm.lookAt(camera.position, camera.position + camera.front, camera.up)

        loc_model = glGetUniformLocation(self.shader_program, b"model")
        loc_view = glGetUniformLocation(self.shader_program, b"view")
        loc_projection = glGetUniformLocation(self.shader_program, b"projection")

        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(model))
        glUniformMatrix4fv(loc_view, 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(loc_projection, 1, GL_FALSE, glm.value_ptr(camera.projection))
        
        glBindVertexArray(self.VAO)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)


class PathTracer:
    def __init__(self):
        self.shader_program = None
        self.vertex_count = 0
        self.model = glm.mat4(1.0)
        self.path_points = []
        self.VBO_position = None

    def add_position(self, new_position):
        self.path_points.append(list(new_position))
        # if len(self.path_points) > 1000:
        #     self.path_points.pop(0)

    def init_object(self) -> None:

        source_vertex = """
        #version 330 core

        layout (location = 0) in vec3 v_pos;
 
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;

        void main() {
          gl_Position = projection * view * model * vec4(v_pos, 1.0f);
        }
        """

        source_fragment = """
        #version 330 core
        out vec4 FragColor;
        void main() {
          FragColor = vec4(58.0/255, 134.0/255.0, 183.0/255.0, 1.0f);
        }
        """

        # ------------------------------------------------------------
        # compilation
        # ------------------------------------------------------------

        vertex_shader = compileShader(source_vertex, GL_VERTEX_SHADER)
        fragment_shader = compileShader(source_fragment, GL_FRAGMENT_SHADER)
        self.shader_program = compileProgram(vertex_shader, fragment_shader)

        self.VAO = glGenVertexArrays(1)
        glBindVertexArray(self.VAO)

        self.VBO_position = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO_position)
        self.vertex_capacity = 1000
        glBufferData(GL_ARRAY_BUFFER, self.vertex_capacity * 3 * 4, None, GL_DYNAMIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

    def draw_object(self, camera: Camera) -> None:

        if self.shader_program == None:
            return

        glUseProgram(self.shader_program)

        vertex_count = len(self.path_points)
        if vertex_count > self.vertex_capacity:
            self.vertex_capacity = vertex_count * 2
            glBindBuffer(GL_ARRAY_BUFFER, self.VBO_position)
            glBufferData(GL_ARRAY_BUFFER, self.vertex_capacity * 3 * 4, None, GL_DYNAMIC_DRAW)
        flat_vertices = np.array(self.path_points, dtype=np.float32).flatten()
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO_position)
        glBufferSubData(GL_ARRAY_BUFFER, 0, flat_vertices.nbytes, flat_vertices)

        view = glm.lookAt(camera.position, camera.position + camera.front, camera.up)

        loc_model = glGetUniformLocation(self.shader_program, b"model")
        loc_view = glGetUniformLocation(self.shader_program, b"view")
        loc_projection = glGetUniformLocation(self.shader_program, b"projection")

        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(self.model))
        glUniformMatrix4fv(loc_view, 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(loc_projection, 1, GL_FALSE, glm.value_ptr(camera.projection))
        
        glBindVertexArray(self.VAO)
        glPointSize(10)
        glLineWidth(4)
        glDrawArrays(GL_LINE_STRIP, 0, len(self.path_points))

class PanelView(glcanvas.GLCanvas):
    def __init__(self, parent):

        dispAttrs = glcanvas.GLAttributes()
        dispAttrs.PlatformDefaults().Depth(16).DoubleBuffer().SampleBuffers(4).Samplers(4).EndList()

        super().__init__(parent, dispAttrs, size=wx.Size(300, 300))

        self.context = None
        self.timer = wx.Timer()
        self.init = False

        self.camera = Camera()
        self.pressed_keys = []

        self.light_directional = {
            "direction": [0, -1, 0.4],
            "ambient": [1.0, 1.0, 1.0],
            "diffuse": [1.0, 1.0, 1.0],
            "specular": [0.4, 0.4, 0.4]
        }

        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnPrimaryDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnPrimaryUp)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.timer.Bind(wx.EVT_TIMER, self.OnTimer)

        self.timer.Start(16)

        self.frame_count = 0
        self.start_time = time.time()
        self.fps = 0
        self.delta_time = 0.0

    def InitGL(self):
        if self.context is None:
            self.context = glcanvas.GLContext(self)
        self.SetCurrent(self.context)
        if not self.init:
            glClearColor(0.0, 0.0, 0.3, 1.0)
            # glClearColor(0.8, 0.8, 0.8, 1.0)
            glClearDepth(1.0)
            glEnable(GL_DEPTH_TEST)
            glDepthMask(GL_TRUE)
            glDepthFunc(GL_LEQUAL)
            glDepthRange(0.0, 1.0)
            glEnable(GL_MULTISAMPLE)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            self.vehicle_base = VehicleBase()
            self.vehicle_base.init_object()

            self.path_tracer = PathTracer()
            self.path_tracer.init_object()

            self.warning_panel_north = WarningPanel()
            self.warning_panel_north.init_object()

            self.warning_panel_south = WarningPanel()
            self.warning_panel_south.init_object()

            self.warning_panel_east = WarningPanel(width=200)
            self.warning_panel_east.init_object()

            self.warning_panel_west = WarningPanel(width=200)
            self.warning_panel_west.init_object()
            
            self.init = True

    def OnEraseBackground(self, event):
        pass

    def OnSize(self, event):
        size = self.GetClientSize()
        if self.context:
            self.SetCurrent(self.context)
            glViewport(0, 0, size.width, size.height)
            self.camera.projection = glm.perspective(glm.radians(self.camera.fov), size.width / size.height, 0.1, 500)
        event.Skip()

    def OnKeyDown(self, event):
        keycode = event.GetKeyCode()
        if keycode not in self.pressed_keys:
            self.pressed_keys.append(keycode)
        event.Skip()

    def OnKeyUp(self, event):
        keycode = event.GetKeyCode()
        if keycode in self.pressed_keys:
            self.pressed_keys.remove(keycode)

    def OnPrimaryDown(self, event):
        self.CaptureMouse()
        self.SetCursor(wx.Cursor(wx.CURSOR_CROSS))
        self.x, self.y = self.lastx, self.lasty = event.GetPosition()

    def OnPrimaryUp(self, event):
        if self.HasCapture():
            self.ReleaseMouse()
            self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

    def OnMotion(self, event):
        if event.Dragging() and event.LeftIsDown():
            self.lastx, self.lasty = self.x, self.y
            self.x, self.y = event.GetPosition()

            xoffset = self.x - self.lastx
            yoffset = self.y - self.lasty
            
            sensitivity = 0.4
            xoffset *= sensitivity
            yoffset *= sensitivity

            self.camera.yaw += xoffset
            self.camera.pitch -= yoffset

            self.camera.pitch = 89 if self.camera.pitch > 89 else self.camera.pitch
            self.camera.pitch = -89 if self.camera.pitch < -89 else self.camera.pitch

    def OnPaint(self, event):
        
        self.InitGL()

        glClear(GL_COLOR_BUFFER_BIT)
        glClear(GL_DEPTH_BUFFER_BIT)

        self.process_input()

        self.path_tracer.add_position(self.vehicle_base.get_position())

        self.vehicle_base.draw_object(self.camera, self.light_directional)
        self.path_tracer.draw_object(self.camera)
        self.warning_panel_north.draw_object(self.camera, self.vehicle_base, "north", True)
        self.warning_panel_south.draw_object(self.camera, self.vehicle_base, "south", True)
        self.warning_panel_east.draw_object(self.camera, self.vehicle_base, "east", True)
        self.warning_panel_west.draw_object(self.camera, self.vehicle_base, "west", True)

        self.SwapBuffers()
        event.Skip()

    def process_input(self):
        amount_movement = 300 * self.delta_time
        right = glm.cross(self.camera.front, self.camera.up)
        right = glm.normalize(right)
        for keycode in self.pressed_keys:
            if keycode == wx.WXK_UP or chr(keycode).lower() == 'w':
                self.camera.position += self.camera.front * amount_movement
            if keycode == wx.WXK_DOWN or chr(keycode).lower() == 's':
                self.camera.position -= self.camera.front * amount_movement
            if keycode == wx.WXK_RIGHT or chr(keycode).lower() == 'd':
                self.camera.position += right * amount_movement
            if keycode == wx.WXK_LEFT or chr(keycode).lower() == 'a':
                self.camera.position -= right * amount_movement
            if keycode == wx.WXK_SPACE:
                self.camera.position += self.camera.up * amount_movement
            if keycode == wx.WXK_SHIFT:
                self.camera.position -= self.camera.up * amount_movement

        front = glm.vec3()
        front.x = cos(glm.radians(self.camera.yaw)) * cos(glm.radians(self.camera.pitch))
        front.y = sin(glm.radians(self.camera.pitch))
        front.z = sin(glm.radians(self.camera.yaw)) * cos(glm.radians(self.camera.pitch))
        self.camera.front = glm.normalize(front)
        
    def OnTimer(self, event:wx.TimerEvent):
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        self.delta_time = elapsed_time
        self.start_time = current_time
        self.vehicle_base.model = glm.translate(self.vehicle_base.model,
                                                glm.vec3(uniform(-5, 2),
                                                         uniform(-0.5, 0.5),
                                                         uniform(-2, 5)))
        self.vehicle_base.model = glm.rotate(self.vehicle_base.model, 0.01, glm.vec3(0.0, 1.0, 0.0))
        self.Refresh(False)
        event.Skip()
