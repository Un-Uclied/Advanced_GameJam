import pygame as pg

from scripts.constants import *
from scripts.core import *

from .light import Light

class Fog(GameObject):
    '''성능 많이 잡아먹음
    쉐이더 없이 빛 효과 만점
    성능 많이 잡아먹음
    화면 전체를 덮지 않고, 오브젝트와 엔티티만 안개 처리가 됨.
    (화면 전체를 덮으면 너무 어두워서)

    예시 : 사과 모양의 검은 종이를 사과 앞에 갖다대면 사과가 전부 검정색으로 보임.\n사과 모양의 종이에 구멍을 내면 구멍을 낸곳에만 사과가 일부 보임.
    
    :param fog_color: 오브젝트랑 엔티티 덮을 색
    '''

    def __init__(self, fog_color : pg.Color = pg.Color(0, 0, 0, 250)):
        '''Fog()하고 타일맵 만들면 안되고, 타일맵 만든후에 Fog()하세여'''
        super().__init__()
        self._fog_color = fog_color
        self.fog_surface = pg.Surface(SCREEN_SIZE, flags=pg.SRCALPHA)

    @property
    def fog_color(self):
        # 만약 씬에 player_status가 없으면 메인 게임 씬이 아닌것으로 간주, 별다른 계산 없이 그대로 리턴
        if not hasattr(self.app.scene, "player_status"):
            return self._fog_color
        ps = self.app.scene.player_status
        color = pg.Color(self._fog_color)
        if SOUL_KIND_B in ps.soul_queue:
            color.a -= KIND_B_FOG_ALPHA_DOWN
        return color

    def draw_fill(self):
        '''싸게 그리기 (LAYER_VOLUME 전체를 채움)'''
        self.app.surfaces[LAYER_VOLUME].fill(self.fog_color)
        Light.draw_lights(self.app.scene.camera, self.app.surfaces[LAYER_VOLUME])

    def draw_mult(self):
        '''비싸게 그리기 (BLEND_RGBA_MULT)'''
        #알파 채널도 0으로
        self.fog_surface.fill((0, 0, 0, 0))

        #최적화를 위해 surface를 copy()하지 않고, 오브젝트 (타일맵), 엔티티 (플레이어, 적) surface에 그려진것들을 다시 self.fog_surface에 그림.
        self.fog_surface.blit(self.app.surfaces[LAYER_OBJ])
        self.fog_surface.blit(self.app.surfaces[LAYER_ENTITY])

        #BLEND_RGBA_MULT를 해서 다른 오브젝트들이 그려진 부분에만 색을 덮어 씌움.
        self.fog_surface.fill(self.fog_color, special_flags=pg.BLEND_RGBA_MULT)
            
        #self.fog_surface의 알파 채널값을 빼면 그 만큼 구멍이 생김.
        Light.draw_lights(self.app.scene.camera, self.fog_surface)

        #볼륨 레이어 surface에 최종적으로 그리기
        self.app.surfaces[LAYER_VOLUME].blit(self.fog_surface, (0, 0))

    def draw(self):
        super().draw()
        if hasattr(self.app.scene, "player_status"):
            ps = self.app.scene.player_status
            # SOUL_EVIL_C가 있다면 시야 감소
            if SOUL_EVIL_C in ps.soul_queue:
                self.draw_fill()
            else:
                self.draw_mult()
        else:
            self.draw_mult()