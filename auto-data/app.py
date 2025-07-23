import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import re
import random
import string
from datetime import datetime
from typing import List, Optional, Dict, Any
import os

class Dato:
    def __init__(self, id: Optional[int] = None, fecha: str = "", codigo: str = "", 
                 nombre: str = "", drireccion: str = "", zip4: Optional[str] = None,
                 amount_current_any: float = 0.0, amount_current_regular: int = 0,
                 amount_pas_any: float = 0.0, amount_pas_regular: int = 0):
        self.id = id
        self.fecha = fecha
        self.codigo = codigo
        self.nombre = nombre
        self.drireccion = drireccion
        self.zip4 = zip4
        self.amount_current_any = amount_current_any
        self.amount_current_regular = amount_current_regular
        self.amount_pas_any = amount_pas_any
        self.amount_pas_regular = amount_pas_regular
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'fecha': self.fecha,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'drireccion': self.drireccion,
            'zip4': self.zip4,
            'amount_current_any': self.amount_current_any,
            'amount_current_regular': self.amount_current_regular,
            'amount_pas_any': self.amount_pas_any,
            'amount_pas_regular': self.amount_pas_regular
        }

class DatabaseManager:
    def __init__(self, db_path: str = "datos.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializar la base de datos con las tablas necesarias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Crear tabla datos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS datos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                codigo TEXT NOT NULL,
                nombre TEXT NOT NULL,
                drireccion TEXT NOT NULL,
                zip4 TEXT,
                amount_current_any REAL,
                amount_current_regular INTEGER,
                amount_pas_any REAL,
                amount_pas_regular INTEGER
            )
        ''')
        
        # Crear tabla direcciones con columna usada
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS direcciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                direccion TEXT UNIQUE NOT NULL,
                zip4 TEXT,
                usada INTEGER DEFAULT 0
            )
        ''')
        
        # Si la columna usada no existe, agregarla
        cursor.execute("PRAGMA table_info(direcciones)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'usada' not in columns:
            cursor.execute('ALTER TABLE direcciones ADD COLUMN usada INTEGER DEFAULT 0')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def crear_dato(self, dato: Dato) -> int:
        """Crear un nuevo dato en la base de datos, evitando nombres duplicados (case-insensitive) y reemplazando guiones por espacios en el nombre"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Reemplazar guiones por espacios en el nombre
            dato.nombre = dato.nombre.replace('-', ' ')
            
            # Verificar nombre duplicado (case-insensitive)
            cursor.execute('SELECT COUNT(*) FROM datos WHERE UPPER(nombre) = UPPER(?)', (dato.nombre,))
            if cursor.fetchone()[0] > 0:
                conn.close()
                raise ValueError('El nombre ya existe en la base de datos.')
            
            # Procesar dirección
            drireccion_original = dato.drireccion
            sin_numero = re.sub(r"^\d+\.\s*", "", drireccion_original)
            sin_la = re.sub(r",\s*LOS ANGELES", "", sin_numero, flags=re.IGNORECASE)
            partes = sin_la.rsplit(",", 1)
            calle_limpia = partes[0].strip() if len(partes) > 1 else sin_la.strip()
            
            # Extraer ZIP+4
            match_zip = re.search(r"(\d{5})(-(\d{4,5}))?$", sin_la)
            if match_zip:
                zip5 = match_zip.group(1)
                zip4_5 = match_zip.group(3)
                if zip4_5:
                    if len(zip4_5) == 4 or len(zip4_5) == 5:
                        zip4 = f"{zip5}-{zip4_5}"
                    else:
                        zip4 = ""
                else:
                    zip4 = zip5
            else:
                zip4 = ""
            dato.drireccion = calle_limpia
            dato.zip4 = zip4
            
            # Buscar ZIP4 en tabla direcciones si no se encontró
            if not dato.zip4:
                cursor.execute('SELECT zip4 FROM direcciones WHERE direccion = ?', (dato.drireccion,))
                resultado = cursor.fetchone()
                if resultado and resultado[0]:
                    dato.zip4 = resultado[0]
                else:
                    dato.zip4 = ""
            
            # Validar que la dirección no esté repetida
            cursor.execute('SELECT COUNT(*) FROM datos WHERE drireccion = ?', (dato.drireccion,))
            if cursor.fetchone()[0] > 0:
                conn.close()
                raise ValueError('La dirección ya existe en la base de datos.')
            
            # Formatear fecha
            if isinstance(dato.fecha, str):
                fecha_formateada = dato.fecha
            else:
                fecha_formateada = str(dato.fecha)
            
            # Insertar dato
            cursor.execute('''
                INSERT INTO datos (fecha, codigo, nombre, drireccion, zip4, amount_current_any, amount_current_regular, amount_pas_any, amount_pas_regular)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (fecha_formateada, dato.codigo, dato.nombre, dato.drireccion, dato.zip4, 
                  dato.amount_current_any, dato.amount_current_regular, dato.amount_pas_any, dato.amount_pas_regular))
            
            # Insertar en direcciones si es necesario y marcar como usada
            if dato.drireccion and dato.zip4:
                cursor.execute('INSERT OR IGNORE INTO direcciones (direccion, zip4, usada) VALUES (?, ?, 0)', 
                             (dato.drireccion, dato.zip4))
                cursor.execute('UPDATE direcciones SET usada=1 WHERE direccion=?', (dato.drireccion,))
            
            conn.commit()
            id_insertado = cursor.lastrowid
            conn.close()
            return id_insertado
            
        except Exception as e:
            if 'conn' in locals():
                conn.close()
            raise e
    
    def leer_datos(self) -> List[Dato]:
        """Leer todos los datos de la base de datos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM datos')
            filas = cursor.fetchall()
            conn.close()
            
            datos = []
            for f in filas:
                if 'q' not in str(f[3]).lower():  # Filtrar nombres con 'q'
                    try:
                        datos.append(Dato(
                            id=f[0], fecha=f[1], codigo=f[2], nombre=f[3], drireccion=f[4],
                            zip4=f[5] if f[5] is not None else "", amount_current_any=float(f[6]) if f[6] is not None else 0.0,
                            amount_current_regular=int(float(f[7])) if f[7] is not None else 0,
                            amount_pas_any=float(f[8]) if f[8] is not None else 0.0,
                            amount_pas_regular=int(float(f[9])) if f[9] is not None else 0
                        ))
                    except Exception:
                        continue
            
            return datos
        except Exception as e:
            raise e
    
    def eliminar_dato(self, id: int) -> bool:
        """Eliminar un dato por ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM datos WHERE id = ?', (int(id),))
            conn.commit()
            eliminado = cursor.rowcount > 0
            conn.close()
            return eliminado
        except Exception as e:
            raise e
    
    def eliminar_todos_datos(self) -> int:
        """Eliminar todos los datos de la tabla datos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM datos')
            eliminados = cursor.rowcount
            conn.commit()
            conn.close()
            return eliminados
        except Exception as e:
            raise e
    
    def eliminar_primer_dato(self) -> bool:
        """Eliminar el primer dato (ID más bajo) de la tabla datos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Obtener el ID más bajo (primer dato)
            cursor.execute('SELECT MIN(id) FROM datos')
            resultado = cursor.fetchone()
            
            if resultado and resultado[0] is not None:
                primer_id = resultado[0]
                cursor.execute('DELETE FROM datos WHERE id = ?', (primer_id,))
                eliminado = cursor.rowcount > 0
                conn.commit()
                conn.close()
                return eliminado
            else:
                conn.close()
                return False
                
        except Exception as e:
            raise e
    
    def obtener_direcciones_ocupadas(self) -> List[str]:
        """Obtener direcciones que ya están en uso"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT drireccion FROM datos')
            filas = cursor.fetchall()
            conn.close()
            return [f[0] for f in filas if f[0]]
        except Exception as e:
            raise e
    
    def obtener_direcciones_limpias(self) -> List[Dict[str, str]]:
        """Obtener todas las direcciones disponibles (no usadas nunca)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT direccion, zip4 FROM direcciones WHERE usada=0')
            filas = cursor.fetchall()
            conn.close()
            # zip4 nunca será None, si lo es, se pone ""
            return [{"direccion": fila[0], "zip4": fila[1] if fila[1] is not None else ""} for fila in filas]
        except Exception as e:
            raise e

    def agregar_direcciones(self, direcciones: List[str]) -> int:
        """Agregar nuevas direcciones a la base de datos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            agregadas = 0
            direcciones_invalidas = []
            
            for linea in direcciones:
                linea = str(linea).strip()
                if not linea:
                    continue
                # Eliminar numeración inicial si existe
                sin_numero = re.sub(r"^\d+\.\s*", "", linea)
                zip4 = ""
                direccion = sin_numero
                # Buscar ZIP+4 al final
                match_zip4 = re.search(r"(\d{5}-\d{4})$", sin_numero)
                if match_zip4:
                    zip4 = match_zip4.group(1)
                    # Quitar el ZIP+4 y la coma final si existe
                    direccion = sin_numero[:match_zip4.start()].rstrip(',').strip()
                    # Quitar la ciudad y estado si existen (asumimos formato ...ST, LOS ANGELES, CA ...)
                    partes = direccion.split(',')
                    if len(partes) >= 3:
                        direccion = partes[0].strip()
                else:
                    # Buscar ZIP5 al final
                    match_zip5 = re.search(r"(\d{5})$", sin_numero)
                    if match_zip5:
                        zip4 = match_zip5.group(1)
                        direccion = sin_numero[:match_zip5.start()].rstrip(',').strip()
                        partes = direccion.split(',')
                        if len(partes) >= 3:
                            direccion = partes[0].strip()
                    else:
                        zip4 = ""
                        direccion = sin_numero.strip()
                if direccion:
                    cursor.execute('INSERT OR IGNORE INTO direcciones (direccion, zip4, usada) VALUES (?, ?, 0)', 
                                 (direccion, zip4))
                    agregadas += cursor.rowcount
            
            conn.commit()
            conn.close()
            
            # Si hay direcciones inválidas, mostrar advertencia
            if direcciones_invalidas:
                from tkinter import messagebox
                messagebox.showwarning("Advertencia", f"Las siguientes direcciones no tienen un ZIP válido y no fueron agregadas:\n\n" + "\n".join(direcciones_invalidas))
            
            return int(agregadas)
        except Exception as e:
            raise e

    def borrar_ultimas_100_direcciones(self) -> int:
        """Borra las últimas 100 direcciones agregadas (por id descendente)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM direcciones ORDER BY id DESC LIMIT 100')
            ids = [row[0] for row in cursor.fetchall()]
            if ids:
                cursor.executemany('DELETE FROM direcciones WHERE id = ?', [(i,) for i in ids])
            conn.commit()
            count = len(ids)
            conn.close()
            return count
        except Exception as e:
            print(f"Error al borrar direcciones: {e}")
            return 0

    def resetear_ids_datos(self, id_inicial: int = 101):
        """Borra todos los datos y reinicia el autoincremento de la tabla 'datos' para que el próximo ID sea el indicado."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            # Borrar todos los datos
            cursor.execute('DELETE FROM datos')
            # Reiniciar el autoincremento al valor indicado menos 1
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='datos'")
            cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('datos', ?)", (id_inicial - 1,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            if 'conn' in locals():
                conn.close()
            raise e

class DataManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.direcciones_disponibles = []
        self.cargar_direcciones()
    
    def cargar_direcciones(self):
        """Cargar direcciones disponibles"""
        try:
            # Obtener todas las direcciones
            direcciones = self.db.obtener_direcciones_limpias()
            # Obtener direcciones ocupadas
            ocupadas = self.db.obtener_direcciones_ocupadas()
            # Normalizar ocupadas
            ocupadas_normalizadas = [d.upper() for d in ocupadas if d]
            # Filtrar solo las libres
            self.direcciones_disponibles = [
                dir_obj for dir_obj in direcciones 
                if not ocupadas_normalizadas.count((dir_obj["direccion"] or "").upper())
            ]
        except Exception as e:
            print(f"Error al cargar direcciones: {e}")
            self.direcciones_disponibles = []
    
    def obtener_direccion_unica(self) -> Dict[str, str]:
        """Obtener una dirección única disponible"""
        if not self.direcciones_disponibles:
            return {"direccion": self.generar_direccion_aleatoria(), "zip4": ""}
        return self.direcciones_disponibles.pop(0)
    
    def generar_direccion_aleatoria(self) -> str:
        """Generar una dirección aleatoria"""
        calles = [
            "Main Street", "Oak Avenue", "Pine Road", "Elm Street", "Cedar Lane",
            "Maple Drive", "Washington Blvd", "Lincoln Avenue", "Park Street"
        ]
        numeros = random.randint(100, 9999)
        calle = random.choice(calles)
        return f"{numeros} {calle}"
    
    def generar_codigo_aleatorio(self, modo: str = 'random') -> str:
        """Generar código aleatorio"""
        letras = string.ascii_uppercase
        digitos = string.digits
        
        def rand_chars(chars, n):
            return ''.join(random.choice(chars) for _ in range(n))
        
        codigo = (rand_chars(digitos, 2) + rand_chars(letras, 2) + 
                 rand_chars(digitos, 3) + rand_chars(letras, 1) + 
                 rand_chars(digitos, 4))
        
        if modo == '5':
            codigo += '5'
        else:
            codigo += rand_chars(digitos, 1)
        
        return codigo
    
    def generar_numero_decimal(self) -> str:
        """Generar número decimal entre 10.00 y 99.99, siempre con dos decimales"""
        return f"{random.uniform(10.0, 99.99):.2f}"

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
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Gestión de Datos", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame izquierdo - Formulario
        form_frame = ttk.LabelFrame(main_frame, text="Formulario de Datos", padding="10")
        form_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        
        # Campos del formulario
        ttk.Label(form_frame, text="Fecha:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.fecha_entry = ttk.Entry(form_frame, width=20)
        self.fecha_entry.grid(row=0, column=1, sticky="we", pady=2)
        self.fecha_entry.insert(0, datetime.now().strftime("%B %d, %Y"))
        
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
        ttk.Button(button_frame, text="Pegar Datos", 
                  command=self.pegar_datos).pack(side=tk.LEFT, padx=(0, 10))
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
        columns = ('ID', 'Fecha', 'Código', 'Nombre', 'Dirección', 'ZIP4', 
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
        ttk.Button(table_button_frame, text="Copiar Seleccionado", 
                  command=self.copiar_dato_seleccionado).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(table_button_frame, text="Copiar Múltiples", 
                  command=self.copiar_datos_multiples).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(table_button_frame, text="Pegar Datos", 
                  command=self.pegar_datos).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(table_button_frame, text="Eliminar Seleccionado", 
                  command=self.eliminar_dato).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(table_button_frame, text="Actualizar Tabla", 
                  command=self.cargar_datos).pack(side=tk.LEFT, padx=(0, 10))
        
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
        
        # Configurar atajos de teclado
        self.root.bind('<Control-c>', lambda e: self.copiar_dato_seleccionado())
        self.root.bind('<Control-v>', lambda e: self.pegar_datos())
        self.root.bind('<Control-Shift-c>', lambda e: self.copiar_datos_multiples())
        
        # También configurar para el frame principal
        self.root.bind_all('<Control-v>', lambda e: self.pegar_datos())
        self.root.bind_all('<Control-c>', lambda e: self.copiar_dato_seleccionado())
        
        # Configurar eventos de teclado específicos para los widgets de texto
        self.nombres_text.bind('<Control-v>', lambda e: self.pegar_en_texto(e))
        self.direcciones_text.bind('<Control-v>', lambda e: self.pegar_en_texto(e))
    
    def guardar_datos(self):
        """Guardar datos desde el formulario"""
        try:
            fecha = self.fecha_entry.get().strip()
            nombres_text = self.nombres_text.get("1.0", tk.END).strip()
            
            if not fecha:
                messagebox.showerror("Error", "La fecha es obligatoria")
                return
            
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
                        fecha=fecha,
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

        ttk.Label(frame, text="Código:").grid(row=2, column=0, sticky=tk.W, pady=2)
        codigo_entry = ttk.Entry(frame)
        codigo_entry.grid(row=2, column=1, sticky="we", pady=2)
        codigo_entry.insert(0, values[2])
        ttk.Button(frame, text="Copiar", command=lambda: self.copiar_campo_directo(codigo_entry, edit_window)).grid(row=2, column=2, padx=2)

        ttk.Label(frame, text="Nombre:").grid(row=3, column=0, sticky=tk.W, pady=2)
        nombre_entry = ttk.Entry(frame)
        nombre_entry.grid(row=3, column=1, sticky="we", pady=2)
        nombre_entry.insert(0, values[3])
        ttk.Button(frame, text="Copiar", command=lambda: self.copiar_campo_directo(nombre_entry, edit_window)).grid(row=3, column=2, padx=2)

        ttk.Label(frame, text="Dirección:").grid(row=4, column=0, sticky=tk.W, pady=2)
        direccion_entry = ttk.Entry(frame)
        direccion_entry.grid(row=4, column=1, sticky="we", pady=2)
        direccion_entry.insert(0, values[4])
        ttk.Button(frame, text="Copiar", command=lambda: self.copiar_campo_directo(direccion_entry, edit_window)).grid(row=4, column=2, padx=2)

        ttk.Label(frame, text="ZIP4:").grid(row=5, column=0, sticky=tk.W, pady=2)
        zip4_entry = ttk.Entry(frame)
        zip4_entry.grid(row=5, column=1, sticky="we", pady=2)
        zip4_entry.insert(0, values[5] if values[5] else "")
        ttk.Button(frame, text="Copiar", command=lambda: self.copiar_campo_directo(zip4_entry, edit_window)).grid(row=5, column=2, padx=2)

        ttk.Label(frame, text="Amount Current Any:").grid(row=6, column=0, sticky=tk.W, pady=2)
        aca_entry = ttk.Entry(frame)
        aca_entry.grid(row=6, column=1, sticky="we", pady=2)
        aca_entry.insert(0, fmt(values[6]))
        ttk.Button(frame, text="Copiar", command=lambda: self.copiar_campo_directo(aca_entry, edit_window)).grid(row=6, column=2, padx=2)

        ttk.Label(frame, text="Amount Current Regular:").grid(row=7, column=0, sticky=tk.W, pady=2)
        acr_entry = ttk.Entry(frame)
        acr_entry.grid(row=7, column=1, sticky="we", pady=2)
        acr_entry.insert(0, values[7])
        ttk.Button(frame, text="Copiar", command=lambda: self.copiar_campo_directo(acr_entry, edit_window)).grid(row=7, column=2, padx=2)

        ttk.Label(frame, text="Amount PAS Any:").grid(row=8, column=0, sticky=tk.W, pady=2)
        apa_entry = ttk.Entry(frame)
        apa_entry.grid(row=8, column=1, sticky="we", pady=2)
        apa_entry.insert(0, fmt(values[8]))
        ttk.Button(frame, text="Copiar", command=lambda: self.copiar_campo_directo(apa_entry, edit_window)).grid(row=8, column=2, padx=2)

        ttk.Label(frame, text="Amount PAS Regular:").grid(row=9, column=0, sticky=tk.W, pady=2)
        apr_entry = ttk.Entry(frame)
        apr_entry.grid(row=9, column=1, sticky="we", pady=2)
        apr_entry.insert(0, values[9])
        ttk.Button(frame, text="Copiar", command=lambda: self.copiar_campo_directo(apr_entry, edit_window)).grid(row=9, column=2, padx=2)
        
        # Botones
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=10, column=0, columnspan=2, pady=20)

        def guardar_cambios():
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
            # Actualizar en la base de datos
            try:
                self.db_manager.get_connection().execute(
                    "UPDATE datos SET fecha=?, codigo=?, nombre=?, drireccion=?, zip4=?, amount_current_any=?, amount_current_regular=?, amount_pas_any=?, amount_pas_regular=? WHERE id=?",
                    (
                        valores[1], valores[2], valores[3], valores[4], valores[5],
                        float(valores[6]), int(valores[7]), float(valores[8]), int(valores[9]), int(valores[0])
                    )
                )
                self.db_manager.get_connection().commit()
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

def main():
    root = tk.Tk()
    app = TkinterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 