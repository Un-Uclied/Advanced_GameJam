import time

class GameObject:
    # 디버그 모드 플래그 (True면 업데이트/드로우 걸린 시간 출력함)
    is_debug = False
    # 모든 GameObject 인스턴스 전역 리스트 (씬 전체 오브젝트 관리)
    all_objects: list["GameObject"] = []

    def __init__(self):
        # 싱글톤 App 인스턴스 참조 가져오기 (게임 전체 자원 접근용)
        from scripts.app import App
        self.app = App.singleton
        
        # 생성되면 all_objects 리스트에 자동 등록됨
        GameObject.all_objects.append(self)

    def destroy(self):
        # 오브젝트 파괴 시 all_objects 리스트에서 제거함
        if self in GameObject.all_objects:
            GameObject.all_objects.remove(self)

    def update(self):
        # 자식 클래스에서 구현, 매 프레임 호출되어 동작 갱신 담당
        pass

    def draw_debug(self):
        # 디버그용 그리기, 필요 시 오버라이드
        pass

    def draw(self):
        # 기본 draw 메서드, 디버그 모드면 draw_debug() 호출
        if GameObject.is_debug:
            self.draw_debug()

    @classmethod
    def update_all(cls):
        # 전체 GameObject를 매 프레임 업데이트함
        # 다만 게임 씬이 일시정지 상태일 땐 Entity(캐릭터 등), PlayerStatus만 업데이트 안 함
        from scripts.entities.base import Entity
        from scripts.status import PlayerStatus
        do_not_update_when_paused = (Entity, PlayerStatus)

        if GameObject.is_debug:
            start = time.perf_counter()

        for obj in cls.all_objects:
            scene = obj.app.scene
            # 씬이 일시정지 상태면 특정 객체들은 업데이트 안함
            if not scene.scene_paused or not isinstance(obj, do_not_update_when_paused):
                obj.update()

        if GameObject.is_debug:
            end = time.perf_counter()
            print(f"[DEBUG] update_all() - {len(cls.all_objects)} objects took {round((end - start)*1000, 3)} ms")

    @classmethod
    def draw_all(cls):
        # 전체 GameObject를 매 프레임 그리기 호출
        # 일시정지 상태에 따른 그리기 제한(현재는 없음)
        do_not_draw_when_paused = ()

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
        '''
        특정 클래스(들)에 해당하는 모든 오브젝트 리스트 반환
        단일 타입이나 튜플로 여러 타입 가능
        
        :param target_classes: 클래스 타입 혹은 타입 튜플
        :return: 해당 타입 인스턴스 리스트
        '''
        # 단일 타입이면 리스트로 감싸줌
        if not isinstance(target_classes, (list, tuple)):
            target_classes = [target_classes]

        result = []
        for obj in cls.all_objects:
            if isinstance(obj, tuple(target_classes)):
                result.append(obj)

        return result