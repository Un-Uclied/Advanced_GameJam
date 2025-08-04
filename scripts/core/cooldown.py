from .game_object import GameObject

class Cooldown(GameObject):
    def __init__(self, duration: float, auto_destroy=True):
        super().__init__()
        self.duration = duration
        self.time_left = 0
        self.auto_destroy = auto_destroy

    def reset(self):
        self.time_left = self.duration

    def ready(self):
        return self.time_left <= 0

    def update(self):
        super().update()
        if self.time_left > 0:
            self.time_left -= self.app.dt
        if self.auto_destroy and self.ready():
            self.destroy()