import pygame as pg
import math

class Object:
    '''클래스가 좀 크긴 한데 그래도 ^^'''
    '''일케 하는 이유가 게임이 작아서 굳이 zIndex로 1 2 3이렇게 안해도 될거 같음 ㅇㅇ'''
    all_objects = {
        "background": [], # 배경 오브젝트들이 여따가 들어오고 (예 : 하늘, 구름)
        "statics" : [], # 정적인거 (예 : 나무, 바위, 건물)
        "entities": [], # 움직이는 오브젝트들 (예 : 플레이어, 적, NPC)
        "dynamics": [], # 총알이나 vfx
        "ui": []  # UI 오브젝트들 (예 : 버튼, 텍스트, 이미지)
    }

    '''for object in Object.all_objects: #이런 느낌쓰로 간단하게 업뎃 가능 ^^
        object.update()
        object.draw()
    Object를 생성하면 all_objects에 추가됨
    Object.all_objects는 모든 Object 인스턴스를 저장하는 리스트임
    Object.all_objects를 통해 모든 Object 인스턴스에 접근할 수 있음
    예시:
    from modules.objects import Object
    for obj in Object.all_objects:
        obj.update()  # 모든 오브젝트 업데이트
        obj.draw()    # 모든 오브젝트 그리기  아 very 이지하게 업뎃
    '''

    @staticmethod
    def update_all():
        '''모든 오브젝트를 업데이트함
        이걸로 게임 오브젝트들을 업데이트 할 수 있음'''
        for tag, objects in Object.all_objects.items():
            for obj in objects:
                obj.update()

    @staticmethod
    def draw_all():
        '''모든 오브젝트를 그리기함
        이걸로 게임 오브젝트들을 그릴 수 있음'''
        for tag, objects in Object.all_objects.items():
            for obj in objects:
                obj.draw()

    def __init__(self, position=pg.Vector2(0, 0), rotation=0.0, tag = "statics"):
        '''
        Object 클래스는 모든 게임 오브젝트의 기본 클래스임
        position: 오브젝트의 위치 (pg.Vector2)
        rotation: 오브젝트의 회전 (라디안 단위)
        '''
        self.position = position
        self.rotation = rotation #얘를 직접 바꾸는건 radian 단위로 바꿔야함 그래서 anlge 프로퍼티를 만들어서 도 단위로 바꿀 수 있게 함
        self.tag = tag
        self.components = {}

        Object.all_objects[tag].append(self)

    def add_component(self, comp):
        '''
        컴포넌트를 오브젝트에 달고 그 컴포넌트를 반환함
        예:
        from modules.components import SpriteRenderer
        from modules.objects import GameObject
        obj = GameObject()
        sprite = obj.add_component(SpriteRenderer(image))
        sprite는 SpriteRenderer 인스턴스임
        '''
        self.components[type(comp)] = comp
        comp.object = self
        
        if hasattr(comp, "on_start"):
            comp.on_start()

        return comp
    
    def remove_component(self, comp_type):
        comp = self.components.pop(comp_type, None)
        if comp and hasattr(comp, "on_destroy"):
            comp.on_destroy()
        return comp

    def get_component(self, comp_type):
        return self.components.get(comp_type)
    
    def destroy(self):
        '''
        오브젝트 제거할때 컴포넌트들도 on_destroy() 호출함
        '''
        for c in self.components.values():
            if hasattr(c, "on_destroy"):
                c.on_destroy()
        Object.all_objects[self.tag].remove(self)

    def update(self):
        for c in self.components.values():
            if hasattr(c, "update"):
                c.update()

    def draw(self):
        for c in self.components.values():
            if hasattr(c, "draw"):
                c.draw()

    @property
    def right(self) -> pg.Vector2: 
        '''오브젝트의 오른쪽 방향 벡터를 반환함'''
        return pg.Vector2(math.cos(self.rotation), -math.sin(self.rotation))

    @property
    def up(self) -> pg.Vector2:
        '''오브젝트의 위쪽 방향 벡터를 반환함
        파이게임에서는 위쪽 방향이 y축이 작아지는 방향이라서 -sin, -cos로 뒤집음'''
        return pg.Vector2(-math.sin(self.rotation), -math.cos(self.rotation)) #파이게임에선 위로 갈수록 작아져서 뒤집음 ㅇㅇ;
    
    @property
    def angle(self) -> float:
        '''오브젝트의 회전 각도를 도 단위로 반환함'''
        return math.degrees(self.rotation)

    @angle.setter
    def angle(self, value: float):
        '''회전도 바꿀꺼면 이걸로 바꿔라잉'''
        self.rotation = math.radians(value)

class GameObject(Object):
    '''얘는 월드 포지션 오브젝트임'''
    def __init__(self, position=pg.Vector2(0, 0), rotation=0.0, tag = "statics"):
        super().__init__(position=position, rotation=rotation, tag=tag)

class UiObject(Object):
    '''얘는 카메라 포지션 오브젝트임'''
    def __init__(self, position=pg.Vector2(0, 0), rotation=0.0, tag = "ui"):
        super().__init__(position=position, rotation=rotation, tag=tag)

