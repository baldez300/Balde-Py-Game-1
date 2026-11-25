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

    def test_main_loop(self):
        batches = iter([[], [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)],
                        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)],
                        [pygame.event.Event(pygame.QUIT)]])
        with patch.object(play, "score_path", return_value=self.game.path), \
                patch.object(pygame.event, "get", side_effect=batches):
            play.main()


if __name__ == "__main__":
    unittest.main()
