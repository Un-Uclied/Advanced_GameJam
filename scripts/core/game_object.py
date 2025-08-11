class GameObject:
    """
    모든 게임 내 객체들의 최상위 부모 클래스.
    
    생명주기(생성, 파괴), 업데이트, 그리기 등 기본적인 기능을 제공함.
    
    Attributes:
        app (App): 게임 애플리케이션 싱글톤 인스턴스.
    """
    
    def __init__(self):
        """
        GameObject를 초기화함.
        
        생성 시 App 싱글톤 인스턴스를 참조하고, 현재 씬의 객체 목록에 자신을 등록함.
        """
        from scripts.app import App
        # App 싱글톤 인스턴스를 참조하여 게임 전체 자원에 접근함.
        self.app = App.singleton
        
        # 씬의 객체 목록에 자신을 등록해서 씬이 객체를 관리하도록 함.
        self.app.scene.add_object(self)

    def destroy(self):
        """
        GameObject를 파괴함.
        
        객체 파괴 시 현재 씬의 객체 목록에서 자신을 제거함.
        """
        # 현재 씬 객체 목록에서 자신을 제거해서 파괴함.
        self.app.scene.remove_object(self)

    def update(self):
        """
        게임 로직을 매 프레임 업데이트함.
        
        자식 클래스에서 이 메서드를 오버라이드해서 각 객체의 동작을 구현해야 함.
        """
        pass

    def draw_debug(self):
        """
        디버그 정보를 화면에 그림.
        
        필요 시 자식 클래스에서 오버라이드하여 객체별 디버그 정보를 시각화함.
        """
        pass

    def draw(self):
        """
        객체를 화면에 그림.
        
        App의 디버그 모드가 활성화되어 있으면 draw_debug()를 호출함.
        """
        # 앱의 디버그 플래그가 켜져 있으면 디버그용 그리기를 호출함.
        if self.app.is_debug:
            self.draw_debug()

    # 클래스 메서드들은 App.scene이 관리하도록 이동됨.
    # GameObject 클래스는 더 이상 전역 객체 리스트를 직접 관리하지 않음.