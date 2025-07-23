import unittest
from unittest.mock import patch, MagicMock
from app.rec import AutomationRecorder

class TestAutomationRecorder(unittest.TestCase):
    def setUp(self):
        self.recorder = AutomationRecorder()

    def test_start_and_stop_recording(self):
        # Simular listeners
        with patch.object(self.recorder, 'mouse_listener'), \
             patch.object(self.recorder, 'keyboard_listener'):
            self.recorder.start_recording()
            self.assertTrue(self.recorder.recording)
            self.recorder.stop_recording()
            self.assertFalse(self.recorder.recording)

    def test_on_mouse_move(self):
        self.recorder.recording = True
        self.recorder.start_time = 0
        self.recorder.on_mouse_move(100, 200)
        self.assertEqual(self.recorder.events[0]['type'], 'mouse_move')
        self.assertEqual(self.recorder.events[0]['x'], 100)
        self.assertEqual(self.recorder.events[0]['y'], 200)

    def test_on_key_press_and_release(self):
        self.recorder.recording = True
        self.recorder.start_time = 0
        self.recorder.on_key_press('a')
        self.recorder.on_key_release('a')
        self.assertEqual(self.recorder.events[0]['type'], 'key_press')
        self.assertEqual(self.recorder.events[1]['type'], 'key_release')

    def test_clear_events(self):
        self.recorder.events = [{'type': 'mouse_move'}]
        self.recorder.clear_events()
        self.assertEqual(len(self.recorder.events), 0)

if __name__ == '__main__':
    unittest.main() 