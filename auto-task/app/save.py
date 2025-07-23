import json
import os
from datetime import datetime
from pathlib import Path

class AutomationManager:
    def __init__(self, save_directory="automations"):
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(exist_ok=True)
        self.automations = {}
        self.load_all_automations()
        
    def save_automation(self, name, events, description="", tags=None):
        """Guarda una automatización con metadatos. No permite duplicados."""
        if tags is None:
            tags = []
        # PREVENIR DUPLICADOS
        if name in self.automations:
            print(f"❌ Ya existe una automatización con el nombre '{name}'")
            return False
            
        automation_data = {
            'name': name,
            'description': description,
            'tags': tags,
            'created_date': datetime.now().isoformat(),
            'modified_date': datetime.now().isoformat(),
            'event_count': len(events),
            'duration': self._calculate_duration(events),
            'events': events
        }
        
        # Crear nombre de archivo seguro
        safe_name = self._sanitize_filename(name)
        filename = f"{safe_name}.json"
        filepath = self.save_directory / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(automation_data, f, indent=2, ensure_ascii=False)
                
            # Actualizar diccionario local
            self.automations[name] = automation_data
            
            print(f"💾 Automatización '{name}' guardada exitosamente")
            print(f"📁 Ubicación: {filepath}")
            print(f"📊 Estadísticas: {len(events)} eventos, {self._calculate_duration(events):.2f}s duración")
            
            return True
            
        except Exception as e:
            print(f"❌ Error guardando automatización: {e}")
            return False
            
    def load_automation(self, name):
        """Carga una automatización específica"""
        if name in self.automations:
            return self.automations[name]['events']
            
        # Intentar cargar desde archivo
        safe_name = self._sanitize_filename(name)
        filename = f"{safe_name}.json"
        filepath = self.save_directory / filename
        
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    automation_data = json.load(f)
                    
                self.automations[name] = automation_data
                print(f"📂 Automatización '{name}' cargada exitosamente")
                return automation_data['events']
                
            except Exception as e:
                print(f"❌ Error cargando automatización '{name}': {e}")
                return None
        else:
            print(f"❌ Automatización '{name}' no encontrada")
            return None
            
    def load_all_automations(self):
        """Carga todas las automatizaciones guardadas"""
        if not self.save_directory.exists():
            return
            
        for filepath in self.save_directory.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    automation_data = json.load(f)
                    
                name = automation_data.get('name', filepath.stem)
                self.automations[name] = automation_data
                
            except Exception as e:
                print(f"⚠️ Error cargando {filepath}: {e}")
                
        print(f"📚 Cargadas {len(self.automations)} automatizaciones")
        
    def list_automations(self):
        """Lista todas las automatizaciones disponibles"""
        if not self.automations:
            print("📭 No hay automatizaciones guardadas")
            return []
            
        print("📋 Automatizaciones disponibles:")
        print("-" * 60)
        
        automations_list = []
        for name, data in self.automations.items():
            duration = self._calculate_duration(data['events'])
            created = data.get('created_date', 'Desconocida')
            description = data.get('description', 'Sin descripción')
            
            print(f"🎯 {name}")
            print(f"   📝 {description}")
            print(f"   ⏱️  {len(data['events'])} eventos, {duration:.2f}s")
            print(f"   📅 Creada: {created[:10]}")
            if data.get('tags'):
                print(f"   🏷️  Tags: {', '.join(data['tags'])}")
            print()
            
            automations_list.append({
                'name': name,
                'description': description,
                'event_count': len(data['events']),
                'duration': duration,
                'created_date': created,
                'tags': data.get('tags', [])
            })
            
        return automations_list
        
    def delete_automation(self, name):
        """Elimina una automatización"""
        if name not in self.automations:
            print(f"❌ Automatización '{name}' no encontrada")
            return False
            
        safe_name = self._sanitize_filename(name)
        filename = f"{safe_name}.json"
        filepath = self.save_directory / filename
        
        try:
            if filepath.exists():
                filepath.unlink()
                
            del self.automations[name]
            print(f"🗑️ Automatización '{name}' eliminada exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error eliminando automatización: {e}")
            return False
            
    def update_automation(self, name, new_events=None, new_description=None, new_tags=None):
        """Actualiza una automatización existente"""
        if name not in self.automations:
            print(f"❌ Automatización '{name}' no encontrada")
            return False
            
        automation_data = self.automations[name]
        
        if new_events is not None:
            automation_data['events'] = new_events
            automation_data['event_count'] = len(new_events)
            automation_data['duration'] = self._calculate_duration(new_events)
            
        if new_description is not None:
            automation_data['description'] = new_description
            
        if new_tags is not None:
            automation_data['tags'] = new_tags
            
        automation_data['modified_date'] = datetime.now().isoformat()
        
        # Guardar cambios
        return self.save_automation(name, automation_data['events'], 
                                  automation_data['description'], 
                                  automation_data['tags'])
                                  
    def search_automations(self, query):
        """Busca automatizaciones por nombre, descripción o tags"""
        results = []
        query_lower = query.lower()
        
        for name, data in self.automations.items():
            # Buscar en nombre
            if query_lower in name.lower():
                results.append(name)
                continue
                
            # Buscar en descripción
            description = data.get('description', '').lower()
            if query_lower in description:
                results.append(name)
                continue
                
            # Buscar en tags
            tags = [tag.lower() for tag in data.get('tags', [])]
            if any(query_lower in tag for tag in tags):
                results.append(name)
                continue
                
        if results:
            print(f"🔍 Encontradas {len(results)} automatizaciones para '{query}':")
            for name in results:
                print(f"  - {name}")
        else:
            print(f"🔍 No se encontraron automatizaciones para '{query}'")
            
        return results
        
    def get_automation_info(self, name):
        """Obtiene información detallada de una automatización"""
        if name not in self.automations:
            print(f"❌ Automatización '{name}' no encontrada")
            return None
            
        data = self.automations[name]
        return {
            'name': name,
            'description': data.get('description', ''),
            'event_count': len(data['events']),
            'duration': self._calculate_duration(data['events']),
            'created_date': data.get('created_date', ''),
            'modified_date': data.get('modified_date', ''),
            'tags': data.get('tags', []),
            'file_size': self._get_file_size(name)
        }
        
    def _calculate_duration(self, events):
        """Calcula la duración total de una automatización"""
        if not events:
            return 0.0
            
        # Encontrar el tiempo del último evento
        max_time = max(event.get('time', 0) for event in events)
        return max_time
        
    def _sanitize_filename(self, filename):
        """Convierte un nombre en un nombre de archivo seguro"""
        # Reemplazar caracteres problemáticos
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
            
        # Limitar longitud
        if len(filename) > 50:
            filename = filename[:50]
            
        return filename
        
    def _get_file_size(self, name):
        """Obtiene el tamaño del archivo de una automatización"""
        safe_name = self._sanitize_filename(name)
        filename = f"{safe_name}.json"
        filepath = self.save_directory / filename
        
        if filepath.exists():
            return filepath.stat().st_size
        return 0

# Funciones de conveniencia
def save_automation(name, events, description="", tags=None):
    """Función para guardar una automatización rápidamente"""
    manager = AutomationManager()
    return manager.save_automation(name, events, description, tags)

def load_automation(name):
    """Función para cargar una automatización rápidamente"""
    manager = AutomationManager()
    return manager.load_automation(name)

def list_all_automations():
    """Función para listar todas las automatizaciones"""
    manager = AutomationManager()
    return manager.list_automations()

if __name__ == "__main__":
    # Ejemplo de uso
    print("💾 Módulo de gestión de automatizaciones")
    print("📁 Directorio de guardado: automations/")
    
    manager = AutomationManager()
    manager.list_automations()
