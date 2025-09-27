import pygame
import sys
import random
from pathlib import Path

# ---------- CONFIG ----------
WIDTH, HEIGHT = 960, 640
FPS = 60
PLAYER_SIZE = (50, 50)
ENEMY_SIZE = (40, 40)
BULLET_SIZE = (10, 5)
ENEMY_SPEED = 3
BULLET_SPEED = 8

ASSET_FILES = {
    "past_player": "past.png.png",
    "future_player": "future.png.png",
    "enemy": "enemy.png",
    "monster": "monster.png",
    "past_bg": "past_bg.png",
    "future_bg": "future_bg.png",
}

# ---------- INIT ----------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Time Swap Survivor")
clock = pygame.time.Clock()
half_h = HEIGHT // 2

# Utility: safe image load with helpful error
def load_image(name, alpha=True):
    path = Path(name)
    if not path.exists():
        raise FileNotFoundError(f"Required image not found: {name}\nPut it in the game folder.")
    img = pygame.image.load(str(path))
    return img.convert_alpha() if alpha else img.convert()

# ---------- LOAD ASSETS ----------
try:
    past_img = pygame.transform.scale(load_image(ASSET_FILES["past_player"]), PLAYER_SIZE)
    future_img = pygame.transform.scale(load_image(ASSET_FILES["future_player"]), PLAYER_SIZE)

    enemy_img = pygame.transform.scale(load_image(ASSET_FILES["enemy"]), ENEMY_SIZE)
    monster_img = pygame.transform.scale(load_image(ASSET_FILES["monster"]), ENEMY_SIZE)

    past_bg = pygame.transform.scale(load_image(ASSET_FILES["past_bg"], alpha=False), (WIDTH, half_h))
    future_bg = pygame.transform.scale(load_image(ASSET_FILES["future_bg"], alpha=False), (WIDTH, half_h))
except Exception as e:
    pygame.quit()
    print(e)
    sys.exit(1)

# Bullet surface (keeps alpha)
bullet_img = pygame.Surface(BULLET_SIZE, pygame.SRCALPHA)
bullet_img.fill((255, 230, 0))

