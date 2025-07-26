import random
import copy

from .base.scene import Scene

from scripts.objects import GameObject
from scripts.entities.base import Entity
from scripts.projectiles.base import Projectile
from scripts.vfx import Outline, AnimatedParticle
from scripts.status import PlayerStatus
from scripts.tilemap import Tilemap, spawn_all_entities
from scripts.volume import Fog, Sky, Clouds

TILEMAP_LEVEL_COUNT = {
    "0" : 3,
    "1" : 3,
    "2" : 4,
    "3" : 4,
    "4" : 5,
    "5" : 5,
    "6" : 1,
}

TILEMAP_WORLDS = {
    "0" : ["difficulty_0/a.json", "difficulty_0/b.json", "difficulty_0/c.json", "difficulty_0/d.json", "difficulty_0/e.json"],
    "1" : ["difficulty_1/a.json", "difficulty_1/b.json", "difficulty_1/c.json", "difficulty_1/d.json", "difficulty_1/e.json"],
    "2" : ["difficulty_2/a.json", "difficulty_2/b.json", "difficulty_2/c.json", "difficulty_2/d.json", "difficulty_2/e.json", "difficulty_2/f.json"],
    "3" : ["difficulty_3/a.json", "difficulty_3/b.json", "difficulty_3/c.json", "difficulty_3/d.json", "difficulty_3/e.json", "difficulty_3/f.json"],
    "4" : ["difficulty_4/a.json", "difficulty_4/b.json", "difficulty_4/c.json", "difficulty_4/d.json", "difficulty_4/e.json", "difficulty_4/f.json", "difficulty_4/g.json"],
    "5" : ["difficulty_5/a.json", "difficulty_5/b.json", "difficulty_5/c.json", "difficulty_5/d.json", "difficulty_5/e.json", "difficulty_5/f.json", "difficulty_5/g.json"],
    "6" : ["difficulty_6/a.json"],
}


class MainGameScene(Scene):
    def on_scene_start(self):
        super().on_scene_start()
        
        PlayerStatus()

        self.level_count = 0
        self.current_difficulty = 0

        self.remaining_tilemap_world = copy.deepcopy(TILEMAP_WORLDS)

        self.load_new_world()
        
        Sky()
        Clouds()
        Fog()

    def load_new_world(self):
        self.tilemap = Tilemap(random.choice(self.remaining_tilemap_world[str(self.current_difficulty)]))

        #야들 없앨때 Entity.on_destroy()를 안부르고 이렇게 하는 이유가 그걸 부르면 효과음이랑 파티클 까지 나와서 이렇게 강제적으로 지움.
        for entity in Entity.all_entities:
            if entity in GameObject.all_objects:
                GameObject.all_objects.remove(entity)
        for projectile in Projectile.all_projectiles:
            if projectile in GameObject.all_objects:
                GameObject.all_objects.remove(projectile)
        for outline in Outline.all_outline:
            if outline in GameObject.all_objects:
                GameObject.all_objects.remove(outline)
        for particle in AnimatedParticle.all_particles:
            if particle in GameObject.all_objects:
                GameObject.all_objects.remove(particle)

        spawn_all_entities(self.tilemap)

    def on_level_end(self):
        self.level_count += 1

        self.remaining_tilemap_world[str(self.current_difficulty)].remove(self.tilemap.json_file_name)

        if self.level_count >= TILEMAP_LEVEL_COUNT[str(self.current_difficulty)]:
            self.level_count = 0
            self.current_difficulty += 1

        self.load_new_world()