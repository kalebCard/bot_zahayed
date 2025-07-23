import json
import time
from datetime import datetime
from app.save import AutomationManager

class AutomationEditor:
    def __init__(self):
        self.manager = AutomationManager()
        self.current_automation = None
        self.current_events = []
        
    def load_for_editing(self, name):
        """Carga una automatización para editar"""
        events = self.manager.load_automation(name)
        if events:
            self.current_automation = name
            self.current_events = events.copy()
            print(f"✏️ Automatización '{name}' cargada para edición")
            print(f"📊 {len(events)} eventos disponibles para editar")
            return True
        return False
        
    def save_changes(self, new_name=None):
        """Guarda los cambios realizados"""
        if not self.current_automation:
            print("❌ No hay automatización cargada para guardar")
            return False
            
        name = new_name or self.current_automation
        info = self.manager.get_automation_info(self.current_automation)
        
        if info:
            description = info.get('description', '')
            tags = info.get('tags', [])
        else:
            description = ""
            tags = []
            
        success = self.manager.save_automation(name, self.current_events, description, tags)
        
        if success and new_name and new_name != self.current_automation:
            # Si se cambió el nombre, eliminar el archivo anterior
            self.manager.delete_automation(self.current_automation)
            self.current_automation = name
            
        return success
        
    def list_events(self, start=0, end=None):
        """Lista los eventos de la automatización actual"""
        if not self.current_events:
            print("❌ No hay eventos para mostrar")
            return
            
        if end is None:
            end = len(self.current_events)
            
        print(f"📋 Eventos {start+1}-{end} de {len(self.current_events)}:")
        print("-" * 80)
        
        for i in range(start, min(end, len(self.current_events))):
            event = self.current_events[i]
            self._print_event(i, event)
            
    def _print_event(self, index, event):
        """Imprime un evento formateado"""
        event_type = event.get('type', 'unknown')
        time_str = f"{event.get('time', 0):.3f}s"
        
        if event_type == 'mouse_move':
            print(f"{index+1:3d}. 🖱️  Mover a ({event['x']}, {event['y']}) - {time_str}")
        elif event_type == 'mouse_click':
            button = event.get('button', 'unknown')
            action = "Presionar" if event.get('pressed', False) else "Soltar"
            print(f"{index+1:3d}. 🖱️  {action} {button} en ({event['x']}, {event['y']}) - {time_str}")
        elif event_type == 'mouse_scroll':
            print(f"{index+1:3d}. 🖱️  Scroll ({event.get('dx', 0)}, {event.get('dy', 0)}) en ({event['x']}, {event['y']}) - {time_str}")
        elif event_type == 'key_press':
            print(f"{index+1:3d}. ⌨️  Presionar {event.get('key', 'unknown')} - {time_str}")
        elif event_type == 'key_release':
            print(f"{index+1:3d}. ⌨️  Soltar {event.get('key', 'unknown')} - {time_str}")
        else:
            print(f"{index+1:3d}. ❓ Evento desconocido: {event} - {time_str}")
            
    def delete_event(self, index):
        """Elimina un evento específico"""
        if not self.current_events:
            print("❌ No hay eventos para eliminar")
            return False
            
        if 0 <= index < len(self.current_events):
            deleted_event = self.current_events.pop(index)
            print(f"🗑️ Evento {index+1} eliminado: {deleted_event.get('type', 'unknown')}")
            return True
        else:
            print(f"❌ Índice {index+1} fuera de rango")
            return False
            
    def insert_event(self, index, event):
        """Inserta un evento en una posición específica"""
        if 0 <= index <= len(self.current_events):
            self.current_events.insert(index, event)
            print(f"➕ Evento insertado en posición {index+1}")
            return True
        else:
            print(f"❌ Índice {index+1} fuera de rango")
            return False
            
    def modify_event(self, index, **kwargs):
        """Modifica un evento específico"""
        if not self.current_events or not (0 <= index < len(self.current_events)):
            print(f"❌ Índice {index+1} fuera de rango")
            return False
            
        event = self.current_events[index]
        original_event = event.copy()
        
        for key, value in kwargs.items():
            if key in event:
                event[key] = value
                
        print(f"✏️ Evento {index+1} modificado:")
        print(f"   Antes: {original_event}")
        print(f"   Después: {event}")
        return True
        
    def adjust_timing(self, factor):
        """Ajusta todos los tiempos por un factor"""
        if not self.current_events:
            print("❌ No hay eventos para ajustar")
            return False
            
        for event in self.current_events:
            if 'time' in event:
                event['time'] *= factor
                
        print(f"⏱️ Tiempos ajustados por factor {factor}")
        return True
        
    def remove_mouse_moves(self, threshold=5):
        """Elimina movimientos de mouse muy pequeños"""
        if not self.current_events:
            print("❌ No hay eventos para filtrar")
            return False
            
        original_count = len(self.current_events)
        filtered_events = []
        last_position = None
        
        for event in self.current_events:
            if event.get('type') == 'mouse_move':
                current_position = (event['x'], event['y'])
                
                if last_position is None:
                    # Mantener el primer movimiento
                    filtered_events.append(event)
                    last_position = current_position
                else:
                    # Calcular distancia
                    distance = ((current_position[0] - last_position[0])**2 + 
                              (current_position[1] - last_position[1])**2)**0.5
                    
                    if distance >= threshold:
                        filtered_events.append(event)
                        last_position = current_position
            else:
                filtered_events.append(event)
                
        removed_count = original_count - len(filtered_events)
        self.current_events = filtered_events
        
        print(f"🧹 Eliminados {removed_count} movimientos de mouse pequeños (umbral: {threshold}px)")
        return True
        
    def remove_all_mouse_moves(self):
        """Elimina todos los movimientos del mouse (mantiene clics)"""
        if not self.current_events:
            print("❌ No hay eventos para filtrar")
            return False
            
        original_count = len(self.current_events)
        filtered_events = []
        
        for event in self.current_events:
            # Mantener todos los eventos excepto los movimientos del mouse
            if event.get('type') != 'mouse_move':
                filtered_events.append(event)
                
        removed_count = original_count - len(filtered_events)
        self.current_events = filtered_events
        
        print(f"🗑️ Eliminados {removed_count} movimientos de mouse (manteniendo clics)")
        return True
        
    def add_delay(self, index, delay_seconds):
        """Añade un retraso en una posición específica"""
        delay_event = {
            'type': 'delay',
            'time': self.current_events[index]['time'] if index < len(self.current_events) else 0,
            'duration': delay_seconds
        }
        
        return self.insert_event(index, delay_event)
        
    def duplicate_event(self, index):
        """Duplica un evento"""
        if not self.current_events or not (0 <= index < len(self.current_events)):
            print(f"❌ Índice {index+1} fuera de rango")
            return False
            
        event = self.current_events[index].copy()
        # Ajustar tiempo ligeramente
        if 'time' in event:
            event['time'] += 0.1
            
        return self.insert_event(index + 1, event)
        
    def get_statistics(self):
        """Obtiene estadísticas de la automatización actual"""
        if not self.current_events:
            return None
            
        stats = {
            'total_events': len(self.current_events),
            'duration': max(event.get('time', 0) for event in self.current_events),
            'mouse_events': 0,
            'keyboard_events': 0,
            'mouse_moves': 0,
            'mouse_clicks': 0,
            'key_presses': 0,
            'key_releases': 0
        }
        
        for event in self.current_events:
            event_type = event.get('type', '')
            
            if 'mouse' in event_type:
                stats['mouse_events'] += 1
                if 'move' in event_type:
                    stats['mouse_moves'] += 1
                elif 'click' in event_type:
                    stats['mouse_clicks'] += 1
            elif 'key' in event_type:
                stats['keyboard_events'] += 1
                if 'press' in event_type:
                    stats['key_presses'] += 1
                elif 'release' in event_type:
                    stats['key_releases'] += 1
                    
        return stats
        
    def print_statistics(self):
        """Imprime estadísticas de la automatización actual"""
        stats = self.get_statistics()
        if not stats:
            print("❌ No hay estadísticas disponibles")
            return
            
        print("📊 Estadísticas de la automatización:")
        print("-" * 40)
        print(f"📈 Total de eventos: {stats['total_events']}")
        print(f"⏱️  Duración total: {stats['duration']:.3f}s")
        print(f"🖱️  Eventos de mouse: {stats['mouse_events']}")
        print(f"   - Movimientos: {stats['mouse_moves']}")
        print(f"   - Clics: {stats['mouse_clicks']}")
        print(f"⌨️  Eventos de teclado: {stats['keyboard_events']}")
        print(f"   - Pulsaciones: {stats['key_presses']}")
        print(f"   - Liberaciones: {stats['key_releases']}")
        
    def export_events(self, filename):
        """Exporta los eventos actuales a un archivo JSON"""
        if not self.current_events:
            print("❌ No hay eventos para exportar")
            return False
            
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.current_events, f, indent=2, ensure_ascii=False)
            print(f"📤 Eventos exportados a {filename}")
            return True
        except Exception as e:
            print(f"❌ Error exportando eventos: {e}")
            return False
            
    def import_events(self, filename):
        """Importa eventos desde un archivo JSON"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                events = json.load(f)
                
            if isinstance(events, list):
                self.current_events = events
                print(f"📥 {len(events)} eventos importados desde {filename}")
                return True
            else:
                print("❌ Formato de archivo inválido")
                return False
        except Exception as e:
            print(f"❌ Error importando eventos: {e}")
            return False

# Funciones de conveniencia
def edit_automation(name):
    """Función para cargar una automatización para edición"""
    editor = AutomationEditor()
    if editor.load_for_editing(name):
        return editor
    return None

if __name__ == "__main__":
    # Ejemplo de uso
    print("✏️ Módulo de edición de automatizaciones")
    print("📝 Para usar este módulo, llama a edit_automation('nombre')")
