import unittest
from app.save import AutomationManager
from app.play import AutomationPlayer
from app.edit import AutomationEditor

class TestIntegrationFlow(unittest.TestCase):
    def setUp(self):
        self.test_dir = 'test_automations_integration'
        self.manager = AutomationManager(save_directory=self.test_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)

    def test_full_flow(self):
        # 1. Guardar automatización
        events = [
            {'type': 'mouse_move', 'x': 10, 'y': 20, 'time': 0.1},
            {'type': 'key_press', 'key': 'a', 'time': 0.2},
        ]
        self.assertTrue(self.manager.save_automation('flow', events, 'desc', ['tag']))
        # 2. Cargar y reproducir
        loaded = self.manager.load_automation('flow')
        player = AutomationPlayer()
        player.load_automation(loaded)
        with unittest.mock.patch.object(player, '_execute_event') as mock_exec:
            self.assertTrue(player.play_automation())
            self.assertTrue(mock_exec.called)
        # 3. Editar
        editor = AutomationEditor()
        editor.manager = self.manager
        self.assertTrue(editor.load_for_editing('flow'))
        self.assertTrue(editor.duplicate_event(0))
        self.assertTrue(editor.save_changes())
        # 4. Verificar edición
        loaded2 = self.manager.load_automation('flow')
        self.assertEqual(len(loaded2), 3)

if __name__ == '__main__':
    unittest.main() 