import ctypes
import os
import sys

import sdl2
import sdl2.sdlttf as sdlttf

from .texture import Texture2D

_ttf_initialized = False

_DEFAULT_FONT_CANDIDATES = {
    "darwin": [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ],
    "linux": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
    ],
    "win32": [
        "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
    ],
}

DEFAULT_CHARSET = "".join(chr(code) for code in range(32, 127))


def _ensure_ttf():
    global _ttf_initialized
    if not _ttf_initialized:
        if sdlttf.TTF_Init() != 0:
            raise RuntimeError(f"TTF_Init failed: {sdl2.SDL_GetError()}")
        _ttf_initialized = True


def find_default_font_path():
    candidates = _DEFAULT_FONT_CANDIDATES.get(sys.platform, [])
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


class Glyph:
    __slots__ = ("u0", "v0", "u1", "v1", "width", "height", "advance")

    def __init__(self, u0, v0, u1, v1, width, height, advance):
        self.u0 = u0
        self.v0 = v0
        self.u1 = u1
        self.v1 = v1
        self.width = width
        self.height = height
        self.advance = advance


class Font:
    def __init__(self, texture, glyphs, line_height, ascent, size):
        self.texture = texture
        self.glyphs = glyphs
        self.line_height = line_height
        self.ascent = ascent
        self.size = size

    @classmethod
    def from_file(cls, path=None, size=18, charset=DEFAULT_CHARSET, atlas_width=512):
        _ensure_ttf()
        resolved_path = path or find_default_font_path()
        if resolved_path is None:
            raise RuntimeError(
                "No font path given and no default system font could be located; "
                "pass an explicit font_path."
            )

        font_ptr = sdlttf.TTF_OpenFont(resolved_path.encode("utf-8"), size)
        if not font_ptr:
            raise RuntimeError(f"TTF_OpenFont failed for {resolved_path}: {sdl2.SDL_GetError()}")

        line_height = sdlttf.TTF_FontHeight(font_ptr)
        ascent = sdlttf.TTF_FontAscent(font_ptr)

        white = sdl2.SDL_Color(255, 255, 255, 255)
        rendered = {}
        for char in charset:
            surface_ptr = sdlttf.TTF_RenderGlyph32_Blended(font_ptr, ord(char), white)
            if not surface_ptr:
                continue
            converted = sdl2.SDL_ConvertSurfaceFormat(surface_ptr, sdl2.SDL_PIXELFORMAT_ABGR8888, 0)
            sdl2.SDL_FreeSurface(surface_ptr)
            if not converted:
                continue
            rendered[char] = converted

        cursor_x = 0
        cursor_y = 0
        row_height = 0
        padding = 1
        placements = {}
        for char, surface_ptr in rendered.items():
            surface = surface_ptr.contents
            width, height = surface.w, surface.h
            if cursor_x + width + padding > atlas_width:
                cursor_x = 0
                cursor_y += row_height + padding
                row_height = 0
            placements[char] = (cursor_x, cursor_y, width, height)
            cursor_x += width + padding
            row_height = max(row_height, height)
        atlas_height = max(1, cursor_y + row_height + padding)

        texture = Texture2D(atlas_width, atlas_height, None, channels=4, nearest=False)

        glyphs = {}
        min_x = ctypes.c_int()
        max_x = ctypes.c_int()
        min_y = ctypes.c_int()
        max_y = ctypes.c_int()
        advance = ctypes.c_int()
        for char, surface_ptr in rendered.items():
            surface = surface_ptr.contents
            x, y, width, height = placements[char]
            pixel_count = width * height * 4
            pixels = ctypes.string_at(surface.pixels, pixel_count)
            if width > 0 and height > 0:
                texture.update_region(x, y, width, height, pixels)

            sdlttf.TTF_GlyphMetrics32(
                font_ptr, ord(char),
                ctypes.byref(min_x), ctypes.byref(max_x),
                ctypes.byref(min_y), ctypes.byref(max_y),
                ctypes.byref(advance),
            )
            glyphs[char] = Glyph(
                u0=x / atlas_width,
                v0=y / atlas_height,
                u1=(x + width) / atlas_width,
                v1=(y + height) / atlas_height,
                width=width,
                height=height,
                advance=advance.value,
            )
            sdl2.SDL_FreeSurface(surface_ptr)

        sdlttf.TTF_CloseFont(font_ptr)
        return cls(texture, glyphs, line_height, ascent, size)

    def get_glyph(self, char):
        return self.glyphs.get(char) or self.glyphs.get("?")

    def measure(self, text):
        lines = text.split("\n")
        max_width = 0.0
        for line in lines:
            width = 0.0
            for char in line:
                glyph = self.get_glyph(char)
                if glyph is not None:
                    width += glyph.advance
            max_width = max(max_width, width)
        return max_width, float(self.line_height) * len(lines)

    def delete(self):
        self.texture.delete()
