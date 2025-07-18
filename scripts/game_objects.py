class GameObject:
    current_scene = None
    object_list : list["GameObject"] = []

    @classmethod
    def update_all(cls):
        if cls.current_scene is None:
            return
        for obj in cls.object_list:
            obj.on_update()

    @classmethod
    def draw_all(cls):
        if cls.current_scene is None:
            return
        for obj in cls.object_list:
            obj.on_draw()

    def __init__(self):
        GameObject.object_list.append(self)
    
    def destroy(self):
        GameObject.object_list.remove(self)

    def on_update(self):
        pass

    def on_draw(self):
        pass