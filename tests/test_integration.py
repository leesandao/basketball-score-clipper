"""Media-level regression checks; skipped when optional local tools are absent."""
from __future__ import annotations

import importlib.util
import csv
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'requires FFmpeg')
class MediaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
                        'testsrc2=size=96x160:rate=10:duration=3',
                        '-c:v', 'libx264', str(self.source)], check=True)

    def run_script(self, script, *args):
        return subprocess.run([sys.executable, str(ROOT / 'scripts' / script),
                               *map(str, args)], capture_output=True, text=True)

    def test_reviewed_make_exports_and_input_manifest_collision_is_refused(self):
        events = self.root / 'events.json'
        events.write_text(json.dumps({'version': 1, 'source': str(self.source), 'events': [
            {'id': 'accepted', 'result': 'made', 'confidence': .2, 'score_time': 1.5,
             'clip_start': .5, 'clip_end': 2.5, 'review': {'status': 'accepted'}}]}))
        out = self.root / 'clips'
        result = self.run_script('clip_events.py', '--events', events, '--output-dir', out,
                                 '--encoder', 'libx264')
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads(result.stdout)
        self.assertEqual(manifest['clips'][0]['status'], 'created')
        self.assertTrue(Path(manifest['clips'][0]['output']).is_file())
        original = self.source.read_bytes()
        refused = self.run_script('clip_events.py', '--events', events, '--output-dir', out,
                                  '--encoder', 'libx264', '--manifest', self.source, '--overwrite')
        self.assertNotEqual(refused.returncode, 0)
        self.assertEqual(self.source.read_bytes(), original)

    def test_proxy_time_mapping_and_no_overwrite(self):
        out = self.root / 'review'
        result = self.run_script('prepare_review.py', '--input', self.source, '--output-dir', out,
                                 '--start', 1, '--duration', 1)
        self.assertEqual(result.returncode, 0, result.stderr)
        mapping = json.loads(result.stdout)
        self.assertEqual(mapping['source_start'], 1)
        self.assertAlmostEqual(mapping['proxy_duration'], 1, delta=.1)
        original = (out / 'review.mp4').read_bytes()
        refused = self.run_script('prepare_review.py', '--input', self.source, '--output-dir', out)
        self.assertNotEqual(refused.returncode, 0)
        self.assertEqual((out / 'review.mp4').read_bytes(), original)

    @unittest.skipUnless(importlib.util.find_spec('cv2'), 'requires OpenCV')
    def test_detector_cannot_replace_source(self):
        original = self.source.read_bytes()
        result = self.run_script('detect_fixed_camera.py', '--input', self.source,
                                 '--hoop-roi', '20,20,30,10', '--output', self.source, '--overwrite')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.source.read_bytes(), original)

    @unittest.skipUnless(importlib.util.find_spec('cv2'), 'requires OpenCV')
    def test_vfr_trace_uses_presentation_times(self):
        import cv2
        import numpy as np
        frames = []
        for index in range(30):
            frame = np.zeros((160, 96, 3), dtype=np.uint8)
            cv2.circle(frame, (45, 30 + index * 2), 5, (0, 128, 255), -1)
            frames.append(frame.tobytes())
        source = self.root / 'vfr.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24',
                        '-s', '96x160', '-r', '10', '-i', '-', '-vf',
                        r'setpts=if(lt(N\,10)\,N\,10+2*(N-10))/(10*TB)',
                        '-fps_mode', 'vfr', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                        str(source)], input=b''.join(frames), check=True)
        trace = self.root / 'trace.csv'
        result = self.run_script('detect_fixed_camera.py', '--input', source,
                                 '--hoop-roi', '35,75,25,10', '--output', self.root / 'events.json',
                                 '--trace-csv', trace)
        self.assertEqual(result.returncode, 0, result.stderr)
        timestamps = json.loads(subprocess.check_output([
            'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_frames',
            '-show_entries', 'frame=best_effort_timestamp_time', '-of', 'json', str(source)]))
        with trace.open() as handle:
            points = list(csv.DictReader(handle))
        self.assertGreater(len(points), 10)
        for point in points:
            expected = float(timestamps['frames'][int(point['frame'])]['best_effort_timestamp_time'])
            self.assertAlmostEqual(float(point['time']), expected, places=5)


if __name__ == '__main__':
    unittest.main()
