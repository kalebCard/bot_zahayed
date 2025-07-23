import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from datetime import datetime

# Importar nuestros módulos
from app.rec import AutomationRecorder, record_automation
from app.play import AutomationPlayer, play_automation
from app.save import AutomationManager
from app.edit import AutomationEditor

class AutomationGUI:
    def __init__(self, parent=None):
        if parent is None:
            self.root = tk.Tk()
            self.is_embedded = False
        else:
            self.root = parent
            self.is_embedded = True
        if not self.is_embedded:
            self.root.title("Auto-Task - Gestor de Automatizaciones")
            self.root.geometry("800x600")
            self.root.configure(bg='#f0f0f0')
        
        # Inicializar componentes
        self.manager = AutomationManager()
        self.recorder = None
        self.player = None
        self.editor = None
        self.recording_thread = None
        self.playing_thread = None
        
        # Variables de control
        self.is_recording = False
        self.is_playing = False
        self.is_paused = False  # Nueva variable para controlar pausa
        
        self.setup_ui()
        self.refresh_automation_list()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="🎯 Auto-Task", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Panel izquierdo - Controles principales
        left_frame = ttk.LabelFrame(main_frame, text="🎮 Controles", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Botones de grabación
        record_frame = ttk.LabelFrame(left_frame, text="🎙️ Grabación", padding="5")
        record_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.record_btn = ttk.Button(record_frame, text="🎙️ Iniciar Grabación", 
                                    command=self.start_recording)
        self.record_btn.pack(fill=tk.X, pady=2)
        
        self.stop_record_btn = ttk.Button(record_frame, text="⏹️ Detener Grabación", 
                                        command=self.stop_recording, state='disabled')
        self.stop_record_btn.pack(fill=tk.X, pady=2)
        
        # Indicador de estado de grabación
        self.recording_status = ttk.Label(record_frame, text="", foreground="gray")
        self.recording_status.pack(fill=tk.X, pady=2)
        
        # Botones de reproducción
        play_frame = ttk.LabelFrame(left_frame, text="▶️ Reproducción", padding="5")
        play_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.play_btn = ttk.Button(play_frame, text="▶️ Reproducir", 
                                  command=self.play_selected)
        self.play_btn.pack(fill=tk.X, pady=2)
        
        self.pause_btn = ttk.Button(play_frame, text="⏸️ Pausar", 
                                   command=self.pause_playing, state='disabled')
        self.pause_btn.pack(fill=tk.X, pady=2)
        
        self.resume_btn = ttk.Button(play_frame, text="▶️ Reanudar", 
                                    command=self.resume_playing, state='disabled')
        self.resume_btn.pack(fill=tk.X, pady=2)
        
        self.stop_play_btn = ttk.Button(play_frame, text="⏹️ Detener", 
                                       command=self.stop_playing, state='disabled')
        self.stop_play_btn.pack(fill=tk.X, pady=2)
        
        self.user_input_btn = ttk.Button(play_frame, text="⌨️ Pausa para Ctrl+C/V", 
                                        command=self.pause_for_user_input, state='disabled')
        self.user_input_btn.pack(fill=tk.X, pady=2)
        
        self.emergency_btn = ttk.Button(play_frame, text="🚨 Pausa de Emergencia", 
                                       command=self.emergency_pause, state='disabled')
        self.emergency_btn.pack(fill=tk.X, pady=2)
        
        self.copy_paste_btn = ttk.Button(play_frame, text="⌨️ Pausa para Copiar/Pegar", 
                                        command=self.copy_paste_pause, state='disabled')
        self.copy_paste_btn.pack(fill=tk.X, pady=2)
        
        # Checkbox para compatibilidad con Ctrl+C/V
        self.copy_paste_compat_var = tk.BooleanVar(value=True)
        self.copy_paste_check = ttk.Checkbutton(play_frame, 
                                               text="✅ Compatibilidad Ctrl+C/V", 
                                               variable=self.copy_paste_compat_var,
                                               command=self.toggle_copy_paste_compatibility)
        self.copy_paste_check.pack(fill=tk.X, pady=2)
        
        # Configuración de reproducción
        config_frame = ttk.LabelFrame(left_frame, text="⚙️ Configuración", padding="5")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(config_frame, text="Velocidad:").pack(anchor=tk.W)
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(config_frame, from_=0.1, to=3.0, 
                               variable=self.speed_var, orient=tk.HORIZONTAL)
        speed_scale.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(config_frame, text="Repeticiones:").pack(anchor=tk.W)
        self.repeats_var = tk.IntVar(value=1)
        repeats_spin = ttk.Spinbox(config_frame, from_=1, to=100, 
                                  textvariable=self.repeats_var, width=10)
        repeats_spin.pack(anchor=tk.W, pady=(0, 5))
        
        # Botones de gestión
        manage_frame = ttk.LabelFrame(left_frame, text="📁 Gestión", padding="5")
        manage_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.edit_btn = ttk.Button(manage_frame, text="✏️ Editar", 
                                  command=self.edit_selected)
        self.edit_btn.pack(fill=tk.X, pady=2)
        
        self.delete_btn = ttk.Button(manage_frame, text="🗑️ Eliminar", 
                                    command=self.delete_selected)
        self.delete_btn.pack(fill=tk.X, pady=2)
        
        self.export_btn = ttk.Button(manage_frame, text="📤 Exportar", 
                                    command=self.export_selected)
        self.export_btn.pack(fill=tk.X, pady=2)
        
        # Panel central - Lista de automatizaciones
        center_frame = ttk.LabelFrame(main_frame, text="📋 Automatizaciones", padding="10")
        center_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Barra de búsqueda
        search_frame = ttk.Frame(center_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="🔍 Buscar:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Lista de automatizaciones
        list_frame = ttk.Frame(center_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview para la lista
        columns = ('Nombre', 'Descripción', 'Eventos', 'Duración', 'Fecha')
        self.automation_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.automation_tree.heading('Nombre', text='Nombre')
        self.automation_tree.heading('Descripción', text='Descripción')
        self.automation_tree.heading('Eventos', text='Eventos')
        self.automation_tree.heading('Duración', text='Duración')
        self.automation_tree.heading('Fecha', text='Fecha')
        
        self.automation_tree.column('Nombre', width=150)
        self.automation_tree.column('Descripción', width=200)
        self.automation_tree.column('Eventos', width=80)
        self.automation_tree.column('Duración', width=80)
        self.automation_tree.column('Fecha', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.automation_tree.yview)
        self.automation_tree.configure(yscrollcommand=scrollbar.set)
        
        self.automation_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Panel derecho - Información y estadísticas
        right_frame = ttk.LabelFrame(main_frame, text="📊 Información", padding="10")
        right_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        # Información de la automatización seleccionada
        self.info_text = tk.Text(right_frame, width=30, height=20, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Barra de estado
        self.status_var = tk.StringVar(value="Listo")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Eventos
        self.automation_tree.bind('<<TreeviewSelect>>', self.on_automation_select)
        
    def start_recording(self):
        """Inicia la grabación en un hilo separado"""
        if self.is_recording:
            return
            
        self.is_recording = True
        self.record_btn.config(state='disabled')
        self.stop_record_btn.config(state='normal')
        self.recording_status.config(text="🔴 Grabando...", foreground="red")
        self.status_var.set("🎙️ Grabando... Solo clics, teclado y scroll. Haz clic en 'Detener Grabación' para finalizar")
        
        # Iniciar grabación en hilo separado
        self.recording_thread = threading.Thread(target=self._record_automation)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
    def _record_automation(self):
        """Función de grabación ejecutada en hilo separado"""
        try:
            # Crear grabador personalizado
            from app.rec import AutomationRecorder
            self.recorder = AutomationRecorder()
            self.recorder.start_recording()
            
            # Mantener grabación activa hasta que se detenga
            while self.recorder.recording and self.is_recording:
                time.sleep(0.1)
            
            # Detener grabación
            events = self.recorder.stop_recording()
            
            if events and len(events) > 0:
                # Mostrar diálogo para guardar
                self.root.after(0, lambda: self.save_recorded_automation(events))
            else:
                self.root.after(0, lambda: self.status_var.set("❌ Grabación cancelada"))
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"❌ Error en grabación: {e}"))
        finally:
            self.root.after(0, self._stop_recording_ui)
            
    def _stop_recording_ui(self):
        """Actualiza la UI después de detener la grabación"""
        self.is_recording = False
        self.record_btn.config(state='normal')
        self.stop_record_btn.config(state='disabled')
        self.recording_status.config(text="✅ Listo para grabar", foreground="green")
        
    def stop_recording(self):
        """Detiene la grabación"""
        self.is_recording = False
        if self.recorder:
            self.recorder.stop_recording()
        self._stop_recording_ui()
        self.status_var.set("⏹️ Grabación detenida")
        
    def save_recorded_automation(self, events):
        """Muestra diálogo para guardar la automatización grabada"""
        dialog = SaveAutomationDialog(self.root, events)
        if dialog.result:
            name, description, tags = dialog.result
            if self.manager.save_automation(name, events, description, tags):
                self.refresh_automation_list()
                self.status_var.set(f"✅ Automatización '{name}' guardada")
            else:
                self.status_var.set("❌ Error guardando automatización")
                
    def play_selected(self):
        """Reproduce la automatización seleccionada"""
        selection = self.automation_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona una automatización")
            return
            
        automation_name = selection[0]
        events = self.manager.load_automation(automation_name)
        
        if not events:
            messagebox.showerror("Error", f"No se pudo cargar la automatización '{automation_name}'")
            return
            
        # Configurar reproducción
        speed = self.speed_var.get()
        repeats = self.repeats_var.get()
        
        self.is_playing = True
        self.is_paused = False
        self.play_btn.config(state='disabled')
        self.pause_btn.config(state='normal')
        self.resume_btn.config(state='disabled')
        self.stop_play_btn.config(state='normal')
        self.user_input_btn.config(state='normal')
        self.emergency_btn.config(state='normal')
        self.copy_paste_btn.config(state='normal')
        self.status_var.set(f"▶️ Reproduciendo '{automation_name}'...")
        
        # Reproducir en hilo separado
        self.playing_thread = threading.Thread(
            target=self._play_automation, 
            args=(automation_name, events, speed, repeats)
        )
        self.playing_thread.daemon = True
        self.playing_thread.start()
        
    def _play_automation(self, name, events, speed, repeats):
        """Reproduce la automatización en hilo separado"""
        try:
            self.player = AutomationPlayer()
            self.player.set_playback_speed(speed)
            self.player.set_repeat_count(repeats)
            
            success = self.player.play_automation(events)
            
            if success:
                self.root.after(0, lambda: self.status_var.set(f"✅ Reproducción completada"))
            else:
                self.root.after(0, lambda: self.status_var.set("❌ Reproducción interrumpida"))
                
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"❌ Error en reproducción: {e}"))
        finally:
            self.root.after(0, self._stop_playing_ui)
            
    def _stop_playing_ui(self):
        """Actualiza la UI después de detener la reproducción"""
        self.is_playing = False
        self.is_paused = False
        self.play_btn.config(state='normal')
        self.pause_btn.config(state='disabled')
        self.resume_btn.config(state='disabled')
        self.stop_play_btn.config(state='disabled')
        self.user_input_btn.config(state='disabled')
        self.emergency_btn.config(state='disabled')
        self.copy_paste_btn.config(state='disabled')
        
    def pause_playing(self):
        """Pausa la reproducción"""
        if self.player:
            self.player.pause_playback()
            self.is_paused = True
            self.pause_btn.config(state='disabled')
            self.resume_btn.config(state='normal')
            self.status_var.set("⏸️ Reproducción pausada")
        
    def resume_playing(self):
        """Reanuda la reproducción"""
        if self.player:
            self.player.resume_playback()
            self.is_paused = False
            self.pause_btn.config(state='normal')
            self.resume_btn.config(state='disabled')
            self.status_var.set("▶️ Reproducción reanudada")
        
    def stop_playing(self):
        """Detiene la reproducción"""
        if self.player:
            self.player.stop_playback()
        self.is_paused = False
        self._stop_playing_ui()
        self.status_var.set("⏹️ Reproducción detenida")
    
    def pause_for_user_input(self):
        """Pausa la reproducción para permitir Ctrl+C y Ctrl+V"""
        if self.player and self.is_playing:
            self.player.pause_for_user_input(3.0)  # Pausa de 3 segundos
            self.status_var.set("⌨️ Pausa para entrada del usuario - Usa Ctrl+C y Ctrl+V")
        else:
            messagebox.showinfo("Información", "No hay reproducción activa")
    
    def emergency_pause(self):
        """Pausa de emergencia para operaciones de copiar/pegar"""
        if self.player and self.is_playing:
            self.player.emergency_pause_for_copy_paste()
            self.status_var.set("🚨 Pausa de emergencia completada")
        else:
            messagebox.showinfo("Información", "No hay reproducción activa")
    
    def copy_paste_pause(self):
        """Pausa específica para operaciones de copiar/pegar"""
        if self.player and self.is_playing:
            self.player.pause_for_copy_paste_operation(5.0)  # 5 segundos
            self.status_var.set("⌨️ Pausa para copiar/pegar completada")
        else:
            messagebox.showinfo("Información", "No hay reproducción activa")
    
    def toggle_copy_paste_compatibility(self):
        """Alterna la compatibilidad con Ctrl+C y Ctrl+V"""
        if self.player:
            if self.copy_paste_compat_var.get():
                self.player.enable_copy_paste_compatibility()
                self.status_var.set("✅ Compatibilidad con Ctrl+C/V habilitada")
            else:
                self.player.disable_copy_paste_compatibility()
                self.status_var.set("❌ Compatibilidad con Ctrl+C/V deshabilitada")
        else:
            messagebox.showinfo("Información", "No hay reproducción activa")
        
    def edit_selected(self):
        """Abre el editor para la automatización seleccionada"""
        selection = self.automation_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona una automatización")
            return
            
        automation_name = selection[0]
        self.editor = AutomationEditor()
        
        if self.editor.load_for_editing(automation_name):
            # Abrir ventana de edición
            EditAutomationWindow(self.root, self.editor, self.refresh_automation_list)
        else:
            messagebox.showerror("Error", f"No se pudo cargar '{automation_name}' para edición")
            
    def delete_selected(self):
        """Elimina las automatizaciones seleccionadas"""
        selection = self.automation_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona una o más automatizaciones")
            return

        nombres = [self.automation_tree.item(item, 'values')[0] for item in selection]
        if not nombres:
            return

        if messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar las siguientes automatizaciones?\n\n" + "\n".join(nombres)):
            eliminadas = []
            errores = []
            for nombre in nombres:
                if self.manager.delete_automation(nombre):
                    eliminadas.append(nombre)
                else:
                    errores.append(nombre)
            self.refresh_automation_list()
            if eliminadas:
                self.status_var.set(f"🗑️ Eliminadas: {', '.join(eliminadas)}")
            if errores:
                messagebox.showerror("Error", f"No se pudieron eliminar: {', '.join(errores)}")
                
    def export_selected(self):
        """Exporta la automatización seleccionada"""
        selection = self.automation_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona una automatización")
            return
            
        automation_name = selection[0]
        events = self.manager.load_automation(automation_name)
        
        if not events:
            messagebox.showerror("Error", f"No se pudo cargar '{automation_name}'")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Exportar automatización"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    import json
                    json.dump(events, f, indent=2, ensure_ascii=False)
                self.status_var.set(f"📤 '{automation_name}' exportada a {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error exportando: {e}")
                
    def refresh_automation_list(self):
        """Actualiza la lista de automatizaciones"""
        # Limpiar lista actual
        for item in self.automation_tree.get_children():
            self.automation_tree.delete(item)
            
        # Obtener automatizaciones
        automations = self.manager.list_automations()
        
        # Filtrar por búsqueda
        search_term = self.search_var.get().lower()
        if search_term:
            automations = [a for a in automations if search_term in a['name'].lower() or 
                         search_term in a['description'].lower()]
            
        # Agregar a la lista
        for automation in automations:
            self.automation_tree.insert('', 'end', automation['name'], values=(
                automation['name'],
                automation['description'][:50] + "..." if len(automation['description']) > 50 else automation['description'],
                automation['event_count'],
                f"{automation['duration']:.2f}s",
                automation['created_date'][:10] if automation['created_date'] else "Desconocida"
            ))
            
    def on_search_change(self, *args):
        """Maneja cambios en la búsqueda"""
        self.refresh_automation_list()
        
    def on_automation_select(self, event):
        """Maneja la selección de una automatización"""
        selection = self.automation_tree.selection()
        if selection:
            automation_name = selection[0]
            info = self.manager.get_automation_info(automation_name)
            
            if info:
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, f"📋 Información de '{automation_name}'\n")
                self.info_text.insert(tk.END, "=" * 40 + "\n\n")
                self.info_text.insert(tk.END, f"📝 Descripción: {info['description']}\n\n")
                self.info_text.insert(tk.END, f"📊 Eventos: {info['event_count']}\n")
                self.info_text.insert(tk.END, f"⏱️ Duración: {info['duration']:.2f}s\n")
                self.info_text.insert(tk.END, f"📅 Creada: {info['created_date'][:19]}\n")
                self.info_text.insert(tk.END, f"📝 Modificada: {info['modified_date'][:19]}\n")
                self.info_text.insert(tk.END, f"📁 Tamaño: {info['file_size']} bytes\n\n")
                
                if info['tags']:
                    self.info_text.insert(tk.END, f"🏷️ Tags: {', '.join(info['tags'])}\n")
                    
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()

