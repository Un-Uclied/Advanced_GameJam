import pygame as pg
import pytweening as pt
import json

from scripts.core import *
from scripts.constants import *
from scripts.status import PlayerStatus
from scripts.enemies import SCORE_UP_MAP, FiveOmega
from scripts.entities import PlayerCharacter
from scripts.backgrounds import *
from scripts.volume import *
from scripts.tilemap import *
from scripts.ui import *
from .base import Scene
from .chapter_select_scene import CUTSCENE_MAP

# 타일맵 데이터 미리 로드 (레벨별 파일, 이름 매핑)
with open("data/tilemap_data.json", 'r', encoding="utf-8") as f:  # 타일맵 데이터 파일 열음
    data = json.load(f)  # JSON 데이터 로드함
    TILEMAP_FILES_BY_CHAPTER = data["maps"]  # 챕터별 맵 파일 경로 저장함
    LEVEL_NAMES_BY_CHAPTER = data["names"]  # 챕터별 레벨 이름 저장함


class GameUI:
    """
    게임 플레이 UI 전담 클래스
    
    인게임에서 플레이어에게 표시되는 모든 UI 요소들을 관리함:
    - 플레이어 상태 UI (체력, 무적, 영혼 타입)
    - 점수 UI
    - 체력 경고 UI
    - 각종 UI 이벤트 연결 및 갱신
    
    Args:
        scene: 게임 씬 객체
        player_status (PlayerStatus): 플레이어 상태 관리자
        vignette: 비네팅 이미지 렌더러
        
    Attributes:
        scene: 게임 씬 참조
        player_status: 플레이어 상태 참조
        vignette: 비네팅 렌더러 참조
        player_health_text: 체력 텍스트 렌더러
        player_health_bar: 체력바 프로그레스 바
        player_invincible_text: 무적 상태 텍스트 렌더러
        player_soul_texts: 영혼 슬롯 텍스트 렌더러 리스트
        player_health_warning_text: 체력 경고 텍스트 렌더러
        score_text: 점수 텍스트 렌더러
    """
    
    def __init__(self, scene, player_status, vignette):
        """
        게임 UI 초기화 및 모든 UI 요소 생성함
        
        Args:
            scene: 게임 씬 객체
            player_status: 플레이어 상태 관리자
            vignette: 비네팅 이미지 렌더러
        """
        self.scene = scene  # 씬 참조 저장함
        self.player_status = player_status  # 플레이어 상태 참조 저장함
        self.vignette = vignette  # 비네팅 렌더러 참조 저장함
        self.create_all_player_ui()  # 모든 플레이어 UI 생성함

    def create_all_player_ui(self):
        """
        모든 플레이어 UI 요소들을 생성함
        
        생성되는 UI 요소들:
        - 체력 UI (텍스트 + 바)
        - 무적 상태 UI
        - 영혼 슬롯 UI
        - 점수 UI
        - 체력 경고 UI
        """
        self.create_health_ui()  # 체력 UI 생성함
        self.create_invincibility_ui()  # 무적 상태 UI 생성함
        self.create_soul_ui()  # 영혼 슬롯 UI 생성함
        self.create_score_ui()  # 점수 UI 생성함
        self.create_health_warning_ui()  # 체력 경고 UI 생성함

    def create_health_ui(self):
        """
        체력 UI 세팅 + 이벤트 연결 (체력 변화 시 텍스트, 바, 비네팅 색 변경)
        
        생성되는 요소들:
        - 체력 텍스트 (현재/최대 형식)
        - 체력바 프로그레스 바
        - 체력 변경 이벤트 리스너
        """
        # 체력 텍스트 렌더러 생성함 (현재/최대 형식으로 표시)
        health_display = f"{self.player_status.health} | {self.player_status.max_health}"
        self.player_health_text = TextRenderer(
            health_display,  # 표시할 체력 텍스트
            pg.Vector2(25, 700),  # 위치 (좌측 하단)
            font_name="gothic",  # 폰트명
            font_size=64,  # 폰트 크기
            anchor=pg.Vector2(0, .5)  # 앵커 포인트 (좌측 중앙 정렬)
        )
        
        # 체력바 프로그레스 바 생성함
        self.player_health_bar = ProgressBar(
            pg.Vector2(25, 740),  # 위치 (체력 텍스트 아래)
            pg.Vector2(150, 5),  # 크기 (가로 150, 세로 5)
            self.player_status.health,  # 현재값
            0,  # 최소값
            self.player_status.max_health,  # 최대값
            anchor=pg.Vector2(0, .5)  # 앵커 포인트
        )
        
        def on_player_health_changed():
            """
            플레이어 체력 변경 시 호출되는 콜백 함수
            
            수행 작업:
            - 체력 텍스트 업데이트
            - 체력바 최대값 및 현재값 업데이트
            - 체력 20 이하 시 붉은 비네팅 + 경고 텍스트 표시
            - 체력 정상 시 검은 비네팅으로 복구
            """
            # 체력 텍스트 업데이트함
            new_display = f"{self.player_status.health} | {self.player_status.max_health}"
            self.player_health_text.text = new_display
            
            # 체력바 최대값 업데이트함
            self.player_health_bar.max_val = self.player_status.max_health
            
            # 체력바 현재값 업데이트함
            self.player_health_bar.value = self.player_status.health

            # 체력 20 이하일 때 위험 상태 UI 표시함
            if self.player_status.health <= 20:
                # 붉은 비네팅으로 변경함
                self.vignette.image = self.scene.app.ASSETS["ui"]["vignette"]["red"]
                
                # 경고 텍스트 알파값 증가시킴
                self.player_health_warning_text.alpha = 180
            else:
                # 검은 비네팅으로 복구함
                self.vignette.image = self.scene.app.ASSETS["ui"]["vignette"]["black"]
                
                # 경고 텍스트 숨김
                self.player_health_warning_text.alpha = 0

        # 플레이어 체력 변경 이벤트에 콜백 연결함
        self.scene.event_bus.connect("on_player_health_changed", lambda _: on_player_health_changed())

    def create_invincibility_ui(self):
        """
        무적 상태 텍스트 표시, 무적 시작/끝에 따라 알파 조절함
        
        생성되는 요소들:
        - 무적 상태 텍스트 렌더러 (기본 숨김)
        - 무적 상태 변경 이벤트 리스너
        """
        # 무적 상태 텍스트 렌더러 생성함 (기본 숨김 상태)
        self.player_invincible_text = TextRenderer(
            "무적 상태",  # 표시할 텍스트
            pg.Vector2(25, 675),  # 위치 (체력 텍스트 위쪽)
            font_size=30,  # 폰트 크기
            anchor=pg.Vector2(0, 1)  # 앵커 포인트 (좌측 하단 정렬)
        )
        self.player_invincible_text.alpha = 0  # 초기에는 투명하게 설정함

        def on_player_invincible(is_start):
            """
            플레이어 무적 상태 변경 시 호출되는 콜백 함수
            
            Args:
                is_start (bool): 무적 시작 여부 (True: 시작, False: 종료)
            """
            # 무적 시작 시 텍스트 보이고, 종료 시 숨김
            self.player_invincible_text.alpha = 255 if is_start else 0

        # 플레이어 무적 상태 변경 이벤트에 콜백 연결함
        self.scene.event_bus.connect("on_player_invincible", on_player_invincible)

    def create_soul_ui(self):
        """
        영혼 슬롯 UI: 큐 크기에 따라 텍스트 동적 생성/제거 + 내용 갱신함
        
        생성되는 요소들:
        - 영혼 슬롯별 텍스트 렌더러 리스트
        - 영혼 변경 이벤트 리스너
        """
        self.player_soul_texts = []  # 영혼 텍스트 렌더러 리스트 초기화함
        queue = self.player_status.soul_queue  # 현재 영혼 큐 참조 가져옴
        
        # 현재 영혼 큐에 있는 각 슬롯별로 텍스트 생성함
        for i in range(len(queue)):
            slot_index = len(queue) - i  # 슬롯 인덱스 계산함 (역순)
            y_pos = 620 - i * 40  # Y 위치 계산함 (위에서부터 40픽셀씩 간격)
            
            # 영혼 슬롯 텍스트 렌더러 생성함
            txt = TextRenderer(
                f"영혼 타입 [{slot_index}]: {queue[i]}",  # 슬롯 정보 텍스트
                pg.Vector2(25, y_pos),  # 위치
                font_size=30,  # 폰트 크기
                anchor=pg.Vector2(0, .5)  # 앵커 포인트
            )
            self.player_soul_texts.append(txt)  # 리스트에 추가함
        
        def on_player_soul_changed():
            """
            플레이어 영혼 변경 시 호출되는 콜백 함수
            
            수행 작업:
            - 영혼 큐 크기에 맞춰 텍스트 렌더러 개수 조정
            - 각 슬롯의 내용 업데이트
            - 불필요한 텍스트 렌더러 제거
            """
            queue = self.player_status.soul_queue  # 현재 영혼 큐 가져옴
            
            # 텍스트 수가 부족하면 새로 생성함
            while len(self.player_soul_texts) < len(queue):
                slot_index = len(self.player_soul_texts) + 1  # 새 슬롯 인덱스
                y_pos = 620 - (len(self.player_soul_texts)) * 40  # Y 위치 계산함
                
                # 새 텍스트 렌더러 생성함
                txt = TextRenderer(
                    "",  # 초기 텍스트 (나중에 업데이트됨)
                    pg.Vector2(25, y_pos),  # 위치
                    font_size=30,  # 폰트 크기
                    anchor=pg.Vector2(0, .5)  # 앵커 포인트
                )
                self.player_soul_texts.append(txt)  # 리스트에 추가함

            # 각 슬롯의 내용 갱신함
            for i, soul_type in enumerate(queue):
                slot_index = len(queue) - i  # 슬롯 인덱스 계산함
                # 텍스트 내용 업데이트함
                self.player_soul_texts[i].text = f"영혼 타입 [{slot_index}]: {soul_type}"
            
            # 남은 텍스트 렌더러들 제거함
            while len(self.player_soul_texts) > len(queue):
                txt_to_destroy = self.player_soul_texts.pop()  # 마지막 텍스트 가져옴
                txt_to_destroy.destroy()  # 텍스트 렌더러 파괴함

        # 플레이어 영혼 변경 이벤트에 콜백 연결함
        self.scene.event_bus.connect("on_player_soul_changed", lambda: on_player_soul_changed())

    def create_health_warning_ui(self):
        """
        체력 경고 텍스트 생성함 (기본 숨김 상태)
        
        생성되는 요소들:
        - 체력 경고 텍스트 렌더러 (화면 상단 중앙)
        """
        # 체력 경고 텍스트 렌더러 생성함
        self.player_health_warning_text = TextRenderer(
            "체력 낮음!!",  # 경고 메시지
            pg.Vector2(SCREEN_SIZE.x / 2, 50),  # 위치 (화면 상단 중앙)
            font_name="bold",  # 굵은 폰트
            font_size=72,  # 큰 폰트 크기
            anchor=pg.Vector2(.5, .5)  # 앵커 포인트 (중앙 정렬)
        )
        self.player_health_warning_text.alpha = 0  # 초기에는 투명하게 설정함

    def create_score_ui(self):
        """
        점수 UI + 점수 변화 시 간단한 스케일 애니메이션 효과함
        
        생성되는 요소들:
        - 점수 텍스트 렌더러
        - 점수 변경 이벤트 리스너 (스케일 애니메이션 포함)
        """
        # 점수 텍스트 렌더러 생성함
        self.score_text = TextRenderer(
            f"[ {self.scene.score} ]",  # 점수 표시 형식
            pg.Vector2(100, 50),  # 위치 (화면 좌상단)
            "gothic",  # 폰트명
            64,  # 폰트 크기
            anchor=pg.Vector2(0.5, 0.5)  # 앵커 포인트 (중앙 정렬)
        )
        
        def score_changed(score_up):
            """
            점수 변경 시 호출되는 콜백 함수
            
            Args:
                score_up (bool): 점수 증가 여부 (True: 증가, False: 감소)
            """
            # 점수 텍스트 업데이트함
            self.score_text.text = f"[ {self.scene.score} ]"
            
            if score_up:  # 점수 증가 시
                # 스케일 확대 애니메이션 실행함 (2배 -> 1배)
                Tween(self.score_text, "scale", 2, 1, .15, pt.easeInOutQuad, use_unscaled_time=True)
            else:  # 점수 감소 시
                # 스케일 축소 애니메이션 실행함 (0.5배 -> 1배)
                Tween(self.score_text, "scale", .5, 1, .15, pt.easeInOutQuad, use_unscaled_time=True)

        # 점수 변경 이벤트에 콜백 연결함
        self.scene.event_bus.connect("on_score_changed", score_changed)


