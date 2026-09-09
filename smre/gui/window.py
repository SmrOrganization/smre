from ..mathlib import Vec2
from .context import get_current_context, point_in_rect
from .layout import begin_content_area

_MIN_WINDOW_SIZE = Vec2(120.0, 80.0)


def _as_vec2(value):
    if value is None:
        return None
    if isinstance(value, Vec2):
        return value
    return Vec2(value[0], value[1])


def begin_window(
    name, opened=True, position=None, size=None, size_ratio=None,
    min_size=None, max_size=None, closable=False, decorated=True, resizable=True,
    scrollable=True, corners=(True, True, True, True),
):
    context = get_current_context()
    style = context.style

    if size_ratio is not None:
        size = (
            context.io.display_size.x * size_ratio[0],
            context.io.display_size.y * size_ratio[1],
        )
    if size is not None and (min_size is not None or max_size is not None):
        size_x, size_y = size
        if min_size is not None:
            size_x = max(size_x, min_size[0])
            size_y = max(size_y, min_size[1])
        if max_size is not None:
            size_x = min(size_x, max_size[0])
            size_y = min(size_y, max_size[1])
        size = (size_x, size_y)

    context.next_window_position = _as_vec2(position)
    context.next_window_size = _as_vec2(size)

    slot = len(context.windows) % 8
    default_position = Vec2(60.0 + slot * 24.0, 60.0 + slot * 24.0)
    default_size = Vec2(320.0, 240.0)
    window = context.get_or_create_window(name, default_position, default_size)
    window.seen_this_frame = True
    window.decorated = decorated
    window.resizable = resizable
    window.scrollable = scrollable

    context.current_window = window
    context._window_stack.append(window)
    window.is_hovered_window = (context._hovered_window_name == name)

    title_bar_height = style.title_bar_height if decorated else 0.0
    mouse = context.io.mouse_pos
    still_opened = opened
    hovering_close = False

    if decorated:
        title_id = "window_title::" + name
        title_rect = (window.position.x, window.position.y, window.size.x, title_bar_height)

        close_size = 16.0
        close_rect = (
            window.position.x + window.size.x - close_size - 6.0,
            window.position.y + (title_bar_height - close_size) * 0.5,
            close_size, close_size,
        )

        collapse_size = 16.0
        collapse_rect = (
            window.position.x + 6.0,
            window.position.y + (title_bar_height - collapse_size) * 0.5,
            collapse_size, collapse_size,
        )

        hovering_close = closable and window.is_hovered_window and point_in_rect(mouse, close_rect)
        hovering_collapse = window.is_hovered_window and point_in_rect(mouse, collapse_rect)

        if hovering_close and context.io.mouse_clicked[0]:
            still_opened = False
        elif hovering_collapse and context.io.mouse_clicked[0]:
            window.collapsed = not window.collapsed
        elif (
            window.is_hovered_window
            and point_in_rect(mouse, title_rect)
            and not hovering_close
            and not hovering_collapse
            and context.io.mouse_clicked[0]
            and context.active_id is None
        ):
            context.set_active(title_id)
            context._drag_anchor_mouse = Vec2(mouse.x, mouse.y)
            context._drag_anchor_value = Vec2(window.position.x, window.position.y)

        if context.is_active(title_id) and context.io.mouse_down[0]:
            delta = Vec2(mouse.x - context._drag_anchor_mouse.x, mouse.y - context._drag_anchor_mouse.y)
            window.position = Vec2(context._drag_anchor_value.x + delta.x, context._drag_anchor_value.y + delta.y)
    else:
        window.collapsed = False

    window.position.x = max(-window.size.x + 40.0, min(window.position.x, context.io.display_size.x - 40.0))
    window.position.y = max(0.0, min(window.position.y, context.io.display_size.y - title_bar_height))

    draw_list = context.draw_list
    body_height = title_bar_height if window.collapsed else window.size.y
    window.last_rect = (window.position.x, window.position.y, window.size.x, body_height)

    draw_list.push_clip_rect(
        window.position.x - 4.0, window.position.y - 4.0,
        window.size.x + 8.0, body_height + 8.0, intersect=False,
    )

    if not window.collapsed:
        draw_list.add_rect_filled(window.position, window.size, style.window_bg_with_alpha(), rounding=style.window_rounding, corners=corners)
        draw_list.add_rect_outline(window.position, window.size, style.window_border, thickness=style.border_size, rounding=style.window_rounding, corners=corners)

    if decorated:
        title_color = style.title_bg_active if (window.is_hovered_window or context.is_active(title_id)) else style.title_bg
        title_corners = (corners[0], corners[1], False, False)
        draw_list.add_rect_filled(Vec2(window.position.x, window.position.y), Vec2(window.size.x, title_bar_height), title_color, rounding=style.window_rounding, corners=title_corners)

        if context.font is not None:
            draw_list.push_clip_rect(window.position.x, window.position.y, window.size.x, title_bar_height)
            text_x = window.position.x + collapse_size + 14.0
            text_y = window.position.y + (title_bar_height - context.font.line_height) * 0.5
            draw_list.add_text(context.font, name, Vec2(text_x, text_y), style.title_text)
            collapse_glyph = "+" if window.collapsed else "-"
            draw_list.add_text(context.font, collapse_glyph, Vec2(collapse_rect[0] + 4.0, collapse_rect[1]), style.text)
            if closable:
                close_color = style.button_active if hovering_close else style.text
                draw_list.add_text(context.font, "x", Vec2(close_rect[0] + 4.0, close_rect[1]), close_color)
            draw_list.pop_clip_rect()

    if window.collapsed:
        return False, still_opened

    content_x = window.position.x + style.window_padding.x
    content_y = window.position.y + title_bar_height + style.window_padding.y - window.scroll_y
    content_width = window.size.x - style.window_padding.x * 2.0

    draw_list.push_clip_rect(
        window.position.x + 1.0, window.position.y + title_bar_height,
        window.size.x - 2.0, window.size.y - title_bar_height - 1.0,
    )

    begin_content_area(context, content_x, content_y, content_width)
    window.content_start_y = content_y

    return True, still_opened


