import pygame as pg
import json

from scripts.constants import *
from scripts.core import *
from scripts.ui import *

BASE_CUT_SCENE_DATA_PATH = "data/cut_scene/"
TEXT_CHARACTER_SPEED = 0.05  # 한 글자 출력 간격 (초)
SKIP_HOLD_TIME = 1.0  # ESC 스킵을 위한 최소 홀드 시간 (초)

class CutSceneData:
    """컷씬 데이터 로드 및 관리를 담당하는 클래스 (Single Responsibility)"""
    
    def __init__(self, cut_scene_name: str, app):
        self.cut_scene_name = cut_scene_name
        self.app = app
        self.data = self._load_data()
        self.current_step = 0
        self.max_steps = len(self.data)
    
    def _load_data(self):
        """JSON 파일에서 컷씬 데이터 읽어오기"""
        path = BASE_CUT_SCENE_DATA_PATH + self.cut_scene_name + ".json"
        with open(path, 'r', encoding="utf-8") as f:
            return json.load(f)
    
    def get_current_step_data(self):
        """현재 스텝 데이터 반환"""
        if self.current_step >= self.max_steps:
            return None
        return self.data[self.current_step]
    
    def get_current_image(self):
        """현재 스텝 이미지 반환"""
        step_data = self.get_current_step_data()
        if not step_data:
            return None
        return self.app.ASSETS["cut_scene"][self.cut_scene_name][step_data["image"]]
    
    def get_current_text(self):
        """현재 스텝 텍스트 반환"""
        step_data = self.get_current_step_data()
        return step_data["text"] if step_data else ""
    
    def next_step(self):
        """다음 스텝으로 이동"""
        self.current_step += 1
        return self.current_step < self.max_steps
    
    def is_last_step(self):
        """마지막 스텝인지 확인"""
        return self.current_step >= self.max_steps - 1

class TypewriterEffect:
    """타자기 효과를 담당하는 클래스 (Single Responsibility)"""
    
    def __init__(self, app, text_renderer, sound):
        self.app = app
        self.text_renderer = text_renderer
        self.sound = sound
        self.target_text = ""
        self.current_text = ""
        self.text_index = 0
        self.char_timer = Timer(
            TEXT_CHARACTER_SPEED,
            on_time_out=self._show_next_character,
            auto_destroy=False,
            use_unscaled=True
        )
    
    def start_typing(self, text: str):
        """새로운 텍스트로 타자기 효과 시작"""
        self.target_text = text
        self.text_index = 0
        self.current_text = ""
        self.text_renderer.text = ""
        self.char_timer.reset()
    
    def _show_next_character(self):
        """타자기 효과로 텍스트 한 글자씩 출력"""
        if self.text_index >= len(self.target_text):
            return
        
        self.text_index += 1
        self.current_text = self.target_text[:self.text_index]
        self.text_renderer.text = self.current_text
        self.app.sound_manager.play_sfx(self.sound)
        self.char_timer.reset()
    
    def is_typing_complete(self):
        """타자기 효과 완료 여부"""
        return self.text_index >= len(self.target_text)
    
    def complete_immediately(self):
        """즉시 모든 텍스트 출력"""
        self.text_index = len(self.target_text)
        self.current_text = self.target_text
        self.text_renderer.text = self.current_text

class SkipController:
    """ESC 스킵 기능을 담당하는 클래스 (Single Responsibility)"""
    
    def __init__(self, app, text_renderer, on_skip_callback):
        self.app = app
        self.text_renderer = text_renderer
        self.on_skip_callback = on_skip_callback
        self.is_holding_escape = False
        
        # 기존 Timer 클래스 활용
        self.skip_timer = Timer(
            SKIP_HOLD_TIME, 
            on_time_out=self.on_skip_callback, 
            auto_destroy=True, 
            use_unscaled=True
        )
        self.skip_timer.active = False
        
    def handle_escape_down(self):
        """ESC 키 눌림 처리"""
        if not self.is_holding_escape:
            self.is_holding_escape = True
            self.skip_timer.reset()
            self.text_renderer.text = "계속 누르고 계세요..."
    
    def handle_escape_up(self):
        """ESC 키 떼어짐 처리"""
        self.is_holding_escape = False
        self.skip_timer.reset()
        self.skip_timer.active = False # 타이머의 리셋 메소드는 active를 True로 만들기 땜에
        self.text_renderer.text = "[ESC] 스킵"

class CutSceneInputHandler:
    """컷씬 입력 처리를 담당하는 클래스"""
    
    def __init__(self, app, typewriter, skip_controller, on_next_step):
        self.app = app
        self.typewriter = typewriter
        self.skip_controller = skip_controller
        self.on_next_step = on_next_step
    
    def handle_input(self):
        """키보드 및 마우스 입력 처리"""
        for event in self.app.events:
            if event.type == pg.KEYDOWN:
                self._handle_key_down(event.key)
            elif event.type == pg.KEYUP:
                self._handle_key_up(event.key)
            elif event.type == pg.MOUSEBUTTONDOWN:
                self._handle_mouse_down(event.button)
    
    def _handle_key_down(self, key):
        """키 눌림 이벤트 처리"""
        if key in (pg.K_SPACE, pg.K_RETURN):
            self._try_advance_step()
        elif key == pg.K_ESCAPE:
            self.skip_controller.handle_escape_down()
    
    def _handle_key_up(self, key):
        """키 떼어짐 이벤트 처리"""
        if key == pg.K_ESCAPE:
            self.skip_controller.handle_escape_up()
    
    def _handle_mouse_down(self, button):
        """마우스 클릭 이벤트 처리"""
        if button == 1:  # 왼쪽 클릭
            self._try_advance_step()
    
    def _try_advance_step(self):
        """스텝 진행 시도 (타자기 효과 완료 시에만)"""
        if self.typewriter.is_typing_complete():
            self.on_next_step()

