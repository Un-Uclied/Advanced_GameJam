import pygame as pg
import pytweening as pt

from scripts.constants import *
from scripts.core import *


class Interpolator:
    '''
    다양한 타입의 값을 보간하는 로직을 담당하는 클래스
    '''
    @staticmethod
    def lerp_color(start: pg.Color, end: pg.Color, t: float) -> pg.Color:
        '''
        색상 보간 함수
        '''
        r = int(start.r + (end.r - start.r) * t)
        g = int(start.g + (end.g - start.g) * t)
        b = int(start.b + (end.b - start.b) * t)
        a = int(start.a + (end.a - start.a) * t)
        return pg.Color(r, g, b, a)

    @staticmethod
    def interpolate(start_value, end_value, t: float, easing) -> any:
        '''
        시작 값과 끝 값을 이징 함수에 따라 보간하여 반환
        '''
        eased_t = easing(t)
        
        # 타입별 보간 함수를 결정
        if isinstance(start_value, pg.Color):
            return Interpolator.lerp_color(start_value, end_value, eased_t)
        elif isinstance(start_value, pg.Vector2):
            return start_value.lerp(end_value, eased_t)
        else:
            # 기본 숫자 타입 보간
            return start_value + (end_value - start_value) * eased_t


class Tween(GameObject):
    '''
    특정 객체의 속성을 일정 시간 동안 이징 함수에 따라 보간(변화)시킴.

    `pytweening` 라이브러리의 다양한 이징 함수를 사용해 자연스러운 애니메이션 효과를 연출.
    `GameObject`를 상속받아 자동으로 업데이트되며, 완료 시 콜백을 실행하고 스스로를 파괴함.

    Attributes:
        target: 속성을 변경할 대상 객체.
        attr_name (str): 변경할 속성명.
        start_value: 트윈 시작 값.
        end_value: 트윈 종료 값.
        duration (float): 트윈 지속 시간(초).
        easing (callable): 보간에 사용할 이징 함수.
        use_unscaled_time (bool): 게임 시간 스케일 무시 여부.
        on_complete (list): 트윈 완료 시 호출될 콜백 함수 목록.
    '''
    
    def __init__(self, target, attr_name: str,
                 start_value, end_value,
                 duration: float,
                 easing=pt.linear, use_unscaled_time: bool = False,
                 on_complete=None):
        """
        Tween 객체를 초기화하고 시작합니다.
        
        Args:
            target: 속성을 변경할 대상 객체.
            attr_name (str): 변경할 속성명.
            start_value: 시작 값.
            end_value: 종료 값.
            duration (float): 지속 시간(초). 0이면 즉시 완료.
            easing (callable): 이징 함수. 기본값은 `pt.linear`.
            use_unscaled_time (bool): True면 게임 시간 스케일을 무시하고 실제 시간으로 계산.
            on_complete (callable or list, optional): 트윈 완료 시 호출할 함수 또는 함수 목록.
        """
        super().__init__()

        self.target = target
        self.attr_name = attr_name
        self.start_value = start_value
        self.end_value = end_value
        self.duration = duration
        self.easing = easing
        self.use_unscaled_time = use_unscaled_time
        self.elapsed = 0.0

        # 콜백을 리스트로 저장하고, 인자로 전달받은 콜백을 추가함.
        self.on_complete = []
        if on_complete:
            if isinstance(on_complete, (list, tuple)):
                self.on_complete.extend(on_complete)
            else:
                self.on_complete.append(on_complete)

        # 트윈 시작 시점에 대상 속성을 시작 값으로 강제 설정.
        # 이렇게 하면 트윈이 생성될 때부터 정확한 값을 가짐.
        setattr(self.target, self.attr_name, self.start_value)
        
        # duration이 0일 경우, 즉시 완료 처리
        if self.duration <= 0:
            self.complete()
            return
    
    def complete(self):
        """
        트윈을 즉시 완료 상태로 만들고 콜백을 실행.
        """
        # 목표값으로 설정
        setattr(self.target, self.attr_name, self.end_value)
        
        # 콜백 실행
        for callback in self.on_complete[:]:
            callback()
            
        # 자기 자신을 파괴
        self.destroy()

    def update(self):
        '''
        매 프레임 호출되어 값을 계산하고 적용.
        '''
        # 이미 완료된 트윈은 업데이트하지 않음.
        if self.elapsed >= self.duration:
            return

        # dt 계산: 언스케일드 시간 또는 스케일드 시간 선택
        dt = self.app.unscaled_dt if self.use_unscaled_time else self.app.dt
        self.elapsed += dt

        # 경과 시간 대비 진행률 (0~1)
        t = min(self.elapsed / self.duration, 1.0)

        # Interpolator 클래스를 사용하여 값 보간 로직을 위임
        value = Interpolator.interpolate(self.start_value, self.end_value, t, self.easing)
        
        # 보간된 값을 타겟 속성에 할당
        setattr(self.target, self.attr_name, value)

        # 완료 시점이면 콜백 실행 및 자기 자신 제거
        if t >= 1.0:
            self.complete()