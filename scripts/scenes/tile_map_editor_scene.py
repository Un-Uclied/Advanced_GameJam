import pygame as pg
import math
import copy

from scripts.constants import *
from scripts.tilemap import Tilemap, IN_GRID_TILES
from scripts.camera import *
from scripts.backgrounds import Sky
from scripts.ui import TextRenderer
from .base import Scene

CAMERA_MOVE_SPEED = 400
MAX_UNDO_STACK = 20

class TileMapEditor:
    """
    타일맵 편집 전담 클래스
    """

    def __init__(self, scene):
        self.scene = scene
        self.tilemap = scene.tilemap
        self.app = scene.app
        self.camera = scene.camera

        self.tile_types = list(self.app.ASSETS["tilemap"].keys())
        self.current_tile_type_index = 0
        self.current_tile_variant = 0
        self.undo_stack = []
        self.last_placed_tile_pos = None

        self.can_collide = True
        self.in_grid_mode = True
        self.in_collision_view = False

        self.create_ui_elements()

        self.mouse_world_pos = pg.Vector2(0, 0)
        self.tile_pos = pg.Vector2(0, 0)

    def create_ui_elements(self):
        """좌측 상단 텍스트 출력 및 상태 표시기 생성"""
        # 반복되는 텍스트 정보 리스트로 정리
        texts = [
            ("[WASD] 움직이기", (10, 10), "white"),
            ("[B] 오토 타일", (10, 110), "white"),
            ("[휠] 타일 종류 변경 | [SHIFT + 휠] 타일 인덱스 변경", (10, 135), "white"),
            ("[O] 저장하기 (temp.json에 저장됨.)", (10, 190), "white"),
            ("[컨트롤 Z] 되돌리기 (최대 20까지)", (10, 215), "white"),
            ("[U] 다 지워버렷", (10, 240), "green")
        ]
        for text, pos, color in texts:
            TextRenderer(text, pg.Vector2(*pos), color=color)

        # 상태 텍스트 렌더러 변수로 저장
        self.collide_mode_text_renderer = TextRenderer("", pg.Vector2(10, 35), color="blue")
        self.grid_mode_text_renderer = TextRenderer("", pg.Vector2(10, 60), color="white")
        self.view_mode_text_renderer = TextRenderer("", pg.Vector2(10, 85), color="white")
        self.current_tile_text_renderer = TextRenderer("", pg.Vector2(10, 165), color="red")

    def save_undo_state(self):
        """undo 스택에 현재 타일맵 상태 저장"""
        self.undo_stack.append({
            "in_grid": copy.deepcopy(self.tilemap.in_grid),
            "off_grid": copy.deepcopy(self.tilemap.off_grid)
        })
        if len(self.undo_stack) > MAX_UNDO_STACK:
            self.undo_stack.pop(0)

    def undo(self):
        """undo 스택에서 마지막 상태 불러와 타일맵 롤백"""
        if not self.undo_stack:
            return
        last_state = self.undo_stack.pop()
        self.tilemap.in_grid = last_state["in_grid"]
        self.tilemap.off_grid = last_state["off_grid"]

    def update_mouse_position(self):
        """마우스 위치를 월드 좌표로 변환, 그리드 모드에 따라 좌표 보정"""
        self.mouse_world_pos = CameraMath.screen_to_world(self.camera, pg.mouse.get_pos())
        if self.in_grid_mode:
            self.mouse_world_pos.x = math.floor(self.mouse_world_pos.x / self.tilemap.tile_size) * self.tilemap.tile_size
            self.mouse_world_pos.y = math.floor(self.mouse_world_pos.y / self.tilemap.tile_size) * self.tilemap.tile_size
            self.tile_pos = pg.Vector2(self.mouse_world_pos.x // self.tilemap.tile_size,
                                      self.mouse_world_pos.y // self.tilemap.tile_size)
        else:
            self.tile_pos = pg.Vector2(self.mouse_world_pos.x / self.tilemap.tile_size,
                                      self.mouse_world_pos.y / self.tilemap.tile_size)

    def handle_keyboard_input(self):
        """키보드 입력 처리 (C, TAB, V, B, O, U, CTRL+Z)"""
        keys = pg.key.get_pressed()
        for event in self.app.events:
            if event.type == pg.KEYUP:
                if event.key == pg.K_c and self.in_grid_mode:
                    self.can_collide = not self.can_collide
                elif event.key == pg.K_TAB:
                    self.in_grid_mode = not self.in_grid_mode
                    self.can_collide = self.in_grid_mode
                elif event.key == pg.K_v:
                    self.in_collision_view = not self.in_collision_view
                elif event.key == pg.K_b:
                    self.tilemap.autotile()
                    self.tilemap.rerender()
                elif event.key == pg.K_o:
                    self.tilemap.save_file()
                elif event.key == pg.K_u:
                    self.erase_all()
                    self.tilemap.rerender()
                elif event.key == pg.K_z and keys[pg.K_LCTRL]:
                    self.undo()
                    self.tilemap.rerender()

    def handle_mouse_input(self):
        """마우스 입력 처리 (좌클릭 설치, 우클릭 삭제, 휠로 타일 변경)"""
        keys = pg.key.get_pressed()
        for event in self.app.events:
            if event.type == pg.MOUSEBUTTONDOWN and not self.in_grid_mode and event.button == 1:
                self.place_tile_offgrid()
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                self.last_placed_tile_pos = None
            if event.type == pg.MOUSEWHEEL:
                if keys[pg.K_LSHIFT]:
                    self.change_tile_variant(event.y)
                else:
                    self.change_tile_type(event.y)

        left, _, right = pg.mouse.get_pressed()
        if left:
            self.place_tile_grid()
        if right:
            self.remove_tile()

    def change_tile_variant(self, delta):
        """타일 변형 인덱스 변경 (SHIFT + 휠)"""
        tile_type_name = self.tile_types[self.current_tile_type_index]
        tile_variant_len = len(self.app.ASSETS["tilemap"][tile_type_name])
        self.current_tile_variant = (self.current_tile_variant + delta) % tile_variant_len

    def change_tile_type(self, delta):
        """타일 종류 인덱스 변경 (휠)"""
        self.current_tile_type_index = (self.current_tile_type_index + delta) % len(self.tile_types)
        self.current_tile_variant = 0

    def move_camera(self):
        """WASD로 카메라 이동 처리"""
        keys = pg.key.get_pressed()
        move_speed = CAMERA_MOVE_SPEED * self.app.dt
        if keys[pg.K_w]:
            self.camera.position += pg.Vector2(0, -move_speed)
        if keys[pg.K_s]:
            self.camera.position += pg.Vector2(0, move_speed)
        if keys[pg.K_a]:
            self.camera.position += pg.Vector2(-move_speed, 0)
        if keys[pg.K_d]:
            self.camera.position += pg.Vector2(move_speed, 0)

    def update_ui(self):
        """화면에 현재 상태 텍스트 갱신"""
        self.collide_mode_text_renderer.text = "[C] 현재 : 충돌 가능" if self.can_collide else "[C] 현재 : 충돌 X"
        self.grid_mode_text_renderer.text = "[Tab] 현재: 그리드" if self.in_grid_mode else "[Tab] 현재: 자유"
        self.view_mode_text_renderer.text = "[V] 현재 : 충돌범위 뷰" if self.in_collision_view else "[V] 현재 : 일반 뷰"
        self.current_tile_text_renderer.text = f"{self.tile_types[self.current_tile_type_index]} : [{self.current_tile_variant}]"

    def draw_grid(self, surface):
        """그리드 모드일 때 그리드 선 그리기"""
        if not self.in_grid_mode:
            return
        tile_size = self.tilemap.tile_size
        top_left_world = CameraMath.screen_to_world(self.camera, pg.Vector2(0, 0))
        bottom_right_world = CameraMath.screen_to_world(self.camera, SCREEN_SIZE)
        start_x = int(top_left_world.x // tile_size)
        end_x = int(bottom_right_world.x // tile_size) + 1
        start_y = int(top_left_world.y // tile_size)
        end_y = int(bottom_right_world.y // tile_size) + 1
        grid_color = pg.Color(100, 100, 100, 50)

        for x in range(start_x, end_x + 1):
            world_x = x * tile_size
            screen_start = CameraMath.world_to_screen(self.camera, pg.Vector2(world_x, top_left_world.y))
            screen_end = CameraMath.world_to_screen(self.camera, pg.Vector2(world_x, bottom_right_world.y))
            pg.draw.line(surface, grid_color, screen_start, screen_end)
        for y in range(start_y, end_y + 1):
            world_y = y * tile_size
            screen_start = CameraMath.world_to_screen(self.camera, pg.Vector2(top_left_world.x, world_y))
            screen_end = CameraMath.world_to_screen(self.camera, pg.Vector2(bottom_right_world.x, world_y))
            pg.draw.line(surface, grid_color, screen_start, screen_end)

    def draw_collision(self, surface):
        """충돌 가능 타일 파란 사각형 표시 (충돌 뷰 모드일 때만)"""
        if not self.in_collision_view:
            return
        tile_size = int(self.tilemap.tile_size)
        for tile_data in self.tilemap.in_grid.values():
            if tile_data["can_collide"]:
                world_pos = pg.Vector2(tile_data["pos"][0] * tile_size,
                                       tile_data["pos"][1] * tile_size)
                screen_pos = CameraMath.world_to_screen(self.camera, world_pos)
                rect = pg.Rect(screen_pos.x, screen_pos.y, tile_size, tile_size)
                pg.draw.rect(surface, "blue", rect)

    def draw_preview(self, surface):
        """마우스 위치에 현재 선택 타일 반투명 미리보기"""
        tile_size = self.tilemap.tile_size
        preview_screen_pos = CameraMath.world_to_screen(self.camera, self.tile_pos * tile_size)
        current_tile_type = self.tile_types[self.current_tile_type_index]
        current_tile_variant = self.current_tile_variant
        preview_image = self.app.ASSETS["tilemap"][current_tile_type][current_tile_variant].copy()
        preview_image.set_alpha(150)
        surface.blit(preview_image, preview_screen_pos)
        if self.can_collide:
            pg.draw.rect(surface, (255, 0, 0, 100),
                         pg.Rect(preview_screen_pos.x, preview_screen_pos.y, tile_size, tile_size), 2)

    def place_tile_grid(self):
        """그리드 모드에서 타일 설치 (중복 방지)"""
        if not self.in_grid_mode:
            return
        if self.tile_types[self.current_tile_type_index] not in IN_GRID_TILES:
            return

        key = f"{int(self.tile_pos.x)},{int(self.tile_pos.y)}"
        if self.last_placed_tile_pos == key:
            return
        self.save_undo_state()

        self.tilemap.in_grid[key] = {
            "pos": [int(self.tile_pos.x), int(self.tile_pos.y)],
            "type": self.tile_types[self.current_tile_type_index],
            "variant": self.current_tile_variant,
            "can_collide": self.can_collide
        }
        self.last_placed_tile_pos = key
        self.tilemap.rerender()

    def place_tile_offgrid(self):
        """자유 모드에서 타일 설치"""
        if self.in_grid_mode:
            return
        self.save_undo_state()
        self.tilemap.off_grid.append({
            "pos": [self.tile_pos.x, self.tile_pos.y],
            "type": self.tile_types[self.current_tile_type_index],
            "variant": self.current_tile_variant
        })
        self.tilemap.rerender()

    def remove_tile(self):
        """마우스 위치 타일 삭제 (그리드/자유 모드 모두)"""
        if self.in_grid_mode:
            key = f"{int(self.tile_pos.x)},{int(self.tile_pos.y)}"
            if key in self.tilemap.in_grid:
                self.save_undo_state()
                del self.tilemap.in_grid[key]
        else:
            for obj_data in self.tilemap.off_grid.copy():
                original_image = self.app.ASSETS["tilemap"][obj_data["type"]][obj_data["variant"]]
                size = original_image.get_size()
                rect = pg.Rect(obj_data["pos"][0] * self.tilemap.tile_size,
                               obj_data["pos"][1] * self.tilemap.tile_size,
                               size[0], size[1])
                if rect.collidepoint(self.mouse_world_pos):
                    self.save_undo_state()
                    if obj_data in self.tilemap.off_grid:
                        self.tilemap.off_grid.remove(obj_data)
        self.tilemap.rerender()

    def erase_all(self):
        """전체 타일 삭제 + undo 저장 + 리렌더"""
        self.tilemap.in_grid = {}
        self.tilemap.off_grid = []
        self.save_undo_state()
        self.tilemap.rerender()

    def update(self):
        """매 프레임 호출, 입력 및 상태 처리"""
        self.update_mouse_position()
        self.handle_keyboard_input()
        self.handle_mouse_input()
        self.move_camera()
        self.update_ui()

    def draw(self):
        """인터페이스 레이어에 그리드, 충돌 영역, 미리보기 그림"""
        self.draw_grid(self.app.surfaces[LAYER_INTERFACE])
        self.draw_collision(self.app.surfaces[LAYER_INTERFACE])
        self.draw_preview(self.app.surfaces[LAYER_INTERFACE])

class TileMapEditScene(Scene):
    """
    타일맵 편집 씬 클래스
    """

    def on_scene_start(self):
        super().on_scene_start()
        self.tilemap = Tilemap("temp.json")
        self.editor = TileMapEditor(self)
        Sky()

    def update(self):
        self.editor.update()
        super().update()

    def draw(self):
        self.editor.draw()
        super().draw()