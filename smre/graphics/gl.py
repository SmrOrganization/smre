from OpenGL import GL as gl

from .. import log


def clear(color, depth=True):
    gl.glClearColor(color.r, color.g, color.b, color.a)
    mask = gl.GL_COLOR_BUFFER_BIT
    if depth:
        mask |= gl.GL_DEPTH_BUFFER_BIT
    gl.glClear(mask)


def set_viewport(x, y, width, height):
    gl.glViewport(x, y, width, height)


def enable_blend(enabled=True):
    if enabled:
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    else:
        gl.glDisable(gl.GL_BLEND)


def enable_depth_test(enabled=True):
    if enabled:
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LESS)
    else:
        gl.glDisable(gl.GL_DEPTH_TEST)


def enable_scissor_test(enabled=True):
    if enabled:
        gl.glEnable(gl.GL_SCISSOR_TEST)
    else:
        gl.glDisable(gl.GL_SCISSOR_TEST)


def set_scissor(x, y, width, height):
    gl.glScissor(int(x), int(y), max(0, int(width)), max(0, int(height)))


def enable_cull_face(enabled=True):
    if enabled:
        gl.glEnable(gl.GL_CULL_FACE)
        gl.glCullFace(gl.GL_BACK)
    else:
        gl.glDisable(gl.GL_CULL_FACE)


def check_gl_error(where=""):
    error = gl.glGetError()
    if error != gl.GL_NO_ERROR:
        log.error(f"OpenGL error {error} at {where}")
    return error


def gl_info():
    return {
        "version": gl.glGetString(gl.GL_VERSION).decode("utf-8"),
        "vendor": gl.glGetString(gl.GL_VENDOR).decode("utf-8"),
        "renderer": gl.glGetString(gl.GL_RENDERER).decode("utf-8"),
        "shading_language_version": gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION).decode("utf-8"),
    }
