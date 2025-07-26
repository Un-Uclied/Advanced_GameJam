IS_DEBUG = True

class GameObject:
    all_objects : list["GameObject"] = []

    def __init__(self):
        GameObject.all_objects.append(self)

        from scripts.core import App
        self.app = App.singleton
    
    def on_destroy(self):
        if self in GameObject.all_objects:
            GameObject.all_objects.remove(self)

    def on_update(self):
        pass
    
    def on_debug_draw(self):
        pass

    def on_draw(self):
        if IS_DEBUG : self.on_debug_draw()

    @classmethod
    def update_all(cls):
        for obj in cls.all_objects:
            obj.on_update()

    @classmethod
    def draw_all(cls):
        for obj in cls.all_objects:
            obj.on_draw()