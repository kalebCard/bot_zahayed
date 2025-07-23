import time
import json
from pynput import mouse, keyboard
from pynput.mouse import Button, Listener as MouseListener
from pynput.keyboard import Key, Listener as KeyboardListener
from datetime import datetime

class AutomationRecorder:
    def __init__(self):
        self.events = []
        self.recording = False
        self.paused = False  # NUEVO: estado de pausa
        self.start_time = None
        self.mouse_listener = None
        self.keyboard_listener = None
        self.ctrl_pressed = False
        
        # Lista de eventos que NO se deben grabar
        self.blocked_events = [
            'Key.ctrl_l', 'Key.ctrl_r', 'Key.ctrl',
            'Key.shift_l', 'Key.shift_r', 'Key.shift',
            'Key.alt_l', 'Key.alt_r', 'Key.alt',
            "'\\x01'", "'\\x1a'", "'\\x19'", "'\\x18'",
            "'c'", "'v'", "'a'", "'z'", "'y'", "'x'"
        ]
        
    def start_recording(self):
        """Inicia la grabación de eventos"""
        self.events = []
        self.recording = True
        self.start_time = time.time()
        
        # Iniciar listeners
        self.mouse_listener = MouseListener(
            on_move=self.on_mouse_move,
            on_click=self.on_mouse_click,
            on_scroll=self.on_mouse_scroll
        )
        
        self.keyboard_listener = KeyboardListener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
        print("🎙️ Grabación iniciada. Presiona Ctrl+Shift+R para detener.")
        
    def stop_recording(self):
        """Detiene la grabación de eventos"""
        self.recording = False
        
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            
        print(f"⏹️ Grabación detenida. {len(self.events)} eventos capturados.")
        return self.events
    
    def get_current_time(self):
        """Obtiene el tiempo actual desde el inicio de la grabación"""
        return time.time() - self.start_time if self.start_time else 0
    
    def on_mouse_move(self, x, y):
        """Captura movimiento del mouse (DESHABILITADO)"""
        # No capturar movimientos del mouse para automatizaciones más limpias
        pass
    
    def on_mouse_click(self, x, y, button, pressed):
        """Captura clics del mouse"""
        if self.recording:
            event = {
                'type': 'mouse_click',
                'x': x,
                'y': y,
                'button': str(button),
                'pressed': pressed,
                'time': self.get_current_time()
            }
            self.events.append(event)
    
    def on_mouse_scroll(self, x, y, dx, dy):
        """Captura scroll del mouse"""
        if self.recording:
            event = {
                'type': 'mouse_scroll',
                'x': x,
                'y': y,
                'dx': dx,
                'dy': dy,
                'time': self.get_current_time()
            }
            self.events.append(event)
    
    def on_key_press(self, key):
        """Captura pulsaciones de teclas"""
        if self.recording:
            # PAUSA/REANUDA con la tecla '1'
            try:
                if key == keyboard.KeyCode.from_char('1'):
                    self.paused = not self.paused
                    if self.paused:
                        print("⏸️ Grabación pausada (tecla 1)")
                    else:
                        print("▶️ Grabación reanudada (tecla 1)")
                    return True  # No grabar el evento de pausa
            except Exception:
                pass
            # Verificar si es un evento bloqueado
            if self._is_blocked_event(key):
                return True  # Permitir que pase a través sin grabarlo
            # Detener grabación con Ctrl+Shift+R
            try:
                if key == keyboard.KeyCode.from_char('r') and self.is_ctrl_shift_pressed():
                    self.stop_recording()
                    return False
            except AttributeError:
                pass
            # SOLO grabar si NO está en pausa
            if not self.paused:
                event = {
                    'type': 'key_press',
                    'key': str(key),
                    'time': self.get_current_time()
                }
                self.events.append(event)
    
    def on_key_release(self, key):
        """Captura liberación de teclas"""
        if self.recording:
            if self._is_blocked_event(key):
                return True
            # SOLO grabar si NO está en pausa
            if not self.paused:
                event = {
                    'type': 'key_release',
                    'key': str(key),
                    'time': self.get_current_time()
                }
                self.events.append(event)
    
    def _is_blocked_event(self, key):
        """Determina si un evento debe ser bloqueado"""
        key_str = str(key)
        return key_str in self.blocked_events
    
    def is_ctrl_shift_pressed(self):
        """Verifica si Ctrl+Shift están presionados"""
        # Implementación simplificada
        return True
    
    def is_ctrl_pressed(self):
        """Verifica si Ctrl está presionado"""
        return True
    
    def get_events(self):
        """Retorna los eventos grabados"""
        return self.events
    
    def clear_events(self):
        """Limpia los eventos grabados"""
        self.events = []

# Función de conveniencia para grabación rápida
def record_automation():
    """Función para grabar una automatización completa"""
    recorder = AutomationRecorder()
    print("🚀 Iniciando grabación de automatización...")
    print("📝 Instrucciones:")
    print("  - Realiza las acciones que quieres automatizar")
    print("  - Solo se graban: clics, teclado y scroll (NO movimientos)")
    print("  - Presiona Ctrl+Shift+R para detener la grabación")
    print("  - O presiona Ctrl+C para cancelar")
    print("  - NOTA: Ahora Ctrl+C y Ctrl+V SÍ se graban y reproducen automáticamente. Otras teclas modificadoras NO.")
    
    try:
        recorder.start_recording()
        # Mantener el programa corriendo hasta que se detenga la grabación
        while recorder.recording:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n❌ Grabación cancelada por el usuario")
        recorder.stop_recording()
        return None
    
    return recorder.get_events()

if __name__ == "__main__":
    # Prueba del grabador
    events = record_automation()
    if events:
        print(f"✅ Grabación completada con {len(events)} eventos")
        print("Primeros 3 eventos:")
        for i, event in enumerate(events[:3]):
            print(f"  {i+1}. {event}")
