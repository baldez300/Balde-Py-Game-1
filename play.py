import os
import random
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import pygame


WIDTH, HEIGHT = 800, 600
SHIP_SIZE = 64
PLAYER_Y = HEIGHT - SHIP_SIZE
FLIGHT_TOP = 220  # Leave space above the ship for new enemies to spawn.
STEP = 1 / 120
WAVE_POINTS = 15
SHIELD_COLOR = (100, 235, 255)
SHIELD_DROP_HIT = 5
BOSS_INTERVAL = 5
BOSS_SIZE = (160, 88)
CHARGE_TIME = 0.65
ASSETS = Path(__file__).resolve().parent


def score_path():
    if sys.platform == "darwin":
        folder = Path.home() / "Library" / "Application Support"
    else:
        folder = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share")
    return folder / "Balde Space Invaders" / "best.txt"


def read_best(path):
    try:
        return max(0, int(path.read_text()))
    except (OSError, ValueError):
        return 0


def save_best(path, score):
    temp = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if score > read_best(path):
            with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as file:
                temp = Path(file.name)
                file.write(str(score))
            temp.replace(path)
    except OSError as error:
        print(f"Could not save best score: {error}", file=sys.stderr)
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


@dataclass
class Enemy:
    x: float
    y: int
    direction: int = 1

    @classmethod
    def spawn(cls):
        return cls(random.randint(0, WIDTH - SHIP_SIZE), random.randint(50, 150))


@dataclass
class Boss:
    x: float = (WIDTH - BOSS_SIZE[0]) / 2
    health: int = WAVE_POINTS
    charging: bool = False
    triple: bool = False

    @property
    def rect(self):
        return pygame.Rect(round(self.x), 108, *BOSS_SIZE)

    def guns(self):
        offsets = (-60, 0, 60) if self.triple else (-46, 46)
        return [(self.rect.centerx + dx, self.rect.bottom) for dx in offsets]


class Audio:
    def __init__(self):
        self.muted = False
        self.effects = {}
        if pygame.mixer.get_init():
            for name in ("shot", "hit", "clear", "over"):
                self.effects[name] = pygame.mixer.Sound(str(ASSETS / "sounds" / (name + ".wav")))

    def play(self, name):
        if self.effects and not self.muted:
            self.effects[name].play()

    def toggle(self):
        self.muted = not self.muted
        if self.muted and self.effects:
            pygame.mixer.stop()


