IS_DEBUG = True

class GameObject:
    #모든 오브젝트들은 여기 들어감 (오브젝트 업데이트 | 드로우 리스트)
    all_objects : list["GameObject"] = []

    def __init__(self):
        '''GameObject()이렇게 하지말고 GameObject를 상속받는 클래스를 만들고 그걸 생성하세여'''
        GameObject.all_objects.append(self)

        #다른 곳에서 계속 임포트할 필요 없이 미리 해놓기
        from scripts.app import App
        self.app = App.singleton

        #액티브 == False면 업데이트도 그려지지도 않음.
        self.active = True
    
    def destroy(self):
        '''특수효과 없이 조용히 삭제하는데, 이걸 오버라이드해서 특수효과 추가 하던가 할수 있음\n
        경고 : destroy()하면 업데이트 | 드로우 리스트에서 빠지는다는거지, 참조는 가능.\n
        예 : self.player = PlayerCharacter(); self.player.destroy()하면 업데이트나 그려지진 않지만,
             다른곳에서 참조할순 있음. => 플레이어가 적에게 맞을수 있음.
        '''
        
        if self in GameObject.all_objects:
            GameObject.all_objects.remove(self)

    def update(self):
        '''이걸 오버라이드 하세여'''
        pass
    
    def draw_debug(self):
        '''objects.py의 IS_DEBUG가 켜져있을때 불림'''
        pass

    def draw(self):
        '''이걸 오버라이드 하세여'''
        if IS_DEBUG and self.active: self.draw_debug()

    @classmethod
    def update_all(cls):
        '''모든 오브젝트들을 업데이트함 (주의 : 오브젝트가 생성된 순서대로 업데이트됨)'''
        for obj in cls.all_objects:
            if not obj.active: continue #액티브가 꺼져있으면 건너뛰기
            obj.update()

    @classmethod
    def draw_all(cls):
        '''모든 오브젝트들을 그림'''
        for obj in cls.all_objects:
            if not obj.active: continue #액티브가 꺼져있으면 건너뛰기
            obj.draw()

    @classmethod
    def get_objects_by_types(cls, target_classes: tuple[type] | type, get_un_actives_too: bool = False) -> list["GameObject"]:
        ''':param target_classes: 여기에 있는 클래스의 객체들 반환, 클래스 하나만 넣어줘도 됨.'''

        if not isinstance(target_classes, (list, tuple)):
            target_classes = [target_classes]

        result = []
        for obj in cls.all_objects:
            if isinstance(obj, tuple(target_classes)):
                if get_un_actives_too or obj.active:
                    result.append(obj)
        return result

    @classmethod
    def remove_all(cls, do_not_destroy: list[type] = []):
        '''모두 조용히 지움.\n
        :param do_not_destroy: 여기에 있는거 빼고 다 지움'''
        for obj in cls.all_objects[:]:
            if not any(isinstance(obj, t) for t in do_not_destroy):
                cls.all_objects.remove(obj)