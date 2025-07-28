import pygame as pg

class Animation:
    '''루프를 이용한 간단한 애니메이션 클래스'''
    def __init__(self, images: list[pg.Surface], img_dur_seconds=0.1, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur_seconds

        self.done = False
        self.elapsed = 0.0
        self.frame = 0

    def copy(self):
        '''애셋 딕셔너리에 있는걸 참조해서 변경하면 다른거에도 변경 되기 때문에 복사해야함'''
        return Animation(self.images, self.img_duration, self.loop)

    def update(self, delta_time: float):
        '''델타타임 직접 넣어줘야함'''
        if self.done:
            return

        self.elapsed += delta_time

        frames_advanced = int(self.elapsed / self.img_duration)
        if frames_advanced > 0:
            self.elapsed %= self.img_duration
            self.frame += frames_advanced

            if self.frame >= len(self.images):
                if self.loop:
                    # 프레임이 총 이미지 길이 넘어가지 않게
                    self.frame %= len(self.images)
                else:
                    # 루프가 아니면 done = True, 업데이트를 불러도 바로 리턴 해버리게끔 
                    self.frame = len(self.images) - 1
                    self.done = True

    def img(self) -> pg.Surface:
        '''현재 이미지 반환!'''
        return self.images[self.frame]