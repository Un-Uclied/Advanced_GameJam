import pygame as pg
import random

from scripts.core import *
from scripts.constants import *

SHAKE_DECREASE = 200  # 카메라 흔들림 세기 감소 속도 (초당)

class Camera2D(GameObject):
    '''
    2D 카메라 클래스
    화면 위치와 흔들림(shake) 효과 처리 담당
    (근데 Zoom이나 회전은 안됨;)
    '''

    def __init__(self, position: pg.Vector2, anchor: pg.Vector2 = pg.Vector2(0.5, 0.5)):
        '''
        :param position: 카메라 중심 위치 (월드 좌표)
        :param anchor: 화면 내 카메라 기준점 (0~1, 기본 중간 0.5,0.5)
        '''
        super().__init__()
        self.position = position
        self.anchor = anchor

        self.shake_offset = pg.Vector2()  # 현재 흔들림 보정 오프셋
        self.shake_amount = 0.0           # 흔들림 세기 (0이면 흔들림 없음)

    def update(self):
        super().update()

        # 흔들림 효과가 있으면
        if self.shake_amount > 0:
            # 흔들림 범위 내에서 랜덤 오프셋 계산
            self.shake_offset = pg.Vector2(
                random.uniform(-self.shake_amount, self.shake_amount),
                random.uniform(-self.shake_amount, self.shake_amount)
            )
            # 흔들림 세기 감소
            self.shake_amount -= SHAKE_DECREASE * self.app.dt
            if self.shake_amount < 0:
                self.shake_amount = 0.0
                self.shake_offset = pg.Vector2()  # 흔들림 종료시 오프셋 초기화