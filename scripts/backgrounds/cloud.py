import pygame as pg
import random

from scripts.constants import *
from scripts.camera import *
from scripts.utils import *

CLOUD_MIN_SPEED = 1
CLOUD_MAX_SPEED = 3

CLOUD_MIN_DEPTH = .2
CLOUD_MAX_DEPTH = .8

CLOUD_ALPHA = 65


class Cloud(GameObject):
    '''
    구름 이펙트를 생성할때 Clouds()로 생성, Cloud클래스는 외부에서 접근 불가.
    '''
    def __init__(self, pos: pg.Vector2, img: pg.Surface, speed: float, depth: float):
        super().__init__()
        self.pos = pos

        self.img = img
        self.size = pg.Vector2(self.img.get_size())

        self.speed = speed
        self.depth = depth

        self.img.set_alpha(CLOUD_ALPHA)
    
    def update(self):
        super().update()
        self.pos.x += self.speed * self.app.dt * 100

    def draw(self):
        super().draw()
        
        # depth에 따라 카메라가 스크롤하는 량이 달라짐. (Parallax 효과 만들기)
        depth_pos = self.pos - (self.scene.camera.position * self.depth)

        # 화면 밖으로 나가면 다시 반대편으로 갖고오기
        clamped_x = depth_pos.x % (SCREEN_SIZE.x + self.size.x) - self.size.x
        clamped_y = depth_pos.y % (SCREEN_SIZE.y + self.size.y) - self.size.y

        screen_pos = pg.Vector2(clamped_x, clamped_y)
        self.app.surfaces[LAYER_BG].blit(self.img, screen_pos)


class CloudFactory:
    '''
    구름 객체 생성을 전담하는 팩토리 클래스
    '''
    def __init__(self, app):
        self.app = app
        self.cloud_images = self.app.ASSETS["backgrounds"]["clouds"]

    def create_cloud(self) -> Cloud:
        '''
        랜덤한 속성과 이미지로 새로운 구름 객체를 생성하고 반환.
        '''
        pos = pg.Vector2(random.random() * 99999, random.random() * 99999)
        img = random.choice(self.cloud_images)
        speed = random.uniform(CLOUD_MIN_SPEED, CLOUD_MAX_SPEED)
        depth = random.uniform(CLOUD_MIN_DEPTH, CLOUD_MAX_DEPTH)
        return Cloud(pos, img, speed, depth)


class Clouds(GameObject):
    '''
    구름 추가 Sky 생성하고 부르세영
    
    :param cloud_count: 구름 개수
    '''
    def __init__(self, cloud_count: int = 16):
        super().__init__()
        self.cloud_factory = CloudFactory(self.app)  # 팩토리 패턴으로 구름 생성 책임 위임
        self.all_clouds : list[Cloud] = []

        for _ in range(cloud_count):
            cloud = self.cloud_factory.create_cloud()
            self.all_clouds.append(cloud)

        # 깊이별로 정렬
        self.all_clouds.sort(key=lambda cloud: cloud.depth)

    def destroy(self):
        for cloud in self.all_clouds[:]:
            cloud.destroy()
        self.all_clouds.clear()
        super().destroy()