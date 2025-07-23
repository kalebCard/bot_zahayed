import unittest
from app.edit import AutomationEditor
from app.save import AutomationManager

class TestAutomationEditor(unittest.TestCase):
    def setUp(self):
        self.manager = AutomationManager(save_directory='test_automations_edit')
        self.manager.save_automation('edit_test', [{'type': 'mouse_move', 'x': 1, 'y': 2, 'time': 0.1}], '', [])
        self.editor = AutomationEditor()
        self.editor.manager = self.manager
        self.editor.load_for_editing('edit_test')

    def tearDown(self):
        import shutil
        shutil.rmtree('test_automations_edit')

    def test_delete_event(self):
        self.assertTrue(self.editor.delete_event(0))
        self.assertEqual(len(self.editor.current_events), 0)

    def test_duplicate_event(self):
        self.assertTrue(self.editor.duplicate_event(0))
        self.assertEqual(len(self.editor.current_events), 2)

    def test_adjust_timing(self):
        self.assertTrue(self.editor.adjust_timing(2.0))
        self.assertAlmostEqual(self.editor.current_events[0]['time'], 0.2)

    def test_save_changes(self):
        self.assertTrue(self.editor.save_changes())

if __name__ == '__main__':
    unittest.main() 