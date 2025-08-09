from .game_object import GameObject

class Timer(GameObject):
    '''
    간단한 타이머 클래스
    
    특정 시간 동안 카운트다운하다가 시간이 다 되면 지정된 콜백 함수 호출함.
    게임 시간 스케일 적용 여부도 선택 가능함.
    
    :param time: 타이머가 시작하는 기본 시간 (초)
    :param on_time_out: 시간이 0이 되었을 때 호출할 함수 (없으면 None)
    :param auto_destroy: 타임아웃 후 타이머 객체를 자동으로 파괴할지 여부 (기본 True)
    :param use_unscaled: True면 게임 시간 스케일 무시하고 실제 경과 시간으로 동작
    '''

    def __init__(self, time: float, on_time_out=None, auto_destroy=True, use_unscaled: bool = False):
        super().__init__()
        
        self.max_time = time            # 타이머 시작 및 리셋 시 기준 시간
        self.current_time = time        # 현재 남은 시간 (초)

        self.on_time_out = on_time_out  # 시간이 다 됐을 때 실행할 콜백
        self.use_unscaled = use_unscaled # 게임 시간 스케일 무시 여부

        self.auto_destroy = auto_destroy # 시간이 다 되면 객체 자동 제거 여부
        self.active = True              # 타이머 동작 중인지 상태 플래그

    def reset(self):
        '''
        타이머 시간을 max_time으로 리셋함.
        '''
        self.current_time = self.max_time

    def update(self):
        '''
        매 프레임마다 호출해서 남은 시간을 감소시키고,
        시간이 0 이하가 되면 콜백 실행 및 필요시 객체 파괴 처리함.
        '''
        super().update()

        if not self.active:
            return
        
        # dt 계산 (언스케일드 또는 게임 시간 스케일 적용)
        dt = self.app.unscaled_dt if self.use_unscaled else self.app.dt
        self.current_time -= dt

        # 시간이 다 됐으면
        if self.current_time <= 0:
            if self.on_time_out is not None:
                self.on_time_out()
            if self.auto_destroy:
                self.destroy()