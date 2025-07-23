"""
Tests para Auto-Task - Gestor de Automatizaciones
=================================================

Este paquete contiene todos los tests unitarios y de integración
para el sistema de automatización Auto-Task.
"""

# Importar todos los tests para facilitar la ejecución
from .test_rec import TestAutomationRecorder
from .test_play import TestAutomationPlayer
from .test_save import TestAutomationManager
from .test_edit import TestAutomationEditor
from .test_integration import TestIntegrationFlow

__all__ = [
    'TestAutomationRecorder',
    'TestAutomationPlayer',
    'TestAutomationManager', 
    'TestAutomationEditor',
    'TestIntegrationFlow',
]

def run_all_tests():
    """Ejecuta todos los tests del paquete"""
    import unittest
    
    # Crear suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar todos los tests
    for test_class in __all__:
        suite.addTests(loader.loadTestsFromTestCase(globals()[test_class]))
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1) 