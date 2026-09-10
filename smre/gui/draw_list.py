import math

from ..graphics.color import WHITE

_BIG = 1_000_000.0


class _P:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y


class DrawCommand:
    __slots__ = ("clip_rect", "texture", "index_offset", "index_count")

    def __init__(self, clip_rect, texture, index_offset):
        self.clip_rect = clip_rect
        self.texture = texture
        self.index_offset = index_offset
        self.index_count = 0


class DrawList:
    def __init__(self, white_texture):
        self.white_texture = white_texture
        self.vertices = []
        self.indices = []
        self.commands = []
        self._clip_stack = [(0.0, 0.0, _BIG, _BIG)]

    def reset(self, clip_rect=None):
        self.vertices.clear()
        self.indices.clear()
        self.commands.clear()
        self._clip_stack = [clip_rect or (0.0, 0.0, _BIG, _BIG)]

    def push_clip_rect(self, x, y, w, h, intersect=True):
        if intersect:
            cx, cy, cw, ch = self._clip_stack[-1]
            x0 = max(x, cx)
            y0 = max(y, cy)
            x1 = min(x + w, cx + cw)
            y1 = min(y + h, cy + ch)
            rect = (x0, y0, max(0.0, x1 - x0), max(0.0, y1 - y0))
        else:
            rect = (x, y, w, h)
        self._clip_stack.append(rect)
        return rect

    def pop_clip_rect(self):
        if len(self._clip_stack) > 1:
            self._clip_stack.pop()

    def current_clip_rect(self):
        return self._clip_stack[-1]

    def _ensure_command(self, texture):
        clip = self._clip_stack[-1]
        if self.commands:
            last = self.commands[-1]
            if last.clip_rect == clip and last.texture is texture:
                return last
        command = DrawCommand(clip, texture, len(self.indices))
        self.commands.append(command)
        return command

    def _push_vertex(self, x, y, u, v, color):
        self.vertices.extend((x, y, u, v, color.r, color.g, color.b, color.a))
        return (len(self.vertices) // 8) - 1

    def _push_triangle(self, texture, i0, i1, i2):
        command = self._ensure_command(texture)
        self.indices.extend((i0, i1, i2))
        command.index_count += 3

    def _push_fan(self, texture, points_with_uv, color):
        base = len(self.vertices) // 8
        for (x, y, u, v) in points_with_uv:
            self._push_vertex(x, y, u, v, color)
        count = len(points_with_uv)
        for i in range(1, count - 1):
            self._push_triangle(texture, base, base + i, base + i + 1)

    @staticmethod
    def _rounded_rect_points(x, y, w, h, rounding, segments, corners=(True, True, True, True)):
        r = max(0.0, min(rounding, w * 0.5, h * 0.5))
        top_left, top_right, bottom_right, bottom_left = corners
        if r <= 0.01 or not any(corners):
            return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        corner_defs = [
            (x + w - r, y + r, -90.0, 0.0, (x + w, y), top_right),
            (x + w - r, y + h - r, 0.0, 90.0, (x + w, y + h), bottom_right),
            (x + r, y + h - r, 90.0, 180.0, (x, y + h), bottom_left),
            (x + r, y + r, 180.0, 270.0, (x, y), top_left),
        ]
        points = []
        for cx, cy, start_deg, end_deg, sharp_point, rounded in corner_defs:
            if not rounded:
                points.append(sharp_point)
                continue
            for i in range(segments + 1):
                t = start_deg + (end_deg - start_deg) * (i / segments)
                rad = math.radians(t)
                points.append((cx + math.cos(rad) * r, cy + math.sin(rad) * r))
        return points

    def add_rect_filled(self, position, size, color, rounding=0.0, segments=12, corners=(True, True, True, True)):
        points = self._rounded_rect_points(position.x, position.y, size.x, size.y, rounding, segments, corners)
        cx = position.x + size.x * 0.5
        cy = position.y + size.y * 0.5
        base = self._push_vertex(cx, cy, 0.0, 0.0, color)
        first = len(self.vertices) // 8
        for px, py in points:
            self._push_vertex(px, py, 0.0, 0.0, color)
        count = len(points)
        for i in range(count):
            next_i = (i + 1) % count
            self._push_triangle(self.white_texture, base, first + i, first + next_i)

    def add_rect_outline(self, position, size, color, thickness=1.0, rounding=0.0, segments=12, corners=(True, True, True, True)):
        points = self._rounded_rect_points(position.x, position.y, size.x, size.y, rounding, segments, corners)
        count = len(points)
        for i in range(count):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % count]
            self.add_line(_P(x0, y0), _P(x1, y1), color, thickness)

    def add_line(self, p0, p1, color, thickness=1.0):
        dx = p1.x - p0.x
        dy = p1.y - p0.y
        length = math.hypot(dx, dy)
        if length < 1e-6:
            return
        nx = -dy / length * thickness * 0.5
        ny = dx / length * thickness * 0.5
        i0 = self._push_vertex(p0.x + nx, p0.y + ny, 0.0, 0.0, color)
        i1 = self._push_vertex(p1.x + nx, p1.y + ny, 0.0, 0.0, color)
        i2 = self._push_vertex(p1.x - nx, p1.y - ny, 0.0, 0.0, color)
        i3 = self._push_vertex(p0.x - nx, p0.y - ny, 0.0, 0.0, color)
        self._push_triangle(self.white_texture, i0, i1, i2)
        self._push_triangle(self.white_texture, i2, i3, i0)

    def add_triangle_filled(self, p0, p1, p2, color):
        i0 = self._push_vertex(p0.x, p0.y, 0.0, 0.0, color)
        i1 = self._push_vertex(p1.x, p1.y, 0.0, 0.0, color)
        i2 = self._push_vertex(p2.x, p2.y, 0.0, 0.0, color)
        self._push_triangle(self.white_texture, i0, i1, i2)

    def add_circle_filled(self, center, radius, color, segments=24):
        cx = self._push_vertex(center.x, center.y, 0.0, 0.0, color)
        first = len(self.vertices) // 8
        for i in range(segments):
            angle = (i / segments) * 2.0 * math.pi
            self._push_vertex(center.x + math.cos(angle) * radius, center.y + math.sin(angle) * radius, 0.0, 0.0, color)
        for i in range(segments):
            self._push_triangle(self.white_texture, cx, first + i, first + (i + 1) % segments)

    def add_image(self, texture, position, size, uv_min=(0.0, 0.0), uv_max=(1.0, 1.0), color=WHITE):
        x, y = position.x, position.y
        w, h = size.x, size.y
        i0 = self._push_vertex(x, y, uv_min[0], uv_min[1], color)
        i1 = self._push_vertex(x + w, y, uv_max[0], uv_min[1], color)
        i2 = self._push_vertex(x + w, y + h, uv_max[0], uv_max[1], color)
        i3 = self._push_vertex(x, y + h, uv_min[0], uv_max[1], color)
        self._push_triangle(texture, i0, i1, i2)
        self._push_triangle(texture, i2, i3, i0)

    def add_text(self, font, text, position, color, scale=1.0):
        cursor_x = position.x
        line_top_y = position.y
        for char in text:
            if char == "\n":
                cursor_x = position.x
                line_top_y += font.line_height * scale
                continue
            glyph = font.get_glyph(char)
            if glyph is None:
                continue
            if glyph.width > 0 and glyph.height > 0:
                width = glyph.width * scale
                height = glyph.height * scale
                i0 = self._push_vertex(cursor_x, line_top_y, glyph.u0, glyph.v0, color)
                i1 = self._push_vertex(cursor_x + width, line_top_y, glyph.u1, glyph.v0, color)
                i2 = self._push_vertex(cursor_x + width, line_top_y + height, glyph.u1, glyph.v1, color)
                i3 = self._push_vertex(cursor_x, line_top_y + height, glyph.u0, glyph.v1, color)
                self._push_triangle(font.texture, i0, i1, i2)
                self._push_triangle(font.texture, i2, i3, i0)
            cursor_x += glyph.advance * scale
        return cursor_x - position.x
