import pygame as pg
from scripts.constants import *
from scripts.core import *

class Slider(GameObject):
    """
    슬라이더 UI 컴포넌트

    마우스로 값을 조정할 수 있는 인터페이스.
    드래그 시 값이 실시간으로 바뀌며, 값 변경 시 콜백 함수를 실행할 수 있음.

    Attributes:
        pos (pg.Vector2): 슬라이더 중심 좌표
        size (pg.Vector2): 슬라이더 전체 크기
        anchor (pg.Vector2): 기준점 비율 (0,0=좌상단, 0.5,0.5=중앙)
        min_val (float): 최소값
        max_val (float): 최대값
        value (float): 현재 값
        btn_size (pg.Vector2): 슬라이더 버튼 크기
        dragging (bool): 드래그 중인지 여부
        hovering (bool): 마우스가 슬라이더 위에 있는지 여부
        on_value_changed (callable): 값 변경 시 호출되는 콜백 함수
        bg_rect (pg.Rect): 슬라이더 바(rect)
        btn_rect (pg.Rect): 슬라이더 버튼(rect)
    """

    def __init__(self,
                 pos: pg.Vector2,
                 size: pg.Vector2,
                 init_val: float = .5,
                 min_val: float = 0,
                 max_val: float = 1,
                 on_value_changed=None,
                 anchor: pg.Vector2 = pg.Vector2(0.5, 0.5)):
        super().__init__()

        # 슬라이더의 위치/크기 관련 속성
        self.pos = pos
        self.size = size
        self.anchor = anchor

        # 값 관련 속성
        self.min_val = min_val
        self.max_val = max_val
        self.value = max(min(init_val, max_val), min_val)

        # 버튼 관련 속성
        self.btn_size = pg.Vector2(30, size.y + 10)
        self.dragging = False
        self.hovering = False

        # 값 변경 시 호출할 콜백
        self.on_value_changed = on_value_changed

        # 그리기용 rect 객체
        self.bg_rect = pg.Rect(0, 0, size.x, size.y)
        self.btn_rect = pg.Rect(0, 0, self.btn_size.x, self.btn_size.y)

        # rect 위치 초기화
        self.update_rects()

    @property
    def percentage(self) -> float:
        """
        현재 값을 0~1 사이 비율로 변환해서 반환.
        """
        return (self.value - self.min_val) / (self.max_val - self.min_val)

    def set_value(self, new_value: float):
        """
        슬라이더 값을 강제로 설정.

        Args:
            new_value (float): 설정할 값 (min_val ~ max_val 사이로 클램프됨)
        """
        self.value = max(min(new_value, self.max_val), self.min_val)
        self.update_rects()

    def get_anchored_pos(self) -> pg.Vector2:
        """
        anchor 기준점을 반영한 실제 좌상단 좌표 반환.
        """
        return self.pos - self.size.elementwise() * self.anchor

    def update_rects(self):
        """
        현재 값에 맞춰 bg_rect와 btn_rect 위치를 갱신.
        """
        bg_pos = self.get_anchored_pos()
        self.bg_rect.topleft = bg_pos

        percent = self.percentage
        btn_center_x = self.bg_rect.left + self.size.x * percent
        btn_center_y = self.bg_rect.centery

        self.btn_rect.size = self.btn_size
        self.btn_rect.center = (btn_center_x, btn_center_y)

    def update(self):
        """
        슬라이더 상태 업데이트 (마우스 입력 처리 + 드래그 상태 유지)
        """
        super().update()

        mouse_pos = pg.mouse.get_pos()
        mouse_down = pg.mouse.get_pressed()[0]

        # 클릭 시작 시 드래그 상태로 전환
        if self.bg_rect.collidepoint(mouse_pos) and mouse_down:
            self.dragging = True
        elif not mouse_down:
            self.dragging = False

        # 드래그 중이면 값 업데이트 + 콜백 실행
        if self.dragging:
            clamped_x = max(self.bg_rect.left, min(mouse_pos[0], self.bg_rect.right))
            percent = (clamped_x - self.bg_rect.left) / self.size.x
            self.value = self.min_val + percent * (self.max_val - self.min_val)
            self.update_rects()

            if self.on_value_changed is not None:
                self.on_value_changed()

        # 마우스 hover 상태 체크
        self.hovering = self.bg_rect.collidepoint(mouse_pos)

    def draw(self):
        """
        슬라이더 UI를 화면에 그림.
        """
        super().draw()
        surface = self.app.surfaces[LAYER_INTERFACE]
        pg.draw.rect(surface, pg.Color("gray"), self.bg_rect)
        pg.draw.rect(surface, pg.Color("white"), self.btn_rect)