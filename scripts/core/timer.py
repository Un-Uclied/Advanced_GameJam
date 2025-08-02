from .game_object import GameObject

class Timer(GameObject):
    '''
    간단한 타이머 클래스

    :param time: 기본적인 시간 ㅇㅇ
    :param on_time_out: 시간 끝나면 호출됨
    :param use_unscaled: True면 App의 time_scale에 영향 안받음
    '''
    def __init__(self, time : float, on_time_out, use_unscaled : bool = False):
        super().__init__()
        self.current_time = time
        self.on_time_out = on_time_out
        self.use_unscaled = use_unscaled
    
    def update(self):
        super().update()

        self.current_time -= self.app.unscaled_dt if self.use_unscaled else self.app.dt
        if self.current_time <= 0:
            self.on_time_out()
            self.destroy()