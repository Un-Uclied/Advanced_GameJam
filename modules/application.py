# 외부 라이브러리 임포트
import pygame as pg
import pygame.freetype

# 내부 라이브러리 임포트
from .scenes import *  # 씬 클래스들
from .constants import *  # 상수들

class Time:
    elapsed_time : float = 0.0
    elapsed_time_unscaled : float = 0.0

    delta_time : float = 0.0
    delta_time_unscaled : float = 0.0

    time_scale : float = 1.0

#외부 라이브러리 임포트
import pygame as pg

class Events:
    events : list[pg.event.Event] = []


class Application:
    '''
    [ Application 클래스 - 싱글톤 ]
    게임의 메인 루프, 씬 관리, 시간 & 이벤트 업데이트 담당

    ✅ 사용 예시:
        from modules.application import Application
        app = Application.singleton  # Application() 실행 후 접근 가능
        app.change_scene("main_menu_scene")  # 씬 변경

    ✅ 싱글톤으로 만든 이유:
        매번 오브젝트에 screen 같은 거 넘기기 귀찮아서
        그냥 Application.singleton.screen 이런 식으로 바로 접근하려고
    '''
    
    singleton = None  # 싱글톤 인스턴스 저장

    def __init__(self):
        # 싱글톤 중복 생성 방지
        if Application.singleton is not None:
            raise Exception("Application은 싱글톤이야! Application.singleton 써라!")

        Application.singleton = self

        # === 초기화 ===
        pg.init()
        pygame.freetype.init()

        self.screen = pg.display.set_mode(APPLICATION_RESOLUTION, vsync=1)
        pg.display.set_caption(APPLICATION_NAME)

        self.clock = pg.time.Clock()
        self.is_running = True

        self.update_time()    # 첫 프레임 시간 초기화
        self.update_events()  # 첫 프레임 이벤트 초기화

        # === 씬 등록 및 초기 진입 ===
        self.scenes_registered = {
            "test_scene": TestScene()
        }
        self.scene = self.scenes_registered["test_scene"]
        self.scene.scene_enter()

    # === 시간 업데이트 ===
    def update_time(self):
        '''
        매 프레임 시간 업데이트 (Time 클래스에 기록됨)
        '''
        dt = self.clock.tick(APPLICATION_TARGET_FPS) / 1000
        Time.delta_time_unscaled = dt
        Time.delta_time = dt * Time.time_scale
        Time.elapsed_time += Time.delta_time
        Time.elapsed_time_unscaled += Time.delta_time_unscaled

    # === 이벤트 업데이트 ===
    def update_events(self):
        '''
        매 프레임 pygame 이벤트를 받아 Events.events에 저장
        (다른 곳에서 재활용하려고)
        '''
        Events.events = pg.event.get()

    # === 씬 변경 ===
    def change_scene(self, scene_name: str):
        '''
        씬 전환 (씬 나가기 → 씬 진입)
        '''
        self.scene.scene_exit()
        self.scene = self.scenes_registered[scene_name]
        self.scene.scene_enter()

    # === 창 닫기 처리 ===
    def check_quit(self):
        '''
        창 닫기 이벤트가 들어오면 게임 루프 종료
        '''
        for event in Events.events:
            if event.type == pg.QUIT:
                self.is_running = False

    # === 게임 루프 시작 ===
    def run(self):
        '''
        메인 게임 루프: 이벤트 → 업데이트 → 그리기 → 화면 갱신 순서로 동작
        '''
        while self.is_running:
            self.update_events()
            self.check_quit()

            self.scene.update()

            self.screen.fill("grey")  # 배경색
            self.scene.draw()

            pg.display.flip()
            self.update_time()

        # 게임 종료 처리
        pg.quit()