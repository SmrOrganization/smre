import ctypes

import numpy as np
from OpenGL import GL as gl

_GL_TYPE_SIZES = {
    gl.GL_FLOAT: 4,
    gl.GL_UNSIGNED_INT: 4,
    gl.GL_UNSIGNED_BYTE: 1,
    gl.GL_INT: 4,
}


class BufferElement:
    __slots__ = ("name", "count", "gl_type", "normalized")

    def __init__(self, name, count, gl_type=gl.GL_FLOAT, normalized=False):
        self.name = name
        self.count = count
        self.gl_type = gl_type
        self.normalized = normalized

    @property
    def size_bytes(self):
        return self.count * _GL_TYPE_SIZES[self.gl_type]


class BufferLayout:
    def __init__(self, elements):
        self.elements = elements
        self.stride = sum(element.size_bytes for element in elements)


class VertexBuffer:
    def __init__(self, size_or_data, dynamic=True):
        self.buffer_id = gl.glGenBuffers(1)
        self.dynamic = dynamic
        self.layout = None
        usage = gl.GL_DYNAMIC_DRAW if dynamic else gl.GL_STATIC_DRAW
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffer_id)
        if isinstance(size_or_data, int):
            self.capacity = size_or_data
            gl.glBufferData(gl.GL_ARRAY_BUFFER, size_or_data, None, usage)
        else:
            data = np.asarray(size_or_data, dtype=np.float32)
            self.capacity = data.nbytes
            gl.glBufferData(gl.GL_ARRAY_BUFFER, data.nbytes, data.tobytes(), usage)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    def bind(self):
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffer_id)

    def unbind(self):
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    def set_data(self, data):
        array = np.asarray(data, dtype=np.float32)
        payload = array.tobytes()
        self.bind()
        if len(payload) > self.capacity:
            gl.glBufferData(gl.GL_ARRAY_BUFFER, len(payload), payload, gl.GL_DYNAMIC_DRAW)
            self.capacity = len(payload)
        else:
            gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, len(payload), payload)
        self.unbind()

    def delete(self):
        gl.glDeleteBuffers(1, [self.buffer_id])


class IndexBuffer:
    def __init__(self, indices, dynamic=False):
        self.buffer_id = gl.glGenBuffers(1)
        self.dynamic = dynamic
        array = np.asarray(indices, dtype=np.uint32)
        self.count = len(array)
        self.capacity = array.nbytes
        usage = gl.GL_DYNAMIC_DRAW if dynamic else gl.GL_STATIC_DRAW
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.buffer_id)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, array.nbytes, array.tobytes(), usage)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)

    def bind(self):
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.buffer_id)

    def unbind(self):
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)

    def set_data(self, indices):
        array = np.asarray(indices, dtype=np.uint32)
        self.count = len(array)
        self.bind()
        if array.nbytes > self.capacity:
            gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, array.nbytes, array.tobytes(), gl.GL_DYNAMIC_DRAW)
            self.capacity = array.nbytes
        else:
            gl.glBufferSubData(gl.GL_ELEMENT_ARRAY_BUFFER, 0, array.nbytes, array.tobytes())
        self.unbind()

    def delete(self):
        gl.glDeleteBuffers(1, [self.buffer_id])


class VertexArray:
    def __init__(self):
        self.array_id = gl.glGenVertexArrays(1)
        self.index_buffer = None
        self._next_attribute = 0

    def bind(self):
        gl.glBindVertexArray(self.array_id)

    def unbind(self):
        gl.glBindVertexArray(0)

    def add_vertex_buffer(self, vertex_buffer, layout):
        self.bind()
        vertex_buffer.bind()
        vertex_buffer.layout = layout
        offset = 0
        for element in layout.elements:
            gl.glEnableVertexAttribArray(self._next_attribute)
            if element.gl_type in (gl.GL_UNSIGNED_INT, gl.GL_INT) and not element.normalized:
                gl.glVertexAttribIPointer(
                    self._next_attribute,
                    element.count,
                    element.gl_type,
                    layout.stride,
                    ctypes.c_void_p(offset),
                )
            else:
                gl.glVertexAttribPointer(
                    self._next_attribute,
                    element.count,
                    element.gl_type,
                    element.normalized,
                    layout.stride,
                    ctypes.c_void_p(offset),
                )
            offset += element.size_bytes
            self._next_attribute += 1
        vertex_buffer.unbind()
        self.unbind()

    def set_index_buffer(self, index_buffer):
        self.bind()
        index_buffer.bind()
        self.index_buffer = index_buffer
        self.unbind()

    def delete(self):
        gl.glDeleteVertexArrays(1, [self.array_id])
