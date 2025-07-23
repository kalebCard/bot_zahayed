import unittest
import os
import shutil
from app.save import AutomationManager

class TestAutomationManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = 'test_automations'
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        self.manager = AutomationManager(save_directory=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_save_and_load_automation(self):
        events = [{'type': 'mouse_move', 'x': 1, 'y': 2, 'time': 0.1}]
        self.assertTrue(self.manager.save_automation('test', events, 'desc', ['tag']))
        loaded = self.manager.load_automation('test')
        self.assertEqual(loaded, events)

    def test_list_automations(self):
        self.manager.save_automation('test1', [], '', [])
        self.manager.save_automation('test2', [], '', [])
        automations = self.manager.list_automations()
        self.assertEqual(len(automations), 2)

    def test_delete_automation(self):
        self.manager.save_automation('test', [], '', [])
        self.assertTrue(self.manager.delete_automation('test'))
        self.assertFalse(self.manager.delete_automation('test'))

if __name__ == '__main__':
    unittest.main() 