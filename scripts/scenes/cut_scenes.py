import pygame as pg
from scripts.constants import *
from scripts.core import *
from scripts.ui import *
from .base import Scene

class CutSceneBase(Scene):
    """
    모든 컷씬의 기본 동작을 담당하는 베이스 클래스
    """
    def __init__(self, cutscene_name, next_chapter=None, next_level=None, bg_color=pg.Color("black"), first_start_flag=None):
        super().__init__()
        self.cutscene_name = cutscene_name
        self.next_chapter = next_chapter
        self.next_level = next_level
        self.bg_color = bg_color
        self.first_start_flag = first_start_flag

    def on_scene_start(self):
        # 텍스트 색상 설정
        text_color = pg.Color("white") if self.bg_color == pg.Color("black") else pg.Color("black")
        # 컷씬 게임오브젝트 생성
        CutScene(self.cutscene_name, self.cut_scene_end, text_color)
        # 컷씬도 씬이라 super().on_scene_start()불러줘야함
        super().on_scene_start()

    def cut_scene_end(self):
        '''
        컷씬이 끝났을때 행동 취하기
        '''
        # 게임 오프닝 씬일때
        if self.first_start_flag is not None:
            self.app.player_data[self.first_start_flag] = False

        if self.next_chapter is not None and self.next_level is not None:
            # 메인게임으로 가기
            main_game = self.app.registered_scenes["main_game_scene"]
            main_game.current_chapter = self.next_chapter
            main_game.current_level = self.next_level
            self.app.change_scene("main_game_scene")
        else:
            # 메인 메뉴로 가기
            self.app.change_scene("main_menu_scene")

    def draw(self):
        # self.app.surfaces[LAYER_INTERFACE]에 self.bg_color를 칠함
        surface = self.app.surfaces[LAYER_INTERFACE]
        pg.draw.rect(surface, self.bg_color, surface.get_rect())
        super().draw()


# 컷씬 설정 데이터
CUTSCENE_CONFIG = {
    "OpeningScene":  dict(cutscene_name="opening", first_start_flag="is_first_start"),
    "Tutorial1Scene": dict(cutscene_name="tutorial_1", next_chapter=1, next_level=0),
    "Tutorial2Scene": dict(cutscene_name="tutorial_2", next_chapter=1, next_level=1),
    "NoLightCutScene": dict(cutscene_name="no_lights", next_chapter=3, next_level=4),
    "NoSoulsCutScene": dict(cutscene_name="no_souls", next_chapter=2, next_level=2),
    "GoodEndingCutScene": dict(cutscene_name="good_ending", bg_color=pg.Color("white")),
    "BadEndingCutScene": dict(cutscene_name="bad_ending", next_chapter=4, next_level=0, bg_color=pg.Color("red")),
}

# 동적으로 클래스 생성하는 꼼수
# type(클래스 이름, 상속할 클래스 튜플, 클래스 속성 딕셔너리) → 새로운 클래스 반환
# 여기서는 CUTSCENE_CONFIG 딕셔너리를 돌면서, 각각에 맞는 CutSceneBase 서브클래스를 자동 생성함
globals().update({  # globals()에 새로 만든 클래스들을 등록해서, 실제 모듈 전역에 존재하게 함
    name: type(  # type()으로 클래스 동적 생성
        name,  # 클래스 이름 (문자열)
        (CutSceneBase,),  # 상속받을 부모 클래스 (CutSceneBase 하나)
        {
            # __init__ 메서드 정의
            # cfg=cfg는 파이썬 클로저 늪(변수 참조 문제) 방지용 → 현재 반복 중인 cfg 값 고정
            "__init__": lambda self, cfg=cfg: CutSceneBase.__init__(self, **cfg)
        }
    )
    for name, cfg in CUTSCENE_CONFIG.items()  # CUTSCENE_CONFIG를 돌면서 name=클래스이름, cfg=설정값 dict
})

# 예시
# globals().update({"FOO": 123, "BAR": "hello"})
# # 이후 이 모듈의 다른 코드에서 FOO, BAR로 접근 가능함
# print(FOO, BAR)  # 123 hello