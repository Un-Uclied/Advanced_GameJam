import random

class WanderAI:
    def __init__(self, entity, move_speed=1.5, change_interval=1.2):
        self.entity = entity
        self.direction = random.choice([-1, 0, 1])
        self.move_speed = move_speed
        self.change_timer = 0.0
        self.change_interval = change_interval
        self.prevent_random_change_timer = 0.0

    def on_update(self):
        dt = self.entity.app.dt
        
        if self.prevent_random_change_timer > 0:
            self.prevent_random_change_timer -= dt
        else:
            self.change_timer += dt
            if self.change_timer >= self.change_interval:
                self.change_timer = 0
                self.direction = random.choice([-1, 0, 1])

        self.entity.velocity.x = self.direction * self.move_speed * 100

    def handle_collision_or_fall(self, event_type):
        if event_type == "fall_left":
            self.direction = 1
        elif event_type == "fall_right":
            self.direction = -1
        elif event_type == "hit_left":
            self.direction = 1
        elif event_type == "hit_right":
            self.direction = -1
        self.prevent_random_change_timer = 0.6
