import pygame as pg

class Time:
    clock : pg.time.Clock = None
    
    delta_time : float = 0.0
    delta_time_unscaled : float = 0.0

    time_scale : float = 1.0

    fps : float = 0