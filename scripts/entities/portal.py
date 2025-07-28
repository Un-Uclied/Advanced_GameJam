import pygame as pg

HIT_BOX_SIZE = (180, 165)

LIGHT_SIZE = 500

from .base import Entity
class Portal(Entity):
    def __init__(self, spawn_position : pg.Vector2):
        rect = pg.Rect(spawn_position, HIT_BOX_SIZE)
        super().__init__("portal", rect)

        # 포탈은 직접 빛 생성
        from scripts.volume import Light
        self.light = Light(LIGHT_SIZE, pg.Vector2(self.rect.center))

    def update(self):
        super().update()

        ps = self.app.scene.player_status
        pc = ps.player_character
        
        # F키 누르면 MainGameScene.on_level_end()를 불러서 다음 레벨로 감
        if self.rect.colliderect(pc.rect):
            for event in self.app.events:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_f:
                        self.app.scene.on_level_end()