import pygame as pg
import math
import copy
import json

from scripts.constants import *
from scripts.tilemap import *
from scripts.camera import *
from scripts.backgrounds import *
from scripts.ui import *
from .base import Scene

CAMERA_MOVE_SPEED = 400
MAX_UNDO_STACK = 20
IN_GRID_TILES = ["dirt", "stone", "dead_grass", "wood_struct"]

def save_tilemap_file(tilemap_data : TilemapData, file_name: str = "temp.json"):
    """
    현재 타일맵 데이터를 JSON 파일로 저장
    :param file_name: 저장할 파일 이름 (기본 temp.json)
    """

    with open(BASE_TILEMAP_PATH + '/' + file_name, 'w', encoding="utf-8") as f:
        json.dump({
            "tile_size": tilemap_data.tile_size,
            "in_grid": tilemap_data.in_grid,
            "off_grid": tilemap_data.off_grid
        }, f)

def autotile(tilemap_data : TilemapData, auto_tile_types : list[str] = ["dirt", "stone", "dead_grass"]):
    """
    오토타일링 알고리즘 적용
    """
    AUTOTILE_MAP = {
        tuple(sorted([(1, 0), (0, 1)])): 0,
        tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
        tuple(sorted([(-1, 0), (0, 1)])): 2,
        tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
        tuple(sorted([(-1, 0), (0, -1)])): 4,
        tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
        tuple(sorted([(1, 0), (0, -1)])): 6,
        tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
        tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,
    }

    for tile in tilemap_data.in_grid.values():
        neighbors = set()
        for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
            check_pos = f"{tile['pos'][0] + shift[0]},{tile['pos'][1] + shift[1]}"
            if check_pos in tilemap_data.in_grid and tilemap_data.in_grid[check_pos]['type'] == tile['type']:
                neighbors.add(shift)
        sorted_neighbors = tuple(sorted(neighbors))
        
        if tile['type'] in auto_tile_types and sorted_neighbors in AUTOTILE_MAP:
            tile['variant'] = AUTOTILE_MAP[sorted_neighbors]

class EditorInputHandler:
    def __init__(self, editor_toolbox, camera, app):
        self.editor_toolbox = editor_toolbox
        self.camera = camera
        self.app = app
        self.keys = pg.key.get_pressed()

    def handle_keyboard_input(self):
        """키보드 입력 처리 (C, TAB, V, B, O, U, CTRL+Z)"""
        for event in self.app.events:
            if event.type == pg.KEYUP:
                if event.key == pg.K_c and self.editor_toolbox.in_grid_mode:
                    self.editor_toolbox.can_collide = not self.editor_toolbox.can_collide
                elif event.key == pg.K_TAB:
                    self.editor_toolbox.in_grid_mode = not self.editor_toolbox.in_grid_mode
                    self.editor_toolbox.can_collide = self.editor_toolbox.in_grid_mode
                elif event.key == pg.K_v:
                    self.editor_toolbox.in_collision_view = not self.editor_toolbox.in_collision_view
                elif event.key == pg.K_b:
                    self.editor_toolbox.autotile_and_rerender()
                elif event.key == pg.K_o:
                    self.editor_toolbox.save_tilemap()
                elif event.key == pg.K_u:
                    self.editor_toolbox.erase_all()
                elif event.key == pg.K_z and self.keys[pg.K_LCTRL]:
                    self.editor_toolbox.undo()

    def handle_mouse_input(self):
        """마우스 입력 처리 (좌클릭 설치, 우클릭 삭제, 휠로 타일 변경)"""
        for event in self.app.events:
            if event.type == pg.MOUSEBUTTONDOWN and not self.editor_toolbox.in_grid_mode and event.button == 1:
                self.editor_toolbox.place_tile_offgrid()
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                self.editor_toolbox.last_placed_tile_pos = None
            if event.type == pg.MOUSEWHEEL:
                if self.keys[pg.K_LSHIFT]:
                    self.editor_toolbox.change_tile_variant(event.y)
                else:
                    self.editor_toolbox.change_tile_type(event.y)

        left, _, right = pg.mouse.get_pressed()
        if left:
            self.editor_toolbox.place_tile_grid()
        if right:
            self.editor_toolbox.remove_tile()

    def update(self):
        self.keys = pg.key.get_pressed()
        self.handle_keyboard_input()
        self.handle_mouse_input()
        self.move_camera()

    def move_camera(self):
        """WASD로 카메라 이동 처리"""
        move_speed = CAMERA_MOVE_SPEED * self.app.dt
        if self.keys[pg.K_w]:
            self.camera.position += pg.Vector2(0, -move_speed)
        if self.keys[pg.K_s]:
            self.camera.position += pg.Vector2(0, move_speed)
        if self.keys[pg.K_a]:
            self.camera.position += pg.Vector2(-move_speed, 0)
        if self.keys[pg.K_d]:
            self.camera.position += pg.Vector2(move_speed, 0)

