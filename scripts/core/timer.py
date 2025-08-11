from .game_object import GameObject

class Timer(GameObject):
    '''
    간단한 타이머 클래스.
    
    특정 시간 동안 카운트다운하다가 시간이 다 되면 지정된 콜백 함수들을 호출.
    게임 시간 스케일 적용 여부를 선택할 수 있음.
    
    Attributes:
        max_time (float): 타이머의 초기 시간.
        current_time (float): 현재 남은 시간.
        on_time_out (list): 시간이 다 됐을 때 호출할 콜백 함수 리스트.
        use_unscaled (bool): 게임 시간 스케일 무시 여부.
        auto_destroy (bool): 타임아웃 후 타이머 객체를 자동으로 파괴할지 여부.
        active (bool): 타이머가 현재 동작 중인지 나타내는 상태 플래그.
    '''

    def __init__(self, time: float, on_time_out=None, auto_destroy: bool = True, use_unscaled: bool = False):
        '''
        Timer 객체를 초기화.
        
        Args:
            time (float): 타이머가 시작하는 기본 시간 (초).
            on_time_out (callable or list, optional): 타임아웃 시 호출할 함수 또는 함수 목록.
            auto_destroy (bool): 타임아웃 후 타이머 객체를 자동으로 파괴할지 여부.
            use_unscaled (bool): True면 게임 시간 스케일을 무시하고 실제 경과 시간으로 동작.
        '''
        super().__init__()
        
        self.max_time = time
        self.current_time = time

        # 콜백을 리스트로 관리해서 여러 함수를 등록할 수 있게 함.
        self.on_time_out = []
        if on_time_out:
            if isinstance(on_time_out, (list, tuple)):
                self.on_time_out.extend(on_time_out)
            else:
                self.on_time_out.append(on_time_out)

        self.use_unscaled = use_unscaled
        self.auto_destroy = auto_destroy
        self.active = True

    def reset(self):
        '''
        타이머 시간을 `max_time`으로 리셋하고 다시 활성화.
        '''
        self.current_time = self.max_time
        self.active = True

    def update(self):
        '''
        매 프레임마다 호출돼서 남은 시간을 감소시킴.
        시간이 0 이하가 되면 콜백을 실행하고 필요시 객체를 파괴.
        '''
        if not self.active:
            return
        
        # dt 계산: 게임 시간 스케일 적용 여부를 결정.
        dt = self.app.unscaled_dt if self.use_unscaled else self.app.dt
        self.current_time -= dt

        # 시간이 0 이하가 되면 타임아웃을 처리.
        if self.current_time <= 0:
            # 타임아웃 처리 로직을 별도 메서드로 분리했음.
            self.time_out()

    def time_out(self):
        '''
        타이머가 0이 됐을 때 호출되는 메서드.
        콜백을 실행하고 타이머를 비활성화하거나 파괴함.
        '''
        # 타임아웃 콜백을 모두 호출함.
        for callback in self.on_time_out:
            callback()
        
        # 자동 파괴 옵션이 켜져 있으면 객체를 파괴함.
        if self.auto_destroy:
            self.destroy()