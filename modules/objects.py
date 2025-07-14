import pygame as pg
import math

class GameObject:
    all_objects = {
        "background": [],  # 배경 (ex: 하늘, 구름)
        "statics": [],     # 정적 오브젝트 (ex: 나무,
        "entities": [],    # 캐릭터나 적 등 (움직임 있는 애들)
        "dynamics": [],    # 탄막, 이펙트 등 일회성
        "ui": []           # UI 요소 (ex: 버튼, 텍스트)
    }

    @classmethod
    def update_all(cls):
        '''
        모든 오브젝트를 업데이트
        '''
        for tag, objects in cls.all_objects.items():
            for obj in objects:
                obj.update()

    @classmethod
    def draw_all(cls):
        '''
        모든 오브젝트를 드로우
        '''
        for tag, objects in cls.all_objects.items():
            for obj in objects:
                obj.draw()

    @classmethod
    def new(cls, instance, parent = None) -> 'GameObject':
        '''
        새로운 오브젝트 생성 및 등록
        - instance: GameObject 인스턴스
        - parent: 부모 오브젝트 (없으면 None)
        '''
        if parent:
            instance.parent = parent
            parent.children.append(instance)
        instance.world_position = instance.local_position + (parent.world_position if parent else pg.Vector2(0, 0))
        
        cls.all_objects[instance.tag].append(instance)
        return instance

    def __init__(self, name : str, tag : str = "statics"):
        self.name = name
        self.tag = tag

        self.parent : GameObject = None  # 부모 오브젝트 (없으면 None)
        self.children : list[GameObject] = []  # 자식 오브젝트들
        self.components = {}

        self._world_position = pg.Vector2(0, 0)  # 월드 공간 위치
        self.local_position = pg.Vector2(0, 0)  # 로컬 공간

        self._angle = 0.0  # 회전 각도 (도 단위)
        self.scale = pg.Vector2(1, 1)  # 스케일 (

    def update(self):
        '''
        오브젝트 업데이트
        '''
        for comp in self.components.values():
            comp.update()
        
    def draw(self):
        '''
        오브젝트 드로우
        '''
        for comp in self.components.values():
            comp.draw()
    
    def set_parent(self, parent):
        '''
        부모 오브젝트 설정
        - parent: 새로운 부모 오브젝트
        '''
        if self.parent:
            self.parent.children.remove(self)
        
        self.parent = parent
        if parent:
            parent.children.append(self)
            self.world_position = self.local_position + parent.world_position
        else:
            self.world_position = self.local_position

    @property
    def position(self):
        '''
        오브젝트의 월드 공간 위치 반환
        '''
        return self._world_position
    @position.setter
    def position(self, value: pg.Vector2):
        '''
        오브젝트의 월드 공간 위치 설정
        - value: 새로운 위치 (pg.Vector2)
        '''
        self.local_position = value - (self.parent._world_position if self.parent else pg.Vector2(0, 0))
        self._world_position = value

    @property
    def rotation(self):
        '''
        오브젝트의 회전 각도 (도 단위) 반환
        '''
        return self._angle
    @rotation.setter
    def rotation(self, value: float):
        '''
        오브젝트의 회전 각도 (도 단위) 설정
        - value: 새로운 회전 각도 (도 단위)
        '''
        self._angle = value % 360

    @property
    def right(self) -> pg.Vector2: 
        '''오브젝트의 오른쪽 방향 벡터를 반환함'''
        radian = math.radians(self.rotation)
        return pg.Vector2(math.cos(radian), -math.sin(radian))

    @property
    def up(self) -> pg.Vector2:
        '''오브젝트의 위쪽 방향 벡터를 반환함
        -(파이게임에서는 위쪽 방향이 y축이 작아지는 방향이라서 -sin, -cos로 뒤집음)'''
        radian = math.radians(self.rotation)
        return pg.Vector2(-math.sin(radian), -math.cos(radian)) #파이게임에선 위로 갈수록 작아져서 뒤집음 ㅇㅇ;

    def add_component(self, comp):
        '''
        오브젝트에 컴포넌트 추가
        - comp: 추가할 컴포넌트 인스턴스
        '''
        self.components[type(comp)] = comp
        comp.object = self

        comp.on_start()

        return comp
    
    def remove_component(self, comp_type):
        '''
        오브젝트에서 컴포넌트 제거
        - comp_type: 제거할 컴포넌트 타입
        '''
        comp = self.components.pop(comp_type, None)
        if comp:
            comp.on_destroy()
        return comp
    
    def get_component(self, comp_type):
        '''
        오브젝트에서 컴포넌트 가져오기
        - comp_type: 가져올 컴포넌트 타입
        '''
        return self.components.get(comp_type, None)
    
    def destroy(self):
        '''
        오브젝트 제거 및 컴포넌트 on_destroy 호출
        '''
        for comp in self.components.values():
            comp.on_destroy()
        
        if self.parent:
            self.parent.children.remove(self)

        for child in self.children:
            child.destroy()
        self.children.clear()
        
        GameObject.all_objects[self.tag].remove(self)

    def find_first_child(self, name: str):
        '''
        자식 오브젝트 중 이름이 일치하는 첫 번째 오브젝트 반환
        - name: 찾을 자식 오브젝트의 이름
        '''
        for child in self.children:
            if child.name == name:
                return child
        return None
    
    def get_descendants(self):
        '''
        모든 자식 오브젝트를 재귀적으로 반환
        '''
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants