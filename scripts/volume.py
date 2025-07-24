import pygame as pg

from datas.const import *
from .objects import *

LIGHT_SEGMENTS = 15
LIGHT_FADE_OUT = 10

class Light2D(GameObject):
    light_list : list['Light2D'] = []
    def __init__(self, radius : float, position : pg.Vector2, strength : float = 25):
        super().__init__()
        Light2D.light_list.append(self)

        self.radius : float = radius

        self.position : pg.Vector2 = position
        self.strength = strength

        self._radius_cache = radius #캐싱해서 fps나락을 방지 (빛의 크기가 달라지지 않을때는 새 surface를 안만들어서 연산량 줄이기)
        
        self.make_surface()

    def make_surface(self):
        self.light_surf = pg.Surface((self.radius, self.radius), pg.SRCALPHA)
        for i in range(LIGHT_SEGMENTS):
            alpha = min(i * self.strength, 255)
            pg.draw.circle(
                self.light_surf,
                (255, 255, 255, alpha),  # 밝은 영역만 뚫리게
                (self.radius / 2, self.radius / 2),
                self.radius / 2 - i * LIGHT_FADE_OUT
            )

    def rect(self):
        p = self.position
        r = self.radius
        return pg.Rect((p.x - r / 2, p.y - r/2), (r, r))

    def on_update(self):
        super().on_update()
        if not self._radius_cache == self.radius:
            self.make_surface()

        self._radius_cache = self.radius
        
    def destroy(self):
        super().destroy()
        Light2D.light_list.remove(self)

#비교적 연산은 가볍지만 그래도 못 생김;;
class LightFog(GameObject):
    def __init__(self, fog_alpha=250):
        super().__init__()
        self.fog_alpha = fog_alpha  # 어두움 정도

    def on_draw(self):
        self.app.surfaces[LAYER_VOLUME].fill(pg.Color(0, 0, 0, self.fog_alpha))

        for light in Light2D.light_list:
            surf = light.light_surf
            pos = self.app.scene.camera.world_to_screen(pg.Vector2(light.position.x - light.radius/2, light.position.y - light.radius/2))
            self.app.surfaces[LAYER_VOLUME].blit(surf, pos, special_flags=pg.BLEND_RGBA_SUB)

#엄청 나게 무거운!!!!
class HeavyFog(GameObject):
    def __init__(self, fog_alpha=250):
        super().__init__()
        self.fog_alpha = fog_alpha
        self.fog_surface = pg.Surface(SCREEN_SIZE, flags=pg.SRCALPHA)

    def on_draw(self):
        self.fog_surface.fill((0, 0, 0, 0)) #알파 까지 지우기 (중요함)

        self.fog_surface.blit(self.app.surfaces[LAYER_OBJ])
        self.fog_surface.blit(self.app.surfaces[LAYER_ENTITY])

        self.fog_surface.fill((0, 0, 0, self.fog_alpha), special_flags=pg.BLEND_RGBA_MULT)

        camera = self.app.scene.camera
        for light in Light2D.light_list:
            screen_pos = camera.world_to_screen(light.position) - pg.Vector2(light.radius / 2, light.radius / 2)
            light_surf = camera.get_scaled_surface(light.light_surf)

            if not camera.is_on_screen(light.rect()) : continue

            self.fog_surface.blit(light_surf, screen_pos, special_flags=pg.BLEND_RGBA_SUB)

        self.app.surfaces[LAYER_VOLUME].blit(self.fog_surface, (0, 0))


