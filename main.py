from kivy.config import Config
Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'resizable', False)

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.graphics import Rectangle
from kivy.core.window import Window
import random
import os

ASSET_DIR = os.path.dirname(os.path.abspath(__file__))

def img(path):
    return os.path.join(ASSET_DIR, path)

# Background widget
class Background(Widget):
    def __init__(self, img_path, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self.rect = Rectangle(source=img(img_path), pos=(0, 0), size=Window.size)
        self.bind(size=self.update_graphics, pos=self.update_graphics)

    def update_graphics(self, *args):
        self.rect.size = Window.size
        self.rect.pos = (0, 0)

    def set_image(self, img_path):
        self.rect.source = img(img_path)

# Player widget
class Player(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (100, 100)
        self.x = Window.width // 2
        self.y = 100
        self.speed_x = 0
        self.speed_y = 0
        self.gravity = -1
        self.jump_strength = 20
        with self.canvas:
            self.rect = Rectangle(source=img("past.png.png"), pos=self.pos, size=self.size)
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def set_image(self, img_path):
        self.rect.source = img(img_path)

    def move_left(self):
        self.speed_x = -5

    def move_right(self):
        self.speed_x = 5

    def stop(self):
        self.speed_x = 0

    def jump(self):
        if self.y <= 100:
            self.speed_y = self.jump_strength

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += self.gravity
        if self.y < 100:
            self.y = 100
            self.speed_y = 0

# Enemy widget
class Enemy(Widget):
    def __init__(self, x, y, img_path="enemy.png", **kwargs):
        super().__init__(**kwargs)
        self.size = (80, 80)
        self.x = x
        self.y = y
        with self.canvas:
            self.rect = Rectangle(source=img(img_path), pos=self.pos, size=self.size)
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def set_image(self, img_path):
        self.rect.source = img(img_path)

# Main game widget
class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # World state
        self.is_past = True

        # Background
        self.bg = Background("past_bg.png")
        self.add_widget(self.bg)

        # Player
        self.player = Player()
        self.add_widget(self.player)

        # Enemy list
        self.enemies = []

        Clock.schedule_interval(self.update, 1 / 60)
        Clock.schedule_interval(self.spawn_enemy, 3)

    def spawn_enemy(self, dt):
        x = random.randint(100, Window.width - 100)
        y = 100
        img_file = "enemy.png" if self.is_past else "monster.png"
        enemy = Enemy(x, y, img_file)
        self.enemies.append(enemy)
        self.add_widget(enemy)

    def update(self, dt):
        self.player.update()
        for enemy in self.enemies[:]:
            if self.player.collide_widget(enemy):
                print("Enemy killed!")
                self.remove_widget(enemy)
                self.enemies.remove(enemy)

    def toggle_world(self):
        self.is_past = not self.is_past
        if self.is_past:
            self.bg.set_image("past_bg.png")
            self.player.set_image("past.png.png")
            for e in self.enemies:
                e.set_image("enemy.png")
        else:
            self.bg.set_image("future_bg.png")
            self.player.set_image("future.png.png")
            for e in self.enemies:
                e.set_image("monster.png")

# Game layout with buttons
class GameLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = GameWidget()
        self.add_widget(self.game)

        # Controls
        btn_size = (100, 100)

        left_btn = Button(text="◀", size=btn_size, pos=(20, 20))
        left_btn.bind(on_press=lambda x: self.game.player.move_left())
        left_btn.bind(on_release=lambda x: self.game.player.stop())
        self.add_widget(left_btn)

        right_btn = Button(text="▶", size=btn_size, pos=(140, 20))
        right_btn.bind(on_press=lambda x: self.game.player.move_right())
        right_btn.bind(on_release=lambda x: self.game.player.stop())
        self.add_widget(right_btn)

        jump_btn = Button(text="⮝", size=btn_size, pos=(Window.width - 120, 20))
        jump_btn.bind(on_press=lambda x: self.game.player.jump())
        self.add_widget(jump_btn)

        swap_btn = Button(text="🌀", size=btn_size, pos=(Window.width//2 - 50, 20))
        swap_btn.bind(on_press=lambda x: self.game.toggle_world())
        self.add_widget(swap_btn)

# App class
class TimeSwapApp(App):
    def build(self):
        return GameLayout()

if __name__ == '__main__':
    TimeSwapApp().run()

