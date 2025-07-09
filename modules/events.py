#외부 라이브러리 임포트
import pygame as pg

class Events:
    events : list[pg.event.Event] = []

    @classmethod
    def keys_pressed(cls):
        '''
        for event in Events.events:
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_w:
                print("W key pressed") 
        위에처럼 하기 귀찮으니깐 걍 이렇게 쓰는겨
        '''
        return pg.key.get_pressed()