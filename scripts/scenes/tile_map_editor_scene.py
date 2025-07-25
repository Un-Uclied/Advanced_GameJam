import pygame as pg
import math

from datas.const import *

from .base.scene import Scene

from scripts.tilemap import Tilemap
from scripts.volume import Sky
from scripts.ui import TextRenderer

class TileMapEditScene(Scene):
    def on_scene_start(self):
        super().on_scene_start()
        Sky()

        self.tilemap = Tilemap("temp.json")

        self.tile_types = list(self.app.ASSET_TILEMAP.keys())
        self.current_tile_type_index = 0
        self.current_tile_variant = 0

        self.undo_stack = []

        self.can_collide = True
        self.in_grid_mode = True
        self.in_collision_view = False

        TextRenderer("[WASD] 움직이기 | [Q,E]로 줌 인,아웃",pg.Vector2(10, 10), color="black")
        TextRenderer("[B] 오토 타일",pg.Vector2(10, 110), color="black")
        TextRenderer("[휠] 타일 종류 변경 | [SHIFT + 휠] 타일 인덱스 변경",pg.Vector2(10, 135), color="black")
        TextRenderer("[O] 저장하기 (temp.json에 저장됨.)",pg.Vector2(10, 190), color="black")
        TextRenderer("[컨트롤 Z] 되돌리기 (인 그리드는 잘 안됨)",pg.Vector2(10, 215), color="black")

        self.collide_mode_text_renderer = TextRenderer("", pg.Vector2(10, 35), color="blue")
        self.grid_mode_text_renderer = TextRenderer("",pg.Vector2(10, 60), color="black")
        self.view_mode_text_renderer = TextRenderer("",pg.Vector2(10, 85), color="black")
        self.current_tile_text_renderer = TextRenderer("", pg.Vector2(10, 165), color="red")
        
        self.mouse_world_pos = pg.Vector2(0, 0)
        self.tile_pos = pg.Vector2(0, 0)

    def _save_undo_state(self):
        self.undo_stack.append({
            "in_grid": self.tilemap.in_grid.copy(),
            "off_grid": self.tilemap.off_grid.copy()
        })

        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)

    def _undo(self):
        if not self.undo_stack:
            return
        last_state = self.undo_stack.pop()
        self.tilemap.in_grid = last_state["in_grid"].copy()
        self.tilemap.off_grid = last_state["off_grid"].copy()

    def _update_mouse_position(self):
        self.mouse_world_pos = self.camera.screen_to_world(pg.mouse.get_pos())

        if self.in_grid_mode:
            self.mouse_world_pos.x = math.floor(self.mouse_world_pos.x / self.tilemap.tile_size) * self.tilemap.tile_size
            self.mouse_world_pos.y = math.floor(self.mouse_world_pos.y / self.tilemap.tile_size) * self.tilemap.tile_size

            self.tile_pos = pg.Vector2(self.mouse_world_pos.x // self.tilemap.tile_size, self.mouse_world_pos.y // self.tilemap.tile_size)
        else:
            self.tile_pos = pg.Vector2(self.mouse_world_pos.x / self.tilemap.tile_size, self.mouse_world_pos.y / self.tilemap.tile_size)

    def _handle_input(self):
        keys = pg.key.get_pressed()
        for event in self.app.events:
            if event.type == pg.KEYUP:
                #콜리션 토글
                if event.key == pg.K_c:
                    if self.in_grid_mode:
                        self.can_collide = not self.can_collide
                #그리드 모드 토글 (오프 그리드 모드 진입시 자동으로 콜리션 끔, 그리드 모드 진입시 그의 반대)
                if event.key == pg.K_TAB:
                    self.in_grid_mode = not self.in_grid_mode
                    self.can_collide = self.in_grid_mode
                    
                # 콜리션 뷰 토글
                if event.key == pg.K_v:
                    self.in_collision_view = not self.in_collision_view
                #오토 타일
                if event.key == pg.K_b:
                    self.tilemap.autotile()
                #저장
                if event.key == pg.K_o:
                    self.tilemap.save_file()
                #되돌리기
                if event.key == pg.K_z and keys[pg.K_LCTRL]:
                    self._undo()

            if event.type == pg.MOUSEBUTTONDOWN and not self.in_grid_mode:
                if event.button == 1:
                    self._place_tile_offgrid()
            
            if event.type == pg.MOUSEWHEEL:
                if keys[pg.K_LSHIFT]:
                    tile_type_name = self.tile_types[self.current_tile_type_index]
                    tile_variant_len = len(self.app.ASSET_TILEMAP[tile_type_name])
                    if event.y > 0:
                        self.current_tile_variant = (self.current_tile_variant + 1) % tile_variant_len
                    elif event.y < 0:
                        self.current_tile_variant = (self.current_tile_variant - 1) % tile_variant_len
                else:
                    self.current_tile_type_index = (self.current_tile_type_index + int(event.y)) % len(self.tile_types)
                    self.current_tile_variant = 0

        left, _, right = pg.mouse.get_pressed()
        if left:
            self._place_tile_grid()
        if right:
            self._remove_tile()

    def _move_camera(self):
        keys = pg.key.get_pressed()

        move_speed = 300 * self.app.dt / self.camera.scale
        if keys[pg.K_w]:
            self.camera.offset += pg.Vector2(0, -move_speed)
        if keys[pg.K_s]:
            self.camera.offset += pg.Vector2(0, move_speed)
        if keys[pg.K_a]:
            self.camera.offset += pg.Vector2(-move_speed, 0)
        if keys[pg.K_d]:
            self.camera.offset += pg.Vector2(move_speed, 0)

        for event in self.app.events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_q:
                    self.camera.scale += 0.5
                if event.key == pg.K_e:
                    self.camera.scale -= 0.5

    def _update_ui(self):
        self.view_mode_text_renderer.text = "[C] 현재 : 충돌 가능" if self.can_collide else "[C] 현재 : 충돌 X"
        self.grid_mode_text_renderer.text = "[Tab] 현재: 그리드" if self.in_grid_mode else "[Tab] 현재: 자유"
        self.view_mode_text_renderer.text = "[V] 현재 : 충돌범위 뷰" if self.in_collision_view else "[V] 현재 : 일반 뷰"
        self.current_tile_text_renderer.text = f"{self.tile_types[self.current_tile_type_index]} : [{self.current_tile_variant}]"

    def _draw_grid(self):
        if not self.in_grid_mode:
            return

        tile_size = self.tilemap.tile_size

        top_left_world = self.camera.screen_to_world(pg.Vector2(0, 0))
        bottom_right_world = self.camera.screen_to_world(SCREEN_SIZE)

        start_x = int(top_left_world.x // tile_size)
        end_x = int(bottom_right_world.x // tile_size) + 1
        start_y = int(top_left_world.y // tile_size)
        end_y = int(bottom_right_world.y // tile_size) + 1

        grid_color = pg.Color(100, 100, 100, 50)

        for x in range(start_x, end_x + 1):
            world_x_coord = x * tile_size
            screen_start = self.camera.world_to_screen(pg.Vector2(world_x_coord, top_left_world.y))
            screen_end = self.camera.world_to_screen(pg.Vector2(world_x_coord, bottom_right_world.y))
            pg.draw.line(self.app.surfaces[LAYER_INTERFACE], grid_color, screen_start, screen_end)

        for y in range(start_y, end_y + 1):
            world_y_coord = y * tile_size
            screen_start = self.camera.world_to_screen(pg.Vector2(top_left_world.x, world_y_coord))
            screen_end = self.camera.world_to_screen(pg.Vector2(bottom_right_world.x, world_y_coord))
            pg.draw.line(self.app.surfaces[LAYER_INTERFACE], grid_color, screen_start, screen_end)

    def _draw_collision(self):
        if not self.in_collision_view:
            return
        
        scaled_tile_size = int(self.tilemap.tile_size * self.camera.scale)
        for key in self.tilemap.in_grid.keys():
            tile_data = self.tilemap.in_grid[key]
            if not tile_data["can_collide"]:
                continue

            world_pos = pg.Vector2(tile_data["pos"][0] * self.tilemap.tile_size, tile_data["pos"][1] * self.tilemap.tile_size)
            screen_pos = self.camera.world_to_screen(world_pos)

            rect = pg.Rect(screen_pos.x, screen_pos.y, scaled_tile_size, scaled_tile_size)
            pg.draw.rect(self.app.surfaces[LAYER_INTERFACE], "blue", rect)

    def _draw_preview(self):
        tile_size = self.tilemap.tile_size
        scaled_tile_size = int(tile_size * self.camera.scale)
        
        preview_screen_pos = self.camera.world_to_screen(self.tile_pos*self.tilemap.tile_size)

        current_tile_type = self.tile_types[self.current_tile_type_index]
        current_tile_variant = self.current_tile_variant

        preview_image = self.camera.get_scaled_surface(self.app.ASSET_TILEMAP[current_tile_type][current_tile_variant].copy())
        preview_image.set_alpha(150)

        self.app.surfaces[LAYER_INTERFACE].blit(preview_image, preview_screen_pos)

        # 충돌 여부 표시 (빨간색 테두리)
        if self.can_collide:
            pg.draw.rect(self.app.surfaces[LAYER_INTERFACE], (255, 0, 0, 100), pg.Rect(preview_screen_pos.x, preview_screen_pos.y, scaled_tile_size, scaled_tile_size), 2)

    def _place_tile_grid(self):
        if not self.in_grid_mode:
            return
        if self.tile_types[self.current_tile_type_index] not in IN_GRID_TILES:
            return
        self._save_undo_state()
        self.tilemap.in_grid[f"{int(self.tile_pos.x)},{int(self.tile_pos.y)}"] = {
            "pos": [int(self.tile_pos.x), int(self.tile_pos.y)],
            "type": self.tile_types[self.current_tile_type_index],
            "variant": self.current_tile_variant,
            "can_collide": self.can_collide
        }

    def _place_tile_offgrid(self):
        if self.in_grid_mode:
            return
        self._save_undo_state() 
        self.tilemap.off_grid.append({
            "pos": [self.tile_pos.x, self.tile_pos.y],
            "type": self.tile_types[self.current_tile_type_index],
            "variant": self.current_tile_variant
        })

    def _remove_tile(self):
        if self.in_grid_mode:
            key = f"{int(self.tile_pos.x)},{int(self.tile_pos.y)}"
            if key in self.tilemap.in_grid:
                self._save_undo_state()
                del self.tilemap.in_grid[key]
        else:
            for object_data in self.tilemap.off_grid.copy():
                original_image = self.app.ASSET_TILEMAP[object_data["type"]][object_data["variant"]]
                size = original_image.get_size()
                rect = pg.Rect(object_data["pos"][0] * self.tilemap.tile_size, object_data["pos"][1] * self.tilemap.tile_size, size[0], size[1])
                if rect.collidepoint(self.mouse_world_pos):
                    self._save_undo_state()
                    self.tilemap.off_grid.remove(object_data)

    def on_update(self):
        super().on_update()
        self._update_mouse_position()
        self._handle_input()
        self._move_camera()
        self._update_ui()

    def on_draw(self):
        self._draw_grid()
        super().on_draw()
        self._draw_collision()
        self._draw_preview()