class EditorUI:
    def __init__(self, editor_toolbox, app):
        self.editor_toolbox = editor_toolbox
        self.app = app
        self.make_ui()

    def make_ui(self):
        """좌측 상단 텍스트 출력 및 상태 표시기 생성"""
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

        self.collide_mode_text_renderer = TextRenderer("", pg.Vector2(10, 35), color="blue")
        self.grid_mode_text_renderer = TextRenderer("", pg.Vector2(10, 60), color="white")
        self.view_mode_text_renderer = TextRenderer("", pg.Vector2(10, 85), color="white")
        self.current_tile_text_renderer = TextRenderer("", pg.Vector2(10, 165), color="red")

    def update(self):
        """화면에 현재 상태 텍스트 갱신"""
        self.collide_mode_text_renderer.text = "[C] 현재 : 충돌 가능" if self.editor_toolbox.can_collide else "[C] 현재 : 충돌 X"
        self.grid_mode_text_renderer.text = "[Tab] 현재: 그리드" if self.editor_toolbox.in_grid_mode else "[Tab] 현재: 자유"
        self.view_mode_text_renderer.text = "[V] 현재 : 충돌범위 뷰" if self.editor_toolbox.in_collision_view else "[V] 현재 : 일반 뷰"
        
        current_tile_type = self.editor_toolbox.tile_types[self.editor_toolbox.current_tile_type_index]
        current_tile_variant = self.editor_toolbox.current_tile_variant
        self.current_tile_text_renderer.text = f"{current_tile_type} : [{current_tile_variant}]"

