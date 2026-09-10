from ..graphics.color import WHITE, Color
from ..mathlib import Vec2
from .context import get_current_context, point_in_rect
from .layout import current_item_width, end_item, item_position

def _menu_bar_height(style):
    return style.scaled(24.0)


def _display_label(label_text):
    index = label_text.find("##")
    return label_text[:index] if index != -1 else label_text


def push_id(value):
    get_current_context().push_id(value)


def pop_id():
    get_current_context().pop_id()


def text(value, color=None, font=None):
    context = get_current_context()
    style = context.style
    x, y = item_position(context)
    display = str(value)
    active_font = font or context.font
    if active_font is not None:
        width, height = active_font.measure(display)
        context.draw_list.add_text(active_font, display, Vec2(x, y), context.dim(color or style.text))
    else:
        width, height = 0.0, 16.0
    end_item(context, x, y, width, height)


def measure_text(value, font=None):
    context = get_current_context()
    active_font = font or context.font
    if active_font is None:
        return (0.0, 16.0)
    return active_font.measure(str(value))


def text_disabled(value):
    context = get_current_context()
    text(value, context.style.text_disabled)


def _wrap_text_lines(font, value, max_width):
    lines = []
    for paragraph in value.split("\n"):
        words = paragraph.split(" ")
        current_line = ""
        for word in words:
            candidate = word if not current_line else current_line + " " + word
            width, _ = font.measure(candidate)
            if width <= max_width or not current_line:
                current_line = candidate
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
    return lines


def text_wrapped(value, width=None, color=None, font=None):
    context = get_current_context()
    style = context.style
    x, y = item_position(context)
    active_font = font or context.font
    display = str(value)

    if active_font is None:
        end_item(context, x, y, 0.0, 16.0)
        return

    max_width = width if width is not None else current_item_width()
    lines = _wrap_text_lines(active_font, display, max_width)
    line_height = active_font.line_height
    text_color = context.dim(color or style.text)
    for i, line in enumerate(lines):
        context.draw_list.add_text(active_font, line, Vec2(x, y + i * line_height), text_color)

    total_height = line_height * max(1, len(lines))
    end_item(context, x, y, max_width, total_height)


def text_disabled_wrapped(value, width=None):
    context = get_current_context()
    text_wrapped(value, width, context.style.text_disabled)


def label(value, color=None):
    text(value, color)


def button(label_text, width=None, height=None):
    context = get_current_context()
    style = context.style
    widget_id = context.make_id(label_text)
    display = _display_label(label_text)

    x, y = item_position(context)
    text_w, text_h = context.font.measure(display) if context.font is not None else (60.0, 16.0)
    w = width if width is not None else text_w + style.frame_padding.x * 2.0
    h = height if height is not None else text_h + style.frame_padding.y * 2.0

    rect = (x, y, w, h)
    hovered = context.set_hovered(widget_id, rect)
    clicked = False

    if hovered and context.io.mouse_clicked[0] and context.active_id is None:
        context.set_active(widget_id)
    if context.is_active(widget_id) and context.io.mouse_released[0]:
        if hovered:
            clicked = True
        context.clear_active()

    hover_t = context.animate(widget_id, 1.0 if hovered else 0.0)
    press_t = context.animate(widget_id + "::press", 1.0 if context.is_active(widget_id) else 0.0, duration=style.anim_press_seconds)

    if context.is_active(widget_id):
        color, text_color = style.button_active, style.button_active_text
    else:
        color = style.button.lerp(style.button_hovered, hover_t)
        text_color = style.text

    color = context.dim(color)
    text_color = context.dim(text_color)

    inset = press_t * style.scaled(2.0)
    context.draw_list.add_rect_filled(Vec2(x + inset, y + inset), Vec2(w - inset * 2.0, h - inset * 2.0), color, rounding=style.frame_rounding)
    if context.font is not None:
        text_x = x + (w - text_w) * 0.5
        text_y = y + (h - text_h) * 0.5
        context.draw_list.add_text(context.font, display, Vec2(text_x, text_y), text_color)

    end_item(context, x, y, w, h)
    return clicked


def checkbox(label_text, value):
    context = get_current_context()
    style = context.style
    widget_id = context.make_id(label_text)
    display = _display_label(label_text)

    box_size = style.scaled(18.0)
    x, y = item_position(context)
    text_w, text_h = context.font.measure(display) if (context.font is not None and display) else (0.0, 16.0)
    h = max(box_size, text_h)
    total_w = box_size + (style.scaled(8.0) + text_w if display else 0.0)
    rect = (x, y, total_w, h)
    hovered = context.set_hovered(widget_id, rect)
    changed = False

    if hovered and context.io.mouse_clicked[0] and context.active_id is None:
        context.set_active(widget_id)
    if context.is_active(widget_id) and context.io.mouse_released[0]:
        if hovered:
            value = not value
            changed = True
        context.clear_active()

    hover_t = context.animate(widget_id, 1.0 if hovered else 0.0)
    check_t = context.animate(widget_id + "::check", 1.0 if value else 0.0, duration=style.anim_value_seconds)

    box_y = y + (h - box_size) * 0.5
    if context.is_active(widget_id):
        box_color = style.frame_bg_active
    else:
        box_color = style.frame_bg.lerp(style.frame_bg_hovered, hover_t)
    box_color = context.dim(box_color)
    border_color = context.dim(style.window_border.lerp(style.slider_grab, check_t))
    context.draw_list.add_rect_filled(Vec2(x, box_y), Vec2(box_size, box_size), box_color, rounding=style.frame_rounding)
    context.draw_list.add_rect_outline(Vec2(x, box_y), Vec2(box_size, box_size), border_color, 1.0, rounding=style.frame_rounding)
    if check_t > 0.001:
        pad = style.scaled(4.0)
        inner = box_size - 2.0 * pad
        mark_size = inner * check_t
        mark_offset = (inner - mark_size) * 0.5
        context.draw_list.add_rect_filled(
            Vec2(x + pad + mark_offset, box_y + pad + mark_offset), Vec2(mark_size, mark_size),
            context.dim(style.checkmark), rounding=1.0,
        )

    if context.font is not None and display:
        text_y = y + (h - text_h) * 0.5
        context.draw_list.add_text(context.font, display, Vec2(x + box_size + style.scaled(8.0), text_y), context.dim(style.text))

    end_item(context, x, y, total_w, h)
    return changed, value


