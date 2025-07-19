import pygame as pg
import math

from .tilemap import *
from .ui import *
from .values import *
from .objects import *
from .camera import *

class Scene:
    def __init__(self):
        from .app import App
        self.app = App.singleton
    
    def on_scene_start(self):
        self.camera = Camera2D(1, pg.Vector2(0, 0))

        self._fps_text = StringValue("")
        TextRenderer(self._fps_text, pg.Vector2(SCREEN_SIZE.x - 55, 10), color="green", use_camera=False)

    def _update_fps_text(self):
        self._fps_text.value = str(round(self.app.clock.get_fps()))
    
    def on_scene_end(self):
        GameObject.object_list.clear()
    
    #얘네 둘이는 굳이 먼저 부를필요 없음 자울적으로 하면 됨.
    def on_update(self):
        GameObject.update_all()
        self._update_fps_text()
        UserInterface.update_all()

    def on_draw(self):
        GameObject.draw_all()
        self.camera.on_draw()
        UserInterface.draw_all()

class TestScene(Scene):
    def __init__(self):
        super().__init__()
    
    def on_scene_start(self):
        super().on_scene_start()
        self.tilemap = Tilemap()

    def on_update(self):
        super().on_update()
        keys = pg.key.get_pressed()
        dt = self.app.dt

        move_speed = 300 * dt / self.camera.scale
        if keys[pg.K_w]:
            self.camera.offset += pg.Vector2(0, -move_speed)
        if keys[pg.K_s]:
            self.camera.offset += pg.Vector2(0, +move_speed)
        if keys[pg.K_a]:
            self.camera.offset += pg.Vector2(-move_speed, 0)
        if keys[pg.K_d]:
            self.camera.offset += pg.Vector2(+move_speed, 0)
    
    def on_draw(self):
        super().on_draw()

