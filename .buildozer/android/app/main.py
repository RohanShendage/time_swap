from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock
from kivy.core.window import Window

Window.clearcolor = (0, 0, 0, 1)  # black background
Window.fullscreen = True

class Player(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0, 1, 0, 1)  # green player
            self.rect = Rectangle(pos=self.pos, size=(50, 50))
        self.size = (50, 50)
        self.velocity_y = 0

    def move(self):
        # Apply gravity
        self.velocity_y -= 1
        new_y = self.y + self.velocity_y
        if new_y < 0:
            new_y = 0
            self.velocity_y = 0
        self.y = new_y
        self.rect.pos = (self.x, self.y)

    def jump(self):
        if self.y == 0:
            self.velocity_y = 20

class Enemy(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(1, 0, 0, 1)  # red enemy
            self.rect = Rectangle(pos=self.pos, size=(40, 40))
        self.size = (40, 40)

    def move(self):
        self.x -= 5
        if self.x < -self.width:
            self.x = Window.width
        self.rect.pos = (self.x, self.y)

class Game(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = Player(pos=(100, 0))
        self.enemy = Enemy(pos=(Window.width, 0))
        self.add_widget(self.player)
        self.add_widget(self.enemy)
        Clock.schedule_interval(self.update, 1/60)

    def update(self, dt):
        self.player.move()
        self.enemy.move()
        # Collision check
        if self.player.collide_widget(self.enemy):
            print("Game Over")

    def on_touch_down(self, touch):
        if touch.x < Window.width / 2:
            self.player.x -= 30  # move left
        else:
            self.player.x += 30  # move right
        self.player.rect.pos = (self.player.x, self.player.y)

    def on_touch_up(self, touch):
        self.player.jump()  # jump when releasing touch

class TimeSwapApp(App):
    def build(self):
        return Game()

if __name__ == "__main__":
    TimeSwapApp().run()

