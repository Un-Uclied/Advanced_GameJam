import pygame as pg

from scripts.constants import *
from scripts.utils import *

class Fog(GameObject):
    """
    씬 내 오브젝트와 엔티티에 안개 효과를 씌우는 클래스.
    
    플레이어 상태에 따라 안개의 투명도를 동적으로 조절할 수 있으며,
    빛 효과와 함께 사용해 시야 확보 효과를 연출함.
    
    Attributes:
        fog_color (pg.Color): 안개 효과의 기본 색상.
        fog_surface (pg.Surface): 안개 효과를 미리 렌더링할 임시 Surface.
    """
    
    def __init__(self, fog_color: pg.Color = pg.Color(0, 0, 0, 250)):
        """
        Fog 객체를 초기화함.
        
        Args:
            fog_color (pg.Color): 안개의 기본 색상 (알파값 포함).
        """
        # 부모 클래스의 생성자를 호출해서 씬에 등록함.
        super().__init__()
        
        # 안개 기본 색상을 저장함.
        self.base_fog_color = pg.Color(fog_color)
        
        # 안개 효과를 그릴 임시 Surface를 생성함.
        # 최적화를 위해 오브젝트와 엔티티 레이어의 크기로 만듦.
        self.fog_surface = pg.Surface(SCREEN_SIZE, flags=pg.SRCALPHA)
    
    @property
    def fog_color(self) -> pg.Color:
        """
        플레이어 상태에 따라 조정된 안개 색상을 반환함.
        
        Returns:
            pg.Color: 현재 상태에 맞는 안개 색상.
        """
        # 기본 안개 색상으로 시작함.
        final_color = pg.Color(self.base_fog_color)
        
        # 씬에 플레이어 상태 객체가 있을 경우에만 효과를 적용함.
        # hasattr 체크 대신, 메인 게임 씬에서만 Fog를 생성하도록 디자인을 변경하는 것이 더 좋음.
        if hasattr(self.scene, "player_status"):
            player_status = self.scene.player_status
            
            # 특정 소울 효과가 있으면 안개 투명도를 낮춤.
            if SOUL_KIND_B in player_status.soul_queue:
                final_color.a = max(0, final_color.a - KIND_B_FOG_ALPHA_DOWN)
                
        return final_color

    def draw_fill(self):
        """
        저사양 방식: 볼륨 레이어 전체를 안개 색으로 채움.
        
        주로 시야가 완전히 가려지는 효과를 위해 사용함.
        """
        # 볼륨 레이어 전체를 계산된 안개 색으로 채움.
        volume_surface = self.app.surfaces[LAYER_VOLUME]
        volume_surface.fill(self.fog_color)
        
        # 라이트매니저를 통해 빛 효과를 적용해서 어두운 배경에 구멍을 뚫음.
        self.scene.light_manager.draw_lights(volume_surface)
        
    def draw_multiply(self):
        """
        고사양 방식: 오브젝트/엔티티 레이어에만 안개 효과를 곱하기 모드로 적용함.
        
        더욱 정교하고 시각적으로 흥미로운 안개 효과를 연출함.
        """
        # 임시 안개 Surface를 투명하게 초기화함.
        self.fog_surface.fill((0, 0, 0, 0))

        # 오브젝트와 엔티티 레이어를 임시 Surface에 복사함.
        # 이렇게 하면 안개 효과를 적용할 영역이 제한됨.
        self.fog_surface.blit(self.app.surfaces[LAYER_OBJ], (0, 0))
        self.fog_surface.blit(self.app.surfaces[LAYER_ENTITY], (0, 0))

        # 복사된 영역에 안개 색을 곱하기 블렌딩 모드로 덧씌움.
        # 이렇게 해서 오브젝트가 있는 부분만 어둡게 만듦.
        self.fog_surface.fill(self.fog_color, special_flags=pg.BLEND_RGBA_MULT)

        # 빛 효과를 임시 안개 Surface에 적용해서 어두워진 부분에 밝은 구멍을 만듦.
        self.scene.light_manager.draw_lights(self.fog_surface)

        # 최종적으로 완성된 안개 Surface를 볼륨 레이어에 그림.
        self.app.surfaces[LAYER_VOLUME].blit(self.fog_surface, (0, 0))
    
    def draw(self):
        """
        매 프레임 호출되며, 플레이어 상태에 따라 적절한 그리기 방식을 선택함.
        """
        super().draw()
        
        # 씬에 플레이어 상태 객체가 있는지 확인해서 모드를 결정함.
        if hasattr(self.scene, "player_status"):
            player_status = self.scene.player_status
            
            # 특정 소울 효과가 있으면 저사양 fill 방식으로 시야를 완전히 가림.
            if SOUL_EVIL_C in player_status.soul_queue:
                self.draw_fill()
            # 아니면 기본 고사양 multiply 방식을 사용함.
            else:
                self.draw_multiply()
        else:
            # 플레이어 상태가 없으면 기본 고사양 multiply 방식을 사용함.
            self.draw_multiply()