import pygame as pg
import pytweening as pt

from scripts.constants import *
from scripts.core import *

class ScreenFaderRenderer(GameObject):
    """
    화면 페이드 효과의 렌더링을 담당하는 클래스.
    
    페이드에 사용될 Surface를 생성하고, alpha 값에 따라 이를 그림.
    """
    def __init__(self):
        super().__init__()
        # 전체 화면 크기의 투명 검정 Surface를 생성함.
        self.surface = pg.Surface(SCREEN_SIZE, pg.SRCALPHA)
        self.surface.fill((0, 0, 0))
        self._last_alpha = -1

    @property
    def alpha(self):
        return self.surface.get_alpha()        

    @alpha.setter
    def alpha(self, value):
        """
        Surface의 투명도를 설정함.
        
        Args:
            alpha (float): 설정할 투명도 값 (0.0-255.0).
        """
        if value != self._last_alpha:
            # alpha 값은 float이지만 set_alpha는 int를 기대하므로 정수형으로 변환함.
            self.surface.set_alpha(int(value))
            self._last_alpha = value

    def draw(self):
        """
        매 프레임 호출되며, Surface를 화면에 그림.
        """
        super().draw()
        # 페이드 효과 Surface를 인터페이스 레이어에 그림.
        self.app.surfaces[LAYER_INTERFACE].blit(self.surface, (0, 0))


class ScreenFaderAnimator:
    """
    화면 페이드 애니메이션 로직을 제어하는 클래스.
    
    특정 객체의 alpha 값을 Tween으로 조작하여 페이드 효과를 만듦.
    """
    def __init__(self, target, duration: float, fade_in: bool, on_complete=None):
        self.target = target
        
        # 페이드 방향에 따라 초기 알파값과 목표 알파값을 설정함.
        initial_alpha = 0 if fade_in else 255
        target_alpha = 255 if fade_in else 0
        
        # on_complete 인자를 직접 전달하는 방식으로 콜백을 등록함.
        Tween(self.target, "alpha", initial_alpha, target_alpha, duration, pt.easeInCubic,
              on_complete=on_complete, use_unscaled_time=True)


class ScreenFader(GameObject):
    """
    화면 전체를 검정으로 페이드 인/아웃하는 UI 효과.

    `Tween` 객체를 사용해서 지정된 시간 동안 화면의 투명도를 부드럽게 변화시킴.
    페이드가 완료되면 지정된 콜백 함수를 호출하고 스스로를 파괴함.

    Attributes:
        surface (pg.Surface): 페이드 효과를 위해 화면 전체를 덮는 투명한 검정 Surface.
        alpha (float): 현재 Surface의 투명도 (0.0-255.0). Tween에 의해 변경됨.
        on_complete (callable): 페이드 완료 시 호출될 콜백 함수.
        fade_in (bool): True면 페이드 인(투명 -> 검정), False면 페이드 아웃(검정 -> 투명).
    """

    def __init__(self, duration: float, fade_in: bool, on_complete=None):
        """
        ScreenFader 객체를 초기화하고 페이드 효과를 시작함.

        Args:
            duration (float): 페이드 효과가 진행될 시간(초).
            fade_in (bool): 페이드 인(True) 또는 페이드 아웃(False) 방향을 결정.
            on_complete (callable, optional): 페이드 완료 시 실행할 함수.
        """
        super().__init__()
        
        # 렌더러와 애니메이터를 조합하여 책임 분리
        self.renderer = ScreenFaderRenderer()
        self.animator = ScreenFaderAnimator(self.renderer, duration, fade_in, self.fade_done)
        
        self.on_complete = on_complete
    
    def destroy(self):
        self.renderer.destroy()
        super().destroy()

    def fade_done(self):
        """
        페이드 효과가 완료된 후 호출되는 콜백 메서드.

        지정된 콜백 함수를 실행하고 객체를 파괴해서 메모리를 정리함.
        """
        # on_complete 콜백 함수가 있으면 호출함.
        if self.on_complete is not None:
            self.on_complete()
        
        # 페이드 효과가 끝났으므로 스스로를 파괴해서 씬 객체 목록에서 제거함.
        self.destroy()

    def draw(self):
        """
        매 프레임 호출되며, Surface를 화면에 그림.
        
        `alpha` 값이 변경되었을 때만 `set_alpha`를 호출해서 성능을 최적화함.
        """
        # 부모 클래스의 draw()를 호출함.
        super().draw()
        
        self.renderer.draw()