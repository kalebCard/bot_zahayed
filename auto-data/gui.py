#!/usr/bin/env python3
"""
Script de inicio para la aplicación Tkinter
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import TkinterApp
    import tkinter as tk
    print("Iniciando aplicación de Gestión de Datos...")
    root = tk.Tk()
    app = TkinterApp(root)
    root.mainloop()
except ImportError as e:
    print(f"Error al importar módulos: {e}")
    print("Asegúrese de que todos los archivos estén en el directorio correcto")
except Exception as e:
    print(f"Error al iniciar la aplicación: {e}") 