import ctypes

import sdl2

from . import gui, input as input_module, log
from . import time as time_module
from . import window as window_module
from .audio import AudioSystem
from .events import EventBus
from .graphics import gl
from .graphics.color import BLACK
from .resources import ResourceManager


class Application:
    def __init__(
        self, title="SMRE Application", width=1280, height=720,
        resizable=True, vsync=True, visible=True, highdpi=True, multisample=4, clear_color=None,
        enable_audio=True, gui_font_path=None, gui_font_size=18, max_frames=None,
    ):
        sdl_flags = sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_GAMECONTROLLER
        if enable_audio:
            sdl_flags |= sdl2.SDL_INIT_AUDIO
        if sdl2.SDL_Init(sdl_flags) != 0:
            raise RuntimeError(f"SDL_Init failed: {sdl2.SDL_GetError()}")

        self.window = window_module.Window(title, width, height, resizable, vsync, visible, highdpi, multisample)
        self.input = input_module.InputManager()
        self.gamepads = input_module.GamepadManager()
        self.clock = time_module.Clock()
        self.events = EventBus()
        self.audio = AudioSystem() if enable_audio else None
        self.resources = ResourceManager(audio_system=self.audio)
        self.clear_color = clear_color or BLACK

        self.dpi_scale_x = 1.0
        self.dpi_scale_y = 1.0
        self._update_dpi_scale()

        gui.init(gui_font_path, gui_font_size, dpi_scale=self.dpi_scale_x)

        self._running = False
        self.max_frames = max_frames
        self._frame_count = 0

    def on_start(self):
        pass

    def on_update(self, delta_time):
        pass

    def on_render(self):
        pass

    def on_gui(self):
        pass

    def on_event(self, event):
        pass

    def on_resize(self, width, height):
        pass

    def on_shutdown(self):
        pass

    def quit(self):
        self._running = False

    def run(self):
        self._running = True
        self.on_start()
        try:
            while self._running:
                self._frame()
        finally:
            self._shutdown()

    def _update_dpi_scale(self):
        window_w, window_h = self.window.size()
        drawable_w, drawable_h = self.window.drawable_size()
        self.dpi_scale_x = (drawable_w / window_w) if window_w else 1.0
        self.dpi_scale_y = (drawable_h / window_h) if window_h else 1.0

    def _frame(self):
        self.input.begin_frame()

        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            self.input.handle_event(event)
            self.gamepads.handle_event(event)
            self.on_event(event)

        if self.input.quit_requested:
            self._running = False
            return

        if self.input.resized_size is not None:
            self._update_dpi_scale()
            self.on_resize(*self.input.resized_size)

        delta_time = self.clock.tick()

        self.on_update(delta_time)

        drawable_w, drawable_h = self.window.drawable_size()
        gl.set_viewport(0, 0, drawable_w, drawable_h)
        gl.clear(self.clear_color)

        self.on_render()

        gui.new_frame(self.input, drawable_w, drawable_h, delta_time, dpi_scale=(self.dpi_scale_x, self.dpi_scale_y))
        self.on_gui()
        gui.render()

        self.window.swap()

        self._frame_count += 1
        if self.max_frames is not None and self._frame_count >= self.max_frames:
            self._running = False

    def _shutdown(self):
        self.on_shutdown()
        gui.shutdown()
        self.resources.unload_all()
        if self.audio is not None:
            self.audio.shutdown()
        self.window.destroy()
        sdl2.SDL_Quit()
        log.info("SMRE application shut down cleanly")
