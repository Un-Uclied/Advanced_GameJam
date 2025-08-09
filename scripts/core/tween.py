import pygame as pg
import pytweening as pt

from scripts.constants import *
from scripts.core import *

def lerp_color(start: pg.Color, end: pg.Color, t: float) -> pg.Color:
    '''
    색상 보간 함수  
    start에서 end로 t(0~1)만큼 선형 보간해서 새로운 색 반환

    :param start: 시작 색상 (pg.Color)
    :param end: 끝 색상 (pg.Color)
    :param t: 보간 값 (0.0 ~ 1.0)
    :return: 보간된 색상 (pg.Color)
    '''
    r = int(start.r + (end.r - start.r) * t)
    g = int(start.g + (end.g - start.g) * t)
    b = int(start.b + (end.b - start.b) * t)
    a = int(start.a + (end.a - start.a) * t)
    return pg.Color(r, g, b, a)


class Tween(GameObject):
    '''
    특정 객체의 속성을 일정 시간 동안 이징 함수에 따라 보간(변화)시킴  

    이징 함수(pytweening 사용) 덕분에 자연스럽고 다양한 애니메이션 효과 가능  

    :param target: 속성 변경 대상 객체
    :param attr_name: 변경할 속성명 (문자열)
    :param start_value: 시작 값 (숫자, pg.Vector2, pg.Color 가능)
    :param end_value: 종료 값 (숫자, pg.Vector2, pg.Color 가능)
    :param duration: 지속 시간(초), 0 이하면 0.0001초 처리
    :param easing: 이징 함수, 기본은 선형(pt.linear)
    :param use_unscaled_time: 게임 시간 스케일 무시 여부 (True면 실제 시간으로 계산)
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

        self.elapsed = 0.0  # 경과 시간
        self.on_complete = []  # 완료 시 호출할 콜백 리스트

        # 트윈 시작 시점에 대상 속성을 시작 값으로 강제 설정
        setattr(self.target, self.attr_name, self.start_value)

    def update(self):
        '''
        매 프레임 호출되어 값을 계산 및 적용함

        게임 내 시간 스케일 적용하거나 무시하는 옵션 포함  
        경과 시간 누적 후 보간 값을 계산하여 속성에 대입

        완료되면 on_complete 이벤트 호출 후 자기 자신 파괴
        '''
        super().update()

        # dt 계산: 언스케일드 시간 쓸지 게임 시간 스케일 적용 시간 쓸지 결정
        dt = self.app.unscaled_dt if self.use_unscaled_time else self.app.dt
        self.elapsed += dt

        # 경과 시간 대비 진행률 (0~1)
        t = min(self.elapsed / self.duration, 1.0)

        # 이징 함수로 보간 진행률 변형 (ease in/out 등 자연스러운 움직임)
        eased_t = self.easing(t)

        # 값 타입에 따라 보간 처리 다름
        if isinstance(self.start_value, pg.Color) and isinstance(self.end_value, pg.Color):
            # 컬러 보간은 각 채널별로 lerp_color 호출
            value = lerp_color(self.start_value, self.end_value, eased_t)

        elif isinstance(self.start_value, pg.Vector2) and isinstance(self.end_value, pg.Vector2):
            # 벡터 보간은 Vector2.lerp 함수 사용
            value = self.start_value.lerp(self.end_value, eased_t)

        else:
            # 숫자(int, float) 타입 기본 보간 처리
            value = self.start_value + (self.end_value - self.start_value) * eased_t

        # 보간된 값을 타겟 속성에 할당
        setattr(self.target, self.attr_name, value)

        # 완료 시점이면 콜백 실행 및 자기 자신 제거
        if t >= 1.0:
            for callback in self.on_complete:
                callback()
            self.destroy()