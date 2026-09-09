from .matrix import Mat4
from .quaternion import Quaternion
from .vector import Vec3


class Transform:
    __slots__ = ("position", "rotation", "scale")

    def __init__(self, position=None, rotation=None, scale=None):
        self.position = position if position is not None else Vec3.zero()
        self.rotation = rotation if rotation is not None else Quaternion.identity()
        self.scale = scale if scale is not None else Vec3.one()

    def translate(self, offset):
        self.position = self.position + offset

    def rotate(self, axis, radians):
        self.rotation = Quaternion.from_axis_angle(axis, radians) * self.rotation

    def forward(self):
        return self.rotation.rotate_vector(Vec3.forward())

    def right(self):
        return self.rotation.rotate_vector(Vec3.right())

    def up(self):
        return self.rotation.rotate_vector(Vec3.up())

    def matrix(self):
        translation = Mat4.translation(self.position)
        rotation = self.rotation.to_mat4()
        scale = Mat4.scale(self.scale)
        return translation @ rotation @ scale

    def copy(self):
        rotation = Quaternion(self.rotation.x, self.rotation.y, self.rotation.z, self.rotation.w)
        return Transform(self.position.copy(), rotation, self.scale.copy())

    def __repr__(self):
        return f"Transform(position={self.position}, rotation={self.rotation}, scale={self.scale})"
