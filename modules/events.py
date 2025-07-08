#외부 라이브러리 임포트
import pygame as pg

class Events:
    events : list[pg.event.Event] = []

    @classmethod
    def keys_pressed(cls):
        return pg.key.get_pressed()