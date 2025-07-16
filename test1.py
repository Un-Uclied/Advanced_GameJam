import arcade

WIDTH = 800
HEIGHT = 600
TITLE = "Arcade FPS Test"

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(WIDTH, HEIGHT, TITLE)
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        fps_text = f"FPS: {arcade.get_fps():.2f}"
        arcade.draw_text(fps_text, 10, HEIGHT - 30, arcade.color.WHITE, 20)

    def on_update(self, delta_time):
        pass  # 여기에 업데이트 로직 넣으면 됨

if __name__ == "__main__":
    window = MyGame()
    arcade.run()
