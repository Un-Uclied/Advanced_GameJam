import pygame as pg

from scripts.constants import *
from scripts.core import *
from scripts.vfx import *
from scripts.entities.base import *

PLAYER_HIT_KNOCKBACK = 1000

class EnemyBase:
    '''
    적 기본 행동 담당 클래스임  
    다른 적 클래스에서 상속하거나 믹스인처럼 씀
    '''

    def __init__(self, enemy: Entity):
        '''
        EnemyBase 초기화함  
        :param enemy: 제어할 Entity 인스턴스
        '''
        self.enemy = enemy
        self.attack_particle_anim = enemy.app.ASSETS["animations"]["vfxs"]["enemy"]["attack"]
        self.attack_sound = enemy.app.ASSETS["sounds"]["enemy"]["attack"]

    def do_attack(self, damage: int, pos: pg.Vector2, shake: int = 0):
        '''
        플레이어 공격 수행함  
        - SOUL_EVIL_B 타입이면 데미지 증가시킴  
        - 플레이어 체력 깎음  
        - on_player_hurt 이벤트 발생시킴  
        - 공격 파티클 생성, 사운드 재생  
        - 카메라 흔들림 적용 가능  
        - 플레이어 넉백 먹임  

        :param damage: 줄 데미지
        :param pos: 공격 위치 (파티클/넉백 기준)
        :param shake: 카메라 흔들림 세기 (기본값 0)
        '''
        # 대미지 0 이하면 return
        if damage <= 0:
            return
        
        if self.enemy.status.soul_type == SOUL_EVIL_B:
            damage += ENEMY_EVIL_B_DAMAGE_UP

        ps = self.enemy.app.scene.player_status
        pc = ps.player_character

        ps.health -= damage
        self.enemy.app.scene.event_bus.emit("on_player_hurt", damage)

        AnimatedParticle(self.attack_particle_anim, pos)
        self.enemy.app.sound_manager.play_sfx(self.attack_sound)

        if shake:
            cam = self.enemy.app.scene.camera
            cam.shake_amount += shake

        direction = pg.Vector2(pc.rect.center) - pos
        if direction.length_squared() > 0:
            direction.normalize_ip()
        pc.velocity += direction * PLAYER_HIT_KNOCKBACK

class PhysicsEnemy(PhysicsEntity, EnemyBase):
    '''
    물리 엔티티 + EnemyBase 합친 클래스  
    충돌 판정 있는 적 전용
    '''

    def __init__(self, name: str, rect: pg.Rect, collide_attack_damage: int):
        '''
        PhysicsEnemy 초기화함  
        :param name: 적 이름
        :param rect: 적 위치/크기
        :param collide_attack_damage: 플레이어와 충돌 시 줄 데미지
        '''
        PhysicsEntity.__init__(self, name, rect, invert_x=True)
        EnemyBase.__init__(self, self)

        self.collide_attack_damage = collide_attack_damage

    def update(self):
        '''
        매 프레임 업데이트함  
        플레이어랑 충돌하면 공격함  
        '''
        super().update()
        if not hasattr(self.enemy.app.scene, "player_status") or not hasattr(self.enemy.app.scene.player_status, "player_character"):
            return
    
        ps = self.enemy.app.scene.player_status
        pc = ps.player_character

        if self.rect.colliderect(pc.rect) and not ps.current_invincible_time > 0:
            self.do_attack(self.collide_attack_damage, pg.Vector2(self.rect.center), shake=10)

class ProjectileEnemy(PhysicsEnemy):
    '''
    발사체 쏘는 적 전용 클래스  
    PhysicsEnemy 상속받음
    '''

    def __init__(self, name: str, rect, collide_attack_damage: int, fire_range: float, fire_cooltime: float, projectile_class: type):
        '''
        ProjectileEnemy 초기화함  
        :param name: 적 이름
        :param rect: 적 위치/크기
        :param collide_attack_damage: 충돌 시 줄 데미지
        :param fire_range: 발사 사거리
        :param fire_cooltime: 발사 쿨타임(초)
        :param projectile_class: 발사체 클래스
        '''
        super().__init__(name, rect, collide_attack_damage)

        self.fire_range = fire_range
        self.cooldown = Timer(fire_cooltime, None, auto_destroy=False)
        self.projectile_class = projectile_class

    def destroy(self):
        '''
        적 제거 시 발사 쿨다운 타이머도 같이 제거함
        '''
        self.cooldown.destroy()
        super().destroy()

    def fire(self):
        '''
        플레이어 방향으로 발사체 쏨  
        플레이어랑 같은 위치면 발사 안 함  
        방향 맞지 않으면 발사 안 함
        '''
        pc = self.app.scene.player_status.player_character
        plr_dir = pc.get_direction_from(pg.Vector2(self.rect.center))
        
        my_dir = pg.Vector2(1 if not self.anim.flip_x else -1, 0)

        if plr_dir.dot(my_dir) < 0:
            self.projectile_class(pg.Vector2(self.rect.center), plr_dir)

    def fire_attack_update(self):
        '''
        플레이어가 사거리 안에 있고  
        발사 쿨타임 끝났으면 발사 실행
        '''
        pc = self.app.scene.player_status.player_character
        dist = pg.Vector2(self.rect.center).distance_to(pg.Vector2(pc.rect.center))

        if dist <= self.fire_range and self.cooldown.current_time <= 0:
            self.fire()
            self.cooldown.reset()

    def update(self):
        '''
        매 프레임 업데이트 + 발사체 공격 체크함  
        '''
        super().update()
        if not hasattr(self.app.scene, "player_status"):
            return
        self.fire_attack_update()

class GhostEnemy(Entity, EnemyBase):
    '''
    물리 충돌 없는 유령형 적  
    충돌하면 공격만 함
    '''

    def __init__(self, name: str, rect: pg.Rect, collide_attack_damage: int, attack_cool: float):
        '''
        GhostEnemy 초기화함  
        :param name: 적 이름
        :param rect: 적 위치/크기
        :param collide_attack_damage: 충돌 시 줄 데미지
        :param attack_cool: 공격 쿨타임(초)
        '''
        Entity.__init__(self, name, rect, invert_x=True)
        EnemyBase.__init__(self, self)

        self.collide_attack_damage = collide_attack_damage
        self.attack_cool = attack_cool

        self.is_attacking = False
        self.attack_timer = None

    def trigger_attack(self):
        '''
        공격 모션 실행 + 공격 처리  
        이미 공격 중이면 무시함
        '''
        if self.is_attacking:
            return
        self.is_attacking = True
        self.set_action("attack")
        self.do_attack(self.collide_attack_damage, pg.Vector2(self.rect.center), shake=15)

        self.attack_timer = Timer(self.attack_cool, lambda: setattr(self, "is_attacking", False))

    def update(self):
        '''
        매 프레임 업데이트함  
        플레이어 충돌 시 공격 트리거  
        '''
        if not hasattr(self.app.scene, "player_status"):
            return super().update()
        
        ps = self.enemy.app.scene.player_status
        pc = ps.player_character

        if not self.is_attacking:
            if self.rect.colliderect(pc.rect) and not ps.current_invincible_time > 0:
                self.trigger_attack()
            else:
                self.set_action("idle")

        super().update()