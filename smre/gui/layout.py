from .context import get_current_context


def begin_content_area(context, content_x, content_y, content_width):
    context.content_origin_x = content_x
    context.cursor_x = content_x
    context.cursor_y = content_y
    context.content_region_x = content_width
    context.line_height = 0.0
    context.prev_line_height = 0.0
    context.cursor_pos_prev_line = (content_x, content_y)
    context.last_item_min = (content_x, content_y)
    context.last_item_max = (content_x, content_y)
    context._item_width_stack = [content_width]


def item_position(context):
    return context.cursor_x, context.cursor_y


def end_item(context, x, y, width, height):
    context.last_item_min = (x, y)
    context.last_item_max = (x + width, y + height)
    context.cursor_pos_prev_line = (context.content_origin_x, y)
    context.line_height = max(context.line_height, height)
    context.prev_line_height = context.line_height
    context.cursor_x = context.content_origin_x
    context.cursor_y = y + context.line_height + context.style.item_spacing.y
    context.line_height = 0.0


def same_line(spacing=None):
    context = get_current_context()
    gap = context.style.item_spacing.x if spacing is None else spacing
    prev_x, prev_y = context.cursor_pos_prev_line
    context.cursor_x = context.last_item_max[0] + gap
    context.cursor_y = prev_y
    context.line_height = context.prev_line_height


def spacing(pixels=None):
    context = get_current_context()
    gap = context.style.item_spacing.y if pixels is None else pixels
    context.cursor_y += gap


def dummy(width, height):
    context = get_current_context()
    x, y = item_position(context)
    end_item(context, x, y, width, height)


def current_item_width():
    context = get_current_context()
    return context._item_width_stack[-1]


def push_item_width(width):
    context = get_current_context()
    context._item_width_stack.append(width)


def pop_item_width():
    context = get_current_context()
    if len(context._item_width_stack) > 1:
        context._item_width_stack.pop()


def cursor_pos():
    context = get_current_context()
    return context.cursor_x, context.cursor_y


def set_cursor_pos(x, y):
    context = get_current_context()
    context.cursor_x = x
    context.cursor_y = y
