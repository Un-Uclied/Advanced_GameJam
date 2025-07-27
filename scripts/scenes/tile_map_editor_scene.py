import pygame as pg
import math
import copy

from .base.scene import Scene

from scripts.constants import *
from scripts.tilemap import Tilemap, IN_GRID_TILES
from scripts.camera import *
from scripts.volume import Sky
from scripts.ui import TextRenderer

CAMERA_MOVE_SPEED = 400
MAX_UNDO_STACK = 10

class TileMapEditScene(Scene):
    def on_scene_start(self):
        super().on_scene_start()
        Sky()

        self.tilemap = Tilemap("temp.json")

        self.tile_types = list(self.app.ASSETS["tilemap"].keys())
        self.current_tile_type_index = 0
        self.current_tile_variant = 0

        self.undo_stack = []

        self.can_collide = True
        self.in_grid_mode = True
        self.in_collision_view = False

        # UI 텍스트 표시
        TextRenderer("[WASD] 움직이기 | [Q,E]로 줌 인,아웃", pg.Vector2(10, 10), color="white")
        TextRenderer("[B] 오토 타일", pg.Vector2(10, 110), color="white")
        TextRenderer("[휠] 타일 종류 변경 | [SHIFT + 휠] 타일 인덱스 변경", pg.Vector2(10, 135), color="white")
        TextRenderer("[O] 저장하기 (temp.json에 저장됨.)", pg.Vector2(10, 190), color="white")
        TextRenderer("[컨트롤 Z] 되돌리기 (인 그리드는 잘 안됨)", pg.Vector2(10, 215), color="white")

        # 상태 표시 UI
        self.collide_mode_text_renderer = TextRenderer("", pg.Vector2(10, 35), color="blue")
        self.grid_mode_text_renderer = TextRenderer("", pg.Vector2(10, 60), color="white")
        self.view_mode_text_renderer = TextRenderer("", pg.Vector2(10, 85), color="white")
        self.current_tile_text_renderer = TextRenderer("", pg.Vector2(10, 165), color="red")

        # 마우스 관련 변수
        self.mouse_world_pos = pg.Vector2(0, 0)
        self.tile_pos = pg.Vector2(0, 0)

    def save_undo_state(self):
        # 깊은 복사로 저장 (얕은 복사는 위험)
        self.undo_stack.append({
            "in_grid": copy.deepcopy(self.tilemap.in_grid),
            "off_grid": copy.deepcopy(self.tilemap.off_grid)
        })
        # 스택 용량 50개 제한
        if len(self.undo_stack) > MAX_UNDO_STACK:
            self.undo_stack.pop(0)

    def undo(self):
        if not self.undo_stack:
            return
        last_state = self.undo_stack.pop()
        self.tilemap.in_grid = last_state["in_grid"]
        self.tilemap.off_grid = last_state["off_grid"]

    def update_mouse_position(self):
        # 카메라 기준 화면 -> 월드 좌표 변환
        self.mouse_world_pos = CameraMath.screen_to_world(self.camera, pg.mouse.get_pos())

        if self.in_grid_mode:
            # 그리드 모드면 타일 크기에 맞춰 좌표 고정
            self.mouse_world_pos.x = math.floor(self.mouse_world_pos.x / self.tilemap.tile_size) * self.tilemap.tile_size
            self.mouse_world_pos.y = math.floor(self.mouse_world_pos.y / self.tilemap.tile_size) * self.tilemap.tile_size
            self.tile_pos = pg.Vector2(self.mouse_world_pos.x // self.tilemap.tile_size,
                                       self.mouse_world_pos.y // self.tilemap.tile_size)
        else:
            # 자유 모드면 그냥 월드 좌표를 타일 단위로 나눠서 저장
            self.tile_pos = pg.Vector2(self.mouse_world_pos.x / self.tilemap.tile_size,
                                       self.mouse_world_pos.y / self.tilemap.tile_size)

    def handle_keyboard_input(self):
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
                elif event.key == pg.K_o:
                    self.tilemap.save_file()
                elif event.key == pg.K_z and keys[pg.K_LCTRL]:
                    self.undo()
                elif event.key == pg.K_q:
                    self.camera.scale += 0.5
                elif event.key == pg.K_e:
                    self.camera.scale -= 0.5

    def handle_mouse_input(self):
        keys = pg.key.get_pressed()
        for event in self.app.events:
            if event.type == pg.MOUSEBUTTONDOWN and not self.in_grid_mode:
                if event.button == 1:
                    self.place_tile_offgrid()
            elif event.type == pg.MOUSEWHEEL:
                if keys[pg.K_LSHIFT]:
                    # 타일 variant 변경
                    tile_type_name = self.tile_types[self.current_tile_type_index]
                    tile_variant_len = len(self.app.ASSETS["tilemap"][tile_type_name])
                    if event.y > 0:
                        self.current_tile_variant = (self.current_tile_variant + 1) % tile_variant_len
                    elif event.y < 0:
                        self.current_tile_variant = (self.current_tile_variant - 1) % tile_variant_len
                else:
                    # 타일 종류 변경
                    self.current_tile_type_index = (self.current_tile_type_index + int(event.y)) % len(self.tile_types)
                    self.current_tile_variant = 0

        left, _, right = pg.mouse.get_pressed()
        if left:
            self.place_tile_grid()
        if right:
            self.remove_tile()

    def move_camera(self):
        keys = pg.key.get_pressed()
        move_speed = CAMERA_MOVE_SPEED * self.app.dt / self.camera.scale

        if keys[pg.K_w]:
            self.camera.position += pg.Vector2(0, -move_speed)
        if keys[pg.K_s]:
            self.camera.position += pg.Vector2(0, move_speed)
        if keys[pg.K_a]:
            self.camera.position += pg.Vector2(-move_speed, 0)
        if keys[pg.K_d]:
            self.camera.position += pg.Vector2(move_speed, 0)

    def update_ui(self):
        # UI 상태 텍스트 업데이트
        self.collide_mode_text_renderer.text = "[C] 현재 : 충돌 가능" if self.can_collide else "[C] 현재 : 충돌 X"
        self.grid_mode_text_renderer.text = "[Tab] 현재: 그리드" if self.in_grid_mode else "[Tab] 현재: 자유"
        self.view_mode_text_renderer.text = "[V] 현재 : 충돌범위 뷰" if self.in_collision_view else "[V] 현재 : 일반 뷰"
        self.current_tile_text_renderer.text = f"{self.tile_types[self.current_tile_type_index]} : [{self.current_tile_variant}]"

    def draw_grid(self):
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
            pg.draw.line(self.app.surfaces[LAYER_INTERFACE], grid_color, screen_start, screen_end)

        for y in range(start_y, end_y + 1):
            world_y = y * tile_size
            screen_start = CameraMath.world_to_screen(self.camera, pg.Vector2(top_left_world.x, world_y))
            screen_end = CameraMath.world_to_screen(self.camera, pg.Vector2(bottom_right_world.x, world_y))
            pg.draw.line(self.app.surfaces[LAYER_INTERFACE], grid_color, screen_start, screen_end)

    def draw_collision(self):
        if not self.in_collision_view:
            return

        scaled_tile_size = int(self.tilemap.tile_size * self.camera.scale)
        for key, tile_data in self.tilemap.in_grid.items():
            if tile_data["can_collide"]:
                world_pos = pg.Vector2(tile_data["pos"][0] * self.tilemap.tile_size,
                                       tile_data["pos"][1] * self.tilemap.tile_size)
                screen_pos = CameraMath.world_to_screen(self.camera, world_pos)
                rect = pg.Rect(screen_pos.x, screen_pos.y, scaled_tile_size, scaled_tile_size)
                pg.draw.rect(self.app.surfaces[LAYER_INTERFACE], "blue", rect)

    def draw_preview(self):
        tile_size = self.tilemap.tile_size
        scaled_tile_size = int(tile_size * self.camera.scale)

        preview_screen_pos = CameraMath.world_to_screen(self.camera, self.tile_pos * tile_size)

        current_tile_type = self.tile_types[self.current_tile_type_index]
        current_tile_variant = self.current_tile_variant

        preview_image = self.app.ASSETS["tilemap"][current_tile_type][current_tile_variant].copy()
        preview_image = CameraView.get_scaled_surface(self.camera, preview_image)
        preview_image.set_alpha(150)

        self.app.surfaces[LAYER_INTERFACE].blit(preview_image, preview_screen_pos)

        if self.can_collide:
            pg.draw.rect(self.app.surfaces[LAYER_INTERFACE], (255, 0, 0, 100),
                         pg.Rect(preview_screen_pos.x, preview_screen_pos.y, scaled_tile_size, scaled_tile_size), 2)

    def place_tile_grid(self):
        if not self.in_grid_mode:
            return
        if self.tile_types[self.current_tile_type_index] not in IN_GRID_TILES:
            return
        self.save_undo_state()
        key = f"{int(self.tile_pos.x)},{int(self.tile_pos.y)}"
        self.tilemap.in_grid[key] = {
            "pos": [int(self.tile_pos.x), int(self.tile_pos.y)],
            "type": self.tile_types[self.current_tile_type_index],
            "variant": self.current_tile_variant,
            "can_collide": self.can_collide
        }

    def place_tile_offgrid(self):
        if self.in_grid_mode:
            return
        self.save_undo_state()
        self.tilemap.off_grid.append({
            "pos": [self.tile_pos.x, self.tile_pos.y],
            "type": self.tile_types[self.current_tile_type_index],
            "variant": self.current_tile_variant
        })

    def remove_tile(self):
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

    def update(self):
        super().update()
        self.update_mouse_position()
        self.handle_keyboard_input()
        self.handle_mouse_input()
        self.move_camera()
        self.update_ui()

    def draw(self):
        self.draw_grid()
        super().draw()
        self.draw_collision()
        self.draw_preview()