
import random
import string
from typing import Dict
from db_manager import DatabaseManager

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
        """
        Genera un código aleatorio en formato compacto.
        Formato: 2D 2L 3D 1L 4D 1D  (D=dígito, L=letra)
        Ejemplo: '12AB345C67890' o '34XY789Z12345' si modo='5'
        """
        def rc(chars, n):  # Función auxiliar más corta
            return ''.join(random.choices(chars, k=n))
            
        # Generar las partes del código de manera más eficiente
        p1 = rc(string.digits, 2)     # 2 dígitos
        p2 = rc(string.ascii_uppercase, 2)  # 2 letras
        p3 = rc(string.digits, 3)     # 3 dígitos
        p4 = rc(string.ascii_uppercase, 1)  # 1 letra
        p5 = rc(string.digits, 4)     # 4 dígitos
        p6 = '5' if modo == '5' else rc(string.digits, 1)  # 1 dígito o '5'
        
        return f"{p1}{p2}{p3}{p4}{p5}{p6}"
    
    def generar_numero_decimal(self) -> str:
        """Generar número decimal entre 10.00 y 99.99, siempre con dos decimales"""
        return f"{random.uniform(10.0, 99.99):.2f}"
