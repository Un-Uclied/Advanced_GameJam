import pygame as pg

from scripts.vfx import AnimatedParticle

class EnemyStatus:
    '''
    적 클래스에서 직접 만들어야하고, GameObject를 상속 받지 않기에 app은 self.enemy.app으로 접근 (좀 돌아가서 접근하는 느낌이 있긴하지만)

    :param enemy: 적 인스턴스!!
    :param max_health: 최대 체력 ㅇㅇ
    '''

    def __init__(self, enemy, max_health : int):
        self.enemy = enemy

        self.max_health = max_health
        self._health = self.max_health

        app = self.enemy.app
        self.hurt_sound = app.ASSETS["sounds"]["enemy"]["hurt"]
        self.hurt_particle_anim = app.ASSETS["animations"]["vfxs"]["hurt"]
        
        self.die_sound = app.ASSETS["sounds"]["enemy"]["die"]
        self.die_particle_anim = app.ASSETS["animations"]["vfxs"]["enemy"]["die"]

    @property
    def health(self):
        return self._health
    
    @health.setter
    def health(self, value):

        before_health = self._health
        self._health = max(min(value, self.max_health), 0)

        app = self.enemy.app
        camera = app.scene.camera

        if before_health > self._health:
            #체력이 깎인 만큼 카메라 흔들기
            camera.shake_amount += before_health - self._health  

            #죽을때와 체력이 깎일때 효과음 | 파티클이 다르게끔
            if self._health > 0:
                app.sound_manager.play_sfx(self.hurt_sound)
                AnimatedParticle(self.hurt_particle_anim, pg.Vector2(self.enemy.rect.center))
            else:
                app.sound_manager.play_sfx(self.die_sound)
                AnimatedParticle(self.die_particle_anim, pg.Vector2(self.enemy.rect.center))
        
        #0이 되면 제거
        if self._health <= 0:
            self.enemy.destroy()