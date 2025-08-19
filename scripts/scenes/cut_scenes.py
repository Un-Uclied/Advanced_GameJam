import pygame as pg
from scripts.constants import *
from scripts.utils import *
from scripts.ui import *
from .base import Scene


class CutScenePlayer:
    """
    컷씬의 UI 재생 및 관련 로직을 관리하는 클래스
    
    Args:
        scene: 현재 씬 객체
        cutscene_name (str): 재생할 컷씬의 이름 (json 파일명)
        on_end_callback (callable): 컷씬 종료 시 호출될 콜백 함수
        text_color (pg.Color): 텍스트 색상
        
    Attributes:
        scene: 씬 객체 참조
        _cutscene_ui: 컷씬 UI 객체
    """
    def __init__(self, scene, cutscene_name, on_end_callback, text_color):
        """
        컷씬 플레이어 초기화 및 컷씬 UI 생성
        """
        self.scene = scene  # 씬 참조
        # 컷씬 UI 게임오브젝트 생성
        self._cutscene_ui = CutScene(
            cutscene_name,
            on_end_callback,
            text_color
        )


class CutSceneBase(Scene):
    """
    모든 컷씬의 기본 동작을 담당하는 베이스 클래스
    
    Attributes:
        _cutscene_player: 컷씬 재생을 담당하는 객체
        cutscene_name (str): 컷씬 이름
        next_chapter (int): 다음 챕터
        next_level (int): 다음 레벨
        bg_color (pg.Color): 배경 색상
        first_start_flag (str): 첫 시작 플래그
    """
    def __init__(self, cutscene_name, next_chapter=None, next_level=None, bg_color=pg.Color("black"), first_start_flag=None):
        """
        컷씬 씬 초기화
        """
        super().__init__()
        self.cutscene_name = cutscene_name
        self.next_chapter = next_chapter
        self.next_level = next_level
        self.bg_color = bg_color
        self.first_start_flag = first_start_flag
        self._cutscene_player = None # 컷씬 플레이어 객체는 나중에 생성

    def on_scene_start(self):
        """
        씬 시작 시 호출됨. 컷씬 UI를 생성하고 재생
        """
        super().on_scene_start()
        # 텍스트 색상 설정
        text_color = pg.Color("white") if self.bg_color == pg.Color("black") else pg.Color("black")
        
        # 컷씬 재생을 담당하는 객체 생성
        self._cutscene_player = CutScenePlayer(self, self.cutscene_name, self.cut_scene_end, text_color)

    def cut_scene_end(self):
        '''
        컷씬이 끝났을 때 행동 취하기
        '''
        # 게임 오프닝 씬일 때
        if self.first_start_flag is not None:
            self.app.player_data[self.first_start_flag] = False

        if self.next_chapter is not None and self.next_level is not None:
            # 메인 게임으로 가기
            main_game = self.app.registered_scenes["main_game_scene"]
            main_game.current_chapter = self.next_chapter
            main_game.current_level = self.next_level
            self.app.change_scene("main_game_scene")
        else:
            # 메인 메뉴로 가기
            self.app.change_scene("main_menu_scene")

    def draw(self):
        """
        씬의 모든 요소를 그림
        """
        # self.app.surfaces[LAYER_INTERFACE]에 self.bg_color를 칠함
        surface = self.app.surfaces[LAYER_INTERFACE]
        pg.draw.rect(surface, self.bg_color, surface.get_rect())
        super().draw()


# 컷씬 설정 데이터
CUTSCENE_CONFIG = {
    "OpeningScene": dict(cutscene_name="opening", first_start_flag="is_first_start"),
    "Tutorial1Scene": dict(cutscene_name="tutorial_1", next_chapter=1, next_level=0),
    "Tutorial2Scene": dict(cutscene_name="tutorial_2", next_chapter=1, next_level=1),
    "NoLightCutScene": dict(cutscene_name="no_lights", next_chapter=3, next_level=4),
    "NoSoulsCutScene": dict(cutscene_name="no_souls", next_chapter=2, next_level=2),
    "GoodEndingCutScene": dict(cutscene_name="good_ending", bg_color=pg.Color("white")),
    "BadEndingCutScene": dict(cutscene_name="bad_ending", next_chapter=4, next_level=0, bg_color=pg.Color("red")),
    "BossIntroCutScene": dict(cutscene_name="boss_intro", next_chapter=4, next_level=0),
}

# 동적으로 클래스 생성하는 꼼수
# type(클래스 이름, 상속할 클래스 튜플, 클래스 속성 딕셔너리) → 새로운 클래스 반환
# 여기서는 CUTSCENE_CONFIG 딕셔너리를 돌면서, 각각에 맞는 CutSceneBase 서브클래스를 자동 생성함
# globals()에 새로 만든 클래스들을 등록해서, 실제 모듈 전역에 존재하게 함
globals().update({
    name: type( # type()으로 클래스 동적 생성
        name, # 클래스 이름 (문자열)
        (CutSceneBase,), # 상속받을 부모 클래스 (CutSceneBase 하나)
        {
            # __init__ 메서드 정의
            # cfg=cfg는 파이썬 클로저 늪(변수 참조 문제) 방지용 → 현재 반복 중인 cfg 값 고정
            "__init__": lambda self, cfg=cfg: CutSceneBase.__init__(self, **cfg)
        }
    )
    for name, cfg in CUTSCENE_CONFIG.items() # CUTSCENE_CONFIG를 돌면서 name=클래스이름, cfg=설정값 dict
})