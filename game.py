#[뉴비니까 건들지 마세요]팀
#사용된 외부 라이브러리: pygame, pytweening
#IDLE에서 열어주시기 바랍니다

#임포트
import pygame, random, math, pytweening as pt
from scripts.entities import Player, Enemy, Boss
from scripts.load_image import load_image, load_images, Animation, load_save, reset_key, write_save
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark
from scripts.ui import UI
from scripts.shop_ui import Shop_UI, Smithy_UI
from scripts.interactions import Interaction
from scripts.item_data import sapphire, topaz, ruby
from scripts.story_dialouge import Dialouge, Credits
from scripts.dialouge_data import start_dialouge, end_dialouge, creditdata 
from scripts.control import Control

#게임
class GAME:
    #셋팅들
    def __init__(self):
        pygame.init()
        pygame.display.init()
        #게임 제목
        pygame.display.set_caption('game')
        pygame.display.set_icon(pygame.image.load('data/images/icon.png'))

        #화면|캔버스 조절
        self.screen = pygame.display.set_mode((1280, 960), pygame.FULLSCREEN)
        self.canvas = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.canvas_no_outline = pygame.Surface(self.canvas.get_size())
        self.ui_canvas = pygame.Surface(self.canvas.get_size(), pygame.SRCALPHA)
        self.shop_canvas = pygame.Surface(self.canvas.get_size(), pygame.SRCALPHA)
        self.dark_surface = pygame.Surface(self.canvas.get_size(), pygame.SRCALPHA)

        #스테이트
        self.state = 'intro_menu'

        #타이머
        self.clock = pygame.time.Clock()

        #에셋
        self.assets = {
            #타일
            'decor' : load_images('tiles/decor'),
            'grass' : load_images('tiles/grass'),
            'large_decor' : load_images('tiles/large_decor'),
            'stone' : load_images('tiles/stone'),
            'clouds' : load_images('clouds'),
            'shrine' : load_images('tiles/shrine'),
            'shrine_frag' : load_images('tiles/shrine fragments'),
            'dirt': load_images('tiles/dirt'),
            'boss_tile': load_images('tiles/boss_tile'),
            'building' : load_images('tiles/buildings'),
            'brick' : load_images('tiles/brick'),
            'util' : load_images('tiles/util'),
            'grav' : load_images('tiles/gravity'),
            'ice_grass' : load_images('tiles/ice_grass'),
            'snowy_grass' : load_images('tiles/snowy_grass'),
            'snow' : load_images('tiles/snow'),

            #배경
            'dungeon' : load_image('backgrounds/dungeon.png'),
            'village' : load_image('backgrounds/village.png'),
            
            #엔티티
            'ackgima/idle' : Animation(load_images('entities/ackgima/idle'), img_dur=6),
            'ackgima/run' : Animation(load_images('entities/ackgima/run'), img_dur=4),
            'craper/idle' : Animation(load_images('entities/craper/idle'), img_dur=6),
            'craper/run' : Animation(load_images('entities/craper/run'), img_dur=4),
            'iced_guy/idle' : Animation(load_images('entities/iced_guy/idle'), img_dur=6),
            'iced_guy/run' : Animation(load_images('entities/iced_guy/run'), img_dur=4),
            'player/idle' : Animation(load_images('entities/player/idle'), img_dur=4),
            'player/run' : Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump' : Animation(load_images('entities/player/jump'), img_dur=6),
            'player/attack' : Animation(load_images('entities/player/attack'), img_dur=4, loop=False),
            'player/wall_slide' : Animation(load_images('entities/player/wall_slide')),
            'boss/idle' : Animation(load_images('entities/boss/idle'), img_dur=6),
            'boss/run' : Animation(load_images('entities/boss/run'), img_dur=4),
            
            #파티클
            'particle/leaf' : Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle' : Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'particle/attack' : Animation(load_images('particles/attack'), img_dur=6, loop=False),
            'projectile' : load_image('projectiles/projectile.png'),
            'magic_bullet_light' : load_image('projectiles/magic_light.png'),
            'magic_bullet_fire' : load_image('projectiles/magic_fire.png'),
            'magic_bullet_ice' : load_image('projectiles/magic_ice.png'),
            'lazer' : load_image('projectiles/lazer.png'),
            'bomb' : load_image('projectiles/bomb.png'),
            'bullet' : load_image('projectiles/bullet.png'),
            
            
            #player GUI
            'intro_title' : load_image('ui/intro_name.png'),
            'magic_icon_light' : load_image('ui/magic_icon_light.png'),
            'magic_icon_fire' : load_image('ui/magic_icon_fire.png'),
            'magic_icon_ice' : load_image('ui/magic_icon_ice.png'),
            'magic_icon_none' : load_image('ui/magic_icon_none.png'),
            'dash_icon' : load_image('ui/dash_icon.png'),
            'melee_icon' : load_image('ui/melee_icon.png'),
            'icons_box' : load_image('ui/icon_box.png'),
            'health_bar' : load_image('ui/health_bar.png'),
            'ui_key_bg' : load_image('ui/button.png'),
            'ui_heart' : load_image('ui/heart.png'),
            'boss_bar' : load_image('ui/boss_bar.png'),
            'info_bar' : load_image('ui/info.png'),

            #스타트 UI
            'ui_start' : load_image('ui/start_img.png'),
            'ui_options' : load_image('ui/option_img.png'),
            'ui_credits' : load_image('ui/credits_img.png'),
            'ui_exit' : load_image('ui/exit_img.png'),
            'arrow' : load_image('ui/arrow.png'),

            #상점 UI
            'shop_items' : {0 : load_image('shop/ice.png'),
                            1 : load_image('shop/light.png'),
                            2 : load_image('shop/fire.png'),},
            'shop_ui' : load_image('shop/item_bg.png'),
            'select_ui' : load_image('shop/select_bg.png'),
            'show_item_bg' : load_image('shop/show_item_bg.png'),
            'select_hand' : load_image('shop/hand.png'),
            'money_bar' : load_image('shop/money_bar.png'),
            'shop_bg' : load_image('shop/shop.png'),
            'smithy_bg' : load_image('shop/smithy.png'),
            'heal' : load_image('ui/heal.png'),
            'heal_bg' : load_image('ui/heal_bg.png'),

            #스토리
            'start_scene' : load_images('scenes/start'),
            'end_scene' : load_images('scenes/end'),

            #기타
            'interaction' : load_images('tiles/interaction'),
            'boom' : load_image('projectiles/poof.png'),
            'slash' : load_image('projectiles/slash.png'),

            #아트
            'main_art' : load_image('arts/main_art.png')
        }

        #사운드 에펙트
        self.sfx = {
            'jump' : pygame.mixer.Sound('data/sfx/jump.wav'),
            'hit' : pygame.mixer.Sound('data/sfx/hit.wav'),
            'dash' : pygame.mixer.Sound('data/sfx/dash.wav'),
            'shoot' : pygame.mixer.Sound('data/sfx/shoot.wav'),
            'attack' : pygame.mixer.Sound('data/sfx/attack.wav'),
            'ice_magic' : pygame.mixer.Sound('data/sfx/ice_magic.wav'),
            'fire_magic' : pygame.mixer.Sound('data/sfx/fire_magic.wav'),
            'light_magic' : pygame.mixer.Sound('data/sfx/magic.wav'),
            'buy' : pygame.mixer.Sound('data/sfx/buy.wav'),
            'confirm' : pygame.mixer.Sound('data/sfx/confirm.wav'),
            'confirm_option' : pygame.mixer.Sound('data/sfx/confirm_option.wav'),
            'change' : pygame.mixer.Sound('data/sfx/change.wav'),
            'explosion' : pygame.mixer.Sound('data/sfx/explosion.wav'),
            'slash' : pygame.mixer.Sound('data/sfx/slash.wav'),
            'heal' : pygame.mixer.Sound('data/sfx/heal.wav'),
            'bounce' : pygame.mixer.Sound('data/sfx/mushroom.wav'),
            'key' : pygame.mixer.Sound('data/sfx/key.wav'),

            'main_bgm' : pygame.mixer.Sound('data/sfx/main_bgm.wav'),
            'cave_bgm' : pygame.mixer.Sound('data/sfx/cave_ambience.wav'),
        }

        #폰트
        self.fonts = {
            'key_guide' : pygame.font.Font('data/fonts/PublicPixel-z84yD.ttf', 6),
            'key_guide_big' : pygame.font.Font('data/fonts/PublicPixel-z84yD.ttf', 12),
            'dialouge_font' : pygame.font.Font('data/fonts/Ramche.ttf', 12),
            'dialouge_font_smol' : pygame.font.Font('data/fonts/Ramche.ttf', 11),
            'font_start' : pygame.font.Font('data/fonts/pixelroborobo.otf', 22),
            'font_stop' : pygame.font.Font('data/fonts/pixelroborobo.otf', 15),
        }

        #소리 볼륨 조절
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.3)
        self.sfx['attack'].set_volume(0.3)
        self.sfx['light_magic'].set_volume(0.2)
        self.sfx['fire_magic'].set_volume(0.2)
        self.sfx['ice_magic'].set_volume(0.1)
        self.sfx['buy'].set_volume(0.3)
        self.sfx['change'].set_volume(0.2)
        self.sfx['confirm'].set_volume(0.3)
        self.sfx['explosion'].set_volume(0.02)
        self.sfx['slash'].set_volume(0.2)
        self.sfx['heal'].set_volume(0.2)
        self.sfx['main_bgm'].set_volume(0.22)
        self.sfx['cave_bgm'].set_volume(0.2)

        pygame.mixer.set_num_channels(10)

        #구름
        self.clouds = Clouds(self.assets['clouds'])

        #플레이어 셋팅
        self.movement = [False, False]
        self.player = Player(self, (50, 50), (9, 17))
        self.player_status = 'shrine' #'shrine' 'dungeon' 'shop' 'village' 'smithy' 
        self.player_inventory = []
        self.player_kills = 0
        self.end_cut_scene = False

        #맵 셋팅
        self.tilemap = Tilemap(self, tile_size=16)
        self.level = 0

        #user interface
        self.ui = UI(self)
        self.shop_ui = Shop_UI(self)
        self.smithy_ui = Smithy_UI(self)

        self.load_level('shrine')

        #intro vars
        self.clicking = False
        self.trigger = False
        self.glow = False   
        
        #스피드런
        self.clock_time = {'h' : 0, 'm' : 0, 's' : 0, 'ms' : 0}

        #플레이어 세이브 파일
        self.player_save = load_save()
        self.control_handler = Control(self.player_save, self)

        pygame.mouse.set_visible(0)
        
    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        #플레이어/적 스포너
        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1),
                                             ('spawners', 2), ('spawners', 3), ('spawners', 4)], keep=True):
            #0 == 플레이어는 특별하기에 __init__에서 이미 스폰 완료
            if spawner['variant'] == 0 :
                self.player.pos = spawner['pos']
                self.player.airtime = 0
            elif spawner['variant'] == 1:
                #게임, '이름', 스폰 위치, (히트박스 rect)('20 넘어가면 안됨!'), 체력, 속도, anim_offset
                self.enemies.append( Enemy(self, 10, 'fire', 'craper', spawner['pos'], (16, 16), 100, 0.7, 10, [1, -1]))
            elif spawner['variant'] == 2:
                #게임, '이름', 스폰 위치, (히트박스 rect)('20 넘어가면 안됨!'), 체력, 속도, anim_offset
                self.enemies.append( Enemy(self, 25, 'dark', 'ackgima', spawner['pos'], (20, 17), 200, 0.7 , 18, [-5, -8]))
            elif spawner['variant'] == 3:
                #게임, '이름', 스폰 위치, (히트박스 rect)('20 넘어가면 안됨!'), 체력, 속도, anim_offset
                self.enemies.append( Enemy(self, 20, 'ice', 'iced_guy', spawner['pos'], (16, 16), 150, 0.5, 10, [0, 0]))
            #보스
            elif spawner['variant'] == 4:
                #게임, '이름', 스폰 위치, (히트박스 rect)('20 넘어가면 안됨!'), 체력, 속도, anim_offset
                self.enemies.append(Boss(self, 35, 'dark', 'boss', spawner['pos'], (9, 17), 1500, 0.7) )
        #체력이 가장많은 순으로 정렬(보스 객체 구하기 위함)
        self.enemies.sort(key= lambda x: x.max_health)
        
        #나무 파티클 스포너
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
        
        #인터랙션 스포너
        self.interactions = []
        for inter in self.tilemap.extract([('interaction', 0),
                                           ('interaction', 1),
                                           ('interaction', 2),
                                           ('interaction', 3),], keep=True):
            if inter['variant'] == 0:
                self.interactions.append(Interaction(pygame.Rect(inter['pos'][0], inter['pos'][1], self.tilemap.tile_size, self.tilemap.tile_size), 'start_dungeon', self, 'press_space'))
            if inter['variant'] == 1:
                self.interactions.append(Interaction(pygame.Rect(inter['pos'][0], inter['pos'][1], self.tilemap.tile_size, self.tilemap.tile_size), 'exit_dungeon', self, 'press_space'))
            if inter['variant'] == 2:
                self.interactions.append(Interaction(pygame.Rect(inter['pos'][0], inter['pos'][1], self.tilemap.tile_size, self.tilemap.tile_size), 'start_shop', self, 'press_space'))
            if inter['variant'] == 3:
                self.interactions.append(Interaction(pygame.Rect(inter['pos'][0], inter['pos'][1], self.tilemap.tile_size, self.tilemap.tile_size), 'start_enforce', self, 'press_space'))
        
        #유틸 타일
        self.util_tiles = []
        for util in self.tilemap.extract([('util', 0), ('util', 1)], keep=True):
            if util['variant'] == 0:
                self.util_tiles.append(Interaction(pygame.Rect(util['pos'][0], util['pos'][1] - 2, self.tilemap.tile_size, self.tilemap.tile_size), 'bounce', self, 'none'))

            if util['variant'] == 1:
                self.util_tiles.append(Interaction(pygame.Rect(util['pos'][0], util['pos'][1] - 2, self.tilemap.tile_size, self.tilemap.tile_size), 'speed', self, 'none'))


        #탄환|플레이어 마법|파티클|스파크|폭탄|검|엔티티
        self.projectiles = []
        self.magic_bullets = []
        self.particles = []
        self.sparks = []
        self.bombs = []
        self.slashes = []

        #맵 스크롤
        self.scroll = [0, 0]
        self.scroll_speed = 25
        #플레이어 쥬금
        self.dead = 0
        self.player.can_heal = 3
        self.player.player_health = self.player.player_max_health
        #플레이어 킬 스탯
        self.player_killing = False
        #화면 흔들림
        self.screenshake = 0
        #화면 전환
        self.transition = -30
        self.change = False

        self.glow_stack = 110#작을수록 원이 작아짐
        self.player.light_plg = False
        
    def intro_menu(self):
        running = True
        selection = 0
        confirm = False

        bg = self.assets['main_art']
        bg.set_alpha(120)
        changing = 0 
        ofs = 70

        bob_range = 60
        bob_speed = 0.8
        bob_step = 0
        bob_dir = 1
        #0 == self.game, 1 == self.option, 2 == self.exit, 3 == self.credits
        while running:

            surface = pygame.Surface(self.canvas.get_size(), pygame.SRCALPHA)
            surface2 = pygame.Surface(self.canvas.get_size(), pygame.SRCALPHA)
            bg_surf = pygame.Surface(self.canvas.get_size(), pygame.SRCALPHA)
            #canvas_no_outline에 그리면 안됨!!
            self.screen.fill('black')
            
            bg_surf.blit(bg, (0, 0))

            btt_0 = self.assets['ui_start']
            btt_1 = self.assets['ui_options']
            btt_2 = self.assets['ui_exit']
            btt_3 = self.assets['ui_credits']
            
            #메뉴 선택
            if confirm:
                if selection == 0:
                    self.start_dialouge()
                    return
                elif selection == 1:
                    self.options()
                elif selection == 2:
                    pygame.quit()
                    exit()
                    return
                elif selection == 3:
                    self.credits()
                    
                else:
                    pass
            else:
                #발적화 ㅋㅋ
                if selection == 0:
                    select_txt = self.fonts['font_start'].render('게임 시작[{}]'.format(pygame.key.name(self.control_handler.controls['MELEE'])), False, 'black')
                    btt_0.set_alpha(255)
                    btt_1.set_alpha(150)
                    btt_2.set_alpha(150)
                    btt_3.set_alpha(150)
                elif selection == 1:
                    select_txt = self.fonts['font_start'].render('설정[{}]'.format(pygame.key.name(self.control_handler.controls['MELEE'])), False, 'black')
                    btt_1.set_alpha(255)
                    btt_0.set_alpha(150)
                    btt_2.set_alpha(150)
                    btt_3.set_alpha(150)
                elif selection == 2:
                    select_txt = self.fonts['font_start'].render('나가기[{}]'.format(pygame.key.name(self.control_handler.controls['MELEE'])), False, 'black')
                    btt_2.set_alpha(255)
                    btt_0.set_alpha(150)
                    btt_1.set_alpha(150)
                    btt_3.set_alpha(150)
                elif selection == 3:
                    select_txt = self.fonts['font_start'].render('크레딧[{}]'.format(pygame.key.name(self.control_handler.controls['MELEE'])), False, 'black')
                    btt_3.set_alpha(255)
                    btt_0.set_alpha(150)
                    btt_1.set_alpha(150)
                    btt_2.set_alpha(150)
                else:
                    print("ERROR:unselected!!")

            if changing > 0:
                ofs -= 2
                changing -=1
            if changing < 0:
                ofs += 2
                changing += 1


            bob_offs = bob_range * (pt.easeInOutSine(bob_step / bob_range) - 0.5)
            surface.blit(pygame.transform.scale(self.assets['intro_title'], (150, 76)), (self.canvas.get_width() // 2 - self.assets['intro_title'].get_width(), (self.canvas.get_height() // 2 - self.assets['intro_title'].get_height() + (bob_offs/8) * bob_dir) / 2))
            surface2.blit(btt_0, (20, 150 + (bob_offs / 6.5) * bob_dir))
            surface2.blit(btt_1, (100,150 + (bob_offs / 6.5) * bob_dir))
            surface2.blit(btt_2, (180,150 + (bob_offs / 6.5) * bob_dir))
            surface2.blit(btt_3, (260,150 + (bob_offs / 6.5) * bob_dir))
            bob_step += bob_speed
            if bob_step > bob_range:
                bob_step = 0
                bob_dir *= -1
            self.canvas_no_outline.blit(bg_surf, (0,0))
            
            display_mask2 = pygame.mask.from_surface(surface2)
            display_silluate2 = display_mask2.to_surface(setcolor=(0,0,0,180), unsetcolor=(0,0,0,0))
            for offset in [[-2, 0], [2, 0], [0, -2], [0, 2]]:
                self.canvas_no_outline.blit(display_silluate2, (offset[0] + ofs, offset[1]))
            
            display_mask = pygame.mask.from_surface(surface)
            display_silluate = display_mask.to_surface(setcolor=(0,0,60,180), unsetcolor=(0,0,0,0))
            for offset in [[-3, 0], [3, 0], [0, -3], [0, 3]]:
                self.canvas_no_outline.blit(display_silluate, (offset[0], offset[1]))
            self.canvas_no_outline.blit(surface, (0,0))
            self.canvas_no_outline.blit(surface2, (ofs,0))
            self.canvas_no_outline.blit(self.assets['arrow'], (35,150))
            pygame.draw.circle(self.canvas_no_outline, 'darkgrey', (0,165), 50)
            self.canvas_no_outline.blit(self.fonts['dialouge_font_smol'].render(pygame.key.name(self.control_handler.controls['LEFT']).capitalize() +'<-', False, 'black'), (0, 149))
            self.canvas_no_outline.blit(self.fonts['dialouge_font_smol'].render(pygame.key.name(self.control_handler.controls['RIGHT']).capitalize() + '->', False, 'black'), (0, 162))
            pygame.draw.polygon(self.canvas_no_outline, 'darkgrey', [(245, 205), (225, 240)], 220)
            self.canvas_no_outline.blit(select_txt, (140,215))
            #screenshake(캔버스 흔들기)
            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            #캔버스 화면에 그리기
            self.screen.blit(pygame.transform.scale(self.canvas_no_outline, self.screen.get_size()), screenshake_offset)
            mp = pygame.mouse.get_pos()
            mp = (mp[0] - 40, mp[1] - 40)
            self.screen.blit(self.make_circle_surf(50, (45,15,15)), mp, special_flags=pygame.BLEND_RGBA_ADD)
            
            #이벤트 루프
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                    return
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == self.control_handler.controls['MELEE']:
                        confirm = True
                        self.sfx['confirm'].play()

                    if event.key == self.control_handler.controls['RIGHT'] and not changing:
                        if not selection > 2:
                            selection += 1
                            changing = 40
                            self.sfx['change'].play()
                    if event.key == self.control_handler.controls['LEFT'] and not changing:
                        if not selection < 1:
                            selection -= 1
                            changing = -40
                            self.sfx['change'].play()

                if event.type == pygame.KEYUP:
                    if event.key == self.control_handler.controls['MELEE']:
                        confirm = False
            
            #업데이트
            pygame.display.update()
            self.clock.tick(60)
    
    def options(self):
        running = True
        bg = self.assets['main_art']
        bg.set_alpha(100)
        key_action = {"LEFT" : False,
                "RIGHT" : False,
                "UP/JUMP" : False,
                "DOWN" : False,
                "MAGIC" : False,
                "DASH" : False,
                "MELEE" : False,
                "HEAL" : False,
                "ACTION1" : False,
                "ACTION2" : False,}
        while running:
            self.canvas_no_outline.fill('black')
            #아웃 라인
            display_mask = pygame.mask.from_surface(self.canvas)
            display_silluate = display_mask.to_surface(setcolor=(0,0,0,180), unsetcolor=(0,0,0,0))
            #[(-1, 0), (1, 0), (0, -1), (0, 1)] = 좌 우 위 아래 한칸씩
            for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                #canvas에 그리면 아웃라인이 생기고, canvas_no_outline에그리면 아웃 라인이 안그려짐(대충 그럼)
                #사실은 self.canvas_no_outline에다 self.canvas의'만'실루엣을 그리는건데
                #게임은 canvas_no_outline 의 실루엣을 안땀
                self.canvas_no_outline.blit(display_silluate, offset)
            self.canvas_no_outline.blit(bg, (0,0))

            self.control_handler.render(self.canvas_no_outline)
            self.canvas_no_outline.blit(self.canvas, (0,0))
            

            #이벤트 루프
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        write_save(self.control_handler.save_file)
                        self.intro_menu()

                    if event.key == self.control_handler.controls['LEFT']:
                        key_action['LEFT'] = True
                        self.sfx['change'].play()
                    if event.key == self.control_handler.controls['UP/JUMP']:
                        key_action['UP/JUMP'] = True
                        self.sfx['change'].play()
                    if event.key == self.control_handler.controls['RIGHT']:
                        key_action['RIGHT'] = True
                        self.sfx['change'].play()
                    if event.key == self.control_handler.controls['DOWN']:
                        key_action['DOWN'] = True
                        self.sfx['change'].play()
                    if event.key == self.control_handler.controls['MAGIC']:
                        key_action['MAGIC'] = True
                    if event.key == self.control_handler.controls['DASH']:
                        key_action['DASH'] = True
                    if event.key == self.control_handler.controls['MELEE']:
                        key_action['MELEE'] = True
                    if event.key == self.control_handler.controls['HEAL']:
                        key_action['HEAL'] = True
                    if event.key == self.control_handler.controls['ACTION1']:
                        key_action['ACTION1'] = True
                        self.sfx['confirm'].play()
                    if event.key == self.control_handler.controls['ACTION2']:
                        key_action['ACTION2'] = True
                        self.sfx['confirm'].play()


                if event.type == pygame.KEYUP:
                    if event.key == self.control_handler.controls['LEFT']:
                        key_action['LEFT'] = False
                    if event.key == self.control_handler.controls['UP/JUMP']:
                        key_action['UP/JUMP'] = False
                    if event.key == self.control_handler.controls['RIGHT']:
                        key_action['RIGHT'] = False
                    if event.key == self.control_handler.controls['DOWN']:
                        key_action['DOWN'] = False
                    if event.key == self.control_handler.controls['MAGIC']:
                        key_action['MAGIC'] = False
                    if event.key == self.control_handler.controls['DASH']:
                        key_action['DASH'] = False
                    if event.key == self.control_handler.controls['MELEE']:
                        key_action['MELEE'] = False
                    if event.key == self.control_handler.controls['HEAL']:
                        key_action['HEAL'] = False
                    if event.key == self.control_handler.controls['ACTION1']:
                        key_action['ACTION1'] = False
                    if event.key == self.control_handler.controls['ACTION2']:
                        key_action['ACTION2'] = False

            self.control_handler.update(key_action)
            self.screen.blit(self.canvas_no_outline, (0,0))

            #screenshake(캔버스 흔들기)
            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            #캔버스 화면에 그리기
            self.screen.blit(pygame.transform.scale(self.canvas_no_outline, self.screen.get_size()), screenshake_offset)
            reset_key(key_action)
            #업데이트
            pygame.display.update()
            self.clock.tick(60)
    
    #게임 반복문
    def main_game(self):
        #일시정지
        running = True
        pause = False

        background = self.assets['dungeon']
        background.set_alpha(40)
        self.sfx['main_bgm'].play(-1)
        self.sfx['cave_bgm'].play(-1)
        while running:
            #시계
            if not pause:
                self.clock_time['ms'] += 1
                if self.clock_time['ms'] > 60:
                    self.clock_time['ms'] = 0
                    self.clock_time['s'] += 1
                elif self.clock_time['s'] > 60:
                    self.clock_time['s'] = 0
                    self.clock_time['m'] += 1
                elif self.clock_time['m'] > 60:
                    self.clock_time['m'] = 0
                    self.clock_time['h'] += 1

            #배경 초기화
            self.canvas.fill((0,0,0,0))
            self.ui_canvas.fill((0,0,0,0))
            self.canvas_no_outline.fill((0,0,0,0))
            
            #화면 흔들림을 줄임 없으면 흔들림이 끝나지 않음 max함수 조아
            self.screenshake = max(0, self.screenshake - 1)
            
            #맵/ui
            if not pause:
                #배경 바꾸기
                if self.player_status == 'village':
                    background = self.assets['village']
                    background.set_alpha(255)
                else:
                    background = self.assets['dungeon']
                    background.set_alpha(40)

                #기본 카메라 속도
                if not self.player.airtime and not self.player.dashing and not self.player.invincible_time and not self.player.speed_boost:
                    self.scroll_speed = 30

                #트랜시션
                if self.change:
                    self.transition += 1
                    if self.transition > 30:
                        self.change = False
                if self.transition < 0:
                    self.transition += 1

                #죽었을때
                if self.dead:
                #타이머임
                    self.dead += 1
                    if self.dead >= 10:
                        self.transition = min(30, self.transition + 1)
                    if self.dead > 40:
                        if self.player.inventory['countable']['코인'] > 10:
                            self.player.inventory['countable']['코인'] -= 10
                        if self.player_status == 'shrine':
                            self.player_status = 'shrine'
                            self.load_level('shrine')
                        elif self.player_status == 'dungeon':
                            self.load_level('village')
                            self.player_status = 'village'

                #데스 트리거
                if self.player.player_health <= 0:
                    self.dead += 1    
                    
                #카메라 움직임/배경 그리기
                self.scroll[0] += (self.player.rect().centerx - self.canvas.get_width() / 2 - self.scroll[0]) / self.scroll_speed#<- 카메라 속도
                self.scroll[1] += (self.player.rect().centery - self.canvas.get_height() / 2 - self.scroll[1]) / self.scroll_speed
                render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
                #배경               
                self.canvas_no_outline.blit(background, (self.scroll[0] / -16,self.scroll[1] / -16))
                #나무 파티클 생성
                for rect in self.leaf_spawners:
                    if random.random() * 29999 < rect.width * rect.height:
                        #위의 랜덤과 곱해지는 수가 작을 수록 파티클이 많이 생성 됨
                        pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                        self.particles.append( Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20) ) )

                #맵 생성/업데이트
                self.clouds.update()
                self.clouds.render(self.canvas_no_outline, offset=render_scroll)
                self.tilemap.render(self.canvas,render_scroll, running)

                #에네미
                for enemy in self.enemies.copy():
                    enemy.update(self.tilemap, (0,0))
                    if enemy.name == 'boss':
                        self.ui.boss_fight = True
                    else:
                        self.ui.boss_fight = False

                    kill = enemy.kill_enemy()
                    enemy.render(self.canvas, offset = render_scroll)
                    if kill:
                        #적 제거/ 플레이어 킬스탯 추가
                        if enemy.name != 'boss':
                            self.enemies.remove(enemy)
                        if enemy.name == 'boss':
                            running = False
                            self.end_dialouge()
                        self.player_kills += 1
                        self.player_killing = True

                        #적 성불(?) 파티클
                        #대쉬 파티클 양
                        particle_amount = 5
                        for i in range(particle_amount):
                            #파티클 만들기
                            angle = random.random() * math.pi * 2
                            speed =  random.random() * 0.5 + 0.5
                            pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                            self.particles.append(Particle(self, 'attack', enemy.rect().center, 
                                                           velocity=pvelocity, frame=random.randint(0, 7)))
                    else:
                        #공격중이 아님
                        self.player_killing = False

                #ui 업데이트
                self.ui.update()    
                if self.player_status == 'shop':
                    self.shop_ui.update()
                if self.player_status == 'smithy':
                    self.smithy_ui.update()

            #탄환/파티클/유틸리티 타일 매니저
            if not pause:
                #(탄환)파티클 매니저| projectile =[[x, y], direction(speed), timer, monster_type(이름)]
                for projectile in self.projectiles.copy():
                    #탄환 앞으로 발사
                    projectile[0][0] += projectile[1]
                    #타이머
                    projectile[2] += 1
                    #탄환 이미지 로드
                    if projectile[3] == 'ackgima' or projectile[3] == 'boss':
                        img = self.assets['lazer']
                    elif projectile[3] == 'craper':
                        img = self.assets['magic_bullet_fire']
                    elif projectile[3] == 'iced_guy':
                        img = self.assets['magic_bullet_ice']
                    else:
                        img = self.assets['projectile']
                    #탄환 그리기
                    self.canvas.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0],
                                            projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                    #탄환빛
                    if projectile[3] == 'ackgima' or projectile[3] == 'boss':
                        self.canvas.blit(self.make_circle_surf(random.randint(5,10), (45,15,45)),
                                          (projectile[0][0] - img.get_width() / 2 - 7.5 - render_scroll[0],
                                            projectile[0][1] - img.get_height() / 2 - 7 - render_scroll[1]),
                                            special_flags=pygame.BLEND_RGB_ADD)
                    elif projectile[3] == 'iced_guy':
                        self.canvas.blit(self.make_circle_surf(random.randint(5,10), (15,45,45)),
                                          (projectile[0][0] - img.get_width() / 2 - 7.5 - render_scroll[0],
                                            projectile[0][1] - img.get_height() / 2 - 7 - render_scroll[1]),
                                            special_flags=pygame.BLEND_RGB_ADD)
                    elif projectile[3] == 'craper':
                        self.canvas.blit(self.make_circle_surf(random.randint(5,10), (45,15,15)),
                                          (projectile[0][0] - img.get_width() / 2 - 7.5 - render_scroll[0],
                                            projectile[0][1] - img.get_height() / 2 - 7 - render_scroll[1]),
                                            special_flags=pygame.BLEND_RGB_ADD)
                    else:
                        self.canvas.blit(self.make_circle_surf(random.randint(5,10), (15,15,15)),
                                          (projectile[0][0] - img.get_width() / 2 - 7.5 - render_scroll[0],
                                            projectile[0][1] - img.get_height() / 2 - 7 - render_scroll[1]),
                                            special_flags=pygame.BLEND_RGB_ADD)
                    #탄환이 벽에 닿았다면 탄환 파괴
                    if self.tilemap.solid_tile_check(projectile[0]):
                        self.projectiles.remove(projectile)
                        for i in range(4):
                            self.sparks.append(Spark(projectile[0],
                                                      random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0),
                                                      2 + random.random(), (255, 255, 255)))
                    elif projectile[2] > 280:
                        #탄환이 생성된지 280이 됐다면 삭제
                        self.projectiles.remove(projectile)
                    #플레이어가 대쉬를 하고 있지 않다면
                    elif abs(self.player.dashing) < 50:
                        if self.player.rect().collidepoint(projectile[0]) and not self.player.invincible_time:
                            #탄환과 플레이어가 닿았다면 탄환이 사라짐
                            self.projectiles.remove(projectile)
                            #플레이어 피해 처리
                            self.player.take_damage(enemy.projectile_damage)
                            #사운드 에펙트
                            self.sfx['hit'].play()
                            #max 앞에 있는게 조절함 max 함수로 인해 점점 강도가 약해짐
                            self.screenshake = max(30, self.screenshake)
                            #파티클
                            if projectile[3] == 'ackgima' or projectile[3] == 'boss':
                                self.glow_stack -= 10
                            for i in range(30):
                                angle = random.random() * math.pi * 2
                                speed = random.random() * 5
                                self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random(),
                                                          (0, 51, 153)))
                                self.particles.append(Particle(self, 'particle', self.player.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                           math.sin(angle + math.pi) * speed * 0.5],
                                                                             frame=random.randint(0, 7)))
            
                #bomb = [[x, y], 타이머, 타입]
                for bomb in self.bombs.copy():
                    img = self.assets['bomb']
                    bomb[1] -= 1
                    if bomb[1] <= 0:
                        bomb_range = pygame.rect.Rect(bomb[0][0], bomb[0][1], 30, 30)
                        img = self.assets['boom']
                        bomb[2] -= 1

                    #마스크
                    display_mask = pygame.mask.from_surface(img)
                    display_silluate = display_mask.to_surface(setcolor= (255, 0,0, self.wave_value()) , unsetcolor=(0,0,0,0))
                    #폭탄 과 폭탄 마스크 그리기
                    self.canvas.blit(img, (bomb[0][0] - img.get_width() / 2 - render_scroll[0], bomb[0][1] - img.get_height() / 2 - render_scroll[1]))
                    self.canvas.blit(display_silluate, (bomb[0][0] - img.get_width() / 2 - render_scroll[0], bomb[0][1] - img.get_height() / 2 - render_scroll[1]))
                    if bomb[1] <= 0 and bomb[2]:
                        if self.player.rect().colliderect(bomb_range):
                            self.player.take_damage(30)
                            bomb[2] = 0
                            self.bombs.remove(bomb)
                            self.sfx['explosion'].play()
                            self.sfx['hit'].play()
                            #파티클
                            for i in range(30):
                                angle = random.random() * math.pi * 2
                                speed = random.random() * 5
                                self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random(), (0, 51, 153)))
                                self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                    elif bomb[1] <= 0 and not bomb[2]:
                        self.bombs.remove(bomb)
                        self.sfx['explosion'].play()

                #(스파크)파티클 매니저
                for spark in self.sparks.copy():
                        kill = spark.update()
                        spark.render(self.canvas, offset=render_scroll)
                        if kill:
                            self.sparks.remove(spark)

                #slash =[[x, y], 대미지, timer, direction, monster_type(이름)]
                for slash in self.slashes.copy():
                    slash[2] -= 1
                    #탄환 앞으로 발사
                    if slash[2] <= 0:
                        slash[0][0] += slash[3]
                        slash_range = pygame.rect.Rect(slash[0][0], slash[0][1], 25, 5)
                    #탄환 이미지 로드
                    img = self.assets['slash']
                    #탄환 그리기
                    self.canvas.blit(img, (slash[0][0] - img.get_width() / 2 - render_scroll[0], slash[0][1] - img.get_height() / 2 - render_scroll[1]))
                    #탄환이 벽에 닿았다면 탄환 파괴
                    if self.tilemap.solid_tile_check(slash[0]):
                        self.slashes.remove(slash)
                        for i in range(4):
                            self.sparks.append(Spark(slash[0], random.random() - 0.5 + (math.pi if slash[1] > 0 else 0), 2 + random.random(), (255, 255, 255)))
                    elif slash[2] > 280:
                        #탄환이 생성된지 280이 됐다면 삭제
                        self.slashes.remove(slash)
                    #플레이어가 대쉬를 하고 있지 않다면
                    elif abs(self.player.dashing) < 50 and slash[2] <= 0:
                        if self.player.rect().colliderect(slash_range) and not self.player.invincible_time:
                            #탄환과 플레이어가 닿았다면 탄환이 사라짐
                            self.slashes.remove(slash)
                            #플레이어 피해 처리
                            self.player.take_damage(slash[1])
                            #사운드 에펙트
                            self.sfx['hit'].play()
                            #max 앞에 있는게 조절함 max 함수로 인해 점점 강도가 약해짐
                            self.screenshake = max(30, self.screenshake)
                            #파티클
                            for i in range(30):
                                angle = random.random() * math.pi * 2
                                speed = random.random() * 5
                                self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random(), (0, 51, 153)))
                                self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))

                #(탄환)마법 매니저| bullet =[[x, y], direction(speed), timer]| magic_bullets = [bullet ...]
                for bullet in self.magic_bullets.copy():
                    #탄환 앞으로 발사
                    bullet[0][0] += bullet[1]
                    #타이머
                    if self.player.using_plugin == 'light':
                        bullet[2] += 5
                    else:
                        bullet[2] += 1
                    #탄환 이미지 로드
                    if self.player.using_plugin == 'empty':
                        img = self.assets['bullet']
                    elif self.player.using_plugin == 'ice':
                        img = self.assets['magic_bullet_ice']
                    elif self.player.using_plugin == 'fire':
                        img = self.assets['magic_bullet_fire']
                    elif self.player.using_plugin == 'light':
                        img = self.assets['magic_bullet_light']
                        
                    #탄환 그리기
                    self.canvas.blit(img, (bullet[0][0] - img.get_width() / 2 - render_scroll[0], bullet[0][1] - img.get_height() / 2 - render_scroll[1]))
                    #탄환빛
                    if self.player.using_plugin == 'light':
                        self.canvas.blit(self.make_circle_surf(7, (45,45,15)), (bullet[0][0] - img.get_width() / 2 - 7.5 - render_scroll[0], bullet[0][1] - img.get_height() / 2 - 7 - render_scroll[1]), special_flags=pygame.BLEND_RGB_ADD)
                    elif self.player.using_plugin == 'ice':
                        self.canvas.blit(self.make_circle_surf(7, (15,45,45)), (bullet[0][0] - img.get_width() / 2 - 7.5 - render_scroll[0], bullet[0][1] - img.get_height() / 2 - 7 - render_scroll[1]), special_flags=pygame.BLEND_RGB_ADD)
                    elif self.player.using_plugin == 'fire':
                        self.canvas.blit(self.make_circle_surf(7, (45,15,15)), (bullet[0][0] - img.get_width() / 2 - 7.5 - render_scroll[0], bullet[0][1] - img.get_height() / 2 - 7 - render_scroll[1]), special_flags=pygame.BLEND_RGB_ADD)
                    else:
                        self.canvas.blit(self.make_circle_surf(7, (15,15,15)), (bullet[0][0] - img.get_width() / 2 - 7.5 - render_scroll[0], bullet[0][1] - img.get_height() / 2 - 7 - render_scroll[1]), special_flags=pygame.BLEND_RGB_ADD)
                    #탄환이 벽에 닿았다면 탄환 파괴
                    if self.tilemap.solid_tile_check(bullet[0]) and not self.player.using_plugin == 'light' and not self.magic_bullets == []:
                        self.magic_bullets.remove(bullet)
                        for i in range(4):
                            self.sparks.append(Spark(bullet[0], random.random() - 0.5 + (math.pi if bullet[1] > 0 else 0), 2 + random.random(), (255, 255, 255)))
                                
                    elif bullet[2] > 360:
                        #탄환이 멀리 떨어졌다면 탄환 파괴 projectile[2] == direction(speed)
                        self.magic_bullets.remove(bullet)

                    for enemy in self.enemies.copy():
                        if enemy.rect().collidepoint(bullet[0]):
                            #적 방향 전환
                            enemy.flipx = True
                            #탄환과 적과 닿았다면 탄환이 사라짐
                            try:
                                self.magic_bullets.remove(bullet)
                            except ValueError:
                                print("error")
                            
                            #적 체력 깎기
                            if self.player.using_plugin == 'empty' and not enemy.element == 'empty':
                                enemy.status = 'bullet'
                            elif self.player.using_plugin == 'fire' and not enemy.element == 'fire':
                                enemy.status = 'fire'
                            elif self.player.using_plugin == 'ice' and not enemy.element == 'ice':
                                enemy.status = 'ice'
                                #얼리는 소리
                                self.sfx['ice_magic'].play()
                            elif self.player.using_plugin == 'light' and not enemy.element == 'light':
                                enemy.status = 'light'
                            if self.player.using_plugin == enemy.element:
                                enemy.status = 'bullet'
                            
                            #적 피해 입히기
                            if enemy.element == self.player.using_plugin:
                                enemy.health -= self.player.magic_attack_damage // 2
                            elif not enemy.type == 'boss':
                                if self.player.using_plugin == 'ice' and enemy.element == 'fire':
                                    enemy.health -= self.player.magic_attack_damage * 1.5
                                elif self.player.using_plugin == 'fire' and enemy.element == 'ice':
                                    enemy.health -= self.player.magic_attack_damage * 1.5
                                elif self.player.using_plugin == 'light' and enemy.element == 'dark':
                                    enemy.health -= self.player.magic_attack_damage * 2
                                else:
                                    enemy.health -= self.player.magic_attack_damage
                            elif enemy.type == 'boss':
                                if self.player.using_plugin == 'light' and enemy.element == 'dark' and enemy.shield == False:
                                    enemy.health -= self.player.magic_attack_damage * 1.5
                                elif self.player.using_plugin == 'light' and enemy.element == 'dark' and enemy.shield == True:
                                    enemy.shield_health -= 50
                            #사운드 에펙트
                            self.sfx['hit'].play()
                            #max 앞에 있는게 조절함 max 함수로 인해 점점 강도가 약해짐
                            self.screenshake = max(30, self.screenshake)
                            #파티클
                            for i in range(30):
                                angle = random.random() * math.pi * 2
                                speed = random.random() * 5
                                self.sparks.append(Spark(enemy.rect().center, angle, 2 + random.random(), (255, 219, 170)))
                                self.particles.append(Particle(self, 'particle',enemy.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                
                #아웃 라인
                display_mask = pygame.mask.from_surface(self.canvas)
                #4번째는 alpha임
                display_silluate = display_mask.to_surface(setcolor=(0,0,0,180), unsetcolor=(0,0,0,0))
                #[(-1, 0), (1, 0), (0, -1), (0, 1)] = 좌 우 위 아래 한칸씩 4번
                for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    #canvas에 그리면 아웃라인이 생기고, canvas_no_outline에그리면 아웃 라인이 안그려짐(대충 그럼)
                    #사실은 self.canvas_no_outline에다 self.canvas의'만'실루엣을 그리는건데
                    #게임은 canvas_no_outline 의 실루엣을 안땀
                    self.canvas_no_outline.blit(display_silluate, offset)

                #파티클 매니저
                for particle in self.particles.copy():
                    kill = particle.update()
                    particle.render(self.canvas, offset=render_scroll)
                    if particle.type == 'leaf':
                        particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                    if kill:
                        self.particles.remove(particle)
                
                #인터랙션 매니저
                for interaction in self.interactions:
                    pygame.event.pump()
                    keys = pygame.key.get_pressed()
                    #인터랙션 과 닿았을시
                    if interaction.update() == 'start_shop':
                        #스페이스바를 누르고 있고 샵에 안들어가 있을시
                        if keys[pygame.K_SPACE] and not self.player_status == 'shop':
                            self.change = True
                            self.trigger = True
                            self.movement[0] = False
                            self.movement[1] = False
                            self.shop_ui.select = 0
                            self.shop_ui.text = random.choice(self.shop_ui.txtscript)
                        #트랜시션 트윈이 끝나있고 샵이 아니고 트리거가 켜져있을시
                        if not self.change and not self.player_status == 'shop' and self.trigger:
                            self.player_status = 'shop'
                            self.transition = -30
                            self.trigger = False
                    
                    if interaction.update() == 'start_enforce':
                        if keys[pygame.K_SPACE] and not self.player_status == 'smithy':
                            self.change = True
                            self.trigger = True
                            self.movement[0] = False
                            self.movement[1] = False
                            self.smithy_ui.select = 0
                            self.smithy_ui.text = random.choice(self.smithy_ui.txtscript)
                        #트랜시션 트윈이 끝나있고 샵이 아니고 트리거가 켜져있을시
                        if not self.change and not self.player_status == 'smithy' and self.trigger:
                            self.player_status = 'smithy'
                            self.transition = -30
                            self.trigger = False

                    if interaction.update() == 'start_dungeon':
                        if keys[pygame.K_SPACE] and not self.player_status == 'dungeon':
                            self.change = True
                            self.trigger = True
                            self.movement[0] = False
                            self.movement[1] = False
                        if not self.change and not self.player_status == 'dungeon' and self.trigger:
                            self.player_status = 'dungeon'
                            self.load_level(self.level)
                            self.trigger = False
                        
                    if interaction.update() == 'exit_dungeon':
                        if not len(self.enemies):
                            if keys[pygame.K_SPACE] and not self.player_status == 'village':
                                self.change = True
                                self.trigger = True
                                self.movement[0] = False
                                self.movement[1] = False
                            if not self.change and not self.player_status == 'village' and self.trigger:
                                if not self.player_status == 'shrine':
                                    self.level += 1
                                self.player_status = 'village'
                                self.load_level('village')
                                self.transition = -30
                                self.trigger = False

                #유틸타일 매니저
                for util in self.util_tiles:
                    if util.update() == 'bounce':
                        if self.player.jumps:
                            self.player.velocity[1] = -6
                            #self.player.jumps -= 1
                            self.player.airtime = 10
                            self.sfx['bounce'].play()
                    if util.update() == 'speed' and not self.player.speed_boost:
                        self.player.speed_boost = 300
                        self.sfx['bounce'].play()

                #플레이어 렌더/업데이트/속도 관리
                if not self.dead:
                    self.player.update(self.tilemap, [self.movement[1] * 3 - self.movement[0] * 3, 0] if self.player.speed_boost
                                       else [self.movement[1] - self.movement[0], 0])
                    self.player.render(self.canvas, offset = render_scroll)

            #그리기
            if not pause:
                #나가기
                if not self.change and (self.player_status == 'shop' or self.player_status == 'smithy') and self.trigger:
                    self.player_status = 'village'
                    self.transition = -30
                    self.trigger = False

                #(캔버스 흔들기)
                screenshake_offset = [random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2]

                #맵 월드에 그리기
                self.canvas_no_outline.blit(self.canvas, (0,0))
                #월드 그리기
                self.screen.blit(pygame.transform.scale(self.canvas_no_outline, (self.screen.get_width(), self.screen.get_height())), screenshake_offset)
                
                #빛
                self.dark_surface.fill((0, 0, 20))
                glow = pygame.math.clamp(15, 0, 50)
                for i in range(25):
                    color = i * glow
                    color = pygame.math.clamp(color, 0, 220)
                    pygame.draw.circle(self.dark_surface, (color, color, 60, 60), (self.player.rect().centerx - render_scroll[0],self.player.rect().centery - render_scroll[1]), (self.glow_stack/1.5) - i * 3)
                    pygame.draw.circle(self.dark_surface, (color, color, 120), (self.player.rect().centerx - render_scroll[0],self.player.rect().centery - render_scroll[1]), (self.glow_stack/1.5) - i * 3)
                self.screen.blit(pygame.transform.scale(self.dark_surface, self.screen.get_size()), (0, 0), special_flags=pygame.BLEND_RGB_MULT)
                
                if self.player.healing:
                    self.glow_stack = pygame.math.clamp(self.glow_stack + 2, 50, 300)
                    self.player.healing -= 1

                #GUI 그리기(ui는 self.ui_canvas 그려야함)
                if self.player_status == 'village' or self.player_status == 'dungeon' or  self.player_status == 'shrine':
                    self.ui.render(self.ui_canvas)
                elif self.player_status == 'shop':
                    self.shop_ui.render(self.shop_canvas)
                elif self.player_status == 'smithy':
                    self.smithy_ui.render(self.shop_canvas)
                #레벨 인트로
                self.ui.level_intro(self.ui_canvas, self.level if self.player_status == 'dungeon' else self.player_status)

                #ui를 최종적으로 그리기
                if self.player_status == 'village' or self.player_status == 'dungeon' or self.player_status == 'shrine':
                    self.screen.blit(pygame.transform.scale(self.ui_canvas, self.screen.get_size()), (0,0))
                #상점 ui를 최종적으로 그리기(상점일때만)발적화 on
                if not self.player_status == 'village' and not self.player_status == 'dungeon' and not self.player_status == 'shrine':
                    self.screen.blit(pygame.transform.scale(self.shop_canvas, self.screen.get_size()), (0,0))

                #맵 화면 전환
                if self.transition:
                    transition_surf = pygame.Surface(self.canvas.get_size())
                    pygame.draw.circle(transition_surf, (255, 255, 255), (self.canvas.get_width() // 2, self.canvas.get_height() // 2), (30 - abs(self.transition)) * 8)
                    transition_surf.set_colorkey((255, 255, 255))
                    self.screen.blit(pygame.transform.scale(transition_surf, self.screen.get_size()), (0, 0))
                
                #FPS 표시
                fps_txt = self.fonts['dialouge_font_smol'].render(str(int(self.clock.get_fps())) + ' FPS', False, 'white')
                self.screen.blit(fps_txt, (self.screen.get_width() - 38, 0))
            
            #일시정지 했을때
            if pause:
                bg = self.assets['main_art']
                bg.set_alpha(50)
                self.canvas_no_outline.blit(bg, (0,0))
                
                text = self.fonts['font_start'].render('일시정지 됨', False, 'white')
                text_esc = self.fonts['dialouge_font_smol'].render('ESC to game', False, 'white')
                text_time_H = self.fonts['dialouge_font_smol'].render('H : ' + str(self.clock_time['h']), False, 'black')
                text_time_M = self.fonts['dialouge_font_smol'].render('M : ' + str(self.clock_time['m']), False, 'black')
                text_time_S = self.fonts['dialouge_font_smol'].render('S : ' + str(self.clock_time['s']), False, 'black')
                text_time_MS = self.fonts['dialouge_font_smol'].render('MS : ' + str(self.clock_time['ms']), False, 'black')
                text_speed = self.fonts['font_stop'].render('스피드런', False, 'black')
                pygame.draw.polygon(self.canvas_no_outline, 'darkgrey', [(0, 195), (60, 240)], 220)
                self.canvas_no_outline.blit(text, (100, 35))
                self.canvas_no_outline.blit(text_esc, (130, 220))
                self.canvas_no_outline.blit(text_time_H, (0, 110))
                self.canvas_no_outline.blit(text_time_M, (0, 125))
                self.canvas_no_outline.blit(text_time_S, (0, 140))
                self.canvas_no_outline.blit(text_time_MS, (0, 155))
                self.canvas_no_outline.blit(text_speed, (0, 220))
                self.screen.blit(pygame.transform.scale(self.canvas_no_outline, self.screen.get_size()), (0,0))
            
            #이벤트 루프
            for event in pygame.event.get():
                #게임 셧다운
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                    return
                        
                #플레이어 움직임/상점
                if event.type == pygame.KEYDOWN:
                    #상점에선 못움직임
                    #샵 안에선 속박
                    #플레이어 움직임 movement는 x축 움직임
                    if event.key == pygame.K_ESCAPE:
                        pause = not pause
                    if not self.transition and (self.player_status == 'village' or self.player_status == 'dungeon' or self.player_status == 'shrine') and not pause:
                        if event.key == self.control_handler.controls['LEFT']:
                            self.movement[0] = True
                        if event.key == self.control_handler.controls['RIGHT']:
                            self.movement[1] = True
                        if event.key == self.control_handler.controls['UP/JUMP']:
                            #플레이어 점프
                            if self.player.jump():
                                #점프|벽점프 성공시
                                self.sfx['jump'].play()
                        if event.key == self.control_handler.controls['DASH']:
                            #플레이어 대쉬
                            self.player.dash()

                        if event.key == self.control_handler.controls['MELEE'] and not self.player.attk_cooldown:
                            #플레이어 공격
                            if self.player.attack():
                                self.sfx['attack'].play()
                                                
                        if event.key == self.control_handler.controls['MAGIC'] and not self.player.magic_attk_cooldown:
                            if self.player.magic():
                                    self.sfx['light_magic'].play()

                        if event.key == self.control_handler.controls['HEAL']:
                            if self.player.heal():
                                self.sfx['heal'].play()
                    
                    #===============================================================================================================
                    #상점:
                    if self.player_status == 'shop':
                        #항목 변경
                        if event.key == self.control_handler.controls['DOWN'] and self.shop_ui.select < 2:
                            self.shop_ui.select += 1
                            self.sfx['change'].play()
                        if event.key == self.control_handler.controls['UP/JUMP'] and self.shop_ui.select != 0:
                            self.shop_ui.select -= 1
                            self.sfx['change'].play()
                        #z로 항목 구매
                        if event.key == self.control_handler.controls['MAGIC'] and self.shop_ui.status == 'buy':
                            if self.shop_ui.select == 0 and not self.smithy_ui.item_info[0]['name'] in self.player.inventory['plugin']:
                                if self.player.inventory['countable']['코인'] >= int(self.shop_ui.item_info[0]['price']):
                                    self.player.inventory['plugin'].append('사파이어장식')
                                    self.player.inventory['countable']['코인'] -= int(self.shop_ui.item_info[0]['price'])
                                    self.sfx['buy'].play()
                            if self.shop_ui.select == 1 and not self.smithy_ui.item_info[1]['name'] in self.player.inventory['plugin']:
                                if self.player.inventory['countable']['코인'] >= int(self.shop_ui.item_info[1]['price']):
                                    self.player.inventory['plugin'].append('토파즈 장식')
                                    self.player.inventory['countable']['코인'] -= int(self.shop_ui.item_info[1]['price'])
                                    self.sfx['buy'].play()
                            if self.shop_ui.select == 2  and not self.smithy_ui.item_info[2]['name'] in self.player.inventory['plugin']:
                                if self.player.inventory['countable']['코인'] >= int(self.shop_ui.item_info[2]['price']):
                                    self.player.inventory['plugin'].append('루비 왕관')
                                    self.player.inventory['countable']['코인'] -= int(self.shop_ui.item_info[2]['price'])
                                    self.sfx['buy'].play()
                                
                        #c로 항목 누르기
                        if event.key == self.control_handler.controls['MELEE'] and self.shop_ui.status == 'talk' and self.shop_ui.select == 0:
                            self.shop_ui.status = 'buy'
                            self.sfx['confirm'].play()
                            self.shop_ui.select = 0
                        
                        if event.key == self.control_handler.controls['MELEE'] and self.shop_ui.status == 'talk' and self.shop_ui.select == 1:
                            self.shop_ui.status = 'say'
                            self.shop_ui.select = 0
                            self.sfx['confirm'].play()

                        if event.key == self.control_handler.controls['MELEE'] and self.shop_ui.status == 'talk' and self.shop_ui.select == 2:
                            self.sfx['confirm'].play()
                            self.change = True
                            self.trigger = True
                    
                    #대장간
                    if self.player_status == 'smithy':
                        #항목 변경
                        if self.smithy_ui.status == 'talk':
                            if event.key == self.control_handler.controls['DOWN'] and self.smithy_ui.select < 3:
                                self.smithy_ui.select += 1
                                self.sfx['change'].play()
                            if event.key == self.control_handler.controls['UP/JUMP'] and self.smithy_ui.select != 0:
                                self.smithy_ui.select -= 1
                                self.sfx['change'].play()
                        if self.smithy_ui.status == 'plugin' or self.smithy_ui.status == 'enforce':
                            if event.key == self.control_handler.controls['DOWN'] and self.smithy_ui.select < 2:
                                self.smithy_ui.select += 1
                                self.sfx['change'].play()
                            if event.key == self.control_handler.controls['UP/JUMP'] and self.smithy_ui.select != 0:
                                self.smithy_ui.select -= 1
                                self.sfx['change'].play()

                        if event.key == self.control_handler.controls['MAGIC'] and self.smithy_ui.status == 'plugin' and self.player.inventory['plugin'] != []:
                            if self.smithy_ui.select == 0 and self.smithy_ui.can_buy and not self.player.using_plugin == 'ice':
                                if self.player.inventory['countable']['코인'] >= int(self.smithy_ui.item_info[0]['change']):
                                    self.player.using_plugin = 'ice'
                                    self.sfx['buy'].play()
                                    self.player.inventory['countable']['코인'] -= int(self.smithy_ui.plugin_change_info[0]['change'])
                            if self.smithy_ui.select == 1 and self.smithy_ui.can_buy and not self.player.using_plugin == 'light':
                                if self.player.inventory['countable']['코인'] >= int(self.smithy_ui.item_info[1]['change']):
                                    self.player.using_plugin = 'light'
                                    self.sfx['buy'].play()
                                    self.player.inventory['countable']['코인'] -= int(self.smithy_ui.plugin_change_info[1]['change'])
                            if self.smithy_ui.select == 2 and self.smithy_ui.can_buy and not self.player.using_plugin == 'fire':
                                if self.player.inventory['countable']['코인'] >= int(self.smithy_ui.item_info[2]['change']):
                                    self.player.using_plugin = 'fire'
                                    self.sfx['buy'].play()
                                    self.player.inventory['countable']['코인'] -= int(self.smithy_ui.plugin_change_info[2]['change'])

                        if event.key == self.control_handler.controls['MAGIC'] and self.smithy_ui.status == 'enforce' and self.player.inventory['plugin'] != []:
                            if self.smithy_ui.select == 0 and self.smithy_ui.can_buy and not sapphire['level'] >= 5 and self.player.inventory['countable']['코인'] >= int(self.smithy_ui.plugin_change_info[0]['price']):
                                sapphire['damage'] = int(sapphire['damage'] * 1.1)
                                sapphire['time'] += 40
                                sapphire['cooltime'] -= 30
                                self.sfx['buy'].play()
                                sapphire['level'] = sapphire['level'] + 1
                                self.player.inventory['countable']['코인'] -= int(self.smithy_ui.plugin_change_info[0]['price'])
                                self.smithy_ui.plugin_change_info[0]['price'] = str(int(self.smithy_ui.plugin_change_info[0]['price']) * 2)
                            if self.smithy_ui.select == 1 and self.smithy_ui.can_buy and not topaz['level'] >= 5 and self.player.inventory['countable']['코인'] >= int(self.smithy_ui.plugin_change_info[1]['price']):
                                topaz['damage'] = int(topaz['damage'] * 1.1)
                                topaz['cooltime'] -= 40
                                topaz['slow_time'] += 20
                                self.sfx['buy'].play()
                                topaz['level'] = topaz['level'] + 1
                                self.player.inventory['countable']['코인'] -= int(self.smithy_ui.plugin_change_info[1]['price'])
                                self.smithy_ui.plugin_change_info[1]['price'] = str(int(self.smithy_ui.plugin_change_info[1]['price']) * 2)
                            if self.smithy_ui.select == 2 and self.smithy_ui.can_buy and not ruby['level'] >= 5 and self.player.inventory['countable']['코인'] >= int(self.smithy_ui.plugin_change_info[2]['price']):
                                ruby['damage'] * int(ruby['damage'] * 1.1)
                                ruby['time'] += 50
                                ruby['cooltime'] -= 20
                                self.sfx['buy'].play()
                                ruby['level'] = ruby['level'] + 1
                                self.player.inventory['countable']['코인'] -= int(self.smithy_ui.plugin_change_info[2]['price'])
                                self.smithy_ui.plugin_change_info[2]['price'] = str(int(self.smithy_ui.plugin_change_info[2]['price']) * 2)

                        #c로 항목 누르기
                        if event.key == self.control_handler.controls['MELEE'] and self.smithy_ui.status == 'talk' and self.smithy_ui.select == 0:
                            self.sfx['confirm'].play()
                            self.smithy_ui.status = 'plugin'
                            self.smithy_ui.select = 0
                        if event.key == self.control_handler.controls['MELEE'] and self.smithy_ui.status == 'talk' and self.smithy_ui.select == 1:
                            self.sfx['confirm'].play()
                            self.smithy_ui.status = 'enforce'
                            self.smithy_ui.select = 0
                        if event.key == self.control_handler.controls['MELEE'] and self.smithy_ui.status == 'talk' and self.smithy_ui.select == 2:
                            self.sfx['confirm'].play()
                            self.smithy_ui.status = 'say'
                            self.smithy_ui.select = 0
                        if event.key == self.control_handler.controls['MELEE'] and self.smithy_ui.status == 'talk' and self.smithy_ui.select == 3:
                            self.sfx['confirm'].play()
                            self.change = True
                            self.trigger = True

                    
                    #샵 뒤로 가기
                    if event.key == self.control_handler.controls['DASH'] and (self.player_status == 'shop' or self.player_status == 'smithy'):
                        for interaction in self.interactions:
                            if interaction.update() == 'start_shop':
                                if not self.shop_ui.status == 'talk':
                                    self.shop_ui.select = 0
                                    self.shop_ui.status = 'talk'
                                    self.shop_ui.text = random.choice(self.shop_ui.txtscript)
                            if interaction.update() == 'start_enforce':
                                if not self.smithy_ui.status == 'talk':
                                    self.smithy_ui.select = 0
                                    self.smithy_ui.status = 'talk'
                                    self.smithy_ui.text = random.choice(self.smithy_ui.txtscript)
                                    
                #플레이어 움직임 캔슬                  
                if event.type == pygame.KEYUP:
                    if event.key == self.control_handler.controls['LEFT']:
                        #이동 캔슬
                        self.movement[0] = False
                    if event.key == self.control_handler.controls['RIGHT']:
                        #이동 캔슬
                        self.movement[1] = False

            #업데이트
            pygame.display.update()
            self.clock.tick(60)

    def start_dialouge(self):
        dialouge = Dialouge(self, start_dialouge, self.assets['start_scene'])
        while True:
            self.canvas.fill((0,0,0))
            self.canvas_no_outline.fill((0,0,0,0))
            self.screen.fill((0,0,0))
            #다이아로그
            #뭐시기
            if dialouge.update():
                self.main_game()
                return
            dialouge.render(self.canvas)
                
            #아웃 라인
            display_mask = pygame.mask.from_surface(self.canvas)
            display_silluate = display_mask.to_surface(setcolor=(0,0,0,180), unsetcolor=(0,0,0,0))
            #[(-1, 0), (1, 0), (0, -1), (0, 1)] = 좌 우 위 아래 한칸씩
            for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                #canvas에 그리면 아웃라인이 생기고, canvas_no_outline에그리면 아웃 라인이 안그려짐(대충 그럼)
                #사실은 self.canvas_no_outline에다 self.canvas의'만'실루엣(마스크)을 그리는거임 ㅇㅇ
                #게임은 canvas_no_outline 의 실루엣을 안땀
                self.canvas_no_outline.blit(display_silluate, offset)
            #이거 뒤에 그리면 UI 즉, 맵과 플레이어 위에 그려짐
            self.canvas_no_outline.blit(self.canvas, (0,0))

            self.screen.blit(pygame.transform.scale(self.canvas_no_outline, self.screen.get_size()), (0,0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                    return
                
            #업데이트
            pygame.display.update()
            self.clock.tick(60)

    def end_dialouge(self):
        dialouge = Dialouge(self, end_dialouge, self.assets['end_scene'])
        while True:
            self.canvas.fill((0,0,0))
            self.canvas_no_outline.fill((0,0,0,0))
            self.screen.fill((0,0,0))
            #다이아로그
            #뭐시기
            if dialouge.update():
                #끝나면 게임 종료
                pygame.quit()
                exit()
                return
            dialouge.render(self.canvas)
                
            #아웃 라인
            display_mask = pygame.mask.from_surface(self.canvas)
            display_silluate = display_mask.to_surface(setcolor=(0,0,0,180), unsetcolor=(0,0,0,0))
            #[(-1, 0), (1, 0), (0, -1), (0, 1)] = 좌 우 위 아래 한칸씩
            for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                #canvas에 그리면 아웃라인이 생기고, canvas_no_outline에그리면 아웃 라인이 안그려짐(대충 그럼)
                #사실은 self.canvas_no_outline에다 self.canvas의'만'실루엣(마스크)을 그리는거임 ㅇㅇ
                #게임은 canvas_no_outline 의 실루엣을 안땀
                self.canvas_no_outline.blit(display_silluate, offset)
            #이거 뒤에 그리면 UI 즉, 맵과 플레이어 위에 그려짐
            self.canvas_no_outline.blit(self.canvas, (0,0))

            self.screen.blit(pygame.transform.scale(self.canvas_no_outline, self.screen.get_size()), (0,0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                    return
                
            #업데이트
            pygame.display.update()
            self.clock.tick(60)

    def credits(self):
        running = True
        bg = self.assets['main_art']
        bg.set_alpha(50)
        credit = Credits(self, creditdata, '심규원 -팀장 : 발표자료, 발표대사 c 서준범 -코딩 : 게임제작, 아트 c 최재훈 -편집 : 편집 c 이우진 -발표 : 발표')
        while running:
            self.canvas_no_outline.fill('black')
            credit.update()
            credit.render(self.canvas_no_outline)
            #아웃 라인
            display_mask = pygame.mask.from_surface(self.canvas)
            display_silluate = display_mask.to_surface(setcolor=(0,0,0,180), unsetcolor=(0,0,0,0))
            #[(-1, 0), (1, 0), (0, -1), (0, 1)] = 좌 우 위 아래 한칸씩
            for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                #canvas에 그리면 아웃라인이 생기고, canvas_no_outline에그리면 아웃 라인이 안그려짐(대충 그럼)
                #사실은 self.canvas_no_outline에다 self.canvas의'만'실루엣을 그리는건데
                #게임은 canvas_no_outline 의 실루엣을 안땀
                self.canvas_no_outline.blit(display_silluate, offset)
            self.canvas_no_outline.blit(bg, (0,0))
            self.canvas_no_outline.blit(self.canvas, (0,0))


            #이벤트 루프
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        self.intro_menu()


            self.screen.blit(pygame.transform.scale(self.canvas_no_outline, self.screen.get_size()), (0,0))
            #캔버스 화면에 그리기
            #업데이트
            pygame.display.update()
            self.clock.tick(60)

#HELPERFUNCTION===========================================================================================================
    def wave_value(self):
        value = math.sin(pygame.time.get_ticks())
        if value >= 0: return 255
        else: return 0
    def make_circle_surf(self, rad, color):
        surf = pygame.Surface((rad*2, rad*2))
        pygame.draw.circle(surf, color, (rad, rad), rad)
        surf.set_colorkey((0,0,0))
        return surf
   
#게임 런
if __name__ == '__main__':
    GAME().intro_menu()