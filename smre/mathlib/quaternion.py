import math

from .matrix import Mat4
from .vector import Vec3


class Quaternion:
    __slots__ = ("x", "y", "z", "w")

    def __init__(self, x=0.0, y=0.0, z=0.0, w=1.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.w = float(w)

    @classmethod
    def identity(cls):
        return cls(0.0, 0.0, 0.0, 1.0)

    @classmethod
    def from_axis_angle(cls, axis, radians):
        axis = axis.normalized()
        half = radians * 0.5
        s = math.sin(half)
        return cls(axis.x * s, axis.y * s, axis.z * s, math.cos(half))

    @classmethod
    def from_euler(cls, pitch, yaw, roll):
        qx = Quaternion.from_axis_angle(Vec3(1.0, 0.0, 0.0), pitch)
        qy = Quaternion.from_axis_angle(Vec3(0.0, 1.0, 0.0), yaw)
        qz = Quaternion.from_axis_angle(Vec3(0.0, 0.0, 1.0), roll)
        return qy * qx * qz

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z + self.w * self.w)

    def normalized(self):
        length = self.length()
        if length == 0.0:
            return Quaternion.identity()
        return Quaternion(self.x / length, self.y / length, self.z / length, self.w / length)

    def conjugate(self):
        return Quaternion(-self.x, -self.y, -self.z, self.w)

    def inverse(self):
        length_sq = self.x * self.x + self.y * self.y + self.z * self.z + self.w * self.w
        if length_sq == 0.0:
            return Quaternion.identity()
        conj = self.conjugate()
        return Quaternion(conj.x / length_sq, conj.y / length_sq, conj.z / length_sq, conj.w / length_sq)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z + self.w * other.w

    def slerp(self, other, t):
        dot = self.dot(other)
        a, b = self, other
        if dot < 0.0:
            b = Quaternion(-other.x, -other.y, -other.z, -other.w)
            dot = -dot
        if dot > 0.9995:
            return Quaternion(
                a.x + (b.x - a.x) * t,
                a.y + (b.y - a.y) * t,
                a.z + (b.z - a.z) * t,
                a.w + (b.w - a.w) * t,
            ).normalized()
        theta_0 = math.acos(max(-1.0, min(1.0, dot)))
        theta = theta_0 * t
        sin_theta = math.sin(theta)
        sin_theta_0 = math.sin(theta_0)
        s0 = math.cos(theta) - dot * sin_theta / sin_theta_0
        s1 = sin_theta / sin_theta_0
        return Quaternion(
            a.x * s0 + b.x * s1,
            a.y * s0 + b.y * s1,
            a.z * s0 + b.z * s1,
            a.w * s0 + b.w * s1,
        )

    def rotate_vector(self, v):
        qv = Vec3(self.x, self.y, self.z)
        uv = qv.cross(v)
        uuv = qv.cross(uv)
        return v + (uv * self.w + uuv) * 2.0

    def to_mat4(self):
        x, y, z, w = self.x, self.y, self.z, self.w
        mat = Mat4()
        mat.m[0, 0] = 1.0 - 2.0 * (y * y + z * z)
        mat.m[0, 1] = 2.0 * (x * y - z * w)
        mat.m[0, 2] = 2.0 * (x * z + y * w)
        mat.m[1, 0] = 2.0 * (x * y + z * w)
        mat.m[1, 1] = 1.0 - 2.0 * (x * x + z * z)
        mat.m[1, 2] = 2.0 * (y * z - x * w)
        mat.m[2, 0] = 2.0 * (x * z - y * w)
        mat.m[2, 1] = 2.0 * (y * z + x * w)
        mat.m[2, 2] = 1.0 - 2.0 * (x * x + y * y)
        return mat

    def to_euler(self):
        x, y, z, w = self.x, self.y, self.z, self.w
        sinr_cosp = 2.0 * (w * x + y * z)
        cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        sinp = 2.0 * (w * y - z * x)
        sinp = max(-1.0, min(1.0, sinp))
        pitch = math.asin(sinp)

        siny_cosp = 2.0 * (w * z + x * y)
        cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        return Vec3(pitch, yaw, roll)

    def __mul__(self, other):
        if isinstance(other, Quaternion):
            return Quaternion(
                self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y,
                self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x,
                self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w,
                self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z,
            )
        raise TypeError("Quaternion can only be multiplied with another Quaternion")

    def __repr__(self):
        return f"Quaternion({self.x:.4f}, {self.y:.4f}, {self.z:.4f}, {self.w:.4f})"
