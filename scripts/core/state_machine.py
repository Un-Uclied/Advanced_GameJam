from typing import Callable, Any

from .game_object import GameObject

class StateMachine(GameObject):
    '''
    간단한 상태 머신인데 만들면 좋을 것 같아서 만듦.
    근데 조심할건 만들면 만든곳에서 지워야함
    '''

    def __init__(self, initial_state: str = ""):
        super().__init__()
        self.states = {}
        self.current = initial_state

    def add(self, name: str, func):
        self.states[name] = func

    def change(self, name: str):
        self.current = name

    def update(self):
        if self.current in self.states:
            self.states[self.current]()  # 함수 실행