import numpy as np
from OpenGL import GL as gl

from ..mathlib import Vec2
from .buffer import BufferElement, BufferLayout, IndexBuffer, VertexArray, VertexBuffer
from .color import WHITE
from .shader import Shader
from .texture import Texture2D

_MAX_QUADS = 10000
_MAX_VERTICES = _MAX_QUADS * 4
_MAX_INDICES = _MAX_QUADS * 6
_MAX_TEXTURE_SLOTS = 8
_FLOATS_PER_VERTEX = 9

_VERTEX_SHADER = """
#version 330 core
layout(location = 0) in vec2 a_position;
layout(location = 1) in vec2 a_uv;
layout(location = 2) in vec4 a_color;
layout(location = 3) in float a_tex_index;

uniform mat4 u_view_projection;

out vec2 v_uv;
out vec4 v_color;
out float v_tex_index;

void main() {
    v_uv = a_uv;
    v_color = a_color;
    v_tex_index = a_tex_index;
    gl_Position = u_view_projection * vec4(a_position, 0.0, 1.0);
}
"""

_FRAGMENT_SHADER = """
#version 330 core
in vec2 v_uv;
in vec4 v_color;
in float v_tex_index;

uniform sampler2D u_textures[8];

out vec4 out_color;

void main() {
    int index = int(v_tex_index + 0.5);
    vec4 sampled = vec4(1.0);
    if (index == 0) sampled = texture(u_textures[0], v_uv);
    else if (index == 1) sampled = texture(u_textures[1], v_uv);
    else if (index == 2) sampled = texture(u_textures[2], v_uv);
    else if (index == 3) sampled = texture(u_textures[3], v_uv);
    else if (index == 4) sampled = texture(u_textures[4], v_uv);
    else if (index == 5) sampled = texture(u_textures[5], v_uv);
    else if (index == 6) sampled = texture(u_textures[6], v_uv);
    else if (index == 7) sampled = texture(u_textures[7], v_uv);
    out_color = sampled * v_color;
    if (out_color.a <= 0.001) discard;
}
"""

_QUAD_LOCAL_CORNERS = (Vec2(-0.5, -0.5), Vec2(0.5, -0.5), Vec2(0.5, 0.5), Vec2(-0.5, 0.5))
_QUAD_UVS_DEFAULT = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))


