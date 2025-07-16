import pygame as pg
from .constants import *

class Component:
    '''모든 컴포넌트의 베이스 클래스'''
    def __init__(self):
        from .objects import GameObject
        self.game_object : GameObject | None = None  # 컴포넌트를 가진 오브젝트

    def on_start(self):
        '''오브젝트에 붙을 때 1회 호출'''
        pass

    def on_destroy(self):
        '''오브젝트에서 제거될 때 호출'''
        pass

    def update(self):
        '''매 프레임 업데이트'''
        pass

    def draw(self):
        '''매 프레임 그리기'''
        pass

class SpriteRenderer(Component):
    def __init__(self, image: pg.Surface, anchor: pg.Vector2 = pg.Vector2(0.5, 0.5), mask_color : pg.Color = pg.Color(0, 0, 0, 0)):
        super().__init__()
        self._original_image = image # 원본 이미지를 저장하여 매번 스케일링/회전 시 화질 저하 방지
        self.image = image
        self.anchor = anchor
        self.mask_color = mask_color

        '''캐싱 하는 이유가 매 프레임마다 rotate()나 scale() 부르면 성능 나락갈수도 있어서 그럼'''
        self._last_rotation = None # 이전 회전값을 캐싱하여 불필요한 연산 방지
        self._last_scale_factor = None # 이전 스케일값을 캐싱하여 불필요한 연산 방지
        self._last_gameobject_scale = None # GameObject의 이전 스케일값을 캐싱

        # 마스크 색상 적용 (최초 한 번만 적용)
        if self.mask_color.a != 0: # 알파값이 0이 아니면 마스크 색상으로 간주
            self._original_image.set_colorkey(self.mask_color)
            self.image.set_colorkey(self.mask_color) # 현재 image에도 적용

    def draw(self):
        #순환 참조 무서웡..
        from .camera import Camera2D
        from .application import Application

        game_object = self.game_object

        # 오브젝트의 월드 포지션
        pos = game_object.position

        # 총 스케일 계산: 카메라 스케일 * 오브젝트 스케일
        total_scale_x = Camera2D.scale * game_object.scale.x
        total_scale_y = Camera2D.scale * game_object.scale.y
        current_scale_factor = (total_scale_x, total_scale_y)

        # 이미지 변환 (회전, 스케일링) 최적화!!
        # 회전, 스케일, GameObject 스케일 중 하나라도 바뀌면 이미지 합성
        if (game_object.rotation != self._last_rotation or
            current_scale_factor != self._last_scale_factor or
            game_object.scale != self._last_gameobject_scale):
            

            scaled_by_object_and_camera_x = int(self._original_image.get_width() * total_scale_x)
            scaled_by_object_and_camera_y = int(self._original_image.get_height() * total_scale_y)

            # 스케일링된 이미지
            if scaled_by_object_and_camera_x > 0 and scaled_by_object_and_camera_y > 0:
                self.image = pg.transform.scale(
                    self._original_image, 
                    (scaled_by_object_and_camera_x, scaled_by_object_and_camera_y)
                )
            else: # 스케일이 0이거나 음수일 경우 렌더링 안함
                return 

            # 스케일링된 이미지를 회전
            self.image = pg.transform.rotate(self.image, game_object.rotation)

            # 캐시 업데이트
            self._last_rotation = game_object.rotation
            self._last_scale_factor = current_scale_factor
            self._last_gameobject_scale = game_object.scale

        # 이미지 크기 가져오기 (변환된 이미지의 크기)
        img_size = pg.Vector2(self.image.get_size())

        # 그리기 위치 계산 (월드 -> 스크린 -> 앵커 적용)
        draw_pos_screen = Camera2D.world_to_screen(pos)
        final_draw_pos = draw_pos_screen - img_size.elementwise() * self.anchor

        # 화면에 그리기
        Application.singleton.screen.blit(self.image, final_draw_pos)

class ObjectDebugger(Component):
    def __init__(self):
        super().__init__()

    def draw(self):
        if not self.game_object:
            return

        from .camera import Camera2D
        from .application import Application
        screen = Application.singleton.screen
        pos = self.game_object.position

        # 위쪽 방향 (빨간 선)
        pg.draw.line(screen, pg.Color(255, 0, 0), 
                     Camera2D.world_to_screen(pos),
                     Camera2D.world_to_screen(pos + self.game_object.up * 500), 20)

        # 오른쪽 방향 (초록 선)
        pg.draw.line(screen, pg.Color(0, 255, 0),
                     Camera2D.world_to_screen(pos),
                     Camera2D.world_to_screen(pos + self.game_object.right * 500), 20)

        # 중심점 (노란 점)
        pg.draw.circle(screen, pg.Color(255, 255, 0),
                       Camera2D.world_to_screen(pos), 10)

class TextRenderer(Component):
    def __init__(self, text: str, font_size: int = 24,
                 color: pg.Color = pg.Color(255, 255, 255),
                 font_name="Galmuri11.ttf"):
        super().__init__()
        self.text = text
        self.font_size = font_size
        self.color = color
        self.font = pg.freetype.Font(DEFAULT_FONT_PATH + font_name, font_size)

    def draw(self):
        if not self.game_object:
            return

        from .camera import Camera2D
        from .application import Application
        pos = Camera2D.world_to_screen(self.game_object.position)
        self.font.render_to(Application.singleton.screen, pos, self.text, self.color)