from OpenGL import GL as gl

from .texture import Texture2D


class Framebuffer:
    def __init__(self, width, height, with_depth=True):
        self.width = width
        self.height = height
        self.framebuffer_id = gl.glGenFramebuffers(1)
        self.color_texture = None
        self.depth_renderbuffer_id = None
        self._with_depth = with_depth
        self._build(width, height, with_depth)

    def _build(self, width, height, with_depth):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.framebuffer_id)

        self.color_texture = Texture2D(width, height, None, channels=4, nearest=True)
        gl.glFramebufferTexture2D(
            gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D,
            self.color_texture.texture_id, 0,
        )

        if with_depth:
            self.depth_renderbuffer_id = gl.glGenRenderbuffers(1)
            gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self.depth_renderbuffer_id)
            gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH24_STENCIL8, width, height)
            gl.glFramebufferRenderbuffer(
                gl.GL_FRAMEBUFFER, gl.GL_DEPTH_STENCIL_ATTACHMENT, gl.GL_RENDERBUFFER,
                self.depth_renderbuffer_id,
            )

        status = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        if status != gl.GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError(f"Framebuffer incomplete, status={status}")

    def resize(self, width, height):
        if width == self.width and height == self.height:
            return
        self.width = width
        self.height = height
        self.color_texture.delete()
        if self.depth_renderbuffer_id:
            gl.glDeleteRenderbuffers(1, [self.depth_renderbuffer_id])
        self._build(width, height, self._with_depth)

    def bind(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.framebuffer_id)
        gl.glViewport(0, 0, self.width, self.height)

    def unbind(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    def delete(self):
        self.color_texture.delete()
        if self.depth_renderbuffer_id:
            gl.glDeleteRenderbuffers(1, [self.depth_renderbuffer_id])
        gl.glDeleteFramebuffers(1, [self.framebuffer_id])
