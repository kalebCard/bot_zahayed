import unittest
from unittest.mock import patch, MagicMock
from app.play import AutomationPlayer

class TestAutomationPlayer(unittest.TestCase):
    def setUp(self):
        self.player = AutomationPlayer()
        self.events = [
            {'type': 'mouse_move', 'x': 10, 'y': 20, 'time': 0.1},
            {'type': 'key_press', 'key': 'a', 'time': 0.2},
            {'type': 'key_release', 'key': 'a', 'time': 0.3},
        ]

    @patch.object(AutomationPlayer, '_execute_event')
    def test_play_automation(self, mock_execute):
        self.player.set_playback_speed(1.0)
        self.player.set_repeat_count(1)
        self.player.load_automation(self.events)
        result = self.player.play_automation()
        self.assertTrue(result)
        self.assertTrue(mock_execute.called)

    def test_parse_button(self):
        self.assertEqual(self.player._parse_button('Button.left'), self.player.mouse_controller.Button.left)
        self.assertEqual(self.player._parse_button('Button.right'), self.player.mouse_controller.Button.right)

    def test_parse_key(self):
        self.assertEqual(self.player._parse_key('Key.space'), self.player.keyboard_controller.Key.space)
        self.assertEqual(self.player._parse_key("KeyCode.from_char('a')"), 'a')

if __name__ == '__main__':
    unittest.main() 