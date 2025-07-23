# Aplicación de Gestión de Datos - Tkinter

Aplicación de escritorio para gestión de datos con interfaz gráfica nativa usando Tkinter.

## Características

- **Interfaz gráfica nativa**: Aplicación de escritorio con Tkinter
- **Gestión de datos**: Crear, editar, eliminar registros
- **Gestión de direcciones**: Agregar y gestionar direcciones
- **Generación automática**: Códigos y números aleatorios
- **Base de datos SQLite**: Almacenamiento local de datos

## Instalación

### Requisitos
- Python 3.6+ con Tkinter (incluido por defecto en la mayoría de instalaciones)
- No se requieren dependencias externas

### Ejecutar la aplicación

```bash
# Opción 1: Usar el script de inicio
python gui.py

# Opción 2: Ejecutar directamente
python main.py

# Opción 3: Ejecutar la aplicación
python app.py
```

## Funcionalidades

### Gestión de Datos
- **Crear registros**: Ingrese fecha y nombres (uno por línea)
- **Editar registros**: Seleccione un registro y haga clic en "Editar"
- **Eliminar registros**: Seleccione un registro y haga clic en "Eliminar"
- **Ver todos los registros**: Tabla con todos los datos

### Gestión de Direcciones
- **Agregar direcciones**: Ingrese direcciones (una por línea)
- **Ver direcciones disponibles**: Contador de direcciones libres
- **Asignación automática**: Las direcciones se asignan automáticamente

### Generación Automática
- **Códigos aleatorios**: Formato personalizable
- **Números decimales**: Para campos de amount
- **Modo de código**: Aleatorio o terminando en 5

## Estructura del Proyecto

```
auto-pdf/
├── main.py                # Punto de entrada principal
├── app.py                 # Aplicación principal
├── gui.py                 # Script de inicio GUI
├── requirements.txt        # Requisitos
├── README_DETAILED.md     # Documentación detallada
├── README.md              # Este archivo
└── datos.db               # Base de datos SQLite
```

## Base de Datos

La aplicación utiliza SQLite con dos tablas principales:

### Tabla `datos`
- `id`: Identificador único
- `fecha`: Fecha del registro
- `codigo`: Código generado
- `nombre`: Nombre del registro
- `drireccion`: Dirección asociada
- `zip4`: Código ZIP+4
- `amount_current_any`: Cantidad actual (decimal)
- `amount_current_regular`: Cantidad actual (entero)
- `amount_pas_any`: Cantidad PAS (decimal)
- `amount_pas_regular`: Cantidad PAS (entero)

### Tabla `direcciones`
- `id`: Identificador único
- `direccion`: Dirección completa
- `zip4`: Código ZIP+4 asociado

## Ventajas

1. **Sin servidor**: No requiere FastAPI ni servidor web
2. **Interfaz nativa**: Mejor integración con el sistema operativo
3. **Más rápida**: Sin latencia de red
4. **Más simple**: Menos dependencias
5. **Offline**: Funciona completamente sin conexión

## Solución de Problemas

### Error: "No module named 'tkinter'"
- Instale tkinter: `sudo apt-get install python3-tk` (Ubuntu/Debian)
- En Windows/macOS, tkinter suele estar incluido

### Error de base de datos
- La aplicación creará automáticamente la base de datos si no existe
- Verifique permisos de escritura en el directorio

### Interfaz no se muestra
- Verifique que Python tenga soporte para GUI
- En servidores sin GUI, use X11 forwarding o VNC

## Documentación Detallada

Para más información, consulte `README_DETAILED.md`. 