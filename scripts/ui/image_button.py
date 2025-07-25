import pygame as pg

from datas.const import *

from scripts.objects import GameObject

class ImageButton(GameObject):
    def __init__(self, 
                 name : str, 
                 position : pg.Vector2, 
                 action : callable):
        super().__init__()
        self.name = name
        self.pos = position
        self.action = action

        self.hover_image = self.app.ASSET_UI["image_button"][name]["on_hover"]
        self.hover_not_image = self.app.ASSET_UI["image_button"][name]["on_not_hover"]
        self.render_image = self.hover_not_image

        size = self.hover_image.get_size()
        self.rect = pg.Rect(self.pos.x, self.pos.y, size[0], size[1])

    def on_update(self):
        super().on_update()

        is_hovered = False

        mouse_pos = pg.Vector2(pg.mouse.get_pos())
        if self.rect.collidepoint(mouse_pos):
            is_hovered = True

        if is_hovered:
            self.render_image = self.hover_image
        else : self.render_image = self.hover_not_image

        for event in self.app.events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and is_hovered:
                self.action()

    def on_draw(self):
        super().on_draw()

        camera = self.app.scene.camera
        screen = self.app.surfaces[LAYER_INTERFACE]
        screen.blit(camera.get_scaled_surface(self.render_image), self.pos)