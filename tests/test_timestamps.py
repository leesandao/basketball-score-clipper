import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('timestamps', Path(__file__).resolve().parents[1] / 'scripts/export_timestamps.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TimestampTests(unittest.TestCase):
    def test_entry_frame_takes_precedence_and_pending_stays_separate(self):
        events = {'source': 'game.mp4', 'events': [
            {'id': 'candidate', 'score_time': 10, 'result': 'made_candidate'},
            {'id': 'accepted', 'score_time': 71, 'basket_entry_time': 70.7,
             'entry_time_basis': 'observed_frame', 'result': 'made', 'review': {'status': 'accepted'}},
            {'id': 'rejected', 'score_time': 30, 'result': 'made', 'review': {'status': 'rejected'}}]}
        text = module.render(events)
        self.assertIn('00:01:10.700', text)
        self.assertNotIn('00:00:10.000', text)
        self.assertIn('已确认 1 个；待复核 1 个', text)
        self.assertIn('00:00:10.000', module.render(events, True))

    def test_legacy_confirmation_is_not_claimed_as_entry_frame(self):
        text = module.render({'source': 'a.mp4', 'events': [
            {'id': 'old', 'result': 'made', 'score_time': 70.933,
             'review': {'status': 'accepted'}}]})
        self.assertIn('确认时刻，入筐时间待精定位', text)

    def test_timecode_hour_and_rounding(self):
        self.assertEqual(module.timecode(3599.9998), '01:00:00.000')
        for value in (True, -1, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                module.timecode(value)

    def test_srt_uses_source_timeline_and_clamps_to_duration(self):
        document = {'source': 'game.mp4', 'events': [
            {'id': '1', 'result': 'made', 'score_time': 72,
             'basket_entry_time': 71.75, 'entry_time_basis': 'observed_frame',
             'review': {'status': 'accepted'}}]}
        text = module.render_srt(document, 72)
        self.assertIn('00:01:11,750 --> 00:01:12,000', text)
        self.assertIn('进球 001', text)
        with self.assertRaises(ValueError):
            module.render_srt(document, 71)
        del document['events'][0]['basket_entry_time']
        with self.assertRaises(ValueError):
            module.render_srt(document, 80)

    def test_srt_does_not_merge_independent_video_timelines(self):
        document = {'events': [{'id': str(i), 'source': source, 'result': 'made',
                               'score_time': 2, 'basket_entry_time': 1,
                               'review': {'status': 'accepted'}}
                              for i, source in enumerate(('a.mp4', 'b.mp4'))]}
        with self.assertRaises(ValueError):
            module.render_srt(document, 10)
        self.assertEqual(module.render_srt(document, 10, 'a.mp4').count('-->'), 1)


if __name__ == '__main__':
    unittest.main()
