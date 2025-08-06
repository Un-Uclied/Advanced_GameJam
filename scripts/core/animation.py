import pygame as pg

class Animation:
    '''루프 애니메이션을 간편하게 처리하는 클래스'''

    def __init__(self, images: list[pg.Surface], img_dur_seconds=0.1, loop=True, flip_x=False, flip_y=False):
        self.images = images
        self.img_duration = img_dur_seconds
        self.loop = loop

        self.flip_x = flip_x
        self.flip_y = flip_y

        self.done = False
        self.paused = False
        self.elapsed = 0.0
        self.frame = 0

        self.on_complete = []      # 콜백 리스트
        self.auto_destroy = False  # 파티클용: 끝나면 알아서 사라지게
        self.owner = None          # destroy 호출할 대상 (AnimatedParticle 등)

    def set_owner(self, obj):
        '''destroy 호출 대상 설정'''
        self.owner = obj

    def copy(self):
        '''깊은 복사'''
        clone = Animation(self.images, self.img_duration, self.loop, self.flip_x, self.flip_y)
        return clone

    def reset(self):
        self.done = False
        self.elapsed = 0.0
        self.frame = 0

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def update(self, dt: float):
        if self.done or self.paused:
            return

        self.elapsed += dt
        frames_advanced = int(self.elapsed / self.img_duration)

        if frames_advanced > 0:
            self.elapsed %= self.img_duration
            self.frame += frames_advanced

            if self.frame >= len(self.images):
                if self.loop:
                    self.frame %= len(self.images)
                else:
                    self.frame = len(self.images) - 1
                    self.done = True

                    for cb in self.on_complete:
                        cb()

                    if self.auto_destroy and self.owner:
                        self.owner.destroy()

    def img(self) -> pg.Surface:
        base = self.images[self.frame]
        return pg.transform.flip(base, self.flip_x, self.flip_y)

    @property
    def frame_percent(self) -> float:
        return self.frame / max(1, len(self.images) - 1)
