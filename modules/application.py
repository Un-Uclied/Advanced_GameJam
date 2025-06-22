#외부 라이브러리 임포트
import pygame as pg
import pygame.freetype

#내부 라이브러리 임포트
from .camera import Camera2D
from .scenes import MainMenuScene

#윈도우 설정
APPLICATION_NAME = "Game Prototype"
APPLICATION_RESOLUTION = (1600, 900)
APPLICATION_TARGET_FPS = 120

class Time:
    delta_time : float = 0.0
    delta_time_unscaled : float = 0.0
    time_scale : float = 0.0

class Events:
    events : list[pg.event.Event] = []

class Camera:
    current : Camera2D = Camera2D(APPLICATION_RESOLUTION)

class Application:
    def __init__(self):
        #초기화
        pg.init()
        self.screen = pg.display.set_mode(APPLICATION_RESOLUTION, vsync=1)
        pg.display.set_caption(APPLICATION_NAME)

        self.clock = pg.time.Clock()
        self.is_running = True

        self.update_time()
        self.update_events()
        
        #씬
        self.scenes_registered = {
            "main_menu_scene" : MainMenuScene(self)
        }
        self.scene = self.scenes_registered["main_menu_scene"]
        self.scene.scene_enter()
    
    #시간 업데이트
    def update_time(self):
        Time.delta_time_unscaled = self.clock.tick(APPLICATION_TARGET_FPS) / 1000
        Time.delta_time = Time.delta_time_unscaled * Time.time_scale

    #이벤트 업데이트
    def update_events(self):
        Events.events = pg.event.get()

    #씬 변경 (나중에 씬 트랜지션도 필요함)
    def change_scene(self, scene_name : str):
        self.scene.scene_exit() #기존씬 나가는 함수
        Camera.current.reset() #카메라 리셋 안하면 바뀐 씬에서 원래씬 위치나 그런게 보존 됨. 이건 좀 스파게티긴 한데 접근성 하나만큼은 쩔어서 이거 써야함 ㅇㅇ ^^
        self.scene = self.scenes_registered[scene_name]
        self.scene.scene_enter() #새씬 들어오는 함수

    #창 끄기 체크
    def check_quit(self):
        for event in Events.events:
            if event.type == pg.QUIT:
                self.is_running = False #창 끄기
    
    def run(self):
        while self.is_running:
            self.update_events()
            self.check_quit()

            self.scene.update()

            self.screen.fill("grey")
            self.scene.draw(self.screen)
            
            pg.display.flip() #업뎃
            self.update_time()

        pg.quit()