class GameObject:
    object_list : list["GameObject"] = []

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
        GameObject.object_list.remove(self)

    def on_update(self):
        pass

    def on_draw(self):
        pass

class UserInterface:
    object_list : list["UserInterface"] = []

    @classmethod
    def update_all(cls):
        for obj in cls.object_list:
            obj.on_update()

    @classmethod
    def draw_all(cls):
        for obj in cls.object_list:
            obj.on_draw()

    def __init__(self, use_camera = False):
        UserInterface.object_list.append(self)
        from .app import App
        self.app = App.singleton

        self.use_camera = use_camera
    
    def destroy(self):
        UserInterface.object_list.remove(self)

    def on_update(self):
        pass

    def on_draw(self):
        pass