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
        self.tile_types = list(App.singleton.ASSET_TILEMAP["tiles"].keys())
        self.current_tile_type_index = 0
        self.current_tile_variant = 0

        self.can_collide = True
        self.collide_mode_text = StringValue("[C] 현재 : 충돌 가능")

        self.in_grid_mode = True
        self.grid_mode_text = StringValue("[Tab] 현재: 그리드")

        self.mouse_world_pos = pg.Vector2(0, 0)
        self.tile_pos = pg.Vector2(0, 0)

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

    def _place_tile(self):
        if (self.in_grid_mode):
            self.tilemap._tiles[f"{int(self.tile_pos.x)},{int(self.tile_pos.y)}"] = {"pos" : [int(self.tile_pos.x), int(self.tile_pos.y)], "type" : self.tile_types[self.current_tile_type_index], "variant" : self.current_tile_variant, "can_collide" : self.can_collide}
        else:
            self.tilemap._objects.append({"pos" : [self.tile_pos.x, self.tile_pos.y], "type" : self.tile_types[self.current_tile_type_index], "variant" : self.current_tile_variant})

    def _remove_tile(self):
        key = f"{self.tile_pos.x},{self.tile_pos.y}"
        if (self.in_grid_mode):
            if key in self.tilemap._tiles:
                del self.tilemap._tiles[key]
        else:
            for object_data in self.tilemap._objects.copy():
                pass

    def on_update(self):
        super().on_update()

        self._move_camera()

        self.mouse_world_pos = self.camera.screen_to_world(pg.mouse.get_pos())

        if (self.in_grid_mode):
            self.mouse_world_pos.x = math.floor(self.mouse_world_pos.x / self.tilemap.tile_size) * self.tilemap.tile_size
            self.mouse_world_pos.y = math.floor(self.mouse_world_pos.y / self.tilemap.tile_size) * self.tilemap.tile_size

            self.tile_pos = pg.Vector2(self.mouse_world_pos.x // self.tilemap.tile_size, self.mouse_world_pos.y // self.tilemap.tile_size)
        else:
            self.tile_pos = pg.Vector2(self.mouse_world_pos.x / self.tilemap.tile_size, self.mouse_world_pos.y / self.tilemap.tile_size)

        from .app import App
        for event in App.singleton.events:
            if event.type == pg.KEYUP:
                if event.key == pg.K_c:
                    self.can_collide = not self.can_collide
                if event.key == pg.K_TAB:
                    self.in_grid_mode = not self.grid_mode_text

        left, middle, right = pg.mouse.get_pressed()
        if left:
            self._place_tile()
        if right:
            self._remove_tile()

        self._update_ui()

    def on_draw(self):
        super().on_draw()

        from .app import App
        camera = self.camera
        tile_size = self.tilemap.tile_size
        scaled_tile_size = int(tile_size * camera.scale)

        if scaled_tile_size <= 0: # 스케일 0이면 크래시 남;
            return

        # 그리드 그리기 (in_grid_mode가 True일 때만)
        if self.in_grid_mode:
            # 화면의 좌상단 월드 좌표
            top_left_world = camera.screen_to_world(pg.Vector2(0, 0))
            # 화면의 우하단 월드 좌표
            bottom_right_world = camera.screen_to_world(pg.Vector2(SCREEN_SIZE[0], SCREEN_SIZE[1]))

            # 보이는 그리드 좌표 범위
            start_x = int(top_left_world.x // tile_size)
            end_x = int(bottom_right_world.x // tile_size) + 1
            start_y = int(top_left_world.y // tile_size)
            end_y = int(bottom_right_world.y // tile_size) + 1

            grid_color = (150, 150, 150, 100) # 회색, 투명도 100
            
            # 세로선 그리기
            for x in range(start_x, end_x + 1):
                world_x_coord = x * tile_size
                screen_x_coord = camera.world_to_screen(pg.Vector2(world_x_coord, 0)).x
                pg.draw.line(App.singleton.screen, grid_color, (screen_x_coord, 0), (screen_x_coord, SCREEN_SIZE[1]))

            # 가로선 그리기
            for y in range(start_y, end_y + 1):
                world_y_coord = y * tile_size
                screen_y_coord = camera.world_to_screen(pg.Vector2(0, world_y_coord)).y
                pg.draw.line(App.singleton.screen, grid_color, (0, screen_y_coord), (SCREEN_SIZE[0], screen_y_coord))

        # 마우스 위치에 현재 선택된 타일 미리보기 그리기
        mouse_pos_screen = pg.mouse.get_pos()
        mouse_pos_world = self.camera.screen_to_world(pg.Vector2(mouse_pos_screen))
        hover_grid_x = int(mouse_pos_world.x // tile_size)
        hover_grid_y = int(mouse_pos_world.y // tile_size)

        # 미리보기 타일의 월드 좌표 (그리드에 스냅)
        preview_world_pos = pg.Vector2(hover_grid_x * tile_size, hover_grid_y * tile_size)
        preview_screen_pos = camera.world_to_screen(preview_world_pos)

        current_tile_type = self.tile_types[self.current_tile_type_index]
        current_tile_variant = self.current_tile_variant

        # 미리보기 이미지 가져오기 및 스케일링
        preview_image = App.singleton.ASSET_TILEMAP["tiles"][current_tile_type][current_tile_variant].copy()
        preview_image = pg.transform.scale(preview_image, (scaled_tile_size, scaled_tile_size))

        # 미리보기 이미지에 투명도 적용 (선택된 타일임을 시각적으로 나타냄)
        preview_image.set_alpha(150) # 0 (완전 투명) ~ 255 (완전 불투명)

        App.singleton.screen.blit(preview_image, preview_screen_pos)

        # 충돌 여부 표시 (빨간색 테두리)
        if self.can_collide:
            pg.draw.rect(App.singleton.screen, (255, 0, 0, 100), pg.Rect(preview_screen_pos.x, preview_screen_pos.y, scaled_tile_size, scaled_tile_size), 2)
