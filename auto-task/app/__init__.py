"""
Auto-Task - Gestor de Automatizaciones de Teclado y Mouse
=========================================================

Un programa completo para grabar, reproducir, editar y gestionar automatizaciones
de teclado y mouse de manera eficiente y fácil de usar.

Este paquete contiene todos los módulos principales del sistema de automatización.
"""

__version__ = "1.0.0"
__author__ = "Auto-Task Team"
__description__ = "Gestor de Automatizaciones de Teclado y Mouse"

# Importar las clases principales para facilitar el acceso
from .rec import AutomationRecorder, record_automation
from .play import AutomationPlayer, play_automation
from .save import AutomationManager, save_automation, load_automation, list_all_automations
from .edit import AutomationEditor, edit_automation
from .gui import AutomationGUI

# Exportar las clases principales
__all__ = [
    # Clases principales
    'AutomationRecorder',
    'AutomationPlayer', 
    'AutomationManager',
    'AutomationEditor',
    'AutomationGUI',
    
    # Funciones de conveniencia
    'record_automation',
    'play_automation',
    'save_automation',
    'load_automation',
    'list_all_automations',
    'edit_automation',
]

def get_version():
    """Retorna la versión actual del paquete"""
    return __version__

def get_info():
    """Retorna información básica del paquete"""
    return {
        'name': 'Auto-Task',
        'version': __version__,
        'author': __author__,
        'description': __description__,
        'modules': [
            'rec - Grabación de automatizaciones',
            'play - Reproducción de automatizaciones', 
            'save - Gestión de archivos',
            'edit - Edición de automatizaciones',
            'gui - Interfaz gráfica'
        ]
    }

def run_gui():
    """Función de conveniencia para ejecutar la interfaz gráfica"""
    app = AutomationGUI()
    app.run()

def run_recording():
    """Función de conveniencia para ejecutar solo la grabación"""
    return record_automation()

def run_playback(automation_name, speed=1.0, repeats=1):
    """Función de conveniencia para reproducir una automatización"""
    manager = AutomationManager()
    events = manager.load_automation(automation_name)
    if events:
        return play_automation(events, speed, repeats)
    return False

def list_automations():
    """Función de conveniencia para listar automatizaciones"""
    return list_all_automations()

# Información del paquete cuando se importa
if __name__ == "__main__":
    print("🎯 Auto-Task - Gestor de Automatizaciones")
    print(f"📦 Versión: {__version__}")
    print(f"👨‍💻 Autor: {__author__}")
    print(f"📝 Descripción: {__description__}")
    print("\n📚 Módulos disponibles:")
    for module in get_info()['modules']:
        print(f"   - {module}") 