import pygame as pg
import pygame.freetype

class TextRenderer:
    def __init__(
        self,
        font: pygame.freetype.Font,
        text: str,
        pos: pg.Vector2,
        fg_color: pygame.Color = "black",
        bg_color: pygame.Color = None,
        rotation: int = 0,
        size: float = 10,
        use_camera: bool = False,  # <- 카메라 적용할지 여부
    ):
        self.font = font
        self.text = text
        self.pos = pos

        self.fg_color = fg_color
        self.bg_color = bg_color

        self.rotation = rotation
        self.size = size
        self.use_camera = use_camera  # ← UI면 False, 월드 텍스트면 True

    def draw(self, target_screen: pg.Surface, camera=None):
        render_pos = self.pos

        # 카메라 적용할 경우
        if self.use_camera and camera:
            render_pos = (self.pos - camera.offset) * camera.scale

        # 위치 정수로 바꿔서 안 깨지게
        render_rect = pg.Rect(int(render_pos.x), int(render_pos.y), 0, 0)

        self.font.render_to(
            target_screen,
            render_rect,
            self.text,
            self.fg_color,
            self.bg_color,
            rotation=self.rotation,
            size=self.size * (camera.scale if self.use_camera and camera else 1),
        )