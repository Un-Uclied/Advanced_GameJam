import pygame as pg
import json

from scripts.constants import *
from scripts.core import *
from scripts.ui import *

BASE_CUT_SCENE_DATA_PATH = "data/cut_scene/"
TEXT_CHARACTER_SPEED = 0.1  # 한 글자 출력 간격 (초)

class CutScene(GameObject):
    """
    컷씬 연출용 GameObject 클래스

    주요 기능:
    - JSON 파일 기반 이미지 및 텍스트 출력
    - 타자기 효과로 텍스트 한 글자씩 표시
    - 스페이스, 엔터, 마우스 왼클릭으로 다음 컷 이동
    - ESC 키를 길게 누르면 컷씬 스킵 가능

    Attributes:
        cut_scene_name (str): 사용할 컷씬 데이터 파일 이름
        on_cut_scene_end (callable): 컷씬 종료 시 호출되는 콜백 함수 (선택)
        cut_scene_data (list): JSON 데이터 파싱 결과 (컷씬 스텝 리스트)
        current_step (int): 현재 출력 중인 스텝 인덱스
        max_steps (int): 총 스텝 수
        current_data (dict): 현재 스텝 데이터 (이미지, 텍스트 등)
        current_image (Surface): 현재 스텝 이미지
        target_text (str): 현재 스텝 출력할 텍스트
        text_index (int): 타자기 효과로 현재까지 출력된 글자 수
        current_text (str): 현재까지 화면에 출력된 텍스트
        char_timer (Timer): 글자 출력 주기 타이머
        skip_timer (Timer): ESC 길게 누름 감지 타이머
        skip_text_renderer (TextRenderer): ESC 스킵 안내 텍스트 렌더러
        image_renderer (ImageRenderer): 현재 이미지 렌더러
        text_renderer (TextRenderer): 텍스트 렌더러
        character_next_sound (Sound): 한 글자 출력 효과음
        next_step_sound (Sound): 스텝 전환 효과음
    """

    def __init__(self, cut_scene_data_name: str = "opening", on_cut_scene_end=None, text_color=pg.Color("black")):
        super().__init__()

        self.cut_scene_name = cut_scene_data_name
        self.on_cut_scene_end = on_cut_scene_end
        self.text_color = text_color

        # 컷씬 데이터 로드 및 초기화
        self.cut_scene_data = self._load_cut_scene_data()
        self.current_step = 0
        self.max_steps = len(self.cut_scene_data)

        self._load_current_step()

        # 이미지 및 텍스트 렌더러 초기화
        self.image_renderer = ImageRenderer(self.current_image, pg.Vector2(SCREEN_SIZE.x / 2, 250))
        self.text_renderer = TextRenderer("", pg.Vector2(SCREEN_SIZE.x / 2, 600), anchor=pg.Vector2(0.5, 0.5), color=self.text_color)

        # 타자기 효과 관련 변수 및 타이머
        self.text_index = 0
        self.current_text = ""
        self.char_timer = Timer(
            TEXT_CHARACTER_SPEED,
            on_time_out=self._show_next_character,
            auto_destroy=False,
            use_unscaled=True
        )

        # ESC 스킵 관련 타이머 및 텍스트
        self.skip_timer = Timer(0.5, on_time_out=self._skip_cut_scene, auto_destroy=False, use_unscaled=True)
        self.skip_timer.active = False
        self.skip_text_renderer = TextRenderer("[ESC] 스킵", pg.Vector2(10, 10), font_name="bold", font_size=20, anchor=pg.Vector2(0, 0), color=self.text_color)

        # 다음 컷 진행 안내 텍스트 (페이드 아웃 효과)
        Tween(
            TextRenderer("[스페이스 | 엔터 | 마우스 왼 클릭]", pg.Vector2(SCREEN_SIZE.x / 2, SCREEN_SIZE.y - 50), anchor=pg.Vector2(0.5, 0.5)),
            "alpha", 255, 0, 4,
            use_unscaled_time=True
        )

        # 사운드 효과
        self.character_next_sound = self.app.ASSETS["sounds"]["ui"]["next"]
        self.next_step_sound = self.app.ASSETS["sounds"]["ui"]["confirm"]

    def _load_cut_scene_data(self):
        """JSON 파일에서 컷씬 데이터 읽어오기"""
        path = BASE_CUT_SCENE_DATA_PATH + self.cut_scene_name + ".json"
        with open(path, 'r', encoding="utf-8") as f:
            return json.load(f)

    def _load_current_step(self):
        """현재 스텝에 맞는 이미지 및 텍스트 데이터 로드"""
        self.current_data = self.cut_scene_data[self.current_step]
        self.current_image = self.app.ASSETS["cut_scene"][self.cut_scene_name][self.current_data["image"]]
        self.target_text = self.current_data["text"]

    def _show_next_character(self):
        """타자기 효과로 텍스트 한 글자씩 출력"""
        if self.text_index >= len(self.target_text):
            return  # 텍스트 끝까지 출력 완료

        self.text_index += 1
        self.current_text = self.target_text[:self.text_index]
        self.text_renderer.text = self.current_text
        self.app.sound_manager.play_sfx(self.character_next_sound)
        self.char_timer.reset()

    def next_step(self):
        """다음 컷으로 넘어가기"""
        self.app.sound_manager.play_sfx(self.next_step_sound)

        if self.current_step < self.max_steps - 1:
            self.current_step += 1
            self._load_current_step()

            # 타자기 효과 초기화
            self.text_index = 0
            self.current_text = ""
            self.text_renderer.text = ""
            self.image_renderer.image = self.current_image
            self.char_timer.reset()
        else:
            self._skip_cut_scene()

    def _skip_cut_scene(self):
        """컷씬 종료 처리 및 콜백 호출"""
        if self.on_cut_scene_end:
            self.on_cut_scene_end()
        self.destroy()

    def handle_input(self):
        """키보드 입력 처리 및 ESC 스킵 감지"""
        for event in self.app.events:
            if event.type == pg.KEYDOWN:
                if event.key in (pg.K_SPACE, pg.K_RETURN):
                    if self.text_index >= len(self.target_text):
                        self.next_step()
                elif event.key == pg.K_ESCAPE:
                    self.skip_timer.active = True
                    self.skip_text_renderer.text = "계속 누르고 계세요..."
            elif event.type == pg.KEYUP:
                if event.key == pg.K_ESCAPE:
                    self.skip_text_renderer.text = "[ESC] 스킵"
                    self.skip_timer.active = False
                    self.skip_timer.reset()

    def update(self):
        """매 프레임마다 업데이트, 입력 및 타이머 관리"""
        super().update()
        self.handle_input()

    def destroy(self):
        """자원 정리 및 삭제 처리"""
        self.image_renderer.destroy()
        self.text_renderer.destroy()
        super().destroy()