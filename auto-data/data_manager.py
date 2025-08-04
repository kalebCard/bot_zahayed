
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
