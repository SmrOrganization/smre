from OpenGL import GL as gl


class ShaderCompileError(Exception):
    pass


def _compile(source, shader_type):
    shader = gl.glCreateShader(shader_type)
    gl.glShaderSource(shader, source)
    gl.glCompileShader(shader)
    success = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
    if not success:
        info = gl.glGetShaderInfoLog(shader).decode("utf-8")
        gl.glDeleteShader(shader)
        raise ShaderCompileError(info)
    return shader


class Shader:
    def __init__(self, program_id):
        self.program_id = program_id
        self._uniform_cache = {}

    @classmethod
    def from_source(cls, vertex_source, fragment_source):
        vertex_shader = _compile(vertex_source, gl.GL_VERTEX_SHADER)
        fragment_shader = _compile(fragment_source, gl.GL_FRAGMENT_SHADER)

        program = gl.glCreateProgram()
        gl.glAttachShader(program, vertex_shader)
        gl.glAttachShader(program, fragment_shader)
        gl.glLinkProgram(program)

        success = gl.glGetProgramiv(program, gl.GL_LINK_STATUS)
        if not success:
            info = gl.glGetProgramInfoLog(program).decode("utf-8")
            gl.glDeleteProgram(program)
            raise ShaderCompileError(info)

        gl.glDeleteShader(vertex_shader)
        gl.glDeleteShader(fragment_shader)
        return cls(program)

    @classmethod
    def from_files(cls, vertex_path, fragment_path):
        with open(vertex_path, "r", encoding="utf-8") as file:
            vertex_source = file.read()
        with open(fragment_path, "r", encoding="utf-8") as file:
            fragment_source = file.read()
        return cls.from_source(vertex_source, fragment_source)

    def use(self):
        gl.glUseProgram(self.program_id)

    def _location(self, name):
        location = self._uniform_cache.get(name)
        if location is None:
            location = gl.glGetUniformLocation(self.program_id, name)
            self._uniform_cache[name] = location
        return location

    def set_int(self, name, value):
        gl.glUniform1i(self._location(name), value)

    def set_float(self, name, value):
        gl.glUniform1f(self._location(name), value)

    def set_vec2(self, name, x, y=None):
        if y is None:
            x, y = x.x, x.y
        gl.glUniform2f(self._location(name), x, y)

    def set_vec3(self, name, x, y=None, z=None):
        if y is None:
            x, y, z = x.x, x.y, x.z
        gl.glUniform3f(self._location(name), x, y, z)

    def set_vec4(self, name, x, y=None, z=None, w=None):
        if y is None:
            x, y, z, w = x.x, x.y, x.z, x.w
        gl.glUniform4f(self._location(name), x, y, z, w)

    def set_color(self, name, color):
        gl.glUniform4f(self._location(name), color.r, color.g, color.b, color.a)

    def set_mat4(self, name, matrix):
        gl.glUniformMatrix4fv(self._location(name), 1, gl.GL_TRUE, matrix.m)

    def delete(self):
        if self.program_id:
            gl.glDeleteProgram(self.program_id)
            self.program_id = None

    def __enter__(self):
        self.use()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
