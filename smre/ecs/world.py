from .entity import Entity


class World:
    def __init__(self):
        self.entities = []
        self.systems = []
        self._pending_destroy = []

    def create_entity(self, name=None):
        entity = Entity(self)
        if name:
            entity.name = name
        self.entities.append(entity)
        return entity

    def destroy_entity(self, entity):
        if entity not in self._pending_destroy:
            self._pending_destroy.append(entity)

    def add_system(self, system):
        system.on_added(self)
        self.systems.append(system)
        return system

    def remove_system(self, system):
        if system in self.systems:
            self.systems.remove(system)

    def get_entities_with(self, *component_types):
        for entity in self.entities:
            if entity.active and entity.has_components(*component_types):
                yield entity

    def find_by_name(self, name):
        for entity in self.entities:
            if entity.name == name:
                return entity
        return None

    def update(self, delta_time):
        for system in self.systems:
            system.update(delta_time)
        self._flush_destroyed()

    def _flush_destroyed(self):
        if not self._pending_destroy:
            return
        for entity in self._pending_destroy:
            if entity in self.entities:
                self.entities.remove(entity)
        self._pending_destroy.clear()

    def clear(self):
        self.entities.clear()
        self._pending_destroy.clear()
