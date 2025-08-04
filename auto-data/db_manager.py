
import sqlite3
import re
from typing import List, Dict
from dato import Dato

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
            
            # Insertar dato
            cursor.execute('''
                INSERT INTO datos (codigo, nombre, drireccion, zip4, amount_current_any, amount_current_regular, amount_pas_any, amount_pas_regular)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (dato.codigo, dato.nombre, dato.drireccion, dato.zip4, 
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
            cursor.execute('SELECT id, codigo, nombre, drireccion, zip4, amount_current_any, amount_current_regular, amount_pas_any, amount_pas_regular FROM datos')
            filas = cursor.fetchall()
            conn.close()
            
            datos = []
            for f in filas:
                if 'q' not in str(f[2]).lower():  # Filtrar nombres con 'q'
                    try:
                        datos.append(Dato(
                            id=f[0], codigo=f[1], nombre=f[2], drireccion=f[3],
                            zip4=f[4] if f[4] is not None else "", amount_current_any=float(f[5]) if f[5] is not None else 0.0,
                            amount_current_regular=int(float(f[6])) if f[6] is not None else 0,
                            amount_pas_any=float(f[7]) if f[7] is not None else 0.0,
                            amount_pas_regular=int(float(f[8])) if f[8] is not None else 0
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