class TileMapEditScene(Scene):
    def __init__(self):
        super().__init__()

    def on_scene_start(self):
        super().on_scene_start()
        self.tilemap = Tilemap("temp.json")

        self.tile_types = list(self.app.ASSET_TILEMAP.keys())
        self.current_tile_type_index = 0
        self.current_tile_variant = 0

        self.can_collide = True
        self.collide_mode_text = StringValue("[C] 현재 : 충돌 가능")

        self.in_grid_mode = True
        self.grid_mode_text = StringValue("[Tab] 현재: 그리드")

        self.in_collision_view = False
        self.view_mode_text = StringValue("[V] 현재 : 일반 뷰")

        self.current_tile_text = StringValue(f"{self.tile_types[self.current_tile_type_index]} : [{self.current_tile_variant}]")

        TextRenderer("[WASD] 움직이기 | [Q,E]로 줌 인,아웃", pg.Vector2(10, 10), color="black", use_camera=False)
        TextRenderer(self.collide_mode_text, pg.Vector2(10, 35), color="blue", use_camera=False)
        TextRenderer(self.grid_mode_text, pg.Vector2(10, 60), color="black", use_camera=False)
        TextRenderer(self.view_mode_text, pg.Vector2(10, 85), color="black", use_camera=False)
        TextRenderer("[B] 오토 타일", pg.Vector2(10, 110), color="black", use_camera=False)
        TextRenderer("[엔터] 타일 종류 변경 | [휠] 타일 인덱스 변경", pg.Vector2(10, 135), color="black", use_camera=False)
        TextRenderer(self.current_tile_text, pg.Vector2(10, 165), color="red", use_camera=False)
        TextRenderer("[O] 저장하기 (temp.json에 저장됨.)", pg.Vector2(10, 190), color="black", use_camera=False)

        self.mouse_world_pos = pg.Vector2(0, 0)
        self.tile_pos = pg.Vector2(0, 0)

    def _update_mouse_position(self):
        self.mouse_world_pos = self.camera.screen_to_world(pg.mouse.get_pos())

        if self.in_grid_mode:
            self.mouse_world_pos.x = math.floor(self.mouse_world_pos.x / self.tilemap.tile_size) * self.tilemap.tile_size
            self.mouse_world_pos.y = math.floor(self.mouse_world_pos.y / self.tilemap.tile_size) * self.tilemap.tile_size

            self.tile_pos = pg.Vector2(self.mouse_world_pos.x // self.tilemap.tile_size, self.mouse_world_pos.y // self.tilemap.tile_size)
        else:
            self.tile_pos = pg.Vector2(self.mouse_world_pos.x / self.tilemap.tile_size, self.mouse_world_pos.y / self.tilemap.tile_size)

    def _handle_input(self):
        for event in self.app.events:
            if event.type == pg.KEYUP:
                if event.key == pg.K_c:
                    if self.in_grid_mode:
                        self.can_collide = not self.can_collide
                if event.key == pg.K_TAB:
                    self.in_grid_mode = not self.in_grid_mode
                    if not self.in_grid_mode:
                        self.can_collide = False
                if event.key == pg.K_v:
                    self.in_collision_view = not self.in_collision_view
                if event.key == pg.K_b:
                    self.tilemap.autotile()
                if event.key == pg.K_RETURN:
                    self.current_tile_type_index = (self.current_tile_type_index + 1) % len(self.tile_types)
                    self.current_tile_variant = 0
                if event.key == pg.K_o:
                    self.tilemap.save_file()

            if event.type == pg.MOUSEBUTTONDOWN and not self.in_grid_mode:
                if event.button == 1:
                    self._place_tile_offgrid()

            if event.type == pg.MOUSEWHEEL:
                tile_type_name = self.tile_types[self.current_tile_type_index]
                tile_variant_len = len(self.app.ASSET_TILEMAP[tile_type_name])
                if event.y > 0:
                    self.current_tile_variant = (self.current_tile_variant + 1) % tile_variant_len
                elif event.y < 0:
                    self.current_tile_variant = (self.current_tile_variant - 1) % tile_variant_len

        left, _, right = pg.mouse.get_pressed()
        if left:
            self._place_tile_grid()
        if right:
            self._remove_tile()

    def _move_camera(self):
        keys = pg.key.get_pressed()
        dt = self.app.dt

        move_speed = 300 * dt / self.camera.scale
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
        self.collide_mode_text.value = "[C] 현재 : 충돌 가능" if self.can_collide else "[C] 현재 : 충돌 X"
        self.grid_mode_text.value = "[Tab] 현재: 그리드" if self.in_grid_mode else "[Tab] 현재: 자유"
        self.view_mode_text.value = "[V] 현재 : 충돌범위 뷰" if self.in_collision_view else "[V] 현재 : 일반 뷰"
        self.current_tile_text.value = f"{self.tile_types[self.current_tile_type_index]} : [{self.current_tile_variant}]"

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
            pg.draw.line(self.app.screen, grid_color, screen_start, screen_end)

        for y in range(start_y, end_y + 1):
            world_y_coord = y * tile_size
            screen_start = self.camera.world_to_screen(pg.Vector2(top_left_world.x, world_y_coord))
            screen_end = self.camera.world_to_screen(pg.Vector2(bottom_right_world.x, world_y_coord))
            pg.draw.line(self.app.screen, grid_color, screen_start, screen_end)

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
            pg.draw.rect(self.app.screen, "blue", rect)

    def _draw_preview(self):
        tile_size = self.tilemap.tile_size
        scaled_tile_size = int(tile_size * self.camera.scale)
        
        preview_screen_pos = self.camera.world_to_screen(self.tile_pos*self.tilemap.tile_size)

        current_tile_type = self.tile_types[self.current_tile_type_index]
        current_tile_variant = self.current_tile_variant

        preview_image = self.camera.get_scaled_surface(self.app.ASSET_TILEMAP[current_tile_type][current_tile_variant].copy())
        preview_image.set_alpha(150)

        self.app.screen.blit(preview_image, preview_screen_pos)

        # 충돌 여부 표시 (빨간색 테두리)
        if self.can_collide:
            pg.draw.rect(self.app.screen, (255, 0, 0, 100), pg.Rect(preview_screen_pos.x, preview_screen_pos.y, scaled_tile_size, scaled_tile_size), 2)

    def _place_tile_grid(self):
        if not self.in_grid_mode:
            return
        if self.tile_types[self.current_tile_type_index] not in IN_GRID_TILES:
            return
        self.tilemap.in_grid[f"{int(self.tile_pos.x)},{int(self.tile_pos.y)}"] = {
            "pos": [int(self.tile_pos.x), int(self.tile_pos.y)],
            "type": self.tile_types[self.current_tile_type_index],
            "variant": self.current_tile_variant,
            "can_collide": self.can_collide
        }

    def _place_tile_offgrid(self):
        if self.in_grid_mode:
            return
        self.tilemap.off_grid.append({
            "pos": [self.tile_pos.x, self.tile_pos.y],
            "type": self.tile_types[self.current_tile_type_index],
            "variant": self.current_tile_variant
        })

    def _remove_tile(self):
        if self.in_grid_mode:
            key = f"{int(self.tile_pos.x)},{int(self.tile_pos.y)}"
            if key in self.tilemap.in_grid:
                del self.tilemap.in_grid[key]
        else:
            for object_data in self.tilemap.off_grid.copy():
                original_image = self.app.ASSET_TILEMAP[object_data["type"]][self.current_tile_variant]
                size = original_image.get_size()
                rect = pg.Rect(object_data["pos"][0] * self.tilemap.tile_size, object_data["pos"][1] * self.tilemap.tile_size, size[0], size[1])
                if rect.collidepoint(self.mouse_world_pos):
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
