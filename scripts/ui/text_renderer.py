import pygame as pg

from scripts.constants import *
from scripts.camera import *
from scripts.core import *

BASE_FONT_PATH = "assets/fonts/"

class TextRenderer(GameObject):
    """
    UI 텍스트 렌더러 클래스

    특징:
    - 런타임 중 텍스트, 색상, 위치, 스케일, 알파값 자유롭게 변경 가능
    - 폰트는 생성 시 로드 (성능 최적화용)
    - 앵커(기준점) 지정 가능 (좌상단, 중앙 등)
    - 월드 좌표 대응 옵션(use_camera)
    - 줄바꿈 지원

    Args:
        start_text (str): 초기 텍스트 내용
        position (pg.Vector2): 화면 또는 월드 위치
        font_name (str): 폰트 이름 (ASSETS["fonts"]에 등록된 키)
        font_size (int): 폰트 크기
        color (pg.Color): 텍스트 색상
        anchor (pg.Vector2): 기준점 (0,0: 좌상단, 0.5,0.5: 중앙)
        use_camera (bool): True면 월드 좌표 + 카메라 적용
    """
    def __init__(self,
                 start_text: str,
                 position: pg.Vector2,
                 font_name: str = "default",
                 font_size: int = 24,
                 color: pg.Color = pg.Color("white"),
                 anchor: pg.Vector2 = pg.Vector2(0, 0),
                 use_camera: bool = False):
        super().__init__()

        self._text = start_text
        self.pos = position
        self.anchor = anchor
        self.use_camera = use_camera

        self._color = pg.Color(color)
        self._alpha = 255
        self._scale = 1  # 스케일 기본값

        font_path = BASE_FONT_PATH + self.app.ASSETS["fonts"][font_name]
        self.font = pg.font.Font(font_path, font_size)

        self._render_text_image()

    @property
    def scale(self):
        return self._scale
    
    @scale.setter
    def scale(self, value):
        if self._scale == value:
            return
        self._scale = value
        self._render_text_image()

    @property
    def size(self) -> pg.Vector2:
        """현재 렌더된 텍스트 이미지 크기 반환 (스케일 적용 포함)"""
        return pg.Vector2(self.image.get_size())

    @property
    def screen_pos(self) -> pg.Vector2:
        """앵커 기준으로 계산된 화면 그릴 좌표"""
        return self.pos - self.size.elementwise() * self.anchor

    @property
    def rect(self) -> pg.Rect:
        """마우스 충돌 체크용 텍스트 사각형"""
        return pg.Rect(self.screen_pos, self.size)

    @property
    def color(self) -> pg.Color:
        return self._color

    @color.setter
    def color(self, value: pg.Color):
        self._color = pg.Color(value)
        self._render_text_image()

    @property
    def alpha(self) -> int:
        return self._alpha

    @alpha.setter
    def alpha(self, value: int):
        self._alpha = max(0, min(255, value))
        if hasattr(self, 'image'):
            self.image.set_alpha(self._alpha)

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str):
        self._text = value
        self._render_text_image()

    def _render_text_image(self):
        """텍스트, 색상, 스케일 변화 있을 때마다 이미지 새로 렌더링"""
        if not self._text.strip():
            self.image = pg.Surface((1, 1), pg.SRCALPHA)
            self.image.set_alpha(self._alpha)
            return
        
        lines = self._text.splitlines()
        rendered_lines = [self.font.render(line, True, self._color) for line in lines]

        width = max(line.get_width() for line in rendered_lines)
        height = sum(line.get_height() for line in rendered_lines)

        base_surface = pg.Surface((width, height), pg.SRCALPHA)
        y_offset = 0
        for line in rendered_lines:
            base_surface.blit(line, (0, y_offset))
            y_offset += line.get_height()

        base_surface.set_alpha(self._alpha)

        if self._scale != 1:
            scaled_size = (round(width * self._scale), round(height * self._scale))
            self.image = pg.transform.smoothscale(base_surface, scaled_size)
        else:
            self.image = base_surface

    def draw(self):
        """앵커와 카메라 적용해 화면에 텍스트 그리기"""
        super().draw()

        if self.alpha <= 0:
            return

        surface = self.app.surfaces[LAYER_INTERFACE]

        draw_pos = self.screen_pos
        if self.use_camera:
            draw_pos = CameraMath.world_to_screen(self.app.scene.camera, draw_pos)

        surface.blit(self.image, draw_pos)