class PauseUI:
    """
    일시정지 메뉴 UI 전담 클래스
    
    일시정지 상태에서 표시되는 UI 요소들을 관리함:
    - 일시정지 배경 및 메뉴
    - 영혼 슬롯 정보 표시
    - 각종 버튼 (챕터 선택, 재시작, 초기화)
    
    Args:
        scene: 게임 씬 객체
        player_status: 플레이어 상태 관리자
        
    Attributes:
        scene: 게임 씬 참조
        player_status: 플레이어 상태 참조
        pause_menu_objects: 일시정지 메뉴 UI 객체들 리스트
    """
    
    def __init__(self, scene, player_status):
        """
        일시정지 UI 초기화함
        
        Args:
            scene: 게임 씬 객체
            player_status: 플레이어 상태 관리자
        """
        self.scene = scene  # 씬 참조 저장함
        self.player_status = player_status  # 플레이어 상태 참조 저장함
        self.pause_menu_objects = []  # UI 객체 리스트 초기화함

    def show(self):
        """
        일시정지 메뉴 UI 표시함
        
        생성되는 요소들:
        - 일시정지 배경
        - 영혼 슬롯별 아이콘, 이름, 설명
        - 제목 텍스트들
        - 각종 버튼들 (챕터 선택, 재시작, 초기화)
        - 일시정지 알림 팝업 텍스트
        """
        # 일시정지 배경 이미지 추가함
        bg_image = ImageRenderer(
            self.scene.app.ASSETS["ui"]["pause_bg"],  # 배경 이미지
            pg.Vector2(0, 0),  # 위치 (좌상단)
            anchor=pg.Vector2(0, 0)  # 앵커 포인트
        )
        self.pause_menu_objects.append(bg_image)

        # 영혼 슬롯별 정보 표시함
        for i, soul_type in enumerate(self.player_status.soul_queue):
            y_offset = i * 200  # 각 슬롯별 Y 오프셋 계산함
            
            # 영혼 아이콘 이미지 렌더러
            soul_icon = ImageRenderer(
                self.scene.app.ASSETS["ui"]["soul_icons"][soul_type],  # 영혼 아이콘
                pg.Vector2(500, 400 - y_offset),  # 위치
                scale=4,  # 스케일 (4배 확대)
                anchor=pg.Vector2(0, .5)  # 앵커 포인트
            )
            
            # 영혼 타입 이름 텍스트 렌더러
            soul_name = TextRenderer(
                soul_type,  # 영혼 타입명
                pg.Vector2(620, 340 - y_offset),  # 위치
                font_name="bold",  # 굵은 폰트
                font_size=35  # 폰트 크기
            )
            
            # 영혼 타입 설명 텍스트 렌더러
            soul_desc = TextRenderer(
                SOUL_DESCRIPTION[soul_type],  # 영혼 설명
                pg.Vector2(620, 400 - y_offset),  # 위치
                font_name="bold",  # 굵은 폰트
                font_size=20  # 폰트 크기
            )
            
            # 영혼 관련 UI 요소들을 리스트에 추가함
            self.pause_menu_objects.extend([soul_icon, soul_name, soul_desc])

        # 게임 제목 세로 텍스트 (L-i-m-e-n)
        title_vertical = TextRenderer(
            "L\ni\nm\ne\nn",  # 세로로 배치할 제목
            pg.Vector2(15, 5),  # 위치 (좌상단)
            font_name="gothic",  # 폰트명
            font_size=75  # 폰트 크기
        )
        
        # 일시정지 제목 텍스트
        pause_title = TextRenderer(
            "일시 정지",  # 제목 텍스트
            pg.Vector2(80, 20),  # 위치
            font_name="bold",  # 굵은 폰트
            font_size=55  # 폰트 크기
        )
        
        # 챕터 선택 안내 텍스트
        chapter_guide = TextRenderer(
            "챕터 선택으로",  # 안내 텍스트
            pg.Vector2(150, 580),  # 위치
            font_size=25,  # 폰트 크기
            anchor=pg.Vector2(0.5, 0.5)  # 앵커 포인트
        )
        
        # 챕터 선택 버튼 (앱 종료 아이콘 사용)
        chapter_btn = ImageButton(
            "app_quit",  # 버튼 이미지 키
            pg.Vector2(150, 650),  # 위치
            lambda _: self.scene.app.change_scene("chapter_select_scene"),  # 클릭 콜백
            None  # 추가 파라미터 없음
        )
        
        # 재시작 버튼
        restart_btn = ImageButton(
            "restart",  # 버튼 이미지 키
            pg.Vector2(150, 750),  # 위치
            lambda _: self.scene.app.change_scene("main_game_scene"),  # 클릭 콜백
            None  # 추가 파라미터 없음
        )
        
        # 초기화 버튼
        reset_btn = ImageButton(
            "reset",  # 버튼 이미지 키
            pg.Vector2(800, 650),  # 위치
            lambda _: self.on_reset_button_clicked(),  # 클릭 콜백
            None  # 추가 파라미터 없음
        )

        # 모든 텍스트와 버튼들을 리스트에 추가함
        self.pause_menu_objects.extend([
            title_vertical, pause_title, chapter_guide,
            chapter_btn, restart_btn, reset_btn
        ])

        # 일시정지 알림 팝업 텍스트 표시함
        PopupText(
            "일시정지 됨.",  # 팝업 메시지
            pg.Vector2(SCREEN_SIZE.x / 2, 730),  # 위치 (화면 하단 중앙)
            fade_delay=0,  # 페이드 딜레이
            fade_duration=1  # 페이드 지속시간
        )

    def hide(self):
        """
        일시정지 메뉴 UI 숨김 및 정리함
        
        수행 작업:
        - 모든 UI 객체들 파괴
        - UI 객체 리스트 비움
        - 일시정지 해제 알림 팝업 표시
        """
        # 모든 UI 객체들 파괴함
        for ui in self.pause_menu_objects:
            ui.destroy()  # 각 UI 객체 파괴함
            
        self.pause_menu_objects.clear()  # UI 객체 리스트 비움
        
        # 일시정지 해제 알림 팝업 텍스트 표시함
        PopupText(
            "일시정지 해제.",  # 팝업 메시지
            pg.Vector2(SCREEN_SIZE.x / 2, 760),  # 위치 (화면 하단 중앙)
            fade_delay=0,  # 페이드 딜레이
            fade_duration=1  # 페이드 지속시간
        )

    def on_reset_button_clicked(self):
        """
        일시정지 상태에서 초기화 버튼 클릭 시 처리함
        
        수행 작업:
        - 일시정지 해제
        - 영혼 큐에 기본 영혼 채움 (버그 방지용)
        - 영혼 변경 이벤트 발생
        - 초기화 사운드 재생
        """
        self.scene.scene_paused = False  # 일시정지 해제함
        
        # 큐에 기본 영혼 채우기 (버그방지용)
        for i in range(len(self.player_status.soul_queue)):
            self.player_status.soul_queue.append(SOUL_DEFAULT)  # 기본 영혼 추가함
            
        # 영혼 변경 이벤트 발생시킴
        self.scene.event_bus.emit("on_player_soul_changed")
        
        # 초기화 사운드 재생함
        self.scene.app.sound_manager.play_sfx(self.scene.app.ASSETS["sounds"]["ui"]["reset"])

