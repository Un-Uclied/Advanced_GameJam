import pygame as pg

from datas.const import *
from .animation import *
from .objects import *
from .outline import *
from .ai import *
from .entities import *

from .status import *

class OneAlpha(PhysicsEntity):
    def __init__(self, rect):
        self.outline = Outline(self, "red")
        super().__init__("one_alpha", rect, invert_x=True)
        self.ai = WanderAI(self, move_speed=2.2)

        self.flip_offset = {
            False: pg.Vector2(-12, -5),
            True: pg.Vector2(-12, -5)
        }

    def control_animation(self):
        if self.ai.direction.x == 0:
            self.set_action("idle")
        else:
            self.set_action("run")
        
    def destroy(self):
        super().destroy()
        self.outline.destroy()

    def on_update(self):
        super().on_update()
        self.ai.on_update()
        self.control_animation()

        self.velocity.x = self.ai.direction.x * self.ai.move_speed * 100

        pc = self.app.scene.pc
        if self.rect.colliderect(pc.rect):
            PlayerStatus.singleton.health -= ATTACK_DMGS[self.name]

class OneBeta(PhysicsEntity):
    def __init__(self, rect):
        self.outline = Outline(self, "red")
        super().__init__("one_beta", rect, invert_x=True)
        self.ai = WanderAI(self, move_speed=3.2, min_change_timer=.5, max_change_timer=1.2)

        self.flip_offset = {
            False: pg.Vector2(-12, -5),
            True: pg.Vector2(-12, -5)
        }

    def control_animation(self):
        if self.ai.direction == 0:
            self.set_action("idle")
        else:
            self.set_action("run")
        
    def destroy(self):
        super().destroy()
        self.outline.destroy()

    def on_update(self):
        super().on_update()
        self.ai.on_update()
        self.control_animation()

        self.velocity.x = self.ai.direction.x * self.ai.move_speed * 100

        pc = self.app.scene.pc
        if self.rect.colliderect(pc.rect):
            PlayerStatus.singleton.health -= ATTACK_DMGS[self.name]

class TwoAlpha(PhysicsEntity):
    def __init__(self, rect):
        super().__init__("two_alpha", rect, invert_x=True)

class TwoBeta(PhysicsEntity):
    def __init__(self, rect):
        super().__init__("two_beta", rect, invert_x=True)

class ChaseEnemy(Entity):
    def __init__(self, name: str, rect: pg.Rect, follow_speed: float, max_follow_dist: float, damage : int, max_attack_time: float = 1):
        super().__init__(name, rect, start_action="run", invert_x=True)

        self.ai = ChaseAI(self, follow_speed, max_follow_dist)

        self.max_attack_time = max_attack_time
        self.current_attack_time = 0

        self.is_attacking = False

        self.attack_damage = damage

    def attack(self):
        if self.is_attacking:
            return
        self.is_attacking = True
        self.current_attack_time = self.max_attack_time
        self.set_action("attack")

        PlayerStatus.singleton.health -= self.attack_damage

    def update_attack(self):
        if self.current_attack_time > 0:
            self.current_attack_time -= self.app.dt
            self.ai.can_follow = False
        else:
            self.is_attacking = False
            self.ai.can_follow = True
            self.set_action("run")

    def on_update(self):
        super().on_update()
        pc = self.app.scene.pc

        if self.rect.colliderect(pc.rect):
            self.attack()

        self.update_attack()

        self.ai.on_update()

class ThreeAlpha(ChaseEnemy):
    def __init__(self, rect):
        super().__init__("three_alpha", rect, 200, 400, ATTACK_DMGS["three_alpha"], 1.2)

class ThreeBeta(ChaseEnemy):
    def __init__(self, rect):
        super().__init__("three_beta", rect, 300, 700, ATTACK_DMGS["three_beta"], .8)

    def attack(self):
        super().attack()
        pc = self.app.scene.pc
        pc_position = pg.Vector2(pc.rect.center)
        pc_position += pg.Vector2(random.randint(-400, 400), random.randint(-400, 0))
        self.rect.center = pc_position

class FourAlpha(PhysicsEntity):
    def __init__(self, rect):
        self.outline = Outline(self, "red")
        super().__init__("four_alpha", rect, invert_x=True)

        self.normal_speed = 1.5
        self.crazy_speed = 5

        self.crazy_distance = 400

        self.ai = WanderAI(self, move_speed=self.normal_speed)

        self.flip_offset = {
            False: pg.Vector2(-20, -20),
            True: pg.Vector2(-20, -20)
        }

    def destroy(self):
        super().destroy()
        self.outline.destroy()

    def control_animation(self):
        if self.ai.direction.x == 0:
            self.set_action("idle")
        else:
            self.set_action("run")

    def on_update(self):
        pc = self.app.scene.pc

        entity_center = pg.Vector2(self.rect.center)
        player_center = pg.Vector2(pc.rect.center)
        current_distance = entity_center.distance_to(player_center)

        if current_distance >= self.crazy_distance:
            self.ai.move_speed = self.normal_speed
        else:
            self.ai.move_speed = self.crazy_speed

        self.ai.on_update()
        super().on_update()
        self.control_animation()

class FourBeta(PhysicsEntity):
    def __init__(self, rect):
        self.outline = Outline(self, "red")
        super().__init__("four_beta", rect, invert_x=True)

        self.ai = WanderAI(self, move_speed=6, min_change_timer=.1, max_change_timer=.5)

        self.flip_offset = {
            False: pg.Vector2(-20, -20),
            True: pg.Vector2(-20, -20)
        }

    def destroy(self):
        super().destroy()
        self.outline.destroy()

    def control_animation(self):
        if self.ai.direction.x == 0:
            self.set_action("idle")
        else:
            self.set_action("run")

    def on_update(self):
        self.ai.on_update()
        super().on_update()
        self.control_animation()

class FiveOmega(PhysicsEntity):
    def __init__(self, rect):
        super().__init__("five_omega", rect, invert_x=True)