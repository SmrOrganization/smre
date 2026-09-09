from ..graphics.color import WHITE
from ..mathlib import Vec2


class Transform2D:
    def __init__(self, position=None, rotation=0.0, scale=None):
        self.position = position if position is not None else Vec2.zero()
        self.rotation = rotation
        self.scale = scale if scale is not None else Vec2.one()


class SpriteRenderer:
    def __init__(self, texture=None, color=None, size=None, layer=0):
        self.texture = texture
        self.color = color if color is not None else WHITE
        self.size = size if size is not None else Vec2(32.0, 32.0)
        self.layer = layer
