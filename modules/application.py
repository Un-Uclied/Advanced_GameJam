#외부 라이브러리 임포트
import pygame as pg
import pygame.freetype

#내부 라이브러리 임포트
from .scenes import MainMenuScene # 여기서 씬들 임포트 하고 Application __init__에서 씬 등록함
from .constants import APPLICATION_RESOLUTION, APPLICATION_NAME, APPLICATION_TARGET_FPS

from .time import Time # Time이랑 Events는 Application에서만 업데이트 함.
from .events import Events

class Application:
    '''
    Application 싱글톤 클래스
    Application()을 실행하면 게임이 시작됨
    Application.singleton을 통해서 다른 모듈에서 Application에 접근 가능
    예시:
    from modules.application import Application
    app = Application.singleton # Application()을 실행한 후에만 접근 가능
    app.change_scene("main_menu_scene") # 씬 변경

    Application()은 게임의 메인 루프를 돌고, 씬을 관리하며, 시간과 이벤트를 업데이트함
    시간과 이벤트는 Application에서만 업데이트 되며, 씬에서는 Time과 Events를 통해 접근함
    씬은 Scene 클래스를 상속받아 구현하며, scene_enter(), scene_exit(), update(), draw() 메소드를 오버라이드하여 사용함
    '''
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

            self.scene.update() #씬 업데이트

            self.screen.fill("grey")
            self.scene.draw() #씬 그리기
            
            pg.display.flip() #업뎃
            self.update_time()

        pg.quit()