import itertools

_id_counter = itertools.count(1)


class Entity:
    def __init__(self, world):
        self.id = next(_id_counter)
        self.world = world
        self.name = f"Entity{self.id}"
        self.active = True
        self._components = {}

    def add_component(self, component):
        self._components[type(component)] = component
        return component

    def get_component(self, component_type):
        return self._components.get(component_type)

    def has_component(self, component_type):
        return component_type in self._components

    def has_components(self, *component_types):
        return all(component_type in self._components for component_type in component_types)

    def remove_component(self, component_type):
        self._components.pop(component_type, None)

    def components(self):
        return self._components.values()

    def destroy(self):
        self.world.destroy_entity(self)

    def __repr__(self):
        return f"Entity(id={self.id}, name={self.name!r})"
