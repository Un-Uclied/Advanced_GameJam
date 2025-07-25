import pygame as pg

from .base.scene import Scene

from scripts.status import PlayerStatus
from scripts.tilemap import Tilemap, TilemapSpawner

from scripts.volume import Fog, Sky

class MainGameScene(Scene):
    def on_scene_start(self):
        super().on_scene_start()

        PlayerStatus()
        self.tilemap = Tilemap()
        TilemapSpawner.spawn_all(self.tilemap)

        from scripts.entities import PlayerCharacter
        for pos in self.tilemap.get_pos_by_data("spawners", 0):
            self.pc = PlayerCharacter(pos) #플레이어는 예외 적으로 여기서 스폰하면, 다른 게임 오브젝트에서도 self.app.scene.pc이렇게 접근 가능!!
            break
        
        Sky()
        Fog()