class BossUI:
    """
    보스 전용 UI 클래스
    
    보스전에서 표시되는 UI 요소들을 관리함:
    - 보스 이름 라벨
    - 보스 체력바
    
    Args:
        scene: 게임 씬 객체
        
    Attributes:
        scene: 게임 씬 참조
        boss: 보스 객체 참조 (FiveOmega)
        name: 보스 이름 텍스트 렌더러
        health_bar: 보스 체력바 프로그레스 바
    """
    
    def __init__(self, scene):
        """
        보스 UI 초기화 및 UI 요소 생성함
        
        Args:
            scene: 게임 씬 객체
        """
        self.scene = scene  # 씬 참조 저장함
        
        # 씬에서 FiveOmega 타입 보스 객체 찾아서 참조 저장함
        self.boss: FiveOmega = self.scene.get_objects_by_types(FiveOmega)[0]

        self.create_name_label()  # 보스 이름 라벨 생성함
        self.create_boss_healthbar()  # 보스 체력바 생성함

    def destroy(self):
        """
        보스 UI 요소들 정리함
        
        메모리 누수 방지를 위해 생성했던 UI 요소들을 파괴함
        """
        self.health_bar.destroy()  # 체력바 파괴함
        self.name.destroy()  # 이름 텍스트 파괴함

    def create_name_label(self):
        """
        보스 이름 라벨 생성함
        
        화면 상단 중앙에 보스 이름을 표시하는 텍스트 렌더러 생성함
        """
        # 보스 이름 텍스트 렌더러 생성함
        self.name = TextRenderer(
            "< ??? >",  # 보스 이름 (미스터리하게 표시)
            pg.Vector2(SCREEN_SIZE.x / 2, 70),  # 위치 (화면 상단 중앙)
            anchor=pg.Vector2(0.5, 0)  # 앵커 포인트 (상단 중앙 정렬)
        )

    def create_boss_healthbar(self):
        """
        보스 체력바 생성 및 이벤트 연결함
        
        화면 상단에 보스의 체력을 표시하는 프로그레스 바 생성하고,
        보스 피격 이벤트에 체력바 업데이트 콜백 연결함
        """
        # 보스 체력바 프로그레스 바 생성함
        self.health_bar = ProgressBar(
            pg.Vector2(SCREEN_SIZE.x / 2, 50),  # 위치 (화면 상단 중앙)
            pg.Vector2(800, 25),  # 크기 (가로 800, 세로 25)
            self.boss.status.health,  # 현재 체력
            0,  # 최소값
            self.boss.status.max_health  # 최대 체력
        )
        
        def on_enemy_hit(enemy):
            """
            적 피격 시 호출되는 콜백 함수 (보스만 체력바 업데이트)
            
            Args:
                enemy: 피격당한 적 객체
            """
            if not enemy is self.boss:  # 보스가 아닌 경우 무시함
                return
                
            # 보스 체력바 현재값 업데이트함
            self.health_bar.value = self.boss.status.health
            
        # 적 피격 이벤트에 콜백 연결함
        self.scene.event_bus.connect("on_enemy_hit", on_enemy_hit)


