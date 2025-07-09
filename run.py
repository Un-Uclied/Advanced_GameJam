# 여기서 게임 실행

'''
세줄 정리 : run.py에서 Application 싱글톤을 만들고 run() 메소드를 실행함으로써 게임이 시작됨.
Application 클래스는 pygame 초기화, 화면 설정, Time 클래스 처리, 이벤트 처리, 씬 관리 등을 담당함.
각 씬들에서 Objects와 Components를 업데이트하고 그리며, 게임 로직을 처리함.
'''

if __name__ == "__main__":
    from modules.application import Application
    Application().run() # 여기서 Application() 싱글톤 만들고 run() 메소드 실행