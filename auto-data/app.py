import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from dato import Dato
from db_manager import DatabaseManager
from data_manager import DataManager


class TkinterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Datos - Tkinter")
        self.root.geometry("1200x800")
        
        # Inicializar componentes
        self.db_manager = DatabaseManager()
        self.data_manager = DataManager(self.db_manager)
        
        # Variables
        self.modo_codigo = tk.StringVar(value='random')
        self.dato_seleccionado = None
        
        self.setup_ui()
        self.cargar_datos()
    
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        # Frame izquierdo - Formulario
        form_frame = ttk.LabelFrame(main_frame, text="Formulario de Datos", padding="10")
        form_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        
        # ...existing code...
        
        ttk.Label(form_frame, text="Nombres (uno por línea):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.nombres_text = scrolledtext.ScrolledText(form_frame, width=30, height=5)
        self.nombres_text.grid(row=1, column=1, sticky="we", pady=2)
        
        # Modo de código
        ttk.Label(form_frame, text="Modo de código:").grid(row=2, column=0, sticky=tk.W, pady=2)
        codigo_frame = ttk.Frame(form_frame)
        codigo_frame.grid(row=2, column=1, sticky="we", pady=2)
        
        ttk.Radiobutton(codigo_frame, text="Aleatorio", variable=self.modo_codigo, 
                       value='random').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(codigo_frame, text="Termina en 5", variable=self.modo_codigo, 
                       value='5').pack(side=tk.LEFT)
        
        # Botones del formulario
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Guardar Datos", 
                  command=self.guardar_datos).pack(side=tk.LEFT, padx=(0, 10))
        # ...existing code...
        ttk.Button(button_frame, text="Limpiar Formulario", 
                  command=self.limpiar_formulario).pack(side=tk.LEFT)
        
        # Frame derecho - Direcciones
        dir_frame = ttk.LabelFrame(main_frame, text="Gestión de Direcciones", padding="10")
        dir_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        
        ttk.Label(dir_frame, text="Nuevas direcciones:").grid(row=0, column=0, sticky=tk.W)
        self.direcciones_text = scrolledtext.ScrolledText(dir_frame, width=30, height=5)
        self.direcciones_text.grid(row=1, column=0, sticky="we", pady=5)
        
        ttk.Button(dir_frame, text="Agregar Direcciones", 
                  command=self.agregar_direcciones).grid(row=2, column=0, pady=5)
        
        # Contador de direcciones
        self.contador_label = ttk.Label(dir_frame, text="Direcciones disponibles: 0")
        self.contador_label.grid(row=3, column=0, pady=5)
        
        # Frame inferior - Tabla de datos
        table_frame = ttk.LabelFrame(main_frame, text="Datos Registrados", padding="10")
        table_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        
        # Crear Treeview para la tabla
        columns = ('ID', 'Código', 'Nombre', 'Dirección', 'ZIP4', 
                  'Amount Current Any', 'Amount Current Regular', 'Amount PAS Any', 'Amount PAS Regular')
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, minwidth=80)
        
        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Botones de la tabla
        table_button_frame = ttk.Frame(table_frame)
        table_button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(table_button_frame, text="Editar Seleccionado", 
                  command=self.editar_dato).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(table_button_frame, text="Eliminar Seleccionado", 
                  command=self.eliminar_dato).pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón para eliminar el primer dato
        ttk.Button(table_button_frame, text="⏮️ Borrar Primero", 
                  command=self.eliminar_primer_dato).pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón para eliminar todos los datos (con estilo de advertencia)
        ttk.Button(table_button_frame, text="🗑️ Borrar Todos los Datos", 
                  command=self.eliminar_todos_datos, 
                  style="Danger.TButton").pack(side=tk.LEFT, padx=(10, 0))
        
        # Botón para resetear IDs y borrar todos los datos
        ttk.Button(table_button_frame, text="🔄 Resetear IDs (empezar en 101)", 
                  command=self.resetear_ids_y_datos, style="Danger.TButton").pack(side=tk.LEFT, padx=(10, 0))
        
        # Configurar grid weights
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        dir_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)
        
        # Configurar estilos
        style = ttk.Style()
        style.configure("Danger.TButton", font=("Arial", 10, "bold"), padding=8)
        
        # ...existing code...
    
    def guardar_datos(self):
        """Guardar datos desde el formulario"""
        try:
            nombres_text = self.nombres_text.get("1.0", tk.END).strip()
            if not nombres_text:
                messagebox.showerror("Error", "Debe ingresar al menos un nombre")
                return
            nombres = [n.strip().upper() for n in nombres_text.split('\n') if n.strip()]
            if len(nombres) > len(self.data_manager.direcciones_disponibles):
                messagebox.showerror("Error", 
                                   f"No hay suficientes direcciones disponibles. "
                                   f"Necesitas {len(nombres)} pero solo tienes {len(self.data_manager.direcciones_disponibles)}")
                return
            # Crear datos
            datos_creados = 0
            for nombre in nombres:
                try:
                    # Generar datos
                    codigo = self.data_manager.generar_codigo_aleatorio(self.modo_codigo.get())
                    amount_current_any = self.data_manager.generar_numero_decimal()
                    amount_current_regular = int(float(amount_current_any))
                    amount_pas_any = self.data_manager.generar_numero_decimal()
                    amount_pas_regular = int(float(amount_pas_any))
                    # Obtener dirección
                    dir_obj = self.data_manager.obtener_direccion_unica()
                    # Crear objeto Dato
                    dato = Dato(
                        codigo=codigo,
                        nombre=nombre,
                        drireccion=dir_obj["direccion"],
                        zip4=dir_obj["zip4"],
                        amount_current_any=float(amount_current_any),
                        amount_current_regular=amount_current_regular,
                        amount_pas_any=float(amount_pas_any),
                        amount_pas_regular=amount_pas_regular
                    )
                    # Guardar en base de datos
                    self.db_manager.crear_dato(dato)
                    datos_creados += 1
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Error al crear dato para {nombre}: {str(e)}")
                    continue
            
            if datos_creados > 0:
                messagebox.showinfo("Éxito", f"Se crearon {datos_creados} registros exitosamente")
                self.limpiar_formulario()
                self.cargar_datos()
                self.actualizar_contador_direcciones()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar datos: {str(e)}")
    
    def limpiar_formulario(self):
        """Limpiar el formulario"""
        self.fecha_entry.delete(0, tk.END)
        self.fecha_entry.insert(0, datetime.now().strftime("%B %d, %Y"))
        self.nombres_text.delete("1.0", tk.END)
        self.dato_seleccionado = None
    
    def cargar_datos(self):
        """Cargar datos en la tabla"""
        try:
            # Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Cargar datos de la base de datos
            datos = self.db_manager.leer_datos()
            
            # Insertar en la tabla
            for dato in datos:
                def fmt(val):
                    try:
                        return f"{float(val):.2f}"
                    except Exception:
                        return val
                self.tree.insert('', 'end', values=(
                    dato.id, dato.fecha, dato.codigo, dato.nombre, dato.drireccion,
                    dato.zip4, fmt(dato.amount_current_any), dato.amount_current_regular,
                    fmt(dato.amount_pas_any), dato.amount_pas_regular
                ))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
    
    def editar_dato(self):
        """Editar el dato seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un dato para editar")
            return
        
        # Obtener datos del item seleccionado
        item = self.tree.item(selection[0])
        values = item['values']
        
        # Crear ventana de edición
        self.crear_ventana_edicion(values)
    
    def copiar_dato_seleccionado(self):
        """Copiar el dato seleccionado al portapapeles sin mensajes"""
        selection = self.tree.selection()
        if not selection:
            return  # No mostrar mensaje, simplemente no hacer nada
        
        # Obtener datos del item seleccionado
        item = self.tree.item(selection[0])
        values = item['values']
        
        # Unir los valores en una sola línea, separados por tabulaciones
        texto = '\t'.join(str(v) for v in values)
        
        # Copiar al portapapeles sin mensajes
        self.root.clipboard_clear()
        self.root.clipboard_append(texto)
        self.root.update()
    
    def pegar_datos(self):
        """Pegar datos desde el portapapeles"""
        try:
            # Obtener datos del portapapeles
            datos_pegados = self.root.clipboard_get()
            
            # Si hay datos en el portapapeles, intentar procesarlos
            if datos_pegados and datos_pegados.strip():
                # Dividir por tabulaciones si es una línea con datos
                if '\t' in datos_pegados:
                    valores = datos_pegados.strip().split('\t')
                    if len(valores) >= 4:  # Mínimo ID, fecha, código, nombre
                        # Intentar insertar en el formulario
                        if len(valores) > 1:
                            self.fecha_entry.delete(0, tk.END)
                            self.fecha_entry.insert(0, valores[1] if len(valores) > 1 else "")
                        
                        if len(valores) > 3:
                            self.nombres_text.delete("1.0", tk.END)
                            self.nombres_text.insert("1.0", valores[3] if len(valores) > 3 else "")
                else:
                    # Si no hay tabulaciones, tratar como texto simple
                    self.nombres_text.delete("1.0", tk.END)
                    self.nombres_text.insert("1.0", datos_pegados.strip())
        except Exception as e:
            # Si hay error al pegar, simplemente no hacer nada
            print(f"Error al pegar datos: {e}")
            pass
    
    def pegar_en_texto(self, event):
        """Pegar texto en el widget de texto que tiene el foco"""
        try:
            # Obtener datos del portapapeles
            datos_pegados = self.root.clipboard_get()
            
            if datos_pegados and datos_pegados.strip():
                # Obtener el widget que tiene el foco
                widget_foco = self.root.focus_get()
                
                # Si es un widget de texto, insertar el contenido
                if hasattr(widget_foco, 'insert'):
                    # Limpiar el widget y insertar el nuevo contenido
                    widget_foco.delete("1.0", tk.END)
                    widget_foco.insert("1.0", datos_pegados.strip())
                    
                    # Prevenir el comportamiento por defecto
                    return "break"
        except Exception as e:
            print(f"Error al pegar en texto: {e}")
            pass
    
    def copiar_campo_actual(self, event, edit_window):
        """Copiar el campo que tiene el foco en la ventana de edición"""
        try:
            # Obtener el widget que tiene el foco
            widget_foco = edit_window.focus_get()
            
            if widget_foco and hasattr(widget_foco, 'get'):
                valor = widget_foco.get()
                edit_window.clipboard_clear()
                edit_window.clipboard_append(valor)
                edit_window.update()
                return "break"  # Prevenir el comportamiento por defecto
        except Exception as e:
            print(f"Error al copiar campo actual: {e}")
            pass
    
    def copiar_campo_directo(self, entry, edit_window):
        """Copiar directamente el valor de un campo Entry"""
        try:
            valor = entry.get()
            edit_window.clipboard_clear()
            edit_window.clipboard_append(valor)
            edit_window.update()
        except Exception as e:
            print(f"Error al copiar campo directo: {e}")
            pass
    
    def copiar_datos_multiples(self):
        """Copiar múltiples datos seleccionados al portapapeles"""
        selection = self.tree.selection()
        if not selection:
            return  # No mostrar mensaje, simplemente no hacer nada
        
        # Obtener todos los datos seleccionados
        datos_copiados = []
        for item_id in selection:
            item = self.tree.item(item_id)
            values = item['values']
            # Unir los valores en una sola línea, separados por tabulaciones
            linea = '\t'.join(str(v) for v in values)
            datos_copiados.append(linea)
        
        # Unir todas las líneas con saltos de línea
        texto_completo = '\n'.join(datos_copiados)
        
        # Copiar al portapapeles sin mensajes
        self.root.clipboard_clear()
        self.root.clipboard_append(texto_completo)
        self.root.update()
    
    def crear_ventana_edicion(self, values):
        """Crear ventana para editar datos"""
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editar Dato")
        edit_window.geometry("400x500")
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Configurar atajos de teclado para la ventana de edición
        edit_window.bind('<Control-c>', lambda e: self.copiar_campo_actual(e, edit_window))
        edit_window.bind('<Escape>', lambda e: edit_window.destroy())
        
        # Frame principal
        frame = ttk.Frame(edit_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos de edición
        def copiar_campo(entry):
            try:
                valor = entry.get()
                edit_window.clipboard_clear()
                edit_window.clipboard_append(valor)
                edit_window.update()
                # No mostrar mensaje de confirmación - copiar silenciosamente
            except Exception as e:
                print(f"Error al copiar campo: {e}")
                pass

        def fmt(val):
            try:
                return f"{float(val):.2f}"
            except Exception:
                return val

        ttk.Label(frame, text="ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        id_entry = ttk.Entry(frame, state='readonly')
        id_entry.grid(row=0, column=1, sticky="we", pady=2)
        id_entry.configure(state='normal')
        id_entry.insert(0, values[0])
        id_entry.configure(state='readonly')
        ttk.Button(frame, text="Copiar", command=lambda: self.copiar_campo_directo(id_entry, edit_window)).grid(row=0, column=2, padx=2)

        ttk.Label(frame, text="Fecha:").grid(row=1, column=0, sticky=tk.W, pady=2)
        fecha_entry = ttk.Entry(frame)
        fecha_entry.grid(row=1, column=1, sticky="we", pady=2)
        fecha_entry.insert(0, values[1])
        ttk.Button(frame, text="Copiar", command=lambda: self.copiar_campo_directo(fecha_entry, edit_window)).grid(row=1, column=2, padx=2)

        ttk.Label(frame, text="Código:").grid(row=1, column=0, sticky=tk.W, pady=2)
        codigo_entry = ttk.Entry(frame)
        codigo_entry.grid(row=1, column=1, sticky="we", pady=2)
        codigo_entry.insert(0, values[1])
        ttk.Button(frame, text="Copiar", command=lambda: self.copiar_campo_directo(codigo_entry, edit_window)).grid(row=1, column=2, padx=2)

        ttk.Label(frame, text="Nombre:").grid(row=2, column=0, sticky=tk.W, pady=2)
        nombre_entry = ttk.Entry(frame)
        nombre_entry.grid(row=2, column=1, sticky="we", pady=2)
        nombre_entry.insert(0, values[2])
        ttk.Button(frame, text="Copiar", command=lambda: self.copiar_campo_directo(nombre_entry, edit_window)).grid(row=2, column=2, padx=2)

        ttk.Label(frame, text="Dirección:").grid(row=3, column=0, sticky=tk.W, pady=2)
        direccion_entry = ttk.Entry(frame)
        direccion_entry.grid(row=3, column=1, sticky="we", pady=2)
        direccion_entry.insert(0, values[3])
        ttk.Button(frame, text="Copiar", command=lambda: self.copiar_campo_directo(direccion_entry, edit_window)).grid(row=3, column=2, padx=2)

        ttk.Label(frame, text="ZIP4:").grid(row=4, column=0, sticky=tk.W, pady=2)
        zip4_entry = ttk.Entry(frame)
        zip4_entry.grid(row=4, column=1, sticky="we", pady=2)
        zip4_entry.insert(0, values[4] if values[4] else "")
        ttk.Button(frame, text="Copiar", command=lambda: self.copiar_campo_directo(zip4_entry, edit_window)).grid(row=4, column=2, padx=2)

        ttk.Label(frame, text="Amount Current Any:").grid(row=5, column=0, sticky=tk.W, pady=2)
        aca_entry = ttk.Entry(frame)
        aca_entry.grid(row=5, column=1, sticky="we", pady=2)
        aca_entry.insert(0, fmt(values[5]))
        ttk.Button(frame, text="Copiar", command=lambda: self.copiar_campo_directo(aca_entry, edit_window)).grid(row=5, column=2, padx=2)

        ttk.Label(frame, text="Amount Current Regular:").grid(row=6, column=0, sticky=tk.W, pady=2)
        acr_entry = ttk.Entry(frame)
        acr_entry.grid(row=6, column=1, sticky="we", pady=2)
        acr_entry.insert(0, values[6])
        ttk.Button(frame, text="Copiar", command=lambda: self.copiar_campo_directo(acr_entry, edit_window)).grid(row=6, column=2, padx=2)

        ttk.Label(frame, text="Amount PAS Any:").grid(row=7, column=0, sticky=tk.W, pady=2)
        apa_entry = ttk.Entry(frame)
        apa_entry.grid(row=7, column=1, sticky="we", pady=2)
        apa_entry.insert(0, fmt(values[7]))
        ttk.Button(frame, text="Copiar", command=lambda: self.copiar_campo_directo(apa_entry, edit_window)).grid(row=7, column=2, padx=2)

        ttk.Label(frame, text="Amount PAS Regular:").grid(row=8, column=0, sticky=tk.W, pady=2)
        apr_entry = ttk.Entry(frame)
        apr_entry.grid(row=8, column=1, sticky="we", pady=2)
        apr_entry.insert(0, values[8])
        ttk.Button(frame, text="Copiar", command=lambda: self.copiar_campo_directo(apr_entry, edit_window)).grid(row=8, column=2, padx=2)
        
        # Botones
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=10, column=0, columnspan=2, pady=20)

        def guardar_cambios():
            # Obtener los valores actuales de los campos
            valores = [
                id_entry.get(),
                codigo_entry.get(),
                nombre_entry.get(),
                direccion_entry.get(),
                zip4_entry.get(),
                aca_entry.get(),
                acr_entry.get(),
                apa_entry.get(),
                apr_entry.get()
            ]
            # Actualizar en la base de datos
            try:
                conn = self.db_manager.get_connection()
                conn.execute(
                    "UPDATE datos SET codigo=?, nombre=?, drireccion=?, zip4=?, amount_current_any=?, amount_current_regular=?, amount_pas_any=?, amount_pas_regular=? WHERE id=?",
                    (
                        valores[1], valores[2], valores[3], valores[4],
                        float(valores[5]), int(valores[6]), float(valores[7]), int(valores[8]), int(valores[0])
                    )
                )
                conn.commit()
            except Exception as e:
                print(f"Error al guardar edición: {e}")
            # Cerrar ventana y refrescar tabla
            edit_window.destroy()
            self.cargar_datos()

        def copiar_dato():
            # Obtener los valores actuales de los campos
            valores = [
                id_entry.get(),
                fecha_entry.get(),
                codigo_entry.get(),
                nombre_entry.get(),
                direccion_entry.get(),
                zip4_entry.get(),
                aca_entry.get(),
                acr_entry.get(),
                apa_entry.get(),
                apr_entry.get()
            ]
            # Unir los valores en una sola línea, separados por tabulaciones
            texto = '\t'.join(str(v) for v in valores)
            edit_window.clipboard_clear()
            edit_window.clipboard_append(texto)
            edit_window.update()  # Mantener el portapapeles

        ttk.Button(button_frame, text="Guardar", command=guardar_cambios).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Copiar", command=copiar_dato).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancelar", command=edit_window.destroy).pack(side=tk.LEFT)
        
        # Configurar grid
        frame.columnconfigure(1, weight=1)
    
    def eliminar_dato(self):
        """Eliminar el dato seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un dato para eliminar")
            return
        
        try:
            item = self.tree.item(selection[0])
            values = item['values']
            id_dato = values[0]
            
            # Eliminar de la base de datos
            if self.db_manager.eliminar_dato(id_dato):
                messagebox.showinfo("Éxito", "Dato eliminado correctamente")
                self.cargar_datos()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el dato")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar dato: {str(e)}")
    
    def eliminar_todos_datos(self):
        """Eliminar todos los datos de la tabla"""
        try:
            # Eliminar todos los datos
            eliminados = self.db_manager.eliminar_todos_datos()
            
            if eliminados > 0:
                messagebox.showinfo("Éxito", f"Se eliminaron {eliminados} registros correctamente")
                self.cargar_datos()
            else:
                messagebox.showinfo("Información", "No había datos para eliminar")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar todos los datos: {str(e)}")
    
    def eliminar_primer_dato(self):
        """Eliminar el primer dato de la lista"""
        try:
            # Eliminar el primer dato
            eliminado = self.db_manager.eliminar_primer_dato()
            
            if eliminado:
                messagebox.showinfo("Éxito", "El primer dato fue eliminado correctamente")
                self.cargar_datos()
            else:
                messagebox.showinfo("Información", "No hay datos para eliminar")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar el primer dato: {str(e)}")
    
    def agregar_direcciones(self):
        """Agregar nuevas direcciones"""
        try:
            direcciones_text = self.direcciones_text.get("1.0", tk.END).strip()
            if not direcciones_text:
                messagebox.showwarning("Advertencia", "Ingrese direcciones para agregar")
                return
            
            direcciones = [d.strip() for d in direcciones_text.split('\n') if d.strip()]
            
            # Agregar a la base de datos
            agregadas = self.db_manager.agregar_direcciones(direcciones)
            
            if agregadas > 0:
                messagebox.showinfo("Éxito", f"Se agregaron {agregadas} direcciones")
                self.direcciones_text.delete("1.0", tk.END)
                self.data_manager.cargar_direcciones()
                self.actualizar_contador_direcciones()
            else:
                messagebox.showinfo("Información", "No se agregaron nuevas direcciones")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar direcciones: {str(e)}")
    
    def actualizar_contador_direcciones(self):
        """Actualizar el contador de direcciones disponibles"""
        count = len(self.data_manager.direcciones_disponibles)
        self.contador_label.config(text=f"Direcciones disponibles: {count}")

    def resetear_ids_y_datos(self):
        """Resetea los IDs de la tabla datos para que el próximo sea el que elija el usuario (borra todos los datos)."""
        if messagebox.askyesno("Confirmar", "¿Seguro que quieres borrar TODOS los datos y reiniciar el ID?\nSe te preguntará desde qué número empezar."):
            try:
                import tkinter.simpledialog
                id_inicial = tkinter.simpledialog.askinteger(
                    "ID inicial", "¿Desde qué número quieres que empiece el ID? (mínimo 1)",
                    minvalue=1, initialvalue=101
                )
                if id_inicial is None:
                    return
                self.db_manager.resetear_ids_datos(id_inicial)
                messagebox.showinfo("Éxito", f"Todos los datos fueron borrados y el próximo ID será {id_inicial}.")
                self.cargar_datos()
                self.actualizar_contador_direcciones()
            except Exception as e:
                messagebox.showerror("Error", f"Error al resetear IDs: {str(e)}")

