import glm
import math
import glfw
import numpy as np

from PIL import Image
from OpenGL.GL import *

class GLWrapper:
    ''' Classe que faz o setup do OpenGL e permite a visualização de imagens '''
        
    def __init__(self, height=1000, width=1000, title='', textures_amount=None):
        ''' Construtor responsável por chamar funções que configuram o OpenGL '''
        self.textures_amount = textures_amount
        self.camera_pos = glm.vec3(-10.0,  -10.0,  -10.0)
        self.camera_front = glm.vec3(0.0,  0.0, 1.0)
        self.camera_up = glm.vec3(0.0,  1.0,  0.0)
        self.polygonal_mode = False
        self.height, self.width = height, width
        self.last_x, self.last_y = height/2, width/2
        self.first_mouse = True
        self.yaw = -90.0
        self.pitch = 0.0
        self.projection_angle = 65.0
        self.near = 0.1
        self.far = 100.0
        self.ka = 0.0
        
        self.set_keys()
        self.window = self.init_window(height, width, title)
        self.add_events(self.window)
        self.program, self.vertex, self.fragment = self.set_shaders()
        self.compile_shaders(self.vertex, 'vertex')
        self.compile_shaders(self.fragment, 'fragment')
        self.attach_shaders(self.program, self.vertex, self.fragment)
        self.link_program(self.program)
        self.loc_color, self.buffer = self.finish_setup(self.program, self.window)

    def set_keys(self):
        ''' Define variáveis de teclado e mouse'''
        self.KEY_ARROW_DOWN = 264
        self.KEY_ARROW_UP = 265
        self.KEY_A = 65
        self.KEY_S = 83
        self.KEY_D = 68
        self.KEY_W = 87
        self.KEY_P = 80
        self.KEY_U = 85
        self.KEY_I = 73
        self.MOUSE_LEFT = 0
        self.MOUSE_RIGHT = 1
    
    def init_window(self, height, width, title):
        ''' Inicializa janela '''
        glfw.init()
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        window = glfw.create_window(height, width, title, None, None)
        glfw.make_context_current(window)
        return window
        
    def key_event(self, window, key, scancode, action, mods):
        ''' Callback para cliques no teclado '''
        if action == 0:
            return
        
        camera_speed = 0.2
        if key == self.KEY_W: # W para aproximar a camera
            self.camera_pos += camera_speed * self.camera_front

        elif key == self.KEY_S: # S para afastar a camera
            self.camera_pos -= camera_speed * self.camera_front

        elif key == self.KEY_A: # A para mover para a esquerda da camera
            self.camera_pos -= glm.normalize(glm.cross(self.camera_front, self.camera_up)) * camera_speed
        
        elif key == self.KEY_D: # D para mover para a direita da camera
            self.camera_pos += glm.normalize(glm.cross(self.camera_front, self.camera_up)) * camera_speed

        elif key == self.KEY_ARROW_UP: # seta para cima para subir a camera
            self.camera_pos += glm.normalize(self.camera_up) * camera_speed * 2

        elif key == self.KEY_ARROW_DOWN: # seta para cima para descer a camera
            self.camera_pos -= glm.normalize(self.camera_up) * camera_speed * 2
            
        elif key == self.KEY_I and action != 2: # P para alternar modo de visualização
            self.polygonal_mode = not self.polygonal_mode
        
        elif key == self.KEY_U: # U para aumentar o ka
            self.ka -= 0.01
        
        elif key == self.KEY_P: # I para diminuir o ka
            self.ka += 0.01
        
        # define limites para as variáveis
        self.camera_pos[0] = max(-18.0, self.camera_pos[0])
        self.camera_pos[1] = max(-13.0, self.camera_pos[1])
        self.camera_pos[2] = max(-18.0, self.camera_pos[2])

        self.camera_pos[0] = min(18.0, self.camera_pos[0])
        self.camera_pos[1] = min(13.0, self.camera_pos[1])
        self.camera_pos[2] = min(18.0, self.camera_pos[2])

        self.projection_angle = max(0.1, self.projection_angle)
        self.projection_angle = min(90.0, self.projection_angle)

        self.near = max(0.1, self.near)
        self.near = min(50.0, self.near)

        self.far = max(-20.0, self.far)
        self.far = min(100.0, self.far)

        self.ka = max(-0.5, self.ka)
        self.ka = min(1.5, self.ka)

    def mouse_event(self, window, xpos, ypos):
        ''' Callback para apontar camera com o mouse '''
        if self.first_mouse:
            self.last_x = xpos
            self.last_y = ypos
            self.first_mouse = False

        xoffset = xpos - self.last_x
        yoffset = self.last_y - ypos
        self.last_x = xpos
        self.last_y = ypos

        sensitivity = 0.3 
        xoffset *= sensitivity
        yoffset *= sensitivity

        self.yaw += xoffset
        self.pitch += yoffset

        
        if self.pitch >= 90.0: self.pitch = 90.0
        if self.pitch <= -90.0: self.pitch = -90.0

        front = glm.vec3()
        front.x = math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        front.y = math.sin(glm.radians(self.pitch))
        front.z = math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        self.camera_front = glm.normalize(front)
    
    def add_events(self, window):
        ''' Adiciona callbacks dos eventos '''
        glfw.set_key_callback(window, self.key_event)
        glfw.set_cursor_pos_callback(window, self.mouse_event)
    
    def set_shaders(self):
        ''' Adiciona shaders '''
        vertex_code = """
                attribute vec3 position;
                attribute vec2 texture_coord;
                attribute vec3 normals;
                
            
                varying vec2 out_texture;
                varying vec3 out_fragPos;
                varying vec3 out_normal;
                        
                uniform mat4 model;
                uniform mat4 view;
                uniform mat4 projection;        
                
                void main(){
                    gl_Position = projection * view * model * vec4(position,1.0);
                    out_texture = vec2(texture_coord);
                    out_fragPos = vec3(model * vec4(position, 1.0));
                    out_normal = normals;            
                }
        """

        fragment_code = """
                // parametros da iluminacao ambiente e difusa
                uniform vec3 lightPos1; // define coordenadas de posicao da luz #1
                uniform vec3 lightPos2; // define coordenadas de posicao da luz #2
                uniform float ka; // coeficiente de reflexao ambiente
                uniform float kd; // coeficiente de reflexao difusa
                
                // parametros da iluminacao especular
                uniform vec3 viewPos; // define coordenadas com a posicao da camera/observador
                uniform float ks; // coeficiente de reflexao especular
                uniform float ns; // expoente de reflexao especular
                
                // parametro com a cor da(s) fonte(s) de iluminacao
                vec3 lightColor = vec3(1.0, 1.0, 1.0);

                // parametros recebidos do vertex shader
                varying vec2 out_texture; // recebido do vertex shader
                varying vec3 out_normal; // recebido do vertex shader
                varying vec3 out_fragPos; // recebido do vertex shader
                uniform sampler2D samplerTexture;
                
                void main(){
                    // calculando reflexao ambiente
                    vec3 ambient = ka * lightColor;             
                
                    // Luz #1
                    // calculando reflexao difusa
                    vec3 norm1 = normalize(out_normal); // normaliza vetores perpendiculares
                    vec3 lightDir1 = normalize(lightPos1 - out_fragPos); // direcao da luz
                    float diff1 = max(dot(norm1, lightDir1), 0.0); // verifica limite angular (entre 0 e 90)
                    vec3 diffuse1 = kd * diff1 * lightColor; // iluminacao difusa
                    
                    // calculando reflexao especular
                    vec3 viewDir1 = normalize(viewPos - out_fragPos); // direcao do observador/camera
                    vec3 reflectDir1 = reflect(-lightDir1, norm1); // direcao da reflexao
                    float spec1 = pow(max(dot(viewDir1, reflectDir1), 0.0), ns);
                    vec3 specular1 = ks * spec1 * lightColor;    
                    
                    // Luz #2
                    // calculando reflexao difusa
                    vec3 norm2 = normalize(out_normal); // normaliza vetores perpendiculares
                    vec3 lightDir2 = normalize(lightPos2 - out_fragPos); // direcao da luz
                    float diff2 = max(dot(norm2, lightDir2), 0.0); // verifica limite angular (entre 0 e 90)
                    vec3 diffuse2 = kd * diff2 * lightColor; // iluminacao difusa
                    
                    // calculando reflexao especular
                    vec3 viewDir2 = normalize(viewPos - out_fragPos); // direcao do observador/camera
                    vec3 reflectDir2 = reflect(-lightDir2, norm2); // direcao da reflexao
                    float spec2 = pow(max(dot(viewDir2, reflectDir2), 0.0), ns);
                    vec3 specular2 = ks * spec2 * lightColor;    

                    // Combinando as duas fontes
                    // aplicando o modelo de iluminacao
                    vec4 texture = texture2D(samplerTexture, out_texture);
                    vec4 result = vec4((ambient + diffuse1 + diffuse2 + specular1 + specular2),1.0) * texture; // aplica iluminacao
                    gl_FragColor = result;

                }
        """

        program  = glCreateProgram()
        vertex   = glCreateShader(GL_VERTEX_SHADER)
        fragment = glCreateShader(GL_FRAGMENT_SHADER)
        
        glShaderSource(vertex, vertex_code)
        glShaderSource(fragment, fragment_code)
        
        return program, vertex, fragment

    def compile_shaders(self, shader, name):
        ''' Compila shaders '''
        glCompileShader(shader)
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(shader).decode()
            print(error)
            raise RuntimeError(f"Erro de compilacao do {name} Shader")
            
    def attach_shaders(self, program, vertex, fragment):
        ''' Associa shaders '''
        glAttachShader(program, vertex)
        glAttachShader(program, fragment)
        
    def link_program(self, program):
        ''' Faz o link do programa '''
        glLinkProgram(program)
        if not glGetProgramiv(program, GL_LINK_STATUS):
            print(glGetProgramInfoLog(program))
            raise RuntimeError('Linking error')

        glUseProgram(program)
    
    def finish_setup(self, program, window):
        ''' Ultimas configurações '''
        loc_color = glGetUniformLocation(program, "color")
        glGenTextures(self.textures_amount)
        glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_TEXTURE_2D)
        buffer = glGenBuffers(3)
        return loc_color, buffer
    
    def load(self, vertices, obj_type):
        ''' Gera um buffer e insere dados vertices na janela, utiliza matriz
            de transformação, caso seja informada '''
        if obj_type == "texture_coord":
            dimensions = 2
            pos = 1
        elif obj_type == "normals":
            dimensions = 3
            pos = 2
        else:
            dimensions = 3
            pos = 0
        
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer[pos])
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        stride = vertices.strides[0]
        offset = ctypes.c_void_p(0)
    
        loc = glGetAttribLocation(self.program, obj_type)
        glEnableVertexAttribArray(loc)

        glVertexAttribPointer(loc, dimensions, GL_FLOAT, False, stride, offset)
            
    def load_images(self, vertices):
        ''' Carrega imagens para a cena '''
        self.load(vertices, 'position')

    def load_normals(self, vertices):
        ''' Carrega normals para a cena '''
        self.load(vertices, 'normals')

    def load_textures(self, vertices):
        ''' Carrega texturas para a cena '''
        self.load(vertices, 'texture_coord')
        
    def view(self):
        ''' Carrega matriz view '''
        mat_view = glm.lookAt(self.camera_pos, self.camera_pos + self.camera_front, self.camera_up)
        mat_view = np.array(mat_view)
        return mat_view
    
    def projection(self):
        ''' Carrega matriz projection '''
        mat_projection = glm.perspective(glm.radians(self.projection_angle), self.height/self.width, self.near, self.far)
        mat_projection = np.array(mat_projection)    
        return mat_projection