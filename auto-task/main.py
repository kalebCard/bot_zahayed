#!/usr/bin/env python3
"""
Auto-Task - Gestor de Automatizaciones de Teclado y Mouse
=========================================================

Un programa completo para grabar, reproducir, editar y gestionar automatizaciones
de teclado y mouse de manera eficiente y fácil de usar.

Características principales:
- 🎙️ Grabación de eventos de teclado y mouse
- ▶️ Reproducción con velocidad y repeticiones configurables
- ✏️ Editor avanzado para modificar automatizaciones
- 💾 Sistema de guardado y gestión de automatizaciones
- 🖥️ Interfaz gráfica intuitiva
- 🔍 Búsqueda y filtrado de automatizaciones
- 📤 Exportación e importación de automatizaciones

Autor: Auto-Task Team
Versión: 1.0.0
"""

import sys
import os
import argparse
from pathlib import Path

# Agregar el directorio actual al path para importar nuestros módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Verifica que todas las dependencias estén instaladas"""
    required_packages = ['pynput', 'tkinter']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Dependencias faltantes:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Instala las dependencias con:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ Todas las dependencias están instaladas")
    return True

def create_directories():
    """Crea los directorios necesarios"""
    directories = ['automations', 'logs', 'exports']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Directorio '{directory}' creado/verificado")

def run_gui():
    """Ejecuta la interfaz gráfica"""
    try:
        from app import run_gui as app_run_gui
        print("🚀 Iniciando Auto-Task...")
        app_run_gui()
    except Exception as e:
        print(f"❌ Error iniciando la interfaz gráfica: {e}")
        return False
    return True

def run_recording():
    """Ejecuta solo la grabación"""
    try:
        from app import run_recording as app_run_recording
        print("🎙️ Iniciando grabación...")
        events = app_run_recording()
        if events:
            print(f"✅ Grabación completada con {len(events)} eventos")
            return events
        else:
            print("❌ Grabación cancelada o fallida")
            return None
    except Exception as e:
        print(f"❌ Error en grabación: {e}")
        return None

def run_playback(automation_name, speed=1.0, repeats=1):
    """Ejecuta solo la reproducción"""
    try:
        from app import run_playback as app_run_playback
        print(f"▶️ Reproduciendo '{automation_name}'...")
        success = app_run_playback(automation_name, speed, repeats)
        if success:
            print("✅ Reproducción completada")
        else:
            print("❌ Reproducción interrumpida")
        return success
    except Exception as e:
        print(f"❌ Error en reproducción: {e}")
        return False

def list_automations():
    """Lista todas las automatizaciones disponibles"""
    try:
        from app import list_automations as app_list_automations
        app_list_automations()
    except Exception as e:
        print(f"❌ Error listando automatizaciones: {e}")

def show_help():
    """Muestra la ayuda del programa"""
    help_text = """
🎯 Auto-Task - Gestor de Automatizaciones

Uso:
    python main.py [opciones]

Opciones:
    --gui, -g          Iniciar interfaz gráfica (por defecto)
    --record, -r       Solo grabar una automatización
    --play <nombre>    Reproducir una automatización específica
    --speed <valor>    Velocidad de reproducción (0.1-3.0)
    --repeats <num>    Número de repeticiones
    --list, -l         Listar todas las automatizaciones
    --check, -c        Verificar dependencias
    --help, -h         Mostrar esta ayuda

Ejemplos:
    python main.py                     # Iniciar interfaz gráfica
    python main.py --record            # Solo grabar
    python main.py --play "mi_auto"   # Reproducir automatización
    python main.py --play "test" --speed 2.0 --repeats 3
    python main.py --list              # Listar automatizaciones

Características:
    🎙️ Grabación de teclado y mouse
    ▶️ Reproducción con velocidad configurable
    ✏️ Editor avanzado de automatizaciones
    💾 Sistema de gestión de archivos
    🔍 Búsqueda y filtrado
    📤 Exportación/importación
    🖥️ Interfaz gráfica intuitiva

Para más información, consulta el README.md
"""
    print(help_text)

def main():
    """Función principal del programa"""
    parser = argparse.ArgumentParser(
        description="Auto-Task - Gestor de Automatizaciones de Teclado y Mouse",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py                     # Interfaz gráfica
  python main.py --record            # Solo grabar
  python main.py --play "test"       # Reproducir
  python main.py --list              # Listar automatizaciones
        """
    )
    
    parser.add_argument('--gui', '-g', action='store_true', 
                       help='Iniciar interfaz gráfica (por defecto)')
    parser.add_argument('--record', '-r', action='store_true',
                       help='Solo grabar una automatización')
    parser.add_argument('--play', type=str, metavar='NOMBRE',
                       help='Reproducir automatización específica')
    parser.add_argument('--speed', type=float, default=1.0,
                       help='Velocidad de reproducción (0.1-3.0, por defecto: 1.0)')
    parser.add_argument('--repeats', type=int, default=1,
                       help='Número de repeticiones (por defecto: 1)')
    parser.add_argument('--list', '-l', action='store_true',
                       help='Listar todas las automatizaciones')
    parser.add_argument('--check', '-c', action='store_true',
                       help='Verificar dependencias')
    
    args = parser.parse_args()
    
    # Mostrar banner
    print("🎯" + "="*50)
    print("🎯 Auto-Task - Gestor de Automatizaciones")
    print("🎯 Versión 1.0.0")
    print("🎯" + "="*50)
    
    # Verificar dependencias si se solicita
    if args.check:
        return check_dependencies()
    
    # Mostrar ayuda si se solicita
    if hasattr(args, 'help') and args.help:
        show_help()
        return True
    
    # Verificar dependencias básicas
    if not check_dependencies():
        return False
    
    # Crear directorios necesarios
    create_directories()
    
    # Procesar argumentos
    if args.record:
        return run_recording() is not None
    elif args.play:
        return run_playback(args.play, args.speed, args.repeats)
    elif args.list:
        list_automations()
        return True
    else:
        # Por defecto, ejecutar interfaz gráfica
        return run_gui()

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Programa interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1) 