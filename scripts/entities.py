import pygame as pg

from .objects import GameObject
from .animation import Animation

class Entity(GameObject):
    # 월드에 존재하는 모든 객체의 기반 클래스임.
    # 위치, 크기, 애니메이션을 가짐.
    def __init__(self, pos: pg.Vector2, size: pg.Vector2, animation: Animation = None):
        super().__init__()
        self.pos = pos.copy()
        self.size = size.copy()
        self.animation = animation
        self.flipx = False
        self.flipy = False

    def rect(self) -> pg.Rect:
        # 충돌 박스를 반환함.
        return pg.Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)

    def set_action(self, action_name: str):
        # 새로운 액션으로 애니메이션을 변경함.
        # NOTE: 자식 클래스에서 이 메소드를 구현해야 함.
        pass

    def on_update(self):
        # 매 프레임 애니메이션을 업데이트함.
        if self.animation:
            self.animation.update()

    def on_draw(self):
        # 화면에 현재 애니메이션 프레임을 그림.
        if self.animation:
            image = self.animation.img()
            flipped_image = pg.transform.flip(image, self.flipx, self.flipy)
            self.app.scene.camera.blit(flipped_image, self.pos)

class PhysicsEntity(Entity):
    # 중력과 속도 등 물리 효과의 영향을 받는 객체임.
    def __init__(self, pos: pg.Vector2, size: pg.Vector2, animation: Animation = None):
        super().__init__(pos, size, animation)
        self.velocity = pg.Vector2(0, 0)
        self.gravity_scale = 1.0
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

    def on_update(self):
        # 물리 계산을 먼저 수행하고, 그 다음에 애니메이션을 업데이트함.
        self._update_physics()
        super().on_update()

    def _update_physics(self):
        # 물리 계산 및 충돌 처리를 수행함.
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        # 중력 적용
        gravity_accel = 450 # 픽셀/초^2
        self.velocity.y += gravity_accel * self.app.dt * self.gravity_scale
        
        # 프레임에 따른 이동량 계산
        frame_movement = self.velocity.copy() * self.app.dt

        # X축 이동 및 충돌 처리
        self.pos.x += frame_movement.x
        entity_rect = self.rect()
        for tile_rect in self.app.scene.tilemap.get_colliding_tiles(entity_rect):
            if frame_movement.x > 0: # 오른쪽으로 이동 중
                entity_rect.right = tile_rect.left
                self.collisions['right'] = True
            elif frame_movement.x < 0: # 왼쪽으로 이동 중
                entity_rect.left = tile_rect.right
                self.collisions['left'] = True
            self.pos.x = entity_rect.x

        # Y축 이동 및 충돌 처리
        self.pos.y += frame_movement.y
        entity_rect = self.rect()
        for tile_rect in self.app.scene.tilemap.get_colliding_tiles(entity_rect):
            if frame_movement.y > 0: # 아래로 이동 중
                entity_rect.bottom = tile_rect.top
                self.collisions['down'] = True
            elif frame_movement.y < 0: # 위로 이동 중
                entity_rect.top = tile_rect.bottom
                self.collisions['up'] = True
            self.pos.y = entity_rect.y
        
        # y축 충돌 시 y축 속도를 0으로 리셋함.
        if self.collisions['down'] or self.collisions['up']:
            self.velocity.y = 0

class Player(PhysicsEntity):
    # 플레이어가 직접 조종하는 객체임.
    def __init__(self, pos: pg.Vector2, size: pg.Vector2):
        super().__init__(pos, size)
        self.speed = 200
        self.jump_power = -5
        self.airtime = 0
        self.jumps = 2
        self.set_action('idle')

    def set_action(self, action_name: str):
        # 현재 액션과 다를 경우에만 애니메이션을 새로 불러옴.
        if not hasattr(self, 'action') or self.action != action_name:
            self.action = action_name
            self.animation = self.app.ASSET_PLAYER[action_name].copy()

    def on_update(self):
        # 입력 처리
        self._handle_input()

        # 물리 및 충돌 처리 (부모 클래스 호출)
        super().on_update()

        # 충돌 결과에 따른 상태 업데이트
        if self.collisions['down']:
            self.airtime = 0
            self.jumps = 2
        else:
            self.airtime += 1
        
        # 상태에 따른 애니메이션 업데이트
        self._update_animation()

    def _handle_input(self):
        # 키 입력에 따라 속도를 조절함.
        keys = pg.key.get_pressed()
        
        self.velocity.x = 0
        if keys[pg.K_a]:
            self.velocity.x = -self.speed
            self.flipx = True
        if keys[pg.K_d]:
            self.velocity.x = self.speed
            self.flipx = False

        # 점프
        for event in self.app.events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.jump()

    def _update_animation(self):
        # 현재 상태에 따라 애니메이션 액션을 변경함.
        if self.airtime > 1:
            self.set_action('jump')
        elif self.velocity.x != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

    def jump(self):
        if self.jumps > 0:
            self.velocity.y = self.jump_power
            self.jumps -= 1
            self.airtime = 2 # 점프 직후 바로 점프 애니메이션으로 변경하기 위함