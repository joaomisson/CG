import os
import glm
import random
import numpy as np

from PIL import Image
from OpenGL.GL import *

class Model:
    def __init__(self, name, model_filename, path, start_figure_id, r, t, s, theta, k, ns):
        self.name = name
        self.theta = np.radians(theta)
        self.rx, self.ry, self.rz = r[0], r[1], r[2]
        self.tx, self.ty, self.tz = t[0], t[1], t[2]
        self.sx, self.sy, self.sz = s[0], s[1], s[2]
        self.ka, self.kd, self.ks = k['a'], k['d'], k['s']
        self.ns = ns
        self.start_figure_id = start_figure_id
        self.parts = []
        self.height = random.uniform(25, 35)
        self.speed = random.uniform(1, 5)

        self.model = self.load_model_from_file(model_filename)
        self.texture = self.load_textures(path, start_figure_id)
        self.vertices_list, self.textures_coord_list, self.normals_list = self.parse_faces()
        self.model_matrix = self.get_model_matrix()
        self.size = len(self.vertices_list)

    def get_model_matrix(self):
        ''' Retorna matriz modelo para o objeto '''
        matrix_transform = glm.mat4(1.0)
        matrix_transform = glm.translate(matrix_transform, glm.vec3(self.tx, self.ty, self.tz))    
        matrix_transform = glm.rotate(matrix_transform, self.theta, glm.vec3(self.rx, self.ry, self.rz))    
        matrix_transform = glm.scale(matrix_transform, glm.vec3(self.sx, self.sy, self.sz))    
        matrix_transform = np.array(matrix_transform).T
        return matrix_transform
    
    def parse_faces(self):
        ''' Faz parsing dos objs, checando as texturas por face '''
        normals_list = []
        vertices_list = []
        textures_coord_list = []
        last_texture = None
        last_start = 0

        for face in self.model['faces']:
            if face[3] != last_texture:     # checa se deve mudar textura
                curr_start = len(vertices_list)
                
                if curr_start != 0:
                    info = {}
                    info['size'] = curr_start - last_start
                    info['id'] = len(self.parts) + self.start_figure_id

                    self.parts.append(info)
                
                last_texture = face[3]
                last_start = curr_start
                
            for vertice_id in face[0]:
                vertices_list.append(self.model['vertices'][vertice_id-1])

            for texture_id in face[1]:
                if len(self.model['texture']) == 0: continue
                textures_coord_list.append(self.model['texture'][texture_id-1])
    
            for normal_id in face[2]:
                normals_list.append(self.model['normals'][normal_id-1])

        curr_start = len(vertices_list)
        if last_start != curr_start:
            info = {}
            info['size'] = curr_start - last_start
            info['id'] = len(self.parts) + self.start_figure_id

            self.parts.append(info)

        self.num_parts = len(self.parts)
        return vertices_list, textures_coord_list, normals_list
    
    def load_model_from_file(self, filename):
        ''' Carrega arquivo OBJ '''
        vertices = []
        normals = []
        texture_coords = []
        faces = []

        material = None

        for line in open(filename, "r"): 
            if line.startswith('#'): continue 
            values = line.split() 
            if not values: continue

            if values[0] == 'v':
                vertices.append(values[1:4])

            if values[0] == 'vn':
                normals.append(values[1:4])

            elif values[0] == 'vt':
                texture_coords.append(values[1:3])

            elif values[0] in ('usemtl', 'usemat'):
                material = values[1]
            elif values[0] == 'f':
                face = []
                face_texture = []
                face_normals = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    face_normals.append(int(w[2]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        face_texture.append(int(w[1]))
                    else:
                        face_texture.append(0)

                faces.append((face, face_texture, face_normals, material))

        model = {}
        model['vertices'] = vertices
        model['texture'] = texture_coords
        model['faces'] = faces
        model['normals'] = normals

        return model
    
    def load_texture_from_file(self, filename, figure_id):
        ''' Carrefa um arquivo de texturas '''
        glBindTexture(GL_TEXTURE_2D, figure_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        img = Image.open(filename)
        img_width = img.size[0]
        img_height = img.size[1]
        image_data = img.convert("RGBA").tobytes("raw", "RGBA", 0, -1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img_width, img_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        
    def load_textures(self, path, start_id):
        ''' Carrefa todos os arquivos de texturas de uma pasta '''
        files = os.listdir(path)
        total_files = len(files)

        for idx, file in enumerate(sorted(files), 1):
            self.load_texture_from_file(path+file, start_id)
            start_id += 1