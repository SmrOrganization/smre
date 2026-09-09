from ..ecs.components import Transform2D
from ..ecs.system import System
from ..mathlib import Vec2
from .collision import resolve_dynamic_pair


class Rigidbody2D:
    def __init__(self, size=None, velocity=None, gravity_scale=1.0, is_static=False):
        self.size = size if size is not None else Vec2(32.0, 32.0)
        self.velocity = velocity if velocity is not None else Vec2.zero()
        self.gravity_scale = gravity_scale
        self.is_static = is_static
        self.on_ground = False


class PhysicsSystem2D(System):
    def __init__(self, gravity=None):
        super().__init__()
        self.gravity = gravity if gravity is not None else Vec2(0.0, 980.0)

    def update(self, delta_time):
        bodies = list(self.world.get_entities_with(Transform2D, Rigidbody2D))

        for entity in bodies:
            body = entity.get_component(Rigidbody2D)
            if body.is_static:
                continue
            transform = entity.get_component(Transform2D)
            body.velocity = body.velocity + self.gravity * body.gravity_scale * delta_time
            transform.position = transform.position + body.velocity * delta_time
            body.on_ground = False

        for i in range(len(bodies)):
            for j in range(i + 1, len(bodies)):
                entity_a, entity_b = bodies[i], bodies[j]
                transform_a = entity_a.get_component(Transform2D)
                body_a = entity_a.get_component(Rigidbody2D)
                transform_b = entity_b.get_component(Transform2D)
                body_b = entity_b.get_component(Rigidbody2D)
                resolve_dynamic_pair(transform_a, body_a, transform_b, body_b)
