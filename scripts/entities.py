import pygame, math, random

from .objects import GameObject

class PhsyicsEntity:
    def __init__(self, game, entity_type, pos, size):
        self.anim_offset = [0,0]
        self.game = game
        self.type = entity_type
        self.pos = list(pos)
        self.size = size
        self.mask_color = (0,0,0,0)

        self.velocity = [0, 0]
        self.collisions = {'up' : False, 'down' : False, 
                           'right' : False, 'left' : False}

        self.action = ''
        self.flipx = False
        self.flipy = False
        self.set_action('idle')

        self.last_movement = [0, 0]
        self.hit_box = pygame.surface.Surface((self.size[0], self.size[1]))
        self.hit_box.fill('red')

    def rect(self):
        return pygame.rect.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def update(self, tilemap, movement = [0, 0]):
        #콜리션 초기화
        self.collisions = {'up' : False,
                            'down' : False,
                              'right' : False,
                                'left' : False}

        #엔티티 이동
        frame_movement = (movement[0] + self.velocity[0],
                           movement[1] + self.velocity[1])
        
        #x축 이동/접촉
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                #x축 오른쪽으로 이동 블록
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                #x축 왼쪽으로 이동 블록
                if frame_movement[0] < 0:
                   entity_rect.left = rect.right
                   self.collisions['left'] = True
                self.pos[0] = entity_rect.x
    
        #y축 이동/접촉
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                #y축 발 - 블럭 위
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                #y축 머리 - 블럭 바닥
                if frame_movement[1] < 0:
                   entity_rect.top = rect.bottom
                   self.collisions['up'] = True
                self.pos[1] = entity_rect.y
        
        #캐릭터 왼/오른쪽 보고있는지 0일때는 해당안됨
        if movement[0] > 0:
            #오른쪽 보고있음
            self.flipx = False
        if movement[0] < 0:
            #왼쪽 보고있음
            self.flipx = True

        self.last_movement = movement

        #중력 (속도가 5 안넘어감)
        if not self.type == 'player':
            self.velocity[1] = min(5, self.velocity[1] + 0.1)
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

    def render(self, surface, offset):
        surface.blit(pygame.transform.flip(self.animation.img(), self.flipx, self.flipy), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
        self.mask = pygame.mask.from_surface(self.animation.img())
        self.mask_img = self.mask.to_surface(setcolor=self.mask_color, unsetcolor=(0,0,0,0))
        surface.blit(pygame.transform.flip(self.mask_img, self.flipx, self.flipy), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
        

class Enemy(PhsyicsEntity):
    def __init__(self, game, damage, element, name ,pos, size, health, speed, money, animoffset = [0, 0]):
        super().__init__(game, name, pos, size)
        self.anim_offset = animoffset
        self.normal_speed = speed
        self.speed = self.normal_speed
        self.max_health = health
        self.health = self.max_health
        self.name = name

        self.walking = 0
        self.projectile_damage = damage
        self.status = ''
        self.can_damage = 0
        self.element = element
        self.time = 0

        self.money = money
        #마스크
        self.display_mask = pygame.mask.from_surface(self.animation.img())
        #4번째는 alpha임
        self.display_silluate = self.display_mask.to_surface(setcolor=(50,50,255,205), unsetcolor=(0,0,0,0))

    def update(self, tilemap, movement=(0, 0)):
        if self.status == '':
            self.mask_color = (0,0,0,0)
        elif self.status == 'bullet':
            self.time = empty['time']
            self.status = 'emptying'
        elif self.status == 'fire':
            self.time = ruby['time']
            self.status = 'fireing'
        elif self.status == 'ice':
            self.time = sapphire['time']
            self.status = 'iceing'
        elif self.status == 'light':
            self.status = 'lighting'
            self.time = topaz['slow_time']

        #플레이어와 충돌시 대미지 줌 (조건에 따라줌)
        if self.game.player.rect().colliderect(self.rect()) and self.status == '' and not self.can_damage and not self.game.player.invincible_time and abs(self.game.player.dashing) < 50:
            self.game.player.take_damage(self.projectile_damage)
        
        if self.walking:
            if tilemap.solid_tile_check((self.rect().centerx + (-7 if self.flipx else 7), self.pos[1] + 23)):
                if (self.collisions['right'] or self.collisions['left']):
                    #벽에 닿았다면(가깝다면) 방향 전환
                    self.flipx = not self.flipx
                else:
                    #일반적인 움직임
                    movement = (movement[0] - self.speed if self.flipx else self.speed, movement[1])
            else:
                #앞 타일이 없을 시 방향 전환
                self.flipx = not self.flipx
            
            #걷는 양 줄이기
            self.walking = max(0, self.walking - 1)
            
            #탄환발사 기회는 이동이 멈춘 즉시에만 허용
            if not self.walking:
                # dis = 플레이어와 enemy와 의 거리(distance)
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if abs((dis[1]) < 16) and abs(dis[0]) < 250:
                    #enemy가 왼쪽을 보고 있고 enemy 왼쪽에 플레이어가 있다면
                    if (self.flipx and dis[0] < 0):
                        #탄환을 쏜다
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0, self.type])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0],
                                                           random.random() - 0.5 + math.pi, 2 + random.random(),
                                                             (255,255,255)))
                    #enemy가 오른쪽을 보고 있고 enemy 오른쪽에 플레이어가 있다면
                    if (not self.flipx and dis[0] > 0):
                        #탄환을 쏜다
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], +1.5, 0, self.type])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0],
                                                           random.random() - 0.5, 2 + random.random(),
                                                             (255,255,255)))
        
        elif random.random() < 0.02 and not self.status == 'iceing':
            #걸을지 안걸을지 랜덤으로 선택
            self.walking = random.randint(20, 100)

        super().update(tilemap, movement = movement)

        if movement[0] != 0:
            #움직일시
            self.set_action('run')
        else:
            #가만히 있을시(movement[0] == 0)
            self.set_action('idle')

        if abs(self.game.player.dashing) >= 50:
            #플레이어가 대쉬를 하고 있을때
            if self.rect().colliderect(self.game.player.rect()):
                #max 앞에 있는게 조절함 max 함수로 인해 점점 강도가 약해짐
                self.game.screenshake = max(30, self.game.screenshake)
                self.game.sfx['attack'].play()
                #플레이어와 Enemy(self)가 닿았을때
                self.game.player.invincible_time = 20
                for i in range(10):
                    #파티클
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random(), (255,255,255)))
                    self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                         velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                    math.sin(angle + math.pi) * speed * 0.5],
                                                                      frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random(), (255,255,255)))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random(), (255,255,255)))  
            
        if self.game.player.melee_attack:
            #플레이어가 근접공격를 하고 있을때
            if self.rect().colliderect(self.game.player.rect()):
                self.flipx = True
                if not self.status == '':
                    self.can_damage = 70
                elif not self.status == 'emptying':
                    self.can_damage = 50
                self.status = ''
                #max 앞에 있는게 조절함 max 함수로 인해 점점 강도가 약해짐
                self.game.screenshake = max(30, self.game.screenshake)
                self.game.sfx['hit'].play()
                #플레이어와 Enemy(self)가 닿았을때
                for i in range(60):
                    #파티클
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random(), (255,255,255)))
                    self.game.particles.append(Particle(self.game, 'attack', self.rect().center,
                                                         velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                    math.sin(angle + math.pi) * speed * 0.5],
                                                                      frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random(), (255,255,255)))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random(), (255,255,255)))
                #대미지 처리 
                self.health -= self.game.player.cape_attack_damage


        if not self.status == '':
            self.time -= 1
            self.speed = self.normal_speed
        if self.time <= 0 and not self.status == '':
            self.status = ''
        if self.can_damage:
            self.can_damage -= 1
        if self.can_damage <= 0:
            self.mask_color = (0,0,0,0)
        elif self.can_damage > 0:
            self.mask_color = (0,0,0,self.wave_value())

        #특수 마법 처리
        #화염
        if self.status == 'fireing':
            self.speed += 0.3
            self.mask_color = (255, 100, 100, 100)
            if self.time % ruby['attack_time'] == 0:
                self.health -= ruby['damage']
                self.game.sfx['fire_magic'].set_volume(0.07)
                self.game.sfx['fire_magic'].play()
        #빛
        elif self.status == 'lighting' and self.time:
            self.mask_color = (255, 255, 10, 150)
            self.speed = topaz['slow']
        #얼음
        elif self.status == 'iceing':
            self.mask_color = (100, 100,255, 100)
            self.walking = 0
        elif self.status == 'emptying':
            self.mask_color = (255,255,255, 100)
        #얼려있지 않을때 애니메이션 업데이트
        if not self.status == 'iceing':
            self.animation.update()
    
    def kill_enemy(self):
        if self.health <= 0:
            for i in range(30):
                #파티클
                angle = random.random() * math.pi * 2
                speed = random.random() * 5
                self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random(), (197, 66, 69)))
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                     velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                math.sin(angle + math.pi) * speed * 0.5],
                                                       frame=random.randint(0, 7)))
            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random(), (197, 66, 69)))
            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random(), (235, 66, 69)))
            self.game.player.inventory['countable']['코인'] += self.money
            return True

    def wave_value(self):
        value = math.sin(pygame.time.get_ticks())
        if value >= 0: return 255
        else: return 0            
    
    def render(self, surface, offset=(0,0)):
        super().render(surface, offset=offset)