def radio_button(label_text, active):
    context = get_current_context()
    style = context.style
    widget_id = context.make_id(label_text)
    display = _display_label(label_text)

    circle_size = style.scaled(18.0)
    x, y = item_position(context)
    text_w, text_h = context.font.measure(display) if (context.font is not None and display) else (0.0, 16.0)
    h = max(circle_size, text_h)
    total_w = circle_size + (style.scaled(8.0) + text_w if display else 0.0)
    rect = (x, y, total_w, h)
    hovered = context.set_hovered(widget_id, rect)
    clicked = False

    if hovered and context.io.mouse_clicked[0] and context.active_id is None:
        context.set_active(widget_id)
    if context.is_active(widget_id) and context.io.mouse_released[0]:
        if hovered:
            clicked = True
        context.clear_active()

    hover_t = context.animate(widget_id, 1.0 if hovered else 0.0)
    dot_t = context.animate(widget_id + "::dot", 1.0 if active else 0.0, duration=style.anim_value_seconds)

    center = Vec2(x + circle_size * 0.5, y + h * 0.5)
    if context.is_active(widget_id):
        ring_color = style.frame_bg_active
    else:
        ring_color = style.frame_bg.lerp(style.frame_bg_hovered, hover_t)
    context.draw_list.add_circle_filled(center, circle_size * 0.5, context.dim(ring_color), segments=20)
    if dot_t > 0.001:
        context.draw_list.add_circle_filled(center, circle_size * 0.28 * dot_t, context.dim(style.checkmark), segments=16)

    if context.font is not None and display:
        text_y = y + (h - text_h) * 0.5
        context.draw_list.add_text(context.font, display, Vec2(x + circle_size + style.scaled(8.0), text_y), context.dim(style.text))

    end_item(context, x, y, total_w, h)
    return clicked


def slider_float(label_text, value, min_value, max_value, width=None, value_format="{:.3f}"):
    context = get_current_context()
    style = context.style
    widget_id = context.make_id(label_text)
    display = _display_label(label_text)

    x, y = item_position(context)
    w = width if width is not None else current_item_width()
    h = style.scaled(20.0)
    rect = (x, y, w, h)
    hovered = context.set_hovered(widget_id, rect)
    changed = False

    if hovered and context.io.mouse_clicked[0] and context.active_id is None:
        context.set_active(widget_id)

    if context.is_active(widget_id) and context.io.mouse_down[0]:
        t = (context.io.mouse_pos.x - x) / max(1.0, w)
        t = max(0.0, min(1.0, t))
        new_value = min_value + t * (max_value - min_value)
        if new_value != value:
            value = new_value
            changed = True

    hover_t = context.animate(widget_id, 1.0 if hovered else 0.0)

    if context.is_active(widget_id):
        bg_color = style.frame_bg_active
    else:
        bg_color = style.frame_bg.lerp(style.frame_bg_hovered, hover_t)
    context.draw_list.add_rect_filled(Vec2(x, y), Vec2(w, h), context.dim(bg_color), rounding=style.frame_rounding)

    t = 0.0 if max_value == min_value else (value - min_value) / (max_value - min_value)
    t = max(0.0, min(1.0, t))
    grab_w = style.scaled(8.0)
    grab_margin = style.scaled(2.0)
    target_grab_x = x + t * (w - grab_w)
    is_dragging = context.is_active(widget_id) and context.io.mouse_down[0]
    grab_x = target_grab_x if is_dragging else context.animate(widget_id + "::grabx", target_grab_x, duration=style.anim_value_seconds)
    grab_color = style.slider_grab_active if context.is_active(widget_id) else style.slider_grab
    context.draw_list.add_rect_filled(Vec2(grab_x, y + grab_margin), Vec2(grab_w, h - grab_margin * 2.0), context.dim(grab_color), rounding=style.frame_rounding)

    if context.font is not None:
        text_value = f"{display}: {value_format.format(value)}" if display else value_format.format(value)
        text_w, text_h = context.font.measure(text_value)
        context.draw_list.add_text(context.font, text_value, Vec2(x + (w - text_w) * 0.5, y + (h - text_h) * 0.5), context.dim(style.text))

    end_item(context, x, y, w, h)
    return changed, value


def slider_int(label_text, value, min_value, max_value, width=None):
    changed, new_value = slider_float(label_text, float(value), float(min_value), float(max_value), width, value_format="{:.0f}")
    return changed, int(round(new_value))