class CutScene(GameObject):
    """
    컷씬 연출용 GameObject 클래스

    주요 기능:
    - JSON 파일 기반 이미지 및 텍스트 출력
    - 타자기 효과로 텍스트 한 글자씩 표시
    - 스페이스, 엔터, 마우스 왼클릭으로 다음 컷 이동
    - ESC 키를 1초 이상 길게 누르면 컷씬 스킵 가능

    Attributes:
        data_manager (CutSceneData): 컷씬 데이터 관리
        typewriter (TypewriterEffect): 타자기 효과 처리
        skip_controller (SkipController): ESC 스킵 기능 처리
        input_handler (CutSceneInputHandler): 입력 처리
        image_renderer (ImageRenderer): 현재 이미지 렌더러
        text_renderer (TextRenderer): 텍스트 렌더러
        skip_text_renderer (TextRenderer): ESC 스킵 안내 텍스트 렌더러
        next_step_sound (Sound): 스텝 전환 효과음
        on_cut_scene_end (callable): 컷씬 종료 시 호출되는 콜백 함수
    """

    def __init__(self, cut_scene_data_name: str = "opening", on_cut_scene_end=None, text_color=pg.Color("black")):
        super().__init__()
        
        self.on_cut_scene_end = on_cut_scene_end
        
        # 데이터 관리자 초기화
        self.data_manager = CutSceneData(cut_scene_data_name, self.app)
        
        # UI 렌더러들 초기화
        self._init_renderers(text_color)
        
        # 컴포넌트들 초기화
        self._init_components()
        
        # 사운드 효과
        self.next_step_sound = self.app.ASSETS["sounds"]["ui"]["confirm"]
        
        # 첫 번째 스텝 시작
        self._start_current_step()
        
        # 다음 컷 진행 안내 텍스트
        self._show_instruction_popup()
    
    def _init_renderers(self, text_color):
        """렌더러들 초기화"""
        self.image_renderer = ImageRenderer(
            self.data_manager.get_current_image(), 
            pg.Vector2(SCREEN_SIZE.x / 2, 250)
        )
        self.text_renderer = TextRenderer(
            "", 
            pg.Vector2(SCREEN_SIZE.x / 2, 600), 
            anchor=pg.Vector2(0.5, 0.5), 
            color=text_color
        )
        self.skip_text_renderer = TextRenderer(
            "[ESC] 스킵", 
            pg.Vector2(10, 10), 
            font_name="bold", 
            font_size=20, 
            anchor=pg.Vector2(0, 0), 
            color=text_color
        )
    
    def _init_components(self):
        """컴포넌트들 초기화"""
        character_sound = self.app.ASSETS["sounds"]["ui"]["next"]
        
        self.typewriter = TypewriterEffect(self.app, self.text_renderer, character_sound)
        self.skip_controller = SkipController(self.app, self.skip_text_renderer, self._skip_cut_scene)
        self.input_handler = CutSceneInputHandler(
            self.app, 
            self.typewriter, 
            self.skip_controller, 
            self._next_step
        )
    
    def _show_instruction_popup(self):
        """안내 팝업 표시 (지연 import로 순환 참조 방지)"""
        PopupText(
            "[스페이스 | 엔터 | 마우스 왼 클릭]", 
            pg.Vector2(SCREEN_SIZE.x / 2, SCREEN_SIZE.y - 50), 
            fade_delay=0, 
            fade_duration=4, 
            anchor=pg.Vector2(0.5, 0.5)
        )
    
    def _start_current_step(self):
        """현재 스텝 시작 (이미지 및 타자기 효과)"""
        self.image_renderer.image = self.data_manager.get_current_image()
        self.typewriter.start_typing(self.data_manager.get_current_text())
    
    def _next_step(self):
        """다음 컷으로 넘어가기"""
        self.app.sound_manager.play_sfx(self.next_step_sound)
        
        if self.data_manager.next_step():
            self._start_current_step()
        else:
            self._skip_cut_scene()
    
    def _skip_cut_scene(self):
        """컷씬 종료 처리 및 콜백 호출"""
        if self.on_cut_scene_end:
            self.on_cut_scene_end()
        self.destroy()
    
    def update(self):
        """매 프레임마다 업데이트"""
        super().update()
        self.input_handler.handle_input()
        # skip_controller.update() 제거 - Timer가 자동으로 처리
    
    def destroy(self):
        """자원 정리 및 삭제 처리"""
        self.image_renderer.destroy()
        self.text_renderer.destroy()
        super().destroy()