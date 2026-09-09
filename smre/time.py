import time as _time


class Clock:
    def __init__(self, fixed_step=1.0 / 60.0, max_delta=0.25):
        self.fixed_step = fixed_step
        self.max_delta = max_delta
        self.delta_time = 0.0
        self.total_time = 0.0
        self.frame_count = 0
        self.fps = 0.0
        self._last_time = _time.perf_counter()
        self._fps_accum = 0.0
        self._fps_frames = 0
        self._accumulator = 0.0

    def tick(self):
        now = _time.perf_counter()
        raw_delta = now - self._last_time
        self._last_time = now
        if raw_delta > self.max_delta:
            raw_delta = self.max_delta
        self.delta_time = raw_delta
        self.total_time += raw_delta
        self.frame_count += 1

        self._fps_accum += raw_delta
        self._fps_frames += 1
        if self._fps_accum >= 0.5:
            self.fps = self._fps_frames / self._fps_accum
            self._fps_accum = 0.0
            self._fps_frames = 0

        self._accumulator += raw_delta
        return self.delta_time

    def consume_fixed_step(self):
        if self._accumulator >= self.fixed_step:
            self._accumulator -= self.fixed_step
            return True
        return False

    def fixed_alpha(self):
        return self._accumulator / self.fixed_step


class Timer:
    def __init__(self, duration, on_complete=None, repeat=False):
        self.duration = duration
        self.on_complete = on_complete
        self.repeat = repeat
        self.elapsed = 0.0
        self.finished = False

    def update(self, delta_time):
        if self.finished and not self.repeat:
            return
        self.elapsed += delta_time
        if self.elapsed >= self.duration:
            self.elapsed -= self.duration if self.repeat else 0.0
            self.finished = True
            if self.on_complete is not None:
                self.on_complete()

    def reset(self):
        self.elapsed = 0.0
        self.finished = False

    def progress(self):
        return min(1.0, self.elapsed / self.duration) if self.duration > 0 else 1.0
