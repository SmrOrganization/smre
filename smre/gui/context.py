from ..graphics.texture import Texture2D
from ..mathlib import Vec2
from .draw_list import DrawList
from .style import SMRStyle


class IO:
    def __init__(self):
        self.mouse_pos = Vec2.zero()
        self.mouse_down = [False, False, False]
        self.mouse_clicked = [False, False, False]
        self.mouse_released = [False, False, False]
        self.mouse_wheel = 0.0
        self.text_input = ""
        self.key_backspace = False
        self.key_delete = False
        self.key_enter = False
        self.key_left = False
        self.key_right = False
        self.key_home = False
        self.key_end = False
        self.key_tab = False
        self.key_escape = False
        self.delta_time = 1.0 / 60.0
        self.display_size = Vec2(1280.0, 720.0)


class WindowState:
    def __init__(self, name, position, size):
        self.name = name
        self.position = position
        self.size = size
        self.collapsed = False
        self.decorated = True
        self.resizable = True
        self.scrollable = True
        self.scroll_y = 0.0
        self.max_scroll_y = 0.0
        self.content_start_y = 0.0
        self.last_rect = (position.x, position.y, size.x, size.y)
        self.is_hovered_window = False
        self.seen_this_frame = False


def point_in_rect(point, rect):
    x, y, w, h = rect
    return x <= point.x <= x + w and y <= point.y <= y + h


class GUIContext:
    def __init__(self):
        self.style = SMRStyle()
        self.io = IO()
        self.white_texture = Texture2D.blank_white()
        self.draw_list = DrawList(self.white_texture)
        self.font = None

        self.windows = {}
        self.window_order = []
        self._hovered_window_name = None

        self.current_window = None
        self._window_stack = []

        self.id_stack = []
        self.hovered_id = None
        self.active_id = None
        self.active_id_window = None
        self.focused_id = None
        self.mouse_captured_offset = Vec2.zero()
        self._drag_anchor_mouse = Vec2.zero()
        self._drag_anchor_value = None

        self.frame_count = 0

        self.cursor_x = 0.0
        self.cursor_y = 0.0
        self.content_origin_x = 0.0
        self.content_region_x = 0.0
        self.line_height = 0.0
        self.prev_line_height = 0.0
        self.cursor_pos_prev_line = (0.0, 0.0)
        self.last_item_min = (0.0, 0.0)
        self.last_item_max = (0.0, 0.0)
        self._item_width_stack = [200.0]

        self.next_window_position = None
        self.next_window_size = None

        self.text_edit_state = {}

        self.tree_open_state = {}

        self.anim_state = {}

        self.disabled_stack = [False]

        self.toasts = []

        self.overlay_draws = []
        self.pending_tooltip = None

    def new_frame(self):
        self.frame_count += 1
        self.draw_list.reset((0.0, 0.0, self.io.display_size.x, self.io.display_size.y))
        self.overlay_draws = []
        self.pending_tooltip = None

        self._hovered_window_name = None
        for name in reversed(self.window_order):
            window = self.windows.get(name)
            if window is None or not window.seen_this_frame:
                continue
            if point_in_rect(self.io.mouse_pos, window.last_rect):
                self._hovered_window_name = name
                break

        for window in self.windows.values():
            window.seen_this_frame = False

        if self.io.mouse_clicked[0] and self._hovered_window_name is not None:
            self.focus_window(self._hovered_window_name)

        self.hovered_id = None

    def end_frame(self):
        if self.active_id is not None and not self.io.mouse_down[0]:
            self.active_id = None
            self.active_id_window = None

    def focus_window(self, name):
        if name in self.window_order:
            self.window_order.remove(name)
        self.window_order.append(name)

    def get_or_create_window(self, name, default_position, default_size):
        window = self.windows.get(name)
        if window is None:
            position = self.next_window_position or default_position
            size = self.next_window_size or default_size
            window = WindowState(name, position.copy(), size.copy())
            self.windows[name] = window
            self.window_order.append(name)
        else:
            if self.next_window_position is not None:
                window.position = self.next_window_position
            if self.next_window_size is not None:
                window.size = self.next_window_size
        self.next_window_position = None
        self.next_window_size = None
        return window

    def push_overlay(self, draw_fn):
        self.overlay_draws.append(draw_fn)

    def push_id(self, value):
        self.id_stack.append(str(value))

    def pop_id(self):
        if self.id_stack:
            self.id_stack.pop()

    def make_id(self, label):
        window_name = self.current_window.name if self.current_window else ""
        return window_name + "/" + "/".join(self.id_stack) + "/" + label

    def set_hovered(self, widget_id, rect):
        if self.disabled_stack[-1]:
            return False
        if self.current_window is None or not self.current_window.is_hovered_window:
            return False
        if not point_in_rect(self.io.mouse_pos, rect):
            return False
        if self.active_id is not None and self.active_id != widget_id:
            return False
        self.hovered_id = widget_id
        return True

    def begin_disabled(self, disabled=True):
        self.disabled_stack.append(disabled or self.disabled_stack[-1])

    def end_disabled(self):
        if len(self.disabled_stack) > 1:
            self.disabled_stack.pop()

    def is_disabled(self):
        return self.disabled_stack[-1]

    def dim(self, color):
        if not self.disabled_stack[-1]:
            return color
        return color.with_alpha(color.a * self.style.disabled_alpha)

    def animate(self, widget_id, target, duration=None):
        seconds = duration if duration is not None else self.style.hover_transition_seconds
        current = self.anim_state.get(widget_id, target)
        if seconds <= 0.0:
            new_value = target
        else:
            t = min(1.0, self.io.delta_time / seconds)
            new_value = current + (target - current) * t
            if abs(new_value - target) < 0.01:
                new_value = target
        self.anim_state[widget_id] = new_value
        return new_value

    def push_toast(self, message, duration=2.5, color=None):
        self.toasts.append({"message": message, "remaining": duration, "duration": duration, "color": color})

    def set_active(self, widget_id):
        self.active_id = widget_id
        self.active_id_window = self.current_window.name if self.current_window else None

    def clear_active(self):
        self.active_id = None
        self.active_id_window = None

    def is_active(self, widget_id):
        return self.active_id == widget_id

    def is_hovered(self, widget_id):
        return self.hovered_id == widget_id

    def set_focused(self, widget_id):
        self.focused_id = widget_id

    def clear_focused(self):
        self.focused_id = None

    def is_focused(self, widget_id):
        return self.focused_id == widget_id

    def delete(self):
        if self.font is not None:
            self.font.delete()
        self.white_texture.delete()


_current_context = None


def get_current_context():
    global _current_context
    if _current_context is None:
        _current_context = GUIContext()
    return _current_context


def set_current_context(context):
    global _current_context
    _current_context = context
