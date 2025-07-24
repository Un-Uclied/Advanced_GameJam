class GameObject:
    object_list : list["GameObject"] = []
    debug = False

    @classmethod
    def update_all(cls):
        for obj in cls.object_list:
            obj.on_update()

    @classmethod
    def draw_all(cls):
        for obj in cls.object_list:
            obj.on_draw()

    def __init__(self):
        GameObject.object_list.append(self)
        
        from .app import App
        self.app = App.singleton
    
    def destroy(self):
        if self in GameObject.object_list:
            GameObject.object_list.remove(self)

    def on_update(self):
        pass

    def on_draw(self):
        if GameObject.debug : self.on_debug_draw()

    def on_debug_draw(self):
        pass