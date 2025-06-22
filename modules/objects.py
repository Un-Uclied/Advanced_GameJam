import pygame as pg

from .camera import Camera2D

class ObjectManager:
    def __init__(self):
        self.objects : list[GameObject]= []
        self.objects : dict[str, list[GameObject]] = {
            "background" : [], # 얘는 하늘 이나 우주 등
            "statics" : [], #벽, 통, 풀, 나무 등
            "particles" : [], #탄환, 파티클 등
            "dynamics" : [], #플레이어, 적 등

            "lights" : [] 
        }

    def add(self, cls, layer_name, *args, **kwargs):
        new_object = cls(*args, **kwargs)
        self.objects[layer_name].append(new_object)
        return new_object
    
    def remove(self, instance):
        for layer_name in self.objects.keys():
            for instance in self.objects[layer_name]:
                self.objects[layer_name].remove(instance)

    def update(self, delta_time, events):
        for layer_name in self.objects.keys():
            for instance in self.objects[layer_name]:
                instance.update(delta_time, events)

    def draw(self, draw_screen: pg.Surface, camera: Camera2D):
        for layer_name in self.objects.keys():
            for instance in self.objects[layer_name]:
                world_pos = instance.get_position()
                screen_pos = camera.world_to_screen(world_pos)

                image = instance.image
                scale = camera.scale

                if scale != 1.0:
                    image = pg.transform.smoothscale(image, (
                        int(image.get_width() * scale),
                        int(image.get_height() * scale)
                    ))

                # 스케일된 이미지 기준으로 앵커 보정
                img_w, img_h = image.get_size()
                anchor_offset = pg.Vector2(
                    img_w * instance.anchor.x,
                    img_h * instance.anchor.y
                )

                screen_topleft = screen_pos - anchor_offset

                draw_screen.blit(image, screen_topleft)
                self.draw_hitbox(draw_screen, camera, instance)

    def draw_hitbox(self, surface: pg.Surface, camera: Camera2D, instance):
        # rect 좌표는 월드 좌표 기준이니까 스크린 좌표로 변환
        screen_pos = camera.world_to_screen(pg.Vector2(instance.rect.topleft))

        # 크기는 스케일 반영해서 조절
        w = int(instance.rect.width * camera.scale)
        h = int(instance.rect.height * camera.scale)

        rect = pg.Rect(screen_pos.x, screen_pos.y, w, h)

        pg.draw.rect(surface, (255, 0, 0), rect, 2)  # 빨간색, 두께 2로 그리기

class GameObject(pg.sprite.Sprite):
    def __init__(self, image: pg.Surface, anchor: pg.Vector2 = pg.Vector2(.5, .5)):
        super().__init__()

        self.image = image
        self.pos = pg.Vector2(0, 0)  # 월드 위치
        self.anchor = anchor

        self.rect = pg.Rect(0, 0, 0, 0)
        self.update_rect()

    def update(self, delta_time, events):
        pass
    
    # private
    def update_rect(self):
        w, h = self.image.get_size()

        # 앵커 기준으로 좌상단 위치 구함
        topleft_x = self.pos.x - w * self.anchor.x
        topleft_y = self.pos.y - h * self.anchor.y

        self.rect = pg.Rect(int(topleft_x), int(topleft_y), w, h)

    def set_position(self, x: float, y: float):
        self.pos.update(x, y)
        self.update_rect()

    def set_anchor(self, x: float, y: float):
        self.anchor.update(x, y)
        self.update_rect()

    def get_position(self) -> pg.Vector2:
        return self.pos

