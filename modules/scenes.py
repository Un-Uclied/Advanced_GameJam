#외부 라이브러리 임포트
import pygame as pg
import pygame.freetype

class Scene:
    '''씬들의 베이스 클래스'''
    def __init__(self): #여기엔 게임이 시작될때. 이미지나 다른 리소스들 로드할때만 쓰면 됨. 게임 시작될때 딱 한번만 실행
        pass

    def scene_enter(self): #플레이어나 오브젝트 같은거 생성.
        pass

    def scene_exit(self): #여기서 카메라 리셋하고 가야함!! Camera2D.reset()
        pass
        
    def update(self):
        pass

    def draw(self):
        pass

from .objects import *
from .components import *
from .camera import Camera2D
from .events import Events
from .load_image import load_image
from .time import Time

class MainMenuScene(Scene):
    def __init__(self):
        super().__init__()

    def scene_enter(self):
        super().scene_enter()

        self.grid = GameObject(position=pg.Vector2(0, 0), rotation=0.0, tag="background")
        self.grid.add_component(SpriteRenderer(load_image("grid.jpg"))) #이렇게 이미지 로드해서 컴포넌트로 추가

        self.player = GameObject(position=pg.Vector2(0, 0), rotation=0.0, tag="entities")
        self.player.add_component(SpriteRenderer(load_image()))
        self.player.add_component(ObjectDebugger()) #디버거 컴포넌트 추가

        Camera2D.scale = 0.5

    def scene_exit(self):
        super().scene_exit()

    def test(self):
        #테스트용
        keys = Events.keys_pressed() 
        if keys[pg.K_w]:
            self.player.position += self.player.up * 500 * Time.delta_time
        if keys[pg.K_s]:
            self.player.position -= self.player.up * 500 * Time.delta_time
        if keys[pg.K_a]:
            self.player.position -= self.player.right * 500 * Time.delta_time
        if keys[pg.K_d]:
            self.player.position += self.player.right * 500 * Time.delta_time

        if keys[pg.K_q]:
            Camera2D.scale *= 1.01
        if keys[pg.K_e]:
            Camera2D.scale /= 1.01

        Camera2D.offset = pg.Vector2.lerp(Camera2D.offset, self.player.position, Time.delta_time * 7)

        self.player.angle -= 20 * Time.delta_time #플레이어 회전
        print(f"Camera Scale: {Camera2D.scale}, Offset: {Camera2D.offset}, Anchor: {Camera2D.anchor}")

    def update(self):
        super().update()
        Object.update_all() #모든 오브젝트 업데이트

        self.test() #테스트용 메소드 호출
        
        
    def draw(self):
        super().draw()
        Object.draw_all() #모든 오브젝트 그리기
