from OpenGL import GL as gl
from PIL import Image


class Texture2D:
    def __init__(self, width, height, pixels=None, channels=4, nearest=False):
        self.width = width
        self.height = height
        self.channels = channels
        internal_format = gl.GL_RGBA8 if channels == 4 else gl.GL_R8
        pixel_format = gl.GL_RGBA if channels == 4 else gl.GL_RED

        self.texture_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_id)
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
        gl.glTexImage2D(
            gl.GL_TEXTURE_2D, 0, internal_format, width, height, 0,
            pixel_format, gl.GL_UNSIGNED_BYTE, pixels,
        )
        filter_mode = gl.GL_NEAREST if nearest else gl.GL_LINEAR
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, filter_mode)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, filter_mode)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    @classmethod
    def from_path(cls, path, nearest=False):
        image = Image.open(path).convert("RGBA")
        return cls(image.width, image.height, image.tobytes(), channels=4, nearest=nearest)

    @classmethod
    def blank_white(cls):
        return cls(1, 1, bytes([255, 255, 255, 255]), channels=4, nearest=True)

    def update_region(self, x, y, width, height, pixels):
        pixel_format = gl.GL_RGBA if self.channels == 4 else gl.GL_RED
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_id)
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
        gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, x, y, width, height, pixel_format, gl.GL_UNSIGNED_BYTE, pixels)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    def bind(self, unit=0):
        gl.glActiveTexture(gl.GL_TEXTURE0 + unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_id)

    def set_wrap_repeat(self):
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_id)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    def delete(self):
        gl.glDeleteTextures(1, [self.texture_id])
