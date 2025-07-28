import pygame as pg
import random

from scripts.constants import *
from scripts.camera import *

CLOUD_MIN_SPEED = .45
CLOUD_MAX_SPEED = 1.2

CLOUD_MIN_DEPTH = .2
CLOUD_MAX_DEPTH = .8

CLOUD_ALPHA = 65

class Cloud:
    '''GameObject를 상속 안해서 Clouds에서 생성, 관리, 제거'''
    def __init__(self, pos: pg.Vector2, img: pg.Surface, speed: float, depth: float):
        '''구름 만들꺼면 Clouds쓰세여'''
        self.pos = pos
        
        self.img = img
        self.size = pg.Vector2(self.img.get_size())
        
        self.speed = speed
        self.depth = depth

        self.img.set_alpha(CLOUD_ALPHA)

    def update(self):
        self.pos.x += self.speed

    def draw(self, camera : Camera2D, surface : pg.Surface):
        depth_pos = self.pos - (camera.position * self.depth)   #depth에 따라 카메라가 스크롤하는 량이 달라짐. (Parallax 효과 만들기)

        #화면 밖으로 나가면 다시 반대편으로 갖고오기
        clamped_x = depth_pos.x % (SCREEN_SIZE.x + self.size.x) - self.size.x
        clamped_y = depth_pos.y % (SCREEN_SIZE.y + self.size.y) - self.size.y

        screen_pos = pg.Vector2(clamped_x, clamped_y)
        surface.blit(self.img, screen_pos)

from scripts.objects import GameObject
class Clouds(GameObject):
    def __init__(self, cloud_count: int = 16):
        '''구름 이펙트 추가!! 구름은 끝없이 스크롤 되니깐 cloud_count그리 안올려도 됨'''
        super().__init__()
        cloud_images = self.app.ASSETS["backgrounds"]["clouds"]
        self.all_clouds : list[Cloud] = []

        for _ in range(cloud_count):
            #랜덤한 위치, 랜덤한 이미지, 랜덤한 속도, 랜덤한 깊이로 구름 생성
            pos = pg.Vector2(random.random() * 99999, random.random() * 99999)
            img = random.choice(cloud_images)
            speed = random.uniform(CLOUD_MIN_SPEED, CLOUD_MAX_SPEED)
            depth = random.uniform(CLOUD_MIN_DEPTH, CLOUD_MAX_DEPTH)
            self.all_clouds.append(Cloud(pos, img, speed, depth))

        #깊이별로 정렬
        self.all_clouds.sort(key=lambda cloud: cloud.depth)

    def update(self):
        super().update()
        for cloud in self.all_clouds:
            cloud.update()

    def draw(self):
        super().draw()
        for cloud in self.all_clouds:
            cloud.draw(self.app.scene.camera, self.app.surfaces[LAYER_BG])