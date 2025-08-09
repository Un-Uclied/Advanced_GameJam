import pygame as pg

from scripts.constants import *
from scripts.core import *

from .light import Light

class Fog(GameObject):
    """
    씬 내 오브젝트와 엔티티에 안개 효과를 씌우는 클래스.
    성능은 좀 잡아먹지만, 쉐이더 없이 빛 효과를 극대화함.

    특징:
    - 화면 전체를 덮지 않고, 오브젝트와 엔티티 레이어만 안개 처리
      (전체 화면 덮으면 너무 어두워서 시야 확보 어려움)
    - 빛 효과(Light 클래스)와 함께 사용해 빛 구멍(투명 영역) 표현 가능
    - 플레이어 상태에 따라 안개의 투명도 조절 가능 (예: SOUL_KIND_B 효과)
    - SOUL_EVIL_C가 있으면 단순 채우기 방식(draw_fill)으로 시야 감소 효과 적용

    주의점:
    - 타일맵 생성 후 Fog 생성 해야함 (Fog 생성 전에 타일맵 있으면 렌더 순서 꼬임)

    :param fog_color: 안개 덮을 색상 (알파 포함). 기본은 거의 검정에 가까운 투명도 250
    """

    def __init__(self, fog_color: pg.Color = pg.Color(0, 0, 0, 250)):
        # 생성시 투명 Surface 생성해둠
        super().__init__()
        self._fog_color = fog_color
        self.fog_surface = pg.Surface(SCREEN_SIZE, flags=pg.SRCALPHA)

    @property
    def fog_color(self) -> pg.Color:
        # 씬에 player_status 없으면 메인 게임 씬 아님 → 기본 안개 색 반환
        if not hasattr(self.app.scene, "player_status"):
            return self._fog_color

        ps = self.app.scene.player_status
        color = pg.Color(self._fog_color)

        # SOUL_KIND_B가 있으면 안개 투명도 줄임 (색 알파값 감소)
        if SOUL_KIND_B in ps.soul_queue:
            color.a = max(0, color.a - KIND_B_FOG_ALPHA_DOWN)

        return color

    def draw_fill(self):
        """
        저사양 방식 - LAYER_VOLUME 레이어 전체를 안개 색으로 채움.
        SOUL_EVIL_C 상태일 때 씀.
        """
        self.app.surfaces[LAYER_VOLUME].fill(self.fog_color)
        Light.draw_lights(self.app.scene.camera, self.app.surfaces[LAYER_VOLUME])

    def draw_mult(self):
        """
        고사양 방식 - 오브젝트/엔티티가 그려진 부분만 안개 색 곱하기 (multiply) 처리.
        오브젝트가 있는 곳만 어둡게 표현, 구멍난 듯한 효과 연출 가능.
        """
        # 알파 0으로 초기화
        self.fog_surface.fill((0, 0, 0, 0))

        # 오브젝트, 엔티티 레이어를 안개 Surface에 복사 (최적화를 위해 복사본 X)
        self.fog_surface.blit(self.app.surfaces[LAYER_OBJ], (0, 0))
        self.fog_surface.blit(self.app.surfaces[LAYER_ENTITY], (0, 0))

        # 곱하기(blend multiply)로 안개 색 덮기
        self.fog_surface.fill(self.fog_color, special_flags=pg.BLEND_RGBA_MULT)

        # 빛 효과 적용 (구멍 난 영역 표현)
        Light.draw_lights(self.app.scene.camera, self.fog_surface)

        # 최종적으로 볼륨 레이어에 안개 그리기
        self.app.surfaces[LAYER_VOLUME].blit(self.fog_surface, (0, 0))

    def draw(self):
        """
        매 프레임 호출됨.
        플레이어 상태에 따라 적절한 안개 그리기 방식 선택.
        """
        super().draw()

        if hasattr(self.app.scene, "player_status"):
            ps = self.app.scene.player_status

            # SOUL_EVIL_C 상태면 저사양 채우기 방식, 아니면 곱하기 방식
            if SOUL_EVIL_C in ps.soul_queue:
                self.draw_fill()
            else:
                self.draw_mult()
        else:
            # 플레이어 상태 없으면 기본 곱하기 방식
            self.draw_mult()