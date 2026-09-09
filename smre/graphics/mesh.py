from OpenGL import GL as gl

from .buffer import BufferElement, BufferLayout, IndexBuffer, VertexArray, VertexBuffer

MESH_LAYOUT = BufferLayout([
    BufferElement("position", 3, gl.GL_FLOAT),
    BufferElement("normal", 3, gl.GL_FLOAT),
    BufferElement("uv", 2, gl.GL_FLOAT),
])


class Mesh:
    def __init__(self, vertices, indices):
        self.vertex_array = VertexArray()
        self.vertex_buffer = VertexBuffer(vertices, dynamic=False)
        self.index_buffer = IndexBuffer(indices, dynamic=False)
        self.vertex_array.add_vertex_buffer(self.vertex_buffer, MESH_LAYOUT)
        self.vertex_array.set_index_buffer(self.index_buffer)

    def draw(self):
        self.vertex_array.bind()
        gl.glDrawElements(gl.GL_TRIANGLES, self.index_buffer.count, gl.GL_UNSIGNED_INT, None)
        self.vertex_array.unbind()

    def delete(self):
        self.vertex_buffer.delete()
        self.index_buffer.delete()
        self.vertex_array.delete()

    @classmethod
    def create_quad(cls):
        vertices = [
            -0.5, -0.5, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
             0.5, -0.5, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0,
             0.5,  0.5, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0,
            -0.5,  0.5, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0,
        ]
        indices = [0, 1, 2, 2, 3, 0]
        return cls(vertices, indices)

    @classmethod
    def create_cube(cls):
        faces = [
            ((0, 0, 1), [(-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)]),
            ((0, 0, -1), [(0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5)]),
            ((0, 1, 0), [(-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5)]),
            ((0, -1, 0), [(-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5)]),
            ((1, 0, 0), [(0.5, -0.5, 0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5)]),
            ((-1, 0, 0), [(-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5)]),
        ]
        uvs = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        vertices = []
        indices = []
        for normal, positions in faces:
            base_index = len(vertices) // 8
            for position, uv in zip(positions, uvs):
                vertices.extend(position)
                vertices.extend(normal)
                vertices.extend(uv)
            indices.extend([base_index, base_index + 1, base_index + 2, base_index + 2, base_index + 3, base_index])
        return cls(vertices, indices)
