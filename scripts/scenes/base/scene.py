import pygame as pg

from scripts.constants import *
from scripts.camera import *
from scripts.ui import *
from scripts.core import *
from scripts.volume import *
from scripts.vfx import *
from scripts.entities.base import Entity

class Scene:
    """
    모든 씬의 부모 클래스.
    
    씬 전환, 일시정지, 카메라, 이벤트 버스 등 공통 기능을 관리함.
    각 씬의 게임 오브젝트를 관리하고, 업데이트 및 그리기를 담당함.
    
    Attributes:
        app (App): 게임 애플리케이션 싱글톤 인스턴스.
        camera (Camera2D): 씬의 카메라 객체.
        event_bus (EventBus): 씬 전용 이벤트 버스.
        objects (list[GameObject]): 현재 씬에 속한 모든 게임 오브젝트 목록.
    """
    
    def __init__(self):
        """씬을 초기화함."""
        # App 싱글톤 인스턴스를 가져와서 게임 전역 리소스에 접근함.
        from scripts.app import App # 순환 참조 피하기.
        self.app = App.singleton

        # 씬에 속한 게임 오브젝트들을 담을 리스트를 초기화함.
        self.objects = []
        self.light_manager = LightManager(self)
        
        # 카메라, 이벤트 버스 등은 씬 시작 시점에 초기화하도록 변경함.
        self.camera = None
        self.event_bus = None
        self._scene_paused = False

    def add_object(self, obj: GameObject):
        """
        씬에 게임 오브젝트를 추가함.
        
        Args:
            obj (GameObject): 추가할 게임 오브젝트 인스턴스.
        """
        self.objects.append(obj)

    def remove_object(self, obj: GameObject):
        """
        씬에서 게임 오브젝트를 제거함.
        
        Args:
            obj (GameObject): 제거할 게임 오브젝트 인스턴스.
        """
        if obj in self.objects:
            self.objects.remove(obj)

    def on_scene_start(self):
        """
        씬이 시작될 때 호출되는 콜백 메서드.
        
        카메라와 이벤트 버스를 초기화하고 씬의 일시정지 상태를 해제함.
        자식 클래스에서 씬에 필요한 초기화 로직을 구현해야 함.
        """
        # 씬 시작 시 카메라와 이벤트 버스를 새로 생성함.
        self.camera = Camera2D(position=pg.Vector2(0, 0))
        self.event_bus = EventBus()
        self._scene_paused = False
        self.app.time_scale = 1

    def on_scene_end(self):
        """
        씬이 종료될 때 호출되는 콜백 메서드.
        
        씬에 속한 모든 게임 오브젝트를 파괴하고 일시정지 상태를 해제함.
        """
        # 씬에 속한 모든 객체를 파괴함.
        for obj in self.objects[:]: # 리스트 복사본을 순회해서 삭제 중 오류 방지
            if hasattr(obj, 'destroy'):
                obj.destroy()
        
        # 씬 종료 후에는 객체 목록이 비어있어야 함.
        self.objects.clear()
        
    @property
    def scene_paused(self) -> bool:
        """
        현재 씬의 일시정지 상태를 반환함.
        
        Returns:
            bool: 씬이 일시정지 상태이면 True, 아니면 False.
        """
        return self._scene_paused

    @scene_paused.setter
    def scene_paused(self, value: bool):
        """
        씬의 일시정지 상태를 변경함.
        
        상태 변경 시 on_pause_start 또는 on_pause_end 콜백을 호출하고,
        앱의 time_scale을 조정함.
        
        Args:
            value (bool): 설정할 일시정지 상태.
        """
        # 상태가 이미 같으면 아무것도 하지 않음.
        if self._scene_paused == value:
            return

        self._scene_paused = value
        
        if value:
            # 씬이 일시정지되면 콜백을 호출하고 앱의 시간을 멈춤.
            self.on_pause_start()
            self.app.time_scale = 0
        else:
            # 씬 일시정지가 끝나면 콜백을 호출하고 앱의 시간을 원래대로 돌림.
            self.on_pause_end()
            self.app.time_scale = 1

    def on_pause_start(self):
        """
        씬 일시정지가 시작될 때 호출되는 콜백 메서드.
        
        기본적으로 모든 효과음을 일시정지함.
        자식 클래스에서 추가적인 일시정지 로직을 구현할 수 있음.
        """
        self.app.sound_manager.pause_all_sfx()

    def on_pause_end(self):
        """
        씬 일시정지가 끝날 때 호출되는 콜백 메서드.
        
        기본적으로 모든 효과음을 다시 재생함.
        자식 클래스에서 추가적인 일시정지 해제 로직을 구현할 수 있음.
        """
        self.app.sound_manager.resume_all_sfx()

    def update(self):
        """
        매 프레임 호출되며, 씬에 속한 모든 오브젝트를 업데이트함.
        
        일시정지 상태에 따라 특정 오브젝트의 업데이트를 건너뛰는 로직을 포함함.
        """
        # 일시정지 상태에서 업데이트 안할 오브젝트의 타입을 정의함.
        do_not_update_when_paused =  (Entity, ALL_VFX_TYPE, Timer)
        
        # 모든 오브젝트를 순회하며 업데이트를 호출함.
        for obj in self.objects[:]: # 리스트 복사본을 순회해서 업데이트 중 객체 추가/삭제 오류 방지
            # 씬이 일시정지 상태가 아니거나, 일시정지 중에도 업데이트해야 하는 객체인 경우
            if not self.scene_paused or not isinstance(obj, do_not_update_when_paused):
                # 객체가 유효한지 확인하고 업데이트 메서드를 호출함.
                if hasattr(obj, 'update'):
                    obj.update()

    def draw(self):
        """
        매 프레임 호출되며, 씬에 속한 모든 오브젝트를 그림.
        
        일시정지 상태에 따른 그리기 제한은 현재 없음.
        """
        # 모든 오브젝트를 순회하며 그림.
        for obj in self.objects[:]: # 리스트 복사본을 순회해서 그리는 중 객체 추가/삭제 오류 방지
            # 객체가 유효한지 확인하고 그리기 메서드를 호출함.
            if hasattr(obj, 'draw'):
                obj.draw()

    def get_objects_by_types(self, target_classes: type | tuple[type]) -> list["GameObject"]:
        """
        특정 클래스(들)에 해당하는 씬 내의 모든 오브젝트 리스트를 반환함.
        
        Args:
            target_classes (type | tuple[type]): 필터링할 클래스 타입 또는 타입 튜플.
        
        Returns:
            list[GameObject]: 해당 타입 인스턴스 리스트.
        """
        # 리스트 컴프리헨션을 사용해 더 간결하게 작성함.
        return [obj for obj in self.objects if isinstance(obj, target_classes)]