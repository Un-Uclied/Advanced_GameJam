import pygame as pg

from scripts.constants import *
from scripts.core import *
from scripts.vfx import *
from scripts.entities.base import *

PLAYER_HIT_KNOCKBACK = 1000

class EnemyBase:
    def __init__(self, enemy: Entity):
        self.enemy = enemy
        self.attack_particle_anim = self.enemy.app.ASSETS["animations"]["vfxs"]["enemy"]["attack"]
        self.attack_sound = self.enemy.app.ASSETS["sounds"]["enemy"]["attack"]

    def do_attack(self, damage: int, pos: pg.Vector2, shake: int = 0):
        # SOUL_EVIL_C가 타입이면 여기서 주는 대미지 더함
        if self.enemy.status.soul_type == SOUL_EVIL_B:
            damage += ENEMY_EVIL_B_DAMAGE_UP

        ps = self.enemy.app.scene.player_status
        pc = ps.player_character
        ps.health -= damage
        AnimatedParticle(self.attack_particle_anim, pos)
        self.enemy.app.sound_manager.play_sfx(self.attack_sound)
        if shake:
            cam = self.app.scene.camera
            cam.shake_amount += shake
        
        direction = pg.Vector2(pc.rect.center) - pos
        if direction.length() > 0:
            direction = direction.normalize()
        pc.velocity += direction * PLAYER_HIT_KNOCKBACK

class PhysicsEnemy(PhysicsEntity, EnemyBase):
    def __init__(self, name: str, rect: pg.Rect, collide_attack_damage: int):
        PhysicsEntity.__init__(self, name, rect, invert_x=True)
        EnemyBase.__init__(self, self)

        self.collide_attack_damage = collide_attack_damage

    def update(self):
        super().update()
        if not hasattr(self.enemy.app.scene, "player_status") or not hasattr(self.enemy.app.scene.player_status, "player_character"):
            return
    
        ps = self.enemy.app.scene.player_status
        pc = ps.player_character

        if self.rect.colliderect(pc.rect) and not ps.is_invincible:
            self.do_attack(self.collide_attack_damage, pg.Vector2(self.rect.center), shake=10)

class ProjectileEnemy(PhysicsEnemy):
    def __init__(self, name: str, rect, collide_attack_damage: int, fire_range: float, fire_cooltime: float, projectile_class: type):
        super().__init__(name, rect, collide_attack_damage)

        self.fire_range = fire_range
        self.cooldown = Timer(fire_cooltime, None, auto_destroy=False)
        self.projectile_class = projectile_class

    def destroy(self):
        # 만든 쿨타임 오브젝트도 지우기
        self.cooldown.destroy()
        super().destroy()

    def fire(self):
        pc = self.app.scene.player_status.player_character
        plr_dir = pg.Vector2(pc.rect.center) - pg.Vector2(self.rect.center)

        if plr_dir.length() == 0:
            return  # 같은 위치면 발사 안함
        else:
            plr_dir = plr_dir.normalize()
        
        my_dir = pg.Vector2(1 if not self.anim.flip_x else -1, 0)

        if plr_dir.dot(my_dir) > 0:
            self.projectile_class(pg.Vector2(self.rect.center), plr_dir)

    def update(self):
        super().update()

        pc = self.app.scene.player_status.player_character
        dist = pg.Vector2(self.rect.center).distance_to(pg.Vector2(pc.rect.center))

        if dist <= self.fire_range and self.cooldown.current_time <= 0:
            self.fire()
            self.cooldown.reset()

class GhostEnemy(Entity, EnemyBase):
    def __init__(self, name: str, rect: pg.Rect, collide_attack_damage: int, attack_cool: float):
        Entity.__init__(self, name, rect, invert_x=True)
        EnemyBase.__init__(self, self)

        self.collide_attack_damage = collide_attack_damage
        self.attack_cool = attack_cool

        self.is_attacking = False
        self.attack_timer = None

    def trigger_attack(self):
        if self.is_attacking:
            return
        self.is_attacking = True
        self.set_action("attack")
        self.do_attack(self.collide_attack_damage, pg.Vector2(self.rect.center), shake=15)

        self.attack_timer = Timer(self.attack_cool, lambda: setattr(self, "is_attacking", False))

    def update(self):
        ps = self.enemy.app.scene.player_status
        pc = ps.player_character

        if not self.is_attacking:
            if self.rect.colliderect(pc.rect) and not ps.is_invincible:
                self.trigger_attack()
            else:
                self.set_action("idle")

        super().update()