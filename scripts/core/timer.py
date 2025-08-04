from .game_object import GameObject

class Timer(GameObject):
    '''
    간단한 타이머 클래스

    :param time: 기본적인 시간 ㅇㅇ
    :param on_time_out: 시간 끝나면 호출됨
    :param use_unscaled: True면 App의 time_scale에 영향 안받음
    '''
    def __init__(self, time : float, on_time_out = None, auto_destroy = True, use_unscaled : bool = False):
        super().__init__()
        self.max_time = time
        self.current_time = time

        self.on_time_out = on_time_out
        self.use_unscaled = use_unscaled

        self.auto_destroy = auto_destroy
        self.active = True

    def reset(self):
        self.current_time = self.max_time

    def update(self):
        super().update()
        
        if not self.active:
            return

        self.current_time -= self.app.unscaled_dt if self.use_unscaled else self.app.dt
        if self.current_time <= 0:
            if self.on_time_out is not None:
                self.on_time_out()
            if self.auto_destroy:
                self.destroy()