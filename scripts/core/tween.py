import pygame as pg
import pytweening as pt

from scripts.constants import *
from scripts.core import *

def lerp_color(start: pg.Color, end: pg.Color, t: float) -> pg.Color:
    '''색은 하나하나 값을 보간해서 새로 만듦;'''
    r = int(start.r + (end.r - start.r) * t)
    g = int(start.g + (end.g - start.g) * t)
    b = int(start.b + (end.b - start.b) * t)
    a = int(start.a + (end.a - start.a) * t)
    return pg.Color(r, g, b, a)

class Tween(GameObject):
    '''
    특정 객체의 속성을 일정 시간 동안 이징 방식으로 보간하는 트윈 객체

    :param target: 트윈할 대상 객체
    :param attr_name: 문자열, 대상 객체의 멤버 변수 이름
    :param start_value: 시작 값 (숫자, Vector2, Color 지원)
    :param end_value: 끝 값 (숫자, Vector2, Color 지원)
    :param duration: 트윈 시간 (초)
    :param easing: 이징 함수 (기본: linear, pytweening 쓰면 EZ)
    :param use_unscaled_time: 트윈 시간 계산에 게임 시간 스케일을 적용할지 여부 (기본: False)
    '''

    def __init__(self, target, attr_name: str,
                 start_value, end_value,
                 duration: float,
                 easing=pt.linear, use_unscaled_time: bool = False):
        super().__init__()

        self.target = target
        self.attr_name = attr_name
        self.start_value = start_value
        self.end_value = end_value
        self.duration = max(0.0001, duration)
        self.easing = easing
        self.use_unscaled_time = use_unscaled_time

        self.elapsed = 0.0
        self.on_complete = []

        # 초기값 강제 세팅
        setattr(self.target, self.attr_name, self.start_value)

    def update(self):
        super().update()
        dt = self.app.unscaled_dt if self.use_unscaled_time else self.app.dt
        self.elapsed += dt

        t = min(self.elapsed / self.duration, 1.0)
        eased_t = self.easing(t)

        # 타입별 보간 처리
        if isinstance(self.start_value, pg.Color) and isinstance(self.end_value, pg.Color):
            value = lerp_color(self.start_value, self.end_value, eased_t)
        elif isinstance(self.start_value, pg.Vector2) and isinstance(self.end_value, pg.Vector2):
            value = self.start_value.lerp(self.end_value, eased_t)
        else:  # 숫자 (int, float) 기본 처리
            value = self.start_value + (self.end_value - self.start_value) * eased_t

        setattr(self.target, self.attr_name, value)

        if t >= 1.0:
            for callback in self.on_complete:
                callback()
            self.destroy()