class Renderer2D:
    def __init__(self):
        self.shader = Shader.from_source(_VERTEX_SHADER, _FRAGMENT_SHADER)
        self.white_texture = Texture2D.blank_white()

        layout = BufferLayout([
            BufferElement("position", 2, gl.GL_FLOAT),
            BufferElement("uv", 2, gl.GL_FLOAT),
            BufferElement("color", 4, gl.GL_FLOAT),
            BufferElement("tex_index", 1, gl.GL_FLOAT),
        ])
        self.vertex_array = VertexArray()
        self.vertex_buffer = VertexBuffer(_MAX_VERTICES * _FLOATS_PER_VERTEX * 4, dynamic=True)
        self.vertex_array.add_vertex_buffer(self.vertex_buffer, layout)

        indices = np.zeros(_MAX_INDICES, dtype=np.uint32)
        offset = 0
        for i in range(0, _MAX_INDICES, 6):
            indices[i + 0] = offset + 0
            indices[i + 1] = offset + 1
            indices[i + 2] = offset + 2
            indices[i + 3] = offset + 2
            indices[i + 4] = offset + 3
            indices[i + 5] = offset + 0
            offset += 4
        self.index_buffer = IndexBuffer(indices, dynamic=False)
        self.vertex_array.set_index_buffer(self.index_buffer)

        self._cpu_buffer = np.zeros(_MAX_VERTICES * _FLOATS_PER_VERTEX, dtype=np.float32)
        self._write_offset = 0
        self._quad_count = 0
        self._texture_slots = [self.white_texture] + [None] * (_MAX_TEXTURE_SLOTS - 1)
        self._texture_slot_count = 1
        self._view_projection = None
        self.draw_calls = 0

        self.shader.use()
        self.shader.set_int("u_textures[0]", 0)
        for slot in range(1, _MAX_TEXTURE_SLOTS):
            self.shader.set_int(f"u_textures[{slot}]", slot)

        self._immediate_array = VertexArray()
        self._immediate_buffer = VertexBuffer(256 * _FLOATS_PER_VERTEX * 4, dynamic=True)
        self._immediate_array.add_vertex_buffer(self._immediate_buffer, layout)

    def begin(self, camera):
        self._view_projection = camera.view_projection_matrix()
        self._write_offset = 0
        self._quad_count = 0
        self._texture_slot_count = 1
        self.draw_calls = 0

    def _texture_slot_for(self, texture):
        if texture is None:
            return 0.0
        for index in range(1, self._texture_slot_count):
            if self._texture_slots[index] is texture:
                return float(index)
        if self._texture_slot_count >= _MAX_TEXTURE_SLOTS:
            self.flush()
        slot = self._texture_slot_count
        self._texture_slots[slot] = texture
        self._texture_slot_count += 1
        return float(slot)

    def _push_quad_vertices(self, positions, uvs, color, tex_index):
        if self._quad_count >= _MAX_QUADS:
            self.flush()
        base = self._write_offset
        for i in range(4):
            self._cpu_buffer[base + 0] = positions[i].x
            self._cpu_buffer[base + 1] = positions[i].y
            self._cpu_buffer[base + 2] = uvs[i][0]
            self._cpu_buffer[base + 3] = uvs[i][1]
            self._cpu_buffer[base + 4] = color.r
            self._cpu_buffer[base + 5] = color.g
            self._cpu_buffer[base + 6] = color.b
            self._cpu_buffer[base + 7] = color.a
            self._cpu_buffer[base + 8] = tex_index
            base += _FLOATS_PER_VERTEX
        self._write_offset = base
        self._quad_count += 1

    def draw_quad(self, position, size, rotation=0.0, color=WHITE, texture=None, uv_min=(0.0, 0.0), uv_max=(1.0, 1.0)):
        tex_index = self._texture_slot_for(texture)
        positions = []
        for corner in _QUAD_LOCAL_CORNERS:
            offset = Vec2(corner.x * size.x, corner.y * size.y)
            if rotation != 0.0:
                offset = offset.rotated(rotation)
            positions.append(Vec2(position.x + offset.x, position.y + offset.y))
        uvs = (
            (uv_min[0], uv_min[1]),
            (uv_max[0], uv_min[1]),
            (uv_max[0], uv_max[1]),
            (uv_min[0], uv_max[1]),
        )
        self._push_quad_vertices(positions, uvs, color, tex_index)

    def draw_texture(self, texture, position, size=None, rotation=0.0, color=WHITE):
        if size is None:
            size = Vec2(texture.width, texture.height)
        self.draw_quad(position, size, rotation, color, texture)

    def draw_rect_filled(self, position, size, color=WHITE):
        self.draw_quad(position, size, 0.0, color, None)

    def draw_line(self, p0, p1, color=WHITE, thickness=1.0):
        direction = Vec2(p1.x - p0.x, p1.y - p0.y)
        length = direction.length()
        if length == 0.0:
            return
        angle = np.arctan2(direction.y, direction.x)
        center = Vec2((p0.x + p1.x) * 0.5, (p0.y + p1.y) * 0.5)
        self.draw_quad(center, Vec2(length, thickness), float(angle), color, None)

    def draw_rect_outline(self, position, size, color=WHITE, thickness=1.0):
        half_w, half_h = size.x * 0.5, size.y * 0.5
        top_left = Vec2(position.x - half_w, position.y - half_h)
        top_right = Vec2(position.x + half_w, position.y - half_h)
        bottom_right = Vec2(position.x + half_w, position.y + half_h)
        bottom_left = Vec2(position.x - half_w, position.y + half_h)
        self.draw_line(top_left, top_right, color, thickness)
        self.draw_line(top_right, bottom_right, color, thickness)
        self.draw_line(bottom_right, bottom_left, color, thickness)
        self.draw_line(bottom_left, top_left, color, thickness)

    def draw_polygon_filled(self, points, color=WHITE):
        if len(points) < 3:
            return
        self.flush()
        vertex_count = len(points)
        data = np.zeros(vertex_count * _FLOATS_PER_VERTEX, dtype=np.float32)
        for i, point in enumerate(points):
            base = i * _FLOATS_PER_VERTEX
            data[base + 0] = point.x
            data[base + 1] = point.y
            data[base + 2] = 0.0
            data[base + 3] = 0.0
            data[base + 4] = color.r
            data[base + 5] = color.g
            data[base + 6] = color.b
            data[base + 7] = color.a
            data[base + 8] = 0.0

        self._immediate_buffer.set_data(data)
        self.shader.use()
        self.shader.set_mat4("u_view_projection", self._view_projection)
        for index in range(_MAX_TEXTURE_SLOTS):
            self.white_texture.bind(index)
        self._immediate_array.bind()
        gl.glDrawArrays(gl.GL_TRIANGLE_FAN, 0, vertex_count)
        self._immediate_array.unbind()
        self.draw_calls += 1

    def draw_text(self, font, text, position, color=WHITE, scale=1.0):
        cursor_x = position.x
        line_top_y = position.y
        for char in text:
            if char == "\n":
                cursor_x = position.x
                line_top_y += font.line_height * scale
                continue
            glyph = font.get_glyph(char)
            if glyph is None:
                continue
            if glyph.width > 0 and glyph.height > 0:
                width = glyph.width * scale
                height = glyph.height * scale
                center = Vec2(cursor_x + width * 0.5, line_top_y + height * 0.5)
                self.draw_quad(
                    center, Vec2(width, height), 0.0, color, font.texture,
                    (glyph.u0, glyph.v0), (glyph.u1, glyph.v1),
                )
            cursor_x += glyph.advance * scale

    def draw_circle_filled(self, center, radius, color=WHITE, segments=32):
        points = [center]
        for i in range(segments + 1):
            angle = (i / segments) * 2.0 * np.pi
            points.append(Vec2(center.x + np.cos(angle) * radius, center.y + np.sin(angle) * radius))
        self.draw_polygon_filled(points, color)

    def flush(self):
        if self._quad_count == 0:
            return
        used_floats = self._quad_count * 4 * _FLOATS_PER_VERTEX
        self.vertex_buffer.set_data(self._cpu_buffer[:used_floats])

        self.shader.use()
        self.shader.set_mat4("u_view_projection", self._view_projection)
        for index in range(_MAX_TEXTURE_SLOTS):
            texture = self._texture_slots[index] if index < self._texture_slot_count else self.white_texture
            texture.bind(index)

        self.vertex_array.bind()
        gl.glDrawElements(gl.GL_TRIANGLES, self._quad_count * 6, gl.GL_UNSIGNED_INT, None)
        self.vertex_array.unbind()

        self.draw_calls += 1
        self._write_offset = 0
        self._quad_count = 0
        self._texture_slot_count = 1

    def end(self):
        self.flush()

    def delete(self):
        self.shader.delete()
        self.white_texture.delete()
        self.vertex_buffer.delete()
        self.index_buffer.delete()
        self.vertex_array.delete()
        self._immediate_buffer.delete()
        self._immediate_array.delete()
