# utils.py

import wx
import numpy as np

def dip(*args):
    if len(args) == 1:
        return wx.ScreenDC().FromDIP(wx.Size(args[0], args[0]))[0]
    elif len(args) == 2:
        return wx.ScreenDC().FromDIP(wx.Size(args[0], args[1]))
    
class ReadOBJ:
    def __init__(self, filename, color=[1, 1, 1]):
        positions = []
        vertices = []
        faces = []
        normals_loaded = []
        uvs = []

        with open(filename) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                line_elements = line.split(' ')

                if line_elements[0] == "v":
                    vertices.append([float(line_elements[1]), float(line_elements[2]), float(line_elements[3])])
                elif line_elements[0] == "f":
                    face = []
                    for i in range(1, len(line_elements)):
                        vertex_data = line_elements[i].split('/')
                        face.append([int(v)-1 if v else None for v in vertex_data])
                    faces.append(face)
                elif line_elements[0] == "vn":
                    normals_loaded.append([float(line_elements[1]), float(line_elements[2]), float(line_elements[3])])
                elif line_elements[0] == "vt":
                    uvs.append([float(line_elements[1]), float(line_elements[2])])

        positions_new = []
        normals_new = []
        uvs_new = []

        for face in faces:
            v1_index = face[0][0]
            v2_index = face[1][0]
            v3_index = face[2][0]

            vertex1 = np.array(vertices[v1_index])
            vertex2 = np.array(vertices[v2_index])
            vertex3 = np.array(vertices[v3_index])

            edge1 = vertex2 - vertex1
            edge2 = vertex3 - vertex1
            face_normal = np.cross(edge1, edge2)
            face_normal = face_normal / np.linalg.norm(face_normal) if np.linalg.norm(face_normal) > 0 else np.array([0.0, 1.0, 0.0])

            for vert in face:
                positions_new.append(vertices[vert[0]])

                if len(vert) > 1 and vert[1] is not None:
                    uvs_new.append(uvs[vert[1]])
                else:
                    uvs_new.append([0.0, 0.0])

                if len(vert) > 2 and vert[2] is not None and normals_loaded:
                    normals_new.append(normals_loaded[vert[2]])
                else:
                    normals_new.append(face_normal.tolist())

        colors = [color for _ in range(len(positions_new))]

        self.vertices = np.array(positions_new, dtype=np.float32)
        self.colors = np.array(colors, np.float32)
        self.normals = np.array(normals_new, dtype=np.float32)
        self.uvs = np.array(uvs_new, dtype=np.float32)

def read_obj(filename, color=[1, 1, 1]):
    positions = []
    vertices = []
    faces = []
    normals_loaded = []
    uvs = []

    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            line_elements = line.split(' ')

            if line_elements[0] == "v":
                vertices.append([float(line_elements[1]), float(line_elements[2]), float(line_elements[3])])
            elif line_elements[0] == "f":
                face = []
                for i in range(1, len(line_elements)):
                    vertex_data = line_elements[i].split('/')
                    face.append([int(v)-1 if v else None for v in vertex_data])
                faces.append(face)
            elif line_elements[0] == "vn":
                normals_loaded.append([float(line_elements[1]), float(line_elements[2]), float(line_elements[3])])
            elif line_elements[0] == "vt":
                uvs.append([float(line_elements[1]), float(line_elements[2])])

    positions_new = []
    normals_new = []
    uvs_new = []

    for face in faces:
        v1_index = face[0][0]
        v2_index = face[1][0]
        v3_index = face[2][0]

        vertex1 = np.array(vertices[v1_index])
        vertex2 = np.array(vertices[v2_index])
        vertex3 = np.array(vertices[v3_index])

        edge1 = vertex2 - vertex1
        edge2 = vertex3 - vertex1
        face_normal = np.cross(edge1, edge2)
        face_normal = face_normal / np.linalg.norm(face_normal) if np.linalg.norm(face_normal) > 0 else np.array([0.0, 1.0, 0.0])

        for vert in face:
            positions_new.append(vertices[vert[0]])

            if len(vert) > 1 and vert[1] is not None:
                uvs_new.append(uvs[vert[1]])
            else:
                uvs_new.append([0.0, 0.0])

            if len(vert) > 2 and vert[2] is not None and normals_loaded:
                normals_new.append(normals_loaded[vert[2]])
            else:
                normals_new.append(face_normal.tolist())

    colors = [color for _ in range(len(positions_new))]

    return np.array(positions_new, dtype=np.float32), np.array(colors, dtype=np.float32), np.array(normals_new, dtype=np.float32), np.array(uvs_new, dtype=np.float32)

# def read_obj(filename, color=[1, 1, 1]):
#         positions = []
#         vertices = []
#         faces = []
#         normals = []
#         uvs = []
#         with open(filename) as f:
#             for line in f:
#                 line = line.strip()
#                 if not line or line.startswith('#'):
#                     continue
#                 line_elements = line.split(' ')
#                 # check if vertex
#                 if (line_elements[0] == "v"):
#                     vertices.append([float(line_elements[1]), float(line_elements[2]), float(line_elements[3])])
#                 # check if face
#                 elif (line_elements[0] == "f"):
#                     face = []
#                     # get data for each vertex in the face
#                     for i in range(1, len(line_elements)):
#                         # split vertex position/uv/normal data
#                         vertex_data = line_elements[i].split('/')
#                         face.append([int(v)-1 if v else None for v in vertex_data])
#                     faces.append(face)
#                 # vertex normal
#                 elif (line_elements[0] == "vn"):
#                     normals.append([float(line_elements[1]), float(line_elements[2]), float(line_elements[3])])
#                 # textures
#                 elif (line_elements[0] == "vt"):
#                     uvs.append([float(line_elements[1]), float(line_elements[2])])

#         positions = []
#         normals_new = []
#         uvs_new = []
        
#         for face in faces:
#             for vert in face:
#                 positions.append(vertices[vert[0]])

#                 if len(vert) > 1 and vert[1] is not None:
#                     uvs_new.append(uvs[vert[1]])
#                 else:
#                     uvs_new.append([0.0, 0.0])
                    
#                 if len(vert) > 2 and vert[2] is not None:
#                     normals_new.append(normals[vert[2]])
#                 else:
#                     normals_new.append([0.0, 1.0, 0.0]) 

#         colors = [color for _ in range(len(positions))]

#         return np.array(positions, dtype=np.float32), np.array(colors, dtype=np.float32), np.array(normals_new, dtype=np.float32), np.array(uvs_new, dtype=np.float32)
