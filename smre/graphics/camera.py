import math

from ..mathlib import Mat4, Vec3


class OrthographicCamera:
    def __init__(self, width, height, zoom=1.0):
        self.position = Vec3.zero()
        self.rotation = 0.0
        self.zoom = zoom
        self.width = width
        self.height = height

    def resize(self, width, height):
        self.width = width
        self.height = height

    def projection_matrix(self):
        half_w = (self.width * 0.5) / self.zoom
        half_h = (self.height * 0.5) / self.zoom
        return Mat4.ortho(-half_w, half_w, half_h, -half_h, -1000.0, 1000.0)

    def view_matrix(self):
        translation = Mat4.translation(self.position).inverse()
        rotation = Mat4.rotation_z(self.rotation).inverse()
        return rotation @ translation

    def view_projection_matrix(self):
        return self.projection_matrix() @ self.view_matrix()

    def screen_to_world(self, screen_x, screen_y):
        world_x = self.position.x + (screen_x - self.width * 0.5) / self.zoom
        world_y = self.position.y + (screen_y - self.height * 0.5) / self.zoom
        return world_x, world_y


class PerspectiveCamera:
    def __init__(self, aspect, fov_degrees=60.0, near=0.1, far=1000.0):
        self.position = Vec3.zero()
        self.yaw = -90.0
        self.pitch = 0.0
        self.fov_degrees = fov_degrees
        self.aspect = aspect
        self.near = near
        self.far = far

    def front(self):
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)
        return Vec3(
            math.cos(yaw_rad) * math.cos(pitch_rad),
            math.sin(pitch_rad),
            math.sin(yaw_rad) * math.cos(pitch_rad),
        ).normalized()

    def right(self):
        return self.front().cross(Vec3.up()).normalized()

    def up(self):
        return self.right().cross(self.front()).normalized()

    def set_aspect(self, width, height):
        self.aspect = width / max(1.0, height)

    def view_matrix(self):
        return Mat4.look_at(self.position, self.position + self.front(), Vec3.up())

    def projection_matrix(self):
        return Mat4.perspective(math.radians(self.fov_degrees), self.aspect, self.near, self.far)

    def view_projection_matrix(self):
        return self.projection_matrix() @ self.view_matrix()
