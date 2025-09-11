from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.core.window import Window
import random


# Player class
class Player(Image):
    def __init__(self, img, **kwargs):
        super().__init__(**kwargs)
        self.source = img
        self.size_hint = (None, None)
        self.size = (64, 64)
        self.pos = (100, 100)


# Enemy class
class Enemy(Image):
    def __init__(self, img, x, y, **kwargs):
        super().__init__(**kwargs)
        self.source = img
        self.size_hint = (None, None)
        self.size = (64, 64)
        self.pos = (x, y)


class Game(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Window size
        Window.size = (800, 600)

        # Backgrounds
        self.past_bg = Image(source="past_bg.png", allow_stretch=True, keep_ratio=False,
                             size_hint=(0.5, 1), pos_hint={"x": 0, "y": 0})
        self.future_bg = Image(source="future_bg.png", allow_stretch=True, keep_ratio=False,
                               size_hint=(0.5, 1), pos_hint={"x": 0.5, "y": 0})

        self.add_widget(self.past_bg)
        self.add_widget(self.future_bg)

        # Players
        self.past_player = Player("past.png.png", pos=(100, 200))
        self.future_player = Player("future.png.png", pos=(500, 200))
        self.add_widget(self.past_player)
        self.add_widget(self.future_player)

        # Enemies list
        self.enemies = []

        # Game loop
        Clock.schedule_interval(self.update, 1 / 60)
        Clock.schedule_interval(self.spawn_enemy, 3)  # spawn every 3s

    def spawn_enemy(self, dt):
        """Spawn enemy in past and synced monster in future"""
        y = random.randint(100, 400)
        enemy = Enemy("enemy.png", 200, y)
        monster = Enemy("monster.png", 600, y)

        self.enemies.append((enemy, monster))
        self.add_widget(enemy)
        self.add_widget(monster)

    def update(self, dt):
        """Game update loop"""
        for enemy, monster in self.enemies:
            enemy.x -= 2  # move left
            monster.x -= 2  # move left

            # Remove off-screen enemies
            if enemy.x < -100:
                self.remove_widget(enemy)
                self.remove_widget(monster)
                self.enemies.remove((enemy, monster))
                break


class TimeSwapApp(App):
    def build(self):
        return Game()


if __name__ == "__main__":
    TimeSwapApp().run()

