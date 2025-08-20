from collections import deque
import pygame as pg

from scripts.utils import GameObject, Timer
from scripts.constants import *
from scripts.vfx import AnimatedParticle
from scripts.ui import PopupText

# 설정 상수들
MAX_HEALTH = 100
HURT_INVINCIBLE_TIME = 1
HEALTH_RESTORE_INTERVAL = 1.0
HEALTH_RESTORE_AMOUNT = 1
ATTACK_COOLTIME = 0.65


class HealthSystem:
    """체력 관리만 전담하는 클래스"""
    
    def __init__(self, initial_health, max_health):
        self.current = initial_health
        self.maximum = max_health
        self.invincible_time = 0.0
    
    def can_take_damage(self):
        """대미지를 받을 수 있는 상태인지"""
        return self.invincible_time <= 0
    
    def take_damage(self, amount):
        """대미지 처리, 성공하면 True 반환"""
        if not self.can_take_damage():
            return False
        
        self.current = max(0, self.current - amount)
        self.invincible_time = HURT_INVINCIBLE_TIME
        return True
    
    def heal(self, amount):
        """회복 처리, 실제로 회복했으면 True 반환"""
        if self.current >= self.maximum:
            return False
        
        prev_health = self.current
        self.current = min(self.maximum, self.current + amount)
        return self.current > prev_health
    
    def set_max_health(self, new_max):
        """최대 체력 변경"""
        self.maximum = new_max
        if self.current > self.maximum:
            self.current = self.maximum
    
    def is_alive(self):
        """생존 여부"""
        return self.current > 0
    
    def update(self, dt):
        """무적 시간 업데이트"""
        if self.invincible_time > 0:
            self.invincible_time -= dt


class SoulManager:
    """영혼 관리만 전담하는 클래스"""
    
    def __init__(self):
        self.souls = deque([SOUL_DEFAULT, SOUL_DEFAULT], maxlen=2)
    
    def has_soul(self, soul_type):
        """특정 영혼을 보유하고 있는지"""
        return soul_type in self.souls
    
    def add_soul(self, soul_type):
        """영혼 추가, 이미 있으면 False 반환"""
        if self.has_soul(soul_type) and soul_type != SOUL_DEFAULT:
            return False
        
        self.souls.append(soul_type)
        return True
    
    def get_max_health_modifier(self):
        """영혼에 따른 최대 체력 보정값"""
        modifier = 0
        if self.has_soul(SOUL_KIND_C):
            modifier -= KIND_C_MAX_HEALTH_DOWN
        if self.has_soul(SOUL_EVIL_B):
            modifier -= EVIL_B_MAX_HEALTH_DOWN
        return modifier
    
    def get_attack_cooltime_modifier(self):
        """영혼에 따른 공격 쿨타임 보정값"""
        modifier = 0
        if self.has_soul(SOUL_EVIL_A):
            modifier += EVIL_A_COOLTIME_UP
        if self.has_soul(SOUL_EVIL_B):
            modifier -= EVIL_B_COOLTIME_DOWN
        return modifier
    
    def get_heal_bonus(self, player_rect, light_manager):
        """영혼에 따른 회복 보너스"""
        if not self.has_soul(SOUL_KIND_A):
            return 0
        
        if light_manager.is_rect_in_light(player_rect):
            return KIND_A_HEALTH_UP
        
        return 0


class PlayerEffects:
    """사운드, 파티클, 카메라 효과 관리"""
    
    def __init__(self, app):
        self.app = app
        self.scene = app.scene
        
        # 애셋 로드
        self.hurt_sound = app.ASSETS["sounds"]["player"]["hurt"]
        self.hurt_particle_anim = app.ASSETS["animations"]["vfxs"]["hurt"]
    
    def play_hurt_effects(self, damage_amount, player_position):
        """피격 효과 재생"""
        # 카메라 흔들림
        if hasattr(self.scene, 'camera'):
            self.scene.camera.shake_amount += damage_amount * 2
        
        # 사운드 재생
        self.app.sound_manager.play_sfx(self.hurt_sound)
        
        # 파티클 생성
        if player_position:
            AnimatedParticle(self.hurt_particle_anim, pg.Vector2(player_position))