class EditorToolbox:
    def __init__(self, scene, tilemap_data, tilemap_renderer, app, camera):
        self.scene = scene
        self.tilemap_data = tilemap_data
        self.tilemap_renderer = tilemap_renderer
        self.app = app
        self.camera = camera
        self.tile_types = list(self.app.ASSETS["tilemap"].keys())
        self.current_tile_type_index = 0
        self.current_tile_variant = 0
        self.undo_stack = []
        self.last_placed_tile_pos = None
        self.can_collide = True
        self.in_grid_mode = True
        self.in_collision_view = False
        self.mouse_world_pos = pg.Vector2(0, 0)
        self.tile_pos = pg.Vector2(0, 0)

    def update_mouse_position(self):
        """마우스 위치를 월드 좌표로 변환, 그리드 모드에 따라 좌표 보정"""
        self.mouse_world_pos = CameraMath.screen_to_world(self.camera, pg.mouse.get_pos())
        if self.in_grid_mode:
            self.mouse_world_pos.x = math.floor(self.mouse_world_pos.x / self.tilemap_data.tile_size) * self.tilemap_data.tile_size
            self.mouse_world_pos.y = math.floor(self.mouse_world_pos.y / self.tilemap_data.tile_size) * self.tilemap_data.tile_size
            self.tile_pos = pg.Vector2(self.mouse_world_pos.x // self.tilemap_data.tile_size,
                                         self.mouse_world_pos.y // self.tilemap_data.tile_size)
        else:
            self.tile_pos = pg.Vector2(self.mouse_world_pos.x / self.tilemap_data.tile_size,
                                         self.mouse_world_pos.y / self.tilemap_data.tile_size)

    def save_undo_state(self):
        """undo 스택에 현재 타일맵 상태 저장"""
        self.undo_stack.append({
            "in_grid": copy.deepcopy(self.tilemap_data.in_grid),
            "off_grid": copy.deepcopy(self.tilemap_data.off_grid)
        })
        if len(self.undo_stack) > MAX_UNDO_STACK:
            self.undo_stack.pop(0)

    def undo(self):
        """undo 스택에서 마지막 상태 불러와 타일맵 롤백"""
        if not self.undo_stack:
            return
        last_state = self.undo_stack.pop()
        self.tilemap_data.in_grid = last_state["in_grid"]
        self.tilemap_data.off_grid = last_state["off_grid"]
        self.tilemap_renderer.rerender()

    def autotile_and_rerender(self):
        autotile(self.tilemap_data)
        self.tilemap_renderer.rerender()

    def save_tilemap(self):
        save_tilemap_file(self.tilemap_data)

    def erase_all(self):
        """전체 타일 삭제 + undo 저장 + 리렌더"""
        self.tilemap_data.in_grid = {}
        self.tilemap_data.off_grid = []
        self.save_undo_state()
        self.tilemap_renderer.rerender()

    def change_tile_variant(self, delta):
        """타일 변형 인덱스 변경 (SHIFT + 휠)"""
        tile_type_name = self.tile_types[self.current_tile_type_index]
        tile_variant_len = len(self.app.ASSETS["tilemap"][tile_type_name])
        self.current_tile_variant = (self.current_tile_variant + delta) % tile_variant_len

    def change_tile_type(self, delta):
        """타일 종류 인덱스 변경 (휠)"""
        self.current_tile_type_index = (self.current_tile_type_index + delta) % len(self.tile_types)
        self.current_tile_variant = 0
    
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

        self.tilemap_data.in_grid[key] = {
            "pos": [int(self.tile_pos.x), int(self.tile_pos.y)],
            "type": self.tile_types[self.current_tile_type_index],
            "variant": self.current_tile_variant,
            "can_collide": self.can_collide
        }
        self.last_placed_tile_pos = key
        self.tilemap_renderer.rerender()

    def place_tile_offgrid(self):
        """자유 모드에서 타일 설치"""
        if self.in_grid_mode:
            return
        self.save_undo_state()
        self.tilemap_data.off_grid.append({
            "pos": [self.tile_pos.x, self.tile_pos.y],
            "type": self.tile_types[self.current_tile_type_index],
            "variant": self.current_tile_variant
        })
        self.tilemap_renderer.rerender()

    def remove_tile(self):
        """마우스 위치 타일 삭제 (그리드/자유 모드 모두)"""
        if self.in_grid_mode:
            key = f"{int(self.tile_pos.x)},{int(self.tile_pos.y)}"
            if key in self.tilemap_data.in_grid:
                self.save_undo_state()
                del self.tilemap_data.in_grid[key]
        else:
            for obj_data in self.tilemap_data.off_grid.copy():
                original_image = self.app.ASSETS["tilemap"][obj_data["type"]][obj_data["variant"]]
                size = original_image.get_size()
                rect = pg.Rect(obj_data["pos"][0] * self.tilemap_data.tile_size,
                                obj_data["pos"][1] * self.tilemap_data.tile_size,
                                size[0], size[1])
                if rect.collidepoint(self.mouse_world_pos):
                    self.save_undo_state()
                    if obj_data in self.tilemap_data.off_grid:
                        self.tilemap_data.off_grid.remove(obj_data)
        self.tilemap_renderer.rerender()
    
    def draw_grid(self, surface):
        """그리드 모드일 때 그리드 선 그리기"""
        if not self.in_grid_mode:
            return
        tile_size = self.tilemap_data.tile_size
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
        tile_size = int(self.tilemap_data.tile_size)
        for tile_data in self.tilemap_data.in_grid.values():
            if tile_data["can_collide"]:
                world_pos = pg.Vector2(tile_data["pos"][0] * tile_size,
                                        tile_data["pos"][1] * tile_size)
                screen_pos = CameraMath.world_to_screen(self.camera, world_pos)
                rect = pg.Rect(screen_pos.x, screen_pos.y, tile_size, tile_size)
                pg.draw.rect(surface, "blue", rect)

    def draw_preview(self, surface):
        """마우스 위치에 현재 선택 타일 반투명 미리보기"""
        tile_size = self.tilemap_data.tile_size
        preview_screen_pos = CameraMath.world_to_screen(self.camera, self.tile_pos * tile_size)
        current_tile_type = self.tile_types[self.current_tile_type_index]
        current_tile_variant = self.current_tile_variant
        preview_image = self.app.ASSETS["tilemap"][current_tile_type][current_tile_variant].copy()
        preview_image.set_alpha(150)
        surface.blit(preview_image, preview_screen_pos)
        if self.can_collide:
            pg.draw.rect(surface, (255, 0, 0, 100),
                            pg.Rect(preview_screen_pos.x, preview_screen_pos.y, tile_size, tile_size), 2)


class TileMapEditor:
    """
    타일맵 편집 전담 클래스
    """
    def __init__(self, scene):
        self.scene = scene
        self.app = scene.app
        self.camera = scene.camera
        
        self.tilemap_data = scene.tilemap_data
        self.tilemap_renderer = scene.tilemap_renderer
        
        self.toolbox = EditorToolbox(self.scene, self.tilemap_data, self.tilemap_renderer, self.app, self.camera)
        self.input_handler = EditorInputHandler(self.toolbox, self.camera, self.app)
        self.ui = EditorUI(self.toolbox, self.app)

    def update(self):
        self.toolbox.update_mouse_position()
        self.input_handler.update()
        self.ui.update()

    def draw(self):
        self.toolbox.draw_grid(self.app.surfaces[LAYER_INTERFACE])
        self.toolbox.draw_collision(self.app.surfaces[LAYER_INTERFACE])
        self.toolbox.draw_preview(self.app.surfaces[LAYER_INTERFACE])

class TileMapEditScene(Scene):
    """
    타일맵 편집 씬 클래스
    """

    def on_scene_start(self):
        super().on_scene_start()
        self.tilemap_data = TilemapData("temp.json")
        self.tilemap_renderer = TilemapRenderer(self.tilemap_data)
        self.editor = TileMapEditor(self)
        Sky()

    def update(self):
        self.editor.update()
        super().update()

    def draw(self):
        self.editor.draw()
        super().draw()