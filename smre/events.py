from collections import defaultdict


class EventBus:
    def __init__(self):
        self._listeners = defaultdict(list)

    def subscribe(self, event_name, callback):
        self._listeners[event_name].append(callback)
        return callback

    def unsubscribe(self, event_name, callback):
        listeners = self._listeners.get(event_name)
        if listeners and callback in listeners:
            listeners.remove(callback)

    def emit(self, event_name, *args, **kwargs):
        for callback in list(self._listeners.get(event_name, ())):
            callback(*args, **kwargs)

    def clear(self, event_name=None):
        if event_name is None:
            self._listeners.clear()
        else:
            self._listeners.pop(event_name, None)


class Signal:
    def __init__(self):
        self._callbacks = []

    def connect(self, callback):
        self._callbacks.append(callback)
        return callback

    def disconnect(self, callback):
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def emit(self, *args, **kwargs):
        for callback in list(self._callbacks):
            callback(*args, **kwargs)

    def clear(self):
        self._callbacks.clear()


global_bus = EventBus()
