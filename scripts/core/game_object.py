import time

class GameObject:
    is_debug = False
    all_objects : list["GameObject"] = []

    def __init__(self):
        from scripts.app import App
        self.app = App.singleton
        GameObject.all_objects.append(self)

    def destroy(self):
        if self in GameObject.all_objects:
            GameObject.all_objects.remove(self)

    def update(self):
        pass

    def draw_debug(self):
        pass

    def draw(self):
        if GameObject.is_debug: self.draw_debug()

    @classmethod
    def update_all(cls):
        from scripts.entities.base import Entity
        do_not_update_when_paused = (Entity)

        if GameObject.is_debug:
            start = time.perf_counter()

        for obj in cls.all_objects:
            scene = obj.app.scene
            if not scene.scene_paused or not isinstance(obj, do_not_update_when_paused):
                obj.update()

        if GameObject.is_debug:
            end = time.perf_counter()
            print(f"[DEBUG] update_all() - {len(cls.all_objects)} objects took {round((end - start)*1000, 3)} ms")

    @classmethod
    def draw_all(cls):
        do_not_draw_when_paused = ()
        from scripts.tilemap import Tilemap
        from scripts.ui import ALL_UI_TYPE
        from scripts.enemies import ALL_ENEMY_TYPE
        from scripts.volume import Fog
        drawit = (Tilemap, ) + ALL_UI_TYPE + ALL_ENEMY_TYPE #+ (Fog, )
        from scripts.backgrounds import ALL_BACKGROUND_TYPE
        drawit = ALL_BACKGROUND_TYPE

        if GameObject.is_debug:
            start = time.perf_counter()

        for obj in cls.all_objects:
            scene = obj.app.scene
            if not scene.scene_paused or not isinstance(obj, do_not_draw_when_paused):
                obj.draw()

        if GameObject.is_debug:
            end = time.perf_counter()
            print(f"[DEBUG] draw_all() - {len(cls.all_objects)} objects took {round((end - start)*1000, 3)} ms")

    @classmethod
    def get_objects_by_types(cls, target_classes: tuple[type] | type) -> list["GameObject"]:
        if not isinstance(target_classes, (list, tuple)):
            target_classes = [target_classes]

        result = []
        for obj in cls.all_objects:
            if isinstance(obj, tuple(target_classes)):
                result.append(obj)

        return result
