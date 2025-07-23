import time
import json
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
import threading

class AutomationPlayer:
    def __init__(self):
        self.mouse_controller = MouseController()
        self.keyboard_controller = KeyboardController()
        self.playing = False
        self.paused = False
        self.current_event_index = 0
        self.playback_speed = 1.0
        self.repeat_count = 1
        self.current_repeat = 0
        self.allow_user_input = True
        self.skip_interfering_keys = True
        
        # Lista de eventos que NUNCA se deben reproducir
        self.blocked_events = [
            'Key.ctrl_l', 'Key.ctrl_r', 'Key.ctrl',
            'Key.shift_l', 'Key.shift_r', 'Key.shift',
            'Key.alt_l', 'Key.alt_r', 'Key.alt',
            "'\\x01'", "'\\x1a'", "'\\x19'", "'\\x18'",
            "'c'", "'v'", "'a'", "'z'", "'y'", "'x'"
        ]
        
    def load_automation(self, events):
        """Carga una automatización desde una lista de eventos"""
        # Filtrar eventos problemáticos al cargar
        filtered_events = []
        for event in events:
            if not self._is_blocked_event(event):
                filtered_events.append(event)
        
        self.events = filtered_events
        self.current_event_index = 0
        print(f"📁 Automatización cargada con {len(filtered_events)} eventos")
        if len(filtered_events) < len(events):
            print(f"⏭️ Se filtraron {len(events) - len(filtered_events)} eventos problemáticos")
        
    def _is_blocked_event(self, event):
        """Determina si un evento debe ser bloqueado completamente"""
        if event['type'] in ['key_press', 'key_release']:
            key_str = str(event['key'])
            return key_str in self.blocked_events
        return False
        
    def set_playback_speed(self, speed):
        """Establece la velocidad de reproducción (1.0 = normal, 2.0 = doble velocidad)"""
        self.playback_speed = speed
        print(f"⚡ Velocidad de reproducción: {speed}x")
        
    def set_repeat_count(self, count):
        """Establece el número de repeticiones"""
        self.repeat_count = count
        print(f"🔄 Repeticiones configuradas: {count}")
        
    def play_automation(self, events=None):
        """Reproduce una automatización"""
        if events:
            self.load_automation(events)
            
        if not hasattr(self, 'events') or not self.events:
            print("❌ No hay automatización cargada para reproducir")
            return False
            
        self.playing = True
        self.current_repeat = 0
        
        print(f"▶️ Iniciando reproducción...")
        print(f"📊 Configuración: {self.repeat_count} repetición(es), {self.playback_speed}x velocidad")
        
        try:
            for repeat in range(self.repeat_count):
                if not self.playing:
                    break
                    
                self.current_repeat = repeat + 1
                print(f"🔄 Repetición {self.current_repeat}/{self.repeat_count}")
                
                # Dar tiempo para que el usuario se prepare
                print("⏳ Preparando reproducción en 3 segundos...")
                print("💡 Durante la reproducción, puedes usar Ctrl+C y Ctrl+V en las pausas automáticas")
                time.sleep(3)
                
                self._play_events()
                
                if repeat < self.repeat_count - 1 and self.playing:
                    print("⏸️ Pausa entre repeticiones...")
                    time.sleep(2)
                    
        except KeyboardInterrupt:
            print("\n⏹️ Reproducción interrumpida por el usuario")
            self.stop_playback()
            return False
            
        print("✅ Reproducción completada")
        return True
        
    def _play_events(self):
        """Reproduce los eventos de la automatización"""
        last_time = 0
        
        for i, event in enumerate(self.events):
            if not self.playing:
                break
                
            # Manejar pausa
            while self.paused and self.playing:
                time.sleep(0.1)
                
            if not self.playing:
                break
                
            # Calcular tiempo de espera
            wait_time = (event['time'] - last_time) / self.playback_speed
            if wait_time > 0:
                elapsed = 0
                while elapsed < wait_time and self.playing and not self.paused:
                    sleep_interval = min(0.1, wait_time - elapsed)
                    time.sleep(sleep_interval)
                    elapsed += sleep_interval
                    
            # Verificar pausa nuevamente antes de ejecutar el evento
            while self.paused and self.playing:
                time.sleep(0.1)
                
            if not self.playing:
                break
                
            # Ejecutar evento
            self._execute_event(event)
            last_time = event['time']
            
            # Mostrar progreso cada 10 eventos
            if (i + 1) % 10 == 0:
                progress = (i + 1) / len(self.events) * 100
                print(f"📈 Progreso: {progress:.1f}% ({i + 1}/{len(self.events)})")
                
            # Pausa específica para Ctrl+C y Ctrl+V cada 25 eventos
            if self.allow_user_input and (i + 1) % 25 == 0:
                print("⏸️ Pausa para Ctrl+C y Ctrl+V...")
                time.sleep(1.5)  # 1.5 segundos de pausa
                
    def _execute_event(self, event):
        """Ejecuta un evento específico"""
        try:
            event_type = event['type']
            
            if event_type == 'mouse_move':
                self.mouse_controller.position = (event['x'], event['y'])
                
            elif event_type == 'mouse_click':
                self.mouse_controller.position = (event['x'], event['y'])
                button = self._parse_button(event['button'])
                if event['pressed']:
                    self.mouse_controller.press(button)
                else:
                    self.mouse_controller.release(button)
                    
            elif event_type == 'mouse_scroll':
                self.mouse_controller.position = (event['x'], event['y'])
                self.mouse_controller.scroll(event['dx'], event['dy'])
                
            elif event_type == 'key_press':
                key = self._parse_key(event['key'])
                if key is not None:
                    self._safe_key_press(key)
                
            elif event_type == 'key_release':
                key = self._parse_key(event['key'])
                if key is not None:
                    self._safe_key_release(key)
                
        except Exception as e:
            print(f"⚠️ Error ejecutando evento: {e}")
    
    def _safe_key_press(self, key):
        """Ejecuta un evento de pulsación de tecla de forma segura"""
        try:
            from pynput.keyboard import KeyCode, Key
            if key == 'ctrl_c':
                self.keyboard_controller.press(Key.ctrl)
                self.keyboard_controller.press('c')
            elif key == 'ctrl_v':
                self.keyboard_controller.press(Key.ctrl)
                self.keyboard_controller.press('v')
            elif isinstance(key, str) and len(key) == 1:
                key_code = KeyCode.from_char(key)
                self.keyboard_controller.press(key_code)
            elif hasattr(key, 'char'):
                self.keyboard_controller.press(key)
            else:
                self.keyboard_controller.press(key)
        except Exception as e:
            print(f"⚠️ Error en pulsación de tecla '{key}': {e}")
    
    def _safe_key_release(self, key):
        """Ejecuta un evento de liberación de teclado de forma segura"""
        try:
            from pynput.keyboard import KeyCode, Key
            if key == 'ctrl_c':
                self.keyboard_controller.release('c')
                self.keyboard_controller.release(Key.ctrl)
            elif key == 'ctrl_v':
                self.keyboard_controller.release('v')
                self.keyboard_controller.release(Key.ctrl)
            elif isinstance(key, str) and len(key) == 1:
                key_code = KeyCode.from_char(key)
                self.keyboard_controller.release(key_code)
            elif hasattr(key, 'char'):
                self.keyboard_controller.release(key)
            else:
                self.keyboard_controller.release(key)
        except Exception as e:
            print(f"⚠️ Error en liberación de tecla '{key}': {e}")
            
    def _parse_button(self, button_str):
        """Convierte string de botón a objeto Button"""
        button_str = button_str.lower()
        if 'left' in button_str:
            return Button.left
        elif 'right' in button_str:
            return Button.right
        elif 'middle' in button_str:
            return Button.middle
        else:
            return Button.left
            
    def _parse_key(self, key_str):
        """Convierte string de tecla a objeto Key"""
        # Mapeo de teclas comunes
        key_mapping = {
            'Key.space': Key.space,
            'Key.enter': Key.enter,
            'Key.tab': Key.tab,
            'Key.esc': Key.esc,
            'Key.backspace': Key.backspace,
            'Key.delete': Key.delete,
            'Key.up': Key.up,
            'Key.down': Key.down,
            'Key.left': Key.left,
            'Key.right': Key.right,
            'Key.home': Key.home,
            'Key.end': Key.end,
            'Key.page_up': Key.page_up,
            'Key.page_down': Key.page_down,
        }
        
        # Si es un evento bloqueado, retornar None
        if key_str in self.blocked_events:
            return None
        
        # Detectar Ctrl+C y Ctrl+V
        if key_str == "'\\x03'":
            return 'ctrl_c'
        if key_str == "'\\x16'":
            return 'ctrl_v'
        
        if key_str in key_mapping:
            return key_mapping[key_str]
        else:
            # Intentar extraer carácter simple
            try:
                if "KeyCode.from_char('" in key_str:
                    char = key_str.split("'")[1]
                    return char
                # Si es del tipo 'a' (con comillas simples)
                if len(key_str) == 3 and key_str.startswith("'") and key_str.endswith("'"):
                    return key_str[1]
                else:
                    return key_str
            except:
                return key_str
                
    def stop_playback(self):
        """Detiene la reproducción"""
        self.playing = False
        self.paused = False
        print("⏹️ Reproducción detenida")
        
    def pause_playback(self):
        """Pausa la reproducción"""
        self.paused = True
        print("⏸️ Reproducción pausada")
        
    def resume_playback(self):
        """Reanuda la reproducción"""
        self.paused = False
        print("▶️ Reproducción reanudada")
        
    def enable_user_input_during_playback(self):
        """Habilita la entrada del usuario durante la reproducción"""
        self.allow_user_input = True
        print("✅ Entrada del usuario habilitada durante reproducción")
    
    def disable_user_input_during_playback(self):
        """Deshabilita la entrada del usuario durante la reproducción"""
        self.allow_user_input = False
        print("❌ Entrada del usuario deshabilitada durante reproducción")
    
    def enable_copy_paste_compatibility(self):
        """Habilita la compatibilidad con Ctrl+C y Ctrl+V"""
        self.skip_interfering_keys = True
        print("✅ Compatibilidad con Ctrl+C y Ctrl+V habilitada")
    
    def disable_copy_paste_compatibility(self):
        """Deshabilita la compatibilidad con Ctrl+C y Ctrl+V"""
        self.skip_interfering_keys = False
        print("❌ Compatibilidad con Ctrl+C y Ctrl+V deshabilitada")
    
    def pause_for_user_input(self, duration=2.0):
        """Pausa la reproducción para permitir entrada del usuario"""
        print(f"⏸️ Pausa de {duration} segundos para entrada del usuario...")
        print("💡 Puedes usar Ctrl+C y Ctrl+V durante esta pausa")
        time.sleep(duration)
        print("▶️ Continuando reproducción...")
    
    def emergency_pause_for_copy_paste(self):
        """Pausa de emergencia para operaciones de copiar/pegar"""
        print("🚨 PAUSA DE EMERGENCIA - Usa Ctrl+C y Ctrl+V ahora...")
        print("💡 Presiona Enter en la consola para continuar...")
        input("Presiona Enter para continuar la reproducción...")
        print("▶️ Continuando reproducción...")
    
    def pause_for_copy_paste_operation(self, duration=5.0):
        """Pausa específica para operaciones de copiar/pegar"""
        print(f"⌨️ PAUSA PARA COPIAR/PEGAR - {duration} segundos...")
        print("💡 Usa Ctrl+C y Ctrl+V ahora...")
        time.sleep(duration)
        print("▶️ Continuando reproducción...")
        
    def get_status(self):
        """Retorna el estado actual de la reproducción"""
        return {
            'playing': self.playing,
            'paused': self.paused,
            'current_event': self.current_event_index,
            'total_events': len(self.events) if hasattr(self, 'events') else 0,
            'current_repeat': self.current_repeat,
            'total_repeats': self.repeat_count,
            'speed': self.playback_speed
        }

# Función de conveniencia para reproducción rápida
def play_automation(events, speed=1.0, repeats=1):
    """Función para reproducir una automatización"""
    player = AutomationPlayer()
    player.set_playback_speed(speed)
    player.set_repeat_count(repeats)
    return player.play_automation(events)

if __name__ == "__main__":
    print("🎮 Módulo de reproducción de automatizaciones")
    print("📝 Para usar este módulo, carga una automatización y llama a play_automation()")
