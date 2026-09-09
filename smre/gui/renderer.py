import ctypes

import numpy as np
from OpenGL import GL as gl

from ..graphics.buffer import BufferElement, BufferLayout, IndexBuffer, VertexArray, VertexBuffer
from ..graphics.shader import Shader
from ..mathlib import Mat4

_VERTEX_SHADER = """
#version 330 core
layout(location = 0) in vec2 a_position;
layout(location = 1) in vec2 a_uv;
layout(location = 2) in vec4 a_color;

uniform mat4 u_projection;

out vec2 v_uv;
out vec4 v_color;

void main() {
    v_uv = a_uv;
    v_color = a_color;
    gl_Position = u_projection * vec4(a_position, 0.0, 1.0);
}
"""

_FRAGMENT_SHADER = """
#version 330 core
in vec2 v_uv;
in vec4 v_color;

uniform sampler2D u_texture;

out vec4 out_color;

void main() {
    out_color = texture(u_texture, v_uv) * v_color;
}
"""


class GuiRenderer:
    def __init__(self):
        self.shader = Shader.from_source(_VERTEX_SHADER, _FRAGMENT_SHADER)
        layout = BufferLayout([
            BufferElement("position", 2, gl.GL_FLOAT),
            BufferElement("uv", 2, gl.GL_FLOAT),
            BufferElement("color", 4, gl.GL_FLOAT),
        ])
        self.vertex_array = VertexArray()
        self.vertex_buffer = VertexBuffer(64 * 1024, dynamic=True)
        self.vertex_array.add_vertex_buffer(self.vertex_buffer, layout)
        self.index_buffer = IndexBuffer(np.zeros(6, dtype=np.uint32), dynamic=True)
        self.vertex_array.set_index_buffer(self.index_buffer)

    def render(self, draw_list, framebuffer_width, framebuffer_height):
        if not draw_list.indices:
            return

        vertex_data = np.asarray(draw_list.vertices, dtype=np.float32)
        index_data = np.asarray(draw_list.indices, dtype=np.uint32)
        self.vertex_buffer.set_data(vertex_data)
        self.index_buffer.set_data(index_data)

        projection = Mat4.ortho(0.0, framebuffer_width, framebuffer_height, 0.0, -1.0, 1.0)

        blend_was_enabled = gl.glIsEnabled(gl.GL_BLEND)
        depth_was_enabled = gl.glIsEnabled(gl.GL_DEPTH_TEST)
        cull_was_enabled = gl.glIsEnabled(gl.GL_CULL_FACE)

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_CULL_FACE)
        gl.glEnable(gl.GL_SCISSOR_TEST)
        gl.glViewport(0, 0, int(framebuffer_width), int(framebuffer_height))

        self.shader.use()
        self.shader.set_mat4("u_projection", projection)
        self.shader.set_int("u_texture", 0)

        self.vertex_array.bind()
        for command in draw_list.commands:
            if command.index_count == 0:
                continue
            clip_x, clip_y, clip_w, clip_h = command.clip_rect
            scissor_x = max(0, int(clip_x))
            scissor_y = max(0, int(framebuffer_height - (clip_y + clip_h)))
            scissor_w = max(0, int(clip_w))
            scissor_h = max(0, int(clip_h))
            if scissor_w <= 0 or scissor_h <= 0:
                continue
            gl.glScissor(scissor_x, scissor_y, scissor_w, scissor_h)
            command.texture.bind(0)
            offset_bytes = ctypes.c_void_p(command.index_offset * 4)
            gl.glDrawElements(gl.GL_TRIANGLES, command.index_count, gl.GL_UNSIGNED_INT, offset_bytes)
        self.vertex_array.unbind()

        gl.glDisable(gl.GL_SCISSOR_TEST)
        if not blend_was_enabled:
            gl.glDisable(gl.GL_BLEND)
        if depth_was_enabled:
            gl.glEnable(gl.GL_DEPTH_TEST)
        if cull_was_enabled:
            gl.glEnable(gl.GL_CULL_FACE)

    def delete(self):
        self.shader.delete()
        self.vertex_buffer.delete()
        self.index_buffer.delete()
        self.vertex_array.delete()
