import ctypes

import sdl2

from . import log


class Window:
    def __init__(self, title="SMRE Window", width=1280, height=720, resizable=True, vsync=True, visible=True, highdpi=False, gl_major=3, gl_minor=3):
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MAJOR_VERSION, gl_major)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MINOR_VERSION, gl_minor)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_PROFILE_MASK, sdl2.SDL_GL_CONTEXT_PROFILE_CORE)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_DOUBLEBUFFER, 1)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_DEPTH_SIZE, 24)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_STENCIL_SIZE, 8)

        flags = sdl2.SDL_WINDOW_OPENGL
        if highdpi:
            flags |= sdl2.SDL_WINDOW_ALLOW_HIGHDPI
        flags |= sdl2.SDL_WINDOW_SHOWN if visible else sdl2.SDL_WINDOW_HIDDEN
        if resizable:
            flags |= sdl2.SDL_WINDOW_RESIZABLE

        self.handle = sdl2.SDL_CreateWindow(
            title.encode("utf-8"),
            sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED,
            width, height, flags,
        )
        if not self.handle:
            raise RuntimeError(f"Failed to create SDL window: {sdl2.SDL_GetError()}")

        self.gl_context = sdl2.SDL_GL_CreateContext(self.handle)
        if not self.gl_context:
            raise RuntimeError(f"Failed to create OpenGL context: {sdl2.SDL_GetError()}")

        self.set_vsync(vsync)
        self._width = width
        self._height = height
        log.info(f"Window created: {title} ({width}x{height})")

    def set_vsync(self, enabled):
        sdl2.SDL_GL_SetSwapInterval(1 if enabled else 0)

    def set_title(self, title):
        sdl2.SDL_SetWindowTitle(self.handle, title.encode("utf-8"))

    def size(self):
        width = ctypes.c_int()
        height = ctypes.c_int()
        sdl2.SDL_GetWindowSize(self.handle, ctypes.byref(width), ctypes.byref(height))
        return width.value, height.value

    def drawable_size(self):
        width = ctypes.c_int()
        height = ctypes.c_int()
        sdl2.SDL_GL_GetDrawableSize(self.handle, ctypes.byref(width), ctypes.byref(height))
        return width.value, height.value

    def swap(self):
        sdl2.SDL_GL_SwapWindow(self.handle)

    def set_relative_mouse_mode(self, enabled):
        sdl2.SDL_SetRelativeMouseMode(sdl2.SDL_TRUE if enabled else sdl2.SDL_FALSE)

    def set_cursor_visible(self, visible):
        sdl2.SDL_ShowCursor(sdl2.SDL_ENABLE if visible else sdl2.SDL_DISABLE)

    def destroy(self):
        if self.gl_context:
            sdl2.SDL_GL_DeleteContext(self.gl_context)
            self.gl_context = None
        if self.handle:
            sdl2.SDL_DestroyWindow(self.handle)
            self.handle = None