def slider_labeled(label_text, value, min_value, max_value, width=None, value_format="{:.2f}", suffix=""):
    context = get_current_context()
    style = context.style
    widget_id = context.make_id(label_text)

    x, y = item_position(context)
    w = width if width is not None else current_item_width()
    label_h = context.font.line_height if context.font is not None else 16.0
    grab_r = style.scaled(7.0)
    track_h = style.scaled(6.0)
    gap = style.scaled(10.0)
    row_h = max(track_h, grab_r * 2.0)
    h = label_h + gap + row_h

    track_y = y + label_h + gap + (row_h - track_h) * 0.5
    hit_rect = (x, track_y - grab_r, w, track_h + grab_r * 2.0)
    hovered = context.set_hovered(widget_id, hit_rect)
    changed = False

    if hovered and context.io.mouse_clicked[0] and context.active_id is None:
        context.set_active(widget_id)
    if context.is_active(widget_id) and context.io.mouse_down[0]:
        t = (context.io.mouse_pos.x - x) / max(1.0, w)
        t = max(0.0, min(1.0, t))
        new_value = min_value + t * (max_value - min_value)
        if new_value != value:
            value = new_value
            changed = True

    hover_t = context.animate(widget_id, 1.0 if (hovered or context.is_active(widget_id)) else 0.0)

    if context.font is not None:
        context.draw_list.add_text(context.font, label_text, Vec2(x, y), context.dim(style.text))
        value_text = value_format.format(value) + suffix
        value_w, _ = context.font.measure(value_text)
        context.draw_list.add_text(context.font, value_text, Vec2(x + w - value_w, y), context.dim(style.text))

    context.draw_list.add_rect_filled(Vec2(x, track_y), Vec2(w, track_h), context.dim(style.frame_bg), rounding=track_h * 0.5)

    t = 0.0 if max_value == min_value else (value - min_value) / (max_value - min_value)
    t = max(0.0, min(1.0, t))
    target_fill_w = w * t
    is_dragging = context.is_active(widget_id) and context.io.mouse_down[0]
    fill_w = target_fill_w if is_dragging else context.animate(widget_id + "::fillw", target_fill_w, duration=style.anim_value_seconds)
    if fill_w > 0.0:
        context.draw_list.add_rect_filled(Vec2(x, track_y), Vec2(fill_w, track_h), context.dim(style.button_active), rounding=track_h * 0.5)

    grab_center = Vec2(x + fill_w, track_y + track_h * 0.5)
    grab_radius = grab_r * (0.88 + 0.12 * hover_t)
    context.draw_list.add_circle_filled(grab_center, grab_radius, context.dim(style.button_active), segments=18)
    context.draw_list.add_circle_filled(grab_center, grab_radius * 0.42, context.dim(style.window_bg_with_alpha()), segments=14)

    end_item(context, x, y, w, h)
    return changed, value


