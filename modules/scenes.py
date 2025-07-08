#외부 라이브러리 임포트
import pygame as pg
import pygame.freetype

class Scene:
    def __init__(self): #여기엔 게임이 시작될때. 이미지나 다른 에
        pass

    def scene_enter(self): #플레이어나 카메라 인스턴스 만들기
        pass

    def scene_exit(self):
        pass
        
    def update(self):
        pass

    def draw(self):
        pass

from .core import * # 씬은 코어에 없으니깐 ㄱㅊ

class MainMenuScene(Scene):
    def __init__(self):
        super().__init__()

    def scene_enter(self):
        super().scene_enter()

        self.grid = GameObject(position=pg.Vector2(0, 0), rotation=0.0)
        self.grid.add_component(SpriteRenderer(load_image("grid.jpg")))

        self.player = GameObject(position=pg.Vector2(0, 0), rotation=0.0)
        self.player.add_component(SpriteRenderer(load_image()))

        Camera2D.scale = 0.1


    def scene_exit(self):
        super().scene_exit()

    def update(self):
        super().update()
        for obj in Object.all_objects:
            obj.update()

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

        print(f"Camera Scale: {Camera2D.scale}, Offset: {Camera2D.offset}, Anchor: {Camera2D.anchor}")
        
    def draw(self):
        super().draw()
        for obj in Object.all_objects:
            obj.draw()
        