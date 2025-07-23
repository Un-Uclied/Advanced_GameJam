import pygame as pg

class Animation:
    def __init__(self, images: list[pg.Surface], img_dur_seconds=0.1, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur_seconds  # 초 단위 (예: 0.1초 = 10fps)
        self.done = False
        self.elapsed = 0.0  # 누적 시간
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)

    def update(self, delta_time):
        if self.done:
            return

        self.elapsed += delta_time
        while self.elapsed >= self.img_duration:
            self.elapsed -= self.img_duration
            self.frame += 1
            if self.frame >= len(self.images):
                if self.loop:
                    self.frame = 0
                else:
                    self.frame = len(self.images) - 1
                    self.done = True
                    break

    def img(self):
        return self.images[self.frame].convert_alpha()
