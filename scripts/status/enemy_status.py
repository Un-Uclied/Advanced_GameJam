import pygame as pg
import random

from scripts.constants import *
from scripts.ui import *
from scripts.vfx import AnimatedParticle
from scripts.utils import GameObject

# UI 아이콘 위치 오프셋 상수 정의함
ICON_UI_OFFSET = pg.Vector2(40, 0)

class EnemyUI(GameObject):
    """
    적 전용 UI 관리 클래스 (체력바, 영혼 타입 텍스트, 아이콘)
    
    적의 머리 위에 표시되는 UI 요소들을 관리함:
    - 영혼 타입 텍스트
    - 영혼 타입 아이콘 
    - 체력바
    
    Args:
        enemy: UI가 붙을 적 객체
        soul_type (str): 적의 영혼 타입 문자열
        max_health (int): 적의 최대 체력값
        
    Attributes:
        enemy: 소유 적 객체 참조
        soul_type (str): 영혼 타입
        max_health (int): 최대 체력
        type_text (TextRenderer): 영혼 타입 텍스트 렌더러
        type_icon_image (ImageRenderer): 영혼 타입 아이콘 렌더러  
        health_bar (ProgressBar): 체력바 UI 컴포넌트
    """
    
    def __init__(self, enemy, soul_type, max_health):
        """
        적 UI 초기화 및 UI 요소들 생성함
        
        Args:
            enemy: 적 객체 참조
            soul_type (str): 영혼 타입
            max_health (int): 최대 체력
        """
        super().__init__()  # 부모 GameObject 초기화함
        self.enemy = enemy  # 적 객체 참조 저장함
        self.soul_type = soul_type  # 영혼 타입 저장함  
        self.max_health = max_health  # 최대 체력 저장함
        self.make_ui()  # UI 요소들 생성함

    def make_ui(self):
        """
        UI 텍스트, 아이콘, 체력바 생성 및 초기 위치 세팅함
        
        - 영혼 타입 텍스트 렌더러 생성
        - 영혼 타입 아이콘 이미지 렌더러 생성
        - 체력바 프로그레스 바 생성
        모든 UI 요소는 카메라 좌표계 사용함
        """
        app = self.app  # 앱 참조 가져옴
        
        # 영혼 타입 텍스트 렌더러 생성함 (우측 정렬, 중앙 세로 정렬)
        self.type_text = TextRenderer(
            self.soul_type,  # 표시할 텍스트
            pg.Vector2(0, 0),  # 초기 위치 (나중에 업데이트됨)
            anchor=pg.Vector2(1, 0.5),  # 앵커 포인트 설정함
            use_camera=True  # 카메라 좌표계 사용함
        )
        
        # 영혼 타입 아이콘 이미지 렌더러 생성함 (좌측 정렬, 중앙 세로 정렬)
        self.type_icon_image = ImageRenderer(
            app.ASSETS["ui"]["soul_icons"][self.soul_type],  # 아이콘 이미지 가져옴
            pg.Vector2(0, 0),  # 초기 위치 (나중에 업데이트됨)
            anchor=pg.Vector2(0, 0.5),  # 앵커 포인트 설정함
            use_camera=True  # 카메라 좌표계 사용함
        )
        
        # 체력바 프로그레스 바 생성함
        self.health_bar = ProgressBar(
            pg.Vector2(0, 0),  # 초기 위치 (나중에 업데이트됨)
            pg.Vector2(100, 3),  # 체력바 크기 (가로 100, 세로 3)
            self.max_health,  # 최대값
            0,  # 최소값
            self.max_health,  # 현재값 (초기에는 최대값)
            use_camera=True  # 카메라 좌표계 사용함
        )

    def update(self):
        """
        매 프레임 적 위치에 맞춰 UI 위치 업데이트함
        
        적의 현재 위치를 기준으로 UI 요소들의 위치를 계산하고 업데이트함:
        - 영혼 타입 텍스트: 적 중심에서 좌측으로 10픽셀 + 오프셋
        - 영혼 타입 아이콘: 적 중심에서 우측으로 10픽셀 + 오프셋  
        - 체력바: 적 중심에서 아래로 15픽셀
        """
        # 적 높이의 절반만큼 위로 올림 (적 머리 위에 UI 표시하기 위함)
        pos_offset = pg.Vector2(0, self.enemy.rect.height / 2)
        
        # 적의 중심 좌표 가져옴
        base_center = pg.Vector2(self.enemy.rect.center)
        
        # 영혼 타입 텍스트 위치 계산 및 설정함 (좌측 배치)
        self.type_text.pos = base_center + pg.Vector2(-10, 0) + pos_offset + ICON_UI_OFFSET
        
        # 영혼 타입 아이콘 위치 계산 및 설정함 (우측 배치)  
        self.type_icon_image.pos = base_center + pg.Vector2(10, 0) + pos_offset + ICON_UI_OFFSET
        
        # 체력바 위치 계산 및 설정함 (아래쪽 배치)
        self.health_bar.pos = base_center + pg.Vector2(-10, 15) + pos_offset
        
        # 부모 클래스 업데이트 호출함
        super().update()

    def update_health_bar(self, current_health):
        """
        체력바 현재값 변경함
        
        Args:
            current_health (int): 현재 체력값
        """
        # 체력바의 현재값을 새로운 체력값으로 설정함
        self.health_bar.value = current_health

    def destroy(self):
        """
        UI 관련 객체 모두 안전하게 제거함
        
        메모리 누수 방지를 위해 생성했던 모든 UI 컴포넌트를 제거함:
        - 영혼 타입 텍스트 렌더러
        - 영혼 타입 아이콘 이미지 렌더러
        - 체력바 프로그레스 바
        """
        # 영혼 타입 텍스트 렌더러 제거함
        self.type_text.destroy()
        
        # 영혼 타입 아이콘 이미지 렌더러 제거함
        self.type_icon_image.destroy()
        
        # 체력바 프로그레스 바 제거함
        self.health_bar.destroy()
        
        # 부모 클래스 제거 메소드 호출함
        super().destroy()


