#외부 라이브러리 임포트
import pygame as pg
import pygame.freetype
#내부 라이브러리 임포트
from modules.scenes import MainMenuScene

#윈도우 설정
APPLICATION_NAME = "Game Prototype"
APPLICATION_RESOLUTION = (1600, 900)
APPLICATION_TARGET_FPS = 120

class Application:
    def __init__(self):
        #초기화
        pg.init()
        self.screen = pg.display.set_mode(APPLICATION_RESOLUTION)
        pg.display.set_caption(APPLICATION_NAME)

        self.clock = pg.time.Clock()
        self.delta_time = 0
        self.is_running = True

        #현재 있는 이벤트들 (이건 한프레임에 하나 해둬야됨)
        self.events = pg.event.get()
        
        #씬들 딕셔너리
        self.scenes = {
            "main_menu_scene" : MainMenuScene(self)
        }
        self.current_scene = self.scenes["main_menu_scene"]
        self.current_scene.scene_enter()
    
    def change_scene(self, scene_name : str):
        self.current_scene.scene_exit() #기존씬 나가는 함수
        self.current_scene = self.scenes[scene_name]
        self.current_scene.scene_enter() #새씬 들어오는 함수
    
    def run(self):
        while self.is_running:
            self.events = pg.event.get()
            for event in self.events:
                if event.type == pg.QUIT:
                    self.is_running = False #창 끄기

            self.current_scene.update(self.delta_time) #현재씬의 업데이트 함수 부르기

            self.screen.fill((20, 20, 20)) #창 클리어
            self.current_scene.draw(self.screen) #후에 그리기
            

            pg.display.flip() #업뎃
            self.delta_time = self.clock.tick(APPLICATION_TARGET_FPS) / 1000 #델타타임 얻으면서 FPS기달
            print(self.clock.get_fps())

        pg.quit()