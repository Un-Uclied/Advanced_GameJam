import pygame as pg
import math

from .tilemap import *
from .text import *
from .values import *
from .game_objects import *
from .camera import *

class Scene:
    def __init__(self):
        pass
    
    def on_scene_start(self):
        GameObject.current_scene = self

    def on_scene_end(self):
        GameObject.current_scene = None

    def on_update(self):
        GameObject.update_all()

    def on_draw(self):
        GameObject.draw_all()

class TestScene(Scene):
    pass

class TileMapEditScene(Scene):
    def __init__(self):
        super().__init__()
        self.tilemap = Tilemap("temp.json")
        self.camera = Camera2D(1, pg.Vector2(0, 0))

        from .app import App
        self.tile_types = list(App.singleton.ASSET_TILEMAP.keys())
        self.current_tile_type_index = 0
        self.current_tile_variant = 0

        self.can_collide = True
        self.collide_mode_text = StringValue("[C] 현재 : 충돌 가능")

        self.in_grid_mode = True
        self.grid_mode_text = StringValue("[Tab] 현재: 그리드")

        self.in_collision_view = False
        self.view_mode_text = StringValue("[V] 현재 : 일반 뷰")

        self.current_tile_text = StringValue(f"{self.tile_types[self.current_tile_type_index]} : [{self.current_tile_variant}]")

        TextRenderer("[WASD] 움직이기 | [Q,E]로 줌 인,아웃", pg.Vector2(10, 10), color="black",use_camera=False)
        TextRenderer(self.collide_mode_text, pg.Vector2(10, 35), color="black",use_camera=False)
        TextRenderer(self.grid_mode_text, pg.Vector2(10, 60), color="black",use_camera=False)
        TextRenderer(self.view_mode_text, pg.Vector2(10, 85), color="black", use_camera=False)
        TextRenderer("[B] 오토 타일", pg.Vector2(10, 110), color="black",use_camera=False)
        TextRenderer("[엔터] 타일 종류 변경 | [휠] 타일 인덱스 변경", pg.Vector2(10, 135), color="black",use_camera=False)
        TextRenderer(self.current_tile_text, pg.Vector2(10, 165), color="red", use_camera=False)


        self.mouse_world_pos = pg.Vector2(0, 0)
        self.tile_pos = pg.Vector2(0, 0)

    def _update_mouse_position(self):
        self.mouse_world_pos = self.camera.screen_to_world(pg.mouse.get_pos())

        if (self.in_grid_mode):
            self.mouse_world_pos.x = math.floor(self.mouse_world_pos.x / self.tilemap.tile_size) * self.tilemap.tile_size
            self.mouse_world_pos.y = math.floor(self.mouse_world_pos.y / self.tilemap.tile_size) * self.tilemap.tile_size

            self.tile_pos = pg.Vector2(self.mouse_world_pos.x // self.tilemap.tile_size, self.mouse_world_pos.y // self.tilemap.tile_size)
        else:
            self.tile_pos = pg.Vector2(self.mouse_world_pos.x / self.tilemap.tile_size, self.mouse_world_pos.y / self.tilemap.tile_size)

    def _handle_input(self):
        from .app import App
        for event in App.singleton.events:
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

            if event.type == pg.MOUSEBUTTONDOWN and not self.in_grid_mode:
                if event.button == 1:
                    self._place_tile_offgrid()

            if event.type == pg.MOUSEWHEEL:
                tile_type_name = self.tile_types[self.current_tile_type_index]
                tile_variant_len = len(App.singleton.ASSET_TILEMAP[tile_type_name])
                if event.y > 0: # 휠 올림
                    self.current_tile_variant = (self.current_tile_variant + 1) % tile_variant_len
                elif event.y < 0:
                    self.current_tile_variant = (self.current_tile_variant - 1) % tile_variant_len

        left, middle, right = pg.mouse.get_pressed()
        if left:
            self._place_tile_grid()
        if right:
            self._remove_tile()

    def _move_camera(self):
        from .app import App

        keys = pg.key.get_pressed()
        dt = App.singleton.dt

        move_speed = 300 * dt / self.camera.scale # 스케일에 따라 이동 속도 조절
        if keys[pg.K_w]:
            self.camera.offset += pg.Vector2(0, -move_speed)
        if keys[pg.K_s]:
            self.camera.offset += pg.Vector2(0, +move_speed)
        if keys[pg.K_a]:
            self.camera.offset += pg.Vector2(-move_speed, 0)
        if keys[pg.K_d]:
            self.camera.offset += pg.Vector2(+move_speed, 0)

        # 카메라 확대/축소
        zoom_speed = 0.5 * dt
        if keys[pg.K_q]:
            self.camera.scale = max(0.1, self.camera.scale - zoom_speed) # 최소 스케일 제한
        if keys[pg.K_e]:
            self.camera.scale = min(5.0, self.camera.scale + zoom_speed) # 최대 스케일 제한

    def _update_ui(self):
        self.collide_mode_text.value = "[C] 현재 : 충돌 가능" if self.can_collide else "[C] 현재 : 충돌 X"
        self.grid_mode_text.value = "[Tab] 현재: 그리드" if self.in_grid_mode else "[Tab] 현재: 자유"
        self.view_mode_text.value = "[V] 현재 : 충돌범위 뷰" if self.in_collision_view else "[V] 현재 : 일반 뷰"
        self.current_tile_text.value = f"{self.tile_types[self.current_tile_type_index]} : [{self.current_tile_variant}]"

    def _draw_grid(self):
        from .app import App
        tile_size = self.tilemap.tile_size

        if self.in_grid_mode:
            # 화면의 좌상단 월드 좌표
            top_left_world = self.camera.screen_to_world(pg.Vector2(0, 0))
            # 화면의 우하단 월드 좌표
            bottom_right_world = self.camera.screen_to_world(pg.Vector2(SCREEN_SIZE[0], SCREEN_SIZE[1]))

            # 보이는 그리드 좌표 범위
            start_x = int(top_left_world.x // tile_size)
            end_x = int(bottom_right_world.x // tile_size) + 1
            start_y = int(top_left_world.y // tile_size)
            end_y = int(bottom_right_world.y // tile_size) + 1

            grid_color = pg.Color(100, 100, 100, 50)
            
            # 세로선 그리기
            for x in range(start_x, end_x + 1):
                world_x_coord = x * tile_size
                screen_x_coord = self.camera.world_to_screen(pg.Vector2(world_x_coord, 0)).x
                pg.draw.line(App.singleton.screen, grid_color, (screen_x_coord, 0), (screen_x_coord, SCREEN_SIZE[1]))

            # 가로선 그리기
            for y in range(start_y, end_y + 1):
                world_y_coord = y * tile_size
                screen_y_coord = self.camera.world_to_screen(pg.Vector2(0, world_y_coord)).y
                pg.draw.line(App.singleton.screen, grid_color, (0, screen_y_coord), (SCREEN_SIZE[0], screen_y_coord))

    def _draw_collision(self):
        if not self.in_collision_view:
            return
        
        from .app import App
        scaled_tile_size = int(self.tilemap.tile_size * self.camera.scale)
        for key in self.tilemap._tiles.keys():
            tile_data = self.tilemap._tiles[key]
            if not tile_data["can_collide"]:
                continue

            world_pos = pg.Vector2(tile_data["pos"][0] * self.tilemap.tile_size, tile_data["pos"][1] * self.tilemap.tile_size)
            screen_pos = self.camera.world_to_screen(world_pos)

            rect = pg.Rect(screen_pos.x, screen_pos.y, scaled_tile_size, scaled_tile_size)
            pg.draw.rect(App.singleton.screen, "blue", rect)

    def _draw_preview(self):
        from .app import App
        
        tile_size = self.tilemap.tile_size
        scaled_tile_size = int(tile_size * self.camera.scale)
        
        preview_screen_pos = self.camera.world_to_screen(self.tile_pos*self.tilemap.tile_size)

        current_tile_type = self.tile_types[self.current_tile_type_index]
        current_tile_variant = self.current_tile_variant

        # 미리보기 이미지 가져오기 및 스케일링
        preview_image = App.singleton.ASSET_TILEMAP[current_tile_type][current_tile_variant].copy()
        preview_image = self.camera.get_scaled_surface(preview_image)

        # 미리보기 이미지에 투명도 적용 (선택된 타일임을 시각적으로 나타냄)
        preview_image.set_alpha(150) # 0 (완전 투명) ~ 255 (완전 불투명)

        App.singleton.screen.blit(preview_image, preview_screen_pos)

        # 충돌 여부 표시 (빨간색 테두리)
        if self.can_collide:
            pg.draw.rect(App.singleton.screen, (255, 0, 0, 100), pg.Rect(preview_screen_pos.x, preview_screen_pos.y, scaled_tile_size, scaled_tile_size), 2)

    def _place_tile_grid(self):
        if not self.in_grid_mode : return
        if not self.tile_types[self.current_tile_type_index] in AUTOTILE_TYPES:
            return # 그리드에는 타일 타입만 둘수 있음.
        self.tilemap._tiles[f"{int(self.tile_pos.x)},{int(self.tile_pos.y)}"] = {"pos" : [int(self.tile_pos.x), int(self.tile_pos.y)], "type" : self.tile_types[self.current_tile_type_index], "variant" : self.current_tile_variant, "can_collide" : self.can_collide}
            
    def _place_tile_offgrid(self):
        if self.in_grid_mode : return
        self.tilemap._objects.append({"pos" : [self.tile_pos.x, self.tile_pos.y], "type" : self.tile_types[self.current_tile_type_index], "variant" : self.current_tile_variant})

    def _remove_tile(self):
        from .app import App
        if (self.in_grid_mode):
            key = f"{int(self.tile_pos.x)},{int(self.tile_pos.y)}"
            if key in self.tilemap._tiles:
                del self.tilemap._tiles[key]
        else:
            for object_data in self.tilemap._objects.copy():
                original_image = App.singleton.ASSET_TILEMAP[object_data["type"]][self.current_tile_variant]
                size = original_image.get_size()
                rect = pg.Rect(object_data["pos"][0] * self.tilemap.tile_size, object_data["pos"][1] * self.tilemap.tile_size, size[0], size[1])
                if rect.collidepoint(self.mouse_world_pos):
                    self.tilemap._objects.remove(object_data)

    def on_update(self):
        super().on_update()

        self._update_mouse_position()
        self._handle_input()

        self._move_camera()

        self._update_ui()

    def on_draw(self):
        if int(self.tilemap.tile_size * self.camera.scale) <= 0:
            return

        self._draw_grid()
        super().on_draw() #텍스트 같은 게임오브젝트들은 그리드 위에 그리기 ㅇㅇ
        self._draw_collision()
        self._draw_preview()

        
