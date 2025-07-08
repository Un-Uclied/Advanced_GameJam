#외부 라이브러리 임포트
import pygame as pg
import pygame.freetype

#내부 라이브러리 임포트
from .scenes import MainMenuScene
from .constants import APPLICATION_RESOLUTION, APPLICATION_NAME, APPLICATION_TARGET_FPS

from .time import Time
from .events import Events

class Application:
    singleton = None # from .application import Application을 함수나 메소드 밖에서 쓰면 순환참조 일어나니깐 조심
    def __init__(self):
        if Application.singleton is not None:
            raise Exception("어허 싱글톤 클래스인데 또 생성하려고 하네? Application()말고 Application.singleton ㄱㄱ")
        Application.singleton = self

        #초기화
        pg.init()
        pygame.freetype.init()
        self.screen = pg.display.set_mode(APPLICATION_RESOLUTION, vsync=1)
        pg.display.set_caption(APPLICATION_NAME)

        self.clock = pg.time.Clock()
        self.is_running = True

        self.update_time()
        self.update_events()
        
        #씬
        self.scenes_registered = {
            "main_menu_scene" : MainMenuScene()
        }
        self.scene = self.scenes_registered["main_menu_scene"]
        self.scene.scene_enter()
    
    #시간 업데이트
    def update_time(self):
        dt = self.clock.tick(APPLICATION_TARGET_FPS) / 1000
        Time.delta_time_unscaled = dt
        Time.delta_time = dt * Time.time_scale

        Time.elapsed_time += Time.delta_time
        Time.elapsed_time_unscaled += Time.delta_time_unscaled

    #이벤트 업데이트
    def update_events(self):
        Events.events = pg.event.get() #얘가 한 프레임에 여러번 부르면 좀 렉? 걸려서 Events에 저장해서 재활용 하는 방법으로 갈거

    #씬 변경 (나중에 씬 트랜지션도 필요함)
    def change_scene(self, scene_name : str):
        self.scene.scene_exit() #기존씬 나가는 함수
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
            self.scene.draw()
            
            pg.display.flip() #업뎃
            self.update_time()

        pg.quit()