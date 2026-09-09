import ctypes

import sdl2

from .mathlib import Vec2


class Keys:
    A = sdl2.SDLK_a
    B = sdl2.SDLK_b
    C = sdl2.SDLK_c
    D = sdl2.SDLK_d
    E = sdl2.SDLK_e
    F = sdl2.SDLK_f
    G = sdl2.SDLK_g
    H = sdl2.SDLK_h
    I = sdl2.SDLK_i
    J = sdl2.SDLK_j
    K = sdl2.SDLK_k
    L = sdl2.SDLK_l
    M = sdl2.SDLK_m
    N = sdl2.SDLK_n
    O = sdl2.SDLK_o
    P = sdl2.SDLK_p
    Q = sdl2.SDLK_q
    R = sdl2.SDLK_r
    S = sdl2.SDLK_s
    T = sdl2.SDLK_t
    U = sdl2.SDLK_u
    V = sdl2.SDLK_v
    W = sdl2.SDLK_w
    X = sdl2.SDLK_x
    Y = sdl2.SDLK_y
    Z = sdl2.SDLK_z
    NUM_0 = sdl2.SDLK_0
    NUM_1 = sdl2.SDLK_1
    NUM_2 = sdl2.SDLK_2
    NUM_3 = sdl2.SDLK_3
    NUM_4 = sdl2.SDLK_4
    NUM_5 = sdl2.SDLK_5
    NUM_6 = sdl2.SDLK_6
    NUM_7 = sdl2.SDLK_7
    NUM_8 = sdl2.SDLK_8
    NUM_9 = sdl2.SDLK_9
    SPACE = sdl2.SDLK_SPACE
    ESCAPE = sdl2.SDLK_ESCAPE
    RETURN = sdl2.SDLK_RETURN
    TAB = sdl2.SDLK_TAB
    BACKSPACE = sdl2.SDLK_BACKSPACE
    DELETE = sdl2.SDLK_DELETE
    LEFT = sdl2.SDLK_LEFT
    RIGHT = sdl2.SDLK_RIGHT
    UP = sdl2.SDLK_UP
    DOWN = sdl2.SDLK_DOWN
    LSHIFT = sdl2.SDLK_LSHIFT
    RSHIFT = sdl2.SDLK_RSHIFT
    LCTRL = sdl2.SDLK_LCTRL
    RCTRL = sdl2.SDLK_RCTRL
    LALT = sdl2.SDLK_LALT
    RALT = sdl2.SDLK_RALT
    HOME = sdl2.SDLK_HOME
    END = sdl2.SDLK_END


class MouseButton:
    LEFT = sdl2.SDL_BUTTON_LEFT
    MIDDLE = sdl2.SDL_BUTTON_MIDDLE
    RIGHT = sdl2.SDL_BUTTON_RIGHT


class InputManager:
    def __init__(self):
        self.keys_down = set()
        self.keys_pressed = set()
        self.keys_released = set()
        self.mouse_buttons_down = set()
        self.mouse_buttons_pressed = set()
        self.mouse_buttons_released = set()
        self.mouse_x = 0.0
        self.mouse_y = 0.0
        self.mouse_dx = 0.0
        self.mouse_dy = 0.0
        self.mouse_wheel_y = 0.0
        self.text_input = ""
        self.quit_requested = False
        self.resized_size = None
        sdl2.SDL_StartTextInput()

    def begin_frame(self):
        self.keys_pressed.clear()
        self.keys_released.clear()
        self.mouse_buttons_pressed.clear()
        self.mouse_buttons_released.clear()
        self.mouse_dx = 0.0
        self.mouse_dy = 0.0
        self.mouse_wheel_y = 0.0
        self.text_input = ""
        self.resized_size = None

    def handle_event(self, event):
        event_type = event.type
        if event_type == sdl2.SDL_QUIT:
            self.quit_requested = True
        elif event_type == sdl2.SDL_KEYDOWN:
            key = event.key.keysym.sym
            if key not in self.keys_down:
                self.keys_pressed.add(key)
            self.keys_down.add(key)
        elif event_type == sdl2.SDL_KEYUP:
            key = event.key.keysym.sym
            self.keys_down.discard(key)
            self.keys_released.add(key)
        elif event_type == sdl2.SDL_MOUSEMOTION:
            self.mouse_x = float(event.motion.x)
            self.mouse_y = float(event.motion.y)
            self.mouse_dx += float(event.motion.xrel)
            self.mouse_dy += float(event.motion.yrel)
        elif event_type == sdl2.SDL_MOUSEBUTTONDOWN:
            button = event.button.button
            self.mouse_buttons_down.add(button)
            self.mouse_buttons_pressed.add(button)
        elif event_type == sdl2.SDL_MOUSEBUTTONUP:
            button = event.button.button
            self.mouse_buttons_down.discard(button)
            self.mouse_buttons_released.add(button)
        elif event_type == sdl2.SDL_MOUSEWHEEL:
            self.mouse_wheel_y += float(event.wheel.y)
        elif event_type == sdl2.SDL_TEXTINPUT:
            self.text_input += ctypes.string_at(event.text.text).decode("utf-8", errors="ignore")
        elif event_type == sdl2.SDL_WINDOWEVENT:
            if event.window.event == sdl2.SDL_WINDOWEVENT_RESIZED:
                self.resized_size = (event.window.data1, event.window.data2)

    def is_key_down(self, key):
        return key in self.keys_down

    def is_key_pressed(self, key):
        return key in self.keys_pressed

    def is_key_released(self, key):
        return key in self.keys_released

    def is_mouse_down(self, button):
        return button in self.mouse_buttons_down

    def is_mouse_pressed(self, button):
        return button in self.mouse_buttons_pressed

    def is_mouse_released(self, button):
        return button in self.mouse_buttons_released

    def mouse_position(self):
        return Vec2(self.mouse_x, self.mouse_y)


class Gamepad:
    def __init__(self, controller_ptr, joystick_id):
        self.controller_ptr = controller_ptr
        self.joystick_id = joystick_id

    def is_button_down(self, button):
        return bool(sdl2.SDL_GameControllerGetButton(self.controller_ptr, button))

    def axis(self, axis_id):
        raw = sdl2.SDL_GameControllerGetAxis(self.controller_ptr, axis_id)
        return max(-1.0, min(1.0, raw / 32767.0))

    def close(self):
        sdl2.SDL_GameControllerClose(self.controller_ptr)


class GamepadManager:
    def __init__(self):
        self.gamepads = {}

    def handle_event(self, event):
        if event.type == sdl2.SDL_CONTROLLERDEVICEADDED:
            index = event.cdevice.which
            if sdl2.SDL_IsGameController(index):
                controller_ptr = sdl2.SDL_GameControllerOpen(index)
                joystick = sdl2.SDL_GameControllerGetJoystick(controller_ptr)
                instance_id = sdl2.SDL_JoystickInstanceID(joystick)
                self.gamepads[instance_id] = Gamepad(controller_ptr, instance_id)
        elif event.type == sdl2.SDL_CONTROLLERDEVICEREMOVED:
            instance_id = event.cdevice.which
            gamepad = self.gamepads.pop(instance_id, None)
            if gamepad:
                gamepad.close()

    def first(self):
        if not self.gamepads:
            return None
        return next(iter(self.gamepads.values()))