# ---------- GAME STATE ----------
playerPast = pygame.Rect(120, half_h // 2 - PLAYER_SIZE[1] // 2, *PLAYER_SIZE)
playerFuture = pygame.Rect(120, half_h + half_h // 2 - PLAYER_SIZE[1] // 2, *PLAYER_SIZE)
speed = 4

past_hp = 5
future_hp = 5

pairs = []      # list of {"past": enemy_dict, "future": enemy_dict}
bullets = []    # list of {"rect": Rect, "lane": "past"|"future"}
explosions = [] # list of {"pos":(x,y), "radius":..., "alpha":...}

enemy_timer = 0
spawn_interval_frames = 60  # ~1s at 60 FPS

font = pygame.font.SysFont(None, 30)

# ---------- FUNCTIONS ----------
def spawn_enemies():
    x = WIDTH
    y_rel = random.randint(0, half_h - ENEMY_SIZE[1])
    y_past = y_rel
    y_future = y_rel + half_h

    past_enemy = {"rect": pygame.Rect(x, y_past, *ENEMY_SIZE), "img": enemy_img, "hp": 1, "lane": "past"}
    future_enemy = {"rect": pygame.Rect(x, y_future, *ENEMY_SIZE), "img": monster_img, "hp": 2, "lane": "future"}
    pairs.append({"past": past_enemy, "future": future_enemy})

def create_explosion(x, y, color=(255, 200, 50)):
    explosions.append({"pos": (x, y), "radius": 8, "alpha": 230, "color": color})

# ---------- MAIN LOOP ----------
running = True
while running:
    dt = clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # Past shoots
                rect = pygame.Rect(playerPast.right, playerPast.centery - BULLET_SIZE[1] // 2, *BULLET_SIZE)
                bullets.append({"rect": rect, "lane": "past"})
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):  # Future shoots
                rect = pygame.Rect(playerFuture.right, playerFuture.centery - BULLET_SIZE[1] // 2, *BULLET_SIZE)
                bullets.append({"rect": rect, "lane": "future"})

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]: playerPast.x -= speed
    if keys[pygame.K_d]: playerPast.x += speed
    if keys[pygame.K_w]: playerPast.y -= speed
    if keys[pygame.K_s]: playerPast.y += speed
    if keys[pygame.K_LEFT]: playerFuture.x -= speed
    if keys[pygame.K_RIGHT]: playerFuture.x += speed
    if keys[pygame.K_UP]: playerFuture.y -= speed
    if keys[pygame.K_DOWN]: playerFuture.y += speed

    playerPast.clamp_ip(pygame.Rect(0, 0, WIDTH, half_h))
    playerFuture.clamp_ip(pygame.Rect(0, half_h, WIDTH, half_h))

    enemy_timer += 1
    if enemy_timer > spawn_interval_frames:
        spawn_enemies()
        enemy_timer = 0

    for pair in pairs[:]:
        pair["past"]["rect"].x -= ENEMY_SPEED
        pair["future"]["rect"].x -= ENEMY_SPEED
        if pair["past"]["rect"].right < 0 and pair["future"]["rect"].right < 0:
            pairs.remove(pair)

    for b in bullets[:]:
        b["rect"].x += BULLET_SPEED
        if b["rect"].left > WIDTH:
            bullets.remove(b)

    for b in bullets[:]:
        for pair in pairs[:]:
            target = pair[b["lane"]]
            if b["rect"].colliderect(target["rect"]):
                target["hp"] -= 1
                try: bullets.remove(b)
                except ValueError: pass
                if b["lane"] == "past" and target["hp"] <= 0:
                    create_explosion(*target["rect"].center, color=(200,200,255))
                    create_explosion(*pair["future"]["rect"].center, color=(255,160,80))
                    pairs.remove(pair)
                elif b["lane"] == "future" and target["hp"] <= 0:
                    create_explosion(*target["rect"].center, color=(255,160,80))
                    pairs.remove(pair)
                break

    for pair in pairs[:]:
        if playerPast.colliderect(pair["past"]["rect"]):
            past_hp -= 1
            create_explosion(*pair["past"]["rect"].center, color=(200,200,255))
            pairs.remove(pair)
        elif playerFuture.colliderect(pair["future"]["rect"]):
            future_hp -= 1
            create_explosion(*pair["future"]["rect"].center, color=(255,160,80))
            pairs.remove(pair)

    for exp in explosions[:]:
        exp["radius"] += 2
        exp["alpha"] -= 18
        if exp["alpha"] <= 0 or exp["radius"] > 60:
            explosions.remove(exp)

    screen.blit(past_bg, (0, 0))
    screen.blit(future_bg, (0, half_h))
    pygame.draw.rect(screen, (80,80,80), (0, half_h - 2, WIDTH, 4))

    screen.blit(past_img, playerPast.topleft)
    screen.blit(future_img, playerFuture.topleft)

    for pair in pairs:
        screen.blit(pair["past"]["img"], pair["past"]["rect"].topleft)
        screen.blit(pair["future"]["img"], pair["future"]["rect"].topleft)

    for b in bullets:
        screen.blit(bullet_img, b["rect"].topleft)

    for exp in explosions:
        surf_size = int(exp["radius"]*2)
        surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        c = exp.get("color", (255,200,50))
        surf_col = (c[0], c[1], c[2], max(0, int(exp["alpha"])))
        pygame.draw.circle(surf, surf_col, (surf_size//2, surf_size//2), int(exp["radius"]))
        screen.blit(surf, (exp["pos"][0]-surf_size//2, exp["pos"][1]-surf_size//2))

    screen.blit(font.render(f"Past HP: {past_hp}", True, (255,255,255)), (10, 10))
    screen.blit(font.render(f"Future HP: {future_hp}", True, (255,255,255)), (10, half_h+10))

    if past_hp <= 0 or future_hp <= 0:
        winner = "Future" if past_hp <= 0 else "Past"
        go_text = font.render(f"GAME OVER - {winner} wins!  Press R to restart or Q to quit.", True, (255, 200, 50))
        screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2 - 10))
        pygame.display.flip()
        waiting = True
        while waiting:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    waiting = False
                    running = False
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_r:
                        past_hp, future_hp = 5, 5
                        pairs.clear(); bullets.clear(); explosions.clear()
                        enemy_timer = 0
                        waiting = False
                    if ev.key == pygame.K_q:
                        waiting = False
                        running = False
            clock.tick(15)
        continue

    pygame.display.flip()

pygame.quit()
sys.exit()

