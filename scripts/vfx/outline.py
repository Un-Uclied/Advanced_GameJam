import pygame as pg

from scripts.constants import *
from scripts.camera import *

from scripts.objects import GameObject
class Outline(GameObject):
    '''엔티티만 대상으로 아웃라인 효과'''
    '''성능 꽤 잡아먹음'''
    def __init__(self, entity, color, thickness=1):
        '''엔티티 대상만 Outline되고, 엔티티 없어질때 이거도 destroy()해줘야함!! (경고 : 엔티티 super().__init__()하기전에 불러야함)'''
        super().__init__()
        self.entity = entity #타겟 엔티티
        self.color = color
        self.thickness = thickness

    def draw(self):
        super().draw()

        entity = self.entity
        camera = entity.app.scene.camera
        surface = entity.app.surfaces[LAYER_ENTITY]

        # 월드 위치 계산 (좌상단 기준)
        world_pos = pg.Vector2(entity.rect.topleft) + entity.flip_offset[entity.flip_x]

        # 원본 이미지 처리
        image = entity.anim.img()
        image = pg.transform.flip(image, entity.flip_x, False)
        scaled_image = CameraView.get_scaled_surface(camera, image)

        # 최적화를 위해서 화면에 없으면 렌더 안함
        world_rect = pg.Rect(world_pos, image.get_size())
        if not CameraView.is_in_view(camera, world_rect):
            return

        # 마스크 따기
        mask = pg.mask.from_surface(scaled_image)
        outline_surf = mask.to_surface(setcolor=self.color, unsetcolor=(0, 0, 0, 0))
        outline_surf.set_colorkey((0, 0, 0))

        # 렌더링 위치 계산
        screen_pos = CameraMath.world_to_screen(camera, world_pos)

        # 외곽선 드로우
        for dx in range(-self.thickness, self.thickness + 1):
            for dy in range(-self.thickness, self.thickness + 1):
                if dx or dy:
                    offset = (screen_pos.x + dx, screen_pos.y + dy)
                    surface.blit(outline_surf, offset)