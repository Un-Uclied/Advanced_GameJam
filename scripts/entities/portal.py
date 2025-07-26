import pygame as pg

from .base import Entity

hit_box_size = (180, 165)

class Portal(Entity):
    def __init__(self, spawn_position : pg.Vector2):
        rect = pg.Rect(spawn_position, hit_box_size)
        super().__init__("portal", rect)

        from scripts.volume import Light
        self.light = Light(500, pg.Vector2(self.rect.center), 50)

    def on_update(self):
        super().on_update()

        from scripts.entities import PlayerCharacter
        pc = PlayerCharacter.singleton
        
        if self.rect.colliderect(pc.rect):
            for event in self.app.events:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_f:
                        self.app.scene.on_level_end()