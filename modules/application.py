#외부 라이브러리 임포트
import pygame as pg
import pygame.freetype
#내부 라이브러리 임포트
from modules.scenes import MainMenuScene

#윈도우 설정
APPLICATION_NAME = "Game Prototype"
APPLICATION_RESOLUTION = (1600, 900)
APPLICATION_TARGET_FPS = 120

class Application:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(APPLICATION_RESOLUTION)
        pg.display.set_caption(APPLICATION_NAME)
        self.clock = pg.time.Clock()
        self.delta_time = 0
        self.is_running = True

        self.events = pg.event.get()
        
        self.scenes = {
            "main_menu_scene" : MainMenuScene(self)
        }
        self.current_scene = self.scenes["main_menu_scene"]
        self.current_scene.scene_enter()
    
    def change_scene(self, scene_name : str):
        self.current_scene.scene_exit()
        self.current_scene = self.scenes[scene_name]
        self.current_scene.scene_enter()
    
    def run(self):
        while self.is_running:
            self.events = pg.event.get()
            for event in self.events:
                if event.type == pg.QUIT:
                    self.is_running = False
                    
            self.current_scene.update(self.delta_time)

            self.screen.fill((20, 20, 20))
            self.current_scene.draw(self.screen)
            

            pg.display.flip()
            self.delta_time = self.clock.tick(APPLICATION_TARGET_FPS) / 1000

        pg.quit()