class SaveAutomationDialog:
    def __init__(self, parent, events):
        self.result = None
        
        # Crear ventana de diálogo
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Guardar Automatización")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar en la ventana padre
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Contenido
        ttk.Label(self.dialog, text="💾 Guardar Automatización", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Nombre
        ttk.Label(self.dialog, text="Nombre:").pack(anchor=tk.W, padx=20)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(self.dialog, textvariable=self.name_var, width=40)
        name_entry.pack(padx=20, pady=(0, 10))
        name_entry.focus()
        
        # Descripción
        ttk.Label(self.dialog, text="Descripción:").pack(anchor=tk.W, padx=20)
        self.desc_var = tk.StringVar()
        desc_entry = ttk.Entry(self.dialog, textvariable=self.desc_var, width=40)
        desc_entry.pack(padx=20, pady=(0, 10))
        
        # Tags
        ttk.Label(self.dialog, text="Tags (separados por comas):").pack(anchor=tk.W, padx=20)
        self.tags_var = tk.StringVar()
        tags_entry = ttk.Entry(self.dialog, textvariable=self.tags_var, width=40)
        tags_entry.pack(padx=20, pady=(0, 20))
        
        # Estadísticas
        duration = max(event.get('time', 0) for event in events)
        stats_text = f"📊 Estadísticas: {len(events)} eventos, {duration:.2f}s duración"
        ttk.Label(self.dialog, text=stats_text).pack(pady=10)
        
        # Botones
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="💾 Guardar", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Cancelar", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        # Eventos
        self.dialog.bind('<Return>', lambda e: self.save())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        # Esperar hasta que se cierre
        self.dialog.wait_window()
        
    def save(self):
        """Guarda la automatización"""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Advertencia", "Por favor ingresa un nombre")
            return
            
        description = self.desc_var.get().strip()
        tags = [tag.strip() for tag in self.tags_var.get().split(',') if tag.strip()]
        
        self.result = (name, description, tags)
        self.dialog.destroy()
        
    def cancel(self):
        """Cancela la operación"""
        self.dialog.destroy()

class EditAutomationWindow:
    def __init__(self, parent, editor, refresh_callback):
        self.editor = editor
        self.refresh_callback = refresh_callback
        
        # Crear ventana de edición
        self.window = tk.Toplevel(parent)
        self.window.title("✏️ Editor de Automatización")
        self.window.geometry("900x600")
        
        # Configurar interfaz de edición
        self.setup_edit_ui()
        
    def setup_edit_ui(self):
        """Configura la interfaz de edición"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel de eventos
        events_frame = ttk.LabelFrame(main_frame, text="📋 Eventos", padding="10")
        events_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Lista de eventos
        columns = ('#', 'Tipo', 'Detalles', 'Tiempo')
        self.events_tree = ttk.Treeview(events_frame, columns=columns, show='headings', height=15)
        
        self.events_tree.heading('#', text='#')
        self.events_tree.heading('Tipo', text='Tipo')
        self.events_tree.heading('Detalles', text='Detalles')
        self.events_tree.heading('Tiempo', text='Tiempo')
        
        self.events_tree.column('#', width=50)
        self.events_tree.column('Tipo', width=100)
        self.events_tree.column('Detalles', width=400)
        self.events_tree.column('Tiempo', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(events_frame, orient=tk.VERTICAL, command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=scrollbar.set)
        
        self.events_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Panel de controles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X)
        
        # Botones de edición
        edit_buttons = ttk.Frame(controls_frame)
        edit_buttons.pack(side=tk.LEFT)
        
        ttk.Button(edit_buttons, text="🗑️ Eliminar", command=self.delete_selected_event).pack(side=tk.LEFT, padx=2)
        ttk.Button(edit_buttons, text="➕ Duplicar", command=self.duplicate_selected_event).pack(side=tk.LEFT, padx=2)
        ttk.Button(edit_buttons, text="⏱️ Ajustar Tiempos", command=self.adjust_timing).pack(side=tk.LEFT, padx=2)
        
        # Botones de guardado
        save_buttons = ttk.Frame(controls_frame)
        save_buttons.pack(side=tk.RIGHT)
        
        ttk.Button(save_buttons, text="💾 Guardar", command=self.save_changes).pack(side=tk.LEFT, padx=2)
        ttk.Button(save_buttons, text="❌ Cancelar", command=self.window.destroy).pack(side=tk.LEFT, padx=2)
        
        # Cargar eventos
        self.load_events()
        
    def load_events(self):
        """Carga los eventos en la lista"""
        try:
            # Limpiar lista actual
            for item in self.events_tree.get_children():
                self.events_tree.delete(item)
            
            # Mostrar progreso si hay muchos eventos
            total_events = len(self.editor.current_events)
            if total_events > 1000:
                self.window.title("✏️ Editor de Automatización - Cargando...")
                self.window.update()
            
            for i, event in enumerate(self.editor.current_events):
                event_type = event.get('type', 'unknown')
                time_str = f"{event.get('time', 0):.3f}s"
                
                if event_type == 'mouse_move':
                    details = f"Mover a ({event['x']}, {event['y']})"
                elif event_type == 'mouse_click':
                    button = event.get('button', 'unknown')
                    action = "Presionar" if event.get('pressed', False) else "Soltar"
                    details = f"{action} {button} en ({event['x']}, {event['y']})"
                elif event_type == 'key_press':
                    details = f"Presionar {event.get('key', 'unknown')}"
                elif event_type == 'key_release':
                    details = f"Soltar {event.get('key', 'unknown')}"
                else:
                    details = str(event)
                    
                self.events_tree.insert('', 'end', i, values=(i+1, event_type, details, time_str))
                
                # Actualizar progreso cada 100 eventos
                if total_events > 1000 and i % 100 == 0:
                    self.window.title(f"✏️ Editor de Automatización - Cargando... ({i}/{total_events})")
                    self.window.update()
            
            # Restaurar título
            self.window.title("✏️ Editor de Automatización")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando eventos: {e}")
            self.window.destroy()
            
    def delete_selected_event(self):
        """Elimina el evento seleccionado"""
        try:
            selection = self.events_tree.selection()
            if selection:
                index = int(selection[0])
                if self.editor.delete_event(index):
                    self.load_events()
                    messagebox.showinfo("Éxito", "Evento eliminado correctamente")
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el evento")
            else:
                messagebox.showwarning("Advertencia", "Por favor selecciona un evento para eliminar")
        except Exception as e:
            messagebox.showerror("Error", f"Error eliminando evento: {e}")
                
    def duplicate_selected_event(self):
        """Duplica el evento seleccionado"""
        try:
            selection = self.events_tree.selection()
            if selection:
                index = int(selection[0])
                if self.editor.duplicate_event(index):
                    self.load_events()
                    messagebox.showinfo("Éxito", "Evento duplicado correctamente")
                else:
                    messagebox.showerror("Error", "No se pudo duplicar el evento")
            else:
                messagebox.showwarning("Advertencia", "Por favor selecciona un evento para duplicar")
        except Exception as e:
            messagebox.showerror("Error", f"Error duplicando evento: {e}")
                
    def adjust_timing(self):
        """Ajusta los tiempos de la automatización"""
        try:
            factor = tk.simpledialog.askfloat("Ajustar Tiempos", 
                                             "Factor de tiempo (1.0 = normal, 2.0 = doble velocidad):",
                                             initialvalue=1.0)
            if factor and factor > 0:
                if self.editor.adjust_timing(factor):
                    self.load_events()
                    messagebox.showinfo("Éxito", f"Tiempos ajustados por factor {factor}")
                else:
                    messagebox.showerror("Error", "No se pudieron ajustar los tiempos")
        except Exception as e:
            messagebox.showerror("Error", f"Error ajustando tiempos: {e}")
                

                
    def save_changes(self):
        """Guarda los cambios realizados"""
        try:
            if self.editor.save_changes():
                self.refresh_callback()
                messagebox.showinfo("Éxito", "Cambios guardados exitosamente")
                self.window.destroy()
            else:
                messagebox.showerror("Error", "No se pudieron guardar los cambios")
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando cambios: {e}")

if __name__ == "__main__":
    # Ejecutar la aplicación
    app = AutomationGUI()
    app.run()
