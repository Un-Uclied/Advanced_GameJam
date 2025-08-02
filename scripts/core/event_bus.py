class EventBus:
    """
    객체 간 직접 참조 없이도 메시지를 주고받을 수 있도록 도움
    예: 플레이어 피격, 적 사망, 아이템 획득, 씬 전환 등 다양한 이벤트에 활용 ㄱㄴ
    """

    def __init__(self):
        """이벤트 구독자를 저장할 딕셔너리를 초기화 (씬에서 부르기!! on_scene_start에서 만들면 씬 나가면 자동으로 사라짐 (GC로 인해서))"""
        self.subscribers: dict[str, list[callable]] = {}

    def on(self, event: str, handler: callable):
        """
        이벤트에 콜백 함수를 등록

        :param event: 문자열로 된 이벤트 이름
        :param handler: 해당 이벤트 발생 시 실행할 함수
        """
        if event not in self.subscribers:
            self.subscribers[event] = []
        self.subscribers[event].append(handler)

    def off(self, event: str, handler: callable):
        """
        등록된 이벤트 핸들러를 제거

        :param event: 이벤트 이름
        :param handler: 제거할 함수
        """
        if event in self.subscribers:
            self.subscribers[event].remove(handler)

    def emit(self, event: str, *args, **kwargs):
        """
        이벤트를 발생시켜 등록된 모든 핸들러를 호출.

        :param event: 이벤트 이름
        :param args: 핸들러에 전달할 위치 인자
        :param kwargs: 핸들러에 전달할 키워드 인자
        """
        if event in self.subscribers:
            for handler in self.subscribers[event]:
                handler(*args, **kwargs)