class Game:
    def __init__(self, path, on_sound=None):
        self.on_sound = on_sound or (lambda name: None)
        self.path = path
        self.best = read_best(path)
        self.new_run()
        self.state = "title"

    def new_run(self):
        self.restarts = 3
        self.restart_round()

    def restart_round(self):
        self.shielded = False
        self.score = 0
        self.wave = 1
        self.start_wave()

    def start_wave(self):
        self.state = "playing"
        self.speed = 240 + 35 * (self.wave - 1)
        self.player_x = (WIDTH - SHIP_SIZE) / 2
        self.player_y = PLAYER_Y
        self.bullet = None
        self.shield_pickup = None
        self.shield_burst = 0
        self.enemy_bolts = []
        self.charging_enemy = None
        self.fire_timer = 1.4
        self.flash = None
        self.timer = 0
        self.boss = Boss() if self.wave % BOSS_INTERVAL == 0 else None
        self.enemies = [] if self.boss else [Enemy.spawn() for _ in range(6)]

    def keydown(self, key):
        if key == pygame.K_p and self.state in ("playing", "paused"):
            self.state = "paused" if self.state == "playing" else "playing"
        elif self.state == "title" and key == pygame.K_RETURN:
            self.new_run()
        elif self.state == "over" and key == pygame.K_r and self.restarts:
            self.restarts -= 1
            self.restart_round()
        elif self.state == "over" and not self.restarts and key == pygame.K_RETURN:
            self.new_run()
        elif self.state == "playing" and key == pygame.K_SPACE and self.bullet is None:
            self.bullet = pygame.Vector2(self.player_x + 16, self.player_y - 20)
            self.on_sound("shot")

    def update_boss_attack(self, dt, hull):
        boss = self.boss
        if not boss.charging:
            # Track the ship while reloading, then lock the firing lanes.
            travel = min(250, 145 + 10 * (self.wave // BOSS_INTERVAL)) * dt
            offset = hull.centerx - boss.rect.centerx
            boss.x += max(-travel, min(travel, offset))
            boss.x = max(0, min(WIDTH - BOSS_SIZE[0], boss.x))
        if self.fire_timer > 0:
            return
        if boss.charging:
            self.enemy_bolts.extend(pygame.Vector2(gun) for gun in boss.guns())
            boss.charging = False
            boss.triple = not boss.triple
            self.fire_timer = 1.25
        elif not self.enemy_bolts:
            boss.charging = True
            self.fire_timer = CHARGE_TIME

    def update_enemy_fire(self, dt, hull):
        bolt_speed = min(440, 280 + 20 * (self.wave - 2))
        for bolt in self.enemy_bolts[:]:
            bolt.y += bolt_speed * dt
            rect = pygame.Rect(round(bolt.x) - 4, round(bolt.y), 8, 20)
            if rect.colliderect(hull):
                if self.shielded:
                    self.shielded = False
                    self.enemy_bolts.remove(bolt)
                    self.shield_burst = 0.25
                    continue
                self.state = "over"
                self.on_sound("over")
                return
            if rect.top >= HEIGHT:
                self.enemy_bolts.remove(bolt)

        self.fire_timer -= dt
        if self.boss:
            self.update_boss_attack(dt, hull)
            return
        if self.fire_timer > 0:
            return
        if self.charging_enemy is not None:
            enemy = self.charging_enemy
            self.enemy_bolts.append(pygame.Vector2(enemy.x + SHIP_SIZE / 2, enemy.y + SHIP_SIZE))
            self.charging_enemy = None
            self.fire_timer = max(0.65, 1.4 - 0.12 * (self.wave - 2))
        elif len(self.enemy_bolts) < 3:
            candidates = [enemy for enemy in self.enemies if enemy.y + SHIP_SIZE < hull.top]
            if candidates:
                self.charging_enemy = min(candidates, key=lambda enemy: abs(enemy.x - self.player_x))
                self.fire_timer = CHARGE_TIME

    def record_hit(self, target, cleared):
        self.flash = (*target.center, 0.18)
        self.on_sound("hit")
        self.score += 1
        if self.score % WAVE_POINTS == SHIELD_DROP_HIT and not self.shielded:
            self.shield_pickup = pygame.Vector2(target.center)
        if self.score > self.best:
            self.best = self.score
            save_best(self.path, self.best)
        if cleared:
            self.on_sound("clear")
            self.state = "clear"
            self.timer = 1.5
            self.shield_pickup = None
            self.enemy_bolts.clear()
            self.charging_enemy = None
            self.enemies.clear()
            self.boss = None

    def update(self, dt, direction, bullet_bounds, vertical=0):
        if self.state == "clear":
            self.timer -= dt
            if self.timer <= 0:
                self.wave += 1
                self.start_wave()
            return
        if self.state != "playing":
            return
        distance = 300 * dt
        if direction and vertical:
            distance /= 2 ** 0.5
        self.player_x = max(0, min(WIDTH - SHIP_SIZE, self.player_x + direction * distance))
        self.player_y = max(FLIGHT_TOP, min(PLAYER_Y, self.player_y + vertical * distance))
        hull = pygame.Rect(round(self.player_x), round(self.player_y), SHIP_SIZE, SHIP_SIZE).inflate(-18, -16)
        self.shield_burst = max(0, self.shield_burst - dt)
        if self.shield_pickup is not None:
            pickup = self.shield_pickup
            pickup.y += 125 * dt
            bounds = pygame.Rect(0, 0, 26, 30)
            bounds.center = round(pickup.x), round(pickup.y)
            if bounds.colliderect(hull):
                self.shielded = True
                self.shield_pickup = None
            elif bounds.top >= HEIGHT:
                self.shield_pickup = None
        if self.flash:
            x, y, duration = self.flash
            self.flash = (x, y, duration - dt) if duration > dt else None

        shot = None
        if self.bullet is not None:
            self.bullet.y -= 600 * dt
            shot = bullet_bounds.move(round(self.bullet.x), round(self.bullet.y))
            if shot.bottom <= 0:
                self.bullet = shot = None

        if self.boss and shot is not None and shot.colliderect(self.boss.rect):
            self.bullet = None
            self.boss.health -= 1
            self.record_hit(self.boss.rect, self.boss.health == 0)
            if self.state == "clear":
                return

        limit = WIDTH - SHIP_SIZE
        for i, enemy in enumerate(self.enemies):
            if enemy is not self.charging_enemy:
                enemy.x += enemy.direction * self.speed * dt
            if enemy.x < 0 or enemy.x > limit:
                enemy.x = -enemy.x if enemy.x < 0 else 2 * limit - enemy.x
                enemy.direction *= -1
                enemy.y += 40
            target = pygame.Rect(round(enemy.x), enemy.y, SHIP_SIZE, SHIP_SIZE)
            if enemy.y >= PLAYER_Y or hull.colliderect(target.inflate(-12, -12)):
                self.state = "over"
                self.on_sound("over")
                return
            if shot is not None and shot.colliderect(target):
                self.bullet = shot = None
                self.record_hit(target, (self.score + 1) % WAVE_POINTS == 0)
                if self.state == "clear":
                    return
                if enemy is self.charging_enemy:
                    self.charging_enemy = None
                    self.fire_timer = 1.4
                self.enemies[i] = Enemy.spawn()
        if self.wave >= 2:
            self.update_enemy_fire(dt, hull)


class Display:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Balde Space Invaders")
        self.background = pygame.image.load(str(ASSETS / "background.jpg")).convert()
        self.ship, self.enemy, self.bullet = [
            pygame.image.load(str(ASSETS / name)).convert_alpha()
            for name in ("player.png", "enemy.png", "bullet.png")
        ]
        self.boss_image = pygame.transform.scale(self.enemy, BOSS_SIZE)
        pygame.display.set_icon(self.ship)
        self.bullet_bounds = self.bullet.get_bounding_rect()
        self.large = pygame.font.Font(None, 68)
        self.small = pygame.font.Font(None, 32)
        self.panel = pygame.Surface((WIDTH, 166), pygame.SRCALPHA)
        self.panel.fill((8, 12, 25, 225))

    def centered(self, text, font, y, color):
        label = font.render(text, True, color)
        self.screen.blit(label, label.get_rect(center=(WIDTH // 2, y)))

    def draw(self, game, audio):
        self.screen.blit(self.background, (0, 0))
        if game.state in ("playing", "paused"):
            if game.boss:
                boss = game.boss
                self.screen.blit(self.boss_image, boss.rect)
                bar = pygame.Rect(boss.rect.left, boss.rect.top - 16, boss.rect.width, 9)
                pygame.draw.rect(self.screen, (51, 25, 46), bar)
                fill = bar.copy()
                fill.width = round(bar.width * boss.health / WAVE_POINTS)
                pygame.draw.rect(self.screen, (255, 116, 134), fill)
                pygame.draw.rect(self.screen, (244, 220, 226), bar, 1)
                if boss.charging:
                    for x, y in boss.guns():
                        pygame.draw.lines(self.screen, (255, 205, 82), False,
                                          [(x - 7, y), (x, y + 10), (x + 7, y)], 3)
            for enemy in game.enemies:
                self.screen.blit(self.enemy, (round(enemy.x), enemy.y))
            if game.charging_enemy is not None:
                enemy = game.charging_enemy
                x, y = round(enemy.x) + SHIP_SIZE // 2, enemy.y + SHIP_SIZE
                radius = 4 + round(7 * (1 - game.fire_timer / CHARGE_TIME))
                pygame.draw.circle(self.screen, (255, 205, 82), (x, y), radius, 2)
                pygame.draw.lines(self.screen, (255, 205, 82), False,
                                  [(x - 6, y + 14), (x, y + 20), (x + 6, y + 14)], 2)
            for bolt in game.enemy_bolts:
                x, y = round(bolt.x), round(bolt.y)
                pygame.draw.ellipse(self.screen, (246, 83, 57), (x - 5, y, 10, 20))
                pygame.draw.ellipse(self.screen, (255, 233, 152), (x - 2, y + 5, 4, 12))
            self.screen.blit(self.ship, (round(game.player_x), round(game.player_y)))
            if game.shield_pickup is not None:
                x, y = round(game.shield_pickup.x), round(game.shield_pickup.y)
                emblem = [(x - 13, y - 14), (x + 13, y - 14), (x + 12, y + 3),
                          (x + 7, y + 10), (x, y + 16), (x - 7, y + 10), (x - 12, y + 3)]
                pygame.draw.polygon(self.screen, (15, 76, 98), emblem)
                pygame.draw.polygon(self.screen, SHIELD_COLOR, emblem, 2)
                pygame.draw.line(self.screen, SHIELD_COLOR, (x, y - 8), (x, y + 8), 3)
            if game.shielded or game.shield_burst > 0:
                center = round(game.player_x + 32), round(game.player_y + 32)
                radius = 37 if game.shielded else 38 + int(64 * (0.25 - game.shield_burst))
                pygame.draw.circle(self.screen, SHIELD_COLOR, center, radius, 2)
            if game.bullet is not None:
                self.screen.blit(self.bullet, (round(game.bullet.x), round(game.bullet.y)))
            if game.flash:
                x, y, remaining = game.flash
                radius = 8 + int(20 * (1 - remaining / 0.18))
                pygame.draw.circle(self.screen, (255, 218, 99), (x, y), radius, 3)
        if game.state != "playing":
            if game.state == "title":
                title = "Balde Space Invaders"
                hint = "Arrows or WASD to fly     Space to fire     Enter to start"
            elif game.state == "paused":
                title = "Paused"
                hint = "P to resume     Q to quit"
            elif game.state == "clear":
                title = f"Wave {game.wave} clear!"
                hint = f"Score {game.score}     Wave {game.wave + 1} incoming"
                if (game.wave + 1) % BOSS_INTERVAL == 0:
                    hint = "Boss incoming! Watch the gold firing lanes"
                elif game.wave % BOSS_INTERVAL == 0:
                    title = "Boss defeated!"
                elif game.wave == 1:
                    hint = "Wave 2: dodge the bolts or shoot the charging enemy"
            else:
                title = "Game over"
                action = "R to restart" if game.restarts else "Enter for a new game"
                hint = f"Score {game.score}     {action}     Q to quit"
            self.screen.blit(self.panel, (0, 200))
            self.centered(title, self.large, 255, (128, 245, 210))
            self.centered(hint, self.small, 325, (255, 255, 255))
        hud = f"Score {game.score}     Best {game.best}     Wave {game.wave}     Restarts {game.restarts}"
        self.centered(hud, self.small, 23, (255, 255, 255))
        sound = "off" if audio.muted else "on"
        controls = f"P  Pause     M  Sound {sound}" if audio.effects else "P  Pause     Audio unavailable"
        if game.state in ("title", "playing", "paused"):
            self.centered(controls, self.small, 53, (210, 223, 235))
        pygame.display.flip()


def main():
    pygame.init()
    try:
        display = Display()
        audio = Audio()
        game = Game(score_path(), audio.play)
        clock = pygame.time.Clock()
        elapsed = 0
        while True:
            # Limit catch-up after a suspended or dragged window.
            elapsed += min(clock.tick(60) / 1000, 0.1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        return
                    if event.key == pygame.K_m:
                        audio.toggle()
                    game.keydown(event.key)
            keys = pygame.key.get_pressed()
            direction = bool(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - bool(keys[pygame.K_LEFT] or keys[pygame.K_a])
            vertical = bool(keys[pygame.K_DOWN] or keys[pygame.K_s]) - bool(keys[pygame.K_UP] or keys[pygame.K_w])
            while elapsed >= STEP:
                game.update(STEP, direction, display.bullet_bounds, vertical)
                elapsed -= STEP
            display.draw(game, audio)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
