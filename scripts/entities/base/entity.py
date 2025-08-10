import pygame as pg

from scripts.constants import *
from scripts.camera import *
from scripts.core import *

class Entity(GameObject):
    """
    게임 내 모든 캐릭터, 적, 플레이어 등의 기본 엔티티 클래스
    
    Attributes:
        name (str): 엔티티 이름 (애니메이션 키로 사용)
        rect (pg.Rect): 위치 및 크기(히트박스)
        movement (pg.Vector2): 이동 방향과 속도 벡터
        current_action (str): 현재 애니메이션 액션 이름
        invert_x (bool): 애니메이션 좌우 반전 여부 기본 설정
        flip_offset (dict): 좌우 반전 시 위치 보정 벡터
        is_being_drawn (bool): 현재 화면에 그려지고 있는지 여부
    """
    
    def __init__(self, name: str, rect: pg.Rect, start_action: str = "idle", invert_x: bool = False):
        super().__init__()
        
        self.name = name
        self.rect = rect
        self.movement = pg.Vector2()

        self.current_action: str = ""
        self.invert_x = invert_x

        # flip_x가 True/False일 때의 위치 오프셋 (필요시 조절)
        self.flip_offset: dict[bool, pg.Vector2] = {
            False: pg.Vector2(0, 0),
            True: pg.Vector2(0, 0)
        }
        
        self.is_being_drawn = True
        
        self.set_action(start_action)

    def set_action(self, action_name: str):
        """
        현재 액션과 다르면 애니메이션 교체

        Args:
            action_name (str): 변경할 애니메이션 액션 이름
        """
        if self.current_action == action_name:
            return
        self.current_action = action_name
        self.anim = self.app.ASSETS["animations"]["entities"][self.name][action_name].copy()

    def get_rect_points(self) -> list[pg.Vector2]:
        """
        히트박스의 4개 꼭짓점 좌표 반환

        Returns:
            list[pg.Vector2]: 좌상, 우상, 좌하, 우하 점 리스트
        """
        return [
            pg.Vector2(self.rect.topleft),
            pg.Vector2(self.rect.topright),
            pg.Vector2(self.rect.bottomleft),
            pg.Vector2(self.rect.bottomright)
        ]

    def _flip_anim(self):
        """
        이동 방향(x축 속도)에 따라 애니메이션 좌우 반전 설정
        invert_x 플래그와 조합하여 뒤집힘 결정
        """
        direction = int(self.movement.x)
        if direction < 0:
            self.anim.flip_x = not self.invert_x
        elif direction > 0:
            self.anim.flip_x = self.invert_x

    def update(self):
        """
        매 프레임 호출
        - 부모 update 호출
        - 애니메이션 방향 설정
        - 애니메이션 프레임 업데이트
        """
        super().update()
        self._flip_anim()
        self.anim.update(self.app.dt)

    def draw_debug(self):
        """
        디버그용 히트박스 그리기 (노란색 사각형)
        """
        super().draw_debug()
        pg.draw.rect(
            self.app.surfaces[LAYER_INTERFACE],
            "yellow",
            CameraView.world_rect_to_screen(self.app.scene.camera, self.rect),
            width=2
        )

    def draw(self):
        """
        실제 화면에 그리기
        카메라 뷰포트 내에 있을 때만 렌더링
        """
        super().draw()

        cam = self.app.scene.camera
        img = self.anim.img()
        world_pos = pg.Vector2(self.rect.topleft) + self.flip_offset[self.anim.flip_x]
        img_rect = pg.Rect(world_pos, img.get_size())

        self.is_being_drawn = True
        if not CameraView.is_in_view(cam, img_rect):
            self.is_being_drawn = False
            return

        screen_pos = CameraMath.world_to_screen(cam, world_pos)
        self.app.surfaces[LAYER_ENTITY].blit(img, screen_pos)