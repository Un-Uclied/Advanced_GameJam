import pygame as pg

from scripts.constants import *
from scripts.objects import *

from .light import Light

class Fog(GameObject):
    '''쉐이더 없이 빛 효과 만점'''
    '''성능 많이 잡아먹음'''
    '''화면 전체를 덮지 않고, 오브젝트와 엔티티만 안개 처리가 됨.'''
    '''(화면 전체를 덮으면 너무 어두워서)'''

    '''예시 : 사과 모양의 검은 종이를 사과 앞에 갖다대면 사과가 전부 검정색으로 보임.'''
    '''사과 모양의 종이에 구멍을 내면 구멍을 낸곳에만 사과가 일부 보임.'''

    def __init__(self, fog_color : pg.Color = pg.Color(0, 0, 0, 250)):
        super().__init__()
        self.fog_color = fog_color
        self.fog_surface = pg.Surface(SCREEN_SIZE, flags=pg.SRCALPHA)

    def draw(self):
        super().draw()
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