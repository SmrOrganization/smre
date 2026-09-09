from OpenGL import GL as gl

from ..mathlib import Vec3
from .color import WHITE
from .shader import Shader
from .texture import Texture2D

_VERTEX_SHADER = """
#version 330 core
layout(location = 0) in vec3 a_position;
layout(location = 1) in vec3 a_normal;
layout(location = 2) in vec2 a_uv;

uniform mat4 u_model;
uniform mat4 u_view_projection;
uniform mat3 u_normal_matrix;

out vec3 v_normal;
out vec2 v_uv;

void main() {
    v_normal = u_normal_matrix * a_normal;
    v_uv = a_uv;
    gl_Position = u_view_projection * u_model * vec4(a_position, 1.0);
}
"""

_FRAGMENT_SHADER = """
#version 330 core
in vec3 v_normal;
in vec2 v_uv;

uniform sampler2D u_texture;
uniform vec4 u_color;
uniform vec3 u_light_direction;
uniform float u_ambient;

out vec4 out_color;

void main() {
    vec3 normal = normalize(v_normal);
    float diffuse = max(dot(normal, normalize(-u_light_direction)), 0.0);
    float lighting = clamp(u_ambient + diffuse, 0.0, 1.0);
    vec4 sampled = texture(u_texture, v_uv);
    out_color = vec4(sampled.rgb * u_color.rgb * lighting, sampled.a * u_color.a);
}
"""


class Renderer3D:
    def __init__(self):
        self.shader = Shader.from_source(_VERTEX_SHADER, _FRAGMENT_SHADER)
        self.white_texture = Texture2D.blank_white()
        self.light_direction = Vec3(-0.4, -1.0, -0.3)
        self.ambient = 0.25
        self._view_projection = None
        self.draw_calls = 0

    def begin(self, camera):
        self._view_projection = camera.view_projection_matrix()
        self.draw_calls = 0

    def submit(self, mesh, model_matrix, color=WHITE, texture=None):
        self.shader.use()
        self.shader.set_mat4("u_view_projection", self._view_projection)
        self.shader.set_mat4("u_model", model_matrix)

        normal_matrix = model_matrix.inverse().transposed().m[:3, :3]
        location = self.shader._location("u_normal_matrix")
        gl.glUniformMatrix3fv(location, 1, gl.GL_TRUE, normal_matrix.astype("float32"))

        self.shader.set_color("u_color", color)
        self.shader.set_vec3("u_light_direction", self.light_direction)
        self.shader.set_float("u_ambient", self.ambient)

        active_texture = texture or self.white_texture
        active_texture.bind(0)
        self.shader.set_int("u_texture", 0)

        mesh.draw()
        self.draw_calls += 1

    def end(self):
        pass

    def delete(self):
        self.shader.delete()
        self.white_texture.delete()
