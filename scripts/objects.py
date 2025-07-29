IS_DEBUG = True

class GameObject:
    '''GameObject()이렇게 하지말고 GameObject를 상속받는 클래스를 만들고 그걸 생성하세여'''
    #모든 오브젝트들은 여기 들어감 (오브젝트 업데이트 | 드로우 리스트)
    all_objects : list["GameObject"] = []

    def __init__(self, draw_layer : int = 1):
        #다른 곳에서 계속 임포트할 필요 없이 미리 해놓기
        from scripts.app import App
        self.app = App.singleton

        self.draw_layer = draw_layer

        GameObject.all_objects.append(self)
    
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
        if IS_DEBUG: self.draw_debug()

    @classmethod
    def update_all(cls, except_classes : tuple[type] | None = None):
        '''모든 오브젝트들을 업데이트함 (주의 : 오브젝트가 생성된 순서대로 업데이트됨)'''

        if except_classes is None:
            for obj in cls.all_objects:
                obj.update()
            return
        else:
            if not isinstance(except_classes, (list, tuple)):
                except_classes = [except_classes]

            for obj in cls.all_objects:
                if not isinstance(obj, tuple(except_classes)):
                    obj.update()
            return

    @classmethod
    def draw_all(cls):
        '''모든 오브젝트들을 그림 draw_layer순서대로 ㅇㅇ 크면 클수록 나중에 됨'''
        for obj in sorted(cls.all_objects, key=lambda o: o.draw_layer):
            obj.draw()

    @classmethod
    def get_objects_by_types(cls, target_classes: tuple[type] | type) -> list["GameObject"]:
        ''':param target_classes: 여기에 있는 클래스의 객체들 반환, 클래스 하나만 넣어줘도 됨.'''

        if not isinstance(target_classes, (list, tuple)):
            target_classes = [target_classes]

        result = []
        for obj in cls.all_objects:
            if isinstance(obj, tuple(target_classes)):
                result.append(obj)
                    
        return result