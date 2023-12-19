'''
    João Antônio Misson Milhorim - 11834331
    Reynaldo Coronatto Neto - 12547594
'''

import glfw
import math
import random
import numpy as np

from time import time
from PIL import Image
from numpy.lib.function_base import angle
from OpenGL.GL import *
from Model import Model
from Objects import objects
from GLWrapper import GLWrapper

def read_objects():
    ''' Lê todos os objetos do arquivo Objects.py '''
    models = []
    normals = []
    vertices = []
    textures = []
    normals_list = []
    vertices_list = []
    textures_coord_list = []
    start_index = 0
    
    # percorre lista de objetos, parseando-os como Model
    for name, obj in objects.items():
        new_model = Model(name, obj['filename'], obj['textures_path'], start_index, obj['r'], obj['t'], obj['s'], obj['theta'], obj['k'], obj['ns'])
        start_index += new_model.num_parts
        
        models.append(new_model)
        vertices_list.extend(new_model.vertices_list)
        textures_coord_list.extend(new_model.textures_coord_list)
        normals_list.extend(new_model.normals_list)
    
    # trata possível erro de falta de objetos
    if not models:
        exit(1)

    vertices = np.zeros(len(vertices_list), [("position", np.float32, 3)])
    textures = np.zeros(len(textures_coord_list), [("position", np.float32, 2)])
    normals = np.zeros(len(normals_list), [("position", np.float32, 3)])

    vertices['position'] = vertices_list
    textures['position'] = textures_coord_list
    normals['position'] = normals_list

    return models, vertices, textures, normals

def add_objs(models, g):
    ''' Carrega os objetos para a cena '''
    start = 0

    # adiciona objeto por objeto
    for model in models:
        ka = model.ka + g.ka
        ka = min(1.0, max(0.0, ka))

        model_matrix = model.get_model_matrix()
        loc_model = glGetUniformLocation(g.program, "model")
        glUniformMatrix4fv(loc_model, 1, GL_TRUE, model_matrix)

        # adiciona parâmetros de luz
        loc_ka = glGetUniformLocation(g.program, "ka") 
        glUniform1f(loc_ka, ka) 
        
        loc_kd = glGetUniformLocation(g.program, "kd") 
        glUniform1f(loc_kd, model.kd)
        
        loc_ks = glGetUniformLocation(g.program, "ks") 
        glUniform1f(loc_ks, model.ks)
        
        loc_ns = glGetUniformLocation(g.program, "ns")
        glUniform1f(loc_ns, model.ns)

        # adiciona os dois modelos de luz
        if 'light' in model.name:
            loc_light_pos = glGetUniformLocation(g.program, "lightPos")
            glUniform3f(loc_light_pos, model.tx, model.ty, model.tz)
        
        # insere cada parte com sua respectiva textura
        for part in model.parts:
            glBindTexture(GL_TEXTURE_2D, part['id'])
            glDrawArrays(GL_QUADS, start, part['size'])
            start += part['size']

    mat_view = g.view()
    loc_view = glGetUniformLocation(g.program, "view")
    glUniformMatrix4fv(loc_view, 1, GL_FALSE, mat_view)

    mat_projection = g.projection()
    loc_projection = glGetUniformLocation(g.program, "projection")
    glUniformMatrix4fv(loc_projection, 1, GL_FALSE, mat_projection)

    loc_view_pos = glGetUniformLocation(g.program, "viewPos")
    glUniform3f(loc_view_pos, g.camera_pos[0], g.camera_pos[1], g.camera_pos[2])

if __name__ == '__main__':
    g = GLWrapper(title='Trabalho 2 - CG', textures_amount=100)

    models, vertices, textures, normals = read_objects()

    # carrega imagens, texturas e normals
    g.load_images(vertices)
    g.load_textures(textures)
    g.load_normals(normals)

    # mostra cena e objetos
    glfw.show_window(g.window)
    glfw.set_cursor_pos(g.window, g.last_x, g.last_y)
    glEnable(GL_DEPTH_TEST)

    while not glfw.window_should_close(g.window):
        glfw.poll_events()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(1.0, 1.0, 1.0, 1.0)

        if g.polygonal_mode:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
        add_objs(models, g)
        glfw.swap_buffers(g.window)

    glfw.terminate()