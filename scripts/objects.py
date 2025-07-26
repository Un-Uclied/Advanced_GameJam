IS_DEBUG = True

class GameObject:
    object_list : list["GameObject"] = []

    def __init__(self):
        GameObject.object_list.append(self)

        from scripts.core import App
        self.app = App.singleton
    
    def on_destroy(self):
        if self in GameObject.object_list:
            GameObject.object_list.remove(self)

    def on_update(self):
        pass
    
    def on_debug_draw(self):
        pass

    def on_draw(self):
        if IS_DEBUG : self.on_debug_draw()

    @classmethod
    def update_all(cls):
        for obj in cls.object_list:
            obj.on_update()

    @classmethod
    def draw_all(cls):
        for obj in cls.object_list:
            obj.on_draw()