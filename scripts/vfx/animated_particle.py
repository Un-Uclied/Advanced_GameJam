import pygame as pg

from scripts.constants import *
from scripts.camera import *
from scripts.core import *

class AnimatedParticle(GameObject):
    """
    애니메이션 기반 파티클 이펙트 객체
    
    설명:
    - 특정 위치에 애니메이션 효과를 띄우는 파티클
    - 애니메이션이 끝나면 자동으로 자신을 파괴해서 메모리 누수 방지
    - 보통 폭발, 불꽃, 마법 효과 등에 사용

    :param anim: Animation 인스턴스 (복사본으로 사용)
    :param position: 월드 좌표 기준 위치 (엔티티 중심 등)
    :param anchor: 이미지 기준 앵커 (0~1), 기본 중앙 (0.5, 0.5)
    """

    def __init__(self, anim : Animation, position: pg.Vector2, anchor: pg.Vector2 = pg.Vector2(.5, .5)):
        super().__init__()

        # 애니메이션 복사본 생성 (원본 공유 X)
        self.anim = anim.copy()

        self.position = position
        self.anchor = anchor

    def update(self):
        super().update()
        # 프레임마다 애니메이션 상태 업데이트 (프레임 넘김, 시간 계산 등)
        self.anim.update(self.app.dt)

        if self.anim.done:
            self.destroy()

    def draw(self):
        super().draw()
        camera = self.app.scene.camera
        surface = self.app.surfaces[LAYER_DYNAMIC]

        image = self.anim.img()
        # 이미지 크기 고려해 앵커 위치에 맞춰서 화면 좌표 계산
        screen_pos = CameraMath.world_to_screen(
            camera,
            self.position - pg.Vector2(image.get_size()).elementwise() * self.anchor
        )

        surface.blit(image, screen_pos)