class MainGameScene(Scene):
    """
    인게임 씬 전담 클래스
    
    게임의 메인 플레이 씬을 관리하는 클래스:
    - 타일맵 로드 및 엔티티 스폰
    - 플레이어 상태 및 캐릭터 관리
    - UI 시스템 관리 (게임, 일시정지, 보스)
    - 점수 시스템 및 타이머
    - 배경 이펙트 및 사운드
    - 레벨 진행 및 전환
    - 입력 처리 (일시정지)
    
    Attributes:
        current_chapter (int): 현재 챕터 번호 (1 ~ 4)
        current_level (int): 현재 레벨 번호 (0 ~ 4)
        vignette: 화면 가장자리 비네팅 이미지 렌더러
        player_status: 플레이어 상태 관리자
        score (int): 현재 점수 (프로퍼티)
        score_down_timer: 점수 감소 타이머
        tilemap: 현재 레벨의 타일맵
        game_ui: 게임 플레이 UI 관리자
        pause_ui: 일시정지 UI 관리자
        boss_ui: 보스 UI 관리자 (보스전에만 생성)
        level_name_text: 레벨 이름 표시 텍스트 렌더러
    """
    
    def __init__(self):
        """
        메인 게임 씬 초기화함
        
        초기 챕터와 레벨을 1, 0으로 설정함
        """
        super().__init__()  # 부모 Scene 클래스 초기화함
        self.current_chapter = 1  # 시작 챕터 번호 설정함
        self.current_level = 0  # 시작 레벨 번호 설정함

    def on_scene_start(self):
        """
        씬 시작 시 모든 게임 요소들을 초기화함
        
        수행 작업들:
        - 비네팅 이미지 생성
        - 진행상황 업데이트
        - 플레이어 상태 초기화
        - 점수 시스템 설정
        - 타일맵 로드 및 엔티티 스폰
        - 이벤트 연결
        - UI 생성
        - 카메라 설정
        - 레벨 인트로
        - 배경 이펙트 생성
        """
        # 씬 시작 시 비네팅 이미지 미리 깔아둠
        vignette_image = self.app.ASSETS["ui"]["vignette"]["black"]  # 검은 비네팅 이미지
        self.vignette = ImageRenderer(
            vignette_image,  # 비네팅 이미지
            pg.Vector2(0, 0),  # 위치 (좌상단)
            anchor=pg.Vector2(0, 0)  # 앵커 포인트
        )
        
        super().on_scene_start()  # 부모 클래스 씬 시작 처리함

        # 다음 진행상황 미리 업데이트함
        self.update_next_progress()

        # 플레이어 상태 초기화 (체력 100으로 시작)
        self.player_status = PlayerStatus(start_health=100)
        self._score = 0  # 점수 내부 변수 초기화함

        # 플레이어 체력 깎이면 점수 -250 감소하도록 이벤트 연결함
        hurt_callback = lambda _: setattr(self, "score", self.score - 250)
        self.event_bus.connect("on_player_hurt", hurt_callback)

        # 1초마다 점수 15점씩 감소시키는 타이머 설정함
        def on_time_out():
            """타이머 만료 시 호출되는 콜백 함수"""
            self.score_down_timer.reset()  # 타이머 리셋함
            self.score -= 15  # 점수 15점 감소시킴
            
        self.score_down_timer = Timer(
            1,  # 1초 간격
            on_time_out,  # 콜백 함수
            auto_destroy=False  # 자동 파괴 비활성화
        )

        # 타일맵 로드 + 엔티티 스폰함
        chapter_str = str(self.current_chapter)  # 챕터 번호를 문자열로 변환함
        file_path = TILEMAP_FILES_BY_CHAPTER[chapter_str][self.current_level]  # 타일맵 파일 경로 가져옴
        self.tilemap = Tilemap(file_path)  # 타일맵 로드함
        spawn_all_entities(self.tilemap)  # 타일맵의 모든 엔티티들 스폰함

        # 적 죽으면 점수 추가하도록 이벤트 연결함
        def on_enemy_died(instance):
            """적 사망 시 호출되는 콜백 함수"""
            score_bonus = SCORE_UP_MAP[instance.__class__]  # 적 타입별 점수 보너스 가져옴
            self.score = self.score + score_bonus  # 점수 추가함
            
        self.event_bus.connect("on_enemy_died", on_enemy_died)

        # 플레이어 캐릭터 생성 + 상태 연결함
        spawn_positions = self.tilemap.get_pos_by_data("spawners_entities", 0)  # 스폰 위치들 가져옴
        spawn_pos = spawn_positions[0]  # 첫 번째 스폰 위치 사용함
        pc = PlayerCharacter(spawn_pos)  # 플레이어 캐릭터 생성함
        
        # 플레이어 상태와 캐릭터 연결함
        self.player_status.player_character = pc
        self.player_status.abilities.player_character = pc
        
        # 플레이어 죽으면 씬 재시작하도록 이벤트 연결함
        def on_player_died():
            """플레이어 사망 시 호출되는 콜백 함수"""
            if self.current_chapter == 4 and self.current_level == 0:  # 보스 레벨인 경우
                # 모든 효과음 정지함
                self.app.sound_manager.pause_all_sfx()
                # 배드 엔딩 컷씬으로 전환함
                self.app.change_scene("bad_ending_cut_scene")
            else:  # 일반 레벨인 경우
                # 메인 게임 씬 재시작함
                self.app.change_scene("main_game_scene")
                
        self.event_bus.connect("on_player_died", lambda: on_player_died())

        # UI 인스턴스 생성함
        if self.current_chapter == 4 and self.current_level == 0:  # 보스 레벨인 경우
            # 보스 배경음악 재생함
            self.app.sound_manager.play_bgm("boss_bgm")
            # 보스 UI 생성함
            self.boss_ui = BossUI(self)
            
        # 게임 UI 생성함
        self.game_ui = GameUI(self, self.player_status, self.vignette)
        # 일시정지 UI 생성함
        self.pause_ui = PauseUI(self, self.player_status)

        # 카메라 초기 위치 설정 (플레이어 중심으로)
        player_center = pg.Vector2(self.player_status.player_character.rect.center)
        self.camera.position = player_center

        # 레벨 이름 텍스트 표시 (페이드 인/아웃)
        self.level_intro()

        # 배경 이펙트 생성함
        Sky()  # 하늘 배경 생성함
        Clouds()  # 구름 이펙트 생성함
        Fog()  # 안개 이펙트 생성함

    @property
    def score(self):
        """
        현재 점수를 반환하는 getter 프로퍼티함
        
        Returns:
            int: 현재 점수값
        """
        return self._score
    
    @score.setter
    def score(self, value):
        """
        점수를 설정하는 setter 프로퍼티함
        
        점수 변경 시 자동으로 점수 증감 이벤트를 발생시킴
        점수는 0보다 작아질 수 없음
        
        Args:
            value (int): 새로운 점수값
        """
        prev = self._score  # 이전 점수 저장함
        self._score = max(value, 0)  # 점수를 0 이상으로 제한함

        # 점수 상승 / 하락 이벤트 발생시킴
        if prev < self._score:  # 점수가 증가한 경우
            self.event_bus.emit("on_score_changed", True)  # 점수 증가 이벤트 발생함
        elif prev > self._score:  # 점수가 감소한 경우
            self.event_bus.emit("on_score_changed", False)  # 점수 감소 이벤트 발생함

    def update_next_progress(self):
        """
        진행 정보 갱신함
        
        현재 레벨 진행상황을 확인하고 다음 단계로 넘어갈지 결정함:
        - 현재 레벨이 챕터 내 마지막이면 챕터를 올리고 레벨 초기화
        - 더 이상 챕터가 없으면 메인 메뉴로 전환
        - 플레이어 데이터에 진행상황 저장
        """
        chapter_str = str(self.current_chapter)  # 챕터 번호를 문자열로 변환함
        chapter_maps = TILEMAP_FILES_BY_CHAPTER.get(chapter_str)  # 현재 챕터의 맵 리스트 가져옴

        if self.current_level >= len(chapter_maps):  # 현재 레벨이 챕터의 마지막을 넘은 경우
            self.current_chapter += 1  # 다음 챕터로 넘어감
            self.current_level = 0  # 레벨을 0으로 초기화함

            if str(self.current_chapter) not in TILEMAP_FILES_BY_CHAPTER:  # 더 이상 챕터가 없는 경우
                # 메인 메뉴로 전환함
                self.app.change_scene("main_menu_scene")
                return

        # 플레이어 데이터에 진행상황 저장함 (해당 레벨을 클리어했다고 표시)
        progress_data = self.app.player_data["progress"]
        chapter_progress = progress_data[str(self.current_chapter)]
        chapter_progress[self.current_level] = True

    def level_intro(self):
        """
        레벨 시작 시 중앙에 레벨 이름 텍스트 보여주고 서서히 사라지게 처리함
        
        수행 작업:
        - 현재 레벨 이름 가져와서 텍스트 렌더러 생성
        - 페이드 인 애니메이션 (0 -> 255 알파)
        - 페이드 아웃 애니메이션 (255 -> 0 알파)
        """
        # 현재 레벨 이름 가져옴
        level_names = LEVEL_NAMES_BY_CHAPTER[str(self.current_chapter)]
        name = level_names[self.current_level]
        
        # 레벨 이름 텍스트 렌더러 생성함 (화면 중앙)
        self.level_name_text = TextRenderer(
            name,  # 레벨 이름
            SCREEN_SIZE / 2,  # 위치 (화면 중앙)
            "bold",  # 굵은 폰트
            50,  # 폰트 크기
            anchor=pg.Vector2(0.5, 0.5)  # 앵커 포인트 (중앙 정렬)
        )
        
        # 페이드 인 애니메이션 생성함 (1초 동안 0에서 255로)
        fade_in_tween = Tween(self.level_name_text, "alpha", 0, 255, 1, pt.easeInQuad)
        
        # 페이드 인 완료 후 페이드 아웃 애니메이션 실행하도록 콜백 연결함
        def start_fade_out():
            """페이드 인 완료 후 페이드 아웃 시작하는 함수"""
            Tween(self.level_name_text, "alpha", 255, 0, 2, pt.easeOutQuad)
            
        fade_in_tween.on_complete.append(lambda: start_fade_out())

    def on_enemy_died(self, enemy_instance):
        """
        적 사망 시 점수 처리함 (추가 기능 예정)
        
        Args:
            enemy_instance: 사망한 적 인스턴스
        """
        pass  # 현재는 빈 메소드 (나중에 추가 기능 구현 예정)

    def on_pause_start(self):
        """
        일시정지 시작 시 호출됨
        
        부모 클래스의 일시정지 처리 후 일시정지 UI를 표시함
        """
        super().on_pause_start()  # 부모 클래스 일시정지 처리함
        self.pause_ui.show()  # 일시정지 UI 표시함
        
    def on_pause_end(self):
        """
        일시정지 종료 시 호출됨
        
        부모 클래스의 일시정지 해제 처리 후 일시정지 UI를 숨김
        """
        super().on_pause_end()  # 부모 클래스 일시정지 해제 처리함
        self.pause_ui.hide()  # 일시정지 UI 숨김

    def handle_input(self):
        """
        입력 처리함 (TAB 누르면 일시정지 토글)
        
        현재 지원하는 입력:
        - TAB 키: 일시정지 상태 토글
        """
        # 모든 이벤트 순회하며 키보드 입력 확인함
        for event in self.app.events:
            if event.type == pg.KEYDOWN and event.key == pg.K_TAB:  # TAB 키 눌림
                # 일시정지 상태 토글함
                self.scene_paused = not self.scene_paused

    def update(self):
        """
        매 프레임 업데이트 처리함
        
        입력 처리 후 부모 클래스 업데이트 호출함
        """
        self.handle_input()  # 입력 처리함
        super().update()  # 부모 클래스 업데이트 호출함

    def on_level_end(self):
        """
        레벨 종료 처리함
        
        수행 작업들:
        - 플레이어에게 무적 상태 부여 (트랜지션 중 사망 방지)
        - 현재 점수가 하이스코어보다 높으면 하이스코어 갱신
        - 점수 초기화
        - 다음 레벨로 진행
        - 특정 레벨이면 컷씬으로 전환
        - 플레이어 데이터 저장
        """
        # 무적 상태 부여 (트랜지션 중 사망 방지용으로 99초 추가)
        self.player_status.current_invincible_time += 99
        
        # 하이스코어 갱신 확인 및 저장함
        current_high_score = self.app.player_data["scores"][str(self.current_chapter)][self.current_level]
        if self._score > current_high_score:
            # 새로운 하이스코어 저장함
            self.app.player_data["scores"][str(self.current_chapter)][self.current_level] = self._score
        
        # 점수 초기화함
        self._score = 0
        
        # 다음 레벨로 진행함
        self.current_level += 1

        # 기본적으로 메인 게임 씬으로 전환함
        target_scene_name = "main_game_scene"
        
        # 특정 레벨이면 컷씬으로 전환함
        level_key = (self.current_chapter, self.current_level)
        if level_key in CUTSCENE_MAP:
            target_scene_name = CUTSCENE_MAP[level_key]  # 해당하는 컷씬 이름 가져옴
            
        # 대상 씬으로 전환함
        self.app.change_scene(target_scene_name)
        
        # 플레이어 데이터 저장함
        self.app.save_player_data()