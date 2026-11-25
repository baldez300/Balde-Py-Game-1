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
STEP = 1 / 120
WAVE_POINTS = 15
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


class Game:
    def __init__(self, path):
        self.path = path
        self.best = read_best(path)
        self.new_run()
        self.state = "title"

    def new_run(self):
        self.restarts = 3
        self.restart_round()

    def restart_round(self):
        self.score = 0
        self.wave = 1
        self.start_wave()

    def start_wave(self):
        self.state = "playing"
        self.speed = 240 + 35 * (self.wave - 1)
        self.player_x = (WIDTH - SHIP_SIZE) / 2
        self.bullet = None
        self.flash = None
        self.timer = 0
        self.enemies = [Enemy.spawn() for _ in range(6)]

    def keydown(self, key):
        if self.state == "title" and key == pygame.K_RETURN:
            self.new_run()
        elif self.state == "over" and key == pygame.K_r and self.restarts:
            self.restarts -= 1
            self.restart_round()
        elif self.state == "over" and not self.restarts and key == pygame.K_RETURN:
            self.new_run()
        elif self.state == "playing" and key == pygame.K_SPACE and self.bullet is None:
            self.bullet = pygame.Vector2(self.player_x + 16, PLAYER_Y - 20)

    def update(self, dt, direction, bullet_bounds):
        if self.state == "clear":
            self.timer -= dt
            if self.timer <= 0:
                self.wave += 1
                self.start_wave()
            return
        if self.state != "playing":
            return
        self.player_x = max(0, min(WIDTH - SHIP_SIZE, self.player_x + direction * 300 * dt))
        if self.flash:
            x, y, duration = self.flash
            self.flash = (x, y, duration - dt) if duration > dt else None

        shot = None
        if self.bullet is not None:
            self.bullet.y -= 600 * dt
            shot = bullet_bounds.move(round(self.bullet.x), round(self.bullet.y))
            if shot.bottom <= 0:
                self.bullet = shot = None

        limit = WIDTH - SHIP_SIZE
        for i, enemy in enumerate(self.enemies):
            enemy.x += enemy.direction * self.speed * dt
            if enemy.x < 0 or enemy.x > limit:
                enemy.x = -enemy.x if enemy.x < 0 else 2 * limit - enemy.x
                enemy.direction *= -1
                enemy.y += 40
            if enemy.y >= PLAYER_Y:
                self.state = "over"
                return
            target = pygame.Rect(round(enemy.x), enemy.y, SHIP_SIZE, SHIP_SIZE)
            if shot is not None and shot.colliderect(target):
                self.bullet = shot = None
                self.flash = (*target.center, 0.18)
                self.score += 1
                if self.score > self.best:
                    self.best = self.score
                    save_best(self.path, self.best)
                if self.score % WAVE_POINTS == 0:
                    self.state = "clear"
                    self.timer = 1.5
                    self.enemies.clear()
                    return
                self.enemies[i] = Enemy.spawn()


class Display:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Balde Space Invaders")
        self.background = pygame.image.load(str(ASSETS / "background.jpg")).convert()
        self.ship, self.enemy, self.bullet = [
            pygame.image.load(str(ASSETS / name)).convert_alpha()
            for name in ("player.png", "enemy.png", "bullet.png")
        ]
        pygame.display.set_icon(self.ship)
        self.bullet_bounds = self.bullet.get_bounding_rect()
        self.large = pygame.font.Font(None, 68)
        self.small = pygame.font.Font(None, 32)
        self.panel = pygame.Surface((WIDTH, 166), pygame.SRCALPHA)
        self.panel.fill((8, 12, 25, 225))

    def centered(self, text, font, y, color):
        label = font.render(text, True, color)
        self.screen.blit(label, label.get_rect(center=(WIDTH // 2, y)))

    def draw(self, game):
        self.screen.blit(self.background, (0, 0))
        if game.state == "playing":
            for enemy in game.enemies:
                self.screen.blit(self.enemy, (round(enemy.x), enemy.y))
            self.screen.blit(self.ship, (round(game.player_x), PLAYER_Y))
            if game.bullet is not None:
                self.screen.blit(self.bullet, (round(game.bullet.x), round(game.bullet.y)))
            if game.flash:
                x, y, remaining = game.flash
                radius = 8 + int(20 * (1 - remaining / 0.18))
                pygame.draw.circle(self.screen, (255, 218, 99), (x, y), radius, 3)
        else:
            if game.state == "title":
                title = "Balde Space Invaders"
                hint = "Left / Right to move     Space to fire     Enter to start"
            elif game.state == "clear":
                title = f"Wave {game.wave} clear!"
                hint = f"Score {game.score}     Wave {game.wave + 1} incoming"
            else:
                title = "Game over"
                action = "R to restart" if game.restarts else "Enter for a new game"
                hint = f"Score {game.score}     {action}     Q to quit"
            self.screen.blit(self.panel, (0, 200))
            self.centered(title, self.large, 255, (128, 245, 210))
            self.centered(hint, self.small, 325, (255, 255, 255))
        hud = f"Score {game.score}     Best {game.best}     Wave {game.wave}     Restarts {game.restarts}"
        self.centered(hud, self.small, 23, (255, 255, 255))
        pygame.display.flip()


def main():
    pygame.init()
    try:
        display = Display()
        game = Game(score_path())
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
                    game.keydown(event.key)
            keys = pygame.key.get_pressed()
            direction = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
            while elapsed >= STEP:
                game.update(STEP, direction, display.bullet_bounds)
                elapsed -= STEP
            display.draw(game)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
