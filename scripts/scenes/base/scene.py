import pygame as pg

from scripts.constants import *
from scripts.camera import *
from scripts.ui import *
from scripts.core import *
from scripts.vfx import *

class Scene:
    """
    모든 씬의 부모 클래스
    씬 전환, 일시정지, 카메라, 이벤트 버스 등 공통 기능 관리
    """
    def __init__(self):
        from scripts.app import App
        self.app = App.singleton

        self.camera = None
        self.event_bus = None
        self._scene_paused = False

    def on_scene_start(self):
        """
        씬이 시작될 때 호출
        카메라와 이벤트 버스를 초기화하고 일시정지 상태를 해제함
        """
        self.camera = Camera2D(position=pg.Vector2(0, 0))
        self.event_bus = EventBus()
        self.scene_paused = False  # setter 호출로 time_scale 설정됨

    @property
    def scene_paused(self):
        """
        현재 씬의 일시정지 상태 반환
        """
        return self._scene_paused

    @scene_paused.setter
    def scene_paused(self, value: bool):
        """
        씬 일시정지 상태 변경
        상태가 바뀌면 on_pause_start 또는 on_pause_end 콜백 호출
        time_scale도 변경함 (일시정지 시 0, 아니면 1)
        """
        if self._scene_paused == value:
            return  # 이미 같은 상태면 무시

        self._scene_paused = value
        if value:
            self.on_pause_start()
            self.app.time_scale = 0
        else:
            self.on_pause_end()
            self.app.time_scale = 1

    def on_pause_start(self):
        """
        씬 일시정지 시작 시 호출되는 콜백
        필요하면 자식 클래스에서 재정의
        """
        pass

    def on_pause_end(self):
        """
        씬 일시정지 종료 시 호출되는 콜백
        필요하면 자식 클래스에서 재정의
        """
        pass

    def on_scene_end(self):
        """
        씬 종료 시 호출
        모든 게임 오브젝트 정리 (삭제)
        """
        GameObject.all_objects.clear()
        self.scene_paused = False

    def update(self):
        """
        매 프레임 호출, 모든 GameObject의 update() 실행
        일시정지 상태라도 update는 호출됨
        """
        GameObject.update_all()

    def draw(self):
        """
        매 프레임 호출, 모든 GameObject의 draw() 실행
        일시정지 상태라도 draw는 호출됨
        """
        GameObject.draw_all()