class EnemyStatus:
    """
    적 상태 관리 클래스 (체력, 영혼 타입, 사망, 피격 이펙트 처리)
    
    적의 생명력 관리, 영혼 타입 결정, 피격/사망 이펙트 처리를 담당함:
    - 체력 시스템 (getter/setter로 안전한 접근)
    - 영혼 타입 랜덤 선택 (플레이어 존재 시)
    - 피격/사망 시 사운드 및 파티클 이펙트 재생
    - 카메라 흔들림 효과
    - UI 업데이트 및 이벤트 발생
    
    Args:
        enemy: 소유 적 객체
        max_health (int): 적 최대 체력 초기값
        
    Attributes:
        enemy: 적 객체 참조
        app: 앱 객체 참조
        soul_type (str): 영혼 타입
        max_health (int): 최대 체력 (영혼 타입에 따라 보정될 수 있음)
        hurt_sound: 피격 사운드 에셋
        hurt_particle_anim: 피격 파티클 애니메이션 에셋
        die_sound: 사망 사운드 에셋  
        die_particle_anim: 사망 파티클 애니메이션 에셋
        enemy_ui (EnemyUI): 적 UI 관리자 (플레이어 존재 시에만)
    """
    
    def __init__(self, enemy, max_health: int):
        """
        적 상태 초기화 및 영혼 타입 결정, UI 생성함
        
        Args:
            enemy: 소유 적 객체
            max_health (int): 적 최대 체력 초기값
        """
        self.enemy = enemy  # 적 객체 참조 저장함
        self.app = enemy.app  # 앱 객체 참조 저장함
        self.scene = enemy.app.scene

        # 영혼 타입 결정 (플레이어 존재 여부에 따라)
        self.soul_type = SOUL_DEFAULT  # 기본 영혼 타입으로 초기화함
        if hasattr(self.scene, "player_status"):  # 플레이어 상태 존재 확인함
            # 악한 영혼 타입 중 랜덤하게 선택함
            self.soul_type = random.choice(ALL_EVIL_SOUL_TYPES)

        # 최대 체력 설정 (영혼 타입에 따른 보정)
        self.max_health = max_health  # 기본 최대 체력 설정함
        if self.soul_type == SOUL_EVIL_C:  # C 타입 악한 영혼인 경우
            # 체력 보너스 추가함
            self.max_health += ENEMY_EVIL_C_HEALTH_UP

        # 현재 체력을 최대 체력으로 초기화함 (private 변수 사용)
        self._health = self.max_health

        # 사운드 에셋 로드함
        self.hurt_sound = self.app.ASSETS["sounds"]["enemy"]["hurt"]  # 피격 사운드
        self.die_sound = self.app.ASSETS["sounds"]["enemy"]["die"]  # 사망 사운드
        
        # 파티클 애니메이션 에셋 로드함
        self.hurt_particle_anim = self.app.ASSETS["animations"]["vfxs"]["hurt"]  # 피격 파티클
        self.die_particle_anim = self.app.ASSETS["animations"]["vfxs"]["enemy"]["die"]  # 사망 파티클

        # UI 생성 (플레이어 상태 존재할 때만)
        self.enemy_ui = None  # UI 초기값 None으로 설정함
        if hasattr(self.scene, "player_status"):  # 플레이어 상태 존재 확인함
            # 적 UI 생성함
            self.enemy_ui = EnemyUI(self.enemy, self.soul_type, self.max_health)

    def on_enemy_die(self):
        """
        적 사망 시 처리 - UI 제거 및 이벤트 발생함
        
        사망 시 수행할 작업들:
        - UI 컴포넌트 안전하게 제거
        - 사망 이벤트를 이벤트 버스로 발생시킴
        """
        if self.enemy_ui:  # UI가 존재하는 경우만
            self.enemy_ui.destroy()  # UI 제거함
            
        # 적 사망 이벤트 발생시킴
        self.scene.event_bus.emit("on_enemy_died", self.enemy)

    def on_enemy_hit(self):
        """
        적 피격 시 이벤트 발생함
        
        피격 시 다른 시스템에 알리기 위한 이벤트 발생시킴
        """
        # 적 피격 이벤트 발생시킴  
        self.scene.event_bus.emit("on_enemy_hit", self.enemy)

    @property
    def health(self):
        """
        현재 체력값 반환하는 getter
        
        Returns:
            int: 현재 체력값
        """
        return self._health
    
    @health.setter
    def health(self, value):
        """
        체력값 설정하는 setter (각종 이펙트 및 검증 포함)
        
        체력 변경 시 수행하는 작업들:
        - 체력값 범위 검증 (0 ~ max_health)
        - 체력 감소 시 카메라 흔들림 효과
        - UI 업데이트
        - 피격/사망 이펙트 재생
        - 관련 이벤트 발생
        
        Args:
            value (int): 새로운 체력값
        """
        before_health = self._health  # 이전 체력값 저장함
        
        # 체력값을 0과 최대 체력 사이로 제한함
        self._health = max(0, min(value, self.max_health))

        if before_health > self._health:  # 체력이 감소한 경우만
            # 카메라 흔들림 강도는 입은 대미지만큼 설정함
            damage_taken = before_health - self._health  # 입은 대미지 계산함
            self.scene.camera.shake_amount += damage_taken  # 카메라 흔들림 추가함
            
            if self.enemy_ui:  # UI가 존재하는 경우
                # 체력바 업데이트함
                self.enemy_ui.update_health_bar(self._health)

            # 생존 여부에 따른 이펙트 처리
            if self._health > 0:  # 아직 살아있는 경우
                # 피격 효과 재생함
                self.app.sound_manager.play_sfx(self.hurt_sound)  # 피격 사운드 재생함
                
                # 피격 파티클 이펙트 생성함
                AnimatedParticle(self.hurt_particle_anim, pg.Vector2(self.enemy.rect.center))
                
                # 피격 이벤트 호출함
                self.on_enemy_hit()
                
            else:  # 체력이 0 이하인 경우 (사망)
                # 사망 효과 재생함
                self.app.sound_manager.play_sfx(self.die_sound)  # 사망 사운드 재생함
                
                # 사망 파티클 이펙트 생성함  
                AnimatedParticle(self.die_particle_anim, pg.Vector2(self.enemy.rect.center))
                
                # 적 객체 제거함
                self.enemy.destroy()
                
                # 사망 이벤트 호출함
                self.on_enemy_die()