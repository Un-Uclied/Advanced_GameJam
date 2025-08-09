class EventBus:
    """
    씬 내부에서 객체들끼리 직접 참조 없이 소통하게 도와주는 이벤트 시스템임.
    씬이 바뀌면 이벤트 버스도 같이 사라지니까 거기 조심할 것.
    예) 플레이어 피격, 적 사망, 아이템 획득 등 다양한 이벤트에 활용 가능함.
    """

    def __init__(self):
        """
        이벤트마다 구독(리스너)들을 저장할 딕셔너리 초기화함.
        씬 시작할 때 새로 만들고, 씬 나가면 GC가 알아서 없애줌.
        """
        self.subscribers: dict[str, list[callable]] = {}

    def connect(self, event: str, handler: callable):
        """
        특정 이벤트에 함수 등록함.
        이벤트 발생하면 등록된 함수들 다 호출됨.

        :param event: 이벤트 이름 (문자열)
        :param handler: 이벤트 발생 시 호출될 콜백 함수
        """
        if event not in self.subscribers:
            self.subscribers[event] = []
        self.subscribers[event].append(handler)

    def disconnect(self, event: str, handler: callable):
        """
        등록했던 이벤트 콜백 해제함.

        :param event: 이벤트 이름
        :param handler: 제거할 콜백 함수
        """
        if event in self.subscribers:
            if handler in self.subscribers[event]:
                self.subscribers[event].remove(handler)

    def emit(self, event: str, *args, **kwargs):
        """
        이벤트 발생시키고 등록된 모든 콜백 함수 호출함.
        인자들은 전부 콜백 함수에 넘겨줌.

        :param event: 발생시킬 이벤트 이름
        :param args: 콜백 위치 인자
        :param kwargs: 콜백 키워드 인자
        """
        if event in self.subscribers:
            for handler in self.subscribers[event]:
                handler(*args, **kwargs)