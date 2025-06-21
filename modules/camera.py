import pygame as pg

class Camera2D:
    def __init__(self):
        self.sprite_groups : dict[str, pg.sprite.Group] = {
            "background" : pg.sprite.Group(),
            "objects" : pg.sprite.Group(),
            "entities" : pg.sprite.Group(),
            "light" : pg.sprite.Group(),
        }
        self.offset : pg.Vector2 = pg.Vector2(0, 0)
        self.scale : float = 1

    def update(self, delta_time):
        pass

    def draw(self, main_screen: pg.surface.Surface):
        layer_order = ["background", "objects", "entities", "light"]
        
        for layer in layer_order:
            if layer not in self.sprite_groups:
                continue
            
            group = self.sprite_groups[layer]
            for sprite in group:
                if not hasattr(sprite, "image") or not hasattr(sprite, "rect"):
                    continue  # 안전하게 스킵

                # 위치 조정 (offset + scale 적용)
                pos = pg.Vector2(sprite.rect.topleft)
                draw_pos = (pos - self.offset) * self.scale

                # 이미지 크기도 스케일 적용
                image = sprite.image
                if self.scale != 1:
                    w, h = image.get_size()
                    image = pg.transform.smoothscale(image, (int(w * self.scale), int(h * self.scale)))

                # 라이트는 additive blending
                if layer == "light":
                    main_screen.blit(image, draw_pos, special_flags=pg.BLEND_RGB_ADD)
                else:
                    main_screen.blit(image, draw_pos)