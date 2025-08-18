import pygame as pg

from scripts.constants import *
from scripts.camera import *
from scripts.core import *

BASE_FONT_PATH = "assets/fonts/"

class TextRenderer(GameObject):
    """
    UI 텍스트 렌더러 클래스.

    게임 내 텍스트를 효율적으로 렌더링하고 관리하는 데 사용함.
    런타임 중 텍스트 내용, 색상, 위치, 크기 등을 자유롭게 변경할 수 있음.

    Attributes:
        app (App): 게임 애플리케이션 인스턴스.
        text (str): 렌더링할 현재 텍스트 내용.
        pos (pg.Vector2): 텍스트의 기준 위치.
        anchor (pg.Vector2): 텍스트의 기준점 (0,0: 좌상단, 0.5,0.5: 중앙).
        use_camera (bool): True면 월드 좌표를 기준으로 카메라를 적용함.
        color (pg.Color): 텍스트 색상.
        alpha (int): 텍스트의 투명도 (0-255).
        scale (float): 텍스트 이미지의 크기 배율.
        font (pg.font.Font): 텍스트 렌더링에 사용되는 Pygame 폰트 객체.
        image (pg.Surface): 렌더링된 텍스트 이미지.
    """
    
    def __init__(self,
                 start_text: str,
                 position: pg.Vector2,
                 font_name: str = "default",
                 font_size: int = 24,
                 color: pg.Color = pg.Color("white"),
                 anchor: pg.Vector2 = pg.Vector2(0, 0),
                 use_camera: bool = False):
        """
        TextRenderer 객체를 초기화함.

        Args:
            start_text (str): 초기 텍스트 내용.
            position (pg.Vector2): 텍스트가 위치할 화면 또는 월드 좌표.
            font_name (str): 사용할 폰트 이름. 앱 에셋에 등록된 키를 사용.
            font_size (int): 폰트 크기.
            color (pg.Color): 텍스트 색상.
            anchor (pg.Vector2): 텍스트의 기준점 (예: (0, 0)은 좌상단, (0.5, 0.5)는 중앙).
            use_camera (bool): True면 텍스트 위치에 카메라 이동을 적용.
        """
        super().__init__()

        self._text = start_text
        self.pos = position
        self.anchor = anchor
        self.use_camera = use_camera
        
        # 기본 폰트 파일 경로
        font_path = BASE_FONT_PATH + self.app.ASSETS["fonts"][font_name]
        # Pygame 폰트 객체 생성
        self.font = pg.font.Font(font_path, font_size)

        # 텍스트, 스케일, 색상, 알파값을 저장할 내부 변수들
        # 프로퍼티를 통해 접근하고 변경함
        self._scale = 1.0
        self._color = pg.Color(color)
        self._alpha = 255
        self._base_surface = None  # 스케일 적용 전 원본 텍스트 서피스

        # 텍스트 이미지를 최초 렌더링함
        self.render_text()
        
    @property
    def scale(self) -> float:
        """현재 텍스트 이미지의 크기 배율을 반환함."""
        return self._scale
    
    @scale.setter
    def scale(self, value: float):
        """
        텍스트의 크기 배율을 설정하고 이미지를 업데이트함.
        
        값이 변경될 때만 렌더링 과정을 다시 수행해서 성능을 최적화함.
        """
        # 기존 스케일과 같으면 아무 작업도 안 하고 종료함.
        if self._scale == value:
            return
        self._scale = value
        self.scale_and_set_image()

    @property
    def size(self) -> pg.Vector2:
        """스케일이 적용된 현재 텍스트 이미지의 크기를 반환함."""
        return pg.Vector2(self.image.get_size())

    @property
    def screen_pos(self) -> pg.Vector2:
        """앵커를 기준으로 계산된, 화면에 텍스트를 그릴 최종 좌표를 반환함."""
        # 텍스트 이미지의 크기에 앵커 값을 곱해서 위치를 조정함.
        # pg.Vector2는 원소별 곱셈을 지원하지 않으므로 직접 연산함.
        return self.pos - pg.Vector2(self.size.x * self.anchor.x, self.size.y * self.anchor.y)

    @property
    def rect(self) -> pg.Rect:
        """충돌 감지 등을 위한 텍스트의 사각형 영역을 반환함."""
        return pg.Rect(self.screen_pos, self.size)

    @property
    def color(self) -> pg.Color:
        """텍스트의 색상을 반환함."""
        return self._color

    @color.setter
    def color(self, value: pg.Color):
        """
        텍스트의 색상을 설정하고 이미지를 다시 렌더링함.
        
        값이 변경될 때만 렌더링 과정을 다시 수행함.
        """
        if self._color == value:
            return
        self._color = pg.Color(value)
        self.render_text()

    @property
    def alpha(self) -> int:
        """텍스트의 투명도(0-255)를 반환함."""
        return self._alpha

    @alpha.setter
    def alpha(self, value: int):
        """
        텍스트의 투명도를 설정함.
        
        값이 변경될 때만 이미지에 투명도 설정을 적용함.
        """
        # 투명도 값을 0-255 범위로 제한함.
        new_alpha = max(0, min(255, value))
        if self._alpha == new_alpha:
            return
        
        self._alpha = new_alpha
        # 이미지가 존재하는 경우에만 투명도를 설정함.
        if hasattr(self, 'image'):
            self.image.set_alpha(self._alpha)

    @property
    def text(self) -> str:
        """렌더링할 텍스트 내용을 반환함."""
        return self._text

    @text.setter
    def text(self, value: str):
        """
        텍스트 내용을 설정하고 이미지를 다시 렌더링함.
        
        값이 변경될 때만 렌더링 과정을 다시 수행함.
        """
        if self._text == value:
            return
        self._text = value
        self.render_text()
        
    def render_text(self):
        """
        텍스트 내용과 색상이 변경될 때마다 원본 텍스트 서피스를 새로 렌더링함.
        
        이 메서드는 텍스트 내용이나 색상이 바뀔 때만 호출되어야 함.
        """
        # 텍스트가 비어있으면 1x1 투명 서피스를 생성함.
        if not self.text.strip():
            self._base_surface = pg.Surface((1, 1), pg.SRCALPHA)
            self._base_surface.set_alpha(self._alpha)
            self.scale_and_set_image()
            return
            
        # 여러 줄의 텍스트를 분리함.
        lines = self.text.splitlines()
        # 각 줄을 폰트로 렌더링함.
        rendered_lines = [self.font.render(line, True, self._color) for line in lines]

        # 모든 줄을 담을 서피스의 크기를 계산함.
        width = max(line.get_width() for line in rendered_lines)
        height = sum(line.get_height() for line in rendered_lines)

        # 여러 줄을 합칠 베이스 서피스를 생성하고, 각 줄을 blit함.
        self._base_surface = pg.Surface((width, height), pg.SRCALPHA)
        y_offset = 0
        for line in rendered_lines:
            self._base_surface.blit(line, (0, y_offset))
            y_offset += line.get_height()
            
        # 텍스트 렌더링 후 스케일 및 알파값을 적용해서 최종 이미지를 만듦.
        self.scale_and_set_image()
        
    def scale_and_set_image(self):
        """
        _base_surface를 스케일링하고 투명도를 적용해서 최종 이미지(self.image)를 만듦.
        
        이 메서드는 텍스트 내용/색상 변경, 스케일 변경 시 호출됨.
        """
        # _base_surface가 없으면(텍스트가 비어있을 때) 함수를 종료함.
        if self._base_surface is None:
            return

        # 스케일이 1이 아닌 경우 이미지를 스케일링함.
        if self.scale != 1.0:
            scaled_size = (round(self._base_surface.get_width() * self.scale),
                           round(self._base_surface.get_height() * self.scale))
            self.image = pg.transform.scale(self._base_surface, scaled_size)
        # 스케일이 1인 경우 원본 서피스를 그대로 사용함.
        else:
            self.image = self._base_surface.copy()

        # 최종 이미지에 투명도를 적용함.
        self.image.set_alpha(self.alpha)
        
    def draw(self):
        """
        텍스트 렌더러를 화면에 그림.
        
        투명도가 0보다 클 경우에만 그림. 
        use_camera 설정에 따라 월드 좌표를 화면 좌표로 변환함.
        """
        # 투명도가 0 이하면 그릴 필요가 없으므로 반환함.
        if self.alpha <= 0:
            return

        # 텍스트를 그릴 서피스 지정
        surface = self.app.surfaces[LAYER_INTERFACE]

        # 그릴 위치를 화면 좌표로 초기화함.
        draw_pos = self.screen_pos
        
        # use_camera가 True일 경우 월드 좌표를 화면 좌표로 변환함.
        if self.use_camera and self.app.scene.camera:
            draw_pos = CameraMath.world_to_screen(self.app.scene.camera, draw_pos)

        # 최종 계산된 위치에 텍스트 이미지를 그림.
        surface.blit(self.image, draw_pos)