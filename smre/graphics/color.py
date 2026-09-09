class Color:
    __slots__ = ("r", "g", "b", "a")

    def __init__(self, r=1.0, g=1.0, b=1.0, a=1.0):
        self.r = float(r)
        self.g = float(g)
        self.b = float(b)
        self.a = float(a)

    @classmethod
    def from_rgb255(cls, r, g, b, a=255):
        return cls(r / 255.0, g / 255.0, b / 255.0, a / 255.0)

    @classmethod
    def from_hex(cls, value):
        value = value.lstrip("#")
        if len(value) == 6:
            value += "ff"
        r = int(value[0:2], 16)
        g = int(value[2:4], 16)
        b = int(value[4:6], 16)
        a = int(value[6:8], 16)
        return cls.from_rgb255(r, g, b, a)

    def to_tuple(self):
        return (self.r, self.g, self.b, self.a)

    def to_rgb255(self):
        return (
            int(round(self.r * 255)),
            int(round(self.g * 255)),
            int(round(self.b * 255)),
            int(round(self.a * 255)),
        )

    def to_uint32(self):
        r, g, b, a = self.to_rgb255()
        return (a << 24) | (b << 16) | (g << 8) | r

    def with_alpha(self, alpha):
        return Color(self.r, self.g, self.b, alpha)

    def lerp(self, other, t):
        return Color(
            self.r + (other.r - self.r) * t,
            self.g + (other.g - self.g) * t,
            self.b + (other.b - self.b) * t,
            self.a + (other.a - self.a) * t,
        )

    def __repr__(self):
        return f"Color({self.r:.3f}, {self.g:.3f}, {self.b:.3f}, {self.a:.3f})"


WHITE = Color(1.0, 1.0, 1.0, 1.0)
BLACK = Color(0.0, 0.0, 0.0, 1.0)
TRANSPARENT = Color(0.0, 0.0, 0.0, 0.0)
RED = Color(1.0, 0.0, 0.0, 1.0)
GREEN = Color(0.0, 1.0, 0.0, 1.0)
BLUE = Color(0.0, 0.0, 1.0, 1.0)
YELLOW = Color(1.0, 1.0, 0.0, 1.0)
CYAN = Color(0.0, 1.0, 1.0, 1.0)
MAGENTA = Color(1.0, 0.0, 1.0, 1.0)
GRAY = Color(0.5, 0.5, 0.5, 1.0)
DARK_GRAY = Color(0.15, 0.15, 0.15, 1.0)
LIGHT_GRAY = Color(0.75, 0.75, 0.75, 1.0)
