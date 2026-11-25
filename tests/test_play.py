import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import play


class GameTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.game = play.Game(Path(temp.name) / "best.txt")
        self.game.keydown(pygame.K_RETURN)
        self.bounds = pygame.Rect(10, 0, 12, 32)

    def step(self):
        self.game.update(play.STEP, 0, self.bounds)

    def hit(self):
        self.game.enemies = [play.Enemy(110, 100), play.Enemy(110, 100)]
        self.game.bullet = pygame.Vector2(100, 105)
        self.step()

    def test_shot_is_required_and_consumed_once(self):
        self.game.enemies = [play.Enemy(0, 520)]
        self.step()
        self.assertEqual(self.game.score, 0)
        self.hit()
        self.step()
        self.assertEqual(self.game.score, 1)
        self.assertIsNone(self.game.bullet)
        self.assertIsNotNone(self.game.flash)

    def test_two_wave_transitions_and_persistence(self):
        for wave in (1, 2):
            speed = self.game.speed
            for _ in range(15):
                self.hit()
            self.assertEqual(self.game.state, "clear")
            self.assertFalse(self.game.enemies)
            for _ in range(182):
                self.step()
            self.assertEqual(self.game.state, "playing")
            self.assertGreater(self.game.speed, speed)
            self.assertEqual(self.game.wave, wave + 1)
            self.assertEqual(len(self.game.enemies), 6)
        self.assertEqual(play.Game(self.game.path).best, 30)

    def test_restart_after_loss(self):
        for remaining in (2, 1, 0):
            self.hit()
            self.game.wave = 3
            self.game.player_x = 0
            self.game.keydown(pygame.K_SPACE)
            self.game.enemies = [play.Enemy(10, play.PLAYER_Y)]
            self.step()
            self.assertEqual(self.game.state, "over")
            self.game.keydown(pygame.K_r)
            self.assertEqual((self.game.score, self.game.wave, self.game.restarts), (0, 1, remaining))
            self.assertIsNone(self.game.bullet)
            self.assertIsNone(self.game.flash)
            self.assertGreater(self.game.player_x, 0)
        self.game.state = "over"
        self.game.keydown(pygame.K_r)
        self.assertEqual(self.game.state, "over")
        self.game.keydown(pygame.K_RETURN)
        self.assertEqual(self.game.restarts, 3)
        self.assertEqual(self.game.best, 1)

    def test_elapsed_time(self):
        for fps in (30, 60, 120):
            self.game.start_wave()
            self.game.player_x = 0
            self.game.enemies = [play.Enemy(0, 50)]
            for _ in range(fps):
                self.game.update(1 / fps, 1, self.bounds)
            self.assertAlmostEqual(self.game.player_x, 300)
            self.assertAlmostEqual(self.game.enemies[0].x, 240)

    def test_flight_controls_and_pause(self):
        game = self.game
        game.enemies.clear()
        x, y = game.player_x, game.player_y
        game.update(0.1, 1, self.bounds, -1)
        self.assertAlmostEqual((game.player_x - x)**2 + (game.player_y - y)**2, 30**2)
        game.keydown(pygame.K_SPACE)
        self.assertEqual(game.bullet.y, game.player_y - 20)
        pos = (game.player_x, game.player_y, game.bullet.y)
        game.keydown(pygame.K_p)
        game.update(0.1, -1, self.bounds, -1)
        self.assertEqual((game.player_x, game.player_y, game.bullet.y), pos)
        game.keydown(pygame.K_p)
        for vertical, limit in ((-1, play.FLIGHT_TOP), (1, play.PLAYER_Y)):
            for _ in range(180):
                game.update(play.STEP, 0, self.bounds, vertical)
            self.assertEqual(game.player_y, limit)

    def test_sound_events_and_ship_collision(self):
        events = []
        self.game.on_sound = events.append
        self.game.keydown(pygame.K_SPACE)
        self.game.keydown(pygame.K_SPACE)
        self.game.score = 14
        self.hit()
        self.assertEqual(events, ["shot", "hit", "clear"])
        self.game.start_wave()
        self.game.player_y = 280
        self.game.enemies = [play.Enemy(self.game.player_x, 280)]
        self.step()
        self.step()
        self.assertEqual(events[-1:], ["over"])
        self.assertEqual(events.count("over"), 1)
        self.game.keydown(pygame.K_r)
        self.assertEqual(self.game.player_y, play.PLAYER_Y)

    def test_audio_playback_and_mute(self):
        pygame.mixer.init()
        self.addCleanup(pygame.mixer.quit)
        audio = play.Audio()
        for name in ("shot", "hit", "clear", "over"):
            audio.play(name)
            self.assertTrue(pygame.mixer.get_busy())
            pygame.mixer.stop()
        audio.toggle()
        audio.play("shot")
        self.assertFalse(pygame.mixer.get_busy())
        audio.toggle()
        audio.play("shot")
        self.assertTrue(pygame.mixer.get_busy())

    def prepare_enemy_fire(self, wave):
        game = self.game
        game.wave = wave
        game.start_wave()
        game.speed = 0
        game.enemies = [play.Enemy(game.player_x, 130)]
        game.fire_timer = 0
        self.step()
        return game

    def test_first_wave_never_fires(self):
        game = self.prepare_enemy_fire(1)
        for _ in range(600):
            self.step()
        self.assertIsNone(game.charging_enemy)
        self.assertFalse(game.enemy_bolts)

    def test_enemy_warning_dodge_and_pause(self):
        game = self.prepare_enemy_fire(2)
        self.assertIs(game.charging_enemy, game.enemies[0])
        game.speed = 275
        x = game.charging_enemy.x
        for _ in range(60):
            self.step()
        self.assertEqual(game.charging_enemy.x, x)
        self.assertFalse(game.enemy_bolts)
        game.keydown(pygame.K_p)
        remaining = game.fire_timer
        self.step()
        self.assertEqual(game.fire_timer, remaining)
        game.keydown(pygame.K_p)
        while game.charging_enemy is not None:
            self.step()
        self.assertEqual(len(game.enemy_bolts), 1)
        for _ in range(180):
            game.update(play.STEP, 1, self.bounds)
        self.assertEqual(game.state, "playing")
        self.assertFalse(game.enemy_bolts)

    def test_enemy_bolt_hit_and_restart(self):
        game = self.prepare_enemy_fire(2)
        for _ in range(300):
            self.step()
        self.assertEqual(game.state, "over")
        game.keydown(pygame.K_r)
        self.assertEqual(game.wave, 1)
        self.assertFalse(game.enemy_bolts)
        self.assertIsNone(game.charging_enemy)

    def test_interrupt_charge_and_clear_hazards(self):
        game = self.prepare_enemy_fire(2)
        for score in (15, 29):
            game.score = score
            enemy = game.charging_enemy
            game.bullet = pygame.Vector2(enemy.x, enemy.y + 30)
            self.step()
            self.assertIsNone(game.charging_enemy)
            self.assertFalse(game.enemy_bolts)
            if score == 15:
                game.fire_timer = 0
                self.step()
                game.enemy_bolts.append(pygame.Vector2(5, 400))
        self.assertEqual(game.state, "clear")

    def test_main_loop(self):
        batches = iter([[], [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)],
                        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)],
                        [pygame.event.Event(pygame.QUIT)]])
        with patch.object(play, "score_path", return_value=self.game.path), \
                patch.object(pygame.event, "get", side_effect=batches):
            play.main()


if __name__ == "__main__":
    unittest.main()
