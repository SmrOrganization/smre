import math

import numpy as np

from .vector import Vec3, Vec4


class Mat4:
    __slots__ = ("m",)

    def __init__(self, data=None):
        if data is None:
            self.m = np.identity(4, dtype=np.float32)
        else:
            self.m = np.array(data, dtype=np.float32).reshape(4, 4)

    @classmethod
    def identity(cls):
        return cls()

    @classmethod
    def from_rows(cls, r0, r1, r2, r3):
        return cls([r0, r1, r2, r3])

    @classmethod
    def translation(cls, v):
        mat = cls()
        mat.m[0, 3] = v.x
        mat.m[1, 3] = v.y
        mat.m[2, 3] = v.z
        return mat

    @classmethod
    def scale(cls, v):
        mat = cls()
        mat.m[0, 0] = v.x
        mat.m[1, 1] = v.y
        mat.m[2, 2] = v.z
        return mat

    @classmethod
    def rotation_x(cls, radians):
        c, s = math.cos(radians), math.sin(radians)
        mat = cls()
        mat.m[1, 1] = c
        mat.m[1, 2] = -s
        mat.m[2, 1] = s
        mat.m[2, 2] = c
        return mat

    @classmethod
    def rotation_y(cls, radians):
        c, s = math.cos(radians), math.sin(radians)
        mat = cls()
        mat.m[0, 0] = c
        mat.m[0, 2] = s
        mat.m[2, 0] = -s
        mat.m[2, 2] = c
        return mat

    @classmethod
    def rotation_z(cls, radians):
        c, s = math.cos(radians), math.sin(radians)
        mat = cls()
        mat.m[0, 0] = c
        mat.m[0, 1] = -s
        mat.m[1, 0] = s
        mat.m[1, 1] = c
        return mat

    @classmethod
    def rotation_axis_angle(cls, axis, radians):
        axis = axis.normalized()
        c = math.cos(radians)
        s = math.sin(radians)
        t = 1.0 - c
        x, y, z = axis.x, axis.y, axis.z
        mat = cls()
        mat.m[0, 0] = t * x * x + c
        mat.m[0, 1] = t * x * y - s * z
        mat.m[0, 2] = t * x * z + s * y
        mat.m[1, 0] = t * x * y + s * z
        mat.m[1, 1] = t * y * y + c
        mat.m[1, 2] = t * y * z - s * x
        mat.m[2, 0] = t * x * z - s * y
        mat.m[2, 1] = t * y * z + s * x
        mat.m[2, 2] = t * z * z + c
        return mat

    @classmethod
    def ortho(cls, left, right, bottom, top, near, far):
        mat = cls()
        mat.m[0, 0] = 2.0 / (right - left)
        mat.m[1, 1] = 2.0 / (top - bottom)
        mat.m[2, 2] = -2.0 / (far - near)
        mat.m[0, 3] = -(right + left) / (right - left)
        mat.m[1, 3] = -(top + bottom) / (top - bottom)
        mat.m[2, 3] = -(far + near) / (far - near)
        return mat

    @classmethod
    def perspective(cls, fov_y_radians, aspect, near, far):
        f = 1.0 / math.tan(fov_y_radians / 2.0)
        mat = cls()
        mat.m[:] = 0.0
        mat.m[0, 0] = f / aspect
        mat.m[1, 1] = f
        mat.m[2, 2] = (far + near) / (near - far)
        mat.m[2, 3] = (2.0 * far * near) / (near - far)
        mat.m[3, 2] = -1.0
        return mat

    @classmethod
    def look_at(cls, eye, target, up):
        forward = (target - eye).normalized()
        side = forward.cross(up).normalized()
        real_up = side.cross(forward)
        mat = cls()
        mat.m[0, 0], mat.m[0, 1], mat.m[0, 2] = side.x, side.y, side.z
        mat.m[1, 0], mat.m[1, 1], mat.m[1, 2] = real_up.x, real_up.y, real_up.z
        mat.m[2, 0], mat.m[2, 1], mat.m[2, 2] = -forward.x, -forward.y, -forward.z
        mat.m[0, 3] = -side.dot(eye)
        mat.m[1, 3] = -real_up.dot(eye)
        mat.m[2, 3] = forward.dot(eye)
        return mat

    def transposed(self):
        return Mat4(self.m.T.copy())

    def inverse(self):
        return Mat4(np.linalg.inv(self.m))

    def transform_point(self, v):
        result = self.m @ np.array([v.x, v.y, v.z, 1.0], dtype=np.float32)
        return Vec3(result[0], result[1], result[2])

    def transform_vector(self, v):
        result = self.m @ np.array([v.x, v.y, v.z, 0.0], dtype=np.float32)
        return Vec3(result[0], result[1], result[2])

    def transform_vec4(self, v):
        result = self.m @ np.array([v.x, v.y, v.z, v.w], dtype=np.float32)
        return Vec4(result[0], result[1], result[2], result[3])

    def to_gl_bytes(self):
        return self.m.astype(np.float32).tobytes()

    def flatten_column_major(self):
        return self.m.T.astype(np.float32).flatten()

    def __matmul__(self, other):
        if isinstance(other, Mat4):
            return Mat4(self.m @ other.m)
        raise TypeError("Mat4 can only be multiplied with another Mat4")

    def __eq__(self, other):
        return isinstance(other, Mat4) and np.allclose(self.m, other.m)

    def __repr__(self):
        return f"Mat4(\n{self.m}\n)"