class PlayerStatus(GameObject):
    """플레이어 상태 관리 메인 클래스"""
    
    def __init__(self, player_character, start_health):
        super().__init__()
        
        # 시스템들 초기화
        self.health_system = HealthSystem(start_health, MAX_HEALTH)
        self.soul_manager = SoulManager()
        self.effects = PlayerEffects(self.app)
        
        # 공격 쿨타임 타이머
        self.attack_cooltime = Timer(
            time=ATTACK_COOLTIME,
            on_time_out=None,
            auto_destroy=False,
        )
        self.attack_cooltime.active = True
        
        # 체력 회복 타이머
        self.heal_timer = Timer(
            time=HEALTH_RESTORE_INTERVAL,
            on_time_out=self.restore_health,
            auto_destroy=False,
            use_unscaled=False
        )
        self.heal_timer.active = True
        
        self.player_character = player_character
        
        # 이벤트 연결
        self.connect_events()
    
    def connect_events(self):
        """이벤트 버스 연결"""
        event_bus = self.scene.event_bus
        event_bus.connect("on_soul_interact", self.handle_soul_interact)
        event_bus.connect("on_player_damaged", self.handle_damage)
    
    # 편의 속성들 (기존 코드와의 호환성)
    @property
    def health(self):
        return self.health_system.current
    
    @health.setter
    def health(self, value):
        prev_health = self.health_system.current
        
        if value < prev_health:
            # 대미지 처리
            damage = prev_health - value
            if self.health_system.take_damage(damage):
                self.on_health_changed(False)
                self.handle_damage(damage)
        elif value > prev_health:
            # 회복 처리  
            heal_amount = value - prev_health
            if self.health_system.heal(heal_amount):
                self.on_health_changed(True)
        
        # 사망 체크
        if not self.health_system.is_alive():
            self.scene.event_bus.emit("on_player_died")
    
    @property
    def max_health(self):
        return self.health_system.maximum
    
    @max_health.setter
    def max_health(self, value):
        self.health_system.set_max_health(value)
    
    @property
    def current_invincible_time(self):
        return self.health_system.invincible_time
    
    @current_invincible_time.setter
    def current_invincible_time(self, value):
        prev = self.health_system.invincible_time
        self.health_system.invincible_time = max(value, 0)
        
        # 무적 상태 변화 이벤트
        if self.health_system.invincible_time > 0 and prev <= 0:
            self.scene.event_bus.emit("on_player_invincible", True)
        elif self.health_system.invincible_time <= 0 and prev > 0:
            self.scene.event_bus.emit("on_player_invincible", False)
    
    @property
    def soul_queue(self):
        return self.soul_manager.souls
    
    def handle_soul_interact(self, soul_type):
        """영혼 상호작용 처리"""
        if not self.soul_manager.add_soul(soul_type):
            PopupText(f'"{soul_type}는 이미 있다."', pg.Vector2(SCREEN_SIZE.x / 2, 700))
            return
        
        self.update_stats_by_souls()
    
    def update_stats_by_souls(self):
        """영혼에 따른 능력치 업데이트"""
        # 최대 체력 조정
        base_health = MAX_HEALTH
        health_modifier = self.soul_manager.get_max_health_modifier()
        self.health_system.set_max_health(base_health + health_modifier)
        
        # 공격 쿨타임 조정
        base_cooltime = ATTACK_COOLTIME
        cooltime_modifier = self.soul_manager.get_attack_cooltime_modifier()
        self.attack_cooltime.max_time = base_cooltime + cooltime_modifier
        self.attack_cooltime.reset()
        
        # 변경사항 알림
        self.scene.event_bus.emit("on_player_soul_changed")
    
    def handle_damage(self, damage_amount):
        """대미지 처리"""
        player_pos = None
        if self.player_character:
            player_pos = self.player_character.rect.center
        
        self.effects.play_hurt_effects(damage_amount, player_pos)
    
    def restore_health(self):
        """체력 회복 처리"""
        self.heal_timer.reset()
        
        if not (0 < self.health_system.current < self.health_system.maximum):
            return
        
        heal_amount = HEALTH_RESTORE_AMOUNT
        
        # 영혼 보너스 회복량
        if self.player_character:
            bonus = self.soul_manager.get_heal_bonus(
                self.player_character.rect, 
                self.scene.light_manager
            )
            heal_amount += bonus
        
        # 실제 회복 처리
        if self.health_system.heal(heal_amount):
            self.on_health_changed(True)
    
    def on_health_changed(self, is_healing):
        """체력 변화 시 호출"""
        self.scene.event_bus.emit("on_player_health_changed", is_healing)
    
    def update(self):
        """매 프레임 업데이트"""
        super().update()
        self.health_system.update(self.app.dt)