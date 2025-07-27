class GameObject:
    #모든 오브젝트들은 여기 들어감 (오브젝트 업데이트 | 드로우 리스트)
    all_objects : list["GameObject"] = []

    def __init__(self):
        GameObject.all_objects.append(self)

        #다른 곳에서 계속 임포트할 필요 없이 미리 해놓기
        from scripts.app import App
        self.app = App.singleton

        #액티브 == False면 업데이트도 그려지지도 않음.
        self.active = True
    
    def destroy(self):
        # 자기 자신 제거
        if self in GameObject.all_objects:
            GameObject.all_objects.remove(self)

    def update(self):
        pass

    def draw(self):
        pass

    @classmethod
    def update_all(cls):
        '''모든 오브젝트들을 업데이트함 (주의 : 오브젝트가 생성된 순서대로 업데이트됨)'''
        for obj in cls.all_objects:
            if not obj.active: continue #액티브가 꺼져있으면 건너뛰기
            obj.update()

    @classmethod
    def draw_all(cls):
        '''모든 오브젝트들을 그림 (주의 : 오브젝트가 생성된 순서대로 그려짐)'''
        for obj in cls.all_objects:
            if not obj.active: continue #액티브가 꺼져있으면 건너뛰기
            obj.draw()

    @classmethod
    def get_objects_by_types(cls, target_classes: list[type]) -> list:
        '''target_classes안에 들어있는 클래스들의 인스턴스 반환'''
        return [obj for obj in cls.all_objects if isinstance(obj, tuple(target_classes))]

    @classmethod
    def remove_all(cls, do_not_destroy: list[type] = []):
        '''do_not_destroy에 있는거 빼고 오브젝트.destroy()를 하지 않고 그냥 지움'''
        for obj in cls.all_objects[:]:
            if not any(isinstance(obj, t) for t in do_not_destroy):
                cls.all_objects.remove(obj)