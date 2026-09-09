from ..mathlib import Vec2


class AABB:
    __slots__ = ("min", "max")

    def __init__(self, min_point, max_point):
        self.min = min_point
        self.max = max_point

    @classmethod
    def from_center_size(cls, center, size):
        half_x, half_y = size.x * 0.5, size.y * 0.5
        return cls(Vec2(center.x - half_x, center.y - half_y), Vec2(center.x + half_x, center.y + half_y))

    def intersects(self, other):
        return (
            self.min.x <= other.max.x and self.max.x >= other.min.x
            and self.min.y <= other.max.y and self.max.y >= other.min.y
        )

    def contains_point(self, point):
        return self.min.x <= point.x <= self.max.x and self.min.y <= point.y <= self.max.y

    def center(self):
        return Vec2((self.min.x + self.max.x) * 0.5, (self.min.y + self.max.y) * 0.5)

    def size(self):
        return Vec2(self.max.x - self.min.x, self.max.y - self.min.y)

    def __repr__(self):
        return f"AABB(min={self.min}, max={self.max})"
