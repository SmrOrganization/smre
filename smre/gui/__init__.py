from ..graphics.font import Font
from ..input import Keys, MouseButton
from ..mathlib import Vec2
from .context import GUIContext, get_current_context, set_current_context
from .layout import (
    current_item_width, cursor_pos, dummy, pop_item_width, push_item_width,
    same_line, set_cursor_pos, spacing,
)
from .renderer import GuiRenderer
from .style import SMRStyle
from .widgets import (
    badge, begin_disabled, begin_main_menu_bar, begin_menu, button, checkbox,
    collapsing_header, color_edit3, combo, draw_toasts, drag_float, drag_int,
    end_disabled, end_main_menu_bar, end_menu, image, indent, input_text,
    is_item_hovered, label, measure_text, menu_item, plot_lines, pop_id, progress_bar,
    push_id, push_toast, radio_button, segmented_control, separator, set_tooltip,
    slider_float, slider_int, slider_labeled, text, text_disabled, text_disabled_wrapped,
    text_wrapped, tree_node, unindent,
)
from .window import begin_window, end_window

_renderer = None


def init(font_path=None, font_size=18, style=None):
    context = GUIContext()
    if style is not None:
        context.style = style
    context.font = Font.from_file(font_path, size=font_size)
    set_current_context(context)
    return context


def _get_renderer():
    global _renderer
    if _renderer is None:
        _renderer = GuiRenderer()
    return _renderer


def new_frame(input_manager, display_width, display_height, delta_time, dpi_scale=(1.0, 1.0)):
    context = get_current_context()
    io = context.io
    io.display_size = Vec2(float(display_width), float(display_height))
    io.delta_time = delta_time
    raw_mouse = input_manager.mouse_position()
    io.mouse_pos = Vec2(raw_mouse.x * dpi_scale[0], raw_mouse.y * dpi_scale[1])
    io.mouse_down = [
        input_manager.is_mouse_down(MouseButton.LEFT),
        input_manager.is_mouse_down(MouseButton.RIGHT),
        input_manager.is_mouse_down(MouseButton.MIDDLE),
    ]
    io.mouse_clicked = [
        input_manager.is_mouse_pressed(MouseButton.LEFT),
        input_manager.is_mouse_pressed(MouseButton.RIGHT),
        input_manager.is_mouse_pressed(MouseButton.MIDDLE),
    ]
    io.mouse_released = [
        input_manager.is_mouse_released(MouseButton.LEFT),
        input_manager.is_mouse_released(MouseButton.RIGHT),
        input_manager.is_mouse_released(MouseButton.MIDDLE),
    ]
    io.mouse_wheel = input_manager.mouse_wheel_y
    io.text_input = input_manager.text_input
    io.key_backspace = input_manager.is_key_pressed(Keys.BACKSPACE)
    io.key_delete = input_manager.is_key_pressed(Keys.DELETE)
    io.key_enter = input_manager.is_key_pressed(Keys.RETURN)
    io.key_left = input_manager.is_key_pressed(Keys.LEFT)
    io.key_right = input_manager.is_key_pressed(Keys.RIGHT)
    io.key_home = input_manager.is_key_pressed(Keys.HOME)
    io.key_end = input_manager.is_key_pressed(Keys.END)
    io.key_tab = input_manager.is_key_pressed(Keys.TAB)
    io.key_escape = input_manager.is_key_pressed(Keys.ESCAPE)
    context.new_frame()


def render():
    context = get_current_context()
    context.end_frame()
    draw_toasts(context)
    renderer = _get_renderer()
    renderer.render(context.draw_list, context.io.display_size.x, context.io.display_size.y)


def shutdown():
    global _renderer
    context = get_current_context()
    context.delete()
    if _renderer is not None:
        _renderer.delete()
        _renderer = None


def get_style():
    return get_current_context().style


def want_capture_mouse():
    context = get_current_context()
    return context._hovered_window_name is not None or context.active_id is not None


begin = begin_window
end = end_window

__all__ = [
    "init", "new_frame", "render", "shutdown",
    "get_style", "want_capture_mouse",
    "GUIContext", "SMRStyle",
    "begin_window", "end_window", "begin", "end",
    "text", "text_disabled", "text_wrapped", "text_disabled_wrapped", "label", "measure_text",
    "button", "checkbox", "radio_button",
    "slider_float", "slider_int", "slider_labeled", "drag_float", "drag_int",
    "input_text", "combo",
    "segmented_control", "badge",
    "progress_bar", "separator", "image",
    "indent", "unindent", "tree_node", "collapsing_header",
    "is_item_hovered", "set_tooltip",
    "color_edit3", "plot_lines",
    "begin_main_menu_bar", "end_main_menu_bar", "begin_menu", "end_menu", "menu_item",
    "same_line", "spacing", "dummy", "cursor_pos", "set_cursor_pos",
    "push_item_width", "pop_item_width", "current_item_width",
    "push_id", "pop_id",
    "begin_disabled", "end_disabled",
    "push_toast",
]
