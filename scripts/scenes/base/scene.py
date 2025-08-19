import pygame as pg

from scripts.constants import *
from scripts.camera import *
from scripts.utils import *
from scripts.vfx import ALL_VFX_TYPE
from scripts.volume import LightManager
from scripts.projectiles.base import Projectile
from scripts.entities.base import Entity


class Scene:
    """모든 씬의 부모 클래스. 씬 전환, 카메라, 이벤트, 객체 관리 담당."""

    def __init__(self, skip_when_paused = (Entity, ALL_VFX_TYPE, Timer, Projectile)):
        from scripts.app import App  # 순환 참조 피하려고 늦게 import
        self.app = App.singleton

        self.objects: list[GameObject] = []
        self.skip_when_paused = skip_when_paused
        self.light_manager = LightManager(self)

        self.camera: Camera2D | None = None
        self.event_bus: EventBus | None = None
        self._scene_paused = False

    # -------------------------------------------------
    # 씬 라이프사이클
    # -------------------------------------------------
    def on_scene_start(self):
        """
        씬이 시작될때 호출되고, 여기서 게임오브젝트, 등등을 생성해야함.
        절대 생성자에서 게임오브젝트 생성하지 말것.
        """
        self.camera = Camera2D(position=pg.Vector2(0, 0))
        self.event_bus = EventBus()
        self.scene_paused = False
        self.app.time_scale = 1

    def on_scene_end(self):
        """씬이 끝날때 호출되고, 씬에서 생성한 모든 게임 오브젝트 제거."""
        for obj in self.objects[:]:
            if hasattr(obj, "destroy"):
                obj.destroy()
        self.objects.clear()

        self.app.sound_manager.fade_all_sfx()

    # -------------------------------------------------
    # 일시정지 관리
    # -------------------------------------------------
    @property
    def scene_paused(self) -> bool:
        return self._scene_paused

    @scene_paused.setter
    def scene_paused(self, value: bool):
        if self._scene_paused == value:
            return
        self._scene_paused = value
        if value:
            self.on_pause_start()
            self.app.time_scale = 0
        else:
            self.on_pause_end()
            self.app.time_scale = 1

    def on_pause_start(self):
        self.app.sound_manager.pause_all_sfx()

    def on_pause_end(self):
        self.app.sound_manager.resume_all_sfx()

    # -------------------------------------------------
    # 오브젝트 관리
    # -------------------------------------------------
    def add_object(self, obj: GameObject):
        self.objects.append(obj)

    def remove_object(self, obj: GameObject):
        if obj in self.objects:
            self.objects.remove(obj)

    def get_objects_by_types(self, target_classes: type | tuple[type]) -> list[GameObject]:
        return [obj for obj in self.objects if isinstance(obj, target_classes)]

    # -------------------------------------------------
    # 메인 루프
    # -------------------------------------------------
    def update(self):
        self.camera.update_shake_amount(self.app.dt)

        for obj in self.objects[:]:
            if self.scene_paused and isinstance(obj, self.skip_when_paused):
                continue
            if hasattr(obj, "update"):
                obj.update()

    def draw(self):
        for obj in self.objects[:]:
            if hasattr(obj, "draw"):
                obj.draw()
