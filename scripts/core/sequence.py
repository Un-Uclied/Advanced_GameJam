from .game_object import GameObject
from .timer import Timer

class Sequence(GameObject):
    def __init__(self, *steps: tuple[float, callable]):
        super().__init__()
        self.steps = list(steps)
        self.index = 0
        self.timer = None
        self.start_next()

    def start_next(self):
        if self.index >= len(self.steps):
            self.destroy()
            return
        delay, func = self.steps[self.index]
        func()
        self.timer = Timer(delay, self.start_next)
        self.index += 1

    def update(self):
        if self.timer:
            self.timer.update()