class Boss(PhsyicsEntity):
    def __init__(self, game, damage, element, name ,pos, size, health, speed):
        super().__init__(game, name, pos, size)
        self.name = name
        self.status = ''
        self.anim_offset = [-3, -3]
        #속도
        self.speed = speed#(보통 0.5)
        self.normal_speed = speed
        #체력과 대미지
        self.max_health = health
        self.health = self.max_health
        self.projectile_damage = damage
        #걷기 타이머
        self.walking = 0
        #대미지 입힐 시간 타이머
        self.can_damage = 0
        #속성
        self.element = element
        #이상 타이머
        self.time = 0
        #대쉬 공격 패턴 타이머
        self.dashing = 0
        #보호막
        self.shield = True
        self.max_shield_health = 100
        self.shield_health = 100
        
        #마스크
        self.display_mask = pygame.mask.from_surface(self.animation.img())
        self.display_silluate = self.display_mask.to_surface(setcolor=(50,50,255,205), unsetcolor=(0,0,0,0))

    def update(self, tilemap, movement=(0, 0)):
        #캐릭터 위치(실질적인 rect와는 상관 ㄴ)
        if self.flipx:
            self.anim_offset[0] = -10
        else:
            self.anim_offset[0] = -3

        if not self.can_damage and not self.shield:
            self.shield = True
            self.shield_health = 100
        if self.shield_health > 100:
            self.shield_health = self.max_shield_health

        if self.status == '':
            self.mask_color = (0,0,0,0)
        elif self.status == 'light':
            self.status = 'lighting'

        #플레이어와 충돌시 대미지 줌 (조건에 따라줌)
        if self.game.player.rect().colliderect(self.rect()) and self.status == '' and not self.can_damage and not self.game.player.invincible_time and abs(self.game.player.dashing) < 50:
            self.game.player.take_damage(self.projectile_damage)

        if self.walking:
            if tilemap.solid_tile_check((self.rect().centerx + (-7 if self.flipx else 7), self.pos[1] + 23)):
                if (self.collisions['right'] or self.collisions['left']):
                    #벽에 닿았다면 방향 전환
                    self.flipx = not self.flipx
                else:
                    movement = (movement[0] - self.speed if self.flipx else self.speed, movement[1])
            else:
                #앞 타일이 없을 시 방향 전환
                self.flipx = not self.flipx

            self.walking = max(0, self.walking - 1)
            if not self.walking:
                # dis = 플레이어와 enemy와 의 거리(distance)
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                #탄
                if abs((dis[1]) < 16) and random.random() < 0.4 and self.shield:
                    #enemy가 왼쪽을 보고 있고 enemy 왼쪽에 플레이어가 있다면
                    if (self.flipx and dis[0] < 0) and not self.game.slashes:
                        #탄환을 쏜다
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0, self.type])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random(), (255,255,255)))
                    #enemy가 오른쪽을 보고 있고 enemy 오른쪽에 플레이어가 있다면
                    if (not self.flipx and dis[0] > 0) and not self.game.slashes:
                        #탄환을 쏜다
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], +1.5, 0, self.type])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random(), (255,255,255)))
                #폭탄
                if abs((dis[1]) < 15) and random.random() < 0.5 and self.shield:
                    if self.health >= 50:
                        for i in range(random.randint(10, 15)):
                            self.bomb()
                    if self.health < 50:
                        for i in range(random.randint(15, 25)):
                            self.bomb()
                #slash
                if abs((dis[1] < 6)) and not self.game.projectiles and random.random() < 0.3 and self.shield:
                    self.game.sfx['slash'].play()
                    self.game.slashes.append([[self.rect().centerx, self.rect().centery], 35, 60, -2, self.type])
                    self.game.slashes.append([[self.rect().centerx, self.rect().centery], 35, 60, +2, self.type])

                #대쉬
                if abs((dis[1]) < 25) and random.random() < 0.7 and self.shield:
                    if (self.flipx and dis[0] < 0):
                        self.dash()
                    if (not self.flipx and dis[0] > 0):
                        self.dash()

        elif random.random() < 0.02:
            #걸을지 안걸을지 랜덤으로 선택
            self.walking = random.randint(30, 110)

        elif random.random() < 0.02:
            #더 많은 방향 전환 (버그를 일으킬수있지만...)
            self.flipx = not self.flipx
            if self.flipx:
                self.anim_offset[0] = -10
            else:
                self.anim_offset[0] = -3

        super().update(tilemap, movement = movement)

        if movement[0] != 0:
            #움직일시
            self.set_action('run')
        else:
            #가만히 있을시(movement[0] == 0)
            self.set_action('idle')

            if abs(self.game.player.dashing) >= 50:
                #플레이어가 대쉬를 하고 있을때
                if self.rect().colliderect(self.game.player.rect()):
                    #max 앞에 있는게 조절함 max 함수로 인해 점점 강도가 약해짐
                    self.game.screenshake = max(30, self.game.screenshake)
                    self.game.sfx['attack'].play()
                    #플레이어와 Enemy(self)가 닿았을때
                    self.game.player.invincible_time = 20
                    for i in range(10):
                        #파티클
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 5
                        self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random(), (255,255,255)))
                        self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                    self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random(), (255,255,255)))
                    self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random(), (255,255,255)))  
            
        if self.game.player.melee_attack:
            #플레이어가 근접공격를 하고 있을때
            if self.rect().colliderect(self.game.player.rect()) and not self.shield:
                self.flipx = not self.flipx
                self.can_damage = 70
                self.status = ''
                #max 앞에 있는게 조절함 max 함수로 인해 점점 강도가 약해짐
                self.game.screenshake = max(30, self.game.screenshake)
                self.game.sfx['hit'].play()
                #플레이어와 Enemy(self)가 닿았을때
                for i in range(60):
                    #파티클
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random(), (255,255,255)))
                    self.game.particles.append(Particle(self.game, 'attack', self.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random(), (255,255,255)))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random(), (255,255,255)))
                #대미지 처리 
                self.health -= self.game.player.cape_attack_damage

        if self.shield_health <= 0 and self.shield:
            self.shield = False
            self.can_damage = random.randint(250, 500)

        
        if not self.status == '':
            self.time -= 1
        else:
            self.speed = self.normal_speed
        if self.time <= 0 and not self.status == '':
            self.status = ''
        if self.can_damage:
            self.can_damage -= 1
        if self.can_damage <= 0:
            self.mask_color = (0,0,0,0)
        elif self.can_damage > 0:
            self.mask_color = (0,0,0,self.wave_value())
        if self.shield:
            self.mask_color = (153, 0, 153, 100)
            
        #빛에만 약화됨
        if self.status == 'lighting' and self.time:
            self.mask_color = (255, 255, 10, 150)
            self.speed = topaz['slow'] / 2

        #대쉬 파티클
        if abs(self.dashing) in {60, 50}:
            #대쉬 파티클 양
            particle_amount = 25
            for i in range(particle_amount):
                #파티클 만들기
                angle = random.random() * math.pi * 2
                speed =  random.random() * 0.5 + 0.5
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))

        #대쉬
        if self.dashing > 0:
            self.dashing = max(0 , self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 60:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            if abs(self.dashing) == 61:
                self.velocity[0] *= 0.1

            pvelocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))

        # 선 방향
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

        self.animation.update()
        return [self.name, self]

    def dash(self):
        #대쉬
        if not self.dashing:
            self.game.sfx['dash'].play()
            if self.flipx:
                self.dashing = -70
            else:
                self.dashing = 70

    
    def bomb(self):
        if self.health >= 50:
            self.game.bombs.append([[self.rect().centerx + random.randint(-70, 70), self.rect().centery + random.randint(-70,70)], 80 ,10, self.type])
        elif self.health < 50:
            self.game.bombs.append([[self.rect().centerx + random.randint(-100, 100), self.rect().centery + random.randint(-100,100)], 80 ,10, self.type])


    def kill_enemy(self):
        if self.health <= 0:
            for i in range(30):
                #파티클
                angle = random.random() * math.pi * 2
                speed = random.random() * 5
                self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random(), (197, 66, 69)))
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random(), (197, 66, 69)))
            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random(), (235, 66, 69)))  
            return True

    def wave_value(self):
        value = math.sin(pygame.time.get_ticks())
        if value >= 0: return 255
        else: return 0            
    
    def render(self, surface, offset=(0,0)):
        super().render(surface, offset=offset)
        if self.shield:
            surface.blit(self.game.make_circle_surf(random.randint(7,14), (75,15,75)), (self.rect().centerx - offset[0] - 7.5,self.rect().centery - offset[1] - 7), special_flags=pygame.BLEND_RGB_ADD)

