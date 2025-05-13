# view.py

import wx
import glm
import ctypes
import wx.glcanvas as glcanvas
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
from math import sin, cos
from utils import read_obj, ReadOBJ
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
        self.near = 0.1
        self.far = 100000
        self.projection = glm.perspective(glm.radians(self.fov), 1, self.near, self.far)

class VehicleBase:
    def __init__(self):

        self.shader_program = None
        self.vertex_count = 0
        self.model = glm.mat4(1.0)

        self.material_data = {
            "shininess": 64.0,
            "ambient": [0.2, 0.2, 0.2],
            "diffuse": [0.3, 0.3, 0.3],
            "specular": [0.5, 0.5, 0.5]
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
          //FragColor = vec4(90/255.0,121/255.0,200/255.0, 1.0f); // 0.6 red only // 90/255.0, 121/255.0, 200/255.0
          FragColor = vec4(0.0f, 0.0f, 0.0f, 1.0f);
        }
        """

        vertex_shader_wire = compileShader(source_vertex, GL_VERTEX_SHADER)
        fragment_shader_wire = compileShader(source_fragment, GL_FRAGMENT_SHADER)
        self.shader_program_wire = compileProgram(vertex_shader_wire, fragment_shader_wire)

        vertices, colors, normals, uvs = read_obj("objects/rocky.obj", [1.0, 1.0, 1.0])

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

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        self.vertex_count = len(vertices)

    def get_position(self) -> glm.vec3:
        return glm.vec3(self.model[3][0],
                        self.model[3][1],
                        self.model[3][2])

    def draw_object(self, camera: Camera, light_directional: dict) -> None:

        if self.shader_program == None:
            return
        
        glBindVertexArray(self.VAO)

        view = glm.lookAt(camera.position, camera.position + camera.front, camera.up)

        # ----------- draw in wireframe ----------- #
        

        glUseProgram(self.shader_program_wire)
        loc_model = glGetUniformLocation(self.shader_program_wire, b"model")
        loc_view = glGetUniformLocation(self.shader_program_wire, b"view")
        loc_projection = glGetUniformLocation(self.shader_program_wire, b"projection")
        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(self.model))
        glUniformMatrix4fv(loc_view, 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(loc_projection, 1, GL_FALSE, glm.value_ptr(camera.projection))
        glLineWidth(2)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_FRONT)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

        # ----------- redraw as solid ----------- #

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
        glDisable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

class VehicleArm:
    def __init__(self):

        self.shader_program = None

        self.material_data = {
            "shininess": 64.0,
            "ambient": [0.2, 0.2, 0.2],
            "diffuse": [0.2, 0.2, 0.2],
            "specular": [0.5, 0.5, 0.5]
        }

    def init_object(self) -> None:

        # ------------------------------------------------------------
        # shaders
        # ------------------------------------------------------------
        
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
          //FragColor = vec4(90/255.0,121/255.0,200/255.0, 1.0f); // 0.6 red only // 90/255.0, 121/255.0, 200/255.0
          FragColor = vec4(0.4f, 0.4f, 0.4f, 1.0f);
        }
        """

        vertex_shader_wire = compileShader(source_vertex, GL_VERTEX_SHADER)
        fragment_shader_wire = compileShader(source_fragment, GL_FRAGMENT_SHADER)
        self.shader_program_wire = compileProgram(vertex_shader_wire, fragment_shader_wire)

        # ------------------------------------------------------------
        # read obj files
        # ------------------------------------------------------------

        p1 = ReadOBJ("objects/servo_support.obj")
        self.vao_p1 = self.setup_vao(p1)
        self.vertex_count_p1 = len(p1.vertices)

        p2 = ReadOBJ("objects/servo_motor.obj")
        self.vao_p2 = self.setup_vao(p2)
        self.vertex_count_p2 = len(p2.vertices)

        p3 = ReadOBJ("objects/servo_adapter.obj")
        self.vao_p3 = self.setup_vao(p3)
        self.vertex_count_p3 = len(p3.vertices)

        p4 = ReadOBJ("objects/servo_support.obj")
        self.vao_p4 = self.setup_vao(p4)
        self.vertex_count_p4 = len(p4.vertices)

        p5 = ReadOBJ("objects/servo_motor.obj")
        self.vao_p5 = self.setup_vao(p5)
        self.vertex_count_p5 = len(p5.vertices)

        p6 = ReadOBJ("objects/servo_adapter.obj")
        self.vao_p6 = self.setup_vao(p6)
        self.vertex_count_p6 = len(p6.vertices)

        p7 = ReadOBJ("objects/arm.obj")
        self.vao_p7 = self.setup_vao(p7)
        self.vertex_count_p7 = len(p7.vertices)

        p8 = ReadOBJ("objects/servo_adapter.obj")
        self.vao_p8 = self.setup_vao(p8)
        self.vertex_count_p8 = len(p8.vertices)

        p9 = ReadOBJ("objects/servo_motor.obj")
        self.vao_p9 = self.setup_vao(p9)
        self.vertex_count_p9 = len(p9.vertices)

        p10 = ReadOBJ("objects/servo_support.obj")
        self.vao_p10 = self.setup_vao(p10)
        self.vertex_count_p10 = len(p10.vertices)

        p11 = ReadOBJ("objects/arm_gripper_union.obj")
        self.vao_p11 = self.setup_vao(p11)
        self.vertex_count_p11 = len(p11.vertices)

    def setup_vao(self, obj_data: ReadOBJ):
        # ----------------- vao ----------------- #
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)
        # --------------- position --------------- #
        vbo_position = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_position)
        glBufferData(GL_ARRAY_BUFFER, obj_data.vertices.flatten(), GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0)) # position
        glEnableVertexAttribArray(0)
        # ---------------- color ---------------- #
        vbo_colors = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_colors)
        glBufferData(GL_ARRAY_BUFFER, obj_data.colors.flatten(), GL_STATIC_DRAW)
        glVertexAttribPointer(1, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0)) # color
        glEnableVertexAttribArray(1)
        # --------------- normals --------------- #
        vbo_normals = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_normals)
        glBufferData(GL_ARRAY_BUFFER, obj_data.normals.flatten(), GL_STATIC_DRAW)
        glVertexAttribPointer(2, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0)) # normal
        glEnableVertexAttribArray(2)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        self.vertex_count = len(obj_data.vertices)

        return vao
    
    def draw_vao(self, vao, vertex_count, model, camera: Camera, light_directional: dict, vehicle_base: VehicleBase):

        glBindVertexArray(vao)

        view = glm.lookAt(camera.position, camera.position + camera.front, camera.up)

        # ----------- draw in wireframe ----------- #
        
        glUseProgram(self.shader_program_wire)
        loc_model = glGetUniformLocation(self.shader_program_wire, b"model")
        loc_view = glGetUniformLocation(self.shader_program_wire, b"view")
        loc_projection = glGetUniformLocation(self.shader_program_wire, b"projection")
        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(model))
        glUniformMatrix4fv(loc_view, 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(loc_projection, 1, GL_FALSE, glm.value_ptr(camera.projection))
        glLineWidth(2)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_FRONT)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glDrawArrays(GL_TRIANGLES, 0, vertex_count)

        # ----------- redraw as solid ----------- #

        glUseProgram(self.shader_program)
        loc_model = glGetUniformLocation(self.shader_program, b"model")
        loc_view = glGetUniformLocation(self.shader_program, b"view")
        loc_projection = glGetUniformLocation(self.shader_program, b"projection")
        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(model))
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
        
        glDisable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glDrawArrays(GL_TRIANGLES, 0, vertex_count)

    def draw_object(self, camera: Camera, light_directional: dict, vehicle_base: VehicleBase) -> None:

        if self.shader_program == None:
            return
        
        # ----------- p1 ----------- # support
        model_p1 = vehicle_base.model
        model_p1 = glm.translate(model_p1, glm.vec3(0.0, 85.0, 80.0))
        model_p1 = glm.rotate(model_p1, glm.pi(), glm.vec3(1.0, 0.0, 0.0))
        model_p1 = glm.rotate(model_p1, glm.pi(), glm.vec3(0.0, 1.0, 0.0))
        self.draw_vao(self.vao_p1, self.vertex_count_p1, model_p1, camera, light_directional, vehicle_base)
        # ----------- p2 ----------- # motor
        model_p2 = model_p1
        model_p2 = glm.rotate(model_p2, glm.pi(), glm.vec3(1.0, 0.0, 0.0))
        model_p2 = glm.translate(model_p2, glm.vec3(10.3, 24, 11.4))
        self.draw_vao(self.vao_p2, self.vertex_count_p2, model_p2, camera, light_directional, vehicle_base)
        # ----------- p3 ----------- # adapter
        model_p3 = model_p2
        #model_p3 = glm.rotate(model_p3, sin(time.time()), glm.vec3(0.0, 1.0, 0.0))
        self.draw_vao(self.vao_p3, self.vertex_count_p3, model_p3, camera, light_directional, vehicle_base)
        # ----------- p4 ----------- # support
        model_p4 = model_p3
        model_p4 = glm.rotate(model_p4, glm.pi()/2, glm.vec3(1.0, 0.0, 0.0))
        model_p4 = glm.rotate(model_p4, -glm.pi()/2, glm.vec3(0.0, 0.0, 1.0))
        model_p4 = model_p4 * glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, -8.5))
        self.draw_vao(self.vao_p4, self.vertex_count_p4, model_p4, camera, light_directional, vehicle_base)
        # ----------- p5 ----------- # motor
        model_p5 = model_p4
        model_p5 = glm.rotate(model_p5, glm.pi(), glm.vec3(1.0, 0.0, 0.0))
        model_p5 = glm.translate(model_p5, glm.vec3(10.3, 24, 11.4))
        self.draw_vao(self.vao_p5, self.vertex_count_p5, model_p5, camera, light_directional, vehicle_base)
        # ----------- p6 ----------- # adapter
        model_p6 = model_p5
        #model_p6 = glm.rotate(model_p6, sin(time.time()), glm.vec3(0.0, 1.0, 0.0))
        self.draw_vao(self.vao_p6, self.vertex_count_p6, model_p6, camera, light_directional, vehicle_base)
        # ----------- p7 ----------- #
        model_p7 = model_p6
        model_p7 = glm.rotate(model_p7, glm.pi()/2, glm.vec3(1.0, 0.0, 0.0))
        model_p7 = glm.rotate(model_p7, glm.pi()/2, glm.vec3(0.0, 1.0, 0.0))
        model_p7 = glm.translate(model_p7, glm.vec3(-19.3, 0.0, 0.0))
        self.draw_vao(self.vao_p7, self.vertex_count_p7, model_p7, camera, light_directional, vehicle_base)
        # ----------- p8 ----------- # adapter
        model_p8 = model_p7
        model_p8 = glm.rotate(model_p8, glm.pi()/2, glm.vec3(0.0, 0.0, 1.0))
        model_p8 = glm.translate(model_p8, glm.vec3(180.0, 19.3, 0.0))
        self.draw_vao(self.vao_p8, self.vertex_count_p8, model_p8, camera, light_directional, vehicle_base)
        # ------------------ p9 ------------------ # motor
        model_p9 = model_p8
        model_p9 = glm.rotate(model_p9, glm.pi(), glm.vec3(0.0, 1.0, 0.0))
        self.draw_vao(self.vao_p9, self.vertex_count_p9, model_p9, camera, light_directional, vehicle_base)
        # ----------------- p10 ----------------- # support
        model_p10 = model_p9
        model_p10 = glm.rotate(model_p10, -glm.pi(), glm.vec3(0.0, 0.0, 1.0))
        model_p10 = glm.translate(model_p10, glm.vec3(10.3, 24, 11.4))
        self.draw_vao(self.vao_p10, self.vertex_count_p10, model_p10, camera, light_directional, vehicle_base)
        # ----------------- p10 ----------------- # arm gripper union
        model_p11 = model_p10
        model_p11 = glm.rotate(model_p11, -glm.pi()/2, glm.vec3(0.0, 0.0, 1.0))
        model_p11 = glm.translate(model_p11, glm.vec3(4.4, 10.0, 2.0))
        self.draw_vao(self.vao_p11, self.vertex_count_p11, model_p11, camera, light_directional, vehicle_base)
        
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
        self.max_points = 2000
        self.VBO_position = None

    def add_position(self, new_position):
        if len(self.path_points) > self.max_points - 1: # use queue
            self.path_points.pop(0)
        self.path_points.append(list(new_position))

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
          //FragColor = vec4(58.0/255, 134.0/255.0, 183.0/255.0, 0.7f);
          FragColor = vec4(0.0f, 0.0f, 0.2f, 0.6f);
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
        glBufferData(GL_ARRAY_BUFFER, self.max_points * 3 * 4, None, GL_DYNAMIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def draw_object(self, camera: Camera) -> None:

        if self.shader_program == None:
            return

        glUseProgram(self.shader_program)

        vertices = np.array(self.path_points, dtype=np.float32).flatten()
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO_position)
        glBufferSubData(GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)

        view = glm.lookAt(camera.position, camera.position + camera.front, camera.up)

        loc_model = glGetUniformLocation(self.shader_program, b"model")
        loc_view = glGetUniformLocation(self.shader_program, b"view")
        loc_projection = glGetUniformLocation(self.shader_program, b"projection")

        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(self.model))
        glUniformMatrix4fv(loc_view, 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(loc_projection, 1, GL_FALSE, glm.value_ptr(camera.projection))
        
        glBindVertexArray(self.VAO)
        glLineWidth(3)
        glDrawArrays(GL_LINE_STRIP, 0, len(self.path_points))

class SkySphere:
    def __init__(self):

        self.shader_program = None
        self.vertex_count = 0

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

        vertices, colors, normals, uvs = read_obj("objects/sphere.obj", [0.7, 0.7, 0.7])

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

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        self.vertex_count = len(vertices)

    def draw_object(self, camera: Camera, show:bool=True) -> None:

        if not show:
            return
        
        glUseProgram(self.shader_program)

        model = glm.mat4(1.0)
        # set position to be the same as camera
        model[3][0] = camera.position.x
        model[3][1] = camera.position.y
        model[3][2] = camera.position.z

        scale = 1000.0
        model = glm.scale(model, glm.vec3(scale, scale, scale))
        view = glm.mat4(1.0)
        view = glm.lookAt(camera.position, camera.position + camera.front, camera.up)

        loc_model = glGetUniformLocation(self.shader_program, b"model")
        loc_view = glGetUniformLocation(self.shader_program, b"view")
        loc_projection = glGetUniformLocation(self.shader_program, b"projection")

        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(model))
        glUniformMatrix4fv(loc_view, 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(loc_projection, 1, GL_FALSE, glm.value_ptr(camera.projection))
        
        glBindVertexArray(self.VAO)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glLineWidth(4)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

class PanelView(glcanvas.GLCanvas):
    def __init__(self, parent):

        dispAttrs = glcanvas.GLAttributes()
        dispAttrs.PlatformDefaults().Depth(16).DoubleBuffer().EndList() # SampleBuffers(4).Samplers(4)

        super().__init__(parent, dispAttrs, size=wx.Size(300, 300))

        self.context = None
        self.timer = wx.Timer()
        self.init = False

        self.camera = Camera()
        self.pressed_keys = []

        self.light_directional = {
            "direction": [0.0, -1, 0.0],
            "ambient": [0.2, 0.2, 0.2],
            "diffuse": [0.7, 0.7, 0.7],
            "specular": [1.0, 1.0, 1.0]
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

        self.timer.Start(5)

        self.start_time = time.time()
        self.delta_time = 0.0

    def InitGL(self):
        if self.context is None:
            self.context = glcanvas.GLContext(self)
        self.SetCurrent(self.context)
        if not self.init:
            glClearColor(0.8, 0.8, 0.8, 1.0)
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            #glClearDepth(1.0)
            #glDepthMask(GL_TRUE)
            #glDepthFunc(GL_LESS)
            #glDepthRange(0.0, 1.0)

            self.sky_sphere = SkySphere()
            self.sky_sphere.init_object()

            self.vehicle_base = VehicleBase()
            self.vehicle_base.init_object()

            self.vehicle_arm = VehicleArm()
            self.vehicle_arm.init_object()

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
            self.camera.projection = glm.perspective(glm.radians(self.camera.fov), size.width / size.height, self.camera.near, self.camera.far)
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
        event.Skip()

    def OnPrimaryDown(self, event):
        self.CaptureMouse()
        self.SetCursor(wx.Cursor(wx.CURSOR_CROSS))
        self.x, self.y = self.lastx, self.lasty = event.GetPosition()
        event.Skip()

    def OnPrimaryUp(self, event):
        if self.HasCapture():
            self.ReleaseMouse()
            self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        event.Skip()

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
        event.Skip()

    def OnPaint(self, event):
        
        self.InitGL()

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        self.process_input()

        self.path_tracer.add_position(self.vehicle_base.get_position())

        self.sky_sphere.draw_object(self.camera)
        self.vehicle_base.draw_object(self.camera, self.light_directional)
        self.vehicle_arm.draw_object(self.camera, self.light_directional, self.vehicle_base)
        self.path_tracer.draw_object(self.camera)
        show_warning_panels = False
        self.warning_panel_north.draw_object(self.camera, self.vehicle_base, "north", show_warning_panels)
        self.warning_panel_south.draw_object(self.camera, self.vehicle_base, "south", show_warning_panels)
        self.warning_panel_east.draw_object(self.camera, self.vehicle_base, "east", show_warning_panels)
        self.warning_panel_west.draw_object(self.camera, self.vehicle_base, "west", show_warning_panels)

        self.SwapBuffers()
        event.Skip()

    def process_input(self):
        amount_movement = 300 * self.delta_time
        right = glm.normalize(glm.cross(self.camera.front, self.camera.up))
        front = glm.normalize(glm.cross(right, self.camera.up))
        for keycode in self.pressed_keys:
            if keycode == wx.WXK_UP or chr(keycode).lower() == 'w':
                self.camera.position -= front * amount_movement
            if keycode == wx.WXK_DOWN or chr(keycode).lower() == 's':
                self.camera.position += front * amount_movement
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
        # self.vehicle_base.model = glm.translate(self.vehicle_base.model,
        #                                         glm.vec3(uniform(-5, 2),
        #                                                  uniform(-0.5, 0.5),
        #                                                  uniform(-2, 5)))
        # self.vehicle_base.model = glm.rotate(self.vehicle_base.model, 0.01, glm.vec3(0.0, 1.0, 0.0))
        # self.vehicle_base.model = glm.rotate(self.vehicle_base.model, 0.007, glm.vec3(0.5, 0.5, 0.5))
        self.Refresh(False)
        event.Skip()