def input_text(label_text, text_value, max_length=256, width=None):
    context = get_current_context()
    style = context.style
    widget_id = context.make_id(label_text)
    display = _display_label(label_text)

    x, y = item_position(context)
    w = width if width is not None else current_item_width()
    h = (context.font.line_height if context.font is not None else 18.0) + style.frame_padding.y * 2.0
    rect = (x, y, w, h)
    hovered = context.set_hovered(widget_id, rect)

    state = context.text_edit_state.get(widget_id)
    if state is None:
        state = {"caret": len(text_value)}
        context.text_edit_state[widget_id] = state

    if hovered and context.io.mouse_clicked[0] and context.active_id is None:
        context.set_focused(widget_id)
        state["caret"] = len(text_value)

    if context.is_focused(widget_id) and context.io.mouse_clicked[0] and not hovered:
        context.clear_focused()

    changed = False
    if context.is_focused(widget_id):
        caret = state["caret"]
        if context.io.text_input:
            insert = context.io.text_input
            if len(text_value) + len(insert) <= max_length:
                text_value = text_value[:caret] + insert + text_value[caret:]
                caret += len(insert)
                changed = True
        if context.io.key_backspace and caret > 0:
            text_value = text_value[:caret - 1] + text_value[caret:]
            caret -= 1
            changed = True
        if context.io.key_delete and caret < len(text_value):
            text_value = text_value[:caret] + text_value[caret + 1:]
            changed = True
        if context.io.key_left and caret > 0:
            caret -= 1
        if context.io.key_right and caret < len(text_value):
            caret += 1
        if context.io.key_home:
            caret = 0
        if context.io.key_end:
            caret = len(text_value)
        state["caret"] = max(0, min(caret, len(text_value)))

    focus_t = context.animate(widget_id + "::focus", 1.0 if context.is_focused(widget_id) else 0.0, duration=style.anim_value_seconds)
    hover_t = context.animate(widget_id, 1.0 if (hovered and not context.is_focused(widget_id)) else 0.0)
    bg_color = style.frame_bg.lerp(style.frame_bg_hovered, hover_t).lerp(style.frame_bg_active, focus_t)
    outline_color = style.window_border.lerp(style.slider_grab, focus_t)
    context.draw_list.add_rect_filled(Vec2(x, y), Vec2(w, h), bg_color, rounding=style.frame_rounding)
    context.draw_list.add_rect_outline(Vec2(x, y), Vec2(w, h), outline_color, 1.0, rounding=style.frame_rounding)

    label_w = 0.0
    if context.font is not None:
        text_x = x + style.frame_padding.x
        text_y = y + style.frame_padding.y
        context.draw_list.push_clip_rect(x, y, w, h)
        context.draw_list.add_text(context.font, text_value, Vec2(text_x, text_y), style.text)
        if context.is_focused(widget_id) and (context.frame_count // 30) % 2 == 0:
            caret_x = text_x + context.font.measure(text_value[:state["caret"]])[0]
            context.draw_list.add_line(Vec2(caret_x, text_y), Vec2(caret_x, text_y + context.font.line_height), style.text, 1.0)
        context.draw_list.pop_clip_rect()
        if display:
            label_gap = style.scaled(8.0)
            label_w, _ = context.font.measure(display)
            context.draw_list.add_text(context.font, display, Vec2(x + w + label_gap, y + style.frame_padding.y), style.text)

    end_item(context, x, y, w + (style.scaled(8.0) + label_w if display else 0.0), h)
    return changed, text_value


def combo(label_text, items, current_index, width=None):
    context = get_current_context()
    style = context.style
    widget_id = context.make_id(label_text)

    x, y = item_position(context)
    w = width if width is not None else current_item_width()
    h = (context.font.line_height if context.font is not None else 18.0) + style.frame_padding.y * 2.0
    rect = (x, y, w, h)
    hovered = context.set_hovered(widget_id, rect)
    changed = False

    if hovered and context.io.mouse_clicked[0] and context.active_id is None:
        if context.is_focused(widget_id):
            context.clear_focused()
        else:
            context.set_focused(widget_id)

    hover_t = context.animate(widget_id, 1.0 if hovered else 0.0)
    if context.is_focused(widget_id):
        bg_color = style.frame_bg_active
    else:
        bg_color = style.frame_bg.lerp(style.frame_bg_hovered, hover_t)
    context.draw_list.add_rect_filled(Vec2(x, y), Vec2(w, h), bg_color, rounding=style.frame_rounding)
    context.draw_list.add_rect_outline(Vec2(x, y), Vec2(w, h), style.window_border, 1.0, rounding=style.frame_rounding)

    current_label = items[current_index] if 0 <= current_index < len(items) else ""
    if context.font is not None:
        arrow_gutter = style.scaled(20.0)
        context.draw_list.push_clip_rect(x, y, w - arrow_gutter, h)
        context.draw_list.add_text(context.font, current_label, Vec2(x + style.frame_padding.x, y + style.frame_padding.y), style.text)
        context.draw_list.pop_clip_rect()
        context.draw_list.add_text(context.font, "v", Vec2(x + w - style.scaled(18.0), y + style.frame_padding.y), style.text)

    is_open = context.is_focused(widget_id)
    if is_open:
        popup_t = context.animate(widget_id + "::popup", 1.0, duration=style.anim_popup_seconds)
        slide = (1.0 - popup_t) * style.scaled(6.0)
        item_h = h
        popup_y = y + h
        mouse = context.io.mouse_pos
        item_hovered_flags = []
        for i, item_text in enumerate(items):
            item_y = popup_y + i * item_h - slide
            item_rect = (x, item_y, w, item_h)
            item_hovered = point_in_rect(mouse, item_rect)
            item_hovered_flags.append(item_hovered)
            if item_hovered and context.io.mouse_clicked[0]:
                current_index = i
                changed = True

        def draw_popup():
            draw_list = context.draw_list
            draw_list.push_clip_rect(x, popup_y, w, item_h * len(items) + style.scaled(4.0), intersect=False)
            for i, item_text in enumerate(items):
                item_y = popup_y + i * item_h - slide
                row_color = style.header_hovered if item_hovered_flags[i] else style.frame_bg
                draw_list.add_rect_filled(Vec2(x, item_y), Vec2(w, item_h), row_color.with_alpha(row_color.a * popup_t))
                if context.font is not None:
                    text_color = style.text.with_alpha(popup_t)
                    draw_list.add_text(context.font, item_text, Vec2(x + style.frame_padding.x, item_y + style.frame_padding.y), text_color)
            draw_list.pop_clip_rect()

        context.push_overlay(draw_popup)

        popup_rect = (x, popup_y, w, item_h * len(items))
        clicked_outside = context.io.mouse_clicked[0] and not hovered and not point_in_rect(mouse, popup_rect)
        if changed or clicked_outside:
            context.clear_focused()
    else:
        context.anim_state.pop(widget_id + "::popup", None)

    end_item(context, x, y, w, h)
    return changed, current_index


def progress_bar(fraction, width=None, overlay_text=None, label="progress_bar"):
    context = get_current_context()
    style = context.style
    widget_id = context.make_id(label)
    x, y = item_position(context)
    w = width if width is not None else current_item_width()
    h = style.scaled(20.0)
    target_fraction = max(0.0, min(1.0, fraction))
    fraction = context.animate(widget_id, target_fraction, duration=style.anim_value_seconds)
    context.draw_list.add_rect_filled(Vec2(x, y), Vec2(w, h), style.frame_bg, rounding=style.frame_rounding)
    if fraction > 0.0:
        context.draw_list.add_rect_filled(Vec2(x, y), Vec2(w * fraction, h), style.button_active, rounding=style.frame_rounding)
    if context.font is not None:
        text_value = overlay_text if overlay_text is not None else f"{int(fraction * 100)}%"
        text_w, text_h = context.font.measure(text_value)
        text_color = style.button_active_text if fraction > 0.5 else style.text
        context.draw_list.add_text(context.font, text_value, Vec2(x + (w - text_w) * 0.5, y + (h - text_h) * 0.5), text_color)
    end_item(context, x, y, w, h)


def separator():
    context = get_current_context()
    style = context.style
    x, y = item_position(context)
    w = context.content_region_x
    half = style.scaled(4.0)
    context.draw_list.add_line(Vec2(x, y + half), Vec2(x + w, y + half), style.separator, 1.0)
    end_item(context, x, y, w, half * 2.0)


def image(texture, width, height, tint=None):
    context = get_current_context()
    x, y = item_position(context)
    context.draw_list.add_image(texture, Vec2(x, y), Vec2(width, height), color=tint or WHITE)
    end_item(context, x, y, width, height)


def indent(amount=None):
    context = get_current_context()
    delta = amount if amount is not None else context.style.indent_spacing
    context.content_origin_x += delta
    context.cursor_x += delta


def unindent(amount=None):
    context = get_current_context()
    delta = amount if amount is not None else context.style.indent_spacing
    context.content_origin_x -= delta
    context.cursor_x -= delta


def tree_node(label_text, default_open=False):
    context = get_current_context()
    style = context.style
    widget_id = context.make_id(label_text)
    display = _display_label(label_text)
    if widget_id not in context.tree_open_state:
        context.tree_open_state[widget_id] = default_open
    is_open = context.tree_open_state[widget_id]

    x, y = item_position(context)
    text_w, text_h = context.font.measure(display) if context.font is not None else (0.0, 16.0)
    h = max(style.scaled(18.0), text_h)
    w = context.content_region_x
    rect = (x, y, w, h)
    hovered = context.set_hovered(widget_id, rect)

    if hovered and context.io.mouse_clicked[0] and context.active_id is None:
        is_open = not is_open
        context.tree_open_state[widget_id] = is_open

    hover_t = context.animate(widget_id + "::hover", 1.0 if hovered else 0.0)
    if hover_t > 0.001:
        context.draw_list.add_rect_filled(Vec2(x, y), Vec2(w, h), style.header_hovered.with_alpha(style.header_hovered.a * hover_t), rounding=style.frame_rounding)

    if context.font is not None:
        arrow = "v" if is_open else ">"
        context.draw_list.add_text(context.font, arrow, Vec2(x, y), style.text)
        context.draw_list.add_text(context.font, display, Vec2(x + style.scaled(16.0), y), style.text)

    end_item(context, x, y, w, h)
    return is_open


def collapsing_header(label_text, default_open=False):
    context = get_current_context()
    style = context.style
    widget_id = context.make_id(label_text)
    display = _display_label(label_text)
    if widget_id not in context.tree_open_state:
        context.tree_open_state[widget_id] = default_open
    is_open = context.tree_open_state[widget_id]

    x, y = item_position(context)
    w = context.content_region_x
    h = (context.font.line_height if context.font is not None else 16.0) + style.frame_padding.y * 2.0
    rect = (x, y, w, h)
    hovered = context.set_hovered(widget_id, rect)

    if hovered and context.io.mouse_clicked[0] and context.active_id is None:
        is_open = not is_open
        context.tree_open_state[widget_id] = is_open

    open_t = context.animate(widget_id + "::open", 1.0 if is_open else 0.0, duration=style.anim_value_seconds)
    hover_t = context.animate(widget_id + "::hover", 1.0 if (hovered and not is_open) else 0.0)
    color = style.header.lerp(style.header_hovered, hover_t).lerp(style.header_active, open_t)
    text_color = style.text.lerp(style.header_active_text, open_t)
    context.draw_list.add_rect_filled(Vec2(x, y), Vec2(w, h), color, rounding=style.frame_rounding)

    if context.font is not None:
        arrow = "v" if is_open else ">"
        context.draw_list.add_text(context.font, arrow + " " + display, Vec2(x + style.frame_padding.x, y + style.frame_padding.y), text_color)

    end_item(context, x, y, w, h)
    return is_open


def is_item_hovered():
    context = get_current_context()
    if context.current_window is None or not context.current_window.is_hovered_window:
        return False
    min_x, min_y = context.last_item_min
    max_x, max_y = context.last_item_max
    return point_in_rect(context.io.mouse_pos, (min_x, min_y, max_x - min_x, max_y - min_y))


def set_tooltip(text_value):
    context = get_current_context()
    if context.font is None:
        return
    context.pending_tooltip = text_value


def draw_tooltip(context):
    text_value = context.pending_tooltip
    if text_value is None or context.font is None:
        return
    style = context.style
    text_w, text_h = context.font.measure(text_value)
    pad = style.scaled(6.0)
    offset = style.scaled(16.0)
    edge = style.scaled(4.0)
    size = Vec2(text_w + pad * 2.0, text_h + pad * 2.0)
    pos = Vec2(context.io.mouse_pos.x + offset, context.io.mouse_pos.y + offset)
    pos.x = min(pos.x, context.io.display_size.x - size.x - edge)
    pos.y = min(pos.y, context.io.display_size.y - size.y - edge)
    pos.x = max(edge, pos.x)
    pos.y = max(edge, pos.y)
    context.draw_list.push_clip_rect(0.0, 0.0, context.io.display_size.x, context.io.display_size.y, intersect=False)
    context.draw_list.add_rect_filled(pos, size, style.window_bg_with_alpha(), rounding=style.frame_rounding)
    context.draw_list.add_rect_outline(pos, size, style.window_border, 1.0, rounding=style.frame_rounding)
    context.draw_list.add_text(context.font, text_value, Vec2(pos.x + pad, pos.y + pad), style.text)
    context.draw_list.pop_clip_rect()


def color_edit3(label_text, color):
    push_id(label_text)
    changed_r, r = slider_float("R", color.r, 0.0, 1.0)
    changed_g, g = slider_float("G", color.g, 0.0, 1.0)
    changed_b, b = slider_float("B", color.b, 0.0, 1.0)
    pop_id()

    context = get_current_context()
    style = context.style
    x, y = item_position(context)
    swatch_size = style.scaled(20.0)
    context.draw_list.add_rect_filled(Vec2(x, y), Vec2(swatch_size, swatch_size), Color(r, g, b, 1.0), rounding=style.frame_rounding)
    display = _display_label(label_text)
    if context.font is not None and display:
        context.draw_list.add_text(context.font, display, Vec2(x + swatch_size + style.scaled(8.0), y), style.text)
    end_item(context, x, y, swatch_size, swatch_size)

    changed = changed_r or changed_g or changed_b
    return changed, Color(r, g, b, color.a)


def plot_lines(label_text, values, width=None, height=60.0, min_scale=None, max_scale=None):
    context = get_current_context()
    style = context.style
    x, y = item_position(context)
    w = width if width is not None else current_item_width()
    display = _display_label(label_text)

    label_h = 0.0
    plot_y = y
    if context.font is not None and display:
        context.draw_list.add_text(context.font, display, Vec2(x, y), context.dim(style.text))
        label_h = context.font.line_height + 4.0
        plot_y = y + label_h

    context.draw_list.add_rect_filled(Vec2(x, plot_y), Vec2(w, height), context.dim(style.frame_bg), rounding=style.frame_rounding)

    if len(values) >= 2:
        lo = min(values) if min_scale is None else min_scale
        hi = max(values) if max_scale is None else max_scale
        span = (hi - lo) or 1.0
        step_x = w / (len(values) - 1)
        prev = None
        for i, value in enumerate(values):
            t = (value - lo) / span
            px = x + i * step_x
            py = plot_y + height - t * height
            point = Vec2(px, py)
            if prev is not None:
                context.draw_list.add_line(prev, point, context.dim(style.slider_grab), 1.5)
            prev = point

    end_item(context, x, y, w, label_h + height)


_menu_state = {
    "open_menu": None,
    "click_consumed": False,
    "bar_cursor_x": 8.0,
    "popup_x": 0.0,
    "popup_y": 0.0,
    "popup_y_start": 0.0,
    "popup_w": 180.0,
    "popup_clip_h": 0.0,
    "popup_open": False,
    "popup_rows": [],
}


def begin_main_menu_bar():
    context = get_current_context()
    style = context.style
    bar_height = _menu_bar_height(style)
    _menu_state["bar_cursor_x"] = style.scaled(8.0)
    _menu_state["click_consumed"] = False
    context.draw_list.push_clip_rect(0.0, 0.0, context.io.display_size.x, bar_height, intersect=False)
    context.draw_list.add_rect_filled(Vec2(0.0, 0.0), Vec2(context.io.display_size.x, bar_height), style.title_bg)
    context.draw_list.add_line(Vec2(0.0, bar_height), Vec2(context.io.display_size.x, bar_height), style.window_border, 1.0)
    return True


def end_main_menu_bar():
    context = get_current_context()
    context.draw_list.pop_clip_rect()
    if context.io.mouse_clicked[0] and not _menu_state["click_consumed"]:
        _menu_state["open_menu"] = None


def begin_menu(label_text):
    context = get_current_context()
    style = context.style
    text_w, text_h = context.font.measure(label_text) if context.font is not None else (40.0, 16.0)
    pad = style.scaled(10.0)
    x = _menu_state["bar_cursor_x"]
    y = 0.0
    w = text_w + pad * 2.0
    h = _menu_bar_height(style)
    rect = (x, y, w, h)
    hovered = point_in_rect(context.io.mouse_pos, rect)
    is_open = (_menu_state["open_menu"] == label_text)

    if hovered and context.io.mouse_clicked[0]:
        _menu_state["click_consumed"] = True
        is_open = not is_open
        _menu_state["open_menu"] = label_text if is_open else None
    elif hovered and _menu_state["open_menu"] is not None and _menu_state["open_menu"] != label_text:
        _menu_state["open_menu"] = label_text
        is_open = True
        _menu_state["click_consumed"] = True

    anim_key = "menu::" + label_text
    open_t = context.animate(anim_key + "::open", 1.0 if is_open else 0.0, duration=style.anim_value_seconds)
    hover_t = context.animate(anim_key + "::hover", 1.0 if (hovered and not is_open) else 0.0)
    color = style.title_bg.lerp(style.header_hovered, hover_t).lerp(style.header_active, open_t)
    text_color = style.text.lerp(style.header_active_text, open_t)
    context.draw_list.add_rect_filled(Vec2(x, y), Vec2(w, h), color)
    if context.font is not None:
        context.draw_list.add_text(context.font, label_text, Vec2(x + pad, (h - text_h) * 0.5), text_color)

    _menu_state["bar_cursor_x"] += w

    if is_open:
        popup_w = style.scaled(180.0)
        _menu_state["popup_x"] = x
        _menu_state["popup_y"] = h
        _menu_state["popup_y_start"] = h
        _menu_state["popup_w"] = popup_w
        _menu_state["popup_clip_h"] = context.io.display_size.y - h
        _menu_state["popup_open"] = True
        _menu_state["popup_rows"] = []
    return is_open


def menu_item(label_text):
    context = get_current_context()
    style = context.style
    if _menu_state["open_menu"] is None:
        return False
    text_w, text_h = context.font.measure(label_text) if context.font is not None else (40.0, 16.0)
    x = _menu_state["popup_x"]
    y = _menu_state["popup_y"]
    w = _menu_state["popup_w"]
    h = _menu_bar_height(style)
    rect = (x, y, w, h)
    hovered = point_in_rect(context.io.mouse_pos, rect)
    clicked = False

    hover_t = context.animate(f"menuitem::{_menu_state['open_menu']}::{label_text}", 1.0 if hovered else 0.0)
    row_color = style.frame_bg.lerp(style.header_hovered, hover_t)
    if hovered and context.io.mouse_clicked[0]:
        clicked = True
        _menu_state["click_consumed"] = True
        _menu_state["open_menu"] = None

    text_pos = Vec2(x + style.scaled(10.0), y + (h - text_h) * 0.5)
    _menu_state["popup_rows"].append((Vec2(x, y), Vec2(w, h), row_color, label_text, text_pos, style.text))
    _menu_state["popup_y"] += h
    return clicked


def end_menu():
    context = get_current_context()
    if not _menu_state["popup_open"]:
        return
    _menu_state["popup_open"] = False
    popup_x = _menu_state["popup_x"]
    popup_y_start = _menu_state["popup_y_start"]
    popup_w = _menu_state["popup_w"]
    popup_clip_h = _menu_state["popup_clip_h"]
    rows = _menu_state["popup_rows"]
    font = context.font

    def draw_popup():
        draw_list = context.draw_list
        draw_list.push_clip_rect(popup_x, popup_y_start, popup_w, popup_clip_h, intersect=False)
        for rect_pos, rect_size, row_color, label_text, text_pos, text_color in rows:
            draw_list.add_rect_filled(rect_pos, rect_size, row_color)
            if font is not None:
                draw_list.add_text(font, label_text, text_pos, text_color)
        draw_list.pop_clip_rect()

    context.push_overlay(draw_popup)


def begin_disabled(disabled=True):
    get_current_context().begin_disabled(disabled)


def end_disabled():
    get_current_context().end_disabled()


def push_toast(message, duration=2.5, color=None):
    get_current_context().push_toast(message, duration, color)


def draw_toasts(context):
    if not context.toasts:
        return
    style = context.style
    dt = context.io.delta_time
    alive = []
    for toast in context.toasts:
        toast["remaining"] -= dt
        if toast["remaining"] > 0.0:
            alive.append(toast)
    context.toasts = alive
    if not context.toasts or context.font is None:
        return

    fade_window = 0.4
    margin = style.scaled(20.0)
    gap = style.scaled(8.0)
    icon_gap = style.scaled(14.0)
    dot_radius = style.scaled(3.5)
    cursor_y = context.io.display_size.y - margin
    context.draw_list.push_clip_rect(0.0, 0.0, context.io.display_size.x, context.io.display_size.y, intersect=False)
    for toast in reversed(context.toasts):
        remaining = toast["remaining"]
        duration = toast["duration"]
        fade_in = min(1.0, (duration - remaining) / 0.15) if duration > 0.15 else 1.0
        fade_out = min(1.0, remaining / fade_window)
        alpha = max(0.0, min(fade_in, fade_out))

        text_value = toast["message"]
        text_w, text_h = context.font.measure(text_value)
        pad_x, pad_y = style.scaled(14.0), style.scaled(10.0)
        w = text_w + pad_x * 2.0 + icon_gap
        h = text_h + pad_y * 2.0
        x = context.io.display_size.x - w - margin
        cursor_y -= h
        accent = toast["color"] or style.success

        context.draw_list.add_rect_filled(Vec2(x, cursor_y), Vec2(w, h), style.toast_bg.with_alpha(style.toast_bg.a * alpha), rounding=style.frame_rounding)
        context.draw_list.add_rect_outline(Vec2(x, cursor_y), Vec2(w, h), style.toast_border.with_alpha(style.toast_border.a * alpha), 1.0, rounding=style.frame_rounding)
        context.draw_list.add_circle_filled(Vec2(x + pad_x + dot_radius * 0.85, cursor_y + h * 0.5), dot_radius, accent.with_alpha(accent.a * alpha), segments=12)
        context.draw_list.add_text(context.font, text_value, Vec2(x + pad_x + icon_gap, cursor_y + pad_y), style.toast_text.with_alpha(style.toast_text.a * alpha))
        cursor_y -= gap
    context.draw_list.pop_clip_rect()


def badge(text_value, color=None, dot=False):
    context = get_current_context()
    style = context.style
    x, y = item_position(context)
    pad_x, pad_y = style.scaled(8.0), style.scaled(3.0)
    text_w, text_h = context.font.measure(text_value) if context.font is not None else (len(text_value) * 7.0, 14.0)
    dot_extra = style.scaled(12.0) if dot else 0.0
    dot_radius = style.scaled(3.5)
    w = text_w + pad_x * 2.0 + dot_extra
    h = text_h + pad_y * 2.0

    context.draw_list.add_rect_filled(Vec2(x, y), Vec2(w, h), context.dim(style.badge_bg), rounding=h * 0.5)
    text_x = x + pad_x
    if dot:
        dot_color = color or style.success
        context.draw_list.add_circle_filled(Vec2(x + pad_x + dot_radius * 0.85, y + h * 0.5), dot_radius, context.dim(dot_color), segments=12)
        text_x += dot_extra
    if context.font is not None:
        context.draw_list.add_text(context.font, text_value, Vec2(text_x, y + pad_y), context.dim(color or style.badge_text))

    end_item(context, x, y, w, h)


def segmented_control(label_id, options, current_index, width=None, equal_width=True):
    context = get_current_context()
    style = context.style
    widget_id = context.make_id(label_id)

    x, y = item_position(context)
    h = style.scaled(28.0)
    count = max(1, len(options))

    text_widths = []
    for option_text in options:
        text_w, _ = context.font.measure(option_text) if context.font is not None else (40.0, 16.0)
        text_widths.append(text_w)

    if equal_width:
        w = width if width is not None else current_item_width()
        seg_widths = [w / count] * count
    else:
        seg_padding = style.scaled(12.0)
        seg_widths = [tw + seg_padding * 2.0 for tw in text_widths]
        w = sum(seg_widths)

    seg_positions = []
    cursor = x
    for seg_w in seg_widths:
        seg_positions.append(cursor)
        cursor += seg_w

    context.draw_list.add_rect_filled(Vec2(x, y), Vec2(w, h), context.dim(style.frame_bg), rounding=style.frame_rounding)

    target_thumb_x = seg_positions[current_index]
    target_thumb_w = seg_widths[current_index]
    thumb_x = context.animate(widget_id + "::thumb_x", target_thumb_x, duration=0.10)
    thumb_w = context.animate(widget_id + "::thumb_w", target_thumb_w, duration=0.10)
    pad = style.scaled(3.0)
    context.draw_list.add_rect_filled(
        Vec2(thumb_x + pad, y + pad), Vec2(thumb_w - 2.0 * pad, h - 2.0 * pad),
        context.dim(style.button_active), rounding=max(1.0, style.frame_rounding - 2.0),
    )

    changed = False
    new_index = current_index
    for i, option_text in enumerate(options):
        seg_x = seg_positions[i]
        seg_w = seg_widths[i]
        seg_id = f"{widget_id}::seg{i}"
        seg_hovered = context.set_hovered(seg_id, (seg_x, y, seg_w, h))

        if seg_hovered and context.io.mouse_clicked[0] and context.active_id is None:
            context.set_active(seg_id)
        if context.is_active(seg_id) and context.io.mouse_released[0]:
            if seg_hovered and i != current_index:
                new_index = i
                changed = True
            context.clear_active()

        is_selected = (i == current_index)
        hover_t = context.animate(seg_id + "::hover", 1.0 if (seg_hovered and not is_selected) else 0.0)
        if hover_t > 0.001:
            context.draw_list.add_rect_filled(
                Vec2(seg_x, y), Vec2(seg_w, h),
                style.frame_bg_hovered.with_alpha(style.frame_bg_hovered.a * hover_t * 0.5),
                rounding=style.frame_rounding,
            )

        if context.font is not None:
            text_w = text_widths[i]
            text_h = context.font.line_height
            text_color = style.button_active_text if is_selected else style.text
            context.draw_list.push_clip_rect(seg_x, y, seg_w, h)
            context.draw_list.add_text(
                context.font, option_text,
                Vec2(seg_x + (seg_w - text_w) * 0.5, y + (h - text_h) * 0.5),
                context.dim(text_color),
            )
            context.draw_list.pop_clip_rect()

    end_item(context, x, y, w, h)
    return changed, new_index


def drag_float(label_text, value, speed=1.0, min_value=None, max_value=None, width=None, value_format="{:.2f}"):
    context = get_current_context()
    style = context.style
    widget_id = context.make_id(label_text)
    display = _display_label(label_text)

    x, y = item_position(context)
    w = width if width is not None else current_item_width()
    h = (context.font.line_height if context.font is not None else 18.0) + style.frame_padding.y * 2.0
    rect = (x, y, w, h)
    hovered = context.set_hovered(widget_id, rect)
    changed = False

    if hovered and context.io.mouse_clicked[0] and context.active_id is None:
        context.set_active(widget_id)
        context._drag_anchor_mouse = Vec2(context.io.mouse_pos.x, context.io.mouse_pos.y)
        context._drag_anchor_value = value

    if context.is_active(widget_id) and context.io.mouse_down[0]:
        delta = (context.io.mouse_pos.x - context._drag_anchor_mouse.x) / style.scale
        new_value = context._drag_anchor_value + delta * speed
        if min_value is not None:
            new_value = max(min_value, new_value)
        if max_value is not None:
            new_value = min(max_value, new_value)
        if new_value != value:
            value = new_value
            changed = True

    hover_t = context.animate(widget_id, 1.0 if hovered else 0.0)
    if context.is_active(widget_id):
        bg_color = style.frame_bg_active
    else:
        bg_color = style.frame_bg.lerp(style.frame_bg_hovered, hover_t)
    context.draw_list.add_rect_filled(Vec2(x, y), Vec2(w, h), context.dim(bg_color), rounding=style.frame_rounding)
    context.draw_list.add_rect_outline(Vec2(x, y), Vec2(w, h), context.dim(style.window_border), 1.0, rounding=style.frame_rounding)

    if context.font is not None:
        text_value = f"{display}: {value_format.format(value)}" if display else value_format.format(value)
        text_w, text_h = context.font.measure(text_value)
        context.draw_list.add_text(context.font, text_value, Vec2(x + (w - text_w) * 0.5, y + (h - text_h) * 0.5), context.dim(style.text))

    end_item(context, x, y, w, h)
    return changed, value


def drag_int(label_text, value, speed=1.0, min_value=None, max_value=None, width=None):
    changed, new_value = drag_float(label_text, float(value), speed, min_value, max_value, width, value_format="{:.0f}")
    return changed, int(round(new_value))