class Player(PhsyicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos,  size)
        #플레이어 체력
        self.player_health = 100
        self.player_max_health = 100
        self.can_heal = 3
        self.healing = 0
        #플레이어 레벨
        self.player_level = 0
        #무적 시간
        self.invincible_time = 0
        #속도 버프 시간
        self.speed_boost = 0
        #애님 오프셋
        self.anim_offset = [-3, -3]
        #플레이어 인벤토리
        self.inventory = {'uncountable' : ['낡은 스카프'],
                          'plugin' : [], 
                          'countable': {'코인' : 0}}
        
        #플레이어 이동
        self.airtime = 0
        self.wall_slide = False
        self.jumps = 1
        self.grav = True
        #플레이어 대쉬 공격
        self.dashing = 0

        #플레이어 물리 공격
        self.attk_cooltime = 45
        self.attacking = 0
        #최종 공격 판정
        self.melee_attack = False
        self.attk_cooldown = self.attk_cooltime
        
        #플레이어 마법 공격
        self.magic_attk_cooltime = empty['cooltime']
        self.magic_attacking = 0
        #최종 공격 판정
        self.magic_attack = False
        self.magic_attk_cooldown = self.magic_attk_cooltime

        #플레이어 공격 스탯
        self.cape_attack_damage = 40
        #대쉬 공격은 초당 대미지임
        self.dash_attack_damage = 5
        self.magic_attack_damage = empty['damage']

        #초반엔 없음
        self.using_plugin = 'empty'#빛, 얼음, 불, 기본(empty)
        self.light_plg = False

    def take_damage(self, damage):
        self.player_health -= damage
        self.invincible_time = 150
        self.game.sfx['hit'].play()
        self.game.screenshake = max(30, self.game.screenshake)
        for i in range(30):
            #파티클
            angle = random.random() * math.pi * 2
            speed = random.random() * 5
            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random(), (255,255,255)))
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
        self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random(), (255,255,255)))
        self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random(), (255,255,255)))  

    def update(self, tilemap, movement=(0, 0)):
        self.gravity()
        if self.speed_boost:
            self.speed_boost -= 1
            self.game.scroll_speed = max(1, self.game.scroll_speed - 1)
        super().update(tilemap, movement = movement)
        if self.using_plugin == 'light' and not self.light_plg:
            self.game.glow_stack += 10 * topaz['level']
            self.light_plg = True

        #플레이어 무적시간
        if self.invincible_time:
            self.game.scroll_speed = 50
            self.invincible_time = max(0, self.invincible_time - 1)
            self.mask_color = (0,0,0,self.wave_value())
        else:
            self.mask_color = (0,0,0,0)

        #마법 클타임 및 공격력
        if self.using_plugin == 'fire':
            self.magic_attk_cooltime = ruby['cooltime']
            self.magic_attack_damage = ruby['damage']
        elif self.using_plugin == 'ice':
            self.magic_attk_cooltime = sapphire['cooltime']
            self.magic_attack_damage = sapphire['damage']
        elif self.using_plugin == 'light':
            self.magic_attk_cooltime = topaz['cooltime']
            self.magic_attack_damage = topaz['damage']
            self.game.light_plg = True

        #캐릭터 위치(실질적인 rect와는 상관 ㄴ)
        if self.flipx:
            self.anim_offset[0] = -10
        else:
            self.anim_offset[0] = -3

        if not self.wall_slide:
            if not self.attacking and not self.magic_attacking:
                if self.airtime > 4:
                    #점프
                    self.set_action('jump')
                elif movement[0] != 0:
                    #달리기
                    self.set_action('run')
                else:
                    #가만히 있을때
                    self.set_action('idle')

            elif self.attacking:
                #공격
                self.set_action('attack')

            elif self.magic_attacking:
                #마법 공격
                self.set_action('attack')
        
        if self.magic_attack:
            #player 왼쪽을 보고 있다면
            if self.flipx:
                #탄환을 쏜다
                self.game.magic_bullets.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                for i in range(10):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.particles.append(Particle(self.game, 'attack', self.game.magic_bullets[-1][0],
                                                         velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                    math.sin(angle + math.pi) * speed * 0.5],
                                                           frame=random.randint(0, 7)))
                for i in range(4):
                    self.game.sparks.append(Spark(self.game.magic_bullets[-1][0],
                                                   random.random() - 0.5 + math.pi, 2 + random.random(), (255,255,255)))
            #player 오른쪽을 보고 있다면
            if not self.flipx:
                #탄환을 쏜다
                self.game.magic_bullets.append([[self.rect().centerx + 7, self.rect().centery], +1.5, 0])
                for i in range(10):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.particles.append(Particle(self.game, 'attack', self.game.magic_bullets[-1][0],
                                                         velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                           frame=random.randint(0, 7)))
                for i in range(4):
                    self.game.sparks.append(Spark(self.game.magic_bullets[-1][0],
                                                   random.random() - 0.5, 2 + random.random(), (255,255,255)))
            
        #근접 공격=====================
        if self.animation.done:
            self.attacking = 0
            self.melee_attack = False
        
        #마법 공격=====================
        if self.animation.done:
            self.magic_attacking = 0
            self.magic_attack = False

        #플레이어 남은 쿨타임 줄이기
        self.attk_cooldown = max(0, self.attk_cooldown - 1)
        #어택 캔슬

        #플레이어 남은 쿨타임 줄이기
        self.magic_attk_cooldown = max(0, self.magic_attk_cooldown - 1)
        #마법 어택 캔슬

        #최종 공격 캔슬
        self.melee_attack = False
        self.magic_attack = False
        
        self.airtime += 1

        if self.airtime > 180:
            if not self.game.dead:
                self.game.screenshake = max(30, self.game.screenshake)
            self.game.dead += 1

        if self.airtime > 70:
            self.game.scroll_speed = 10
        elif self.airtime > 100:
            self.game.scroll_speed = 20
        
        if self.collisions['down']:
            #에어 타임 초기화
            self.airtime = 0
            self.jumps = 1

        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.airtime > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            #시선 방향
            if self.collisions['right']:
                self.flipx = False
            else:
                self.flipx = True
            self.set_action('wall_slide')

    
        #대쉬 파티클
        if abs(self.dashing) in {60, 50}:
            #대쉬 파티클 양
            particle_amount = 25
            for i in range(particle_amount):
                #파티클 만들기
                angle = random.random() * math.pi * 2
                speed =  random.random() * 0.5 + 0.5
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(Particle(self.game, 'attack', self.rect().center, velocity=pvelocity,
                                                     frame=random.randint(0, 7)))

        #대쉬
        if self.dashing > 0:
            self.game.scroll_speed = 10
            self.dashing = max(0 , self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1

            pvelocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
            self.game.particles.append(Particle(self.game, 'attack', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))
        
        # 선 방향
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

        self.animation.update()
            
        
    def render(self, surface, offset = (0,0)):
        #대쉬 할때 사라짐
        if abs(self.dashing) <= 50:
            super().render(surface, offset=offset)

    def jump(self):
        #벽 점프
        if self.wall_slide:
            if self.flipx and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.airtime = 5
                self.jumps = max(0, self.jumps - 1)
                return True
            elif not self.flipx and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.airtime = 5
                self.jumps = max(0, self.jumps - 1)
                return True
        #일반 점프
        elif self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.airtime = 5
            return True
        
    def dash(self):
        #대쉬
        if not self.dashing:
            self.game.sfx['dash'].play()
            if self.flipx:
                self.dashing = -60
                return False
            else:
                self.dashing = 60
                return True
    
    def attack(self):
        #어택 성공
        if not self.attk_cooldown:
            self.attacking = 1
            self.melee_attack = True
            self.attk_cooldown = self.attk_cooltime
            return True
        
    def magic(self):
        #마법 어택 성공
        if not self.magic_attk_cooldown:
            self.magic_attacking = 1
            self.magic_attack = True
            self.magic_attk_cooldown = self.magic_attk_cooltime
            return True
    
    def wave_value(self):
        value = math.sin(pygame.time.get_ticks())
        if value >= 0: return 255
        else: return 0

    def heal(self):
        if self.can_heal:
            self.player_health = self.player_max_health
            self.can_heal -= 1
            self.healing = 15
            return True
        else:return False

    def gravity(self):

        if self.grav == True and not self.grav == False:
            self.velocity[1] = min(5, self.velocity[1] + 0.1)
            self.flipy = False
        elif self.grav == False:
            self.velocity[1] = max(-5, self.velocity[1] - 0.1)
            self.flipy = True