import pygame as pg

class Animation:
    '''  
    루프 가능한 스프라이트 시퀀스 애니메이션 클래스  
    이미지 리스트를 받아서 일정 시간마다 프레임 넘겨줌  
    파티클이나 캐릭터 애니메이션에 씀  
    '''

    def __init__(self, images: list[pg.Surface], img_dur_seconds=0.1, loop=True, flip_x=False, flip_y=False):
        '''
        :param images: 프레임 이미지 리스트  
        :param img_dur_seconds: 각 프레임 지속 시간(초)  
        :param loop: True면 끝나도 계속 반복  
        :param flip_x: True면 이미지 좌우 반전  
        :param flip_y: True면 이미지 상하 반전  
        '''
        self.images = images
        self.img_duration = img_dur_seconds
        self.loop = loop

        self.flip_x = flip_x
        self.flip_y = flip_y

        self.done = False         # 애니메이션 끝났는지 여부
        self.paused = False       # 일시정지 상태
        self.elapsed = 0.0        # 현재 프레임까지 지난 시간
        self.frame = 0            # 현재 프레임 인덱스

        self.on_complete = []      # 애니메이션 끝나면 호출할 콜백 함수 리스트
        self.auto_destroy = False  # 파티클용, 끝나면 자동으로 소멸시킬지 여부
        self.owner = None          # auto_destroy시 destroy 호출할 대상 객체

    def set_owner(self, obj):
        '''  
        auto_destroy 활성화 시, 끝나면 호출할 destroy 대상 지정  
        '''
        self.owner = obj

    def copy(self):
        '''  
        애니메이션 복제 (깊은 복사 같은 효과)  
        '''
        clone = Animation(self.images, self.img_duration, self.loop, self.flip_x, self.flip_y)
        return clone

    def reset(self):
        '''애니메이션 처음부터 다시 시작'''
        self.done = False
        self.elapsed = 0.0
        self.frame = 0

    def pause(self):
        '''애니메이션 일시정지'''
        self.paused = True

    def resume(self):
        '''일시정지 해제'''
        self.paused = False

    def update(self, dt: float):
        '''  
        dt만큼 시간을 더해 애니메이션 진행  
        끝나면 콜백 호출, auto_destroy면 owner.destroy() 호출  
        '''
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
        '''  
        현재 프레임 이미지 반환 (flip_x, flip_y 적용됨)  
        '''
        base = self.images[self.frame]
        return pg.transform.flip(base, self.flip_x, self.flip_y)