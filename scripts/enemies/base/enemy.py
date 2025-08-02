import pygame as pg

from scripts.constants import *
from scripts.timer import Timer
from scripts.entities.base import *
from scripts.vfx import Outline, AnimatedParticle

class PhysicsEnemy(PhysicsEntity):
    """
    물리 기반의 적 클래스. 플레이어와 충돌 시 데미지를 입힘.
    
    :param name: 애니메이션 등 리소스를 불러올 이름
    :param rect: 초기 위치와 크기를 지정하는 Pygame Rect
    :param collide_attack_damage: 플레이어와 충돌했을 때 입히는 데미지
    """
    def __init__(self, name: str, rect: pg.Rect, collide_attack_damage: int):
        self.outline = Outline(self, "red")
        super().__init__(name, rect, invert_x=True)

        self.collide_attack_damage = collide_attack_damage

        self.attack_particle_anim = self.app.ASSETS["animations"]["vfxs"]["enemy"]["attack"]
        self.attack_sound = self.app.ASSETS["sounds"]["enemy"]["attack"]

    def destroy(self):
        """적 제거 시 호출. 외곽선도 제거됨."""
        self.outline.destroy()
        super().destroy()

    def handle_collision_attack(self):
        """플레이어와 충돌했을 때 데미지를 입히고 효과를 발생시킴."""
        ps = self.app.scene.player_status
        pc = ps.player_character

        if self.rect.colliderect(pc.rect) and not ps.is_invincible:
            ps.health -= self.collide_attack_damage
            AnimatedParticle(self.attack_particle_anim, pg.Vector2(self.rect.center))
            self.app.sound_manager.play_sfx(self.attack_sound)

    def update(self):
        """기본 업데이트 + 충돌 공격 처리"""
        super().update()
        self.handle_collision_attack()

class ProjectileEnemy(PhysicsEnemy):
    """
    일정 거리 내에 플레이어가 있으면 투사체를 발사하는 적 클래스.
    
    :param fire_range: 플레이어가 이 거리 안에 있으면 발사
    :param fire_cooltime: 발사 쿨타임 (초 단위)
    :param projectile_class: 발사할 투사체 클래스
    """
    def __init__(self, name: str, rect, collide_attack_damage: int, fire_range: float, fire_cooltime: float, projectile_class: type):
        super().__init__(name, rect, collide_attack_damage)

        self.fire_range = fire_range
        self.fire_cooltime = fire_cooltime
        self.current_cooltime_timer = fire_cooltime

        self.projectile_class = projectile_class

    def fire(self):
        """투사체를 발사함."""
        direction = pg.Vector2(1, 0) if self.flip_x else pg.Vector2(-1, 0)
        self.projectile_class(pg.Vector2(self.rect.center), direction)

    def update_fire(self):
        """쿨타임 체크 후 발사 로직 실행"""
        if self.current_cooltime_timer > 0:
            self.current_cooltime_timer -= self.app.dt
            return

        pc = self.app.scene.player_status.player_character
        distance = pg.Vector2(self.rect.center).distance_to(pg.Vector2(pc.rect.center))

        if distance <= self.fire_range:
            self.fire()
            self.current_cooltime_timer = self.fire_cooltime

    def update(self):
        """기본 업데이트 + 발사 쿨타임 관리"""
        super().update()
        self.update_fire()

class GhostEnemy(Entity):
    """
    플레이어와 충돌 시 짧은 시간 동안 공격 애니메이션 재생 + 데미지를 입히는 적.
    
    :param max_attack_time: 공격 애니메이션 유지 시간
    """
    def __init__(self, name: str, rect: pg.Rect, collide_attack_damage: int, max_attack_time: float):
        self.outline = Outline(self, "red")
        super().__init__(name, rect, start_action="run", invert_x=True)

        self.collide_attack_damage = collide_attack_damage
        self.max_attack_time = max_attack_time

        self.is_attacking = False
        self.attack_timer: Timer | None = None

        self.attack_particle_anim = self.app.ASSETS["animations"]["vfxs"]["enemy"]["attack"]
        self.attack_sound = self.app.ASSETS["sounds"]["enemy"]["attack"]

    def destroy(self):
        """유령 제거 시 외곽선도 제거"""
        self.outline.destroy()
        super().destroy()

    def control_animation(self):
        """상태에 따라 애니메이션 결정"""
        self.set_action("attack" if self.is_attacking else "run")

    def trigger_attack(self):
        """공격을 발동함. 쿨타임은 Timer로 관리"""
        if self.is_attacking:
            return

        self.is_attacking = True
        self.attack_timer = Timer(self.max_attack_time, lambda: setattr(self, "is_attacking", False))

        ps = self.app.scene.player_status
        ps.health -= self.collide_attack_damage

        AnimatedParticle(self.attack_particle_anim, pg.Vector2(self.rect.center))
        self.app.sound_manager.play_sfx(self.attack_sound)

    def update(self):
        """기본 업데이트 + 공격 처리"""
        super().update()
        self.control_animation()

        ps = self.app.scene.player_status
        pc = ps.player_character

        if self.rect.colliderect(pc.rect) and not ps.is_invincible:
            self.trigger_attack()