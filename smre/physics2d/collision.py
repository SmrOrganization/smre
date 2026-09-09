from ..mathlib import Vec2
from .aabb import AABB


def aabb_vs_aabb(a, b):
    return a.intersects(b)


def circle_vs_circle(center_a, radius_a, center_b, radius_b):
    distance = center_a.distance_to(center_b)
    return distance <= (radius_a + radius_b)


def point_in_aabb(point, box):
    return box.contains_point(point)


def resolve_dynamic_pair(transform_a, body_a, transform_b, body_b):
    box_a = AABB.from_center_size(transform_a.position, body_a.size)
    box_b = AABB.from_center_size(transform_b.position, body_b.size)
    if not box_a.intersects(box_b):
        return

    overlap_x = min(box_a.max.x, box_b.max.x) - max(box_a.min.x, box_b.min.x)
    overlap_y = min(box_a.max.y, box_b.max.y) - max(box_a.min.y, box_b.min.y)
    if overlap_x <= 0 or overlap_y <= 0:
        return

    a_static = body_a.is_static
    b_static = body_b.is_static
    if a_static and b_static:
        return

    if overlap_x < overlap_y:
        direction = 1.0 if transform_a.position.x < transform_b.position.x else -1.0
        _separate_axis(transform_a, body_a, transform_b, body_b, overlap_x, direction, axis="x")
    else:
        direction = 1.0 if transform_a.position.y < transform_b.position.y else -1.0
        _separate_axis(transform_a, body_a, transform_b, body_b, overlap_y, direction, axis="y")


def _separate_axis(transform_a, body_a, transform_b, body_b, overlap, direction, axis):
    a_static = body_a.is_static
    b_static = body_b.is_static

    if a_static:
        push_a, push_b = 0.0, overlap
    elif b_static:
        push_a, push_b = overlap, 0.0
    else:
        push_a, push_b = overlap * 0.5, overlap * 0.5

    if axis == "x":
        transform_a.position = Vec2(transform_a.position.x - direction * push_a, transform_a.position.y)
        transform_b.position = Vec2(transform_b.position.x + direction * push_b, transform_b.position.y)
        if not a_static:
            body_a.velocity = Vec2(0.0, body_a.velocity.y)
        if not b_static:
            body_b.velocity = Vec2(0.0, body_b.velocity.y)
    else:
        transform_a.position = Vec2(transform_a.position.x, transform_a.position.y - direction * push_a)
        transform_b.position = Vec2(transform_b.position.x, transform_b.position.y + direction * push_b)
        if not a_static:
            body_a.velocity = Vec2(body_a.velocity.x, 0.0)
            if direction > 0.0:
                body_a.on_ground = True
        if not b_static:
            body_b.velocity = Vec2(body_b.velocity.x, 0.0)
            if direction < 0.0:
                body_b.on_ground = True
