# 🎯 Auto-Task - Gestor de Automatizaciones

Un programa completo y eficiente para gestionar automatizaciones de teclado y mouse de manera profesional.

## ✨ Características Principales

- 🎙️ **Grabación Inteligente**: Captura eventos de teclado y mouse con precisión
- ▶️ **Reproducción Avanzada**: Control de velocidad y repeticiones configurables
- ✏️ **Editor Completo**: Modifica, edita y optimiza automatizaciones
- 💾 **Gestión de Archivos**: Sistema robusto de guardado y organización
- 🖥️ **Interfaz Gráfica**: UI intuitiva y fácil de usar
- 🔍 **Búsqueda y Filtrado**: Encuentra automatizaciones rápidamente
- 📤 **Exportación/Importación**: Comparte automatizaciones fácilmente
- 🏷️ **Sistema de Tags**: Organiza automatizaciones con etiquetas

## 🚀 Instalación

### Requisitos Previos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**:
   ```bash
   git clone https://github.com/tu-usuario/auto-task.git
   cd auto-task
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verificar instalación**:
   ```bash
   python main.py --check
   ```

## 📖 Uso

### Interfaz Gráfica (Recomendado)

```bash
python main.py
```

### Línea de Comandos

#### Grabar una automatización:
```bash
python main.py --record
```

#### Reproducir una automatización:
```bash
python main.py --play "nombre_automatizacion"
```

#### Reproducir con velocidad personalizada:
```bash
python main.py --play "mi_auto" --speed 2.0 --repeats 3
```

#### Listar automatizaciones:
```bash
python main.py --list
```

#### Verificar dependencias:
```bash
python main.py --check
```

## 🎮 Guía de Uso

### 1. Grabación de Automatizaciones

1. **Iniciar grabación**:
   - Haz clic en "🎙️ Iniciar Grabación"
   - Realiza las acciones que quieres automatizar
   - **Solo se graban**: clics, teclado y scroll (NO movimientos del mouse)
   - Presiona `Ctrl+Shift+R` para detener

2. **Guardar automatización**:
   - Ingresa un nombre descriptivo
   - Añade una descripción
   - Agrega tags para organización

### 2. Reproducción de Automatizaciones

1. **Seleccionar automatización**:
   - Busca en la lista de automatizaciones
   - Selecciona la que quieres reproducir

2. **Configurar reproducción**:
   - Ajusta la velocidad (0.1x - 3.0x)
   - Establece el número de repeticiones
   - Haz clic en "▶️ Reproducir"

### 3. Edición de Automatizaciones

1. **Abrir editor**:
   - Selecciona una automatización
   - Haz clic en "✏️ Editar"

2. **Herramientas de edición**:
   - **Eliminar eventos**: Selecciona y elimina eventos no deseados
   - **Duplicar eventos**: Copia eventos para reutilización
   - **Ajustar tiempos**: Modifica la velocidad de toda la automatización
   - **Limpiar movimientos**: Elimina movimientos de mouse pequeños

### 4. Gestión de Archivos

- **Exportar**: Guarda automatizaciones en formato JSON
- **Importar**: Carga automatizaciones desde archivos externos
- **Eliminar**: Borra automatizaciones no deseadas
- **Buscar**: Encuentra automatizaciones por nombre, descripción o tags

## 📁 Estructura del Proyecto

```
auto-task/
├── main.py              # Archivo principal
├── gui.py               # Interfaz gráfica
├── rec.py               # Módulo de grabación
├── play.py              # Módulo de reproducción
├── save.py              # Módulo de guardado
├── edit.py              # Módulo de edición
├── requirements.txt     # Dependencias
├── README.md           # Documentación
├── automations/        # Directorio de automatizaciones
├── logs/              # Directorio de logs
└── exports/           # Directorio de exportaciones
```

## 🔧 Configuración Avanzada

### Personalización de Atajos de Teclado

Puedes modificar los atajos de teclado editando el archivo `rec.py`:

```python
# Cambiar atajo para detener grabación
if key == keyboard.KeyCode.from_char('r') and self.is_ctrl_shift_pressed():
    self.stop_recording()
```

### Configuración de Directorios

Los directorios se crean automáticamente, pero puedes personalizarlos:

```python
# En save.py
self.save_directory = Path("mi_directorio_personalizado")
```

## 🐛 Solución de Problemas

### Error: "pynput no está instalado"
```bash
pip install pynput
```

### Error: "tkinter no está disponible"
- En Ubuntu/Debian: `sudo apt-get install python3-tk`
- En CentOS/RHEL: `sudo yum install tkinter`
- En Windows: Normalmente viene incluido con Python

### Error: "Permisos insuficientes"
- En Linux/macOS: Ejecuta con permisos de administrador
- En Windows: Ejecuta como administrador

### La grabación no funciona
1. Verifica que no haya otros programas usando el teclado/mouse
2. Asegúrate de que el programa tenga permisos de administrador
3. Revisa que no haya antivirus bloqueando la aplicación

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Para contribuir:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

- [pynput](https://github.com/moses-palmer/pynput) - Librería para control de teclado y mouse
- [tkinter](https://docs.python.org/3/library/tkinter.html) - Interfaz gráfica de Python

## 📞 Soporte

Si tienes problemas o preguntas:

1. Revisa la sección de [Solución de Problemas](#-solución-de-problemas)
2. Busca en los [Issues](https://github.com/tu-usuario/auto-task/issues)
3. Crea un nuevo issue si no encuentras solución

---

**¡Disfruta automatizando tus tareas! 🎯** 