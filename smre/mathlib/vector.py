import math


class Vec2:
    __slots__ = ("x", "y")

    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    @classmethod
    def zero(cls):
        return cls(0.0, 0.0)

    @classmethod
    def one(cls):
        return cls(1.0, 1.0)

    def copy(self):
        return Vec2(self.x, self.y)

    def to_tuple(self):
        return (self.x, self.y)

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def length_squared(self):
        return self.x * self.x + self.y * self.y

    def normalized(self):
        length = self.length()
        if length == 0.0:
            return Vec2(0.0, 0.0)
        return Vec2(self.x / length, self.y / length)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def cross(self, other):
        return self.x * other.y - self.y * other.x

    def rotated(self, radians):
        cos_a = math.cos(radians)
        sin_a = math.sin(radians)
        return Vec2(self.x * cos_a - self.y * sin_a, self.x * sin_a + self.y * cos_a)

    def perpendicular(self):
        return Vec2(-self.y, self.x)

    def lerp(self, other, t):
        return Vec2(self.x + (other.x - self.x) * t, self.y + (other.y - self.y) * t)

    def distance_to(self, other):
        return (self - other).length()

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __neg__(self):
        return Vec2(-self.x, -self.y)

    def __mul__(self, scalar):
        if isinstance(scalar, Vec2):
            return Vec2(self.x * scalar.x, self.y * scalar.y)
        return Vec2(self.x * scalar, self.y * scalar)

    __rmul__ = __mul__

    def __truediv__(self, scalar):
        return Vec2(self.x / scalar, self.y / scalar)

    def __eq__(self, other):
        return isinstance(other, Vec2) and self.x == other.x and self.y == other.y

    def __iter__(self):
        yield self.x
        yield self.y

    def __repr__(self):
        return f"Vec2({self.x:.4f}, {self.y:.4f})"


class Vec3:
    __slots__ = ("x", "y", "z")

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    @classmethod
    def zero(cls):
        return cls(0.0, 0.0, 0.0)

    @classmethod
    def one(cls):
        return cls(1.0, 1.0, 1.0)

    @classmethod
    def up(cls):
        return cls(0.0, 1.0, 0.0)

    @classmethod
    def right(cls):
        return cls(1.0, 0.0, 0.0)

    @classmethod
    def forward(cls):
        return cls(0.0, 0.0, -1.0)

    def copy(self):
        return Vec3(self.x, self.y, self.z)

    def to_tuple(self):
        return (self.x, self.y, self.z)

    def xy(self):
        return Vec2(self.x, self.y)

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def length_squared(self):
        return self.x * self.x + self.y * self.y + self.z * self.z

    def normalized(self):
        length = self.length()
        if length == 0.0:
            return Vec3(0.0, 0.0, 0.0)
        return Vec3(self.x / length, self.y / length, self.z / length)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def lerp(self, other, t):
        return Vec3(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
            self.z + (other.z - self.z) * t,
        )

    def distance_to(self, other):
        return (self - other).length()

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self):
        return Vec3(-self.x, -self.y, -self.z)

    def __mul__(self, scalar):
        if isinstance(scalar, Vec3):
            return Vec3(self.x * scalar.x, self.y * scalar.y, self.z * scalar.z)
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    __rmul__ = __mul__

    def __truediv__(self, scalar):
        return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)

    def __eq__(self, other):
        return (
            isinstance(other, Vec3)
            and self.x == other.x
            and self.y == other.y
            and self.z == other.z
        )

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def __repr__(self):
        return f"Vec3({self.x:.4f}, {self.y:.4f}, {self.z:.4f})"


class Vec4:
    __slots__ = ("x", "y", "z", "w")

    def __init__(self, x=0.0, y=0.0, z=0.0, w=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.w = float(w)

    @classmethod
    def zero(cls):
        return cls(0.0, 0.0, 0.0, 0.0)

    def copy(self):
        return Vec4(self.x, self.y, self.z, self.w)

    def to_tuple(self):
        return (self.x, self.y, self.z, self.w)

    def xyz(self):
        return Vec3(self.x, self.y, self.z)

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z + self.w * self.w)

    def normalized(self):
        length = self.length()
        if length == 0.0:
            return Vec4(0.0, 0.0, 0.0, 0.0)
        return Vec4(self.x / length, self.y / length, self.z / length, self.w / length)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z + self.w * other.w

    def lerp(self, other, t):
        return Vec4(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
            self.z + (other.z - self.z) * t,
            self.w + (other.w - self.w) * t,
        )

    def __add__(self, other):
        return Vec4(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)

    def __sub__(self, other):
        return Vec4(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)

    def __mul__(self, scalar):
        if isinstance(scalar, Vec4):
            return Vec4(self.x * scalar.x, self.y * scalar.y, self.z * scalar.z, self.w * scalar.w)
        return Vec4(self.x * scalar, self.y * scalar, self.z * scalar, self.w * scalar)

    __rmul__ = __mul__

    def __eq__(self, other):
        return (
            isinstance(other, Vec4)
            and self.x == other.x
            and self.y == other.y
            and self.z == other.z
            and self.w == other.w
        )

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z
        yield self.w

    def __repr__(self):
        return f"Vec4({self.x:.4f}, {self.y:.4f}, {self.z:.4f}, {self.w:.4f})"
