'''

pip uninstall pygame (만약 이미 파이게임이 깔려있다면 지우고)
pip install pygame-ce (파이게임 커뮤니티 에디션으로 다시 깔기)

'''
#왜 파이게임을 지우고 파이게임 커뮤니티 에디션을 깔냐? -> 커뮤니티 에디션이든 아니든 import pygame를 해서 다른걸 쓸려면 무조건 하나만 깔려있어야함;
#왜 커뮤니티 에디션을 쓰냐? -> 이게 성능이 더 좋고, (40%정도?) FRect라는 객체가 있는데, 일반 버전엔 FRect가 없음. 그냥 Rect쓰면 충돌판정 나락가서 FRect쓰는거;

from scripts.app import App
App('main_game_scene').run()