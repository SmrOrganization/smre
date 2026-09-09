class System:
    def __init__(self):
        self.world = None

    def on_added(self, world):
        self.world = world

    def update(self, delta_time):
        raise NotImplementedError
