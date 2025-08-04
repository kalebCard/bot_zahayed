
from typing import Optional, Dict, Any

class Dato:
    def __init__(self, id: Optional[int] = None, codigo: str = "", 
                 nombre: str = "", drireccion: str = "", zip4: Optional[str] = None,
                 amount_current_any: float = 0.0, amount_current_regular: int = 0,
                 amount_pas_any: float = 0.0, amount_pas_regular: int = 0):
        self.id = id
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
            'codigo': self.codigo,
            'nombre': self.nombre,
            'drireccion': self.drireccion,
            'zip4': self.zip4,
            'amount_current_any': self.amount_current_any,
            'amount_current_regular': self.amount_current_regular,
            'amount_pas_any': self.amount_pas_any,
            'amount_pas_regular': self.amount_pas_regular
        }
