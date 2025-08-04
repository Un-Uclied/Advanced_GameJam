import pygame as pg
import json

from scripts.constants import *
from scripts.core import *
from scripts.ui import *

BASE_CUT_SCENE_DATA_PATH = "data/cut_scene/"
TEXT_CHARACTER_SPEED = .1  # 한 글자 출력 간격 (초)

class CutScene(GameObject):
    '''
    컷씬 연출용 GameObject

    - json 파일을 기반으로 이미지 & 텍스트 출력
    - 타자기 효과로 텍스트 출력
    - 스페이스/엔터로 다음 컷
    - ESC 길게 누르면 컷씬 스킵
    '''

    def __init__(self, cut_scene_data_name: str = "opening", on_cut_scene_end=None):
        super().__init__()

        # 컷씬 이름 및 끝났을 때 호출될 콜백
        self.cut_scene_name = cut_scene_data_name
        self.on_cut_scene_end = on_cut_scene_end

        # 컷씬 데이터 로드
        self.cut_scene_data = self.load_data()
        self.current_step = 0
        self.max_steps = len(self.cut_scene_data)

        # 현재 스텝용 텍스트/이미지 정보
        self.load_current_step_data()

        # 렌더러 생성
        self.image_renderer = ImageRenderer(self.current_image, pg.Vector2(SCREEN_SIZE.x / 2, 250))
        self.text_renderer = TextRenderer("", pg.Vector2(SCREEN_SIZE.x / 2, 600), anchor=pg.Vector2(0.5, 0.5))

        # 타자기 텍스트 출력용 타이머
        self.text_index = 0
        self.current_text = ""
        self.char_timer = Timer(TEXT_CHARACTER_SPEED, self.show_next_character, auto_destroy=False, use_unscaled=True)

        # ESC 스킵용 타이머
        self.skip_timer = Timer(0.5, self.end_cut_scene, auto_destroy=False, use_unscaled=True)
        self.skip_timer.active = False
        self.skip_text_renderer = TextRenderer("[ESC] 스킵", pg.Vector2(10, 10), font_name="bold", font_size=20, anchor=pg.Vector2(0, 0))

        # 키 힌트
        Tween(TextRenderer("[스페이스 | 엔터 | 마우스 왼 클릭]", pg.Vector2(SCREEN_SIZE.x / 2, SCREEN_SIZE.y - 50), anchor=pg.Vector2(.5, .5)), "alpha", 255, 0, 4, use_unscaled_time=True)

        # 사운드
        self.character_next_sound = self.app.ASSETS["sounds"]["ui"]["next"]
        self.next_step_sound = self.app.ASSETS["sounds"]["ui"]["confirm"]

    def load_data(self):
        with open(BASE_CUT_SCENE_DATA_PATH + self.cut_scene_name + ".json", 'r', encoding="utf-8") as f:
            return json.load(f)

    def load_current_step_data(self):
        '''현재 스텝용 이미지 & 텍스트 로드'''
        self.current_data = self.cut_scene_data[self.current_step]
        self.current_image = self.app.ASSETS["cut_scene"][self.cut_scene_name][self.current_data["image"]]
        self.target_text = self.current_data["text"]

    def show_next_character(self):
        '''타자기 효과로 한 글자씩 출력'''
        if self.text_index >= len(self.target_text):
            return

        self.text_index += 1
        self.current_text = self.target_text[:self.text_index]
        self.text_renderer.text = self.current_text
        self.app.sound_manager.play_sfx(self.character_next_sound)
        self.char_timer.reset()

    def next_step(self):
        '''다음 컷으로 넘어감'''
        self.app.sound_manager.play_sfx(self.next_step_sound)

        if self.current_step < self.max_steps - 1:
            self.current_step += 1
            self.load_current_step_data()

            self.text_index = 0
            self.current_text = ""
            self.text_renderer.text = ""
            self.image_renderer.image = self.current_image
            self.char_timer.reset()
        else:
            self.end_cut_scene()

    def end_cut_scene(self):
        '''컷씬 종료 처리'''
        if self.on_cut_scene_end:
            self.on_cut_scene_end()
        self.destroy()

    def handle_input(self):
        for event in self.app.events:
            if event.type == pg.KEYDOWN:
                if event.key in (pg.K_SPACE, pg.K_RETURN):
                    if self.text_index >= len(self.target_text):
                        self.next_step()

                elif event.key == pg.K_ESCAPE:
                    self.skip_timer.active = True
                    self.skip_text_renderer.text = "계속 누르고 계세요..."

            elif event.type == pg.KEYUP and event.key == pg.K_ESCAPE:
                self.skip_text_renderer.text = "[ESC] 스킵"
                self.skip_timer.active = False
                self.skip_timer.reset()

    def update(self):
        super().update()
        self.handle_input()

    def destroy(self):
        self.image_renderer.destroy()
        self.text_renderer.destroy()
        super().destroy()