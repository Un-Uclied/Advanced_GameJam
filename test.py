import pygame as pg
import math
import sys

pg.init()
screen = pg.display.set_mode((1900, 1080))
clock = pg.time.Clock()

boss_pos = pg.Vector2(1900/2, 1080/2)

class OrbitBall:
    def __init__(self, angle_offset: float, radius=120):
        self.angle_offset = angle_offset
        self.angle = 0
        self.radius = radius
        self.pos = pg.Vector2(0, 0)
        self.velocity = pg.Vector2(0, 0)
        self.released = False

    def update(self, dt, base_angle, released):
        if not released:
            # 회전 상태
            self.angle = base_angle + self.angle_offset
            x = boss_pos.x + math.cos(self.angle) * self.radius
            y = boss_pos.y + math.sin(self.angle) * self.radius
            self.pos = pg.Vector2(x, y)
        else:
            if not self.released:
                # 처음 이탈할 때
                tangent = pg.Vector2(-math.sin(self.angle), math.cos(self.angle))
                self.velocity = tangent * 300
                self.released = True
            self.pos += self.velocity * dt

    def draw(self, surface):
        pg.draw.circle(surface, "red", (int(self.pos.x), int(self.pos.y)), 12)


# 설정
balls = [OrbitBall(i * (2 * math.pi / 12), 200) for i in range(12)]
for i in range(6):
    balls.append(OrbitBall(i * (2 * math.pi / 6), 100))
for i in range(3):
    balls.append(OrbitBall(i * (2 * math.pi / 3), 50))
base_angle = 0
rotation_speed = 4.0
timer = 0
release_time = 3.0
released = False

# 게임 루프
running = True
while running:
    dt = clock.tick(60) / 1000
    timer += dt
    if timer >= release_time:
        released = True

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    base_angle += rotation_speed * dt

    screen.fill("black")

    # 보스
    pg.draw.rect(screen, "blue", pg.Rect(boss_pos.x - 25, boss_pos.y - 25, 50, 50))

    # 공들 업데이트 & 그리기
    for ball in balls:
        ball.update(dt, base_angle, released)
        ball.draw(screen)

    pg.display.flip()

pg.quit()
sys.exit()
