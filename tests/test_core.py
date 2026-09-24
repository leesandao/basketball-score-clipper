from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from collections import deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


clip_events = load_script("clip_events")
fixed_camera = load_script("detect_fixed_camera")


class ClipEventTests(unittest.TestCase):
    def setUp(self) -> None:
        self.args = argparse.Namespace(pre_roll=1.5, post_roll=1.5, fallback_lead=4.0)

    def test_release_time_boundary(self) -> None:
        self.assertEqual(
            clip_events.event_bounds(
                {"score_time": 10.0, "release_time": 7.0}, self.args
            ),
            (5.5, 11.5),
        )

    def test_fallback_clamps_start(self) -> None:
        self.assertEqual(
            clip_events.event_bounds({"score_time": 2.0}, self.args), (0.0, 3.5)
        )

    def test_auto_encoder_prefers_nvenc(self) -> None:
        self.assertEqual(
            clip_events.choose_encoder("auto", {"libx264", "h264_nvenc"}),
            "h264_nvenc",
        )

    def test_output_name_is_sanitized(self) -> None:
        self.assertEqual(clip_events.sanitize("Game 1 / score"), "Game-1-score")


class CrossingTests(unittest.TestCase):
    def test_downward_crossing_is_candidate(self) -> None:
        history = deque(
            [
                {"time": 1.0, "x": 100.0, "y": 80.0, "quality": 0.8},
                {"time": 1.1, "x": 101.0, "y": 95.0, "quality": 0.8},
                {"time": 1.2, "x": 100.0, "y": 115.0, "quality": 0.8},
                {"time": 1.3, "x": 100.0, "y": 135.0, "quality": 0.8},
            ]
        )
        evidence = fixed_camera.crossing_evidence(
            history, history[-1], 100.0, 105.0, 40.0, 20.0, 1.2
        )
        self.assertIsNotNone(evidence)
        assert evidence is not None
        self.assertEqual(evidence[2], 1.0)

    def test_side_pass_is_rejected(self) -> None:
        history = deque(
            [
                {"time": 1.0, "x": 20.0, "y": 80.0, "quality": 0.8},
                {"time": 1.2, "x": 20.0, "y": 135.0, "quality": 0.8},
            ]
        )
        self.assertIsNone(
            fixed_camera.crossing_evidence(
                history, history[-1], 100.0, 105.0, 40.0, 20.0, 1.2
            )
        )


class ProjectInitTests(unittest.TestCase):
    def test_initializer_is_non_destructive(self) -> None:
        script = ROOT / "scripts" / "init_project.py"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subprocess.run(
                [sys.executable, str(script), "--root", str(root)], check=True
            )
            config = root / "basketball-score-clipper.json"
            original = json.loads(config.read_text(encoding="utf-8"))
            config.write_text('{"custom": true}\n', encoding="utf-8")
            subprocess.run(
                [sys.executable, str(script), "--root", str(root)], check=True
            )
            self.assertEqual(
                json.loads(config.read_text(encoding="utf-8")), {"custom": True}
            )
            self.assertIn("directories", original)


if __name__ == "__main__":
    unittest.main()
