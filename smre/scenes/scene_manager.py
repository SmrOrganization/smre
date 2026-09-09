class SceneManager:
    def __init__(self, app):
        self.app = app
        self.stack = []

    @property
    def current(self):
        return self.stack[-1] if self.stack else None

    def push(self, scene):
        if self.stack:
            self.stack[-1].on_pause()
        self.stack.append(scene)
        scene.on_enter()

    def pop(self):
        if not self.stack:
            return None
        scene = self.stack.pop()
        scene.on_exit()
        if self.stack:
            self.stack[-1].on_resume()
        return scene

    def replace(self, scene):
        while self.stack:
            self.pop()
        self.push(scene)

    def handle_event(self, event):
        if self.current is not None:
            self.current.handle_event(event)

    def update(self, delta_time):
        if self.current is not None:
            self.current.update(delta_time)

    def render(self):
        if self.current is not None:
            self.current.render()

    def render_gui(self):
        if self.current is not None:
            self.current.render_gui()

    def is_empty(self):
        return len(self.stack) == 0