def end_window():
    context = get_current_context()
    window = context.current_window
    style = context.style
    if window is None:
        return

    title_bar_height = style.title_bar_height if window.decorated else 0.0

    if not window.collapsed:
        content_bottom = context.cursor_y
        used_height = max(0.0, content_bottom - window.content_start_y - style.item_spacing.y)
        visible_height = window.size.y - title_bar_height - style.window_padding.y * 2.0
        window.max_scroll_y = max(0.0, used_height - visible_height)

        if not window.scrollable:
            window.scroll_y = 0.0
        else:
            window.scroll_y = max(0.0, min(window.scroll_y, window.max_scroll_y))

            if window.is_hovered_window and context.io.mouse_wheel != 0.0 and window.max_scroll_y > 0.0:
                window.scroll_y -= context.io.mouse_wheel * 24.0
                window.scroll_y = max(0.0, min(window.scroll_y, window.max_scroll_y))

            if window.max_scroll_y > 0.0:
                _draw_scrollbar(context, window, title_bar_height)

        if window.resizable:
            _resize_grip(context, window)

        context.draw_list.pop_clip_rect()

    context.draw_list.pop_clip_rect()

    context._window_stack.pop()
    context.current_window = context._window_stack[-1] if context._window_stack else None


def _resize_grip(context, window):
    style = context.style
    resize_id = "window_resize::" + window.name
    grip_size = 14.0
    grip_rect = (
        window.position.x + window.size.x - grip_size,
        window.position.y + window.size.y - grip_size,
        grip_size, grip_size,
    )
    mouse = context.io.mouse_pos
    hovering_grip = window.is_hovered_window and point_in_rect(mouse, grip_rect)

    if hovering_grip and context.io.mouse_clicked[0] and context.active_id is None:
        context.set_active(resize_id)
        context._drag_anchor_mouse = Vec2(mouse.x, mouse.y)
        context._drag_anchor_value = Vec2(window.size.x, window.size.y)

    if context.is_active(resize_id) and context.io.mouse_down[0]:
        delta = Vec2(mouse.x - context._drag_anchor_mouse.x, mouse.y - context._drag_anchor_mouse.y)
        new_width = max(_MIN_WINDOW_SIZE.x, context._drag_anchor_value.x + delta.x)
        new_height = max(_MIN_WINDOW_SIZE.y, context._drag_anchor_value.y + delta.y)
        window.size = Vec2(new_width, new_height)

    grip_color = style.button_active if (hovering_grip or context.is_active(resize_id)) else style.window_border
    context.draw_list.add_triangle_filled(
        Vec2(grip_rect[0] + grip_size, grip_rect[1]),
        Vec2(grip_rect[0] + grip_size, grip_rect[1] + grip_size),
        Vec2(grip_rect[0], grip_rect[1] + grip_size),
        grip_color,
    )


def _draw_scrollbar(context, window, title_bar_height):
    style = context.style
    track_x = window.position.x + window.size.x - style.scrollbar_size - 2.0
    track_y = window.position.y + title_bar_height
    track_h = window.size.y - title_bar_height
    context.draw_list.add_rect_filled(Vec2(track_x, track_y), Vec2(style.scrollbar_size, track_h), style.scrollbar_bg)

    visible_ratio = min(1.0, track_h / (track_h + window.max_scroll_y))
    thumb_h = max(20.0, track_h * visible_ratio)
    scroll_ratio = window.scroll_y / window.max_scroll_y if window.max_scroll_y > 0.0 else 0.0
    thumb_y = track_y + (track_h - thumb_h) * scroll_ratio

    scrollbar_id = "scrollbar::" + window.name
    thumb_rect = (track_x, thumb_y, style.scrollbar_size, thumb_h)
    mouse = context.io.mouse_pos
    hovering_thumb = window.is_hovered_window and point_in_rect(mouse, thumb_rect)

    if hovering_thumb and context.io.mouse_clicked[0] and context.active_id is None:
        context.set_active(scrollbar_id)
        context._drag_anchor_mouse = Vec2(mouse.x, mouse.y)
        context._drag_anchor_value = window.scroll_y

    if context.is_active(scrollbar_id) and context.io.mouse_down[0]:
        delta_y = mouse.y - context._drag_anchor_mouse.y
        track_range = max(1.0, track_h - thumb_h)
        scroll_delta = delta_y / track_range * window.max_scroll_y
        window.scroll_y = max(0.0, min(context._drag_anchor_value + scroll_delta, window.max_scroll_y))

    color = style.scrollbar_grab
    if context.is_active(scrollbar_id):
        color = style.scrollbar_grab_active
    elif hovering_thumb:
        color = style.scrollbar_grab_hovered
    context.draw_list.add_rect_filled(Vec2(track_x, thumb_y), Vec2(style.scrollbar_size, thumb_h), color, rounding=3.0)
